---
title: 7. Text processing and regular expressions
---

# 7. Text processing and regular expressions

<div class="lecture-meta">
  <span>Session 7</span><span>practice: <code>07-text-and-regex/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- change the case of text and remove extra spaces - the Python versions of the SAS
  functions `UPCASE`, `PROPCASE`, `STRIP` and `COMPBL`;
- find and test parts of a string, and check what kind of characters it has;
- split a line into fields and join fields into a line - `SCAN` and `CATX` in SAS;
- replace and remove parts of a text - `TRANWRD` and `COMPRESS` in SAS;
- clean real identifiers: client ids, company names, EIKs, IBANs, city names;
- read a number and a date from text, with `float` and `datetime`;
- describe the **shape** of a text with a regular expression, and find, check and
  extract with the `re` module - the Python version of SAS `PRXMATCH` and of SQL
  `LIKE` and `REGEXP_LIKE`.

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

The lecture has two parts. Sections 1 - 6 use the **methods of `str`**: they are
enough for most cleaning. Sections 7 - 11 add **regular expressions**: patterns for
texts that have a shape, like an IBAN or a date.

## 1. Strings: a recap and the new data

You know from [session 1](./01-intro-syntax-types.md#str-text) and 3: a string is a **sequence** of characters; `len(s)`,
`s[0]`, `s[-1]`, `s[2:5]` work like on a list; `s[2:5]` is `SUBSTR(s, 3, 3)` in SAS. And a
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
| `registered` | five date formats |
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

To compare two texts without the case, make **both** sides lower case (or both upper
case):

```python run
city = "SOFIA"
print(city == "Sofia")
print(city.lower() == "sofia")
```

::: warning `title()` is not clever
`title()` gives a capital after **every** character that is not a letter, and it
does not know legal forms or abbreviations:

```python run
print("blue wines eood".title())      # 'Blue Wines Eood' - should be EOOD
print("2nd floor".title())            # '2Nd Floor'
```

Fix the known words after `title()` (section 5).
:::

### Remove spaces: `strip`

`strip()` removes spaces (and tabs and new lines) at **both ends**; `lstrip()` only
at the start, `rstrip()` only at the end:

```python run
city = "  ruse "

print(repr(city.strip()))       # STRIP in SAS, TRIM in SQL
print(repr(city.lstrip()))      # LEFT in SAS, LTRIM in SQL
print(repr(city.rstrip()))      # TRIM in SAS, RTRIM in SQL
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

`strip` does not touch the spaces **inside** a text. `split()` without an argument
cuts the text into words at every group of spaces, and `" ".join(...)` puts the words
back with one space between them:

```python run
name = "  Iron   Retail  ET "

print(repr(name.strip()))
print(repr(" ".join(name.split())))        # COMPBL(STRIP(name)) in SAS
```

`" ".join(s.split())` is the usual Python way to say "remove all extra spaces".
Section 4 explains `split` and `join`.

::: tip Try it
Clean `"  GREEN   build  ltd "` into `"Green Build Ltd"`. You need `split`, `join`
and `title`.
:::

## 3. Find and test

### Is it in there?

```python run
comment = "Payment of 1 250,00 EUR received on 15.09.2026."

print("EUR" in comment)                        # INDEX(comment, 'EUR') > 0 in SAS
print(comment.startswith("Payment"))           # LIKE 'Payment%' in SQL
print(comment.endswith("."))                   # LIKE '%.' in SQL
print("eur" in comment)                        # case matters
print("eur" in comment.lower())
```

`startswith` and `endswith` also take a **tuple** of options - "starts with one of
these":

```python run
loan_ids = ["L000001", "C0002", "L000003", "X1"]
print([x for x in loan_ids if x.startswith(("L", "C"))])

files = ["loans.csv", "clients.CSV", "report.xlsx"]
print([f for f in files if f.lower().endswith((".csv", ".xlsx"))])
```

### Where is it? `find` and `count`

`find` gives the position of the first match, or **-1** if there is none. `count`
says how many times a text occurs:

```python run
comment = "Payment of 1 250,00 EUR received on 15.09.2026."

print(comment.find("EUR"))           # the position (from 0)
print(comment.find("USD"))           # -1: not found
print(comment.count("0"))            # how many times
```

The SAS functions `INDEX` and `FIND` count from **1** and give **0** when nothing is
found. Python counts from 0 and gives -1. A classic bug: `if s.find("x"):` is true
for -1, and false when `"x"` is at position 0. Use `in` for "is it there?".

### What kind of characters?

These methods return `True` if **all** characters are of one kind (and the string is
not empty):

```python run
for s in ["131234567", "12O.50", "EUR", "BG80", ""]:
    print(f"{s!r:<12} digit={s.isdigit()!s:<6} alpha={s.isalpha()!s:<6} alnum={s.isalnum()}")
```

| Method | `True` when all characters are | SAS |
|---|---|---|
| `s.isdigit()` | digits | `NOTDIGIT(s) = 0` |
| `s.isalpha()` | letters | `NOTALPHA(s) = 0` |
| `s.isalnum()` | letters or digits | `NOTALNUM(s) = 0` |

Check an id by its parts - "an L and six digits":

```python run
def is_loan_id(s):
    return len(s) == 7 and s[0] == "L" and s[1:].isdigit()

print([is_loan_id(x) for x in ["L000001", "L00001", "l000001", "L00000A", "L999999"]])
```

::: warning `isdigit` is not "is a number"
`"12.50".isdigit()` and `"-5".isdigit()` are `False`: a point and a minus are not
digits. Use `isdigit` for ids and codes. For numbers, convert with `float()`
(section 6).
:::

::: tip Try it
Write `is_client_id(s)`: `"C"` and four digits. Test it on `"C0001"`, `"c0001"`,
`"C001"`, `"C00010"`. Then change it to accept a lower-case `c` too.
:::

## 4. Split, join and replace

### `split`: a line into fields

```python run
line = "L000002,C0132,investment,EUR,2019-04-16"
fields = line.split(",")
print(fields)
print(fields[2])                  # SCAN(line, 3, ',') in SAS
```

There are two kinds of `split`:

- `split(",")` with a separator: **every** comma cuts, so two commas give an
  **empty** field. This is right for CSV, where an empty field means a missing
  value.
- `split()` without an argument: every group of spaces, tabs and new lines cuts, and
  there are no empty fields. This is right for words.

```python run
print("a,,b".split(","))           # ['a', '', 'b'] - the missing value is kept
print("a  b".split(" "))           # ['a', '', 'b'] - often not what you want
print("a  b".split())              # ['a', 'b']
print("  Iron   Retail ".split())
```

A second argument limits the number of cuts. `rsplit` cuts from the right - the last
word of a company name is its legal form:

```python run
name = "Black Sea Design ET"

print(name.split(" ", 1))          # the first word, and the rest
print(name.rsplit(" ", 1))         # the rest, and the last word
base, form = name.rsplit(" ", 1)
print(base, "|", form)
```

`partition` cuts at the **first** separator and always gives three parts: the text
before, the separator, the text after. It is handy for `key=value`:

```python run
setting = "report_date=2026-09-30"
key, _, value = setting.partition("=")
print(key, value)

print("no equals sign".partition("="))
```

(The name `_` is a normal variable. By convention it means "I do not need this
value".)

### `join`: fields into a line

`separator.join(list_of_strings)` - the separator comes **first**, the list goes in
the brackets:

```python run
fields = ["L000002", "C0132", "investment"]

print(",".join(fields))           # a CSV line
print(" | ".join(fields))
print("".join(["B", "G", "8", "0"]))
```

This is `CATX(',', a, b, c)` in SAS, and `CONCAT_WS(',', ...)` or `STRING_AGG` in SQL.

::: warning `join` takes only strings
A number in the list is a `TypeError`. Convert the values first:

```python run
row = ["L000002", 651927.30, 2]
print(",".join(str(x) for x in row))
print(",".join(row))              # TypeError: sequence item 1: expected str instance, float found
```
:::

::: info Do not use `split(",")` to read a CSV file
A field can contain a comma, inside quotes: `C0026,"Silver Textiles, Plovdiv",AD`.
`split` does not know quotes; the `csv` module does. That is why the examples since
[session 6](./06-dictionaries.md#a-row-as-a-dictionary) read files with `csv.DictReader`. [Lecture 8](./08-errors-and-files.md#_7-csv-files) covers the `csv` module.
:::

### `replace`

`replace(old, new)` replaces **every** occurrence. A third argument limits the
number:

```python run
iban = "BG80 TEST 9661 1020 3456 78"

print(iban.replace(" ", ""))             # remove all spaces: COMPRESS(iban) in SAS
print("a-b-c".replace("-", "/", 1))      # only the first one
```

Several `replace` calls in a row run from left to right - each one works on the
result of the one before:

```python run
amount = "1.234.567,89"
print(amount.replace(".", ""))                        # step 1: no thousands points
print(amount.replace(".", "").replace(",", "."))      # step 2: a decimal point
```

### `removeprefix` and `removesuffix`

They remove a text at the start or at the end - only if it is there:

```python run
print("gr. Varna".removeprefix("gr. "))
print("Varna".removeprefix("gr. "))
print("BG165960351".removeprefix("BG"))
print("loans_2026-09.csv".removesuffix(".csv"))
```

This is not the same as `strip("gr. ")`. `strip` removes the **characters** g, r, `.`
and space from both ends, as long as it finds them:

```python run
print("gr. ruse".strip("gr. "))         # 'use'  - the r of ruse is gone too
print("gr. ruse".removeprefix("gr. "))  # 'ruse'
```

### `zfill`: zeros in front

`zfill` adds zeros on the left until the text has the given length - the SAS format
`Z`:

```python run
print("17".zfill(4))                  # PUT(17, Z4.) in SAS
print("C" + "17".zfill(4))
print("C17".zfill(5))                 # '00C17' - zfill does not know that C is a prefix
print("C" + "C17"[1:].zfill(4))       # 'C0017' - pad the digits, then add the C
```

::: info The same in pandas
In pandas, every string method works on a whole column with `.str`:
`loans["product"].str.upper()`, `names.str.split()`, `ids.str.startswith("L")`
([lecture 14](./14-pandas-select-aggregate-join.md#text-and-dates-in-a-column)):

```python run
import pandas as pd

reg = pd.read_csv("data/client_register.csv")
print(reg["city"].str.strip().str.title().value_counts().head(4))
```
:::

::: tip Try it
`settings = "lgd=0.45;currency=EUR;report_date=2026-09-30"`. Turn it into a
dictionary `{"lgd": "0.45", ...}`: `split(";")` gives the three parts, and
`partition("=")` cuts each part into a key and a value. Then join the dictionary
back into the same string.
:::

## 5. Cleaning identifiers and names

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
        if bare in LEGAL_FORMS:
            result.append(bare)
        else:
            result.append(word.title())
    return " ".join(result)

for raw in ["  BLACK SEA DESIGN ET", 'rila print ead', '"Silver Textiles" AD',
            "Green Build E.A.D.", "  Iron  Retail ET ", "NIKOLAY KOLEV"]:
    print(f"{raw!r:<26} -> {clean_name(raw)}")
```

### EIK and IBAN

The EIK (the company id of the Bulgarian register) has 9 digits, or 13 for a branch.
With `BG` in front it is a VAT number. Keep the digits only, then check the length:

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

People write an IBAN in groups of 4; systems want it without spaces. A Bulgarian
IBAN has 22 characters and starts with `BG`:

```python run
def clean_iban(raw):
    """'bg80 test 9661 ...' -> 'BG80TEST9661...'; None if empty or not 22 characters."""
    s = raw.replace(" ", "").upper()
    if len(s) == 22 and s.startswith("BG") and s.isalnum():
        return s
    return None

print(clean_iban("bg05 test 7701 8249 4644 61"))
print(clean_iban(""))
```

Both checks are only the **shape**. A real EIK and a real IBAN also have **check
digits** that catch typing errors - see [Check digits](#check-digits-iban-and-eik) in the Self-study part.

### Cities: a mapping of variants

Some variants differ only by case and spaces; some have a prefix; some are in
Cyrillic. Clean what string methods can clean. Then a **dictionary**
([session 6](./06-dictionaries.md#_5-lookup-tables-and-nomenclatures)) maps the Cyrillic names:

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

::: tip Try it
Change `clean_name` so that it also removes a comma before the legal form
(`"Rila Print, EAD"` -> `"Rila Print EAD"`). Then run it on all names of the file
and count how many names were changed.
:::

## 6. Numbers and dates from text

### Numbers

`float()` understands only one format: a point for the decimals, and no separators
between the thousands. Text from Excel, from reports and from people has other
formats:

```python run
print(float("1234567.89"))
print(float(" 1234567.89 "))     # spaces at the ends are fine
print(float("1 234 567,89"))     # ValueError: could not convert string to float
```

When you know the format of the source, bring the text to the Python format with
`replace`, then convert. The Bulgarian format has spaces between the thousands and a
decimal comma:

```python run
def parse_bg_amount(raw):
    """'1 234 567,89' -> 1234567.89"""
    return float(raw.replace(" ", "").replace(",", "."))

print(parse_bg_amount("1 234 567,89"))
print(parse_bg_amount("644,25"))
```

::: warning Know the format of the source
`"1,234"` - is it one thousand two hundred thirty-four (the English format), or one
point two three four (the Bulgarian format)? The text does not say. **Ask** which
format a source uses and write one function for it. Do not guess value by value.
(A column with several formats, like `turnover` in the register: see
[Numbers in any format](#numbers-in-any-format) in the Self-study part.)
:::

### `date`: a day

The module `datetime` has the types for dates and times. `date` is a day: a year, a
month and a day.

```python run
from datetime import date

report_date = date(2026, 9, 30)
print(report_date, report_date.year, report_date.month, report_date.day)
print(report_date.weekday())                   # 0 = Monday ... 6 = Sunday
print(date.today())                            # TODAY() in SAS
```

### From text to a date

The ISO format `YYYY-MM-DD` is the format of the sample data, of databases and of
JSON. It has its own method, `date.fromisoformat`:

```python run
from datetime import date

start = date.fromisoformat("2019-04-16")
print(start, type(start))
print(start.isoformat())               # and back to text
```

For any other format, describe it with **format codes**.
`datetime.strptime(text, format)` reads a date from text, and `strftime(format)`
writes a date as text:

| Code | Means | Example |
|---|---|---|
| `%Y` | year, 4 digits | `2026` |
| `%m` | month, 2 digits | `09` |
| `%d` | day, 2 digits | `30` |

```python run
from datetime import datetime

d = datetime.strptime("30.09.2026", "%d.%m.%Y").date()     # INPUT(x, DDMMYY10.) in SAS
print(d)
print(datetime.strptime("30/09/2026", "%d/%m/%Y").date())
print(datetime.strptime("20260930", "%Y%m%d").date())      # INPUT(x, YYMMDD8.) in SAS

print(d.strftime("%d.%m.%Y"))                               # PUT(d, DDMMYYP10.) in SAS
print(f"{d:%d.%m.%Y}")                                      # the codes work in f-strings too
```

`strptime` gives a `datetime` (a day **and** a time); `.date()` keeps only the day.

A text that does not fit the format is a `ValueError`. An impossible date is one
too:

```python run
from datetime import datetime

print(datetime.strptime("31.09.2026", "%d.%m.%Y"))     # ValueError: there is no 31 September
```

(How to catch such an error and go on with the next row: [lecture 8](./08-errors-and-files.md#_2-try-except).)

::: warning `08/06/2014` - June or August?
In Bulgaria and most of Europe it is the 8th of June; in the USA it is the 6th of
August. Python does not guess: you choose `%d/%m` or `%m/%d`. As with numbers:
know the source.
:::

### Days between two dates

Subtracting two dates gives a `timedelta` - a length of time. Its `.days` is the
number of days - `INTCK('day', a, b)`, or `b - a`, in SAS:

```python run
from datetime import date, timedelta

start = date(2019, 4, 16)
report_date = date(2026, 9, 30)

age = report_date - start
print(age.days, "days |", round(age.days / 365.25, 1), "years")

print(report_date + timedelta(days=30))           # 30 days later
```

::: tip Try it
How many days are left from today to the end of this year? Use `date.today()` and
`date(year, 12, 31)`.
:::

## 7. Regular expressions: a pattern for many strings

### What a regular expression is

The string methods look for **one** exact text: `"EUR" in s`. A **regular
expression** (*regex*) describes a **set** of texts by their shape: "a date like
30.09.2026" covers every date in that format.

| Want | String method | Regular expression |
|---|---|---|
| contains `EUR` | `"EUR" in s` | `re.search(r"EUR", s)` |
| an L and 6 digits | `len(s) == 7 and s[0] == "L" and s[1:].isdigit()` | `re.fullmatch(r"L\d{6}", s)` |
| every date `dd.mm.yyyy` inside a text | - (a loop with `find` and checks) | `re.findall(r"\d{2}\.\d{2}\.\d{4}", s)` |

For a simple test, use the string methods - they are clearer. For a shape, use a
regex. In SAS the same patterns work with `PRXMATCH`; in SQL, `LIKE` does a small
part of it and `REGEXP_LIKE` the rest.

### `re.search` and the match object

The module `re` comes with Python. `re.search(pattern, text)` looks for the first
place where the pattern fits. It returns a **match object** - or `None` if the
pattern fits nowhere:

```python run
import re

comment = "Payment of 1 250,00 EUR received on 15.09.2026."

m = re.search(r"\d{2}\.\d{2}\.\d{4}", comment)
print(m)
print(m.group())          # the text that fits the pattern
print(m.start(), m.end())

print(re.search(r"USD", comment))     # None
```

The pattern `\d{2}\.\d{2}\.\d{4}` reads: two digits, a point, two digits, a point,
four digits. Section 8 explains every part.

In an `if`, a match object counts as true and `None` as false. So `if
re.search(...):` asks "is it there?" - like `if prxmatch(...) > 0` in SAS:

```python run
import re

for comment in ["Payment of 1 250,00 EUR received.", "Annual review done; no findings."]:
    if re.search(r"\d+,\d{2} EUR", comment):
        print("has an amount: ", comment)
    else:
        print("no amount:     ", comment)
```

The same test on the loan portfolio. The file `loan_comments.csv` (new today) has the
comments of the credit officers. How many of them mention a date in the format
`dd.mm.yyyy`?

```python run
import csv
import re

with open("data/loan_comments.csv", encoding="utf-8") as file:
    comments = list(csv.DictReader(file))

with_date = [c for c in comments if re.search(r"\d{2}\.\d{2}\.\d{4}", c["comment"])]
print(len(with_date), "of", len(comments), "comments")
print(with_date[0]["comment"])
```

### Raw strings: `r"..."`

Patterns use many backslashes: `\d`, `\.`, `\s`. In a normal string, Python itself
reads some pairs with a backslash first (`\n` is a new line, `\t` is a tab). A **raw
string** `r"..."` gives every backslash to the `re` module unchanged:

```python run
print("C:\new_folder")                # \n became a new line!
print(r"C:\new_folder")
```

Rule: **always write a pattern as a raw string**, `r"..."`.

::: tip Try it
Change the pattern of the first block of this section to find the amount
(`1 250,00`) instead of the date. Hint: digits, a space, digits, a comma, two digits:
`r"\d+ \d+,\d{2}"`.
:::

## 8. Writing a pattern

### One character

Letters and digits in a pattern mean themselves. These parts mean **one character**
of a kind:

| Pattern | One character that is |
|---|---|
| `.` | any character |
| `\.` | a point (the backslash removes the special meaning) |
| `\d` | a digit |
| `\s` | a space, a tab or a new line |
| `\w` | a letter, a digit or `_` |
| `[abc]` | `a`, `b` or `c` |
| `[A-Z]` | a capital Latin letter |
| `[A-Z0-9]` | a capital Latin letter or a digit |
| `[^0-9]` | **not** a digit (`^` first inside the brackets) |

```python run
import re

print(re.findall(r"2.26", "2026 2.26 2-26 2x26"))     # . is any character
print(re.findall(r"2\.26", "2026 2.26 2-26 2x26"))    # \. is a point
print(re.findall(r"\d", "L000123"))
print(re.findall(r"[^0-9]", "L000123"))
print(re.findall(r"[A-Z][A-Z][A-Z]", "100 EUR and 50 USD and 7 eur"))
```

`re.findall` returns a list with **all** the places where the pattern fits (section
9).

The characters with a special meaning are `. ^ $ * + ? { } [ ] \ | ( )`. Put a `\` in
front when you mean the character itself: `\.`, `\(`, `\+`.

### How many times

A **quantifier** after a character says how many times it repeats:

| Quantifier | Means |
|---|---|
| `+` | 1 or more |
| `*` | 0 or more |
| `?` | 0 or 1 (optional) |
| `{3}` | exactly 3 |
| `{2,4}` | 2 to 4 |
| `{2,}` | 2 or more |

```python run
import re

print(re.findall(r"\d+", "Overdue 35 days, 120 days, 5 days"))      # whole numbers
print(re.findall(r"\d{2}", "2026"))                                 # pairs of digits
print(re.findall(r"BG\d{2}", "BG80 bg12 BG7"))
print(re.findall(r"colou?r", "color colour"))                       # the u is optional
```

On the client register: the names typed with two or more spaces in a row - `\s{2,}`:

```python run
import csv
import re

with open("data/client_register.csv", encoding="utf-8") as file:
    names = [row["name"] for row in csv.DictReader(file)]

double = [name for name in names if re.search(r"\s{2,}", name)]
print(len(double), "names with extra spaces, e.g.", double[:3])
```

### Where: `^`, `$`, `\b`

These parts fit a **position**, not a character:

- `^` - the start of the text;
- `$` - the end of the text;
- `\b` - a word boundary: the place between a word character (`\w`) and another
  character.

```python run
import re

print(bool(re.search(r"^L", "L000001")), bool(re.search(r"^L", "XL000001")))
print(bool(re.search(r"\.$", "No findings.")))

text = "loan L000391; LL0001; L0003915"
print(re.findall(r"L\d{6}", text))           # also inside longer words
print(re.findall(r"\bL\d{6}\b", text))       # only whole words
```

### `LIKE` and regex

| SQL `LIKE` | Regex | |
|---|---|---|
| `_` | `.` | any one character |
| `%` | `.*` | any text, also empty |
| `'L%'` | `^L` | starts with L |
| `'%EUR'` | `EUR$` | ends with EUR |
| `'%EUR%'` | `EUR` | contains EUR |

::: tip Try it
Write a pattern that finds the three-letter currency codes (`EUR`, `USD`, ...) in
`"100 EUR, 50 usd, 20 GBP and EURO"` - whole words in capitals only. What do you
need so that `EURO` is not found?
:::

## 9. The functions of `re`

### `search`, `match`, `fullmatch`: where must the pattern fit?

| Function | Where the pattern must fit | SAS / SQL |
|---|---|---|
| `re.search(p, s)` | anywhere in the text | `PRXMATCH(p, s) > 0` in SAS, `LIKE '%...%'` in SQL |
| `re.match(p, s)` | at the **start** of the text | `LIKE '...%'` in SQL |
| `re.fullmatch(p, s)` | the **whole** text | `LIKE '...'`, `REGEXP_LIKE(s, '^...$')` in SQL |

```python run
import re

LOAN = r"L\d{6}"

for s in ["L000001", "L000001 ", "xL000001", "L0000012"]:
    found = bool(re.search(LOAN, s))
    at_start = bool(re.match(LOAN, s))
    whole = bool(re.fullmatch(LOAN, s))
    print(f"{s!r:>12} search={found!s:<6} match={at_start!s:<6} fullmatch={whole}")
```

To **validate** a value, use `fullmatch`. `search` says yes when the pattern is
**somewhere** in the text, also with other characters around it.

### `findall`: all matches

`findall` returns a **list of strings** - all the places where the pattern fits:

```python run
import re

comment = "Refinanced from loan L000391; L000048 and L000387 closed."
print(re.findall(r"L\d{6}", comment))
print(re.findall(r"L\d{6}", "no loans here"))       # an empty list
print(len(re.findall(r"L\d{6}", comment)))          # how many: REGEXP_COUNT in SQL
```

### `sub`: replace

`re.sub(pattern, replacement, text)` replaces **every** match - `PRXCHANGE` in SAS,
`REGEXP_REPLACE` in SQL:

```python run
import re

print(re.sub(r"\s+", " ", "  Iron   Retail \t ET ").strip())   # COMPBL in SAS
print(re.sub(r"\D", "", "BG 131-234 567"))                     # keep the digits only
print(re.sub(r"\d", "*", "card 4532 7711"))                    # hide the digits
```

`\D` is "not a digit": a capital letter turns the meaning around (`\S` is "not a
space", `\W` is "not a word character").

### Ignore the case: `re.IGNORECASE`

A **flag** changes how a pattern works. The most useful one ignores the case:

```python run
import re

text = "100 EUR, 50 eur, 20 Eur"
print(re.findall(r"\d+ EUR", text))
print(re.findall(r"\d+ EUR", text, flags=re.IGNORECASE))     # the short name: re.I
```

::: tip Try it
Count the comments of `loan_comments.csv` that contain the word `review` in any
case, with `re.search` and a flag. Then count them with a string method
(`"review" in text.lower()`). Is it the same number?
:::

## 10. Groups and alternatives

### Groups: take the match apart

Round brackets make a **group**. After a match, `group(1)`, `group(2)`, ... give the
text of each group, and `groups()` gives all of them as a tuple:

```python run
import re

m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", "received on 15.09.2026.")
print(m.group())                 # the whole match
print(m.group(1), m.group(2), m.group(3))
print(m.groups())

day, month, year = m.groups()
print(f"{year}-{month}-{day}")
```

In SAS: `PRXPOSN(re, 1, text)` after `PRXMATCH`.

With **one** group in the pattern, `findall` returns the text of the group. With
**several** groups, it returns a list of tuples:

```python run
import re

text = "Payment 1 250,00 EUR; payment 99,50 USD; fee 10,00 EUR"
print(re.findall(r"\d[\d ]*,\d{2} [A-Z]{3}", text))        # no group: the whole match
print(re.findall(r"(\d[\d ]*,\d{2}) [A-Z]{3}", text))      # one group: only the amount
print(re.findall(r"(\d[\d ]*,\d{2}) ([A-Z]{3})", text))    # two groups: tuples
```

### Alternatives: `|`

`a|b` fits `a` or `b`. Put the options in brackets when they are only one part of
the pattern:

```python run
import re

text = "Payment 1 250,00 EUR; payment 99,50 USD; fee 10,00 BGN"
print(re.findall(r"\d+,\d{2} (EUR|USD)", text))
```

The brackets also made a group, so `findall` returned only the currency. Write
`(?:...)` for brackets that only **keep parts together** and are not a group:

```python run
import re

text = "Payment 1 250,00 EUR; payment 99,50 USD; fee 10,00 BGN"
print(re.findall(r"\d+,\d{2} (?:EUR|USD)", text))

# an optional part: a point and digits, 0 or 1 time
print(re.findall(r"\d+(?:\.\d+)?", "rates 12.97 and 13 and 4.5"))
```

::: tip Try it
Write a pattern with three groups for `"Overdue 60 days. Reminder sent on
2026-04-24."` that gives the year, the month and the day of the date with
`groups()`.
:::

## 11. Validate and extract

### Validate: the patterns of our ids

Each pattern describes the **shape** of a valid value. With `fullmatch`, the whole
text must fit:

```python run
import re

PATTERNS = {
    "loan_id":   r"L\d{6}",
    "client_id": r"C\d{4}",
    "eik":       r"\d{9}|\d{13}",
    "iban_bg":   r"BG\d{2}[A-Z]{4}\d{6}[A-Z0-9]{8}",
    "date_bg":   r"\d{2}\.\d{2}\.\d{4}",
    "email":     r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}",
}

tests = {"loan_id": ["L000001", "L00001", "l000001"],
         "eik": ["175591301", "1965730713386", "12345678901"],
         "iban_bg": ["BG05TEST77018249464461", "BG05 TEST 7701", "DE89370400440532013000"],
         "date_bg": ["30.09.2026", "2026-09-30", "3.9.2026"],
         "email": ["yana.koleva@example.org", "office at example.net", "a@b"]}

for name, values in tests.items():
    for value in values:
        print(f"{name:<9}{value:<26}{bool(re.fullmatch(PATTERNS[name], value))}")
```

- The Bulgarian IBAN: `BG`, 2 check digits, 4 letters of the bank, 6 digits (the
  branch and the account type), 8 letters or digits of the account - 22 characters.
- The e-mail: some characters that are not `@` and not a space, an `@`, some more
  such characters, a point, 2 or more letters. This is a practical pattern, not the
  full official rule.

A whole column - the IBANs of the register. Clean them as in section 5, then check
the shape:

```python run
import csv
import re

IBAN_BG = r"BG\d{2}[A-Z]{4}\d{6}[A-Z0-9]{8}"

with open("data/client_register.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

ibans = [row["iban"].replace(" ", "").upper() for row in rows]
ok = sum(1 for x in ibans if re.fullmatch(IBAN_BG, x))
empty = ibans.count("")
print(f"{ok} valid shape, {empty} empty, {len(ibans) - ok - empty} wrong")
```

::: warning The shape is not the meaning
A regex checks the **form**. `31.09.2026` has the right shape, but there is no 31st
of September. So: first the shape with a regex, then the real check - for a date,
`strptime` (section 6).
:::

### Extract: values from free text

The comments of the credit officers are free text. A payment comment looks like
`Payment of 2 069,77 EUR received on 26.04.2026.` One pattern with groups takes the
amount and the parts of the date:

```python run
import re

PAYMENT = r"Payment of ([\d ]+,\d{2}) EUR received on (\d{2})\.(\d{2})\.(\d{4})"

m = re.search(PAYMENT, "Payment of 2 069,77 EUR received on 26.04.2026.")
print(m.groups())

amount = float(m.group(1).replace(" ", "").replace(",", "."))
print(amount, m.group(3), m.group(4))
```

On the file: the total of the payments received in September 2026.

```python run
import csv
import re

PAYMENT = r"Payment of ([\d ]+,\d{2}) EUR received on (\d{2})\.(\d{2})\.(\d{4})"

with open("data/loan_comments.csv", encoding="utf-8") as file:
    comments = list(csv.DictReader(file))

total = 0.0
count = 0
for c in comments:
    m = re.search(PAYMENT, c["comment"])
    if m and m.group(4) == "2026" and m.group(3) == "09":
        total += float(m.group(1).replace(" ", "").replace(",", "."))
        count += 1
print(count, "payments in September, total", f"{total:,.2f} EUR")
```

::: info The same in pandas and SQL
pandas: `df["iban"].str.fullmatch(pattern)` gives a column of `True` / `False`;
`str.contains`, `str.extract` and `str.replace(..., regex=True)` use patterns too
([lecture 14](./14-pandas-select-aggregate-join.md#text-and-dates-in-a-column)). Most databases have regex functions: `REGEXP_LIKE` (Oracle, MySQL),
`~` (PostgreSQL); MS SQL Server only since version 2025.

```python run
import pandas as pd

reg = pd.read_csv("data/client_register.csv", dtype=str).fillna("")
iban = reg["iban"].str.replace(" ", "").str.upper()
print(iban.str.fullmatch(r"BG\d{2}[A-Z]{4}\d{6}[A-Z0-9]{8}").value_counts())
```
:::

::: warning A regex is code: test it
A pattern that looks right can fit too much or too little. Test it on good **and**
bad examples, as the checks of the tasks do. [regex101.com](https://regex101.com)
(choose the flavour *Python*) shows what each part of a pattern fits.
:::

::: tip Try it
All loan ids that the comments **mention** in their text (`L` and 6 digits, whole
words): collect them with `findall` from every comment. How many different ids are
there?
:::

## 12. Summary

| Topic | Remember |
|-------|----------|
| Immutable | every method returns a new string: `s = s.strip()` |
| Case | `upper`, `lower`, `title` (fix legal forms after it); compare with `.lower()` on both sides |
| Spaces | `strip` / `lstrip` / `rstrip` at the ends; `" ".join(s.split())` = `COMPBL` |
| Find and test | `in`; `startswith((...))`; `find` gives -1; `count`; `isdigit`, `isalpha`, `isalnum` |
| Split and join | `split(",")` keeps empty fields; `split()` cuts at any spaces; `rsplit`, `partition`; `", ".join(strings)` |
| Replace | `replace(old, new)`; `removeprefix` / `removesuffix`; `zfill` |
| Cleaning | one function per column, `None` for what cannot be fixed; check against a trusted source |
| Numbers | know the format of the source; `replace`, then `float` |
| Dates | `date.fromisoformat`; `datetime.strptime(s, "%d.%m.%Y").date()`; `strftime`; `b - a` gives a `timedelta` |
| Patterns | always `r"..."`; `.` any character, `\.` a point; `\d`, `\s`, `\w`; `[A-Z]`, `[^0-9]` |
| Quantifiers | `+` `*` `?` `{n}` `{n,m}` |
| Positions | `^` start, `$` end, `\b` word boundary |
| Functions | `search` (anywhere), `match` (start), `fullmatch` (the whole text - to validate), `findall`, `sub`; `re.I` |
| Groups | `( )` and `group(1)`, `groups()`; `findall` with groups; `a\|b`; `(?:...)` is not a group |
| SAS / SQL | `PRXMATCH` = `search`; `PRXPOSN` = `group`; `PRXCHANGE` = `sub`; `LIKE` `_` / `%` = `.` / `.*` |

## Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 07-text-and-regex/practice/task1-case-and-spaces.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-case-and-spaces.py` | Normalise names, cities and codes: case, spaces, prefixes |
| 2 | `task2-predict-strings.py` | Predict: `split`, `strip`, `find`, `join`, `replace`, slices |
| 3 | `task3-split-join.py` | Settings `key=value;...` into a dict and back; `SCAN`; a CSV line |
| 4 | `task4-identifiers.py` | Clean client ids, EIKs, IBANs and e-mails |
| 5 | `task5-dates.py` | Dates from text and back; days between; whole years |
| 6 | `task6-first-patterns.py` | Write patterns: ids, codes, currencies, whole words |
| 7 | `task7-predict-regex.py` | Predict `findall`, `search`, `fullmatch`, `sub` |
| 8 | `task8-validate.py` | Validators with `fullmatch`: loan id, EIK, IBAN, e-mail, date |
| 9 | `task9-extract.py` (Optional) | Loan ids, dates, amounts and percents from comments |

Three more files are for the [Self-study](#self-study) topics - do them after you
read the topic:

| Task | File | Self-study topic |
|------|------|------------------|
| 10 | `task10-amounts.py` | Numbers in any format; `translate` |
| 11 | `task11-groups.py` | Named groups |
| 12 | `task12-sub.py` | Greedy and lazy; back-references; a function as the replacement |

## Homework

1. `07-text-and-regex/homework.py` (in the homework repository): **clean the client
   register** - a function for each column of `client_register.csv`, then the whole
   file as a list of clean records, with a summary: how many values were fixed and
   how many could not be fixed, per column. The last part takes the payments out of
   the comments with a regular expression. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: `07-text-and-regex/homework2-comments.py` - **read the comments**: find
   the type of every comment of `loan_comments.csv`, take out the amounts of the
   payments, the new maturities and the IBANs, and compare the IBANs with the
   register.

## Self-study

This part is not covered in class. It is for reading at home. The first six topics
continue the string methods and the dates; the last six continue the regular
expressions. Nothing here is needed for the practice tasks 1 - 9 or for the
homework.

### Padding and alignment

`rjust`, `ljust` and `center` pad to a width with any character:

```python run
print(repr("EUR".ljust(6)), repr("EUR".rjust(6)), repr("EUR".center(7, "*")))
```

A fixed-width line - some old systems still want them. The f-string format spec of
[session 1](./01-intro-syntax-types.md#formatting-the-values) does the same, and is easier to read:

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

**Exercise**

1. Print the numbers 1, 25 and 400 as loan ids `L000001`, `L000025`, `L000400` -
   once with `zfill`, once with an f-string.

::: details Answer
```python
for n in [1, 25, 400]:
    print("L" + str(n).zfill(6), f"L{n:06d}")
```
:::

### `translate`: change or delete characters

`str.maketrans` builds a table of character changes, `translate` applies it - in one
pass. The SAS `TRANSLATE` and `COMPRESS(s, chars)`:

```python run
swap = str.maketrans({",": ".", ".": ","})
print("1,234.56".translate(swap))                    # swap , and . at once

drop = str.maketrans("", "", " -.")                  # the third argument: delete these
print("C-00 26".translate(drop))
print("131 234-567.".translate(drop))
```

Why not two `replace` calls? Because the second call also changes the result of the
first one:

```python run
s = "1,234.56"
print(s.replace(",", ".").replace(".", ","))     # '1,234,56' - wrong
print(s.replace(",", "X").replace(".", ",").replace("X", " "))   # a temporary marker
```

And back: a number in the Bulgarian format for a report. The format spec gives the
English format; then swap the characters with `translate`:

```python run
def format_bg(value, decimals=2):
    """1234567.891 -> '1 234 567,89'"""
    return f"{value:,.{decimals}f}".translate(str.maketrans({",": " ", ".": ","}))

print(format_bg(1234567.891))
print(format_bg(644.25))
print(format_bg(-5000, 0))
```

**Exercise**

1. `"BG80 test 9661-1020 3456 78"`: make it upper case, without spaces and dashes -
   in one line with `translate` and `upper`.

::: details Answer
```python
drop = str.maketrans("", "", " -")
print("BG80 test 9661-1020 3456 78".translate(drop).upper())    # BG80TEST96611020345678
```
:::

### Numbers in any format

The `turnover` column of the register has several formats:

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

**Exercise**

1. What does `parse_amount("12,5")` give? And `parse_amount("1,234")`? Predict, then
   run. Which of the two answers would be wrong for a source in the English format?

::: details Answer
`parse_amount("12,5")` gives `12.5`: one digit after the comma, so the comma is the
decimal separator. `parse_amount("1,234")` gives `1234.0`: three digits after the
comma, so the comma separates the thousands. For a source in the English format the
first answer is wrong: there `12,5` cannot be a number at all, and a rule that
accepts it hides a typing error.
:::

### Several date formats, and month ends

The `registered` column of the register has five formats. Decide the format by the **shape** of the
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

::: details Advanced: month names and the language
`%b` and `%B` follow the **locale**. By default Python uses English month names, but
if a program (or a library) switches the locale with `locale.setlocale`, `%b` expects
the month names of that language, and `strptime("8 Jun 2014", "%d %b %Y")` can fail.
For data, prefer numeric formats. If a source has English month names, a small
dictionary `{"Jan": 1, ...}` ([session 6](./06-dictionaries.md)) is the safe way.
:::

The first and the last day of a month - the **report dates** of risk reporting:

```python run
from datetime import date, timedelta

d = date(2026, 2, 17)
first = d.replace(day=1)                                       # INTNX('month', d, 0, 'b')
next_first = (first + timedelta(days=32)).replace(day=1)
last = next_first - timedelta(days=1)                          # INTNX('month', d, 0, 'e')
print(first, last)
```

(Adding **months** is not in `datetime`: a month has no fixed length. [Lecture 15](./15-pandas-reports.md#month-ends-intnx)
does it with pandas; [lecture 9](./09-modules-and-git.md#datetime-and-calendar-report-dates) shows the standard library.)

On the file - how long each client has been a client:

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

**Exercise**

1. Check the parsed dates against `clients.csv`, where `client_since` is a clean ISO
   date: are all 150 equal?

::: details Answer
```python
with open("data/clients.csv", encoding="utf-8") as file:
    trusted = [date.fromisoformat(row["client_since"]) for row in csv.DictReader(file)]
print(since == trusted)        # True (after the block above)
```
:::

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
3.12 - 3.14 on Windows uses the Windows encoding of the computer (often cp1252 or
cp1251), and the same script gives different results on different computers. (From
Python 3.15 on, UTF-8 is the default everywhere. Still write it: the script may run
on an older Python.)

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
(Writing files with `csv`: [lecture 8](./08-errors-and-files.md#write-csv-writer-and-csv-dictwriter).)
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

### Greedy and lazy quantifiers

`*` also matches **nothing** - zero digits are "0 or more". With `findall`, that gives
empty strings between the matches:

```python run
import re

print(re.findall(r"\d*", "a12b3"))       # ['', '12', '', '3', ''] - the empty matches too
print(re.findall(r"\d+", "a12b3"))       # ['12', '3'] - what was meant
```

When you want "at least one", write `+`, not `*`.

Quantifiers are **greedy**: they take as much text as they can, and give back only
what is needed for the rest of the pattern to match:

```python run
import re

text = 'name="North Hotels" form="ET"'
print(re.findall(r'".*"', text))       # from the first " to the LAST "
```

A `?` after the quantifier makes it **lazy**: as little as possible.

```python run
import re

text = 'name="North Hotels" form="ET"'
print(re.findall(r'".*?"', text))      # each quoted part
print(re.findall(r'"[^"]*"', text))    # the same, often clearer: anything but a quote
```

::: warning `.*` takes too much
`.*` is the most common cause of a wrong match: it runs to the end of the line, then
steps back. When the text between two markers cannot contain the marker, write a
class with `^`: `"[^"]*"`, `\([^)]*\)`.
:::

**Exercise**

1. In `"(valuation report from 12.06.2026) (checked 2026-06-15)"`, find the text
   inside each pair of brackets. First try `\(.*\)`, then make it lazy.

::: details Answer
```python
import re

text = "(valuation report from 12.06.2026) (checked 2026-06-15)"
print(re.findall(r"\(.*\)", text))       # one match: from the first ( to the last )
print(re.findall(r"\(.*?\)", text))      # two matches
print(re.findall(r"\(([^)]*)\)", text))  # two matches, without the brackets
```
:::

### More functions of `re`

**`finditer`: the match objects.** `finditer` gives the **match objects**, with their positions - when you need more
than the text:

```python run
import re

comment = "Refinanced from loan L000391; L000048 and L000387 closed."
for m in re.finditer(r"L\d{6}", comment):
    print(m.group(), "at", m.start())
```

**`split` with a pattern.** `re.split` cuts at every match - when the separators vary:

```python run
import re

print(re.split(r"\s*[;,]\s*", "retail; sme,corporate ,  project"))
print(re.split(r"\s+", "  Iron   Retail  ET ".strip()))
```

**`re.MULTILINE`.** With a text of many lines, `^` and `$` mean the start and the end of the **whole**
text. The flag `re.MULTILINE` (`re.M`) makes them work **per line**:

```python run
import re

log = """2026-09-30 OK loaded 400 loans
2026-09-30 ERROR bad date in row 58
2026-09-30 OK loaded 150 clients
2026-09-30 ERROR unknown loan L999999"""

print(re.findall(r"^\S+ ERROR (.*)$", log))                  # nothing: ^ is the start of the text
print(re.findall(r"^\S+ ERROR (.*)$", log, flags=re.M))      # one per line
```

**`re.compile`: a pattern used many times.** `re.compile` turns a pattern into an object with the same methods. Give it a name at
the top of the script, and use it in a loop - it reads well and is checked once:

```python run
import csv
import re

LOAN_ID = re.compile(r"\bL\d{6}\b")

with open("data/loan_comments.csv", encoding="utf-8") as file:
    comments = list(csv.DictReader(file))

mentioned = [(c["loan_id"], LOAN_ID.findall(c["comment"])) for c in comments]
others = [(loan, found) for loan, found in mentioned if found]
print(len(others), "comments mention another loan, e.g.", others[:3])
```

**`re.subn`: count the replacements.** `re.subn` works like `re.sub`, and also returns the number of replacements - useful in a
cleaning report:

```python run
import re

text, n = re.subn(r"\s{2,}", " ", "a  b   c d")
print(text, "|", n, "replacements")
```

**`re.escape`.** When a text that you look for has special characters, `re.escape(text)` puts the backslashes for you:

```python run
import re

print(re.escape("12.5% (net)"))
print(re.findall(re.escape("(net)"), "12.5% (net), 14% (gross), 3% (net)"))
```

**Exercise**

1. Split `"retail;sme , corporate,project"` into the four words with one
   `re.split`, without spaces around the words.

::: details Answer
```python
import re

print(re.split(r"\s*[;,]\s*", "retail;sme , corporate,project"))
```
:::

### Named groups, back-references, a function as the replacement

#### Named groups: `(?P<name>...)`

With many groups, numbers are hard to follow. Give each group a **name**:

```python run
import re

pattern = r"Rate changed from (?P<old>[\d.]+)% to (?P<new>[\d.]+)% as of (?P<date>\d{2}\.\d{2}\.\d{4})"
m = re.search(pattern, "Rate changed from 12.97% to 13.47% as of 22.03.2026.")

print(m.group("old"), m.group("new"), m.group("date"))
print(m.groupdict())                    # all groups as a dictionary
print(float(m["new"]) - float(m["old"]))     # m["new"] is the same as m.group("new")
```

A group that did not take part in the match gives `None` - for example an optional
part:

```python run
import re

PAYMENT = re.compile(r"(\d[\d ]*),(\d{2})(?: (EUR|USD))?")
print(PAYMENT.search("paid 1 250,00 EUR").groups())
print(PAYMENT.search("paid 99,50").groups())          # the currency is missing
print(PAYMENT.search("paid 99,50").groups("EUR"))     # a default for missing groups
```

A list of records from a text - `finditer` with named groups and `groupdict()`, one
dictionary per match ([session 6](./06-dictionaries.md)):

```python run
import re

text = "Rate changed from 12.97% to 13.47% as of 22.03.2026. Rate changed from 4.17% to 2.67% as of 23.03.2026."
RATE = re.compile(r"from (?P<old>[\d.]+)% to (?P<new>[\d.]+)% as of (?P<date>[\d.]+\d)")
records = [m.groupdict() for m in RATE.finditer(text)]
print(records)
print([round(float(r["new"]) - float(r["old"]), 2) for r in records])
```

#### Back-references: reorder the parts

In the replacement, `\1`, `\2` (or `\g<name>`) insert the text of a group. A date
`dd.mm.yyyy` becomes ISO:

```python run
import re

text = "Payment received on 15.09.2026, review on 01.03.2027."
print(re.sub(r"(\d{2})\.(\d{2})\.(\d{4})", r"\3-\2-\1", text))
print(re.sub(r"(?P<d>\d{2})\.(?P<m>\d{2})\.(?P<y>\d{4})", r"\g<y>-\g<m>-\g<d>", text))
```

::: warning The replacement is a raw string too
Without `r`, Python reads `"\1"` itself, as the character number 1 - the group is
lost:

```python run
import re

print(repr(re.sub(r"(\d{2})\.(\d{2})", "\2/\1", "15.09")))    # '\x02/\x01' - not a date
print(repr(re.sub(r"(\d{2})\.(\d{2})", r"\2/\1", "15.09")))   # '09/15'
```
:::

#### A function as the replacement

When the new text must be **calculated**, give `sub` a function: it gets the match
object and returns the replacement. Every amount in a text, converted to thousands
of EUR:

```python run
import re

def to_thousands(m):
    value = float(m.group(1).replace(" ", "").replace(",", "."))
    return f"{value / 1000:.1f}k EUR"

text = "Payment of 2 069,77 EUR received; then 45 544,40 EUR."
print(re.sub(r"(\d[\d ]*,\d{2}) EUR", to_thousands, text))
```

Normalise all legal forms in company names with one pattern and a dictionary:

```python run
import re

FORMS = {"OOD": "OOD", "EOOD": "EOOD", "AD": "AD", "EAD": "EAD", "ET": "ET", "LTD": "Ltd."}
FORM_AT_END = re.compile(r"\b((?:[A-Za-z]\.?){2,4})\.?$")

def fix_form(m):
    bare = m.group(1).replace(".", "").upper()
    return FORMS.get(bare, m.group(1))

for name in ["Green Build E.A.D.", "Blue Wines eood", "Rila Print e.o.o.d.", "North Hotels ET", "Iron Foods ad"]:
    print(f"{name:<22} -> {FORM_AT_END.sub(fix_form, name)}")
```

::: details Advanced: patterns that take forever
Patterns with nested quantifiers, like `(\d+)+$`, can take a very long time on a long
text that almost matches ("catastrophic backtracking"). Keep patterns simple, avoid
`(...+)+`, and do not run patterns written by other people on big data without a
test. Python 3.11 added *possessive* quantifiers (`*+`, `++`) and atomic groups
`(?>...)` that prevent it - rarely needed in data work.
:::

**Exercise**

1. Write one pattern with named groups for `"Overdue 60 days. Reminder sent to
   radoslav.iliev@example.org on 2026-04-24."` that gives the days, the e-mail and
   the date with `groupdict()`.

::: details Answer
```python
import re

text = "Overdue 60 days. Reminder sent to radoslav.iliev@example.org on 2026-04-24."
m = re.search(r"Overdue (?P<days>\d+) days.*sent to (?P<email>\S+) on (?P<date>\d{4}-\d{2}-\d{2})", text)
print(m.groupdict())
```
:::

### Extraction from free text

The comments of the credit officers (`loan_comments.csv`, new today) are free text.
Each type of comment has its own shape:

```python run
import csv
from collections import Counter

with open("data/loan_comments.csv", encoding="utf-8") as file:
    comments = list(csv.DictReader(file))

print(len(comments), "comments")
print(Counter(c["comment"].split()[0] for c in comments))
for c in comments[:6]:
    print(c["comment"])
```

Classify every comment with a dictionary **type -> pattern**: the first pattern
that matches gives the type - like a `CASE WHEN ... LIKE` chain in SQL:

```python run
import csv
import re
from collections import Counter

TYPES = {
    "payment": r"^Payment of",
    "restructuring": r"restructuring",
    "collateral": r"^Collateral revalued",
    "reminder": r"^Overdue \d+ days",
    "refinancing": r"^Refinanced from loan L\d{6}",
    "disbursement": r"^Disbursement to IBAN",
    "guarantee": r"\bEIK \d{9}",
    "rate change": r"^Rate changed",
    "review": r"^Annual review",
}

def comment_type(text):
    for name, pattern in TYPES.items():
        if re.search(pattern, text):
            return name
    return "other"

with open("data/loan_comments.csv", encoding="utf-8") as file:
    print(Counter(comment_type(c["comment"]) for c in csv.DictReader(file)))
```

#### Amounts and their currency

A Bulgarian amount with groups of thousands: 1 to 3 digits, then any number of
"a space and 3 digits", then a comma and 2 digits:

```python run
import re

BG_AMOUNT = r"\d{1,3}(?: \d{3})*,\d{2}"
text = "Payment of 2 069,77 EUR, then 45 544,40 EUR and 1 250 000,00 EUR; ref 12345,6"
print(re.findall(BG_AMOUNT, text))
print([bool(re.fullmatch(BG_AMOUNT, s)) for s in ["1 234,56", "1234,56", "12 34,56", "1 234,5"]])
```

Amounts are written in different styles: `2 069,77 EUR`, `20,960.03 EUR`, `99,400
EUR`. One pattern for "digits with spaces, commas and points, then a currency", and
the `parse_amount` of [Numbers in any format](#numbers-in-any-format) for the number:

```python run
import re

AMOUNT = re.compile(r"(\d[\d ,.]*\d)\s?(EUR|USD)")

def parse_amount(raw):
    s = raw.replace(" ", "")
    last = max(s.rfind(","), s.rfind("."))
    if last >= 0 and len(s) - last - 1 in (1, 2):
        whole, decimals = s[:last], s[last + 1:]
    else:
        whole, decimals = s, "0"
    return float(whole.replace(",", "").replace(".", "") + "." + decimals)

for text in ["Payment of 2 069,77 EUR received on 26.04.2026.",
             "Refinanced from loan L000391; old balance 20,960.03 EUR closed.",
             "Collateral revalued: 99,400 EUR (valuation report from 12.06.2026)."]:
    for number, currency in AMOUNT.findall(text):
        print(f"{number!r:<14}{currency} -> {parse_amount(number)}")
```

The total of the payments received in September 2026:

```python run
import csv
import re

PAYMENT = re.compile(r"Payment of (?P<amount>[\d ]+,\d{2}) EUR received on (?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})")

with open("data/loan_comments.csv", encoding="utf-8") as file:
    comments = list(csv.DictReader(file))

total, count = 0.0, 0
for c in comments:
    m = PAYMENT.search(c["comment"])
    if m and m["year"] == "2026" and m["month"] == "09":
        total += float(m["amount"].replace(" ", "").replace(",", "."))
        count += 1
print(count, "payments in September, total", f"{total:,.2f} EUR")
```

#### Dates in two formats

The comments use `dd.mm.yyyy`, `dd/mm/yyyy` and ISO dates. One pattern with
alternatives - and a **named group per part**, in both orders:

```python run
import re
from datetime import date

DATE = re.compile(r"(?P<d>\d{2})[./](?P<m>\d{2})[./](?P<y>\d{4})|(?P<y2>\d{4})-(?P<m2>\d{2})-(?P<d2>\d{2})")

def dates_in(text):
    result = []
    for m in DATE.finditer(text):
        if m["y"]:
            result.append(date(int(m["y"]), int(m["m"]), int(m["d"])))
        else:
            result.append(date(int(m["y2"]), int(m["m2"]), int(m["d2"])))
    return result

print(dates_in("Overdue 60 days. Reminder sent on 2026-04-24."))
print(dates_in("Disbursement confirmed on 22/09/2026; next review 01.03.2027."))
```

#### IBANs, with or without spaces

An IBAN in a comment can be written in groups of four. Allow an optional space
between the groups, then remove the spaces:

```python run
import re

IBAN_IN_TEXT = re.compile(r"BG\d{2}(?: ?[A-Z0-9]{4}){4} ?[A-Z0-9]{2}")

for text in ["Disbursement to IBAN BG64 FAKE 2979 3117 0461 39 confirmed on 22/09/2026.",
             "Disbursement to IBAN BG46FAKE96787581635390 confirmed on 18/06/2026."]:
    m = IBAN_IN_TEXT.search(text)
    print(m.group().replace(" ", ""))
```

#### Does the comment agree with the register?

A real check: the IBAN in a disbursement comment must be the IBAN of the client of
the loan. Three files, a dictionary for each lookup ([session 6](./06-dictionaries.md#_5-lookup-tables-and-nomenclatures)):

```python run
import csv
import re

IBAN_IN_TEXT = re.compile(r"BG\d{2}(?: ?[A-Z0-9]{4}){4} ?[A-Z0-9]{2}")

with open("data/loans.csv", encoding="utf-8") as file:
    client_of = {r["loan_id"]: r["client_id"] for r in csv.DictReader(file)}
with open("data/client_register.csv", encoding="utf-8") as file:
    iban_of = {}
    for r in csv.DictReader(file):
        client_id = "C" + re.sub(r"\D", "", r["client_id"]).zfill(4)    # clean the id
        iban_of[client_id] = r["iban"].replace(" ", "").upper()

checked = differ = 0
with open("data/loan_comments.csv", encoding="utf-8") as file:
    for c in csv.DictReader(file):
        m = IBAN_IN_TEXT.search(c["comment"])
        if m:
            checked += 1
            if m.group().replace(" ", "") != iban_of[client_of[c["loan_id"]]]:
                differ += 1
print(checked, "IBANs in comments,", differ, "differ from the register")
```

(`re.sub(r"\D", "", ...)` keeps only the digits - section 9.)

The same check for the EIKs in the guarantee comments - are they EIKs of companies
in the register?

```python run
import csv
import re

with open("data/client_register.csv", encoding="utf-8") as file:
    known = {re.sub(r"\D", "", r["eik"]) for r in csv.DictReader(file) if r["eik"]}

with open("data/loan_comments.csv", encoding="utf-8") as file:
    found = [m.group(1) for c in csv.DictReader(file)
             for m in [re.search(r"\bEIK (\d{9}(?:\d{4})?)\b", c["comment"])] if m]

print(len(found), "EIKs in comments;", sum(1 for e in found if e in known), "known in the register")
```

(`for m in [...]` inside the comprehension gives the match a name, so it is computed
once. Python 3.8+ also has `:=`, the "walrus" operator, for the same.)

**Exercise**

1. Take the **new maturity** out of every restructuring comment (`"... new maturity
   2034-11-04."`) and find the latest one.

::: details Answer
```python
import csv
import re

with open("data/loan_comments.csv", encoding="utf-8") as file:
    texts = [row["comment"] for row in csv.DictReader(file)]

found = [m.group(1) for t in texts for m in [re.search(r"new maturity (\d{4}-\d{2}-\d{2})", t)] if m]
print(len(found), max(found))      # ISO dates sort correctly as text
```
:::

### Lookarounds and verbose patterns

A **lookaround** checks what is before or after a position, without making it part of
the match:

| Syntax | Means |
|---|---|
| `X(?=Y)` | X, if Y follows |
| `X(?!Y)` | X, if Y does not follow |
| `(?<=Y)X` | X, if Y is before it |
| `(?<!Y)X` | X, if Y is not before it |

```python run
import re

text = "Rate changed from 12.97% to 13.47%; fee 25.00 EUR"
print(re.findall(r"\d+\.\d{2}(?=%)", text))            # numbers followed by %
print(re.findall(r"\d+\.\d{2}(?!%)\b", text))          # numbers not followed by %
print(re.findall(r"(?<=IBAN )\S+", "to IBAN BG46FAKE96787581635390 confirmed"))
```

Long patterns are hard to read. With `re.VERBOSE` (`re.X`), spaces in the pattern are
ignored and `#` starts a comment - the pattern can be written on several lines:

```python run
import re

IBAN_BG = re.compile(r"""
    BG              # the country
    \d{2}           # the check digits
    [A-Z]{4}        # the bank
    \d{4}           # the branch
    \d{2}           # the account type
    [A-Z0-9]{8}     # the account
""", re.VERBOSE)

print(bool(IBAN_BG.fullmatch("BG05TEST77018249464461")))
```

**Exercises**

1. Find the amounts that are **followed** by ` EUR`, without taking ` EUR` into the
   match, in `"paid 2 069,77 EUR and 15,00 USD and 99,50 EUR"`.
2. Rewrite the e-mail pattern of section 11 with `re.VERBOSE` and a comment per part.

::: details Answer
1. `re.findall(r"\d[\d ]*,\d{2}(?= EUR)", text)` gives `['2 069,77', '99,50']`.
2.
```python
EMAIL = re.compile(r"""
    [^@\s]+         # the user: no @, no spaces
    @
    [^@\s]+         # the domain name
    \.[A-Za-z]{2,}  # a point and the top-level domain
""", re.VERBOSE)
```
:::

### Check digits: IBAN and EIK

The shape is half of the check. Both an IBAN and an EIK have **check digits**,
computed from the other digits, that catch most typing errors.

**IBAN (ISO 13616):** move the first four characters to the end, replace each letter
by a number (`A` = 10, `B` = 11, ..., `Z` = 35), and read it all as one big number.
It must give the remainder **1** when divided by 97. Python's `int` has no size
limit, so this is two lines:

```python run
import re

def iban_ok(iban):
    s = iban.replace(" ", "").upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", s):
        return False
    digits = "".join(str(int(ch, 36)) for ch in s[4:] + s[:4])     # int("B", 36) is 11
    return int(digits) % 97 == 1

print(iban_ok("BG05 TEST 7701 8249 4644 61"))
print(iban_ok("BG06 TEST 7701 8249 4644 61"))       # one digit changed
```

**EIK (BULSTAT), 9 digits:** multiply the first 8 digits by the weights 1, 2, ..., 8,
and take the sum modulo 11. If it is 10, use the weights 3, 4, ..., 10 instead; if it
is 10 again, the check digit is 0. The result must be the 9th digit.

```python run
def eik9_ok(eik):
    if len(eik) != 9 or not eik.isdigit():
        return False
    d = [int(c) for c in eik]
    s = sum(x * w for x, w in zip(d[:8], range(1, 9))) % 11
    if s == 10:
        s = sum(x * w for x, w in zip(d[:8], range(3, 11))) % 11 % 10
    return s == d[8]

print(eik9_ok("175591301"), eik9_ok("175591302"))
```

(The 13-digit EIK of a branch has a second check digit for the last 4 digits, with the
weights 2, 7, 3, 5 - and 4, 9, 5, 7 if the first sum gives 10.)

**Exercises**

1. Find the IBANs of the register with a valid shape but wrong check digits. How
   many are there?
2. Find the 9-digit EIKs of the register (after cleaning) whose check digit is wrong.

::: details Answer
```python
import csv
with open("data/client_register.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

bad_ibans = [r["client_id"] for r in rows if r["iban"] and not iban_ok(r["iban"])]
print(bad_ibans)         # 2 clients

eiks = [(r["client_id"], r["eik"].upper().removeprefix("BG").replace(" ", "")) for r in rows if r["eik"]]
print([cid for cid, e in eiks if len(e) == 9 and not eik9_ok(e)])
```
The register has two IBANs and three EIKs with wrong check digits - typing errors
that a shape check cannot find.
:::

## Read more

- Reference: [String methods](https://docs.python.org/3/library/stdtypes.html#string-methods),
  [`datetime`](https://docs.python.org/3/library/datetime.html) (the table of
  [format codes](https://docs.python.org/3/library/datetime.html#format-codes)),
  [`re`](https://docs.python.org/3/library/re.html)
- [Regular expression HOWTO](https://docs.python.org/3/howto/regex.html) (the official
  tutorial)
- [regex101.com](https://regex101.com) - test a pattern and see what each part
  fits (choose *Python*)
- [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) (encodings, normalisation)
- Real Python: [Strings and character data](https://realpython.com/python-strings/),
  [Using Python datetime to work with dates and times](https://realpython.com/python-datetime/),
  [Regular expressions: regexes in Python](https://realpython.com/regex-python/)

**Next session:** errors and files - catch errors instead of stopping, read and write
CSV, JSON and Excel files, and load data with bad rows the way a SAS log would report
them.
