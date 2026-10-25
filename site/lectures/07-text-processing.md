---
title: 7. Text processing
---

# 7. Text processing

<div class="lecture-meta">
  <span>Session 7</span><span>practice: <code>07-text-processing/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- change the case of text and remove extra spaces - the Python `UPCASE`, `PROPCASE`,
  `STRIP` and `COMPBL`;
- find and test parts of a string, and check what kind of characters it has;
- split a line into fields and join fields into a line - `SCAN` and `CATX`;
- replace and remove characters - `TRANWRD` and `COMPRESS`;
- pad codes with zeros and align text in columns;
- clean real identifiers: client ids, company names, EIKs, IBANs, e-mails, city
  names;
- read numbers written the Bulgarian way (`1 234 567,89`), and dates written in
  different formats, with `datetime`.

From SAS to Python - the same cleaning step, two ways:

```sas
data clean;
    set register;
    client_id = upcase(compress(client_id, ' -'));
    name      = propcase(compbl(strip(name)));
    city      = propcase(strip(tranwrd(city, 'gr. ', '')));
run;
```

```python run
import csv

with open("data/client_register.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

for row in rows[12:16]:
    client_id = row["client_id"].replace(" ", "").replace("-", "").upper()
    name = " ".join(row["name"].split()).title()
    city = row["city"].strip().removeprefix("gr. ").title()
    print(f"{row['client_id']!r:>10} -> {client_id:<6} | {name:<22} | {city}")
```

The file `client_register.csv` is new today: the 150 clients of the sample data,
with their text fields typed by many people over many years. It is made up, but the
problems in it are real ones.

## 1. Strings: a recap and the new data

You know from session 1 and 3: a string is a **sequence** of characters; `len(s)`,
`s[0]`, `s[-1]`, `s[2:5]` work like on a list; `s[2:5]` is `SUBSTR(s, 3, 3)`. And a
string **cannot change** (it is immutable): every method returns a **new** string.

```python run
client_id = " c0014 "

client_id.strip()               # a new string - but nobody keeps it
print(repr(client_id))          # unchanged!

client_id = client_id.strip()   # keep the result
print(repr(client_id))
```

This is the most common mistake of today: a method call without `=`. `repr()` (or
`!r` in an f-string) shows the quotes, so you can see the spaces.

The columns of the new file:

```python run
import csv

with open("data/client_register.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

print(len(rows), "rows; columns:", list(rows[0]))
for row in rows[1:4]:
    print(row)
```

| Column | What is wrong in it |
|---|---|
| `client_id` | lower case, spaces, `-`, missing zeros: `c0014`, `C 0009`, `C-0026`, `C17` |
| `name` | case, extra spaces, quotes, legal forms written as `E.A.D.` |
| `eik` | spaces inside, a `BG` prefix (the VAT number), 9 or 13 digits |
| `iban` | groups of 4 with spaces, lower case, empty |
| `email` | upper case, spaces, `" at "` instead of `@` |
| `city` | case, spaces, `gr. ` in front, Cyrillic |
| `registered` | four date formats |
| `turnover` | Bulgarian and English number formats, `EUR` in front |

## 2. Case and spaces

### Upper, lower, title

```python run
name = "blue Wines eood"

print(name.upper())          # UPCASE
print(name.lower())          # LOWCASE
print(name.title())          # PROPCASE: every word with a capital
print(name.capitalize())     # only the first letter of the string
```

| SAS | SQL | Python |
|---|---|---|
| `UPCASE(s)` | `UPPER(s)` | `s.upper()` |
| `LOWCASE(s)` | `LOWER(s)` | `s.lower()` |
| `PROPCASE(s)` | `INITCAP(s)` (Oracle, PostgreSQL) | `s.title()` |

Compare text without case: lower (or upper) **both** sides:

```python run
city = "SOFIA"
print(city == "Sofia")
print(city.lower() == "sofia")
```

::: warning `title()` is not clever
`title()` gives a capital after **every** non-letter, and it does not know legal
forms or abbreviations:

```python run
print("blue wines eood".title())      # 'Blue Wines Eood' - should be EOOD
print("o'neil trade".title())         # "O'Neil Trade" - fine here
print("2nd floor".title())            # '2Nd Floor'
```

Fix the known words after `title()` (section 7).
:::

::: details Advanced: `casefold()`
For comparing text in any language, `casefold()` is stronger than `lower()`: the
German `"Straße".casefold()` is `"strasse"`. For Bulgarian and English, `lower()` is
enough.
:::

### Remove spaces: `strip`

`strip()` removes spaces (and tabs and new lines) at **both ends**; `lstrip()` only
at the start, `rstrip()` only at the end:

```python run
city = "  ruse "

print(repr(city.strip()))       # STRIP
print(repr(city.lstrip()))      # LEFT
print(repr(city.rstrip()))      # TRIM (SAS), RTRIM (SQL)
```

With an argument, `strip` removes **those characters** from the ends (any of them,
in any order) - not a word:

```python run
print("**12.50**".strip("*"))
print('"North Hotels"'.strip('"'))
print("0001200".lstrip("0"))
print("www.example.com".strip("w.com"))      # careful: characters, not a word!
```

### Spaces inside: `COMPBL`

`strip` does not touch the spaces **inside**. `split()` without an argument splits
on any run of spaces, and `" ".join(...)` puts the words back with one space:

```python run
name = "  Iron   Retail  ET "

print(repr(name.strip()))
print(repr(" ".join(name.split())))        # COMPBL(STRIP(name))
```

`" ".join(s.split())` is the standard Python idiom for "remove all extra spaces".
Section 4 explains `split` and `join`.

::: tip Try it
Clean `"  GREEN   build  eood "` into `"Green Build EOOD"`. You need `split`,
`join`, `title`, and one more step for the legal form. (Hint: `s[:-4] + "EOOD"`
works when you know the last word; section 7 does it properly.)
:::

## 3. Find and test

### Is it in there?

```python run
comment = "Payment of 1 250,00 EUR received on 15.09.2026."

print("EUR" in comment)                        # INDEX(comment, 'EUR') > 0
print(comment.startswith("Payment"))           # LIKE 'Payment%'
print(comment.endswith("."))                   # LIKE '%.'
print("eur" in comment)                        # case matters
print("eur" in comment.lower())
```

`startswith` and `endswith` take a **tuple** of options:

```python run
loan_ids = ["L000001", "C0002", "L000003", "X1"]
print([x for x in loan_ids if x.startswith(("L", "C"))])

files = ["loans.csv", "clients.CSV", "report.xlsx"]
print([f for f in files if f.lower().endswith((".csv", ".xlsx"))])
```

### Where is it? `find` and `index`

`find` gives the position of the first match, or **-1** if there is none. `index`
does the same, but a missing value is an **error**:

```python run
comment = "Payment of 1 250,00 EUR received on 15.09.2026."

print(comment.find("EUR"))           # the position (from 0)
print(comment.find("USD"))           # -1: not found
print(comment.rfind("e"))            # from the right
print(comment.count("0"))            # how many times
print(comment.index("USD"))          # ValueError: substring not found
```

SAS `INDEX` and `FIND` count from **1** and give **0** when nothing is found; Python
counts from 0 and gives -1. A classic bug: `if s.find("x"):` is true for -1 and false
when `"x"` is at position 0. Use `in` for "is it there?".

With a position you can cut: the text after `"on "`:

```python run
comment = "Payment of 1 250,00 EUR received on 15.09.2026."

start = comment.find(" on ") + len(" on ")
print(comment[start:start + 10])
```

(Session 8 does this kind of extraction with regular expressions - shorter and
safer.)

### What kind of characters?

These methods return `True` if **all** characters are of a kind (and the string is
not empty):

```python run
for s in ["131234567", "12O.50", "EUR", "BG80", "", "  "]:
    print(f"{s!r:<12} digit={s.isdigit()!s:<6} alpha={s.isalpha()!s:<6} "
          f"alnum={s.isalnum()!s:<6} space={s.isspace()}")
```

| SAS | Python |
|---|---|
| `NOTDIGIT(s) = 0` | `s.isdigit()` |
| `ANYDIGIT(s) > 0` | `any(c.isdigit() for c in s)` |
| `NOTALPHA(s) = 0` | `s.isalpha()` |
| `COUNTC(s, '0')` | `s.count("0")` |

Check an id by its parts - "an L and six digits":

```python run
def is_loan_id(s):
    return len(s) == 7 and s[0] == "L" and s[1:].isdigit()

print([is_loan_id(x) for x in ["L000001", "L00001", "l000001", "L00000A", "L999999"]])
```

::: warning `isdigit` is not "is a number"
`"12.50".isdigit()` and `"-5".isdigit()` are `False` - a point and a minus are not
digits. Use `isdigit` for ids and codes; for numbers, convert with `float()` (section
8).
:::

::: tip Try it
Write `is_client_id(s)`: `"C"` and four digits. Test it on `"C0001"`, `"c0001"`,
`"C001"`, `"C00010"`. Then change it to accept a lower-case `c` too.
:::

## 4. Split and join

### `split`: a line into fields

```python run
line = "L000002,C0132,investment,EUR,2019-04-16"
fields = line.split(",")
print(fields)
print(fields[2])                  # SCAN(line, 3, ',')
```

Two kinds of `split`:

- `split(",")` with a separator: **every** comma splits, so two commas give an
  **empty** field - right for CSV, where an empty field means a missing value;
- `split()` without an argument: any run of spaces, tabs and new lines splits, and
  there are no empty fields - right for words.

```python run
print("a,,b".split(","))           # ['a', '', 'b'] - the missing value is kept
print("a  b".split(" "))           # ['a', '', 'b'] - often not what you want
print("a  b".split())              # ['a', 'b']
print("  Iron   Retail ".split())
```

`maxsplit` limits the number of cuts; `rsplit` cuts from the right - the last word
of a company name is its legal form:

```python run
name = "Black Sea Design ET"

print(name.split(" ", 1))          # the first word, and the rest
print(name.rsplit(" ", 1))         # the rest, and the last word
base, form = name.rsplit(" ", 1)
print(base, "|", form)
```

`partition` cuts at the **first** separator and always gives three parts - handy for
`key=value`:

```python run
setting = "report_date=2026-09-30"
key, _, value = setting.partition("=")
print(key, value)

print("no equals sign".partition("="))
```

`splitlines` splits a text into lines (on `\n`, `\r\n` and more):

```python run
text = "line one\nline two\r\nline three"
print(text.splitlines())
```

### `join`: fields into a line

`separator.join(list_of_strings)` - the separator comes **first**, the list in the
brackets:

```python run
fields = ["L000002", "C0132", "investment"]

print(",".join(fields))           # a CSV line
print(" | ".join(fields))
print("".join(["B", "G", "8", "0"]))
```

`CATX(',', a, b, c)` in SAS, `CONCAT_WS(',', ...)` or `STRING_AGG` in SQL.

::: warning `join` takes only strings
A number in the list is a `TypeError`. Convert first:

```python run
row = ["L000002", 651927.30, 2]
print(",".join(str(x) for x in row))
print(",".join(row))              # TypeError: sequence item 1: expected str instance, float found
```
:::

### Why not `split(",")` for CSV files?

A field can contain the separator, inside quotes. `split` does not know quotes;
the `csv` module does:

```python run
import csv

line = 'C0026,"Silver Textiles, Plovdiv" AD,1965730713386'
print(line.split(","))                 # 4 fields - wrong
print(next(csv.reader([line])))        # 3 fields - right
```

That is why the examples since session 6 read files with `csv.DictReader`. Session
9 covers the `csv` module.

::: info The same in pandas
In pandas, every string method works on a whole column with `.str`:
`loans["product"].str.upper()`, `names.str.split()`, `ids.str.startswith("L")`
(session 15):

```python run
import pandas as pd

reg = pd.read_csv("data/client_register.csv")
print(reg["city"].str.strip().str.title().value_counts().head(4))
```
:::

::: tip Try it
`settings = "lgd=0.45;currency=EUR;report_date=2026-09-30"`. Turn it into a
dictionary `{"lgd": "0.45", ...}` with one comprehension: `split(";")`, then
`partition("=")`. Then join it back into the same string.
:::

## 5. Replace and remove

### `replace`

`replace(old, new)` replaces **every** occurrence; a third argument limits the
number:

```python run
iban = "BG80 TEST 9661 1020 3456 78"

print(iban.replace(" ", ""))             # remove all spaces: COMPRESS(iban)
print("1.234.567,89".replace(".", ""))   # remove the thousands points
print("a-b-c".replace("-", "/", 1))      # only the first one
```

Chains of `replace` run from left to right - each one on the result of the one
before:

```python run
amount = "1.234.567,89"
print(amount.replace(".", "").replace(",", "."))      # Bulgarian -> Python
print(float(amount.replace(".", "").replace(",", ".")))
```

::: warning The order of replacements matters
Swap `,` and `.` in `"1,234.56"` (English -> Bulgarian) with two `replace` calls,
and the second one changes the result of the first:

```python run
s = "1,234.56"
print(s.replace(",", ".").replace(".", ","))     # '1,234,56' - wrong
print(s.replace(",", "X").replace(".", ",").replace("X", " "))   # a temporary marker
```

`translate` (below) swaps characters in one step, without this problem.
:::

### `removeprefix` and `removesuffix`

Since Python 3.9: remove a text at the start or the end - only if it is there:

```python run
print("gr. Varna".removeprefix("gr. "))
print("Varna".removeprefix("gr. "))
print("BG165960351".removeprefix("BG"))
print("loans_2026-09.csv".removesuffix(".csv"))
```

Not the same as `strip("gr. ")` - that removes the **characters** g, r, `.` and
space from both ends, as long as it finds them:

```python run
print("gr. Burgas".strip("gr. "))       # 'Burgas' - looks right ...
print("gr. ruse".strip("gr. "))         # 'use'    - the r of ruse is gone too
print("gr. ruse".removeprefix("gr. "))  # 'ruse'
```

### `translate`: map or delete characters

`str.maketrans` builds a table of character changes, `translate` applies it - in one
pass. The SAS `TRANSLATE` and `COMPRESS(s, chars)`:

```python run
swap = str.maketrans({",": ".", ".": ","})
print("1,234.56".translate(swap))                    # swap , and . at once

drop = str.maketrans("", "", " -.")                  # the third argument: delete these
print("C-00 26".translate(drop))
print("131 234-567.".translate(drop))
```

::: tip Try it
`"BG80 test 9661-1020 3456 78"`: make it upper case, without spaces and dashes - in
one line with `translate` and `upper`.
:::

## 6. Padding and alignment

`zfill` pads a number-like string with zeros on the left - the SAS format `Z`:

```python run
print("17".zfill(4))                  # PUT(17, Z4.)
print(("C" + "17".zfill(4)))
print(f"L{42:06d}")                   # the same with an f-string (session 1)
```

`zfill` pads the **whole** string, and keeps a sign in front - it does not know that
`C` is a prefix. Pad the number part only:

```python run
print("17".zfill(4), "-17".zfill(4))     # '0017' '-017': the sign stays in front
print("C17".zfill(5))                    # '00C17' - the zeros go before the C
print("C" + "C17"[1:].zfill(4))          # 'C0017' - pad the digits, then add the C
```

`rjust`, `ljust` and `center` pad to a width with any character:

```python run
print(repr("EUR".ljust(6)), repr("EUR".rjust(6)), repr("EUR".center(7, "*")))
```

A fixed-width line - some old systems still want them. The f-string format spec of
session 1 does the same, and is easier to read:

```python run
rows = [("L000001", "investment", 1044231.30), ("L000003", "credit_card", 644.25)]

for loan_id, product, amount in rows:
    print(loan_id.ljust(8) + product.ljust(14) + f"{amount:.2f}".rjust(14))
    print(f"{loan_id:<8}{product:<14}{amount:>14.2f}")
```

The same on the loan portfolio - a small text report with a title, a header and the
amounts aligned on the right:

```python run
import csv

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))[:5]

print("THE FIRST FIVE LOANS".center(40, "="))
print(f"{'loan':<8}{'product':<16}{'amount':>16}")
for row in loans:
    print(f"{row['loan_id']:<8}{row['product']:<16}{float(row['amount']):>16,.2f}")
```

::: tip Try it
Print the numbers 1, 25 and 400 as loan ids `L000001`, `L000025`, `L000400` - once
with `zfill`, once with an f-string.
:::

## 7. Cleaning identifiers and names

Now the real file. One **function per column**: it takes the raw text and returns
the clean value - or `None` when the value cannot be fixed. Small functions are easy
to test, and the same function cleans the next file too.

### Client ids

`c0014`, `C 0009`, `C-0026`, `C17`, `" C0011"` -> `C0014`, `C0009`, `C0026`, `C0017`,
`C0011`:

```python run
def clean_client_id(raw):
    """'c-0026 ' -> 'C0026'; None if it is not a C and a number."""
    s = raw.strip().upper().replace(" ", "").replace("-", "")
    if not s.startswith("C") or not s[1:].isdigit():
        return None
    return "C" + s[1:].zfill(4)

for raw in ["c0014", "C 0009", "C-0026", "C17", " C0011", "X0001", "C"]:
    print(f"{raw!r:>10} -> {clean_client_id(raw)}")
```

On the whole file - how many ids needed a fix, and are they unique now?

```python run
import csv

def clean_client_id(raw):
    s = raw.strip().upper().replace(" ", "").replace("-", "")
    if not s.startswith("C") or not s[1:].isdigit():
        return None
    return "C" + s[1:].zfill(4)

with open("data/client_register.csv", encoding="utf-8") as file:
    raw_ids = [row["client_id"] for row in csv.DictReader(file)]

clean_ids = [clean_client_id(x) for x in raw_ids]
print("changed:", sum(1 for raw, clean in zip(raw_ids, clean_ids) if raw != clean))
print("invalid:", clean_ids.count(None))
print("unique: ", len(set(clean_ids)) == len(clean_ids))
```

### Company and person names

Spaces, case, quotes, and the legal form at the end:

```python run
LEGAL_FORMS = {"OOD", "EOOD", "AD", "EAD", "ET"}

def clean_name(raw):
    """One space between words, quotes removed, Title Case, legal forms in capitals."""
    words = raw.replace('"', "").split()
    result = []
    for word in words:
        bare = word.replace(".", "").upper()
        result.append(bare if bare in LEGAL_FORMS else word.title())
    return " ".join(result)

for raw in ["  BLACK SEA DESIGN ET", 'rila print ead', '"Silver Textiles" AD',
            "Green Build E.A.D.", "  Iron  Retail ET ", "NIKOLAY KOLEV"]:
    print(f"{raw!r:<26} -> {clean_name(raw)}")
```

### EIK and IBAN

The EIK (the company id of the Bulgarian register) has 9 digits, or 13 for a branch.
`BG` in front makes it a VAT number. Keep the digits only, then check the length:

```python run
def clean_eik(raw):
    """'BG 131 234 567' -> '131234567'; None if not 9 or 13 digits."""
    s = raw.strip().upper().removeprefix("BG").replace(" ", "")
    if s.isdigit() and len(s) in (9, 13):
        return s
    return None

for raw in ["175591301", "144 229 539", "BG165960351", "1965730713386", "12345678", ""]:
    print(f"{raw!r:>18} -> {clean_eik(raw)}")
```

An IBAN is written in groups of 4 for people, and without spaces for machines. A
Bulgarian IBAN has 22 characters and starts with `BG`:

```python run
def clean_iban(raw):
    """'bg80 test 9661 ...' -> 'BG80TEST9661...'; None if empty or not 22 characters."""
    s = raw.replace(" ", "").upper()
    if len(s) == 22 and s.startswith("BG") and s.isalnum():
        return s
    return None

def pretty_iban(iban):
    """The groups of 4, for a report."""
    return " ".join(iban[i:i + 4] for i in range(0, len(iban), 4))

iban = clean_iban("bg05test77018249464461")
print(iban)
print(pretty_iban(iban))
print(clean_iban(""))
```

Both checks are only the **shape**. A real EIK and a real IBAN also have **check
digits** that catch typing errors - the Self-study of session 8 computes them.

### E-mails

```python run
def clean_email(raw):
    """Lower case, no spaces; None unless it has exactly one @ and a dot after it."""
    s = raw.strip().lower()
    if s.count("@") != 1 or " " in s:
        return None
    user, _, domain = s.partition("@")
    if not user or "." not in domain:
        return None
    return s

for raw in ["OFFICE.NORTHHOTELS@EXAMPLE.ORG", " yana.koleva@example.org",
            "office.balkanfoods at example.net", "a@b"]:
    print(f"{raw!r:<38} -> {clean_email(raw)}")
```

(Session 8 checks e-mails with a regular expression.)

### Cities: a mapping of variants

Some variants are only case and spaces; some are a prefix; some are in Cyrillic.
Clean what string methods can clean, then a **dictionary** (session 6) maps the
Cyrillic names:

```python run
import csv
from collections import Counter

CYRILLIC = {"София": "Sofia", "Пловдив": "Plovdiv", "Варна": "Varna", "Бургас": "Burgas",
            "Русе": "Ruse", "Стара Загора": "Stara Zagora", "Плевен": "Pleven"}

def clean_city(raw):
    s = " ".join(raw.split()).removeprefix("gr. ")
    s = CYRILLIC.get(s, s)
    return s.title()

with open("data/client_register.csv", encoding="utf-8") as file:
    cities = [row["city"] for row in csv.DictReader(file)]

print(len(Counter(cities)), "different spellings before")
clean = Counter(clean_city(c) for c in cities)
print(len(clean), "after:", dict(clean))
```

Compare with `clients.csv`, where the region is clean: the counts must be the same.

```python run
import csv
from collections import Counter

CYRILLIC = {"София": "Sofia", "Пловдив": "Plovdiv", "Варна": "Varna", "Бургас": "Burgas",
            "Русе": "Ruse", "Стара Загора": "Stara Zagora", "Плевен": "Pleven"}

def clean_city(raw):
    s = " ".join(raw.split()).removeprefix("gr. ")
    return CYRILLIC.get(s, s).title()

with open("data/client_register.csv", encoding="utf-8") as file:
    from_register = Counter(clean_city(row["city"]) for row in csv.DictReader(file))
with open("data/clients.csv", encoding="utf-8") as file:
    from_clients = Counter(row["region"] for row in csv.DictReader(file))

print(from_register == from_clients)
```

A check like this - "the cleaned data agrees with a trusted source" - is worth more
than any amount of looking at the data.

::: info The same in pandas
The same functions work on a column with `.map(function)`, or with the `.str`
methods (session 15):

```python run
import pandas as pd

reg = pd.read_csv("data/client_register.csv", dtype=str)
clean = reg["client_id"].str.strip().str.upper().str.replace("[ -]", "", regex=True)
print(clean.head(10).tolist())
```
:::

::: tip Try it
Change `clean_name` so that it also removes a comma before the legal form
(`"Rila Print, EAD"`). Then run it on all names of the file and count how many
were changed.
:::

## 8. Numbers from text

`float()` understands only one format: a point for the decimals, no separators.
Text from Excel, reports and people has other formats:

```python run
print(float("1234567.89"))
print(float(" 1234567.89 "))     # spaces at the ends are fine
print(float("1 234 567,89"))     # ValueError: could not convert string to float
```

`int()` is even stricter: it takes only whole numbers. A value like `"4.0"` from an
export needs `float` first:

```python run
print(int(" 042 "))           # 42: spaces and leading zeros are fine
print(int(float("4.0")))      # 4: through float
print(int("4.0"))             # ValueError: invalid literal for int() with base 10
```

The turnover column has all of these:

| Text | Style | Value |
|---|---|---|
| `1 234 567,89` | Bulgarian: space, comma | 1234567.89 |
| `1.234.567,89` | German / Bulgarian Excel: point, comma | 1234567.89 |
| `1,234,567.89` | English: comma, point | 1234567.89 |
| `1234567.89` | plain | 1234567.89 |
| `EUR 7 729 271` | a currency, no decimals | 7729271.0 |

The rule: the **last** of `,` and `.` is the decimal separator - if it has one to two
digits after it; everything else is a thousands separator.

```python run
def parse_amount(raw):
    """A number in any of the usual formats -> float; None if empty."""
    s = raw.strip().removeprefix("EUR").replace(" ", "")
    if not s:
        return None
    last = max(s.rfind(","), s.rfind("."))
    if last >= 0 and len(s) - last - 1 in (1, 2):           # a decimal separator
        whole, decimals = s[:last], s[last + 1:]
    else:
        whole, decimals = s, "0"
    whole = whole.replace(",", "").replace(".", "")
    return float(whole + "." + decimals)

for raw in ["1 234 567,89", "1.234.567,89", "1,234,567.89", "1234567.89", "EUR 7 729 271", ""]:
    print(f"{raw!r:>18} -> {parse_amount(raw)}")
```

::: warning A number without decimals is ambiguous
`"1,234"` - is it one thousand two hundred thirty-four (English), or one point two
three four (Bulgarian)? The rule above says 1234, because three digits after the
separator are thousands. In your own data, **ask** which format a source uses, and
write it down - do not guess per value.
:::

The SAS informats do the same with a fixed rule per column: `COMMA12.` for
`1,234,567.89` and `COMMAX12.` for `1.234.567,89`.

And back: a number in the Bulgarian format for a report. The format spec gives the
English format; then swap the characters with `translate` (section 5):

```python run
def format_bg(value, decimals=2):
    """1234567.891 -> '1 234 567,89'"""
    return f"{value:,.{decimals}f}".translate(str.maketrans({",": " ", ".": ","}))

print(format_bg(1234567.891))
print(format_bg(644.25))
print(format_bg(-5000, 0))
```

On the file - the total turnover of the companies:

```python run
import csv

def parse_amount(raw):
    s = raw.strip().removeprefix("EUR").replace(" ", "")
    if not s:
        return None
    last = max(s.rfind(","), s.rfind("."))
    if last >= 0 and len(s) - last - 1 in (1, 2):
        whole, decimals = s[:last], s[last + 1:]
    else:
        whole, decimals = s, "0"
    return float(whole.replace(",", "").replace(".", "") + "." + decimals)

with open("data/client_register.csv", encoding="utf-8") as file:
    turnovers = [parse_amount(row["turnover"]) for row in csv.DictReader(file)]

known = [t for t in turnovers if t is not None]
print(len(known), "companies, total turnover", f"{sum(known):,.2f}")
print("largest:", f"{max(known):,.2f}")
```

::: tip Try it
What does `parse_amount("12,5")` give? And `parse_amount("1,234")`? Predict, then run.
Which of the two answers would be wrong for an English-style source?
:::

## 9. Dates from text

### `date` and `datetime`

The module `datetime` has the types for dates and times:

- `date` - a day: year, month, day;
- `datetime` - a day and a time;
- `timedelta` - a length of time (days, seconds).

```python run
from datetime import date, datetime, timedelta

report_date = date(2026, 9, 30)
print(report_date, report_date.year, report_date.month, report_date.day)
print(report_date.weekday())                   # 0 = Monday ... 6 = Sunday
print(date.today())                            # TODAY()
print(datetime(2026, 9, 30, 17, 45))
```

### From ISO text: `fromisoformat`

The ISO format `YYYY-MM-DD` is the format of the sample data, of databases and of
JSON. It has its own method:

```python run
from datetime import date

start = date.fromisoformat("2019-04-16")
print(start, type(start))
print(start.isoformat())               # and back to text
```

ISO dates have one more advantage: as **text**, they sort in the right order
(session 2). `"16.04.2019"` does not.

### Any format: `strptime` and `strftime`

`datetime.strptime(text, format)` reads a date in a format you describe with
**format codes**; `strftime(format)` writes one:

| Code | Means | Example |
|---|---|---|
| `%Y` | year, 4 digits | `2026` |
| `%m` | month, 2 digits | `09` |
| `%d` | day, 2 digits | `30` |
| `%b` | month name, short | `Sep` |
| `%B` | month name | `September` |
| `%H:%M:%S` | hours, minutes, seconds | `17:45:00` |

```python run
from datetime import datetime

d = datetime.strptime("30.09.2026", "%d.%m.%Y").date()     # INPUT(x, DDMMYY10.)
print(d)
print(datetime.strptime("30/09/2026", "%d/%m/%Y").date())
print(datetime.strptime("20260930", "%Y%m%d").date())      # INPUT(x, YYMMDD8.)
print(datetime.strptime("8 Jun 2014", "%d %b %Y").date())

print(d.strftime("%d.%m.%Y"))                               # PUT(d, DDMMYYP10.)
print(d.strftime("%B %Y"))
print(f"{d:%d.%m.%Y}")                                      # the format codes work in f-strings too
```

`strptime` gives a `datetime`; `.date()` keeps only the day.

A text that does not match the format is a `ValueError` - also an impossible date:

```python run
from datetime import datetime

print(datetime.strptime("31.09.2026", "%d.%m.%Y"))     # ValueError: there is no 31 September
```

(How to catch such an error and go on with the next row: session 9.)

::: details Advanced: month names and the language
`%b` and `%B` follow the **locale**. By default Python uses English month names, but
if a program (or a library) switches the locale with `locale.setlocale`, `%b` expects
the month names of that language, and `strptime("8 Jun 2014", "%d %b %Y")` can fail.
For data, prefer numeric formats. If a source has English month names, a small
dictionary `{"Jan": 1, ...}` (session 6) is the safe way.
:::

### Several formats in one column

The `registered` column has four formats. Decide the format by the **shape** of the
text, then read it:

```python run
from datetime import date, datetime

def parse_date(raw):
    """A date in one of the formats of the register -> date; None if empty."""
    s = raw.strip()
    if not s:
        return None
    if len(s) == 10 and s[4] == "-":
        return date.fromisoformat(s)                          # 2014-06-08
    if len(s) == 10 and s[2] == ".":
        return datetime.strptime(s, "%d.%m.%Y").date()        # 08.06.2014
    if len(s) == 10 and s[2] == "/":
        return datetime.strptime(s, "%d/%m/%Y").date()        # 08/06/2014
    if len(s) == 8 and s.isdigit():
        return datetime.strptime(s, "%Y%m%d").date()          # 20140608
    return datetime.strptime(s, "%d %b %Y").date()            # 8 Jun 2014

for raw in ["2014-06-08", "08.06.2014", "08/06/2014", "20140608", "8 Jun 2014"]:
    print(f"{raw:>12} -> {parse_date(raw)}")
```

::: warning `08/06/2014` - June or August?
In Bulgaria and most of Europe it is the 8th of June; in the USA it is the 6th of
August. Python does not guess: you choose `%d/%m` or `%m/%d`. As with numbers:
know the source.
:::

### Date arithmetic

Subtracting two dates gives a `timedelta`; its `.days` is the number of days -
`INTCK('day', a, b)`, or `b - a` in SAS:

```python run
from datetime import date, timedelta

start = date(2019, 4, 16)
report_date = date(2026, 9, 30)

age = report_date - start
print(age, "|", age.days, "days |", round(age.days / 365.25, 1), "years")

print(report_date + timedelta(days=30))           # 30 days later
print(report_date - timedelta(weeks=1))
```

The first and the last day of a month - the **report dates** of risk reporting:

```python run
from datetime import date, timedelta

d = date(2026, 2, 17)
first = d.replace(day=1)                                       # INTNX('month', d, 0, 'b')
next_first = (first + timedelta(days=32)).replace(day=1)
last = next_first - timedelta(days=1)                          # INTNX('month', d, 0, 'e')
print(first, last)
```

(Adding **months** is not in `datetime`: a month has no fixed length. Session 16
does it with pandas; session 10 shows the standard library.)

### On the file: years as a client

```python run
import csv
from datetime import date, datetime

def parse_date(raw):
    s = raw.strip()
    if len(s) == 10 and s[4] == "-":
        return date.fromisoformat(s)
    if len(s) == 10 and s[2] == ".":
        return datetime.strptime(s, "%d.%m.%Y").date()
    if len(s) == 10 and s[2] == "/":
        return datetime.strptime(s, "%d/%m/%Y").date()
    if len(s) == 8 and s.isdigit():
        return datetime.strptime(s, "%Y%m%d").date()
    return datetime.strptime(s, "%d %b %Y").date()

REPORT_DATE = date(2026, 9, 30)
with open("data/client_register.csv", encoding="utf-8") as file:
    since = [parse_date(row["registered"]) for row in csv.DictReader(file)]

years = [(REPORT_DATE - d).days / 365.25 for d in since]
print("oldest:", min(since), " newest:", max(since))
print("average years as a client:", round(sum(years) / len(years), 1))
print("clients for less than 1 year:", sum(1 for y in years if y < 1))
```

::: tip Try it
Check the parsed dates against `clients.csv`, where `client_since` is clean ISO: are
all 150 equal? (Read both files, compare the lists with `==`.)
:::

## 10. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: `git pull upstream main`) and run the tasks from the
terminal, in the repository root:

```bash
python 07-text-processing/practice/task1-case-and-spaces.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-case-and-spaces.py` | Normalise names, cities and codes: case, spaces, prefixes |
| 2 | `task2-predict-strings.py` | Predict: `split`, `strip`, `find`, `join`, `replace`, slices |
| 3 | `task3-split-join.py` | Settings `key=value;...` into a dict and back; `SCAN`; a CSV line |
| 4 | `task4-identifiers.py` | Clean client ids, EIKs, IBANs and e-mails |
| 5 | `task5-amounts.py` | Numbers in four formats to `float`; the Bulgarian format back |
| 6 | `task6-dates.py` (Optional) | Dates in five formats; days between; month ends; years as a client |

## Summary

| Topic | Remember |
|-------|----------|
| Immutable | every method returns a new string: `s = s.strip()` |
| Case | `upper`, `lower`, `title` (fix legal forms after it); compare with `.lower()` on both sides |
| Spaces | `strip` / `lstrip` / `rstrip` at the ends; `" ".join(s.split())` = `COMPBL` |
| Find | `in`; `startswith((...))`; `find` gives -1, `index` raises; `count` |
| Test | `isdigit`, `isalpha`, `isalnum`, `isspace` - all characters, non-empty |
| Split | `split(",")` keeps empty fields; `split()` splits on any spaces; `rsplit`, `partition`, `splitlines` |
| Join | `", ".join(strings)` - only strings; CSV with quotes: the `csv` module |
| Replace | `replace(old, new)`; `removeprefix` / `removesuffix`; `translate(str.maketrans(...))` |
| Pad | `zfill`, `rjust`, `ljust`; f-string `:>10`, `:06d` |
| Cleaning | one function per column, `None` for what cannot be fixed; check against a trusted source |
| Numbers | the last `,` or `.` with 1 - 2 digits after it is the decimal separator; know the source |
| Dates | `date.fromisoformat`; `datetime.strptime(s, "%d.%m.%Y").date()`; `strftime`; `b - a` gives a `timedelta` |

## Homework

1. `07-text-processing/homework.py` (in the homework repository): **clean the client
   register** - a function for each column of `client_register.csv`, then the whole
   file into a list of clean records, with a summary: how many values were fixed and
   how many could not be fixed, per column. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: print the clean register as a fixed-width report: the client id, the
   name (30 characters), the EIK, the IBAN in groups of 4, and the turnover in the
   Bulgarian format, right-aligned.

## Self-study

This part is not covered in class. It is for reading at home: what an encoding is,
why Cyrillic text sometimes comes out as `РЎРѕС„РёСЏ`, and how to write Cyrillic names in
Latin letters.

### Encodings: UTF-8, cp1251 and Cyrillic

A file on disk is **bytes**, not text. An **encoding** is the rule that turns text
into bytes and back. The same text gives different bytes in different encodings:

```python run
city = "София"

utf8 = city.encode("utf-8")
cp1251 = city.encode("cp1251")
print(utf8, len(utf8))           # 2 bytes per Cyrillic letter
print(cp1251, len(cp1251))       # 1 byte per letter
print(utf8.decode("utf-8"), cp1251.decode("cp1251"))
```

- **UTF-8** - every character of every language; the standard of the web, of
  Python source files and of most new files.
- **cp1251** (Windows-1251) - the old Windows encoding for Cyrillic. Exports from old
  systems and Excel files saved as "CSV" on a Bulgarian Windows are often cp1251.

Reading with the wrong encoding gives either an error, or **mojibake** - wrong
letters:

```python run
data = "София".encode("utf-8")
print(data.decode("cp1251"))         # UTF-8 bytes read as cp1251: mojibake

data = "София".encode("cp1251")
print(data.decode("utf-8"))          # UnicodeDecodeError
```

That is why every `open()` in this course says `encoding="utf-8"`: without it, Python
3.12 / 3.13 on Windows uses the Windows encoding of the computer (often cp1252 or
cp1251), and the same script gives different results on different computers. (Python
3.15 uses UTF-8 by default everywhere.)

The file `regions_bg.csv` is saved in **cp1251**:

```python run
with open("data/regions_bg.csv", encoding="cp1251") as file:
    print(file.read())

with open("data/regions_bg.csv", encoding="utf-8", errors="replace") as file:
    print(file.read())          # the wrong encoding: the letters become question marks
```

`errors="replace"` puts `?` (or `�`) instead of a byte that cannot be read,
instead of stopping. Use it only to **look** at a file, never to load data.

One more detail: Excel saves "CSV UTF-8" with a **BOM** - three bytes `EF BB BF` at the
start. Read such a file with `encoding="utf-8-sig"`, or the first column name gets an
invisible character in front:

```python run
with open("data/loans_export.csv", encoding="utf-8") as file:
    print(repr(file.readline()[:12]))
with open("data/loans_export.csv", encoding="utf-8-sig") as file:
    print(repr(file.readline()[:12]))
```

**Exercises**

1. Read `regions_bg.csv` with `csv.DictReader` and the right encoding, and build a
   dictionary `name_bg -> name_en`.
2. Write the same rows into a new file `regions_utf8.csv` in UTF-8, and read it back.

::: details Answer
```python
import csv

with open("data/regions_bg.csv", encoding="cp1251") as file:
    rows = list(csv.DictReader(file))
to_en = {r["name_bg"]: r["name_en"] for r in rows}
print(to_en)

with open("regions_utf8.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["code", "name_bg", "name_en"])
    writer.writeheader()
    writer.writerows(rows)
with open("regions_utf8.csv", encoding="utf-8") as file:
    print(file.read())
```
(Writing files with `csv`: session 9.)
:::

### Cyrillic names in Latin letters

Bulgaria has an official transliteration (the Transliteration Act of 2009): `ж` ->
`zh`, `ц` -> `ts`, `ч` -> `ch`, `ш` -> `sh`, `щ` -> `sht`, `ъ` -> `a`, `ю` -> `yu`, `я`
-> `ya`, ... A dictionary of single letters to strings, used with `translate`:

```python run
LETTERS = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ж": "zh", "з": "z",
    "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p",
    "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "sht", "ъ": "a", "ь": "y", "ю": "yu", "я": "ya",
}
TABLE = str.maketrans(LETTERS | {k.upper(): v.capitalize() for k, v in LETTERS.items()})

for name in ["София", "Стара Загора", "Пловдив", "Шумен", "Ямбол"]:
    print(name, "->", name.translate(TABLE))
```

`str.maketrans` accepts a dictionary of **one character -> any string**, so one
letter can become two or three. (The full rules have a few exceptions, for example
`-ия` at the end of a word is `-ia`: `София` -> `Sofia`, not `Sofiya`.)

Another trap of text from many sources: the same letter can be stored in two ways -
`"й"` as one character, or `"и"` plus a combining mark. They look the same, but are
not `==`. `unicodedata.normalize("NFC", s)` brings both to the same form:

```python run
import unicodedata

a = "й"
b = "й"                 # и + a combining breve
print(a, b, a == b, len(a), len(b))
print(unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b))
```

**Exercise**

1. Add the rule "`ия` at the end of a word -> `ia`" to the transliteration: first
   replace it, then `translate`. Check it with `София` and `Мария`.

::: details Answer
```python
def to_latin(text):
    words = []
    for word in text.split():
        if word.lower().endswith("ия"):
            word = word[:-2] + ("IA" if word.isupper() else "ia")
        words.append(word.translate(TABLE))
    return " ".join(words)

print(to_latin("София"), to_latin("Мария"))      # Sofia Maria
```
(The ASCII letters `ia` pass through `translate` unchanged.)
:::

## Read more

- Reference: [String methods](https://docs.python.org/3/library/stdtypes.html#string-methods),
  [`datetime`](https://docs.python.org/3/library/datetime.html) (the table of
  [format codes](https://docs.python.org/3/library/datetime.html#format-codes)),
  [`csv`](https://docs.python.org/3/library/csv.html)
- [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) (encodings, normalisation)
- Real Python: [Strings and character data](https://realpython.com/python-strings/),
  [Using Python datetime to work with dates and times](https://realpython.com/python-datetime/)

**Next session:** regular expressions - patterns that find, check and extract IBANs,
EIKs, e-mails, dates and amounts in free text; the Python `PRXMATCH`.
