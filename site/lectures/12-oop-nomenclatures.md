---
title: "12. OOP in practice: nomenclatures"
---

# 12. OOP in practice: nomenclatures

<div class="lecture-meta">
  <span>Session 12</span><span>practice: <code>12-oop-nomenclatures/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- turn a nomenclature - products, regions, a rating scale, DPD buckets - into **one
  class** that holds its codes, its metadata, its rules and its methods;
- check a nomenclature when it is created, and check a dataset against it;
- apply a nomenclature to a dataset, and report the values it does not know;
- create objects in more than one way with `classmethod`, and write helpers with
  `staticmethod`;
- build special kinds of nomenclatures - with **ranges** and with a **hierarchy** -
  by **inheritance**;
- keep all nomenclatures in a **registry** and apply them in the same way to
  different datasets - by **composition**.

This session is built on one sentence - the reason the team asked for OOP:

> *Classes and objects allow to represent nomenclatures as structured entities that
> combine **data**, **metadata**, **validation rules**, and **processing methods**,
> making them easier to manage and apply **consistently across datasets**.*

From SAS to Python - a nomenclature from a table, and its use:

```sas
data fmt;                                  /* the code list as a dataset */
    set products (rename=(code=start name=label));
    retain fmtname '$product';
run;
proc format cntlin=fmt; run;               /* a format from a dataset */

data loans2;
    set loans;
    product_name = put(product, $product.);
run;
```

```python run
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict                    # code -> label

    def lookup(self, code, default=None):
        return self.codes.get(code, default)


products = Nomenclature("product", {"mortgage": "Mortgage loan", "overdraft": "Overdraft"})
print(products.lookup("overdraft"), products.lookup("leasing", "?"))
```

By the end of today this small class knows its version and owner, refuses bad codes,
applies itself to any list of rows, reports what it cannot map - and has a family of
special kinds.

## 1. The use case

### What a nomenclature is

A **nomenclature** (a code list, a classifier, a reference table) gives each code of a
dataset its meaning and its place:

| Nomenclature | Codes | Maps to |
|---|---|---|
| products | `mortgage`, `overdraft`, ... | a name; a group (retail / business) |
| regions | `SOF`, `PDV`, ... | the English and the Bulgarian name |
| the rating scale | 1 ... 10 | a grade and a PD band |
| DPD buckets | days past due | `current`, `1-30`, `31-90`, `90+` |
| IFRS 9 stages | 1, 2, 3 | performing, under-performing, non-performing |

### The problems without a class

In most teams, the same mapping lives in **many** programs: a `PROC FORMAT` here, a
`CASE WHEN` there, a lookup table in a third place. Then:

- the copies drift apart - one report has the new product, another does not;
- nobody knows which **version** a report used, or who owns the list;
- a code that is not in the list goes through silently - as a missing value, or as
  "Other";
- every new dataset needs the mapping written again.

Two reports with their own copy of the product groups - one copy has the new product,
the other does not. The same loans, two different totals:

```python run
import csv

GROUPS_REPORT_A = {"mortgage": "retail", "consumer": "retail", "credit_card": "retail", "overdraft": "retail",
                   "investment": "business", "working_capital": "business", "project_finance": "business"}
GROUPS_REPORT_B = {"mortgage": "retail", "consumer": "retail", "credit_card": "retail", "overdraft": "retail",
                   "investment": "business", "working_capital": "business"}      # an old copy

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

for name, groups in [("A", GROUPS_REPORT_A), ("B", GROUPS_REPORT_B)]:
    business = sum(float(l["outstanding"]) for l in loans if groups.get(l["product"]) == "business")
    print(f"report {name}: business exposure {business:,.2f}")
```

And a copy with a typo - `"credit card"` instead of `"credit_card"` - loses a whole
product, without an error:

```python run
import csv
from collections import Counter

NAMES = {"mortgage": "Mortgage loan", "consumer": "Consumer loan", "credit card": "Credit card",
         "overdraft": "Overdraft", "investment": "Investment loan", "working_capital": "Working capital",
         "project_finance": "Project finance"}

with open("data/loans.csv", encoding="utf-8") as file:
    names = Counter(NAMES.get(row["product"], "Other") for row in csv.DictReader(file))
print(names)          # 68 credit cards are now "Other"
```

### The plan

The four parts of the sentence become the four parts of the class:

| The client's words | In the class | Section |
|---|---|---|
| data | the codes and their labels | 2 |
| metadata | name, version, valid from, owner | 2 |
| validation rules | checks when it is created; `validate()` for a dataset | 3 |
| processing methods | `lookup()`, `apply()` to rows, the unmapped report | 4 |
| consistently across datasets | one object, used for every dataset; a registry | 7 |

![The four parts of the sentence of the client as the four parts of the Nomenclature class, and the classes built on it](/diagrams/nomenclature.svg){.diagram}

::: tip Try it
Name two nomenclatures from your own work that are copied into several programs. What
would their metadata be (who owns them, how often do they change)?
:::

## 2. Data and metadata

### The data and the metadata in one object

A dataclass (session 11) with the codes and the facts about them:

```python run
from dataclasses import dataclass
from datetime import date

@dataclass
class Nomenclature:
    """A code list with its metadata."""
    name: str
    codes: dict                         # code -> label
    version: str = "1"
    valid_from: date | None = None
    owner: str = ""

    def lookup(self, code, default=None):
        """The label of a code; `default` if the code is unknown."""
        return self.codes.get(code, default)


stages = Nomenclature("stage", {1: "performing", 2: "under-performing", 3: "non-performing"},
                      version="2026.1", valid_from=date(2026, 1, 1), owner="Risk Methodology")
print(stages)
print(stages.lookup(3), stages.lookup(4, "unknown"))
```

`date | None` means "a date, or `None`" (session 4; Python 3.10+). The metadata does
not change how the codes work - but it is printed with every report that uses them,
so anybody can see **which** list was used:

```python run
from dataclasses import dataclass
from datetime import date

@dataclass
class Nomenclature:
    name: str
    codes: dict
    version: str = "1"
    valid_from: date | None = None
    owner: str = ""


stages = Nomenclature("stage", {1: "performing", 2: "under-performing", 3: "non-performing"},
                      "2026.1", date(2026, 1, 1), "Risk Methodology")
print(f"Nomenclature: {stages.name} v{stages.version}, valid from {stages.valid_from:%d.%m.%Y}, owner {stages.owner}")
print(f"{'code':<6}label")
for code, label in stages.codes.items():
    print(f"{code:<6}{label}")
```

Two nomenclatures are **equal** when all their fields are equal - the dataclass
`__eq__` of session 11. The same codes with another version are **not** the same
nomenclature:

```python run
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict
    version: str = "1"


a = Nomenclature("stage", {1: "performing", 2: "under-performing"}, "2026.1")
b = Nomenclature("stage", {1: "performing", 2: "under-performing"}, "2026.1")
c = Nomenclature("stage", {1: "performing", 2: "under-performing"}, "2026.2")
print(a == b, a == c, a.codes == c.codes)
```

A trap of dataclasses: an empty dictionary as a default is refused - it would be one
dictionary for all objects (session 11):

```python run
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict = {}
# ValueError: mutable default <class 'dict'> for field codes is not allowed: use default_factory
```

### Behave like a container: `len`, `in`, `for`

Three special methods (session 11, Self-study) make the object work with `len()`,
`in` and `for` - like the dictionary inside it:

```python run
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def __len__(self):                 # len(nom)
        return len(self.codes)

    def __contains__(self, code):      # code in nom
        return code in self.codes

    def __iter__(self):                # for code in nom
        return iter(self.codes)


products = Nomenclature("product", {"mortgage": "Mortgage loan", "consumer": "Consumer loan",
                                    "overdraft": "Overdraft"})
print(len(products), "overdraft" in products, "leasing" in products)
print([code for code in products])
print(sorted(products))
```

### A readable `__repr__`

The automatic `repr` of a dataclass prints **all** the codes - too long for a list of
200 products. A short one, with the metadata:

```python run
from dataclasses import dataclass
from datetime import date

@dataclass
class Nomenclature:
    name: str
    codes: dict
    version: str = "1"
    valid_from: date | None = None

    def __repr__(self):
        since = f", valid from {self.valid_from}" if self.valid_from else ""
        return f"<Nomenclature {self.name!r} v{self.version}: {len(self.codes)} codes{since}>"


print(Nomenclature("product", {"mortgage": "Mortgage loan", "overdraft": "Overdraft"}, "3", date(2026, 7, 1)))
```

(A dataclass does not write `__repr__` if the class has its own.)

### Protect the codes

The dictionary of codes is **shared** with whoever passed it in - a change outside
changes the nomenclature (references, session 3). Take a **copy** in `__post_init__`:

```python run
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def __post_init__(self):
        self.codes = dict(self.codes)          # our own copy


mapping = {"mortgage": "Mortgage loan"}
products = Nomenclature("product", mapping)
mapping["leasing"] = "Leasing"                 # a change outside ...
print("leasing" in products.codes)             # ... does not reach the nomenclature
```

A copy can still be changed through `nom.codes[...] = ...`. If nobody should change
the codes after the nomenclature is created, keep them behind a **read-only view** -
`types.MappingProxyType` looks like a dictionary, but refuses changes:

```python run
from types import MappingProxyType

codes = MappingProxyType(dict({"mortgage": "Mortgage loan"}))
print(codes["mortgage"], len(codes), "mortgage" in codes)
codes["leasing"] = "Leasing"            # TypeError: the view is read-only
```

::: tip Try it
Create a `Nomenclature` for the currencies `EUR`, `USD`, `GBP` (labels: the names) with
the owner `"Treasury"` and the version `"2026.2"`. Print it, and the label of `USD`.
:::

## 3. Validation rules

### Rules when the nomenclature is created

A nomenclature with a duplicate code, an empty label or a malformed code must not
exist at all. `__post_init__` checks it, and raises a clear error (session 9):

```python run
import re
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict
    code_pattern: str = r".+"                  # a regex every code must fit (session 8)

    def __post_init__(self):
        if not self.codes:
            raise ValueError(f"{self.name}: the nomenclature has no codes")
        for code, label in self.codes.items():
            if not re.fullmatch(self.code_pattern, str(code)):
                raise ValueError(f"{self.name}: code {code!r} does not fit {self.code_pattern!r}")
            if label is None or str(label).strip() == "":
                raise ValueError(f"{self.name}: code {code!r} has no label")
        self.codes = dict(self.codes)


regions = Nomenclature("region", {"SOF": "Sofia", "PDV": "Plovdiv"}, code_pattern=r"[A-Z]{3}")
print(len(regions.codes), "region codes")

for codes in [{"SOF": "Sofia", "Var": "Varna"}, {"SOF": ""}, {}]:
    try:
        Nomenclature("region", codes, code_pattern=r"[A-Z]{3}")
    except ValueError as error:
        print("rejected:", error)
```

The pattern of the product codes: lower-case words with `_` - "Credit Card" is refused
at once, not discovered in a report a month later:

```python run
import re
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict
    code_pattern: str = r".+"

    def __post_init__(self):
        bad = [c for c in self.codes if not re.fullmatch(self.code_pattern, str(c))]
        if bad:
            raise ValueError(f"{self.name}: codes that do not fit {self.code_pattern!r}: {bad}")


try:
    Nomenclature("product", {"mortgage": "Mortgage loan", "Credit Card": "Credit card"}, code_pattern=r"[a-z_]+")
except ValueError as error:
    print(error)
```

### Duplicate codes

A dictionary cannot **have** duplicate keys - the last one wins silently (session 6).
So the duplicates must be caught **before** the dictionary is built - when the codes
come as pairs, for example from a file:

```python run
from collections import Counter

pairs = [("mortgage", "Mortgage loan"), ("overdraft", "Overdraft"), ("mortgage", "Housing loan")]

print(dict(pairs))                                     # mortgage: the last label, silently
duplicates = [code for code, n in Counter(code for code, _ in pairs).items() if n > 1]
print("duplicates:", duplicates)
```

Section 5 builds this check into the way a nomenclature is read from a file.

### Rules for a dataset: `validate`

The second kind of rule checks a **dataset** against the nomenclature: which values
are not codes, and how often?

```python run
import csv
from collections import Counter
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def __contains__(self, code):
        return code in self.codes

    def validate(self, values):
        """The values that are not codes, with their counts (empty: all known)."""
        return Counter(v for v in values if v not in self)


products = Nomenclature("product", {"mortgage": "Mortgage loan", "consumer": "Consumer loan",
                                    "credit_card": "Credit card", "overdraft": "Overdraft",
                                    "investment": "Investment loan", "working_capital": "Working capital"})

with open("data/loans.csv", encoding="utf-8") as file:
    values = [row["product"] for row in csv.DictReader(file)]
print(products.validate(values))                       # project_finance is missing in the list!
```

The check found a gap in the **nomenclature**, not in the data: `project_finance` is a
real product that the list does not know. Without the check, 21 loans - the largest of
the portfolio - would get no product name in the report.

The register of session 7 against a nomenclature of the region names - first the raw
city column, then after the cleaning function of session 7:

```python run
import csv
from collections import Counter
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def validate(self, values):
        return Counter(v for v in values if v not in self.codes)


regions = Nomenclature("region", {r: r for r in ["Sofia", "Plovdiv", "Varna", "Burgas", "Ruse", "Stara Zagora", "Pleven"]})
CYRILLIC = {"София": "Sofia", "Пловдив": "Plovdiv", "Варна": "Varna", "Бургас": "Burgas", "Русе": "Ruse",
            "Стара Загора": "Stara Zagora", "Плевен": "Pleven"}

def clean_city(raw):
    s = " ".join(raw.split()).removeprefix("gr. ")
    return CYRILLIC.get(s, s).title()

with open("data/client_register.csv", encoding="utf-8") as file:
    cities = [row["city"] for row in csv.DictReader(file)]

print("raw:     ", sum(regions.validate(cities).values()), "unknown values")
print("cleaned: ", sum(regions.validate(clean_city(c) for c in cities).values()), "unknown values")
```

::: warning `1` is not `"1"`
A CSV file gives **text**. A nomenclature with **number** codes knows none of the
values - every row is "unknown". Use the same type on both sides:

```python run
import csv
from collections import Counter

stage_codes = {1: "performing", 2: "under-performing", 3: "non-performing"}     # int codes
with open("data/loans.csv", encoding="utf-8") as file:
    values = [row["stage"] for row in csv.DictReader(file)]                       # str values

print(Counter(v for v in values if v not in stage_codes))                         # all 400!
print(Counter(v for v in values if int(v) not in stage_codes))                    # convert first
```
:::

### A check report

A method that returns a small report - the numbers a data owner wants to see:

```python run
import csv
from collections import Counter
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def validate(self, values):
        return Counter(v for v in values if v not in self.codes)

    def check(self, rows, column):
        values = [row[column] for row in rows]
        unknown = self.validate(values)
        empty = sum(1 for v in values if v in ("", None))
        return {"nomenclature": self.name, "column": column, "rows": len(values),
                "unknown": sum(n for v, n in unknown.items() if v not in ("", None)), "empty": empty,
                "unknown values": sorted(v for v in unknown if v not in ("", None))}


stages = Nomenclature("stage", {"1": "performing", "2": "under-performing", "3": "non-performing"})
with open("data/loans_export.csv", encoding="utf-8-sig") as file:
    rows = list(csv.DictReader(file, delimiter=";"))
print(stages.check(rows, "Stage"))
```

::: tip Try it
Add `"project_finance": "Project finance"` to the product codes of the `validate`
example and run it again. Then validate the `Product` column of `loans_export.csv`
(`;`, `utf-8-sig`): what does it find?
:::

## 4. Processing methods: apply to a dataset

### `apply`: a new column for every row

The main method: take rows (a list of dictionaries, session 6), and return **new** rows
with one more column - the label of the code. Like `put(product, $product.)` in a DATA
step, or a `LEFT JOIN` to a lookup table:

```python run
import csv
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def lookup(self, code, default=None):
        return self.codes.get(code, default)

    def apply(self, rows, column, new_column, default=None):
        """New rows: each row with new_column = the label of row[column]."""
        return [row | {new_column: self.lookup(row[column], default)} for row in rows]


stages = Nomenclature("stage", {"1": "performing", "2": "under-performing", "3": "non-performing"})
with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

result = stages.apply(loans, "stage", "stage_name")
print(result[1]["loan_id"], result[1]["stage"], result[1]["stage_name"])
print("stage_name" in loans[1])                 # the input rows are not changed
```

`row | {...}` (session 6) makes a **new** dictionary - the input stays as it was.

The new column is ready for the usual reports - the number of loans per product
**name**, and two nomenclatures one after the other (name, then group):

```python run
import csv
from collections import Counter
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def apply(self, rows, column, new_column, default=None):
        return [row | {new_column: self.codes.get(row[column], default)} for row in rows]


names = Nomenclature("product name", {"mortgage": "Mortgage loan", "consumer": "Consumer loan",
                                      "credit_card": "Credit card", "overdraft": "Overdraft",
                                      "investment": "Investment loan", "working_capital": "Working capital",
                                      "project_finance": "Project finance"})
groups = Nomenclature("product group", {"mortgage": "retail", "consumer": "retail", "credit_card": "retail",
                                        "overdraft": "retail", "investment": "business",
                                        "working_capital": "business", "project_finance": "business"})

with open("data/loans.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))
rows = groups.apply(names.apply(rows, "product", "product_name"), "product", "group")

print(Counter(r["product_name"] for r in rows).most_common(3))
print(Counter(r["group"] for r in rows))
```

The new column, then a total per label - the outstanding per stage name, the `GROUP BY`
of session 6:

```python run
import csv
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def apply(self, rows, column, new_column, default=None):
        return [row | {new_column: self.codes.get(row[column], default)} for row in rows]


stages = Nomenclature("stage", {"1": "performing", "2": "under-performing", "3": "non-performing"})
with open("data/loans.csv", encoding="utf-8") as file:
    rows = stages.apply(list(csv.DictReader(file)), "stage", "stage_name")

total = defaultdict(float)
for row in rows:
    total[row["stage_name"]] += float(row["outstanding"])
for name, amount in total.items():
    print(f"{name:<18}{amount:>18,.2f}")
```

::: warning Do not change the rows you were given
An `apply` that writes into the input rows (`row[new_column] = ...`) changes the data of
the caller - a second nomenclature, a second report, all see the change. `row | {...}`
makes a new row and leaves the input as it was:

```python run
rows = [{"loan_id": "L1", "stage": "1"}]
codes = {"1": "performing"}

def apply_in_place(rows, column, new_column):
    for row in rows:
        row[new_column] = codes.get(row[column])        # changes the caller's rows
    return rows

result = apply_in_place(rows, "stage", "stage_name")
print(rows)                    # the input has the new column too
print(result is rows)          # the "result" is the same list
```
:::

### The unmapped report

`apply` should also tell what it could not map. Return the new rows **and** a
`Counter` of the unknown values:

```python run
import csv
from collections import Counter
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def apply(self, rows, column, new_column, default=None):
        new_rows, unmapped = [], Counter()
        for row in rows:
            label = self.codes.get(row[column])
            if label is None:
                unmapped[row[column]] += 1
                label = default
            new_rows.append(row | {new_column: label})
        return new_rows, unmapped


products = Nomenclature("product", {"mortgage": "Mortgage loan", "consumer": "Consumer loan",
                                    "credit_card": "Credit card", "overdraft": "Overdraft"})
with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

rows, unmapped = products.apply(loans, "product", "product_name", default="(unknown)")
print(len(rows), "rows; unmapped:", dict(unmapped))
```

### Strict or lenient?

For some reports, an unknown code is acceptable (show it as "unknown"); for others it
must **stop** the process (session 9: when to stop, when to go on). One parameter
decides:

```python run
from collections import Counter
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def apply(self, rows, column, new_column, default=None, strict=False):
        new_rows, unmapped = [], Counter()
        for row in rows:
            label = self.codes.get(row[column])
            if label is None:
                unmapped[row[column]] += 1
                label = default
            new_rows.append(row | {new_column: label})
        if strict and unmapped:
            raise ValueError(f"{self.name}: unknown codes in {column!r}: {dict(unmapped)}")
        return new_rows, unmapped


stages = Nomenclature("stage", {"1": "performing", "2": "under-performing", "3": "non-performing"})
rows = [{"loan_id": "L1", "stage": "1"}, {"loan_id": "L2", "stage": "4"}]
print(stages.apply(rows, "stage", "stage_name")[1])
stages.apply(rows, "stage", "stage_name", strict=True)
```

### The same nomenclature, another dataset

`loans_export.csv` has the same products - but written by another system: some are
empty, and the column is called `Product`. The **same** object maps both; only the
column name changes:

```python run
import csv
from collections import Counter
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def apply(self, rows, column, new_column, default=None):
        new_rows, unmapped = [], Counter()
        for row in rows:
            label = self.codes.get(row[column])
            if label is None:
                unmapped[row[column]] += 1
                label = default
            new_rows.append(row | {new_column: label})
        return new_rows, unmapped


products = Nomenclature("product", {"mortgage": "Mortgage loan", "consumer": "Consumer loan",
                                    "credit_card": "Credit card", "overdraft": "Overdraft",
                                    "investment": "Investment loan", "working_capital": "Working capital",
                                    "project_finance": "Project finance"})

with open("data/loans.csv", encoding="utf-8") as file:
    _, unmapped_a = products.apply(list(csv.DictReader(file)), "product", "product_name")
with open("data/loans_export.csv", encoding="utf-8-sig") as file:
    _, unmapped_b = products.apply(list(csv.DictReader(file, delimiter=";")), "Product", "product_name")

print("loans.csv:       ", dict(unmapped_a))
print("loans_export.csv:", dict(unmapped_b))          # 3 empty products
```

This is "apply consistently across datasets": one definition, many inputs, and the
same report of what did not fit.

::: info The same in pandas
A nomenclature's dictionary works directly with `Series.map` (session 15); the unknown
values become `NaN` and are easy to count:

```python run
import pandas as pd

codes = {"mortgage": "Mortgage loan", "consumer": "Consumer loan", "overdraft": "Overdraft"}
loans = pd.read_csv("data/loans.csv")
names = loans["product"].map(codes)
print(names.isna().sum(), "unmapped;", loans.loc[names.isna(), "product"].value_counts().to_dict())
```
:::

::: tip Try it
Apply the stage nomenclature to `loans_export.csv` (column `Stage`) and to
`loans.csv` (column `stage`) with `strict=True`. Do both pass?
:::

## 5. `classmethod` and `staticmethod`

### `classmethod`: another way to create an object

Nomenclatures live in files and databases. A **class method** is a method of the
**class**, not of an object: its first parameter is the class itself (`cls`), and it is
used as an **alternative constructor** - like `CNTLIN=` builds a format from a dataset:

```python run
import csv
from collections import Counter
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict
    version: str = "1"

    @classmethod
    def from_pairs(cls, name, pairs, **metadata):
        """A nomenclature from (code, label) pairs; duplicate codes are an error."""
        pairs = list(pairs)
        duplicates = sorted(c for c, n in Counter(code for code, _ in pairs).items() if n > 1)
        if duplicates:
            raise ValueError(f"{name}: duplicate codes {duplicates}")
        return cls(name, dict(pairs), **metadata)

    @classmethod
    def from_csv(cls, path, code_column, label_column, name=None, encoding="utf-8", delimiter=",", **metadata):
        """A nomenclature from two columns of a CSV file."""
        with open(path, encoding=encoding, newline="") as file:
            rows = list(csv.DictReader(file, delimiter=delimiter))
        return cls.from_pairs(name or label_column, ((r[code_column], r[label_column]) for r in rows), **metadata)


grades = Nomenclature.from_csv("data/rating_scale.csv", "rating", "grade", version="2026")
print(grades)
regions = Nomenclature.from_csv("data/regions_bg.csv", "code", "name_en", name="region", encoding="cp1251")
print(regions.codes)
```

- `@classmethod` above the method; the first parameter `cls` is the class - here
  `Nomenclature`. `cls(...)` creates the object, so a **subclass** (section 6) that
  calls `from_csv` gets an object of the subclass.
- The call is on the class: `Nomenclature.from_csv(...)`.
- A file with a duplicate code is refused - the check of section 3, now built into the
  way the file is read:

```python run
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Nomenclature:
    name: str
    codes: dict

    @classmethod
    def from_csv(cls, path, code_column, label_column):
        with open(path, encoding="utf-8", newline="") as file:
            pairs = [(r[code_column], r[label_column]) for r in csv.DictReader(file)]
        duplicates = sorted(c for c, n in Counter(c for c, _ in pairs).items() if n > 1)
        if duplicates:
            raise ValueError(f"{path}: duplicate codes {duplicates}")
        return cls(label_column, dict(pairs))


Path("out").mkdir(exist_ok=True)
Path("out/products.csv").write_text("code,name\nmortgage,Mortgage loan\noverdraft,Overdraft\nmortgage,Housing loan\n",
                                    encoding="utf-8")
try:
    Nomenclature.from_csv("out/products.csv", "code", "name")
except ValueError as error:
    print(error)
```
- The same file can give **several** nomenclatures - other columns, another
  direction:

```python run
import csv
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    @classmethod
    def from_csv(cls, path, code_column, label_column, name=None, encoding="utf-8"):
        with open(path, encoding=encoding, newline="") as file:
            return cls(name or label_column, {r[code_column]: r[label_column] for r in csv.DictReader(file)})


en_to_code = Nomenclature.from_csv("data/regions_bg.csv", "name_en", "code", "region code", "cp1251")
bg_to_en = Nomenclature.from_csv("data/regions_bg.csv", "name_bg", "name_en", "region (from Bulgarian)", "cp1251")
print(en_to_code.codes["Stara Zagora"], bg_to_en.codes["Русе"])
```

A class method can also build a **first draft** of a nomenclature from the data itself -
the distinct values of a column, each code its own label. The owner then writes the
real labels:

```python run
import csv
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    @classmethod
    def from_values(cls, name, values):
        """A draft: the distinct values, sorted; the label is the code."""
        return cls(name, {v: v for v in sorted(set(values)) if v})


with open("data/clients.csv", encoding="utf-8") as file:
    regions = Nomenclature.from_values("region", [row["region"] for row in csv.DictReader(file)])
print(len(regions.codes), list(regions.codes))
```

The trap: a normal method called on the **class** has no object for `self`:

```python run
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    def lookup(self, code, default=None):
        return self.codes.get(code, default)


stages = Nomenclature("stage", {"1": "performing"})
print(stages.lookup("1"))                   # on an object: fine
Nomenclature.lookup("1")
# TypeError: Nomenclature.lookup() missing 1 required positional argument: 'code'
# - "1" was taken as self
```

### `staticmethod`: a helper that needs no object

A **static method** has neither `self` nor `cls` - it is a plain function that lives in
the class because it belongs to its job. For example, the cleaning of a code before the
lookup (session 7):

```python run
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict
    case: str = "keep"                    # "lower", "upper" or "keep"

    @staticmethod
    def clean_text(value):
        """One space between words, no spaces at the ends; non-text values unchanged."""
        return " ".join(value.split()) if isinstance(value, str) else value

    def normalize(self, code):
        code = self.clean_text(code)
        if isinstance(code, str) and self.case == "lower":
            return code.lower()
        if isinstance(code, str) and self.case == "upper":
            return code.upper()
        return code

    def lookup(self, code, default=None):
        return self.codes.get(self.normalize(code), default)


products = Nomenclature("product", {"credit_card": "Credit card", "overdraft": "Overdraft"}, case="lower")
print(products.lookup(" OVERDRAFT "), products.lookup("Credit_Card"))
print(Nomenclature.clean_text("  credit   card "))       # usable without an object
```

| Kind | First parameter | Called on | Use it for |
|---|---|---|---|
| a method | `self` - the object | an object: `nom.lookup(x)` | work with the data of one object |
| `@classmethod` | `cls` - the class | the class: `Nomenclature.from_csv(...)` | alternative constructors |
| `@staticmethod` | none | either | a helper that needs neither |

`normalize` needs `self` (it reads `self.case`), so it is a normal method; `clean_text`
needs nothing, so it is static.

A class method knows **which** class it was called on - a subclass gets objects of the
subclass, without writing its own `from_pairs`:

```python run
from dataclasses import dataclass

@dataclass
class Nomenclature:
    name: str
    codes: dict

    @classmethod
    def from_pairs(cls, name, pairs):
        return cls(name, dict(pairs))


class CurrencyList(Nomenclature):
    pass


currencies = CurrencyList.from_pairs("currency", [("EUR", "Euro"), ("USD", "US dollar")])
print(type(currencies).__name__, isinstance(currencies, Nomenclature))
```

### The class so far, as a module

All the pieces of sections 2 - 5 together, in a module `nomenclature.py` (session 10)
that the next sections import. (On this page: run this example first.)

```python run
from pathlib import Path

Path("nomenclature.py").write_text('''"""nomenclature.py - nomenclatures as classes."""
import csv
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date


@dataclass
class Nomenclature:
    """A code list with its metadata, validation rules and processing methods."""
    name: str
    codes: dict                         # code -> label
    version: str = "1"
    valid_from: date | None = None
    owner: str = ""
    code_pattern: str = r".+"
    case: str = "keep"                  # how codes are normalised: "lower", "upper", "keep"

    def __post_init__(self):
        if not self.codes:
            raise ValueError(f"{self.name}: the nomenclature has no codes")
        for code, label in self.codes.items():
            if not re.fullmatch(self.code_pattern, str(code)):
                raise ValueError(f"{self.name}: code {code!r} does not fit {self.code_pattern!r}")
            if label is None or str(label).strip() == "":
                raise ValueError(f"{self.name}: code {code!r} has no label")
        self.codes = dict(self.codes)

    def __repr__(self):
        return f"<{type(self).__name__} {self.name!r} v{self.version}: {len(self)} codes>"

    def __len__(self):
        return len(self.codes)

    def __contains__(self, code):
        return self.lookup(code) is not None

    def __iter__(self):
        return iter(self.codes)

    @staticmethod
    def clean_text(value):
        return " ".join(value.split()) if isinstance(value, str) else value

    def normalize(self, code):
        code = self.clean_text(code)
        if isinstance(code, str) and self.case == "lower":
            return code.lower()
        if isinstance(code, str) and self.case == "upper":
            return code.upper()
        return code

    def lookup(self, code, default=None):
        """The label of a code; `default` if the code is unknown."""
        return self.codes.get(self.normalize(code), default)

    def validate(self, values):
        """The values that are not codes, with their counts."""
        return Counter(v for v in values if v not in self)

    def apply(self, rows, column, new_column, default=None, strict=False):
        """New rows with new_column = lookup(row[column]); also a Counter of the unmapped values."""
        new_rows, unmapped = [], Counter()
        for row in rows:
            value = self.lookup(row[column])
            if value is None:
                unmapped[row[column]] += 1
                value = default
            new_rows.append(row | {new_column: value})
        if strict and unmapped:
            raise ValueError(f"{self.name}: unknown values in {column!r}: {dict(unmapped)}")
        return new_rows, unmapped

    @classmethod
    def from_pairs(cls, name, pairs, **metadata):
        pairs = list(pairs)
        duplicates = sorted(str(c) for c, n in Counter(code for code, _ in pairs).items() if n > 1)
        if duplicates:
            raise ValueError(f"{name}: duplicate codes {duplicates}")
        return cls(name, dict(pairs), **metadata)

    @classmethod
    def from_csv(cls, path, code_column, label_column, name=None, encoding="utf-8", delimiter=",", **metadata):
        with open(path, encoding=encoding, newline="") as file:
            rows = list(csv.DictReader(file, delimiter=delimiter))
        return cls.from_pairs(name or label_column, ((r[code_column], r[label_column]) for r in rows), **metadata)
''', encoding="utf-8")

import sys
sys.modules.pop("nomenclature", None)          # only on this page: read the new file
from nomenclature import Nomenclature

products = Nomenclature.from_pairs("product", [("mortgage", "Mortgage loan"), ("overdraft", "Overdraft")],
                                   case="lower")
print(products, products.lookup(" Overdraft"), "MORTGAGE" in products)
```

::: tip Try it
Use `Nomenclature.from_csv` to build a nomenclature `rating -> description` from
`rating_scale.csv`, and apply it to `clients.csv` (column `rating`) with `apply`. How
many clients have the description `"elevated risk"`?
:::

## 6. Inheritance: banded and hierarchical nomenclatures

### "A banded nomenclature is a nomenclature"

Some nomenclatures do not map **codes** but **ranges**: days past due to a bucket, a PD
to a grade, an amount to a size class. In SAS, a range format:

```sas
proc format;
    value dpd  0 = 'current'  1 - 30 = '1-30'  31 - 90 = '31-90'  91 - high = '90+';
run;
```

Everything else stays the same: a name, metadata, codes with labels, `apply`,
`validate`. Only `lookup` works differently. That is what **inheritance** is for: a
**subclass** takes everything of its **base class**, and changes or adds only what is
different:

```python run
import sys
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature           # written in section 5


@dataclass(repr=False)
class BandedNomenclature(Nomenclature):
    """Codes for ranges of a number: bands of (low, high, code), low <= x < high."""
    bands: list = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()                      # all the checks of the base class
        for low, high, code in self.bands:
            if code not in self.codes:
                raise ValueError(f"{self.name}: band code {code!r} is not a code")
            if not low < high:
                raise ValueError(f"{self.name}: empty band {low} - {high}")
        for (_, high, _), (low, _, _) in zip(self.bands, self.bands[1:]):
            if high != low:
                raise ValueError(f"{self.name}: gap or overlap at {high} / {low}")

    def lookup(self, value, default=None):           # OVERRIDES lookup of the base class
        """The code of the band that contains value."""
        for low, high, code in self.bands:
            if low <= value < high:
                return code
        return default


INF = float("inf")
dpd = BandedNomenclature("dpd bucket",
                         {"current": "no delay", "1-30": "1 to 30 days", "31-90": "31 to 90 days", "90+": "over 90 days"},
                         bands=[(0, 1, "current"), (1, 31, "1-30"), (31, 91, "31-90"), (91, INF, "90+")])

print(dpd)
print([dpd.lookup(d) for d in (0, 1, 30, 31, 90, 91, 400)])
print(isinstance(dpd, BandedNomenclature), isinstance(dpd, Nomenclature))
```

- `class BandedNomenclature(Nomenclature)` - the base class in brackets. The subclass
  **is a** `Nomenclature`: it has all its fields and methods.
- `lookup` is **overridden**: the subclass has its own version, and every call of
  `lookup` - also the one **inside** `apply` and `__contains__`, written in the base
  class - uses it. This is the power of inheritance.
- `super().__post_init__()` runs the checks of the base class first, then the new
  checks. Without it, the base checks would be lost.

The checks of the subclass find a gap between two bands - a value in the gap would get
no bucket:

```python run
import sys
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


@dataclass(repr=False)
class BandedNomenclature(Nomenclature):
    bands: list = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        for (_, high, _), (low, _, _) in zip(self.bands, self.bands[1:]):
            if high != low:
                raise ValueError(f"{self.name}: gap or overlap at {high} / {low}")


try:
    BandedNomenclature("dpd", {"current": "-", "1-30": "-", "90+": "-"},
                       bands=[(0, 1, "current"), (1, 31, "1-30"), (91, 9999, "90+")])
except ValueError as error:
    print(error)
```

Python looks for a method first in the class of the object, then in its base classes,
in an order called the **MRO** (method resolution order):

```python run
import sys
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


@dataclass(repr=False)
class BandedNomenclature(Nomenclature):
    bands: list = field(default_factory=list)

    def lookup(self, value, default=None):
        return next((code for low, high, code in self.bands if low <= value < high), default)


print([cls.__name__ for cls in BandedNomenclature.__mro__])
print("lookup" in vars(BandedNomenclature), "apply" in vars(BandedNomenclature), "apply" in vars(Nomenclature))
```

`lookup` is found in `BandedNomenclature` itself; `apply` is not there, so Python takes
it from `Nomenclature`. (`object` is the base of every class in Python.)

`apply` was never written for bands - it comes from the base class and works:

```python run
import csv
import sys
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


@dataclass(repr=False)
class BandedNomenclature(Nomenclature):
    bands: list = field(default_factory=list)

    def lookup(self, value, default=None):
        for low, high, code in self.bands:
            if low <= value < high:
                return code
        return default


dpd = BandedNomenclature("dpd bucket", {"current": "-", "1-30": "-", "31-90": "-", "90+": "-"},
                         bands=[(0, 1, "current"), (1, 31, "1-30"), (31, 91, "31-90"), (91, float("inf"), "90+")])

with open("data/loans.csv", encoding="utf-8") as file:
    loans = [row | {"days_past_due": int(row["days_past_due"])} for row in csv.DictReader(file)]

rows, unmapped = dpd.apply(loans, "days_past_due", "bucket")
from collections import Counter
print(Counter(r["bucket"] for r in rows), dict(unmapped))
```

### The rating scale as bands of PD

`rating_scale.csv` is a banded nomenclature: each grade has a PD band. A class method of
the subclass builds it from the file:

```python run
import csv
import sys
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


@dataclass(repr=False)
class BandedNomenclature(Nomenclature):
    bands: list = field(default_factory=list)

    def lookup(self, value, default=None):
        for low, high, code in self.bands:
            if low <= value < high:
                return code
        return default

    @classmethod
    def rating_scale(cls, path):
        """grade -> description, with the PD band of each grade."""
        with open(path, encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        codes = {r["grade"]: r["description"] for r in rows}
        bands = [(float(r["pd_min"]), float(r["pd_max"]), r["grade"]) for r in rows]
        low, high, grade = bands[-1]                   # D: PD = 1.0 exactly
        bands[-1] = (low, high + 1e-9, grade)
        return cls("rating scale", codes, version="2026", bands=bands)


scale = BandedNomenclature.rating_scale("data/rating_scale.csv")
print(scale)
for pd_value in (0.0003, 0.0043, 0.02, 0.15, 1.0):
    grade = scale.lookup(pd_value)
    print(f"PD {pd_value:<7} -> {grade:<4} {scale.codes[grade]}")
```

`cls(...)` in the class method makes a `BandedNomenclature` - the class it was called
on.

A consistency check of the data: the PD of each client's rating (the middle of its
band) must map back to the client's own grade:

```python run
import csv

with open("data/rating_scale.csv", encoding="utf-8") as file:
    scale = list(csv.DictReader(file))
grade_of_rating = {int(r["rating"]): r["grade"] for r in scale}
pd_of_rating = {int(r["rating"]): (float(r["pd_min"]) + float(r["pd_max"])) / 2 for r in scale}
bands = [(float(r["pd_min"]), float(r["pd_max"]) + (1e-9 if r["grade"] == "D" else 0), r["grade"]) for r in scale]

def grade_of_pd(pd_value):
    return next((g for low, high, g in bands if low <= pd_value < high), None)

with open("data/clients.csv", encoding="utf-8") as file:
    ratings = [int(r["rating"]) for r in csv.DictReader(file)]
mismatches = [r for r in ratings if grade_of_pd(pd_of_rating[r]) != grade_of_rating[r]]
print(len(ratings), "clients,", len(mismatches), "mismatches")
```

An override can also **extend** the method of the base class with `super()` - here the
`repr` gets the number of bands:

```python run
import sys
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


@dataclass(repr=False)
class BandedNomenclature(Nomenclature):
    bands: list = field(default_factory=list)

    def __repr__(self):
        return super().__repr__()[:-1] + f", {len(self.bands)} bands>"


sizes = BandedNomenclature("size", {"small": "below 50k", "medium": "50k - 1m", "large": "from 1m"},
                           bands=[(0, 50_000, "small"), (50_000, 1_000_000, "medium"), (1_000_000, float("inf"), "large")])
print(sizes)
```

### A hierarchy: products and their groups

Another kind: each code has a **parent** - a product belongs to a group, a region to a
country, an industry to a sector. A subclass adds the parents and two methods:

```python run
import sys
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


@dataclass(repr=False)
class HierarchicalNomenclature(Nomenclature):
    parents: dict = field(default_factory=dict)      # code -> parent code

    def __post_init__(self):
        super().__post_init__()
        missing = [code for code in self.codes if code not in self.parents]
        if missing:
            raise ValueError(f"{self.name}: no parent for {missing}")

    def parent(self, code):
        return self.parents.get(self.normalize(code))

    def children(self, parent):
        return sorted(code for code, p in self.parents.items() if p == parent)


products = HierarchicalNomenclature(
    "product",
    {"mortgage": "Mortgage loan", "consumer": "Consumer loan", "credit_card": "Credit card",
     "overdraft": "Overdraft", "investment": "Investment loan", "working_capital": "Working capital",
     "project_finance": "Project finance"},
    case="lower",
    parents={"mortgage": "retail", "consumer": "retail", "credit_card": "retail", "overdraft": "retail",
             "investment": "business", "working_capital": "business", "project_finance": "business"})

print(products.parent("Mortgage"), products.children("business"))
print(products.lookup("project_finance"), len(products))
```

Here nothing is overridden except `__post_init__` (with `super()`); the subclass only
**adds**. Both are normal uses of inheritance.

On the portfolio: the outstanding per product **group**, through `parent`:

```python run
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


@dataclass(repr=False)
class HierarchicalNomenclature(Nomenclature):
    parents: dict = field(default_factory=dict)

    def parent(self, code):
        return self.parents.get(self.normalize(code))


groups = {"mortgage": "retail", "consumer": "retail", "credit_card": "retail", "overdraft": "retail",
          "investment": "business", "working_capital": "business", "project_finance": "business"}
products = HierarchicalNomenclature("product", {code: code.replace("_", " ") for code in groups}, parents=groups)

total = defaultdict(float)
with open("data/loans.csv", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        total[products.parent(row["product"])] += float(row["outstanding"])
print({group: round(amount, 2) for group, amount in total.items()})
```

::: warning Forget `super()`, lose the checks
A subclass with its own `__post_init__` **replaces** the one of the base class. Without
`super().__post_init__()`, the checks of the base class do not run - an empty
nomenclature is created without a word:

```python run
import sys
from dataclasses import dataclass, field

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


@dataclass(repr=False)
class HierarchicalNomenclature(Nomenclature):
    parents: dict = field(default_factory=dict)

    def __post_init__(self):                          # no super().__post_init__()
        missing = [code for code in self.codes if code not in self.parents]
        if missing:
            raise ValueError(f"{self.name}: no parent for {missing}")


empty = HierarchicalNomenclature("product", {})       # the base class would refuse it
print(empty, len(empty))
```
:::

::: warning Inheritance or a new field?
Inherit when the new kind **is a** nomenclature that works differently (bands) or has
more (parents). Do not inherit just to reuse two lines of code - a function or a
module does that. Deep chains of subclasses are hard to follow; one level is usually
enough.
:::

::: tip Try it
Make a `BandedNomenclature` for the size of a loan: `small` below 50,000, `medium`
below 1,000,000, `large` from 1,000,000. Apply it to the outstanding amounts of
`loans.csv` and count the loans per size.
:::

## 7. Composition: a registry, many datasets

### A registry "has" nomenclatures

A report uses many nomenclatures. A **registry** keeps them in one place, by name, and
applies several at once. It does not inherit from `Nomenclature` - it **has**
nomenclatures inside: this is **composition**.

```python run
import sys
from collections import Counter

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


class Registry:
    """The nomenclatures of a report, by name."""

    def __init__(self):
        self._items = {}

    def register(self, nomenclature):
        if nomenclature.name in self._items:
            raise ValueError(f"{nomenclature.name!r} is already registered")
        self._items[nomenclature.name] = nomenclature

    def get(self, name):
        return self._items[name]

    def __repr__(self):
        return f"<Registry: {', '.join(f'{n} v{x.version}' for n, x in self._items.items())}>"

    def apply(self, rows, plan):
        """plan: {column: (nomenclature name, new column)} -> (rows, {column: Counter of unmapped})."""
        report = {}
        for column, (name, new_column) in plan.items():
            rows, unmapped = self.get(name).apply(rows, column, new_column)
            report[column] = unmapped
        return rows, report


registry = Registry()
registry.register(Nomenclature("stage", {"1": "performing", "2": "under-performing", "3": "non-performing"}))
registry.register(Nomenclature("currency", {"EUR": "Euro", "USD": "US dollar"}, version="2026.2"))
print(registry)

rows = [{"loan_id": "L1", "stage": "1", "currency": "EUR"}, {"loan_id": "L2", "stage": "3", "currency": "GBP"}]
rows, report = registry.apply(rows, {"stage": ("stage", "stage_name"), "currency": ("currency", "currency_name")})
print(rows[1])
print({column: dict(c) for column, c in report.items()})
```

Ask the registry what it knows - `in` and a list of the names, with special methods of
the registry itself:

```python run
import sys

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


class Registry:
    def __init__(self, *nomenclatures):
        self._items = {n.name: n for n in nomenclatures}

    def __contains__(self, name):
        return name in self._items

    def names(self):
        return sorted(self._items)


registry = Registry(Nomenclature("stage", {"1": "performing"}), Nomenclature("currency", {"EUR": "Euro"}))
print(registry.names(), "stage" in registry, "product" in registry)
```

| | Inheritance | Composition |
|---|---|---|
| relation | `BandedNomenclature` **is a** `Nomenclature` | a `Registry` **has** nomenclatures |
| in the code | `class B(A):` | an attribute that holds objects |
| use it when | the new thing is a special kind of the old | the new thing uses or collects the old |

The registry holds the **objects**, not copies. Change a nomenclature once - a new
code - and every dataset that the registry maps sees the change:

```python run
import sys

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


class Registry:
    def __init__(self, *nomenclatures):
        self._items = {n.name: n for n in nomenclatures}

    def get(self, name):
        return self._items[name]


currencies = Nomenclature("currency", {"EUR": "Euro", "USD": "US dollar"})
registry = Registry(currencies)
print(registry.get("currency") is currencies)        # the same object

currencies.codes["GBP"] = "Pound sterling"           # a new code, added once
print(registry.get("currency").lookup("GBP"))
```

### One registry, three datasets

The point of the client's sentence: the **same** nomenclatures applied in the **same**
way to different datasets - loans, clients, and the rating history:

```python run
import csv
import sys

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature

stages = Nomenclature("stage", {"1": "performing", "2": "under-performing", "3": "non-performing"})
grades = Nomenclature.from_csv("data/rating_scale.csv", "rating", "grade", name="grade")
regions = Nomenclature.from_csv("data/regions_bg.csv", "name_en", "code", name="region code", encoding="cp1251")

def read(path):
    with open(path, encoding="utf-8") as file:
        return list(csv.DictReader(file))

datasets = {
    "loans": (read("data/loans.csv"), [(stages, "stage", "stage_name")]),
    "clients": (read("data/clients.csv"), [(grades, "rating", "grade"), (regions, "region", "region_code")]),
    "ratings_history": (read("data/ratings_history.csv"), [(grades, "rating", "grade")]),
}

for name, (rows, plan) in datasets.items():
    for nomenclature, column, new_column in plan:
        rows, unmapped = nomenclature.apply(rows, column, new_column)
        print(f"{name:<16}{column:<8}-> {new_column:<12} rows {len(rows):>5}, unmapped {sum(unmapped.values())}")
```

`grades` maps the ratings of `clients.csv` **and** of `ratings_history.csv` - one
definition, one version, one place to change it.

With a registry and a plan per dataset, the check of the two loan files becomes one
loop - and the report for the data owner lists every column that did not map:

```python run
import csv
import sys

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature

registry = {
    "stage": Nomenclature("stage", {"1": "performing", "2": "under-performing", "3": "non-performing"}),
    "currency": Nomenclature("currency", {"EUR": "Euro", "USD": "US dollar"}),
    "product": Nomenclature.from_pairs("product", [(p, p) for p in ["mortgage", "consumer", "credit_card",
                                       "overdraft", "investment", "working_capital", "project_finance"]]),
}
plans = {
    "loans.csv": ({"delimiter": ",", "encoding": "utf-8"}, {"stage": "stage", "currency": "currency", "product": "product"}),
    "loans_export.csv": ({"delimiter": ";", "encoding": "utf-8-sig"}, {"Stage": "stage", "Currency": "currency", "Product": "product"}),
}

for file_name, (options, plan) in plans.items():
    with open("data/" + file_name, encoding=options["encoding"]) as file:
        rows = list(csv.DictReader(file, delimiter=options["delimiter"]))
    for column, name in plan.items():
        _, unmapped = registry[name].apply(rows, column, column + "_label")
        if unmapped:
            print(f"{file_name}: {column}: {dict(unmapped)}")
print("checked", len(plans), "files")
```

And the product nomenclature with `case="lower"` maps the export of another system as
well, where a code could come in capitals - the normalisation is part of the
nomenclature, not of each report:

```python run
import csv
import sys

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature

products = Nomenclature.from_pairs("product", [
    ("mortgage", "Mortgage loan"), ("consumer", "Consumer loan"), ("credit_card", "Credit card"),
    ("overdraft", "Overdraft"), ("investment", "Investment loan"), ("working_capital", "Working capital"),
    ("project_finance", "Project finance")], case="lower")

with open("data/loans_export.csv", encoding="utf-8-sig") as file:
    rows = [row | {"Product": row["Product"].upper()} for row in csv.DictReader(file, delimiter=";")]
print(rows[0]["Product"])
rows, unmapped = products.apply(rows, "Product", "product_name", default="(missing)")
print(rows[0]["product_name"], dict(unmapped))
```

::: tip Try it
Add the hierarchical product nomenclature (section 6) to the plan of `loans`, and a
second step that maps the product group. (Hint: `apply` with `lookup` gives the name;
for the group, a second `Nomenclature` built from `products.parents`.)
:::

## 8. Versions: what changed?

Nomenclatures change: a new product, a renamed region, a new rating scale. The
metadata says **which** version a report used; a `diff` says **what** changed between
two versions - the report a data owner signs:

```python run
import sys
from datetime import date

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature


def diff(old, new):
    """Added, removed and changed codes from old to new."""
    added = sorted(set(new.codes) - set(old.codes))
    removed = sorted(set(old.codes) - set(new.codes))
    changed = sorted(c for c in set(old.codes) & set(new.codes) if old.codes[c] != new.codes[c])
    return {"added": added, "removed": removed, "changed": {c: (old.codes[c], new.codes[c]) for c in changed}}


v1 = Nomenclature("product", {"mortgage": "Mortgage loan", "consumer": "Consumer loan", "leasing": "Leasing"},
                  version="1", valid_from=date(2025, 1, 1))
v2 = Nomenclature("product", {"mortgage": "Housing loan", "consumer": "Consumer loan", "overdraft": "Overdraft"},
                  version="2", valid_from=date(2026, 7, 1))

print(f"{v1.name}: v{v1.version} ({v1.valid_from}) -> v{v2.version} ({v2.valid_from})")
print(diff(v1, v2))
```

The rating scale of the file against a recalibrated copy - what would the owner sign?

```python run
import csv
import sys

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature

current = Nomenclature.from_csv("data/rating_scale.csv", "grade", "pd_max", name="pd_max", version="2026")
proposal = Nomenclature("pd_max", current.codes | {"CCC": "0.12", "CC": "0.27"}, version="2027-draft")

changed = {g: (current.codes[g], proposal.codes[g]) for g in current.codes if current.codes[g] != proposal.codes[g]}
print(f"v{current.version} -> v{proposal.version}: {changed}")
```

Before a new version goes live: which **loans** change their label? The impact on the
data, not only on the list:

```python run
import csv
import sys

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature

v1 = Nomenclature("product", {"mortgage": "Mortgage loan", "consumer": "Consumer loan", "overdraft": "Overdraft"}, version="1")
v2 = Nomenclature("product", {"mortgage": "Housing loan", "consumer": "Consumer loan", "overdraft": "Overdraft"}, version="2")

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

moved = [l for l in loans if v1.lookup(l["product"]) != v2.lookup(l["product"])]
print(len(moved), "loans get another label, outstanding", f"{sum(float(l['outstanding']) for l in moved):,.2f}")
```

And a code **removed** in the new version, but still used by the data, must stop the
release - `validate` of the new version on the current data finds it:

```python run
import csv
import sys

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature

current = ["mortgage", "consumer", "credit_card", "overdraft", "investment", "working_capital", "project_finance"]
proposal = Nomenclature.from_pairs("product", [(p, p) for p in current if p != "credit_card"], version="2027-draft")

with open("data/loans.csv", encoding="utf-8") as file:
    products = [row["product"] for row in csv.DictReader(file)]
print(f"v{proposal.version} would leave unmapped:", dict(proposal.validate(products)))
```

A nomenclature can also be **saved** with its metadata - a small CSV with the version
in the file name, read back with `from_csv`:

```python run
import csv
import sys
from pathlib import Path

sys.modules.pop("nomenclature", None)
from nomenclature import Nomenclature

stages = Nomenclature("stage", {"1": "performing", "2": "under-performing", "3": "non-performing"}, version="2026.1")

Path("out").mkdir(exist_ok=True)
path = Path("out") / f"nomenclature_{stages.name}_v{stages.version}.csv"
with open(path, "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["code", "label"])
    writer.writerows(stages.codes.items())

again = Nomenclature.from_csv(path, "code", "label", name="stage", version="2026.1")
print(path.name, again.codes == stages.codes)
```

In the class, `diff` would be a method: `v1.diff(v2)`. The Self-study goes one step
further: several versions in one object, and the right one for a report date.

::: tip Try it
Make `diff` a method of a subclass `VersionedNomenclature(Nomenclature)`, and print a
one-line summary: `"v1 -> v2: 1 added, 1 removed, 1 changed"`.
:::

## 9. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: `git pull upstream main`) and run the tasks from the
terminal, in the repository root:

```bash
python 12-oop-nomenclatures/practice/task1-nomenclature-basics.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-nomenclature-basics.py` | A `Nomenclature` dataclass with metadata, `lookup`, `len`, `in` |
| 2 | `task2-predict-oop.py` | Predict: `classmethod`, `staticmethod`, overriding, `super()`, `isinstance` |
| 3 | `task3-validation.py` | The rules at creation, duplicate codes, `validate(values)` |
| 4 | `task4-apply.py` | `apply` to a list of rows, the unmapped report, `strict` |
| 5 | `task5-banded.py` | `BandedNomenclature`: DPD buckets, PD -> grade, size classes |
| 6 | `task6-registry.py` (Optional) | A registry applied to two datasets |

## Summary

| Topic | Remember |
|-------|----------|
| The use case | one class for a nomenclature: data, metadata, validation rules, processing methods |
| Data and metadata | `codes` + `name`, `version`, `valid_from`, `owner`; a short `__repr__`; a copy of the codes |
| Container | `__len__`, `__contains__`, `__iter__` -> `len(nom)`, `code in nom`, `for code in nom` |
| Rules | at creation in `__post_init__` (no codes, bad codes, empty labels); duplicates before the dict is built |
| Dataset checks | `validate(values)` -> a `Counter` of the unknown values; a check report |
| Processing | `apply(rows, column, new_column)` -> new rows + the unmapped values; `strict=True` stops |
| `classmethod` | `cls` as the first parameter; alternative constructors: `from_csv`, `from_pairs` |
| `staticmethod` | no `self`, no `cls`: a helper that belongs to the class |
| Inheritance | `class Banded(Nomenclature)`; override `lookup`; `super().__post_init__()`; "is a" |
| Composition | a `Registry` has nomenclatures; "has a" |
| Consistency | one object for every dataset; the same report of what does not fit |
| Versions | the metadata says which; a `diff` says what changed |

## Homework

1. `12-oop-nomenclatures/homework.py` and `12-oop-nomenclatures/homework_nomenclature.py`
   (in the homework repository): **the nomenclature module of the project** - the
   classes `Nomenclature`, `BandedNomenclature` and `Registry` in a module, three
   nomenclatures built from the files (products with their groups, the rating scale
   with its PD bands, the regions from the cp1251 file), applied to `loans.csv`,
   `clients.csv` and the cleaned cities of `client_register.csv`, and a data quality
   report of the unmapped values. Every check must print `OK`.
2. The practice tasks you did not finish in class.

## Self-study

This part is not covered in class. It is for reading at home: an interface that every
nomenclature must follow, and nomenclatures with several versions in time.

### Abstract base classes: an interface

`Nomenclature` and `BandedNomenclature` both have `lookup`, `apply`, `validate`. A
report can use **any** nomenclature - as long as it has these methods. An **abstract
base class** writes this promise down: it cannot be used directly, and every subclass
**must** implement the abstract methods:

```python run
from abc import ABC, abstractmethod
from collections import Counter


class BaseNomenclature(ABC):
    """What every nomenclature must be able to do."""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def lookup(self, value, default=None):
        """The mapped value of `value`."""

    def apply(self, rows, column, new_column, default=None):     # shared by all
        new_rows, unmapped = [], Counter()
        for row in rows:
            mapped = self.lookup(row[column])
            if mapped is None:
                unmapped[row[column]] += 1
                mapped = default
            new_rows.append(row | {new_column: mapped})
        return new_rows, unmapped


class CodeList(BaseNomenclature):
    def __init__(self, name, codes):
        super().__init__(name)
        self.codes = dict(codes)

    def lookup(self, value, default=None):
        return self.codes.get(value, default)


class Broken(BaseNomenclature):            # forgot lookup
    pass


stages = CodeList("stage", {1: "performing", 2: "under-performing", 3: "non-performing"})
print(stages.apply([{"s": 1}, {"s": 7}], "s", "name"))
try:
    Broken("x")
except TypeError as error:
    print("TypeError:", error)
```

The error comes when the object is **created**, not later in the middle of a report.

**Exercises**

1. Add an abstract method `describe()` that returns one line about the nomenclature,
   and implement it in `CodeList`.
2. Can you create a `BaseNomenclature("x")` directly? Try it, and explain the message.

::: details Answer
1. In `BaseNomenclature`: `@abstractmethod def describe(self): ...`; in `CodeList`:
   `def describe(self): return f"{self.name}: {len(self.codes)} codes"`.
2. No: `TypeError: Can't instantiate abstract class BaseNomenclature without an
   implementation for abstract method 'lookup'` (the exact text depends on the
   Python version). An abstract class is only a base for others.
:::

### Versioned nomenclatures

A rating scale can be recalibrated; a product list changes in July. A report for
**March** must use the version valid in March. A class that keeps several versions,
each with its `valid_from`, and picks the right one for a date:

```python run
from bisect import bisect_right
from dataclasses import dataclass
from datetime import date


@dataclass
class Version:
    valid_from: date
    codes: dict


class VersionedNomenclature:
    def __init__(self, name, versions):
        self.name = name
        self.versions = sorted(versions, key=lambda v: v.valid_from)

    def version_at(self, day):
        i = bisect_right([v.valid_from for v in self.versions], day)     # session 6, Advanced
        if i == 0:
            raise ValueError(f"{self.name}: no version valid on {day}")
        return self.versions[i - 1]

    def lookup(self, code, day, default=None):
        return self.version_at(day).codes.get(code, default)


grades = VersionedNomenclature("grade", [
    Version(date(2020, 1, 1), {4: "BBB", 5: "BB", 6: "B"}),
    Version(date(2026, 4, 1), {4: "BBB+", 5: "BBB-", 6: "BB"}),        # a new scale from April 2026
])

for day in [date(2026, 3, 31), date(2026, 4, 30), date(2026, 9, 30)]:
    print(day, grades.lookup(5, day))
```

With `ratings_history.csv`, each month end is mapped with the version of **that**
month - a report for any past month gives the same result as when it was first made.

**Exercises**

1. Map the ratings of `ratings_history.csv` with `grades` above, using the
   `month_end` of each row. How many rows get `"BBB-"`?
2. What should `version_at` do for a date before the first version? Is raising an
   error the right choice for a report?

::: details Answer
1.
```python
import csv
from datetime import date
with open("data/ratings_history.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))
print(sum(1 for r in rows if grades.lookup(int(r["rating"]), date.fromisoformat(r["month_end"])) == "BBB-"))
```
(The rows with rating 5 from April 2026 on.)
2. Yes for a report: a date without a valid version means the report would use an
   unknown mapping, which is worse than stopping (session 9: wrong settings stop the
   report).
:::

## Read more

- Python tutorial: [Classes - inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- Reference: [`classmethod`](https://docs.python.org/3/library/functions.html#classmethod),
  [`staticmethod`](https://docs.python.org/3/library/functions.html#staticmethod),
  [`super`](https://docs.python.org/3/library/functions.html#super),
  [`abc`](https://docs.python.org/3/library/abc.html),
  [dataclasses - inheritance](https://docs.python.org/3/library/dataclasses.html#inheritance)
- Real Python: [Inheritance and composition: a Python OOP guide](https://realpython.com/inheritance-composition-python/),
  [Python's instance, class, and static methods demystified](https://realpython.com/instance-class-and-static-methods-demystified/)

**Next session:** databases - SQL from Python: connect, query with parameters,
transactions, and the result of a query straight into a DataFrame.
