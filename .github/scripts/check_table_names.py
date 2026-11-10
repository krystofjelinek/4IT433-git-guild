"""Kontrola názvů tabulek v notebooch Fabricu (T8, GitHub Actions).

Projde všechny notebook-content.py ve složce s Fabric položkami a najde místa,
kde notebook vytváří nebo zapisuje tabulku:

  Python / PySpark   .saveAsTable("x"), .toTable("x"), .tableName("x"),
                     .save("Tables/x"), spark.sql("CREATE TABLE x ...")
  SQL buňky (%%sql)  CREATE [OR REPLACE] TABLE x, CREATE MATERIALIZED LAKE VIEW x

U každého názvu ověří:
  1. začíná povoleným prefixem vrstvy (bronze_, silver_, ...),
  2. odpovídá vzoru názvu (malá písmena, číslice, podtržítka).

Název se vyhodnocuje staticky z kódu, data se nečtou:
  * řetězec "bronze_x"                       → ověří se celý,
  * f-string f"silver_{name}"                 → ověří se pevný začátek,
  * proměnná target = f"bronze_{t}"           → dohledá se přiřazení ve stejném souboru,
  * cokoli jiného (parametr, výsledek funkce) → nejde ověřit, hlásí se varování
                                                (v režimu strict jako chyba).

Výjimka: na stejný nebo předchozí řádek napište komentář
    # allow-table-name: <důvod>       (Python)
    -- allow-table-name: <důvod>      (SQL)
Důvod je povinný. Výjimku musí schválit guilda (viz standard).

Použití:  python .github/scripts/check_table_names.py [--config .github/pr-checks.toml] [--strict]
"""
import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path

from _report import Finding, die, load_config, report, repo_relative

WRITE_METHODS = {"saveAsTable", "toTable", "tableName"}
EXCEPTION_RE = re.compile(r"(?:#|--)\s*allow-table-name\s*:?\s*(.*)$", re.IGNORECASE)
NAME_TOKEN = r"(`[^`]+`|\[[^\]]+\]|[\w.`\[\]{}…]+)"
SQL_CREATE_RE = re.compile(
    r"\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:EXTERNAL\s+)?"
    r"(?:TABLE|MATERIALIZED\s+LAKE\s+VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?" + NAME_TOKEN,
    re.IGNORECASE,
)


@dataclass
class Candidate:
    """Jeden nalezený zápis do tabulky."""
    line: int
    kind: str                 # "literal" | "prefix" | "unknown"
    value: str                # celý název, pevný začátek nebo popis výrazu
    origin: str               # čím se tabulka zapisuje (pro hlášení)


# ---------------------------------------------------------------- názvy

def normalize(name: str) -> str:
    """lakehouse.dbo.`bronze_x` → bronze_x"""
    name = name.strip().strip(";,()")
    name = name.replace("`", "").replace("[", "").replace("]", "").replace('"', "")
    return name.split(".")[-1]


def table_from_path(path: str) -> str:
    """Tables/bronze_x nebo Tables/dbo/bronze_x → bronze_x"""
    return path.rstrip("/").split("/")[-1]


# ---------------------------------------------------------------- Python (AST)

def literal_prefix(node: ast.AST) -> tuple[str, str] | None:
    """Vrátí (kind, hodnota) pro řetězec nebo f-string, jinak None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return "literal", node.value
    if isinstance(node, ast.JoinedStr):
        if all(isinstance(p, ast.Constant) for p in node.values):
            return "literal", "".join(p.value for p in node.values)
        prefix = ""
        for part in node.values:
            if not isinstance(part, ast.Constant):
                break
            prefix += part.value
        return "prefix", prefix
    return None


def collect_assignments(tree: ast.AST) -> dict[str, list[ast.AST]]:
    assigns: dict[str, list[ast.AST]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigns.setdefault(target.id, []).append(node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value:
            assigns.setdefault(node.target.id, []).append(node.value)
    return assigns


def resolve(node: ast.AST, assigns: dict[str, list[ast.AST]], line: int, origin: str) -> list[Candidate]:
    lit = literal_prefix(node)
    if lit:
        kind, value = lit
        return [Candidate(line, kind, value, origin)]
    if isinstance(node, ast.Name) and node.id in assigns:
        out = []
        for value in assigns[node.id]:
            lit = literal_prefix(value)
            if not lit:
                return [Candidate(line, "unknown", node.id, origin)]
            out.append(Candidate(line, lit[0], lit[1], f"{origin} přes proměnnou {node.id}"))
        return out
    return [Candidate(line, "unknown", ast.unparse(node), origin)]


def scan_python(tree: ast.AST) -> list[Candidate]:
    assigns = collect_assignments(tree)
    found: list[Candidate] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        method = node.func.attr
        line = node.func.end_lineno or node.lineno   # řádek s .saveAsTable(), ne začátek řetězu
        arg = node.args[0] if node.args else next(
            (k.value for k in node.keywords if k.arg in ("name", "tableName", "path")), None)
        if arg is None:
            continue

        if method in WRITE_METHODS:
            found += resolve(arg, assigns, line, f".{method}()")

        elif method == "save":
            lit = literal_prefix(arg)
            if lit and lit[1].startswith("Tables/"):
                kind, value = lit
                found.append(Candidate(line, kind, table_from_path(value) if kind == "literal"
                                       else value[len("Tables/"):].split("/")[-1], '.save("Tables/...")'))

        elif method == "sql":
            lit = literal_prefix(arg)
            if lit and lit[0] == "literal":
                for m in SQL_CREATE_RE.finditer(lit[1]):
                    found.append(Candidate(line, "literal", normalize(m.group(1)), "spark.sql(CREATE ...)"))
            elif isinstance(arg, ast.JoinedStr):
                text = "".join(p.value if isinstance(p, ast.Constant) else "{…}" for p in arg.values)
                for m in SQL_CREATE_RE.finditer(text):
                    name = normalize(m.group(1))
                    kind = "prefix" if "{…}" in name else "literal"
                    found.append(Candidate(line, kind, name.split("{…}")[0], "spark.sql(f\"CREATE ...\")"))
    return found


def scan_regex_fallback(text: str) -> list[Candidate]:
    """Pro soubory, které nejdou zparsovat (syntaktickou chybu nahlásí lint)."""
    found = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r"\.(saveAsTable|toTable|tableName)\(\s*[\"']([^\"']+)[\"']", line):
            found.append(Candidate(i, "literal", m.group(2), f".{m.group(1)}()"))
    return found


# ---------------------------------------------------------------- SQL buňky

def scan_sql_cells(lines: list[str]) -> list[Candidate]:
    """Fabric ukládá SQL buňky jako řádky '# MAGIC ...'."""
    found = []
    for i, line in enumerate(lines, 1):
        if line.startswith("# MAGIC"):
            sql = line[len("# MAGIC"):]
            for m in SQL_CREATE_RE.finditer(sql):
                found.append(Candidate(i, "literal", normalize(m.group(1)), "SQL buňka CREATE"))
    return found


# ---------------------------------------------------------------- vyhodnocení

def exception_for(lines: list[str], line: int) -> str | None:
    for idx in (line - 1, line - 2):
        if 0 <= idx < len(lines):
            m = EXCEPTION_RE.search(lines[idx])
            if m:
                return m.group(1).strip()
    return None


def evaluate(c: Candidate, prefixes: list[str], pattern: re.Pattern, rel: str,
             lines: list[str]) -> tuple[Finding | None, str | None]:
    reason = exception_for(lines, c.line)
    if reason is not None:
        if not reason:
            return Finding("error", "Výjimka allow-table-name nemá uvedený důvod.", rel, c.line), None
        return None, f"{rel}:{c.line}  {c.value or c.origin}  (výjimka: {reason})"

    allowed = ", ".join(prefixes)
    if c.kind == "unknown":
        return Finding("warning",
                       f"Název tabulky v {c.origin} je výraz `{c.value}`, nejde ověřit staticky. "
                       f"Použijte řetězec nebo f-string začínající prefixem ({allowed}).", rel, c.line), None

    name = normalize(c.value)          # lakehouse.dbo.silver_x → silver_x
    shown = name if c.kind == "literal" else f"{name}…"

    if c.kind == "literal" and not pattern.match(name):
        return Finding("error",
                       f"Tabulka `{name}` ({c.origin}) porušuje konvenci názvu: "
                       f"jen malá písmena, číslice a podtržítka.", rel, c.line), None

    if not name.startswith(tuple(prefixes)):
        return Finding("error",
                       f"Tabulka `{shown}` ({c.origin}) nemá povolený prefix vrstvy. Povolené: {allowed}.",
                       rel, c.line), None

    suffix = "" if c.kind == "literal" else "  (ověřen pevný začátek)"
    return None, f"{rel}:{c.line}  {shown}  {c.origin}{suffix}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=".github/pr-checks.toml")
    ap.add_argument("--strict", action="store_true", help="varování také shodí kontrolu")
    args = ap.parse_args()

    cfg = load_config(args.config).get("tables", {})
    scan_dir = Path(cfg.get("scan_dir", "fabric"))
    prefixes = cfg.get("allowed_prefixes", ["bronze_", "silver_"])
    pattern = re.compile(cfg.get("name_pattern", r"^[a-z][a-z0-9_]*$"))
    strict = args.strict or cfg.get("strict", False)

    if not scan_dir.is_dir():
        die(f"Složka {scan_dir} neexistuje. Spouštějte z kořene repozitáře.")

    findings: list[Finding] = []
    ok: list[str] = []
    notebooks = sorted(scan_dir.rglob("notebook-content.py"))

    for path in notebooks:
        rel = repo_relative(path)
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        try:
            candidates = scan_python(ast.parse(text))
        except SyntaxError as e:
            findings.append(Finding("warning",
                                    f"Soubor nejde zparsovat ({e.msg}, ř. {e.lineno}); názvy tabulek "
                                    f"ověřeny jen zjednodušeně. Chybu syntaxe hlásí lint.", rel, e.lineno))
            candidates = scan_regex_fallback(text)
        candidates += scan_sql_cells(lines)

        for c in sorted(candidates, key=lambda c: c.line):
            finding, ok_line = evaluate(c, prefixes, pattern, rel, lines)
            if finding:
                findings.append(finding)
            if ok_line:
                ok.append(ok_line)

    if not notebooks:
        findings.append(Finding("warning", f"Ve složce {scan_dir} nebyl nalezen žádný notebook."))

    return report("Názvy tabulek", findings, ok, strict)


if __name__ == "__main__":
    raise SystemExit(main())
