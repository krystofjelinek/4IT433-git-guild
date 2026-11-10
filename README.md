# 4IT433-git-guild
Repo used for sharing methodology of work with Git during 4IT433 course

# Konvence pro commity

## Základní formát

```text
<typ>[volitelný rozsah][!]: <stručný popis>

[volitelné tělo zprávy]

[volitelné patičky]
```

- **Typ** určuje druh změny.
- **Rozsah (scope)** upřesňuje část projektu, například `auth`, `api` nebo `ui`.
- **Popis** stručně vystihuje změnu.
- **Tělo** může vysvětlit důvod a kontext změny.
- **Patičky** mohou obsahovat reference na úkoly a informace o nekompatibilních změnách.

Příklad:

```text
feat(auth): přidání přihlášení pomocí Google

Uživatelé se nyní mohou přihlásit pomocí svého Google účtu.
```

## Typy commitů

Specifikace přímo definuje typy `feat` a `fix`. Další typy jsou rozšířenou týmovou konvencí.

| Typ | Význam | Použití |
| --- | --- | --- |
| `feat` | Nová funkce | Přidání funkcionality |
| `fix` | Oprava chyby | Oprava nesprávného chování |
| `docs` | Dokumentace | README, návody a dokumentace |
| `style` | Formátování | Odsazení, mezery, formátování bez změny chování |
| `refactor` | Refaktoring | Změna struktury bez změny chování |
| `perf` | Výkon | Optimalizace výkonu |
| `test` | Testy | Přidání a úpravy testů |
| `build` | Sestavení | Závislosti a build nástroje |
| `ci` | CI/CD | Pipeline a automatizace |
| `chore` | Údržba | Rutinní technické změny |
| `revert` | Vrácení změny | Vrácení dřívějšího commitu |

## Příklady v češtině

```text
feat(auth): přidání dvoufaktorového ověřování
fix(api): oprava chybného zpracování odpovědi
docs(readme): aktualizace instalačního návodu
style(ui): sjednocení formátování komponent
refactor(user): zjednodušení validace uživatele
perf(db): optimalizace databázových dotazů
test(auth): doplnění testů přihlašování
build(deps): aktualizace závislostí
ci(github): přidání automatického spouštění testů
chore(config): odstranění nepoužívaných nastavení
revert: vrácení změny přihlašovacího formuláře
```

## Nekompatibilní změny (BREAKING CHANGE)

Změnu narušující zpětnou kompatibilitu označte `!` bezprostředně před dvojtečkou nebo patičkou `BREAKING CHANGE:`. Obě možnosti lze kombinovat.

```text
feat(api)!: odstranění zastaralého endpointu
```

Podrobnější příklad:

```text
feat(api): změna struktury odpovědi uživatele

Odpověď API nyní používá objekt profile místo původních polí.

BREAKING CHANGE: klienti musí upravit zpracování odpovědi endpointu /users.
```

Patička `BREAKING CHANGE:` musí být napsána přesně tímto způsobem. Lze použít také `BREAKING-CHANGE:` jako token patičky podle pravidel specifikace.

## Verzování podle SemVer

| Změna | Navýšení verze | Příklad |
| --- | --- | --- |
| `fix` | PATCH | `1.2.3` → `1.2.4` |
| `feat` | MINOR | `1.2.3` → `1.3.0` |
| `BREAKING CHANGE` | MAJOR | `1.2.3` → `2.0.0` |

Poznámka: u verzí `0.x.y` může být způsob verzování odlišný. Automatické vydávání verzí závisí na nástrojích projektu.

## Doporučená týmová pravidla

1. Každá commit zpráva začíná typem, například `feat:` nebo `fix:`.
2. Typy a názvy oblastí ponecháváme v angličtině, popisy píšeme česky.
3. Rozsah uvádíme, pokud pomáhá určit dotčenou část projektu.
4. Jeden commit představuje jednu logickou změnu.
5. Popis je konkrétní: nepoužíváme jen `opravy`, `update`, `změny` nebo `hotovo`.
6. U složitějších změn přidáváme tělo vysvětlující **co** a **proč**.
7. Nekompatibilní změny označujeme `!` nebo patičkou `BREAKING CHANGE:`.
8. Typy zapisujeme malými písmeny; konzistenci názvů oblastí stanoví tým.
9. Za prefixem a dvojtečkou následuje jedna mezera.
10. Prázdný řádek odděluje hlavičku od těla a tělo od patiček.

## Šablona k použití

```text
<typ>(<oblast>): <stručný popis>

<co se změnilo a proč – nepovinné>

Refs: #123
```

Příklad s referencí na úkol:

```text
fix(cart): oprava výpočtu ceny po slevě

Při kombinaci procentní a pevné slevy docházelo k chybnému zaokrouhlení.

Refs: #123
```

`Refs: #123` je volitelná týmová konvence; není povinnou součástí Conventional Commits.

## Rychlý tahák

- Nová funkce → `feat`
- Oprava chyby → `fix`
- Dokumentace → `docs`
- Refaktoring → `refactor`
- Výkon → `perf`
- Testy → `test`
- Údržba → `chore`
- Nekompatibilní změna → `!` nebo `BREAKING CHANGE:`

---

**Zdroj:** [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). Dokument kombinuje požadavky specifikace a doporučené týmové postupy.

