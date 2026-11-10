## 📌 Popis změn
<!-- Stručně shrňte, co tento PR řeší, jaké vrstvy nebo notebooků se týká a proč. -->
- **Typ změny:** 
  - [ ] Ingest / Nový datový zdroj
  - [ ] Bronze vrstva
  - [ ] Silver transformace / DQ
  - [ ] CI/CD, správa repozitáře, dokumentace
- **Dotčené tabulky / položky ve Fabricu:** (např. `bronze_cestujici`, `silver_prepravni_kontrola`)

## 🎯 Cíl a kontext
<!-- Odkaz na issue, úkol z milníku nebo byznys otázku DPP, kterou toto řešení podporuje. -->

---

## 🔍 Checklist pro autora před předáním k review
- [ ] Větev směřuje z `dev` do `main` (nebo z feature větve do `dev`).
- [ ] Kód **neobsahuje žádná tajemství** (API tokeny, hesla, connection stringy) – jsou využity Fabric Connections / Azure Key Vault[cite: 1, 3].
- [ ] V commitu jsou **pouze definice a kód** (notebooky, konfigurace pipeline, JSON definice položek), **žádná surová ani zpracovaná data**[cite: 2, 3].
- [ ] Názvy tabulek dodržují konvence: malá písmena s prefixem vrstvy (`bronze_*`, `silver_*`)[cite: 2, 3].
- [ ] README.md bylo aktualizováno (zdokumentovaná pravidla čištění, srovnání počtu řádků, licence externích zdrojů)[cite: 1, 2].

---

## 📋 Checklist pro reviewera (Peer Review)
*Reviewer musí před schválením projít následující body. Reviewer nesmí být autor PR.*

### 1. Architektura a vrstvy (Data Engineering)
- [ ] **Bronze vrstva:** Data jsou 1:1 se zdrojem, append-only, obsahují technický sloupec `_loaded_at` (příp. `_source`, `_run_id`)[cite: 1, 2].
- [ ] **Silver vrstva:** Sloupce jsou ve formátu `snake_case`, správně otypované (datum, decimal), ošetřeny nekorektní hodnoty a je zachována historie (SCD2/snapshot) dle potřeby[cite: 1, 2].
- [ ] **Idempotence & Duplicity:** Běh notebooku/pipeline je opakovatelný bez vzniku duplicitních záznamů[cite: 1, 2, 3].
- [ ] **Kapacita a výkon:** Kód zbytečně neplýtvá Fabric kapacitou (odfiltrování zbytečných dat, přiměřená velikost clusteru/session, absence nekonečných smyček či real-time streamingu).

### 2. Bezpečnost a Governance
- [ ] **Osobní údaje:** Citlivé sloupce (jména, rodná čísla, adresy, doklady) jsou v Silver vrstvě pseudonymizované nebo maskované[cite: 1, 3].
- [ ] **API limity:** Volání externích API (Golemio, Open-Meteo apod.) respektuje limity volání a ukládá surové odpovědi do `Files`[cite: 1, 3].

### 3. Kód a Git hygiena
- [ ] Commit zprávy jsou srozumitelné a odpovídají konvenci týmu (např. `bronze: načtení tabulky CESTUJICI`)[cite: 2, 3].
- [ ] Kód notebooku je čistý, bez ladicích ad-hoc výpisů celých tabulek a mrtvého kódu.

---

## 💬 Poznámky a závěr reviewera
<!-- Zde reviewer popíše případné výhrady nebo doporučení k optimalizaci. -->
