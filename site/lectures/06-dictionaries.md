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
  without searching through a list;
- add, change and remove entries, and loop over keys, values and pairs;
- use a dictionary as a **lookup table** - the Python version of a SAS format, a
  hash object and a small SQL reference table;
- build dictionaries in one line with a **dict comprehension**;
- work with **records**: a row as a dictionary, a table as a dictionary of rows.

Follow the main sections for the core lesson. Collapsed **Advanced** blocks keep
extra techniques for later reading; they are not needed for the practice tasks.

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
brackets as a set ([session 3](./03-lists-tuples-sets.md#_11-sets)) - but a set has only values, a dictionary has pairs.

Think of it as a two-column table with a **unique key**, like a SQL table with a
primary key:

| key (`grade`) | value (`pd`) |
|---|---|
| `"AAA"` | `0.0003` |
| `"BBB"` | `0.0043` |
| `"B"` | `0.0275` |


### Create a dictionary

```python run
empty = {}
currencies = {"EUR": "Euro", "USD": "US dollar"}
print(empty, currencies)
```

::: details Advanced: other constructors

```python run
empty = {}                                         # an empty dict (not a set!)
currencies = {"EUR": "Euro", "USD": "US dollar"}
same = dict(EUR="Euro", USD="US dollar")           # keys that are valid names
from_pairs = dict([("EUR", "Euro"), ("USD", "US dollar")])

print(type(empty), currencies == same == from_pairs)
```
:::

From two lists - the keys and the values - with `zip` ([session 5](./05-lists-advanced.md#zip-several-lists-side-by-side)):

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
default - like `OTHER=` in a SAS format:

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
print(0.0003 in pd_of_grade.values())           # True, looks at the values: .values()
```

### Rules for keys and values

- Keys are **unique**. The same key twice: the last value wins.
- Keys must be **hashable**: values that cannot change - `str`, `int`, `float`,
  `bool`, `tuple` (of such values). A list cannot be a key. (The same rule as for the
  items of a set.)
- Values can be anything: numbers, lists, other dictionaries, functions.
- A dictionary keeps the **order** in which the keys were added (since Python 3.7).
- Finding a key is **fast**, also in a big dictionary: Python does not search
  through all the keys (the Self-study explains how).
- Keys are **case-sensitive**: `"a"` and `"A"` are two different keys.
- Keys and values can be of **mixed data types** within the same dictionary.

```python run
d = {"EUR": 1, "USD": 2, "EUR": 3}
print(d)                                        # one EUR, the last value

by_segment_stage = {("retail", 1): 120, ("retail", 2): 15}     # a tuple as the key
print(by_segment_stage[("retail", 2)])

bad = {["retail", 1]: 120}                      # TypeError: a list is unhashable
```

::: details Advanced: `fromkeys`: unique values and initial values

Two useful forms of `dict.fromkeys`: unique values **in the order of their first
appearance** (a set loses the order), and many keys with one start value:

```python run
currencies = ["EUR", "USD", "EUR", "EUR", "USD", "GBP"]

print(list(dict.fromkeys(currencies)))        # unique, order kept
print(dict.fromkeys(["retail", "sme", "corporate"], 0))
```
:::


::: details Advanced: `1`, `True` and `1.0` are one key
```python run
d = {1: "one", True: "yes", 1.0: "float"}
print(d)
```

`1`, `True` and `1.0` are equal and have the same hash, so they are **one** key: the
first key stays, the last value wins.
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
print(base | {"USD": "US dollar"})       # a NEW dict; base is not changed
print(base)
```

`|` is the safe way to add a column to a record (section 6) without changing the
original row - a new dictionary with one more pair:

```python run
row = {"loan_id": "L000001", "stage": "1"}
new_row = row | {"stage_name": "performing"}
print(new_row)
print(row)                               # unchanged
```

### Remove: `del`, `pop`

```python run
names = {"mortgage": "Mortgage loan", "overdraft": "Overdraft", "consumer": "Consumer loan"}

del names["overdraft"]                     # KeyError if the key is not there
removed = names.pop("consumer")            # removes and gives back the value
print(removed, names)

print(names.pop("leasing", None))          # a default: no KeyError
```

::: details Advanced: `setdefault`: add only if missing

### `setdefault`: add only if missing

`d.setdefault(key, value)` returns the value of the key; if the key is missing, it
first adds it with `value`:

```python run
limits = {"retail": 50000}

print(limits.setdefault("retail", 99))     # exists: 50000, nothing changes
print(limits.setdefault("sme", 250000))    # missing: added
print(limits)
```
:::

### A trap: changing a dictionary while looping over it

Adding or removing keys while a loop goes over the same dictionary is an error:

```python run
balances = {"L000001": 1044231.30, "L000002": 0.0, "L000003": 644.25}

for loan_id in balances:
    if balances[loan_id] == 0:
        del balances[loan_id]       # RuntimeError: dictionary changed size during iteration
```

Loop over a **copy of the keys**, or build a new dictionary (section 4):

```python run
balances = {"L000001": 1044231.30, "L000002": 0.0, "L000003": 644.25}

for loan_id in list(balances):              # a list of the keys - a copy
    if balances[loan_id] == 0:
        del balances[loan_id]
print(balances)
```

Changing only the **values** of existing keys in a loop is fine.

::: details Advanced: compare two dictionaries

### Compare two dictionaries

`==` compares the pairs - the order does not matter. A quick check that a
nomenclature did not change between two versions:

```python run
version_1 = {"mortgage": "Mortgage loan", "overdraft": "Overdraft"}
version_2 = {"overdraft": "Overdraft", "mortgage": "Mortgage loan"}
version_3 = {"overdraft": "Overdraft", "mortgage": "Housing loan"}

print(version_1 == version_2)
print(version_1 == version_3)
```
:::

::: tip Try it
Start from `rates = {"EUR": 3.5, "USD": 5.25}`. Add `"GBP": 4.75`, change `EUR` to
`3.25`, remove `USD` with `pop`, and print the dict. What does
`rates.pop("CHF", 0)` return? Then predict: what does `rates | {"CHF": 0.5}` give,
and is `rates` changed after it?
:::

## 3. Iterating over a dictionary

### `keys()`, `values()`, and `items()`

When you loop through a dictionary with a `for` loop, it iterates over the **keys** by default. To loop over values or pairs instead, use explicit dictionary methods:

- **`keys()`**: Returns all keys (this is identical to looping directly over the dictionary).
- **`values()`**: Returns all values.
- **`items()`**: Returns key-value pairs as `(key, value)` tuples, which you can unpack directly in the loop.

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

### Sort the keys

`sorted(d)` returns a list of the keys in sorted order. It does not change `d`:

```python run
names = {"overdraft": "Overdraft", "mortgage": "Mortgage loan"}
print(sorted(names))
for code in sorted(names):
    print(code, names[code])
```


### Sorting and ranking by values

The order of a dictionary is the order of insertion. To show it sorted, sort the
`items()` - by the key, or by the value:

```python run
outstanding = {"sme": 39.5, "corporate": 85.0, "retail": 6.9}

for segment, amount in sorted(outstanding.items()):                       # by key
    print(segment, amount)
print("~"*20)
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

A ranked report: `enumerate` over the sorted items ([session 5](./05-lists-advanced.md#enumerate-the-number-of-each-item)):

```python run
outstanding = {"sme": 39.5, "corporate": 85.0, "retail": 6.9}
total = sum(outstanding.values())

ranked = sorted(outstanding.items(), key=lambda kv: kv[1], reverse=True)
for rank, (segment, amount) in enumerate(ranked, start=1):
    print(f"{rank}. {segment:<10}{amount:>7.1f}{amount / total:>8.1%}")
```


::: details Advanced: the views are live
`keys()`, `values()` and `items()` are **views**: they show the dictionary as it is
**now**, also after a change:

```python run
outstanding = {"retail": 6.9}
keys = outstanding.keys()
print(keys)

outstanding["sme"] = 39.5
print(keys)                        # the view shows the new key too
```
:::

::: details Advanced: keys behave like a set
`keys()` supports the set operations of [session 3](./03-lists-tuples-sets.md#_12-set-operations-sql-union-intersect-except) - handy to compare two
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
From `outstanding = {"retail": 6.9, "sme": 39.5, "corporate": 85.0}`, print
each segment and amount with `items()`. Then print the segment names alphabetically.
:::

## 4. Dict comprehensions

### `{key: value for ...}`

Like a list comprehension ([session 5](./05-lists-advanced.md#_2-list-comprehensions)), with `key: value` and curly brackets:

```python run
grades = ["AAA", "AA", "A", "BBB"]
pds = [0.0003, 0.0008, 0.0018, 0.0043]

pd_of_grade = {g: p for g, p in zip(grades, pds)}
in_bp = {g: round(p * 10000, 1) for g, p in pd_of_grade.items()}       # basis points
low_risk = {g: p for g, p in pd_of_grade.items() if p < 0.001}         # a filter

print(in_bp)
print(low_risk)
```

In SQL terms: `SELECT key, expression FROM ... WHERE ...` into a lookup table. Common forms, on a
small list of clients:

```python run
clients = [("C0001", "retail", "Sofia"), ("C0002", "sme", "Ruse"), ("C0003", "corporate", "Varna")]

region_of = {client_id: region for client_id, segment, region in clients}          # id -> one column
corporate = {client_id: region for client_id, segment, region in clients if segment == "corporate"}
print(region_of["C0002"], corporate)

```

::: details Advanced: invert a dictionary

```python run
# invert a dict whose values ARE unique
grade_of_rating = {1: "AAA", 2: "AA", 3: "A"}
rating_of_grade = {g: r for r, g in grade_of_rating.items()}
print(rating_of_grade)
```

### Inverting a dictionary - a trap

Value -> key: swap the pairs. But values are not unique; when two keys have the
same value, one of them is lost:

```python run
group_of = {"mortgage": "retail", "consumer": "retail", "investment": "business"}

inverted = {group: product for product, group in group_of.items()}
print(inverted)              # {'retail': 'consumer', ...} - mortgage is gone
```

For "group -> all products" you need a dictionary of **lists**: `{"retail": ["mortgage", "consumer"], ...}`.
:::

::: tip Try it
From `grades` and `pds` of the first example, build `{grade: pd}` only for the grades
with a PD below 0.002, with the PD in basis points. Predict how many grades you get.
:::

## 5. Lookup tables and nomenclatures

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
in capitals: one place to change it. [Lecture 11](./11-oop-nomenclatures.md) turns such a nomenclature into a
class with its own checks.

### A chain of lookups: loan -> client -> rating -> PD

A loan has no PD of its own. The loan has a client, the client has a rating, and
the rating has a PD. So, to find the PD of a loan, look up two times, one after
the other:

1. the client of the loan -> its rating (in `rating_of`);
2. the rating -> its PD (in `pd_of`).

In SQL, these are two joins: the loan to its client by `client_id`, then the
client to the rating scale by `rating`. With the PD, the example computes the
expected loss of the loan: EL = PD x LGD x outstanding. On small made-up tables:

```python run
rating_of = {"C0001": 3, "C0002": 7}              # client_id -> rating
pd_of = {3: 0.0018, 7: 0.1}                       # rating -> PD

loan = {"loan_id": "L000001", "client_id": "C0002", "outstanding": 250000.0}

rating = rating_of[loan["client_id"]]             # loan -> client -> rating
pd_value = pd_of[rating]                          # rating -> PD
print(rating, pd_value)

LGD = 0.45
print(f"EL = {pd_value * LGD * loan['outstanding']:,.2f}")
print(pd_of[rating_of[loan["client_id"]]])        # the same chain in one line
```

`[]` needs every key to exist: a client that is not in `rating_of` raises
`KeyError` (`get` with a default avoids that).

Each loan needs only two lookups, and a lookup is fast, however big the dictionary
is (the Self-study explains why). Without a dictionary, you would loop over all the
clients to find the client of each loan. A SAS programmer would do this with a hash object
(`h.find()`); the dictionary is the same idea, with less code.

::: tip Try it
Change the loan to the client `C0001`. Predict the rating, the PD and the EL before
you run it. What happens with a client that is not in `rating_of`, and how would
`get` change that?
:::

:::: details Advanced: ranges and `bisect`

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

In pandas, `pd.cut` does the same for a whole column ([lecture 14](./14-pandas-select-aggregate-join.md#bands-pd-cut)).
:::
::::

::: details Advanced: the same in pandas
`Series.map(dictionary)` applies a dictionary to a whole column - a SAS format on a
column. Missing keys become `NaN`:

```python run
import pandas as pd

names = {"mortgage": "Mortgage loan", "overdraft": "Overdraft"}
loans = pd.read_csv("data/loans.csv")
print(loans["product"].map(names).fillna("Other").head())
```
:::

## 6. Nested dictionaries and records

### A row as a dictionary

A row of a table can be a dictionary: a **record** with named fields. A list of
them is a table where the columns have names:

```python run
loans = [
    {"loan_id": "L000001", "client_id": "C0002", "product": "mortgage", "currency": "EUR", "outstanding": 120000.0},
    {"loan_id": "L000002", "client_id": "C0001", "product": "consumer", "currency": "USD", "outstanding": 8500.0},
    {"loan_id": "L000003", "client_id": "C0002", "product": "overdraft", "currency": "USD", "outstanding": 1200.0},
]

print(len(loans), loans[0]["loan_id"], loans[0]["product"])
usd = [loan["loan_id"] for loan in loans if loan["currency"] == "USD"]
print(usd)
```

Compare with [session 5](./05-lists-advanced.md#on-the-portfolio): `row[3] == "USD"` vs `loan["currency"] == "USD"`. The name
says what the column is, and adding a column does not break the code. In
[lecture 8](./08-errors-and-files.md#_7-csv-files) you will read rows like these from a CSV file.

::: details Advanced: convert and sort whole records

A CSV file (lecture 8) gives all values as **text**. Convert them once, into a new
record:

```python run
def typed(loan):
    """A loan record with numbers instead of text."""
    return loan | {
        "amount": float(loan["amount"]),
        "outstanding": float(loan["outstanding"]),
        "interest_rate": float(loan["interest_rate"]),
        "days_past_due": int(loan["days_past_due"]),
        "stage": int(loan["stage"]),
    }

rows = [
    {"loan_id": "L000001", "amount": "150000", "outstanding": "120000.00", "interest_rate": "4.2", "days_past_due": "0", "stage": "1"},
    {"loan_id": "L000002", "amount": "10000", "outstanding": "8500.50", "interest_rate": "9.9", "days_past_due": "95", "stage": "3"},
]                                                    # all values are text
loans = [typed(row) for row in rows]

print(loans[1])
print(sum(l["outstanding"] for l in loans if l["stage"] == 3))
```

Sort a list of records by one or more fields - SQL `ORDER BY` with column names:

```python run
loans = [
    {"loan_id": "L000001", "product": "mortgage", "outstanding": 120000.0},
    {"loan_id": "L000002", "product": "consumer", "outstanding": 8500.0},
    {"loan_id": "L000003", "product": "mortgage", "outstanding": 250000.0},
    {"loan_id": "L000004", "product": "consumer", "outstanding": 15000.0},
]

by_product = sorted(loans, key=lambda l: (l["product"], -l["outstanding"]))
for loan in by_product:
    print(loan["product"], loan["loan_id"], loan["outstanding"])
```

:::

### A dictionary of dictionaries: a table keyed by id

The outer key is the client id; the value is the whole row:

```python run
rows = [
    {"client_id": "C0001", "segment": "retail", "region": "Ruse", "rating": 3},
    {"client_id": "C0002", "segment": "sme", "region": "Ruse", "rating": 7},
    {"client_id": "C0003", "segment": "corporate", "region": "Varna", "rating": 6},
    {"client_id": "C0004", "segment": "corporate", "region": "Sofia", "rating": 2},
]
clients = {row["client_id"]: row for row in rows}     # client_id -> the whole row

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

::: details Advanced: the shape of JSON

### The shape of JSON

Nested dictionaries and lists are the shape of **JSON**, the text format of web
APIs and of many configuration files. The module `json` turns one into the other
(JSON files: [lecture 8](./08-errors-and-files.md#_8-json-files)):

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

:::

::: details Advanced: copies of nested dictionaries

### Copies of nested dictionaries

The same rule as for the copies of lists ([session 3](./03-lists-tuples-sets.md#make-a-copy)): `d.copy()` and `dict(d)` are
**shallow** - the inner dictionaries are shared. `copy.deepcopy` copies all levels:

```python run
import copy

limits = {"retail": {"max": 50000}, "sme": {"max": 250000}}
shallow = limits.copy()
deep = copy.deepcopy(limits)

limits["retail"]["max"] = 0
print(shallow["retail"], deep["retail"])
```
:::

::: tip Try it
From `rows` of "A dictionary of dictionaries", build
`{client_id: {"segment": ..., "rating": ...}}` with one dict comprehension (only two
fields per client). Then print the rating of `C0003` and the number of corporate
clients with a rating of 6 or worse.
:::

## 7. Summary
| Topic | Remember |
|-------|----------|
| Dictionary | `{key: value}`; keys unique and hashable; keeps insertion order |
| Read | `d[key]` for a required key; `d.get(key, default)` for an expected missing key; `key in d` |
| Change | `d[key] = value` adds or changes; `pop(key, default)` removes and returns a value |
| Loop | `for key in d`; `d.values()`; `for key, value in d.items()`; `sorted(d)` sorts the keys |
| Comprehension | `{key: value for ... if ...}`; `dict(zip(keys, values))` pairs two lists |
| Lookups | A dictionary is like a SAS format or a SQL lookup table with unique keys |
| Records | a row as a dict, a table as a list of dicts; `clients[id]["region"]` reads a nested field |

## Practice
Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 06-dictionaries/practice/task1-dict-basics.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-dict-basics.py` | A product nomenclature: create, read with a default, add, change, remove |
| 2 | `task2-predict-dicts.py` | Predict: duplicate keys, lookups, membership and changes |

Start with Task 1, then Task 2. Each part has its own checks. While you work on one
part, `TODO` for the other parts means they are still unfinished.
`task2-predict-dicts-advanced.py` is an optional extension after reading the
relevant Advanced blocks.

## Homework

1. Finish the practice tasks 1 and 2. Every check must print `OK`.
2. Optional: `task2-predict-dicts-advanced.py`.

## Self-study

This part is not covered in class. It is for reading at home: a cross table by hand,
and why a dictionary is fast.

### A pivot by hand: `PROC TABULATE` without pandas

A **dictionary of dictionaries** is a cross table: the outer key is the row, the inner
key is the column. Build it, then print it with the rows and columns sorted:

```python run
from collections import defaultdict

clients = [
    {"region": "Ruse", "segment": "retail"}, {"region": "Ruse", "segment": "sme"},
    {"region": "Varna", "segment": "retail"}, {"region": "Ruse", "segment": "retail"},
    {"region": "Sofia", "segment": "corporate"}, {"region": "Varna", "segment": "sme"},
]

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

A `defaultdict` (from the module `collections`) is a dictionary that creates a
missing key by itself: `defaultdict(int)` gives a new key the value `int()`, that is
`0`. `defaultdict(lambda: defaultdict(int))`: a missing row is created as a new
`defaultdict(int)` - so `table[region][segment] += 1` works for any new pair.

And back - from the cross table to rows (`region, segment, count`), the job of
SAS `PROC TRANSPOSE`, or of `melt` in pandas ([lecture 15](./15-pandas-reports.md#_2-from-wide-to-long-melt)):

```python run
table = {"Ruse": {"retail": 18, "sme": 7}, "Varna": {"retail": 13, "corporate": 3}}
rows = [(region, segment, n) for region, cols in table.items() for segment, n in cols.items()]
print(rows)
```

**Exercises**

1. Build the cross table **product x stage** from the list `loans` below, with the
   total outstanding (in EUR thousands, rounded) in each cell.
2. Add a total row at the bottom.

```python
loans = [("mortgage", 1, 120000.0), ("consumer", 1, 8500.0), ("mortgage", 2, 250000.0),
         ("overdraft", 3, 1200.0), ("consumer", 2, 15000.0), ("mortgage", 1, 95000.0)]
```

::: details Answer
```python
from collections import defaultdict

loans = [("mortgage", 1, 120000.0), ("consumer", 1, 8500.0), ("mortgage", 2, 250000.0),
         ("overdraft", 3, 1200.0), ("consumer", 2, 15000.0), ("mortgage", 1, 95000.0)]

table = defaultdict(lambda: defaultdict(float))
for product, stage, outstanding in loans:
    table[product][stage] += outstanding / 1000

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
find the key later, it computes the hash again. Different keys can lead to the
same slot (a collision), so Python may need to check more than one slot and compare
keys. Lookups take approximately constant time **on average**; they are not a
guaranteed single step or an identical runtime for every dictionary size:

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
  [`collections.defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
- Real Python: [Dictionaries in Python](https://realpython.com/python-dicts/)

**Next session:** text processing and regular expressions - clean ids, names and
codes, read numbers and dates from text with the methods of `str` and `datetime`,
and describe the shape of a text with a pattern.
