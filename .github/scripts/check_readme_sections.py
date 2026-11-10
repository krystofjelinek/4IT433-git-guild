"""Kontrola povinných sekcí README (T8, GitHub Actions).

Seznam povinných sekcí je v .github/pr-checks.toml ([[readme.sections]]).
Sekce je splněná, když:
  1. existuje nadpis (# až ######), který obsahuje některé z klíčových slov,
  2. pod nadpisem je skutečný obsah (aspoň min_content_chars znaků
     včetně podsekcí, bez samotných nadpisů),
  3. obsah není jen zástupný text (TODO, doplnit, ...).

Porovnání ignoruje velikost písmen i diakritiku a klíčové slovo musí začínat
na začátku slova: „licenc“ najde „Licence zdrojů“, ale „ai“ nenajde „detail“.
Jeden nadpis může splnit víc sekcí (např. „Licence zdrojů a použití AI“).

Použití:  python .github/scripts/check_readme_sections.py [--config .github/pr-checks.toml] [--readme README.md]
"""
import argparse
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from _report import Finding, die, load_config, report

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


@dataclass
class Section:
    level: int
    title: str
    line: int
    body: list[str] = field(default_factory=list)   # řádky včetně podsekcí


def plain(text: str) -> str:
    """Malá písmena, bez diakritiky, bez markdown značek."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[`*_\[\]()]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def parse_sections(lines: list[str]) -> list[Section]:
    sections: list[Section] = []
    in_fence = False
    for i, line in enumerate(lines, 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
        m = None if in_fence else HEADING_RE.match(line)
        if m:
            sections.append(Section(len(m.group(1)), m.group(2), i))
    # Tělo sekce: od nadpisu po další nadpis stejné nebo vyšší úrovně (podsekce patří dovnitř).
    for idx, s in enumerate(sections):
        end = None
        for nxt in sections[idx + 1:]:
            if nxt.level <= s.level:
                end = nxt.line
                break
        s.body = lines[s.line:(end - 1) if end else len(lines)]
    return sections


def content_of(section: Section) -> str:
    out, in_fence = [], False
    for line in section.body:
        if FENCE_RE.match(line):
            in_fence = not in_fence
        if not in_fence and HEADING_RE.match(line):
            continue
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)         # komentáře ze šablony se nepočítají
    return text


def keyword_matches(keyword: str, heading: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(plain(keyword)), plain(heading)) is not None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=".github/pr-checks.toml")
    ap.add_argument("--readme", help="cesta k README (jinak z konfigurace)")
    ap.add_argument("--strict", action="store_true", help="varování také shodí kontrolu")
    args = ap.parse_args()

    cfg = load_config(args.config).get("readme", {})
    readme = Path(args.readme or cfg.get("path", "README.md"))
    required = cfg.get("sections", [])
    min_chars = int(cfg.get("min_content_chars", 40))
    placeholders = [plain(p) for p in cfg.get("placeholders", [])]

    if not required:
        die("V konfiguraci nejsou definované žádné povinné sekce ([[readme.sections]]).")
    if not readme.is_file():
        return report("Povinné sekce README",
                      [Finding("error", f"Soubor {readme} v repozitáři chybí.")], [])

    lines = readme.read_text(encoding="utf-8").splitlines()
    sections = parse_sections(lines)
    rel = readme.as_posix()

    findings: list[Finding] = []
    ok: list[str] = []

    for req in required:
        level = req.get("level", "error")
        title = req.get("title", req.get("id", "?"))
        source = req.get("source")
        hint = f" Požadavek: {source}." if source else ""
        # Nadpis 1. úrovně je název dokumentu, ne sekce, proto se nepočítá.
        matches = [s for s in sections
                   if s.level > 1 and any(keyword_matches(k, s.title) for k in req["keywords"])]

        if not matches:
            keywords = ", ".join(req["keywords"])
            findings.append(Finding(level,
                                    f"Chybí sekce „{title}“ (nadpis obsahující: {keywords}).{hint}", rel))
            continue

        # Stačí, když aspoň jeden odpovídající nadpis je vyplněný. Hlásí se první z nich.
        problem = None
        for sec in matches:
            body = content_of(sec)
            size = len(re.sub(r"\s", "", body))
            placeholder = next((p for p in placeholders
                                if re.search(r"(?<![a-z0-9])" + re.escape(p) + r"(?![a-z0-9])", plain(body))), None)
            if size < min_chars:
                problem = problem or Finding(level,
                    f"Sekce „{sec.title}“ ({title}) je prázdná nebo příliš krátká "
                    f"({size} znaků, minimum {min_chars}).{hint}", rel, sec.line)
            elif placeholder:
                problem = problem or Finding(level,
                    f"Sekce „{sec.title}“ ({title}) obsahuje zástupný text „{placeholder}“, "
                    f"není dokončená.", rel, sec.line)
            else:
                ok.append(f"{title}  →  „{sec.title}“ (ř. {sec.line})")
                problem = None
                break
        if problem:
            findings.append(problem)

    return report("Povinné sekce README", findings, ok, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
