# <Název projektu> — tým XX

Jedna až dvě věty: co projekt dělá, pro koho a v jakém nástroji.

## Stav

| Milník | Stav | Poznámka |
|---|---|---|
| 1 – <název milníku> | ✅ / 🟡 / ⬜ | |
| 2 – … | ⬜ | |

## Prostředí

| Položka | Hodnota |
|---|---|
| Workspace (DEV) | `<workspace>` |
| Lakehouse | `lh_team_XX` |
| Zdroj (workspace / databáze / schéma) | `<workspace>` / `<databáze>` / `<schéma>` |
| Git větev pro vývoj | `dev` (do `main` jen přes Pull Request) |
| Složka ve repozitáři | `fabric/` |

## Architektura

```
<zdroj>          ──pl_bronze_load──▶ bronze_* ──nb_silver_transform──▶ silver_*
                                         │                                 │
                                         └────────── ops_run_log ◀─────────┘
```

Krátce: proč tento nástroj (pipeline / notebook) a proč tento režim zápisu.

## Konvence

| Co | Pravidlo | Příklad |
|---|---|---|
| Notebook | `nb_<vrstva>_<akce>` | `nb_silver_transform` |
| Pipeline | `pl_<vrstva>_<akce>` | `pl_bronze_load` |
| Tabulka | `<vrstva>_<zdroj>`, malá písmena | `bronze_orders`, `silver_orders` |
| Provozní tabulka | `ops_<co>` | `ops_run_log` |
| Sloupec | malá písmena, podtržítka | `order_id` |
| Technický sloupec | začíná `_`, časy v UTC | `_loaded_at` |
| Commit | `<vrstva>: <co se změnilo>` | `bronze: načtení všech tabulek` |

### Technické sloupce

| Sloupec | Vrstva | Význam |
|---|---|---|
| `_loaded_at` | Bronze (přenáší se do Silver) | Čas načtení ze zdroje (UTC) |
| `_processed_at` | Silver | Čas zpracování do Silver (UTC) |
| `_run_id` | Silver | ID běhu, spojuje řádek se záznamem v `ops_run_log` |
| `_source_table` | Silver | Tabulka, ze které řádek vznikl |

## Struktura repozitáře

```
fabric/
  lh_team_XX.Lakehouse/
  pl_bronze_load.DataPipeline/
  nb_bronze_validation.Notebook/
  nb_silver_transform.Notebook/
README.md
```

Osobní pokusy a ukázky z hodin nepatří do `fabric/` ve větvi `dev`.

## Bronze – načtení

- **Zdroj:** …
- **Nástroj:** pipeline / notebook a proč.
- **Režim:** full load, Overwrite. Opakované spuštění nevytvoří duplicity, protože …
- **Úpravy:** žádné, jen `_loaded_at`.
- **Výjimky:** technické převody typů (např. `time` → text) s důvodem.

### Kontrola počtů

Spočítáno v notebooku `nb_bronze_validation`, datum: …

| Zdrojová tabulka | Bronze tabulka | Počet ve zdroji | Počet v Bronze | Rozdíl |
|---|---|---:|---:|---:|
| | | | | |

## Silver – pravidla čištění

Společná pravidla (platí pro všechny tabulky):
- názvy sloupců malými písmeny s podtržítky,
- data jako `date` / `timestamp`, částky jako `decimal(p,s)`,
- řádky se nemažou potichu; při chybě notebook skončí chybou.

Pravidla po tabulkách:

| Tabulka | Klíč | Převody typů | Chybějící hodnoty | Duplicity | Nesmyslné hodnoty |
|---|---|---|---|---|---|
| `silver_<tabulka>` | `<klíč>` | … | co se našlo → rozhodnutí | … | … |

## Kvalita dat a logování

- Každý běh notebooku zapíše řádek za tabulku do `ops_run_log`
  (run_id, tabulka, stav, počty řádků, čas, chyba).
- Kontroly kvality, které běží: …
- Kde najít poslední běh:
  ```sql
  SELECT TOP 20 * FROM dbo.ops_run_log ORDER BY started_at DESC;
  ```

## Jak spustit

1. …
2. Parametry notebooku:

| Parametr | Výchozí | Význam |
|---|---|---|
| `lakehouse_name` | `lh_team_XX` | Cílový lakehouse |
| `tables` | prázdné = všechny | Seznam tabulek oddělený čárkou |
| `run_id` | z pipeline | ID běhu |
| `dry_run` | `False` | Jen kontrola, bez zápisu |

## Bezpečnost a přístupy

- V kódu nejsou žádné tajné údaje ani ID prostředí. Tajné klíče jsou v Azure Key Vault.
- Osobní údaje: které sloupce, jak se s nimi zachází.
- Kdo má jakou roli ve workspace.

## Git workflow

- Fabric commituje do `dev` přes panel Source control.
- Do `main` jen přes Pull Request z `dev`, schvaluje jiný člen týmu než autor.

## Známá omezení a otevřené úlohy

- …

## Tým

| Role | Člen |
|---|---|
| Tech lead (architektura, konvence, review) | |
| Ingest interních dat | |
| Ingest externích dat | |
| Silver (čištění, datový slovník) | |
| DataOps a governance | |

## Použití AI

Které nástroje, k čemu, a že výsledky tým ověřil.
