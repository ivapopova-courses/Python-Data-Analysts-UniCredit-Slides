---
title: 8. Regular expressions
---

# 8. Regular expressions

<div class="lecture-meta">
  <span>Session 8</span><span>practice: <code>08-regular-expressions/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- describe the **shape** of a text with a pattern: "an L and six digits", "BG, two
  digits, four letters, ...";
- find, check and extract with the `re` module - the Python `PRXMATCH`, `LIKE` and
  `REGEXP_LIKE`;
- use groups to take a text apart: the day, the month and the year of a date; the
  amount and the currency of a payment;
- validate a whole column of ids, IBANs, e-mails and dates;
- pull amounts, dates, IBANs and loan ids out of free-text comments;
- replace with patterns - the Python `PRXCHANGE` and `REGEXP_REPLACE`.

From SAS to Python - which comments mention an IBAN?

```sas
data with_iban;
    set comments;
    if prxmatch('/BG\d{2}\s?[A-Z]{4}/', comment) > 0;
run;
```

```python run
import csv
import re

with open("data/loan_comments.csv", encoding="utf-8") as file:
    comments = list(csv.DictReader(file))

with_iban = [c for c in comments if re.search(r"BG\d{2}\s?[A-Z]{4}", c["comment"])]
print(len(with_iban), "of", len(comments), "comments mention an IBAN")
for c in with_iban[:3]:
    print(c["loan_id"], c["comment"])
```

`r"BG\d{2}\s?[A-Z]{4}"` reads: `BG`, two digits, maybe a space, four capital
letters. By the end of today you will read and write such patterns.

## 1. What a regular expression is

### A pattern for many strings

The string methods of session 7 look for **one** exact text: `"EUR" in s`. A
**regular expression** (*regex*) describes a **set** of texts by their shape: "a
date like 30.09.2026" covers every date in that format.

| Want | String method | Regular expression |
|---|---|---|
| contains `EUR` | `"EUR" in s` | `re.search(r"EUR", s)` |
| starts with `L` | `s.startswith("L")` | `re.search(r"^L", s)` |
| an L and 6 digits | `len(s) == 7 and s[0] == "L" and s[1:].isdigit()` | `re.fullmatch(r"L\d{6}", s)` |
| any date `dd.mm.yyyy` inside a text | - (a loop with `find` and checks) | `re.findall(r"\d{2}\.\d{2}\.\d{4}", s)` |

Simple tests: use the string methods - they are clearer. Patterns: use a regex.
The same check, both ways:

```python run
import re

ids = ["L000001", "L00001", "LX00001", "L0000012"]
print([len(s) == 7 and s[0] == "L" and s[1:].isdigit() for s in ids])
print([bool(re.fullmatch(r"L\d{6}", s)) for s in ids])
```

### `re.search` and the match object

The module `re` comes with Python. `re.search(pattern, text)` looks for the first
place where the pattern matches. It returns a **match object** - or `None` if there
is no match:

```python run
import re

comment = "Payment of 1 250,00 EUR received on 15.09.2026."

m = re.search(r"\d{2}\.\d{2}\.\d{4}", comment)
print(m)
print(m.group())          # the text that matched
print(m.start(), m.end(), m.span())

print(re.search(r"USD", comment))     # None
```

A match object is "true" and `None` is "false", so `if re.search(...):` asks "is it
there?" - like `if prxmatch(...) > 0` in SAS:

```python run
import re

for comment in ["Payment of 1 250,00 EUR received.", "Annual review done; no findings."]:
    if re.search(r"\d+,\d{2} EUR", comment):
        print("has an amount: ", comment)
    else:
        print("no amount:     ", comment)
```

The same test on the loan portfolio: how many of the comments mention a date in the
format `dd.mm.yyyy`?

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
reads some backslash pairs first (`\n` is a new line, `\b` a backspace). A **raw
string** `r"..."` gives every backslash to the `re` module unchanged:

```python run
print(len("\b"), len(r"\b"))          # one control character vs a backslash and a b
print("C:\new_folder")                # \n became a new line!
print(r"C:\new_folder")
```

Rule: **always write patterns as raw strings**, `r"..."`.

::: tip Try it
Change the pattern of the first block of this section to find the amount
(`1 250,00`) instead of the date. Hint: digits, a space, digits, a comma, two digits:
`r"\d+ \d+,\d{2}"`.
:::

## 2. Characters and classes

### Literal characters and `.`

Letters and digits match themselves. The **point** `.` matches **any one character**
(except a new line). To match a real point, escape it: `\.`

```python run
import re

print(re.findall(r"EUR", "EUR 100, eur 200, EUR 300"))
print(re.findall(r"2.26", "2026 2.26 2-26 2x26"))     # . is any character
print(re.findall(r"2\.26", "2026 2.26 2-26 2x26"))    # \. is a point
```

The characters with a special meaning are `. ^ $ * + ? { } [ ] \ | ( )`. Escape them
with `\` when you mean the character itself; `re.escape(text)` does it for you:

```python run
import re

print(re.escape("12.5% (net)"))
print(re.findall(re.escape("(net)"), "12.5% (net), 14% (gross), 3% (net)"))
```

### Classes: `[...]`

Square brackets match **one** character from a set:

| Pattern | Matches one character that is |
|---|---|
| `[abc]` | `a`, `b` or `c` |
| `[0-9]` | a digit |
| `[A-Z]` | a capital Latin letter |
| `[A-Za-z0-9]` | a Latin letter or a digit |
| `[^0-9]` | **not** a digit (`^` first inside the brackets) |
| `[.,]` | a point or a comma (inside brackets, `.` is a point) |

```python run
import re

print(re.findall(r"[0-9]", "L000123"))
print(re.findall(r"[^0-9]", "L000123"))
print(re.findall(r"[.,]", "1.234.567,89"))
print(re.findall(r"[A-Z][A-Z][A-Z]", "100 EUR and 50 USD and 7 eur"))
```

### Shorthand classes

| Shorthand | Means | The capital means "not" |
|---|---|---|
| `\d` | a digit, `[0-9]` | `\D` not a digit |
| `\w` | a "word" character: a letter, a digit or `_` | `\W` |
| `\s` | a space, a tab, a new line | `\S` |

```python run
import re

text = "Overdue 35 days. Reminder sent to radoslav.iliev@example.org"
print(re.findall(r"\d", text))
print(re.findall(r"\s", text)[:3])
print(re.sub(r"\D", "", "+359 (88) 123-45"))      # keep only the digits
```

::: info `\d` and `\w` know Cyrillic too
In Python, `\w` matches letters of **all** languages, and `\d` all kinds of digits.
For "Latin letters only", write `[A-Za-z]`.

```python run
import re

print(re.findall(r"\w+", "gr. Русе, Ruse"))
print(re.findall(r"[A-Za-z]+", "gr. Русе, Ruse"))
```
:::

### Anchors: `^`, `$`, `\b`

Anchors match a **position**, not a character:

- `^` - the start of the text;
- `$` - the end of the text;
- `\b` - a word boundary: between a word character and a non-word character.

```python run
import re

print(bool(re.search(r"^L", "L000001")), bool(re.search(r"^L", "XL000001")))
print(bool(re.search(r"\.$", "No findings.")))

text = "loan L000391; LL0001; L0003915"
print(re.findall(r"L\d{6}", text))           # also inside longer strings
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

```python run
import re

ids = ["L000001", "C0002", "L0009", "XL000001"]
# WHERE id LIKE 'L______'  (an L and exactly six characters)
print([x for x in ids if re.fullmatch(r"L.{6}", x)])
```

::: tip Try it
Write a pattern that finds the three-letter currency codes (`EUR`, `USD`, ...) in
`"100 EUR, 50 usd, 20 GBP and EURO"` - whole words in capitals only. Which anchor
do you need so that `EURO` is not found?
:::

## 3. Quantifiers

### How many times

A **quantifier** after a character or a class says how many times it repeats:

| Quantifier | Means |
|---|---|
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 (optional) |
| `{3}` | exactly 3 |
| `{2,4}` | 2 to 4 |
| `{2,}` | 2 or more |

```python run
import re

print(re.findall(r"\d+", "Overdue 35 days, 120 days, 5 days"))      # whole numbers
print(re.findall(r"\d{2}", "2026"))                                 # pairs of digits
print(re.findall(r"BG\d{2}", "BG80 bg12 BG7"))
print(re.findall(r"colou?r", "color colour colouur"))                # the u is optional
```

`*` also matches **nothing** - zero digits are "0 or more". With `findall`, that gives
empty strings between the matches:

```python run
import re

print(re.findall(r"\d*", "a12b3"))       # ['', '12', '', '3', ''] - the empty matches too
print(re.findall(r"\d+", "a12b3"))       # ['12', '3'] - what was meant
```

When you want "at least one", write `+`, not `*`.

On the client register: the names typed with two or more spaces in a row - `\s{2,}`:

```python run
import csv
import re

with open("data/client_register.csv", encoding="utf-8") as file:
    names = [row["name"] for row in csv.DictReader(file)]

double = [name for name in names if re.search(r"\s{2,}", name)]
print(len(double), "names with extra spaces, e.g.", double[:3])
```

An amount with an optional decimal part - `?` after a **group** in brackets (section 5)
makes the whole part optional:

```python run
import re

text = "paid 1250, then 99.5, then 0.75 and 10."
print(re.findall(r"\d+(?:\.\d+)?", text))
```

A Bulgarian amount with groups of thousands: 1 to 3 digits, then any number of
"a space and 3 digits", then a comma and 2 digits:

```python run
import re

BG_AMOUNT = r"\d{1,3}(?: \d{3})*,\d{2}"
text = "Payment of 2 069,77 EUR, then 45 544,40 EUR and 1 250 000,00 EUR; ref 12345,6"
print(re.findall(BG_AMOUNT, text))
print([bool(re.fullmatch(BG_AMOUNT, s)) for s in ["1 234,56", "1234,56", "12 34,56", "1 234,5"]])
```

### Greedy and lazy

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

::: tip Try it
In `"(valuation report from 12.06.2026) (checked 2026-06-15)"`, find the text inside
each pair of brackets. First try `\(.*\)`, then make it lazy.
:::

## 4. The functions of `re`

### `search`, `match`, `fullmatch`

| Function | Where the pattern must match | SAS / SQL |
|---|---|---|
| `re.search(p, s)` | anywhere | `PRXMATCH(p, s) > 0`, `LIKE '%...%'` |
| `re.match(p, s)` | at the **start** | `LIKE '...%'` |
| `re.fullmatch(p, s)` | the **whole** text | `LIKE '...'`, `REGEXP_LIKE(s, '^...$')` |

```python run
import re

LOAN = r"L\d{6}"

for s in ["L000001", "L000001 ", "xL000001", "L0000012"]:
    found = bool(re.search(LOAN, s))
    at_start = bool(re.match(LOAN, s))
    whole = bool(re.fullmatch(LOAN, s))
    print(f"{s!r:>12} search={found!s:<6} match={at_start!s:<6} fullmatch={whole}")
```

For **validation**, use `fullmatch`: `search` says yes when the pattern is
**somewhere** in the text, also with junk around it.

### `findall` and `finditer`: all matches

`findall` returns a **list of strings** - all the matches:

```python run
import re

comment = "Refinanced from loan L000391; L000048 and L000387 closed."
print(re.findall(r"L\d{6}", comment))
print(re.findall(r"L\d{6}", "no loans here"))       # an empty list
```

`finditer` gives the **match objects**, with their positions - when you need more
than the text:

```python run
import re

comment = "Refinanced from loan L000391; L000048 and L000387 closed."
for m in re.finditer(r"L\d{6}", comment):
    print(m.group(), "at", m.start())
```

How many times a pattern occurs - `REGEXP_COUNT` in SQL - is the length of
`findall`:

```python run
import re

text = "Refinanced from loan L000391; L000048 and L000387 closed."
print(len(re.findall(r"L\d{6}", text)))
```

### `split` with a pattern

`re.split` cuts at every match - when the separators vary:

```python run
import re

print(re.split(r"\s*[;,]\s*", "retail; sme,corporate ,  project"))
print(re.split(r"\s+", "  Iron   Retail  ET ".strip()))
```

### Flags: `re.IGNORECASE`

Flags change how a pattern works. The most useful one ignores the case:

```python run
import re

text = "100 EUR, 50 eur, 20 Eur"
print(re.findall(r"\d+ EUR", text))
print(re.findall(r"\d+ EUR", text, flags=re.IGNORECASE))     # also: re.I
```

With a text of many lines, `^` and `$` mean the start and the end of the **whole**
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

### `re.compile`: a pattern used many times

`re.compile` turns a pattern into an object with the same methods. Give it a name at
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

::: tip Try it
Count the comments that contain the word `review` in any case, with `search` and a
flag. Then count them with a string method (`"review" in c.lower()`). Same number?
:::

## 5. Groups and alternatives

### Groups: take the match apart

Round brackets make a **group**. After a match, `group(1)`, `group(2)`, ... give the
text of each group; `groups()` gives all of them as a tuple:

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

### Named groups: `(?P<name>...)`

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

### `findall` with groups gives tuples

With **one** group, `findall` returns the text of the group; with **several**
groups, a list of tuples:

```python run
import re

text = "Payment 1 250,00 EUR; payment 99,50 USD; fee 10,00 EUR"
print(re.findall(r"(\d[\d ]*,\d{2}) (EUR|USD)", text))
print(re.findall(r"(\d[\d ]*,\d{2}) (?:EUR|USD)", text))
```

`(?:...)` is a group that only **groups** - for `|` or a quantifier - and is not
returned.

A list of records from a text - `finditer` with named groups and `groupdict()`, one
dictionary per match (session 6):

```python run
import re

text = "Rate changed from 12.97% to 13.47% as of 22.03.2026. Rate changed from 4.17% to 2.67% as of 23.03.2026."
RATE = re.compile(r"from (?P<old>[\d.]+)% to (?P<new>[\d.]+)% as of (?P<date>[\d.]+\d)")
records = [m.groupdict() for m in RATE.finditer(text)]
print(records)
print([round(float(r["new"]) - float(r["old"]), 2) for r in records])
```

### Alternatives: `|`

`a|b` matches `a` or `b`. Inside a group, it is one of several options in one place:

```python run
import re

for comment in ["Payment of 2 069,77 EUR received", "Annual review done", "Overdue 35 days"]:
    m = re.match(r"(Payment|Overdue|Annual review)", comment)
    print(m.group(1) if m else None)
```

::: warning The order of the alternatives
At one position, the alternatives are tried **from left to right**, and the first
one that matches wins - not the longest:

```python run
import re

text = "Rate changed from 12.97% to 13.5%"
print(re.findall(r"\d+|\d+\.\d+", text))      # the short one first: the numbers are cut
print(re.findall(r"\d+\.\d+|\d+", text))      # the long one first
print(re.findall(r"\d+(?:\.\d+)?", text))      # or one pattern with an optional part
```
:::

::: tip Try it
Write one pattern with named groups for `"Overdue 60 days. Reminder sent to
radoslav.iliev@example.org on 2026-04-24."` that gives the days, the e-mail and the
date with `groupdict()`.
:::

## 6. Validation with `fullmatch`

### The patterns of our ids

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
    "currency":  r"[A-Z]{3}",
}

tests = {"loan_id": ["L000001", "L00001", "l000001"],
         "eik": ["175591301", "1965730713386", "12345678901"],
         "iban_bg": ["BG05TEST77018249464461", "BG05 TEST 7701", "DE89370400440532013000"],
         "date_bg": ["30.09.2026", "2026-09-30", "3.9.2026"]}

for name, values in tests.items():
    for value in values:
        print(f"{name:<9}{value:<26}{bool(re.fullmatch(PATTERNS[name], value))}")
```

The Bulgarian IBAN: `BG`, 2 check digits, 4 letters of the bank, 4 digits of the
branch, 2 digits of the account type, 8 letters or digits of the account - 22
characters.

::: warning `|` and `fullmatch`
`fullmatch(r"\d{9}|\d{13}", s)` works: `fullmatch` applies to the whole pattern. But
with `search` and anchors, `^\d{9}|\d{13}$` means "`^\d{9}` **or** `\d{13}$`" - write
`^(?:\d{9}|\d{13})$`.
:::

Validate a whole column - every loan id of `loans.csv`, every currency:

```python run
import csv
import re

LOAN_ID = re.compile(r"L\d{6}")
CURRENCY = re.compile(r"[A-Z]{3}")

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

bad_ids = [l["loan_id"] for l in loans if not LOAN_ID.fullmatch(l["loan_id"])]
bad_currencies = [l["currency"] for l in loans if not CURRENCY.fullmatch(l["currency"])]
print(len(loans), "loans;", len(bad_ids), "bad ids;", len(bad_currencies), "bad currencies")
```

### E-mails

The official grammar of e-mail addresses is very complex. For data checks, a
practical pattern is enough: something without spaces and `@`, an `@`, a domain with
at least one point:

```python run
import re

EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}")

for s in ["yana.koleva@example.org", "OFFICE.NORTHHOTELS@EXAMPLE.ORG",
          "office.balkanfoods at example.net", "a@b", "x@@example.com"]:
    print(f"{s:<36}{bool(EMAIL.fullmatch(s))}")
```

### The shape is not the meaning

A regex checks the **form**. `31.09.2026` has the right shape, but there is no 31st
of September; `BG00TEST...` has the right shape, but wrong check digits. So: the
regex first, then the real check - `strptime` for a date (session 7), the check
digits for an IBAN (Self-study):

```python run
import re
from datetime import datetime

def valid_date_bg(s):
    if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", s):
        return False
    day, month, year = (int(x) for x in s.split("."))
    return 1 <= month <= 12 and 1 <= day <= [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30,
                                             31, 31, 30, 31, 30, 31][month - 1]

print([valid_date_bg(s) for s in ["30.09.2026", "31.09.2026", "29.02.2028", "2026-09-30"]])
```

(Session 9 shows a shorter way: try `strptime` and catch the error.)

### A whole column

The IBANs of the register: clean them with the function of session 7, then check
the shape:

```python run
import csv
import re

IBAN_BG = re.compile(r"BG\d{2}[A-Z]{4}\d{6}[A-Z0-9]{8}")

with open("data/client_register.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

ibans = [row["iban"].replace(" ", "").upper() for row in rows]
ok = sum(1 for x in ibans if IBAN_BG.fullmatch(x))
empty = ibans.count("")
print(f"{ok} valid shape, {empty} empty, {len(ibans) - ok - empty} wrong")
```

::: info The same in pandas and SQL
pandas: `df["iban"].str.fullmatch(pattern)` gives a column of `True` / `False`;
`str.contains`, `str.extract` and `str.replace(..., regex=True)` use patterns too
(session 15). Most databases have regex functions: `REGEXP_LIKE` (Oracle, MySQL),
`~` (PostgreSQL); MS SQL Server only since version 2025.

```python run
import pandas as pd

reg = pd.read_csv("data/client_register.csv", dtype=str).fillna("")
iban = reg["iban"].str.replace(" ", "").str.upper()
print(iban.str.fullmatch(r"BG\d{2}[A-Z]{4}\d{6}[A-Z0-9]{8}").value_counts())
```
:::

::: tip Try it
Write a pattern for a client id that also accepts the messy forms of the register:
an optional space or `-` after the `C`, and 1 to 4 digits (`C17`, `c 0014`,
`C-0026`). Use `re.I`. How many of the 150 raw ids does it accept?
:::

## 7. Extraction from free text

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
that matches gives the type - like a `CASE WHEN ... LIKE` chain:

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

### Amounts and their currency

Amounts are written in different styles: `2 069,77 EUR`, `20,960.03 EUR`, `99,400
EUR`. One pattern for "digits with spaces, commas and points, then a currency", and
the `parse_amount` of session 7 for the number:

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

### Dates in two formats

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

### IBANs, with or without spaces

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

### Does the comment agree with the register?

A real check: the IBAN in a disbursement comment must be the IBAN of the client of
the loan. Three files, a dictionary for each lookup (session 6):

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

(`re.sub(r"\D", "", ...)` keeps only the digits - section 8.)

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

::: tip Try it
Extract the **new maturity** of every restructuring comment (`"... new maturity
2034-11-04."`) with a named group, and find the latest one.
:::

## 8. Replace with `sub`

### `re.sub(pattern, replacement, text)`

`re.sub` replaces **every** match - the SAS `PRXCHANGE('s/.../.../', -1, text)`, SQL
`REGEXP_REPLACE`:

```python run
import re

print(re.sub(r"\s+", " ", "  Iron   Retail \t ET ").strip())   # COMPBL
print(re.sub(r"\D", "", "BG 131-234 567"))                     # digits only
print(re.sub(r"[^A-Z0-9]", "", "bg80 test-9661".upper()))       # letters and digits
print(re.sub(r"\bE\.?A\.?D\.?$", "EAD", "Green Build E.A.D."))
```

`re.subn` also returns the number of replacements - useful in a cleaning report:

```python run
import re

text, n = re.subn(r"\s{2,}", " ", "a  b   c d")
print(text, "|", n, "replacements")
```

Before you share a file of comments, hide the e-mail addresses - the same `sub` on
every row:

```python run
import csv
import re

with open("data/loan_comments.csv", encoding="utf-8") as file:
    comments = [row["comment"] for row in csv.DictReader(file)]

masked = [re.sub(r"\S+@\S+\.[a-z]+", "<e-mail>", c) for c in comments]
for before, after in zip(comments, masked):
    if before != after:
        print(after)
        break
print(sum(1 for b, a in zip(comments, masked) if b != a), "comments changed")
```

### Back-references: reorder the parts

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

### A function as the replacement

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

::: warning A regex is code: test it
A pattern that looks right can match too much or too little. Test it on good **and**
bad examples, as the checks of the tasks do. [regex101.com](https://regex101.com)
(choose the flavour *Python*) shows what each part of a pattern matches.
:::

::: details Advanced: patterns that take forever
Patterns with nested quantifiers, like `(\d+)+$`, can take a very long time on a long
text that almost matches ("catastrophic backtracking"). Keep patterns simple, avoid
`(...+)+`, and do not run patterns written by other people on big data without a
test. Python 3.11 added *possessive* quantifiers (`*+`, `++`) and atomic groups
`(?>...)` that prevent it - rarely needed in data work.
:::

::: tip Try it
Mask the account part of every IBAN in a text for a report: keep `BG` and the first
6 characters, replace the rest with `*`. Hint: a group for the part you keep, and
`r"\1" + "*" * 14` as the replacement.
:::

## 9. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 08-regular-expressions/practice/task1-first-patterns.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-first-patterns.py` | Write patterns: ids, codes, currencies, whole words |
| 2 | `task2-predict-regex.py` | Predict `findall`, `search`, `sub`; greedy and lazy |
| 3 | `task3-validate.py` | Validators with `fullmatch`: loan id, EIK, IBAN, e-mail, date |
| 4 | `task4-extract.py` | Amounts, dates and loan ids from comments |
| 5 | `task5-groups.py` | Named groups: a payment line, a file name, a rate change |
| 6 | `task6-sub.py` (Optional) | Clean and reformat with `sub`: dates, spaces, masks |

## Summary

| Topic | Remember |
|-------|----------|
| Patterns | always `r"..."`; letters match themselves; `.` any character, `\.` a point |
| Classes | `[abc]`, `[0-9]`, `[^...]`; `\d`, `\w`, `\s` and `\D`, `\W`, `\S` |
| Anchors | `^` start, `$` end, `\b` word boundary |
| Quantifiers | `*` `+` `?` `{n}` `{n,m}`; greedy - add `?` for lazy, or use `[^x]*` |
| Functions | `search` (anywhere), `match` (start), `fullmatch` (all - for validation), `findall`, `finditer`, `split`, `sub`, `subn` |
| Groups | `( )` and `group(1)`; `(?P<name>...)`, `m["name"]`, `groupdict()`; `(?:...)` does not capture |
| Alternatives | `a\|b` - the first that matches wins; use `\b` or the longer one first |
| Flags | `re.I` ignores the case; `re.compile` for a pattern used many times |
| Validation | the shape with a regex, then the meaning (a real date, check digits) |
| SAS / SQL | `PRXMATCH` = `search`; `PRXPOSN` = `group`; `PRXCHANGE` = `sub`; `LIKE` `_` / `%` = `.` / `.*` |

## Homework

1. `08-regular-expressions/homework.py` (in the homework repository): **mine the
   comments** - classify every comment of `loan_comments.csv` by its type, extract
   the amounts of the payments, the new maturities of the restructurings and the
   IBANs of the disbursements, and check the IBANs against the register. Every check
   must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: find the e-mail addresses in the comments that are **not** in the
   register (after cleaning both).

## Self-study

This part is not covered in class. It is for reading at home: patterns that look
around without taking text, readable patterns with comments, and the check digits of
an IBAN and an EIK.

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
2. Rewrite the e-mail pattern of section 6 with `re.VERBOSE` and a comment per part.

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

- [Regular expression HOWTO](https://docs.python.org/3/howto/regex.html) (the official
  tutorial); reference: [`re`](https://docs.python.org/3/library/re.html)
- [regex101.com](https://regex101.com) - test a pattern and see what each part
  matches (choose *Python*)
- Real Python: [Regular expressions: regexes in Python](https://realpython.com/regex-python/)

**Next session:** errors and files - catch errors instead of stopping, read and write
CSV, JSON and Excel files, and load data with bad rows the way a SAS log would report
them.
