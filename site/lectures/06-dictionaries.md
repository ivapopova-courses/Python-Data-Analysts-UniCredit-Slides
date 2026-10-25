---
title: 6. Dictionaries
---

# 6. Dictionaries

<div class="lecture-meta">
  <span>Session 6</span><span>practice: <code>06-dictionaries/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- keep pairs of a **key** and a **value** in a dictionary, and find a value by its key
  in one step;
- add, change and remove entries, and loop over keys, values and pairs;
- use a dictionary as a **lookup table** - the Python version of a SAS format, a
  hash object and a small SQL reference table;
- build dictionaries in one line with a **dict comprehension**;
- count, sum and average **by group** - `GROUP BY` without pandas - with `get`,
  `defaultdict` and `Counter`;
- work with **records**: a row as a dictionary, a table as a dictionary of rows.

From SAS to Python - a format that turns a code into a name:

```sas
proc format;
    value $product
        'mortgage'    = 'Mortgage loan'
        'credit_card' = 'Credit card'
        'overdraft'   = 'Overdraft'
        other         = 'Other';
run;

data _null_;
    name = put('overdraft', $product.);
    put name=;
run;
```

```python run
product_names = {
    "mortgage": "Mortgage loan",
    "credit_card": "Credit card",
    "overdraft": "Overdraft",
}

print(product_names["overdraft"])
print(product_names.get("investment", "Other"))     # OTHER = 'Other'
```

And the question of homework 4, "what is the rating of the client of each loan?",
answered for all 400 loans with one dictionary - instead of 400 x 150 comparisons:

```python run
import csv

with open("data/clients.csv", encoding="utf-8") as file:
    rating_of = {row["client_id"]: int(row["rating"]) for row in csv.DictReader(file)}

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

for loan in loans[:5]:
    print(loan["loan_id"], loan["client_id"], rating_of[loan["client_id"]])
```

## 1. What is a dictionary?

### A key and a value

A **dictionary** (type `dict`) keeps **pairs**: a **key** and its **value**. You
find a value by its key - not by a position, as in a list:

```python run
pd_of_grade = {"AAA": 0.0003, "BBB": 0.0043, "B": 0.0275}

print(pd_of_grade["BBB"])
print(len(pd_of_grade))
print(pd_of_grade)
```

The syntax: curly brackets, pairs `key: value`, separated by commas. The same curly
brackets as a set (session 3) - but a set has only values, a dictionary has pairs.

Think of it as a two-column table with a **unique key**, like a SQL table with a
primary key:

| key (`grade`) | value (`pd`) |
|---|---|
| `"AAA"` | `0.0003` |
| `"BBB"` | `0.0043` |
| `"B"` | `0.0275` |

![A dictionary next to a SAS format and a SQL lookup table: the same key-value pairs in three forms](/diagrams/dict-lookup.svg){.diagram}

| | SAS | SQL | Python |
|---|---|---|---|
| A code -> a text | `PROC FORMAT` `VALUE` + `PUT()` | a lookup table + `JOIN` | `names[code]` |
| A key -> several values | a hash object, `h.find()` | a reference table + `JOIN` | a dict of tuples or dicts |
| Not found | `OTHER=` | `LEFT JOIN` + `COALESCE` | `.get(key, default)` |

### Create a dictionary

```python run
empty = {}                                         # an empty dict (not a set!)
currencies = {"EUR": "Euro", "USD": "US dollar"}
same = dict(EUR="Euro", USD="US dollar")           # keys that are valid names
from_pairs = dict([("EUR", "Euro"), ("USD", "US dollar")])

print(type(empty), currencies == same == from_pairs)
```

From two lists - the keys and the values - with `zip` (session 5):

```python run
grades = ["AAA", "AA", "A", "BBB"]
pds = [0.0003, 0.0008, 0.0018, 0.0043]

pd_of_grade = dict(zip(grades, pds))
print(pd_of_grade)
```

### Read a value: `[]` and `get`

`d[key]` gives the value. A key that is not there is a `KeyError` - the program
stops:

```python run
pd_of_grade = {"AAA": 0.0003, "BBB": 0.0043}

print(pd_of_grade["AAA"])
print(pd_of_grade["CCC"])          # KeyError: 'CCC'
```

`d.get(key)` gives `None` for a missing key, and `d.get(key, default)` gives the
default - like `OTHER=` in a format:

```python run
pd_of_grade = {"AAA": 0.0003, "BBB": 0.0043}

print(pd_of_grade.get("CCC"))
print(pd_of_grade.get("CCC", 1.0))
print(pd_of_grade.get("AAA", 1.0))
```

Which one to use? `d[key]` when a missing key is an **error** in the data and you
want to know at once. `get` when a missing key is **normal**, and you know what to
use instead.

### `in` checks the keys

```python run
pd_of_grade = {"AAA": 0.0003, "BBB": 0.0043}

print("AAA" in pd_of_grade)
print(0.0003 in pd_of_grade)                    # False: in looks at the keys
print(0.0003 in pd_of_grade.values())           # the values: .values()
```

### Rules for keys

- Keys are **unique**. The same key twice: the last value wins.
- Keys must be **hashable**: values that cannot change - `str`, `int`, `float`,
  `bool`, `tuple` (of such values). A list cannot be a key. (The same rule as for the
  items of a set.)
- Values can be anything: numbers, lists, other dictionaries, functions.
- A dictionary keeps the **order** in which the keys were added (since Python 3.7).

```python run
d = {"EUR": 1, "USD": 2, "EUR": 3}
print(d)                                        # one EUR, the last value

by_segment_stage = {("retail", 1): 120, ("retail", 2): 15}     # a tuple as the key
print(by_segment_stage[("retail", 2)])

bad = {["retail", 1]: 120}                      # TypeError: a list is unhashable
```

Two useful forms of `dict.fromkeys`: unique values **in the order of their first
appearance** (a set loses the order), and many keys with one start value:

```python run
currencies = ["EUR", "USD", "EUR", "EUR", "USD", "GBP"]

print(list(dict.fromkeys(currencies)))        # unique, order kept
print(dict.fromkeys(["retail", "sme", "corporate"], 0))
```

::: tip Try it
Predict, then run:

```python run
d = {1: "one", True: "yes", 1.0: "float"}
print(d)
print(len({"a": 1, "A": 2}))
```

(`1`, `True` and `1.0` are equal and have the same hash, so they are **one** key: the
first key stays, the last value wins.)
:::

## 2. Change a dictionary

A dictionary is **mutable**: you can add, change and remove pairs.

### Add and change: `d[key] = value`

The same statement does both: a new key is **added**, an existing key gets a **new
value**:

```python run
product_names = {"mortgage": "Mortgage loan"}

product_names["overdraft"] = "Overdraft"              # INSERT
product_names["mortgage"] = "Mortgage (housing)"      # UPDATE
print(product_names)
```

### Several at once: `update` and `|`

```python run
names = {"mortgage": "Mortgage loan", "overdraft": "Overdraft"}
more = {"overdraft": "Current account overdraft", "consumer": "Consumer loan"}

names.update(more)              # changes names; the values of more win
print(names)

base = {"EUR": "Euro"}
print(base | {"USD": "US dollar"})       # a NEW dict (Python 3.9+); base is not changed
print(base)
```

### Remove: `del`, `pop`

```python run
names = {"mortgage": "Mortgage loan", "overdraft": "Overdraft", "consumer": "Consumer loan"}

del names["overdraft"]                     # KeyError if the key is not there
removed = names.pop("consumer")            # removes and gives back the value
print(removed, names)

print(names.pop("leasing", None))          # a default: no KeyError
```

### `setdefault`: add only if missing

`d.setdefault(key, value)` returns the value of the key; if the key is missing, it
first adds it with `value`:

```python run
limits = {"retail": 50000}

print(limits.setdefault("retail", 99))     # exists: 50000, nothing changes
print(limits.setdefault("sme", 250000))    # missing: added
print(limits)
```

### A trap: changing a dictionary while looping over it

Adding or removing keys while a loop goes over the same dictionary is an error:

```python run
balances = {"L000001": 1044231.30, "L000002": 0.0, "L000003": 644.25}

for loan_id in balances:
    if balances[loan_id] == 0:
        del balances[loan_id]       # RuntimeError: dictionary changed size during iteration
```

Loop over a **copy of the keys**, or build a new dictionary (section 5):

```python run
balances = {"L000001": 1044231.30, "L000002": 0.0, "L000003": 644.25}

for loan_id in list(balances):              # a list of the keys - a copy
    if balances[loan_id] == 0:
        del balances[loan_id]
print(balances)
```

Changing only the **values** of existing keys in a loop is fine.

### Compare two dictionaries

`==` compares the pairs - the order does not matter. A quick check that a
nomenclature did not change between two versions:

```python run
version_1 = {"mortgage": "Mortgage loan", "overdraft": "Overdraft"}
version_2 = {"overdraft": "Overdraft", "mortgage": "Mortgage loan"}
version_3 = {"overdraft": "Overdraft", "mortgage": "Housing loan"}

print(version_1 == version_2)
print(version_1 == version_3)
print({k for k in version_1 if version_1[k] != version_3.get(k)})     # what changed
```

::: tip Try it
Start from `rates = {"EUR": 3.5, "USD": 5.25}`. Add `"GBP": 4.75`, change `EUR` to
`3.25`, remove `USD` with `pop`, and print the dict. What does
`rates.pop("CHF", 0)` return?
:::

## 3. Loop over a dictionary

### `keys()`, `values()`, `items()`

A `for` over a dictionary goes over its **keys**. For the values or the pairs, use
the methods:

```python run
outstanding = {"retail": 6.9, "sme": 39.5, "corporate": 85.0}     # EUR million

for segment in outstanding:                     # the keys
    print(segment)

print(list(outstanding.values()))
print(sum(outstanding.values()))

for segment, amount in outstanding.items():     # pairs - unpack them
    print(f"{segment:<10}{amount:>8.1f}")
```

`items()` is the most common: it gives the key and the value together.

### Sort the result

The order of a dictionary is the order of insertion. To show it sorted, sort the
`items()` - by the key, or by the value:

```python run
outstanding = {"sme": 39.5, "corporate": 85.0, "retail": 6.9}

for segment, amount in sorted(outstanding.items()):                       # by key
    print(segment, amount)
print()
for segment, amount in sorted(outstanding.items(), key=lambda kv: kv[1], reverse=True):
    print(segment, amount)                                                # by value DESC
```

The key with the largest value:

```python run
outstanding = {"sme": 39.5, "corporate": 85.0, "retail": 6.9}

print(max(outstanding, key=outstanding.get))
```

(`key=outstanding.get` - the method itself, without brackets: `max` calls it for
each key.)

A ranked report: `enumerate` over the sorted items (session 5):

```python run
outstanding = {"sme": 39.5, "corporate": 85.0, "retail": 6.9}
total = sum(outstanding.values())

ranked = sorted(outstanding.items(), key=lambda kv: kv[1], reverse=True)
for rank, (segment, amount) in enumerate(ranked, start=1):
    print(f"{rank}. {segment:<10}{amount:>7.1f}{amount / total:>8.1%}")
```

### The views are live

`keys()`, `values()` and `items()` are **views**: they show the dictionary as it is
**now**, also after a change:

```python run
outstanding = {"retail": 6.9}
keys = outstanding.keys()
print(keys)

outstanding["sme"] = 39.5
print(keys)                        # the view shows the new key too
```

::: details Advanced: keys behave like a set
`keys()` supports the set operations of session 3 - handy to compare two
nomenclatures:

```python run
old = {"mortgage": 1, "consumer": 2, "leasing": 3}
new = {"mortgage": 1, "consumer": 2, "overdraft": 4}

print(old.keys() & new.keys())     # in both
print(old.keys() - new.keys())     # removed
print(new.keys() - old.keys())     # added
```
:::

::: tip Try it
Print the segments of the example sorted by the **length** of their name. Then print
only the segments with more than EUR 10 million.
:::

## 4. Lookup tables and nomenclatures

This is the main use of dictionaries in data work: a **code -> description** or
**key -> attributes** table, used for every row of a dataset.

### A format with `OTHER=`

```python run
product_names = {
    "mortgage": "Mortgage loan",
    "consumer": "Consumer loan",
    "credit_card": "Credit card",
    "overdraft": "Overdraft",
}

codes = ["overdraft", "mortgage", "leasing", "consumer"]
print([product_names.get(code, "Other") for code in codes])
```

::: info Animation
**Grouping by hand:** [1. A lookup](../animations/groupingByHand.html#1){target="_blank"}
:::

### A nomenclature from a file: the rating scale

`rating_scale.csv` is a nomenclature: one row per rating. Read it into a dictionary
**rating -> (grade, PD)** once, and use it for every client:

```python run
import csv

scale = {}
with open("data/rating_scale.csv", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        pd_mid = (float(row["pd_min"]) + float(row["pd_max"])) / 2
        scale[int(row["rating"])] = (row["grade"], round(pd_mid, 6))

print(scale[4])
grade, pd_value = scale[7]
print(grade, pd_value)
```

`csv.DictReader` (the module `csv` comes with Python) reads a CSV file row by row,
and gives each row as a dictionary: the column name is the key. No more `row[7]` -
`row["outstanding"]`. Files and `csv` in depth: session 9.

```python run
import csv

with open("data/loans.csv", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    first = next(reader)          # the first row

print(first)
print(first["outstanding"], type(first["outstanding"]))     # still text
```

### Codes in the data: a lookup in a function

When the same lookup is used in many places, put it in a function with the
default in one place:

```python run
STAGE_NAMES = {1: "performing", 2: "under-performing", 3: "non-performing"}

def stage_name(stage):
    """The name of an IFRS 9 stage; "unknown stage" for anything else."""
    return STAGE_NAMES.get(stage, "unknown stage")

print([stage_name(s) for s in [1, 3, 2, 4]])
```

Keep the nomenclature (the dictionary) as a **constant** at the top of the script,
in capitals: one place to change it. Session 12 turns such a nomenclature into a
class with its own checks.

### The join: loans with the region of their client

A `LEFT JOIN loans -> clients ON client_id` is: a dictionary of the clients, and a
lookup for every loan.

```sql
SELECT l.loan_id, l.client_id, c.region, c.segment
FROM loans l LEFT JOIN clients c ON l.client_id = c.client_id;
```

```python run
import csv

with open("data/clients.csv", encoding="utf-8") as file:
    client = {row["client_id"]: row for row in csv.DictReader(file)}   # client_id -> the whole row

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

for loan in loans[:5]:
    c = client.get(loan["client_id"], {})                  # LEFT JOIN: {} if not found
    print(loan["loan_id"], loan["client_id"], c.get("region"), c.get("segment"))
```

::: info Animation
**Grouping by hand:** [5. The join by key](../animations/groupingByHand.html#5){target="_blank"}
:::

A SAS programmer would do this with a hash object (`declare hash h(dataset:
"clients"); h.defineKey("client_id"); ...; rc = h.find();`). The dictionary is the
same idea, with less code.

Why it is fast: a dictionary finds a key in **one step**, however big it is -
homework 4 needed up to 150 comparisons per loan. Section "How a dictionary works"
in the Self-study explains why.

### The expected loss of homework 4, again

The same result as homework 4 - 1,140,106.56 - with two lookups per loan:

```python run
import csv

with open("data/rating_scale.csv", encoding="utf-8") as file:
    pd_of = {int(r["rating"]): (float(r["pd_min"]) + float(r["pd_max"])) / 2 for r in csv.DictReader(file)}

with open("data/clients.csv", encoding="utf-8") as file:
    rating_of = {r["client_id"]: int(r["rating"]) for r in csv.DictReader(file)}

LGD = 0.45
total = 0.0
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        pd_value = pd_of[rating_of[loan["client_id"]]]          # loan -> client -> rating -> PD
        total += pd_value * LGD * float(loan["outstanding"])

print(f"{total:,.2f}")
```

### Inverting a dictionary - a trap

Value -> key: swap the pairs. But values are not unique; when two keys have the
same value, one of them is lost:

```python run
group_of = {"mortgage": "retail", "consumer": "retail", "investment": "business"}

inverted = {group: product for product, group in group_of.items()}
print(inverted)              # {'retail': 'consumer', ...} - mortgage is gone
```

For "group -> all products" you need a dictionary of **lists** (section 6).

### Ranges are not keys

A dictionary needs the **exact** key. PD bands, days-past-due buckets, amount
ranges - a value **between** two limits - are not a dictionary lookup. Use a
function with `if` (sessions 2 and 4), or a list of limits:

```python run
BUCKETS = [(0, "current"), (30, "1-30"), (90, "31-90")]        # upper limit -> name

def dpd_bucket(days):
    for limit, name in BUCKETS:
        if days <= limit:
            return name
    return "90+"

print([dpd_bucket(d) for d in [0, 15, 45, 200]])
```

::: details Advanced: `bisect` for many ranges
For a long, sorted list of limits, the module `bisect` finds the position of a value
by halving the list, not by checking every limit:

```python run
import bisect

pd_limits = [0.0005, 0.001, 0.0025, 0.006, 0.015, 0.04, 0.1, 0.25, 0.9999]   # the pd_max of grades 1 - 9
grades = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]

def grade_of_pd(pd_value):
    return grades[bisect.bisect_left(pd_limits, pd_value)]

print([grade_of_pd(p) for p in [0.0003, 0.0043, 0.02, 0.5, 1.0]])
```

In pandas, `pd.cut` does the same for a whole column (session 15).
:::

::: info The same in pandas
`Series.map(dictionary)` applies a dictionary to a whole column - a SAS format on a
column. Missing keys become `NaN`:

```python run
import pandas as pd

names = {"mortgage": "Mortgage loan", "overdraft": "Overdraft"}
loans = pd.read_csv("data/loans.csv")
print(loans["product"].map(names).fillna("Other").head())
```
:::

::: tip Try it
In "The join" example, add the `rating` of the client to each printed line. Then
change one `client_id` in the loop to `"C9999"` (a client that does not exist): what
does `client.get(...)` give, and what would `client[...]` do?
:::

## 5. Dict comprehensions

Like a list comprehension (session 5), with `key: value` and curly brackets:

```python run
grades = ["AAA", "AA", "A", "BBB"]
pds = [0.0003, 0.0008, 0.0018, 0.0043]

pd_of_grade = {g: p for g, p in zip(grades, pds)}
in_bp = {g: round(p * 10000, 1) for g, p in pd_of_grade.items()}       # basis points
low_risk = {g: p for g, p in pd_of_grade.items() if p < 0.001}         # a filter

print(in_bp)
print(low_risk)
```

`SELECT key, expression FROM ... WHERE ...` into a lookup table. Common forms:

```python run
import csv

with open("data/clients.csv", encoding="utf-8") as file:
    clients = list(csv.DictReader(file))

region_of = {c["client_id"]: c["region"] for c in clients}                 # id -> one column
corporate = {c["client_id"]: c for c in clients if c["segment"] == "corporate"}
print(region_of["C0002"], len(corporate))

# invert a dict whose values ARE unique
grade_of_rating = {1: "AAA", 2: "AA", 3: "A"}
rating_of_grade = {g: r for r, g in grade_of_rating.items()}
print(rating_of_grade)
```

::: tip Try it
From `rating_scale.csv`, build `{grade: description}` with one comprehension over
`csv.DictReader`. Then keep only the grades whose description contains `"risk"`.
:::

## 6. Grouping by hand: `GROUP BY`

### Count by group: from `if` to `Counter`

`SELECT region, COUNT(*) FROM clients GROUP BY region` - four ways, from the longest to
the shortest. All do the same: a dictionary **group -> count** that grows row by
row.

**1. `if key in d`:**

```python run
import csv

with open("data/clients.csv", encoding="utf-8") as file:
    regions = [row["region"] for row in csv.DictReader(file)]

counts = {}
for region in regions:
    if region in counts:
        counts[region] += 1
    else:
        counts[region] = 1
print(counts)
```

**2. `get` with a default** - "the count so far, or 0":

```python run
import csv

with open("data/clients.csv", encoding="utf-8") as file:
    regions = [row["region"] for row in csv.DictReader(file)]

counts = {}
for region in regions:
    counts[region] = counts.get(region, 0) + 1
print(counts)
```

**3. `defaultdict(int)`** - a dictionary that creates a missing key by itself, with
`int()`, that is `0`:

```python run
import csv
from collections import defaultdict

with open("data/clients.csv", encoding="utf-8") as file:
    regions = [row["region"] for row in csv.DictReader(file)]

counts = defaultdict(int)
for region in regions:
    counts[region] += 1
print(dict(counts))
```

**4. `Counter`** - made for counting:

```python run
import csv
from collections import Counter

with open("data/clients.csv", encoding="utf-8") as file:
    counts = Counter(row["region"] for row in csv.DictReader(file))

print(counts)
print(counts.most_common(3))        # PROC FREQ ORDER=FREQ, the top 3
print(counts["Sofia"], counts["Vidin"])      # a missing key counts 0 - no KeyError
```

::: info Animation
**Grouping by hand:** [2. Count with `get`](../animations/groupingByHand.html#2){target="_blank"}
:::

### Sum by group

`SELECT segment, SUM(outstanding) ... GROUP BY segment` - the segment is in
`clients.csv`, the amount in `loans.csv`: a lookup (section 4) and a sum:

```python run
import csv
from collections import defaultdict

with open("data/clients.csv", encoding="utf-8") as file:
    segment_of = {r["client_id"]: r["segment"] for r in csv.DictReader(file)}

totals = defaultdict(float)                         # float() is 0.0
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        totals[segment_of[loan["client_id"]]] += float(loan["outstanding"])

for segment, total in sorted(totals.items()):
    print(f"{segment:<10}{total:>18,.2f}")
```

::: info Animation
**Grouping by hand:** [3. Sum with `defaultdict`](../animations/groupingByHand.html#3){target="_blank"}
:::

### Several aggregates per group

`COUNT`, `SUM`, `AVG`, `MAX` by product - keep a small list per group,
`[count, sum, max]`, and compute the average at the end:

```python run
import csv

stats = {}
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        amount = float(loan["outstanding"])
        s = stats.setdefault(loan["product"], [0, 0.0, 0.0])     # count, sum, max
        s[0] += 1
        s[1] += amount
        s[2] = max(s[2], amount)

print(f"{'product':<16}{'n':>4}{'sum':>16}{'avg':>14}{'max':>14}")
for product, (n, total, largest) in sorted(stats.items()):
    print(f"{product:<16}{n:>4}{total:>16,.0f}{total / n:>14,.0f}{largest:>14,.0f}")
```

This is `PROC MEANS` with `CLASS product`, by hand. pandas does it in one line
(session 15) - but now you know what it does.

The **share** of each group in the total - one more pass over the small result, not
over the data:

```python run
import csv
from collections import defaultdict

totals = defaultdict(float)
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        totals[loan["currency"]] += float(loan["outstanding"])

grand_total = sum(totals.values())
shares = {cur: round(t / grand_total, 4) for cur, t in totals.items()}
print(shares)
```

### Group into lists

Sometimes you need the **rows** of each group, not only a number - a dictionary of
lists:

```python run
import csv
from collections import defaultdict

loans_of = defaultdict(list)                   # list() is []
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        loans_of[loan["client_id"]].append(loan["loan_id"])

print(loans_of["C0030"])
print(max(loans_of, key=lambda c: len(loans_of[c])), "has the most loans")
```

::: info Animation
**Grouping by hand:** [4. Group into lists](../animations/groupingByHand.html#4){target="_blank"}
:::

### Two keys: `GROUP BY segment, stage`

A **tuple** of the two values is the key:

```python run
import csv
from collections import defaultdict

with open("data/clients.csv", encoding="utf-8") as file:
    segment_of = {r["client_id"]: r["segment"] for r in csv.DictReader(file)}

totals = defaultdict(float)
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        key = (segment_of[loan["client_id"]], int(loan["stage"]))
        totals[key] += float(loan["outstanding"])

for (segment, stage), total in sorted(totals.items()):
    print(f"{segment:<10} stage {stage}{total:>18,.2f}")
```

### `HAVING` and `ORDER BY` on the result

The result is a dictionary - filter it with a comprehension (`HAVING`), sort its
items (`ORDER BY`):

```python run
import csv
from collections import Counter

with open("data/loans.csv", encoding="utf-8") as file:
    loans_per_client = Counter(row["client_id"] for row in csv.DictReader(file))

# HAVING COUNT(*) >= 6, ORDER BY COUNT(*) DESC, client_id
many = {c: n for c, n in loans_per_client.items() if n >= 6}
for client_id, n in sorted(many.items(), key=lambda kv: (-kv[1], kv[0])):
    print(client_id, n)
```

### `Counter` arithmetic: two months side by side

Counters can be added and subtracted. The change of the number of loans per stage
between two months:

```python run
from collections import Counter

august = Counter({1: 330, 2: 52, 3: 18})
september = Counter({1: 323, 2: 58, 3: 19})

print(september - august)              # only the positive changes
september.subtract(august)             # all changes, also negative
print(dict(september))
print((august + Counter({3: 1})).total())       # total(): Python 3.10+
```

### A trap: the group key from dirty text

`"Sofia"`, `"sofia"` and `"Sofia "` are three different keys. Clean the key before
you group (text cleaning: session 7):

```python run
from collections import Counter

cities = ["Sofia", "sofia", "Sofia ", "Varna", "VARNA"]
print(Counter(cities))
print(Counter(c.strip().title() for c in cities))
```

::: info The same in pandas
`value_counts` and `groupby` do all of this section (sessions 14 - 15):

```python run
import pandas as pd

clients = pd.read_csv("data/clients.csv")
print(clients["region"].value_counts().head(3))
loans = pd.read_csv("data/loans.csv")
print(loans.groupby("product")["outstanding"].agg(["count", "sum", "mean", "max"]).round(0))
```
:::

::: tip Try it
Count the loans per **currency** with `Counter`, then sum the outstanding per
**currency and stage** with a tuple key. Predict first: how many groups will the
second result have at most?
:::

## 7. Nested dictionaries and records

### A row as a dictionary

`csv.DictReader` gives each row as a dictionary: a **record** with named fields. A
list of them is a table where the columns have names:

```python run
import csv

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

print(len(loans), loans[0]["loan_id"], loans[0]["product"])
usd = [loan["loan_id"] for loan in loans if loan["currency"] == "USD"]
print(usd[:5])
```

Compare with session 5: `row[3] == "USD"` vs `loan["currency"] == "USD"`. The name
says what the column is, and adding a column to the file does not break the code.

The values are still **text**. Convert them once, into a new record:

```python run
import csv

def typed(loan):
    """A loan record with numbers instead of text."""
    return loan | {
        "amount": float(loan["amount"]),
        "outstanding": float(loan["outstanding"]),
        "interest_rate": float(loan["interest_rate"]),
        "days_past_due": int(loan["days_past_due"]),
        "stage": int(loan["stage"]),
    }

with open("data/loans.csv", encoding="utf-8") as file:
    loans = [typed(row) for row in csv.DictReader(file)]

print(loans[1])
print(sum(l["outstanding"] for l in loans if l["stage"] == 3))
```

Sort a list of records by one or more fields - `ORDER BY` with column names:

```python run
import csv

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

by_product = sorted(loans, key=lambda l: (l["product"], -float(l["outstanding"])))
for loan in by_product[:4]:
    print(loan["product"], loan["loan_id"], loan["outstanding"])
```

### A dictionary of dictionaries: a table keyed by id

```python run
import csv

with open("data/clients.csv", encoding="utf-8") as file:
    clients = {row["client_id"]: row for row in csv.DictReader(file)}

print(clients["C0002"])
print(clients["C0002"]["region"])            # two steps: the client, then the field
```

Like a SAS dataset with an index on `client_id`, or a hash object with several data
fields.

### Safe nested access

With nested dictionaries, a missing level is a `KeyError` (or a `TypeError` on
`None`). Chain `get` with an empty dictionary as the default:

```python run
clients = {"C0002": {"segment": "sme", "region": "Ruse"}}

print(clients.get("C0002", {}).get("region"))
print(clients.get("C9999", {}).get("region", "unknown"))
print(clients["C9999"]["region"])               # KeyError: 'C9999'
```

### The shape of JSON

Nested dictionaries and lists are the shape of **JSON**, the text format of web
APIs and of many configuration files. The module `json` turns one into the other
(JSON files: session 9):

```python run
import json

report = {
    "report_date": "2026-09-30",
    "segments": {"retail": {"loans": 242, "outstanding": 6.8e6}, "sme": {"loans": 104, "outstanding": 3.14e7}},
    "checks": ["no negative balances", "all stages known"],
}
text = json.dumps(report, indent=2)
print(text)
print(json.loads(text)["segments"]["sme"]["loans"])
```

### Copies of nested dictionaries

The same rule as for nested lists (session 5): `d.copy()` and `dict(d)` are
**shallow** - the inner dictionaries are shared. `copy.deepcopy` copies all levels:

```python run
import copy

limits = {"retail": {"max": 50000}, "sme": {"max": 250000}}
shallow = limits.copy()
deep = copy.deepcopy(limits)

limits["retail"]["max"] = 0
print(shallow["retail"], deep["retail"])
```

::: tip Try it
From `clients.csv`, build `{client_id: {"segment": ..., "rating": int(...)}}` with one
dict comprehension (only two fields per client). Then print the rating of `C0132`
and the number of corporate clients with a rating of 6 or worse.
:::

## 8. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: `git pull upstream main`) and run the tasks from the
terminal, in the repository root:

```bash
python 06-dictionaries/practice/task1-dict-basics.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-dict-basics.py` | A product nomenclature: create, read with a default, add, change, remove |
| 2 | `task2-predict-dicts.py` | Predict: duplicate keys, `True` / `1` keys, `get` vs `[]`, live views |
| 3 | `task3-lookups.py` | Rating -> grade / PD; codes -> names; loans with the region of their client |
| 4 | `task4-count-and-sum.py` | Clients per region, outstanding per segment, `most_common` |
| 5 | `task5-group-aggregates.py` | Count / sum / average / max per product, `HAVING`, a sorted report |
| 6 | `task6-nested-groups.py` (Optional) | Clients as a dict of dicts; segment x stage totals with tuple keys |

## Summary

| Topic | Remember |
|-------|----------|
| Dictionary | `{key: value}`; keys unique and hashable; keeps the insertion order |
| Read | `d[key]` (KeyError if missing); `d.get(key, default)`; `key in d` checks the keys |
| Change | `d[key] = v` adds or changes; `update`, `\|`; `del`, `pop(key, default)`; `setdefault` |
| Loop | `for k in d`; `d.values()`; `for k, v in d.items()`; sort with `sorted(d.items(), key=...)` |
| Lookups | a dict = a SAS format / hash object / lookup table; `get(code, "Other")` = `OTHER=` |
| Join | a dict of the right table, `get` for every row of the left one = `LEFT JOIN` |
| Ranges | not keys: a function with `if`, or `bisect` |
| Comprehension | `{k: v for ... if ...}` |
| `GROUP BY` | `d[k] = d.get(k, 0) + 1`; `defaultdict(int / float / list)`; `Counter(...)`; `most_common(n)` |
| Several keys | a tuple as the key: `(segment, stage)` |
| Records | `csv.DictReader`: rows as dicts; a dict of dicts keyed by id; `json.dumps` / `loads` |
| Copies | `copy()` is shallow; `copy.deepcopy` for nested dicts |

## Homework

1. `06-dictionaries/homework.py` (in the homework repository): **homework 4 again,
   with dictionaries** - lookups instead of loops; the expected loss of the portfolio
   (it must be the same 1,140,106.56), the expected loss by segment and by grade, and
   a sorted text report. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: a **migration of client counts by region**: count the clients per region
   in `clients.csv`, then per region **and segment**, and print a small table with
   the regions as rows and the segments as columns (the Self-study below shows how).

## Self-study

This part is not covered in class. It is for reading at home: a cross table by hand,
and why a dictionary is fast.

### A pivot by hand: `PROC TABULATE` without pandas

A **dictionary of dictionaries** is a cross table: the outer key is the row, the inner
key is the column. Build it, then print it with the rows and columns sorted:

```python run
import csv
from collections import defaultdict

with open("data/clients.csv", encoding="utf-8") as file:
    clients = list(csv.DictReader(file))

table = defaultdict(lambda: defaultdict(int))      # region -> segment -> count
for c in clients:
    table[c["region"]][c["segment"]] += 1

columns = sorted({c["segment"] for c in clients})
print(f"{'region':<14}" + "".join(f"{col:>11}" for col in columns) + f"{'total':>8}")
for region in sorted(table):
    row = table[region]
    cells = "".join(f"{row[col]:>11}" for col in columns)
    print(f"{region:<14}{cells}{sum(row.values()):>8}")
```

`defaultdict(lambda: defaultdict(int))`: a missing row is created as a new
`defaultdict(int)` - so `table[region][segment] += 1` works for any new pair.

And back - from the cross table to rows (`region, segment, count`), the job of
`PROC TRANSPOSE` or `melt` in pandas (session 16):

```python run
table = {"Ruse": {"retail": 18, "sme": 7}, "Varna": {"retail": 13, "corporate": 3}}
rows = [(region, segment, n) for region, cols in table.items() for segment, n in cols.items()]
print(rows)
```

**Exercises**

1. Build the cross table **product x stage** from `loans.csv`, with the total
   outstanding (in EUR thousands, rounded) in each cell.
2. Add a total row at the bottom.

::: details Answer
```python
import csv
from collections import defaultdict

table = defaultdict(lambda: defaultdict(float))
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        table[loan["product"]][int(loan["stage"])] += float(loan["outstanding"]) / 1000

print(f"{'product':<16}" + "".join(f"{s:>12}" for s in (1, 2, 3)))
for product in sorted(table):
    print(f"{product:<16}" + "".join(f"{table[product][s]:>12,.0f}" for s in (1, 2, 3)))
print(f"{'total':<16}" + "".join(f"{sum(table[p][s] for p in table):>12,.0f}" for s in (1, 2, 3)))
```
:::

### How a dictionary works: hashing

Why is `d[key]` fast, and why must keys not change?

A dictionary keeps its pairs in a table of slots. To store a key, Python computes
`hash(key)` - a big integer made from the value - and uses it to choose the slot. To
find the key later, it computes the hash again and looks **in that slot only**. So a
lookup costs the same for 10 keys or 10 million keys:

```python run
print(hash("C0002"), hash("C0002") == hash("C0002"))
print(hash(42), hash(("retail", 1)))
print(hash([1, 2]))             # TypeError: a list is unhashable
```

A list is not hashable because it can **change**: after a change, its hash would
change, and the dictionary would look in the wrong slot. That is why keys must be
immutable values.

The hash of a string changes **between runs** of Python (a security feature), but
not during one run. Never save hashes to a file.

The speed, measured:

```python run
import time

ids = [f"C{i:06d}" for i in range(200_000)]
as_list = ids
as_dict = {c: True for c in ids}

start = time.perf_counter()
"C199999" in as_list
t_list = time.perf_counter() - start

start = time.perf_counter()
"C199999" in as_dict
t_dict = time.perf_counter() - start

print(f"list: {t_list:.6f} s, dict: {t_dict:.6f} s")
```

**Exercise**

1. Why is `{(1, [2, 3]): "x"}` an error, but `{(1, (2, 3)): "x"}` is fine?

::: details Answer
A tuple is hashable only if everything inside it is hashable. `(1, [2, 3])` contains a
list, which can change, so the tuple has no hash. `(1, (2, 3))` contains only
immutable values.
:::

## Read more

- Python tutorial: [Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries),
  [Looping techniques](https://docs.python.org/3/tutorial/datastructures.html#looping-techniques)
- Reference: [Mapping types - dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict),
  [`collections`](https://docs.python.org/3/library/collections.html) (`defaultdict`,
  `Counter`), [`csv.DictReader`](https://docs.python.org/3/library/csv.html#csv.DictReader)
- Real Python: [Dictionaries in Python](https://realpython.com/python-dicts/),
  [Python's Counter](https://realpython.com/python-counter/)

**Next session:** text processing - clean ids, names and codes, read numbers written
the Bulgarian way, and dates from text, with the methods of `str` and `datetime`.
