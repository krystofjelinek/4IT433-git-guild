# T8 · Automatické kontroly Pull Requestů (GitHub Actions)

Při každém Pull Requestu do `main` spustí workflow `.github/workflows/pr-checks.yml` čtyři kontroly. Každá se v PR ukáže jako samostatný řádek, takže je hned vidět, co neprošlo.

| Kontrola | Nástroj | Co hlídá | Neprojde, když |
|---|---|---|---|
| Gitleaks | [gitleaks-action](https://github.com/gitleaks/gitleaks-action) | API klíče, tokeny a hesla v kódu i v historii commitů v PR | najde tajný údaj |
| Ruff (lint notebooků) | [Ruff](https://docs.astral.sh/ruff/) | Python a PySpark v `fabric/**/notebook-content.py` | syntaktická chyba, nedefinovaný nebo nepoužitý název |
| Názvy tabulek | `.github/scripts/check_table_names.py` | prefix vrstvy `bronze_`/`silver_` a tvar názvu | viz [standard názvů tabulek a sekcí README](table_names_and_README.md) |
| Povinné sekce README | `.github/scripts/check_readme_sections.py` | že README má všechny povinné sekce a jsou vyplněné | viz [standard názvů tabulek a sekcí README](table_names_and_README.md) |

Ruff, názvy tabulek a README běží jen v repozitáři squadu, tedy tam, kde je složka `fabric/`. V repozitáři guildy se přeskočí a běží jen Gitleaks.

## Ruff

Nastavení je v `.github/ruff.toml`. Používáme výchozí pravidla Ruffu (`E4`, `E7`, `E9`, `F`), délku řádku nehlídáme.

Fabric v notebooku sám vytvoří objekty `spark`, `sc`, `notebookutils`, `mssparkutils` a `display`. Ruff je proto bere jako vestavěné a nehlásí je jako nedefinované.

Lokálně si kontrolu spustíte z kořene repozitáře:

```bash
pip install ruff
ruff check fabric --config .github/ruff.toml
```

Nepoužitý import opraví `ruff check fabric --config .github/ruff.toml --fix`. Pokud je řádek v pořádku a Ruff se mýlí, přidejte na jeho konec `# noqa: <kód>`, například `# noqa: F401`.

## Jak kontroly zapnout v repozitáři squadu

1. Zkopírujte z repozitáře guildy do svého repozitáře, do větve `dev`:
   - `.github/workflows/pr-checks.yml`
   - `.github/pr-checks.toml`
   - `.github/ruff.toml`
   - celou složku `.github/scripts/`
2. Změnu dejte do `main` přes Pull Request. Kontroly se spustí už na tomto PR.
3. Správce repozitáře v **Settings → Branches → Branch protection rule** pro `main` zapne *Require status checks to pass before merging* a vybere všechny čtyři kontroly. Bez toho jde PR sloučit, i když kontrola neprošla.

Na `.github/` smí sahat jen správce repozitáře, proto kroky 1 a 3 dělá on.

## Ukázka

Ukázkový repozitář squadu: [davidmalasek/t8-pr-checks-demo](https://github.com/davidmalasek/t8-pr-checks-demo).

- [PR #1](https://github.com/davidmalasek/t8-pr-checks-demo/pull/1) přidá silver tabulku se správným názvem, všechny kontroly projdou.
- [PR #2](https://github.com/davidmalasek/t8-pr-checks-demo/pull/2) přidá tabulku `ZastavkyCiste`, nepoužitý import a smaže z README sekci o AI. Neprojdou Ruff, názvy tabulek ani README, Gitleaks projde.
