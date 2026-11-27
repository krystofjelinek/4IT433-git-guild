# Git Guild — Data Engineering (4IT433)

Repozitář sdílí pravidla a šablony pro týmovou práci s GitHubem v předmětu Data Engineering. Obsahuje také návrh pravidel Data governance pro projekt Pražská doprava (DPP) v Microsoft Fabric.

## Stav

| Milník | Stav | Poznámka |
|---|---|---|
| Pravidla práce s Gitem | ✅ | Základní workflow je popsáno níže a v dokumentaci v `standards/`. |
| Data governance – DPP | ✅ | Návrh pravidel je v [`standards/data_governance.md`](standards/data_governance.md). |

## Prostředí

| Položka | Hodnota |
|---|---|
| Platforma | GitHub |
| Git větev pro vývoj | `dev` |
| Hlavní větev | `main` (změny pouze přes Pull Request) |
| Pravidla a šablony | `standards/`, `templates/` |

## Architektura

Tento repozitář slouží jako dokumentační a metodická podpora pro týmovou práci. Neobsahuje implementaci datových pipeline ani Fabric workspace artefakty.

```text
README.md
standards/   pravidla a standardy
templates/   opakovaně použitelné šablony
```

## Konvence

| Co | Pravidlo | Příklad |
|---|---|---|
| Dokumentace | Markdown (`.md`) | `standards/pr_checks.md` |
| Názvy souborů | Výstižné, malá písmena, podtržítka dle potřeby | `data_governance.md` |
| Commit | Stručně popsat změnu; doporučený formát je v [pravidlech commitů](standards/commit.md) | `docs: doplnění pravidel` |
| Pull Request | Změny připravit ve větvi `dev`; do `main` přes Pull Request a code review | `dev` → `main` |

## Struktura repozitáře

```text
standards/
  commit.md
  data_governance.md
  pr_checks.md
  table_names_and_README.md
templates/
  README_template.md
README.md
```

## Kvalita dokumentace

- Dokumenty ukládají pravidla a rozhodnutí přehledně v Markdownu.
- Změny pravidel se verzují v Gitu a procházejí code review přes Pull Request.
- Projektová README vycházejí ze [šablony README](templates/README_template.md).

## Jak přispívat

1. Změny připravte ve větvi `dev`.
2. Otevřete Pull Request do `main`.
3. Zajistěte code review jiným členem týmu; po schválení lze změnu sloučit.

## Bezpečnost a přístupy

Pro pravidla klasifikace dat, ochrany PII, pseudonymizace a správy tajemství v projektu DPP viz [Data governance](standards/data_governance.md).

## Známá omezení a otevřené úlohy

- Informace specifické pro jednotlivé týmové projekty (workspace, členové, zdroje a průběh milníků) patří do jejich projektového README.

## Tým a kontakt

Repozitář spravuje Git Guild pro předmět 4IT433. S dotazy se obraťte na [Teams kanál Git Guild](https://teams.cloud.microsoft/l/channel/19%3Ab183a764649b45c7bd96fc0870ef1004%40thread.tacv2/Odpoledni_Git%2C%20CI%2CCD%20a%20governance?groupId=f42500c7-8406-4492-82b1-2528e81665cb&tenantId=2b51a4b3-443f-4406-8ca4-19056a79a444).
