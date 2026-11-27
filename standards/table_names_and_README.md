# T8 · Kontroly v GitHub Actions: názvy tabulek a povinné sekce README

Část standardu guildy Git, CI/CD a governance. Obě kontroly běží při každém Pull Requestu do `main` jako kroky workflow `.github/workflows/pr-checks.yml`. Kontrolují jen kód v repozitáři, data v lakehouse nevidí.

Pravidla jsou v jednom konfiguračním souboru `.github/pr-checks.toml`. Změnu pravidel navrhuje kdokoli Pull Requestem, rozhoduje guilda.

## 1. Názvy tabulek

**Skript:** `.github/scripts/check_table_names.py`

**Co se kontroluje.** Všechny notebooky ve složce `fabric/` (soubory `notebook-content.py`). Skript najde každé místo, kde notebook vytváří nebo zapisuje tabulku:

| Zápis | Příklad |
|---|---|
| PySpark | `.saveAsTable("bronze_platba")`, `.toTable(...)`, `.tableName(...)` |
| Zápis do složky Tables | `.save("Tables/bronze_platba")` |
| SQL v Pythonu | `spark.sql("CREATE TABLE bronze_platba ...")` |
| SQL buňka | `CREATE [OR REPLACE] TABLE ...`, `CREATE MATERIALIZED LAKE VIEW ...` |

**Pravidla.**

1. Název začíná prefixem vrstvy: `bronze_`, `silver_`. Prefix `log_` pro technické tabulky (log běhů) je návrh, o kterém rozhodne guilda.
2. Název obsahuje jen malá písmena, číslice a podtržítka.
3. Schéma a lakehouse v názvu se ignorují: `lh_team_25.dbo.silver_platba` se posuzuje jako `silver_platba`.

**Jak se vyhodnocuje název v proměnné.** Kontrola je statická, notebook se nespouští.

| V kódu | Výsledek |
|---|---|
| `"silver_platba"` | ověří se celý název |
| `f"silver_{name}"` | ověří se pevný začátek `silver_` |
| `target = f"bronze_{t}"` a pak `saveAsTable(target)` | skript dohledá přiřazení ve stejném souboru |
| `saveAsTable(table_name)`, kde `table_name` je parametr funkce | nejde ověřit, **varování** |

Doporučení pro squady: název tabulky vždy skládejte jako řetězec nebo f-string, který začíná prefixem vrstvy. Pak ho kontrola umí ověřit.

**Výjimka.** Pokud tabulka z dobrého důvodu prefix mít nemůže, napište na stejný nebo předchozí řádek komentář s důvodem:

```python
# allow-table-name: sdílený číselník kurzu, schváleno guildou 12. 11. 2026
df.write.saveAsTable("kurz_ciselnik")
```

V SQL buňce `-- allow-table-name: důvod`. Výjimka bez důvodu je chyba. Podle pravidel guildy musí odchylku schválit guilda a squad ji uvede v README.

## 2. Povinné sekce README

**Skript:** `.github/scripts/check_readme_sections.py`

**Co se kontroluje.** Soubor `README.md` v kořeni repozitáře musí mít všechny povinné sekce a každá musí být vyplněná.

**Kdy je sekce splněná.**

1. Existuje nadpis 2. až 6. úrovně, který obsahuje některé z klíčových slov sekce. Velikost písmen a diakritika nehrají roli, takže `Licence zdrojů`, `licence zdroju` i `Datové zdroje` projdou. Nadpis 1. úrovně je název dokumentu a nepočítá se.
2. Pod nadpisem (včetně podsekcí) je aspoň 40 znaků obsahu.
3. Obsah není jen zástupný text: `TODO`, `TBD`, `doplnit`, `doplníme`, `lorem ipsum`.

Jeden nadpis může pokrýt více sekcí, například „Licence zdrojů a použití AI“. Nadpisy uvnitř bloků kódu a komentáře `<!-- -->` ze šablony se nepočítají.

**Povinné sekce.** Seznam vychází ze zadání projektu a milníku 1 a sladí se se šablonou README od T7.

| Sekce | Úroveň | Odkud požadavek je |
|---|---|---|
| Tým a role | chyba | Zadání: Organizace týmu a role |
| Architektura a struktura workspace | chyba | Zadání: výstupy role Tech lead |
| Konvence pojmenování | varování | Zadání: výstupy role Tech lead |
| Datové zdroje a licence | chyba | Pravidla: licence a odkaz u každého zdroje |
| Ingest a Bronze | chyba | Zadání: Architektura a požadované výstupy |
| Kontrola počtů řádků zdroj a Bronze | chyba | Milník 1, úkol 3 |
| Silver a pravidla čištění | chyba | Milník 1, úkol 4 |
| Kvalita dat (DQ) | chyba | Zadání: DQ pravidla s karanténou |
| Průběžný sběr dat a zdůvodnění kapacity | varování | Zadání: Průběžný sběr dat |
| Osobní údaje a pseudonymizace | varování | Pravidla: Osobní údaje |
| Použití AI asistentů | chyba | Pravidla: AI asistenti |

**Úroveň.** *Chyba* shodí kontrolu. *Varování* se zobrazí v PR, ale kontrolu neshodí. Varování mají sekce pro pozdější milníky; guilda je postupně přepne na chybu.

## Výstup v Pull Requestu

Obě kontroly:

* zapíšou chyby přímo k řádku souboru v záložce *Files changed* (anotace),
* do souhrnu běhu (*Summary*) přidají tabulku s výsledkem,
* skončí s kódem 1, pokud najdou chybu. Varování kontrolu neshodí, pokud v konfiguraci není `strict = true` nebo se skript nespustí s `--strict`.

## Spuštění lokálně

Z kořene repozitáře, stačí Python 3.11 nebo novější, žádné knihovny:

```bash
python .github/scripts/check_table_names.py
python .github/scripts/check_readme_sections.py
```

## Známá omezení

* Kontrola nevidí data, jen kód. Že tabulka v lakehouse opravdu existuje se správným názvem, musí ověřit notebook ve Fabricu.
* Názvy skládané mimo soubor (parametr pipeline, výsledek funkce) nejde staticky ověřit, proto jsou jen varování.
* Pokud notebook obsahuje syntaktickou chybu, ověří se názvy jen zjednodušeně. Chybu samotnou zachytí lint (Ruff).
