# Data governance – Pražská doprava (DPP)

> Návrh pravidel pro správu dat, klasifikaci, ochranu osobních údajů (PII), správu tajemství, kvalitu dat a přístupy v Microsoft Fabric. Projekt používá vrstvy Bronze a Silver, povolené nástroje bez Sparku a sdílenou kapacitu F8.

## 1. Klasifikace datových sloupců

- **Osobní (PII):** údaje umožňující identifikaci osoby. Považují se za reálné PII; například jméno, příjmení, e-mail, adresa, datum narození, doklad, telefon nebo identifikátory cestujících a uživatelů.
- **Interní:** provozní data DPP a systémů, například ID případů kontrol, pohledávek, plateb, reklamací, vratek, vymáhání, podnětů, prodejů jízdenek, relací a událostí v aplikaci nebo jejich stavy.
- **Veřejné:** veřejná data a číselníky, například GTFS, zastávky PID, Golemio, Open-Meteo, svátky, ČSÚ a opendata.praha.eu.
- **Git workflow:** katalog, klasifikace a slovník se verzují v repozitáři (například v `docs/`). Změny se připravují ve větvi `dev` a přes Pull Request s code review se dostávají do `main`.

## 2. Ochrana osobních údajů a pseudonymizace

- **Bronze:** věrná kopie zdroje v režimu append-only s technickými sloupci `_source`, `_ingested_at`, `_run_id` a případně `_snapshot_date` a `_observed_at`. Přístup je omezen na oprávněné role.
- **Silver:** transformace probíhají v Python notebooku bez Sparku. Citlivé PII se pseudonymizuje (například hashováním se solí pro zachování vazeb mezi tabulkami), případně se omezí nebo zamaskuje tak, aby analytik citlivé osobní údaje neviděl.
- **Validace:** ověřuje se, že PII nejsou v Silver nekontrolovaně vystavené.

## 3. Správa tajemství a bezpečnost

- Hesla, API klíče, tokeny, connection stringy ani soli se neukládají do kódu, notebooků, parametrů pipeline ani Gitu.
- Tajemství se spravují prostřednictvím **Fabric connections** nebo **Azure Key Vault**.
- **AI asistenti:** jsou povoleni pouze mimo Fabric (v prohlížeči nebo editoru); Copilot přímo ve Fabricu je zakázán. Použití AI se zaznamená v `README.md` a tým odpovídá za výsledný kód.

## 4. Kvalita dat, logování a kapacita

- Bronze data nefiltruje, nečistí ani nemaže. Případné vynucené úpravy typů při načtení se zdokumentují. Deduplikace, kontrola typů a klíčů, logická a časová konzistence a karanténa vadných dat patří do Silver.
- Každý běh se loguje: čas, stav, počty řádků a chyby. Sleduje se čerstvost a úplnost podle SLO.
- Používají se pouze povolené nástroje: Copy job, pipeline, Python notebook bez Sparku a SQL analytics endpoint.
- Zakázané jsou Spark, Real-Time Intelligence, průběžné stahování a plány častější než jednou denně nebo spouštěné ve fázi TEST. Dodržuje se limit kapacity přibližně 5 % denně.

## 5. Role, přístupy a odpovědnosti

| Role | Workspace role / oprávnění | Bronze | Silver | Hlavní odpovědnost |
| --- | --- | --- | --- | --- |
| Data Engineer / Vývojář | Contributor / Member | Čtení a zápis | Čtení a zápis | Ingest, transformace v Pythonu a správa tabulek |
| DataOps & Governance | Member / Admin | Čtení (audit / DQ) | Čtení a metadata | DQ pravidla, logování, kapacita, oprávnění a katalog |
| Analytik DPP / Konzument | Viewer / SQL oprávnění | Bez přístupu | Pouze čtení (`SELECT`) | Dotazy nad vyčištěnými a pseudonymizovanými daty |

## 6. Dokumentace Silver

Pro vrstvu Silver se udržuje datový slovník, popisy v OneLake catalogu, lineage a datové kontrakty.
