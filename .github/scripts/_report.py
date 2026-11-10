"""Společné hlášení výsledků pro kontroly T8.

Lokálně vypisuje čitelný text. V GitHub Actions navíc:
  * vytvoří anotace (::error / ::warning), které se zobrazí přímo u řádku v PR,
  * zapíše tabulku do souhrnu běhu (GITHUB_STEP_SUMMARY).
"""
import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"


@dataclass
class Finding:
    level: str          # "error" | "warning"
    message: str
    file: str | None = None
    line: int | None = None


def load_config(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _escape(text: str) -> str:
    # Escapování podle GitHub workflow commands.
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def report(title: str, findings: list[Finding], ok_lines: list[str], strict: bool = False) -> int:
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    print(f"== {title} ==")
    for line in ok_lines:
        print(f"  OK    {line}")
    for f in findings:
        where = f"{f.file}:{f.line}" if f.file and f.line else (f.file or "")
        tag = "CHYBA" if f.level == "error" else "POZOR"
        print(f"  {tag} {where}  {f.message}" if where else f"  {tag} {f.message}")
        if IN_ACTIONS:
            props = []
            if f.file:
                props.append(f"file={f.file}")
            if f.line:
                props.append(f"line={f.line}")
            props.append(f"title={title}")
            print(f"::{f.level} {','.join(props)}::{_escape(f.message)}")

    failed = bool(errors) or (strict and bool(warnings))
    verdict = "NEPROŠLO" if failed else "PROŠLO"
    print(f"\n{verdict}: {len(errors)} chyb, {len(warnings)} varování\n")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as s:
            icon = "❌" if failed else "✅"
            s.write(f"### {icon} {title}\n\n")
            s.write(f"{len(errors)} chyb, {len(warnings)} varování, {len(ok_lines)} v pořádku\n\n")
            if findings:
                s.write("| Úroveň | Kde | Zjištění |\n|---|---|---|\n")
                for f in findings:
                    where = f"`{f.file}:{f.line}`" if f.file and f.line else (f"`{f.file}`" if f.file else "")
                    lvl = "chyba" if f.level == "error" else "varování"
                    s.write(f"| {lvl} | {where} | {f.message.replace('|', '/')} |\n")
                s.write("\n")
            if ok_lines:
                s.write("<details><summary>V pořádku</summary>\n\n")
                for line in ok_lines:
                    s.write(f"- {line}\n")
                s.write("\n</details>\n\n")

    return 1 if failed else 0


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def die(msg: str) -> None:
    print(f"CHYBA: {msg}", file=sys.stderr)
    sys.exit(2)
