---
title: "11. OOP: first steps, classes and objects"
---

# 11. OOP: first steps, classes and objects

<div class="lecture-meta">
  <span>Session 11</span><span>practice: <code>11-oop-classes/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- see why everything in Python is an **object**, and what a **class** is;
- write your own class: its data (**attributes**) and its behaviour (**methods**);
- give your objects a readable form for reports and for debugging;
- share values between all objects of a class, and keep values per object;
- check the data when an object is created, and compute values with `property`;
- write data classes in a few lines with `@dataclass`;
- make objects work together: a client with its loans.

From a row of data to an object - the same loan, two ways:

```python run
# a dictionary: the data only; the rules are somewhere else
loan = {"loan_id": "L000002", "amount": 1977400.0, "outstanding": 651927.30, "rate": 5.44}
print(round(1 - loan["outstanding"] / loan["amount"], 4))


# a class: the data AND the rules that belong to it
class Loan:
    def __init__(self, loan_id, amount, outstanding, rate):
        self.loan_id = loan_id
        self.amount = amount
        self.outstanding = outstanding
        self.rate = rate

    def repaid_share(self):
        return round(1 - self.outstanding / self.amount, 4)


loan = Loan("L000002", 1977400.0, 651927.30, 5.44)
print(loan.repaid_share())
```

The client asked for this course with one idea in mind: *nomenclatures as structured
entities that combine data, metadata, validation rules and processing methods*. That
is exactly what a class is. Today: the building blocks. Session 12: the nomenclature.

## 1. Why classes; everything is an object

### You use objects every day

Every value in Python is an **object** (session 1): it has a **type**, **data**, and
**methods** - functions that belong to it:

```python run
text = "  c0014 "
amounts = [1044231.30, 651927.30]

print(type(text), text.strip().upper())        # str methods
print(type(amounts))
amounts.append(644.25)                         # a list method changes the list
print(amounts)
print(type(len), type(Exception("x")))
```

A **class** is the blueprint of a type: `str`, `list`, `dict` are classes. An
**object** (or **instance**) is one thing made from the blueprint: `"c0014"` is an
instance of `str`. A DataFrame (session 14) is an instance of the class `DataFrame`,
and `df.groupby(...)` is one of its methods.

```python run
print(isinstance("c0014", str), isinstance([1, 2], list), isinstance(5, float))
print(str.upper("abc"), "abc".upper())          # a method is a function of the class
```

Even numbers and functions are objects, with attributes and methods:

```python run
print((651927).bit_length(), (2.5).is_integer(), (3.0).is_integer())
print(print.__name__, len.__doc__.splitlines()[0])
print(int.__add__(2, 3), 2 + 3)                # + is a method call underneath
```

The objects of the libraries you use have attributes too. A `csv.DictReader` knows
its column names and the line it has read:

```python run
import csv

with open("data/loans.csv", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    print(type(reader).__name__)
    print(reader.fieldnames)              # an attribute: the header
    first = next(reader)                  # a method underneath: read one row
    print(reader.line_num, first["loan_id"])
```

`isinstance` with a tuple tests for several types at once - the usual check of an
input. One trap: `True` and `False` **are** integers in Python:

```python run
for value in [100, 99.5, "100", True]:
    print(repr(value), isinstance(value, (int, float)))
print(True + True, isinstance(True, int))      # bool is a kind of int
```

### When a class helps an analyst

| Use | When |
|---|---|
| a function | one calculation: `expected_loss(pd, lgd, ead)` |
| a dictionary | data without rules: a row of a file, a lookup table |
| a **class** | data **and** the rules that belong to it, used in many places: a loan that knows its stage, a nomenclature that knows its codes and checks them |

In SAS terms: a row of a dataset has its variables, but the rules (stage, bucket,
checks) live in a DATA step somewhere else - and are copied into the next program. A
class keeps the data and the rules **together**, in one place.

::: tip Try it
Find three methods of `dict` you used in session 6 with `[m for m in dir(dict) if not
m.startswith("_")]`. What does `type(dict)` print?
:::

## 2. The first class: `__init__`, `self`, attributes

### Define a class, create objects

```python run
class Loan:
    """One loan of the portfolio."""

    def __init__(self, loan_id, product, amount, outstanding):
        self.loan_id = loan_id
        self.product = product
        self.amount = amount
        self.outstanding = outstanding


first = Loan("L000001", "investment", 1156900.0, 1044231.30)
second = Loan("L000002", "investment", 1977400.0, 651927.30)

print(first.loan_id, first.outstanding)
print(second.loan_id, second.outstanding)
print(type(first), isinstance(first, Loan))
```

- `class Loan:` - the name of a class is in **CamelCase** (PEP 8): `Loan`,
  `RatingGrade`, `DataError`.
- `__init__` is the special method that runs when an object is **created**:
  `Loan("L000001", ...)` creates a new, empty object and calls `__init__` with it.
- `self` is that new object. `self.loan_id = loan_id` stores a value **in the
  object** - an **attribute**.
- Each object has its own attributes: `first.outstanding` and `second.outstanding`
  are different.

![A class Loan as a blueprint, and two objects made from it, each with its own loan_id, product, amount and outstanding](/diagrams/class-objects.svg){.diagram}

### Read and change attributes

```python run
class Loan:
    def __init__(self, loan_id, product, amount, outstanding):
        self.loan_id = loan_id
        self.product = product
        self.amount = amount
        self.outstanding = outstanding


loan = Loan("L000004", "overdraft", 15900.0, 5875.11)
loan.outstanding = 5000.0                 # change an attribute
loan.comment = "reviewed"                 # a NEW attribute, only on this object
print(loan.outstanding, loan.comment)
print(vars(loan))                         # all attributes of the object, as a dict
```

Two objects with the same data are still **two** objects. And two names can point
to **one** object (session 3) - a change through one name is seen through the other:

```python run
class Loan:
    def __init__(self, loan_id, outstanding):
        self.loan_id = loan_id
        self.outstanding = outstanding


a = Loan("L1", 100.0)
b = Loan("L1", 100.0)
print(a == b, a is b)              # different objects (a normal class compares identity)

c = a                              # a second name for the SAME object
c.outstanding = 0.0
print(a.outstanding)
```

(Dataclasses, section 7, compare by value.)

`vars(obj)` shows that an object keeps its attributes in a dictionary - the same
structure as the rows of session 6, with a name and rules around it.

### Objects from a file

The rows of `loans.csv` as `Loan` objects - one object per row:

```python run
import csv

class Loan:
    def __init__(self, loan_id, product, amount, outstanding):
        self.loan_id = loan_id
        self.product = product
        self.amount = amount
        self.outstanding = outstanding


with open("data/loans.csv", encoding="utf-8") as file:
    loans = [Loan(r["loan_id"], r["product"], float(r["amount"]), float(r["outstanding"]))
             for r in csv.DictReader(file)]

print(len(loans), "objects")
print(loans[1].loan_id, loans[1].outstanding)
print(f"{sum(l.outstanding for l in loans):,.2f}")
largest = max(loans, key=lambda l: l.outstanding)
print(largest.loan_id, largest.product)
```

`l.outstanding` instead of `row[7]` or `row["outstanding"]` - and it is already a
number.

### A trap: the wrong number of arguments

The arguments of `Loan(...)` go to `__init__`: the same rules as for a function
(session 4). The error message names `__init__`:

```python run
class Loan:
    def __init__(self, loan_id, product, amount, outstanding):
        self.loan_id = loan_id
        self.product = product
        self.amount = amount
        self.outstanding = outstanding


loan = Loan("L000001", "investment", 1156900.0)
# TypeError: Loan.__init__() missing 1 required positional argument: 'outstanding'
```

### A trap: the forgotten `self`

```python run
class Loan:
    def __init__(self, loan_id, outstanding):
        loan_id = loan_id                  # a LOCAL variable - not stored in the object!
        self.outstanding = outstanding


loan = Loan("L000001", 1044231.30)
print(loan.outstanding)
print(loan.loan_id)                        # AttributeError: 'Loan' object has no attribute 'loan_id'
```

Inside a method, only `self.name = ...` stores a value in the object. A plain
`name = ...` is a local variable of the method (session 4) and is gone after the call.

::: tip Try it
Add the attribute `currency` (with the default `"EUR"`, as a default value of the
parameter) to the first `Loan` class. Create a USD loan and a EUR loan, and print the
currency of both.
:::

## 3. Methods

### A method is a function of the class

A **method** is a function written inside the class. Its first parameter is `self` -
the object it is called on:

```python run
class Loan:
    def __init__(self, loan_id, amount, outstanding, rate, days_past_due=0):
        self.loan_id = loan_id
        self.amount = amount
        self.outstanding = outstanding
        self.rate = rate
        self.days_past_due = days_past_due

    def repaid_share(self):
        """The share of the amount that is repaid."""
        return round(1 - self.outstanding / self.amount, 4)

    def yearly_interest(self):
        """The interest of one year on the outstanding amount."""
        return round(self.outstanding * self.rate / 100, 2)

    def is_late(self, limit=30):
        """True if the loan is more than `limit` days past due."""
        return self.days_past_due > limit


loan = Loan("L000002", 1977400.0, 651927.30, 5.44, days_past_due=35)
print(loan.repaid_share(), loan.yearly_interest(), loan.is_late(), loan.is_late(limit=90))
```

`loan.is_late(limit=90)` is, inside, `Loan.is_late(loan, limit=90)`: Python passes the
object as `self`. That is why the definition has one parameter more than the call:

```python run
class Loan:
    def __init__(self, loan_id, days_past_due):
        self.loan_id = loan_id
        self.days_past_due = days_past_due

    def is_late(self, limit=30):
        return self.days_past_due > limit


loan = Loan("L000002", 35)
print(loan.is_late(), Loan.is_late(loan))           # the same call, two ways
loans = [Loan("L1", 0), Loan("L2", 45), Loan("L3", 120)]
print([l.loan_id for l in loans if l.is_late()])
print([l.loan_id for l in sorted(loans, key=lambda l: l.days_past_due, reverse=True)])
```

On the portfolio: the late loans per product, with the method doing the test:

```python run
import csv
from collections import Counter

class Loan:
    def __init__(self, loan_id, product, days_past_due):
        self.loan_id = loan_id
        self.product = product
        self.days_past_due = days_past_due

    def is_late(self, limit=30):
        return self.days_past_due > limit


with open("data/loans.csv", encoding="utf-8") as file:
    loans = [Loan(r["loan_id"], r["product"], int(r["days_past_due"])) for r in csv.DictReader(file)]

print(Counter(l.product for l in loans if l.is_late()))
print(Counter(l.product for l in loans if l.is_late(limit=90)))
```

Two traps with methods. A method written **without** `self` cannot be called on an
object - Python passes the object anyway:

```python run
class Loan:
    def __init__(self, outstanding):
        self.outstanding = outstanding

    def outstanding_k():                     # self is missing
        return self.outstanding / 1000


Loan(651927.30).outstanding_k()
# TypeError: Loan.outstanding_k() takes 0 positional arguments but 1 was given
```

And a method **without the brackets** is not called - you get the method itself, and
no error:

```python run
class Loan:
    def __init__(self, amount, outstanding):
        self.amount = amount
        self.outstanding = outstanding

    def repaid_share(self):
        return round(1 - self.outstanding / self.amount, 4)


loan = Loan(1977400.0, 651927.30)
print(loan.repaid_share)                     # <bound method ...> - not a number
print(loan.repaid_share())
```

### A method that changes the object

```python run
class Loan:
    def __init__(self, loan_id, outstanding):
        self.loan_id = loan_id
        self.outstanding = outstanding
        self.payments = []                       # a new list for EACH object

    def pay(self, amount):
        """Book a payment: lower the outstanding amount, keep the payment."""
        self.outstanding = round(self.outstanding - amount, 2)
        self.payments.append(amount)


loan = Loan("L000004", 5875.11)
loan.pay(1000)
loan.pay(875.11)
print(loan.outstanding, loan.payments)
```

### A method that uses other methods

```python run
class Loan:
    def __init__(self, loan_id, outstanding, days_past_due, rating):
        self.loan_id = loan_id
        self.outstanding = outstanding
        self.days_past_due = days_past_due
        self.rating = rating

    def stage(self):
        if self.days_past_due > 90 or self.rating == 10:
            return 3
        if self.days_past_due > 30 or self.rating >= 7:
            return 2
        return 1

    def expected_loss(self, pd_value, lgd=0.45):
        """EL = PD * LGD * EAD; a stage 3 loan has PD 1."""
        if self.stage() == 3:
            pd_value = 1.0
        return round(pd_value * lgd * self.outstanding, 2)


loan = Loan("L000002", 651927.30, 35, 7)
print(loan.stage(), loan.expected_loss(0.07))
print(Loan("L999", 1000.0, 120, 5).expected_loss(0.02))
```

Inside a method, call another one with `self.stage()`.

### Change the object, or return a new one?

A method can **change** the object (`pay` above), or **return a new object** and leave
the old one as it is - safer when the old values are still needed (the scenario of a
stress test next to the base case):

```python run
import copy

class Loan:
    def __init__(self, loan_id, outstanding, rate):
        self.loan_id = loan_id
        self.outstanding = outstanding
        self.rate = rate

    def with_rate(self, new_rate):
        """A copy of the loan with another rate - the original is not changed."""
        new = copy.copy(self)
        new.rate = new_rate
        return new

    def yearly_interest(self):
        return round(self.outstanding * self.rate / 100, 2)


base = Loan("L000002", 651927.30, 5.44)
stressed = base.with_rate(base.rate + 2.0)          # +200 basis points
print(base.yearly_interest(), stressed.yearly_interest(), base.rate)
```

### The EL of homework 4, with objects

Each `Loan` knows its client's rating; the PD comes from the rating scale (session 6) -
the same 1,140,106.56:

```python run
import csv

class Loan:
    def __init__(self, loan_id, client_id, outstanding):
        self.loan_id = loan_id
        self.client_id = client_id
        self.outstanding = outstanding

    def expected_loss(self, pd_value, lgd=0.45):
        return pd_value * lgd * self.outstanding


with open("data/rating_scale.csv", encoding="utf-8") as file:
    pd_of = {int(r["rating"]): (float(r["pd_min"]) + float(r["pd_max"])) / 2 for r in csv.DictReader(file)}
with open("data/clients.csv", encoding="utf-8") as file:
    rating_of = {r["client_id"]: int(r["rating"]) for r in csv.DictReader(file)}
with open("data/loans.csv", encoding="utf-8") as file:
    loans = [Loan(r["loan_id"], r["client_id"], float(r["outstanding"])) for r in csv.DictReader(file)]

total = sum(loan.expected_loss(pd_of[rating_of[loan.client_id]]) for loan in loans)
print(f"{total:,.2f}")
```

::: tip Try it
Add a method `months_to_maturity(report_date)` to a `Loan` with a `maturity_date`
attribute (a `date`). Use the `months_between` idea of session 10:
`(m.year - r.year) * 12 + (m.month - r.month)`.
:::

## 4. `__str__` and `__repr__`

Print an object of your class, and you get its type and its memory address - not
useful:

```python run
class Loan:
    def __init__(self, loan_id, outstanding):
        self.loan_id = loan_id
        self.outstanding = outstanding

loan = Loan("L000002", 651927.30)
print(loan)
print([loan])
```

Two special methods give an object a text form:

- `__repr__` - for **developers**: unambiguous, ideally like the code that creates
  the object. Used in lists, in the REPL, in the debugger, with `!r`.
- `__str__` - for **people**: a report line. Used by `print` and f-strings. Without
  it, Python uses `__repr__`.

```python run
class Loan:
    def __init__(self, loan_id, outstanding):
        self.loan_id = loan_id
        self.outstanding = outstanding

    def __repr__(self):
        return f"Loan({self.loan_id!r}, {self.outstanding!r})"

    def __str__(self):
        return f"{self.loan_id}: EUR {self.outstanding:,.2f}"


loan = Loan("L000002", 651927.30)
print(loan)                     # __str__
print(repr(loan))               # __repr__
print([loan, Loan("L000003", 644.25)])     # a list shows __repr__ of the items
print(f"{loan} | {loan!r}")
```

Always write at least `__repr__` - the first time you debug a list of objects, you
will be glad. With `__str__`, a report loop needs no formatting code of its own:

```python run
class Client:
    def __init__(self, client_id, segment, rating):
        self.client_id = client_id
        self.segment = segment
        self.rating = rating

    def __repr__(self):
        return f"Client({self.client_id!r}, {self.segment!r}, {self.rating})"

    def __str__(self):
        return f"{self.client_id} ({self.segment}, rating {self.rating})"


clients = [Client("C0002", "sme", 5), Client("C0030", "corporate", 4)]
for c in clients:
    print(c)
print(clients)
```

With `__str__`, the largest loans of the file are a report in two lines:

```python run
import csv

class Loan:
    def __init__(self, loan_id, product, outstanding):
        self.loan_id = loan_id
        self.product = product
        self.outstanding = outstanding

    def __repr__(self):
        return f"Loan({self.loan_id!r}, {self.product!r}, {self.outstanding!r})"

    def __str__(self):
        return f"{self.loan_id} {self.product:<16} EUR {self.outstanding:>15,.2f}"


with open("data/loans.csv", encoding="utf-8") as file:
    loans = [Loan(r["loan_id"], r["product"], float(r["outstanding"])) for r in csv.DictReader(file)]

for loan in sorted(loans, key=lambda l: l.outstanding, reverse=True)[:3]:
    print(loan)
print(loans[:2])
```

`__str__` and `__repr__` must **return** a string - not print it, and not return a
number:

```python run
class Loan:
    def __init__(self, outstanding):
        self.outstanding = outstanding

    def __str__(self):
        return self.outstanding              # a float, not a str


print(Loan(644.25))
# TypeError: __str__ returned non-string (type float)
```

::: tip Try it
Write `__str__` for a `Client` with `client_id`, `segment` and `rating` so that
`print(client)` shows `C0002 (sme, rating 5)`.
:::

## 5. Class attributes

### Shared by all objects

An attribute assigned **in the class body** (not on `self`) belongs to the **class**,
and all objects share it - a constant of the class:

```python run
class Loan:
    LGD = 0.45                                # a class attribute: one value for all loans

    def __init__(self, loan_id, outstanding):
        self.loan_id = loan_id                # object attributes: one value per loan
        self.outstanding = outstanding

    def expected_loss(self, pd_value):
        return round(pd_value * self.LGD * self.outstanding, 2)


a = Loan("L1", 100000.0)
b = Loan("L2", 250000.0)
print(a.LGD, b.LGD, Loan.LGD)
print(a.expected_loss(0.02), b.expected_loss(0.02))

Loan.LGD = 0.40                               # change it for ALL loans
print(a.expected_loss(0.02), b.expected_loss(0.02))
```

`self.LGD` finds the class attribute, because the object has no own `LGD`: Python
looks in the object first, then in its class.

On the whole portfolio - the expected loss with a stage-based PD, then a stress
scenario with a higher LGD for **all** loans, changed in one place:

```python run
import csv

class Loan:
    LGD = 0.45
    PD_OF_STAGE = {1: 0.01, 2: 0.10, 3: 1.0}

    def __init__(self, loan_id, outstanding, stage):
        self.loan_id = loan_id
        self.outstanding = outstanding
        self.stage = stage

    def expected_loss(self):
        return self.PD_OF_STAGE[self.stage] * self.LGD * self.outstanding


with open("data/loans.csv", encoding="utf-8") as file:
    loans = [Loan(r["loan_id"], float(r["outstanding"]), int(r["stage"])) for r in csv.DictReader(file)]

print(f"base   LGD {Loan.LGD:.2f}: {sum(l.expected_loss() for l in loans):>14,.2f}")
Loan.LGD = 0.60
print(f"stress LGD {Loan.LGD:.2f}: {sum(l.expected_loss() for l in loans):>14,.2f}")
```

A class attribute is a good place for the **nomenclature** a method needs - one copy
for all objects:

```python run
class Loan:
    STAGE_NAMES = {1: "performing", 2: "under-performing", 3: "non-performing"}

    def __init__(self, loan_id, stage):
        self.loan_id = loan_id
        self.stage = stage

    def stage_name(self):
        return self.STAGE_NAMES.get(self.stage, "unknown")


print([Loan("L1", s).stage_name() for s in (1, 3, 5)])
```

### An assignment on the object hides it

```python run
class Loan:
    LGD = 0.45

    def __init__(self, loan_id):
        self.loan_id = loan_id


a = Loan("L1")
b = Loan("L2")
a.LGD = 0.75                 # a NEW attribute on a only (a secured loan, say)
print(a.LGD, b.LGD, Loan.LGD)
print(vars(a), vars(b))
```

### A counter of objects

```python run
class Loan:
    created = 0

    def __init__(self, loan_id):
        self.loan_id = loan_id
        Loan.created += 1                  # the class attribute, not self.created


for i in range(1, 4):
    Loan(f"L{i:06d}")
print(Loan.created, "loans created")
```

::: warning A list as a class attribute is shared
A **mutable** class attribute - a list, a dict - is **one** object for all instances.
Appending through one object changes it for all (the same trap as the list default of
session 4):

```python run
class Loan:
    payments = []                          # one list for ALL loans!

    def __init__(self, loan_id):
        self.loan_id = loan_id

    def pay(self, amount):
        self.payments.append(amount)


a = Loan("L1")
b = Loan("L2")
a.pay(100)
print(b.payments)                          # [100] - b "has" a's payment
```

Create lists and dicts **in `__init__`**: `self.payments = []` (section 3).
:::

::: tip Try it
Give `Loan` a class attribute `REPORT_DATE = date(2026, 9, 30)` and a method
`age_days(start_date)` that uses it. Then change `Loan.REPORT_DATE` and call the
method again.
:::

## 6. Validation and `property`

### Check the data when the object is created

An object that holds wrong data is worse than no object: every report made from it
is wrong. Check in `__init__`, and raise a clear error (session 9):

```python run
class Loan:
    def __init__(self, loan_id, amount, outstanding):
        if not (len(loan_id) == 7 and loan_id[0] == "L" and loan_id[1:].isdigit()):
            raise ValueError(f"bad loan id {loan_id!r}")
        if amount <= 0:
            raise ValueError(f"{loan_id}: amount must be positive, got {amount}")
        if not 0 <= outstanding <= amount:
            raise ValueError(f"{loan_id}: outstanding {outstanding} is not between 0 and {amount}")
        self.loan_id = loan_id
        self.amount = amount
        self.outstanding = outstanding


print(vars(Loan("L000001", 1156900.0, 1044231.30)))
for args in [("X1", 100.0, 50.0), ("L000002", 100.0, 150.0)]:
    try:
        Loan(*args)
    except ValueError as error:
        print("rejected:", error)
```

This is the "validation rules" part of the client's nomenclature idea: the rules sit
in the class, and **every** object that exists has passed them.

With a file, the loader of session 9 decides what to do with a row that fails: one
`try` per row, and a list of the rejected rows:

```python run
import csv

class Loan:
    def __init__(self, loan_id, amount, outstanding):
        if outstanding > amount:
            raise ValueError(f"{loan_id}: outstanding > amount")
        self.loan_id = loan_id
        self.amount = amount
        self.outstanding = outstanding


rows = [{"loan_id": "L000001", "amount": "1156900", "outstanding": "1044231.30"},
        {"loan_id": "L000002", "amount": "100", "outstanding": "150"},
        {"loan_id": "L000003", "amount": "800", "outstanding": "n/a"}]

loans, rejected = [], []
for row in rows:
    try:
        loans.append(Loan(row["loan_id"], float(row["amount"]), float(row["outstanding"])))
    except ValueError as error:
        rejected.append((row["loan_id"], str(error)))
print(len(loans), "loans;", rejected)
```

### `property`: a computed attribute

First, the problem. A value computed **once** in `__init__` is a copy - it does not
follow a later change of the attributes it came from:

```python run
class Loan:
    def __init__(self, loan_id, amount, outstanding):
        self.loan_id = loan_id
        self.amount = amount
        self.outstanding = outstanding
        self.repaid = amount - outstanding        # computed once, now


loan = Loan("L000004", 15900.0, 5875.11)
loan.outstanding = 0.0                            # the loan is paid off
print(loan.repaid)                                # still 10024.89 - out of date
```

`@property` above a method makes it look like an **attribute** - no brackets. Use it
for values computed from the other attributes:

```python run
class Loan:
    def __init__(self, loan_id, outstanding, days_past_due):
        self.loan_id = loan_id
        self.outstanding = outstanding
        self.days_past_due = days_past_due

    @property
    def dpd_bucket(self):
        d = self.days_past_due
        return "current" if d == 0 else "1-30" if d <= 30 else "31-90" if d <= 90 else "90+"

    @property
    def is_defaulted(self):
        return self.days_past_due > 90


loan = Loan("L000002", 651927.30, 35)
print(loan.dpd_bucket, loan.is_defaulted)       # no brackets
loan.days_past_due = 120
print(loan.dpd_bucket, loan.is_defaulted)       # always up to date
```

On the file - how many loans are defaulted, and their outstanding, from the property:

```python run
import csv

class Loan:
    def __init__(self, loan_id, outstanding, days_past_due):
        self.loan_id = loan_id
        self.outstanding = outstanding
        self.days_past_due = days_past_due

    @property
    def is_defaulted(self):
        return self.days_past_due > 90


with open("data/loans.csv", encoding="utf-8") as file:
    loans = [Loan(r["loan_id"], float(r["outstanding"]), int(r["days_past_due"])) for r in csv.DictReader(file)]

defaulted = [l for l in loans if l.is_defaulted]
print(len(defaulted), "defaulted loans,", f"{sum(l.outstanding for l in defaulted):,.2f} EUR")
```

`@property` is a **decorator** (lecture 4, Advanced): it turns the method into a
read-only attribute. A computed value never gets out of date, because it is computed
each time it is read - like a computed column of an SQL view.

```python run
class Loan:
    def __init__(self, outstanding):
        self.outstanding = outstanding

    @property
    def outstanding_k(self):
        return round(self.outstanding / 1000, 1)


loan = Loan(651927.30)
print(loan.outstanding_k)
loan.outstanding_k = 5                          # AttributeError: a property without a setter is read-only
```

`hasattr` and `getattr` ask an object for an attribute by its **name** - handy for
reports that take the list of columns from a setting:

```python run
class Loan:
    def __init__(self, loan_id, outstanding, days_past_due):
        self.loan_id = loan_id
        self.outstanding = outstanding
        self.days_past_due = days_past_due

    @property
    def is_defaulted(self):
        return self.days_past_due > 90


loan = Loan("L000002", 651927.30, 35)
columns = ["loan_id", "outstanding", "is_defaulted", "rating"]
print({c: getattr(loan, c, None) for c in columns})
print(hasattr(loan, "rating"))
```

### A setter that validates

A property can also have a **setter**: code that runs when the attribute is assigned.
The value itself is kept in an attribute with a leading underscore - by convention,
"internal, do not use from outside":

```python run
class Loan:
    def __init__(self, loan_id, outstanding):
        self.loan_id = loan_id
        self.outstanding = outstanding          # this already calls the setter below

    @property
    def outstanding(self):
        return self._outstanding

    @outstanding.setter
    def outstanding(self, value):
        if value < 0:
            raise ValueError(f"{self.loan_id}: outstanding cannot be negative ({value})")
        self._outstanding = round(value, 2)


loan = Loan("L000004", 5875.111)
print(loan.outstanding)
loan.outstanding = 5000
print(loan.outstanding)
loan.outstanding = -10                          # ValueError
```

Now the rule holds not only at creation, but after **every** change.

::: tip Try it
Add a read-only property `stage` to the `Loan` with `days_past_due` (and a `rating`
attribute). Then add a setter for `days_past_due` that refuses negative values.
:::

## 7. Dataclasses

### A class in a few lines

Most classes for data start with an `__init__` that only copies the parameters into
attributes, and a `__repr__`. The module `dataclasses` writes them for you, from the
**fields** with their type hints (session 4):

```python run
from dataclasses import dataclass

@dataclass
class Loan:
    loan_id: str
    product: str
    outstanding: float
    rate: float = 0.0                      # a default value
    currency: str = "EUR"

    def yearly_interest(self):
        return round(self.outstanding * self.rate / 100, 2)


loan = Loan("L000002", "investment", 651927.30, 5.44)
print(loan)                                # a ready __repr__
print(loan.yearly_interest())
print(loan == Loan("L000002", "investment", 651927.30, 5.44))     # a ready __eq__: by value
```

`@dataclass` writes `__init__`, `__repr__` and `__eq__` (equal when all fields are
equal). Methods and properties are written as in a normal class.

::: warning Type hints are not checked
`Loan("L1", "x", "a lot")` works: a dataclass does not check the types (like all type
hints, session 4). Check what matters in `__post_init__` (below).
:::

A row of `csv.DictReader` can go straight into a dataclass with `**` (session 4) - if
the column names are the field names. Convert the types in `__post_init__` (below), or
before:

```python run
import csv
from dataclasses import dataclass

@dataclass
class RatingGrade:
    rating: str
    grade: str
    pd_min: str
    pd_max: str
    description: str


with open("data/rating_scale.csv", encoding="utf-8") as file:
    scale = [RatingGrade(**row) for row in csv.DictReader(file)]
print(scale[0])
print(type(scale[0].pd_min))            # still text - a dataclass does not convert
```

### Lists as fields: `field(default_factory=list)`

A default list would be shared (section 5) - so a dataclass refuses `= []`. Use
`field(default_factory=list)`: a new list for each object:

```python run
from dataclasses import dataclass, field

@dataclass
class Client:
    client_id: str
    segment: str
    loan_ids: list = field(default_factory=list)


a = Client("C0001", "retail")
b = Client("C0002", "sme")
a.loan_ids.append("L000123")
print(a, b, sep="\n")
```

### Validation: `__post_init__`

`__post_init__` runs right after the written `__init__` - the place for checks and
for computed fields:

```python run
from dataclasses import dataclass

@dataclass
class Loan:
    loan_id: str
    amount: float
    outstanding: float

    def __post_init__(self):
        if self.outstanding > self.amount:
            raise ValueError(f"{self.loan_id}: outstanding {self.outstanding} > amount {self.amount}")
        self.outstanding = round(self.outstanding, 2)


print(Loan("L000001", 1156900.0, 1044231.301))
try:
    Loan("L000009", 100.0, 150.0)
except ValueError as error:
    print("rejected:", error)
```

### Records that cannot change: `frozen=True`

A **frozen** dataclass cannot be changed after it is created - like a tuple (session
3), but with names. Good for reference data: a grade of the rating scale must not be
changed by a report by mistake:

```python run
from dataclasses import dataclass

@dataclass(frozen=True)
class RatingGrade:
    rating: int
    grade: str
    pd_min: float
    pd_max: float

    @property
    def pd_mid(self):
        return (self.pd_min + self.pd_max) / 2


bbb = RatingGrade(4, "BBB", 0.0025, 0.006)
print(bbb, bbb.pd_mid)
bbb.pd_max = 0.5                           # FrozenInstanceError
```

A frozen dataclass is also **hashable**: it can be a key of a dictionary or an item of
a set (session 6). To "change" it, make a new one with `dataclasses.replace`:

```python run
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class RatingGrade:
    rating: int
    grade: str
    pd_min: float
    pd_max: float


bbb = RatingGrade(4, "BBB", 0.0025, 0.006)
recalibrated = replace(bbb, pd_max=0.0065)       # a new object; bbb is unchanged
print(bbb.pd_max, recalibrated.pd_max)
print({bbb: "moderate risk"}[bbb])                # usable as a dictionary key
```

### Sorting: `order=True`

`order=True` adds `<`, `>` and friends - the fields are compared in order, like
tuples:

```python run
from dataclasses import dataclass

@dataclass(order=True, frozen=True)
class RatingGrade:
    rating: int
    grade: str

grades = [RatingGrade(7, "CCC"), RatingGrade(1, "AAA"), RatingGrade(4, "BBB")]
print(sorted(grades))
print(max(grades).grade)
```

### Rows of a file as dataclasses

```python run
import csv
from dataclasses import dataclass

@dataclass(frozen=True)
class RatingGrade:
    rating: int
    grade: str
    pd_min: float
    pd_max: float
    description: str

    @property
    def pd_mid(self):
        return (self.pd_min + self.pd_max) / 2


with open("data/rating_scale.csv", encoding="utf-8") as file:
    scale = [RatingGrade(int(r["rating"]), r["grade"], float(r["pd_min"]), float(r["pd_max"]), r["description"])
             for r in csv.DictReader(file)]

for g in scale[:4]:
    print(f"{g.rating:>2} {g.grade:<4} {g.pd_mid:.5f}  {g.description}")
by_grade = {g.grade: g for g in scale}
print(by_grade["CCC"].pd_max)
```

Back to rows: `asdict` and `astuple` turn a dataclass into a dictionary or a tuple -
ready for `csv.DictWriter` (session 9) or JSON. `fields` lists the fields:

```python run
import csv
import io
from dataclasses import asdict, astuple, dataclass, fields

@dataclass
class Loan:
    loan_id: str
    product: str
    outstanding: float


loans = [Loan("L000001", "investment", 1044231.30), Loan("L000003", "credit_card", 644.25)]
print(asdict(loans[0]), astuple(loans[0]))
print([f.name for f in fields(Loan)])

buffer = io.StringIO()
writer = csv.DictWriter(buffer, fieldnames=[f.name for f in fields(Loan)])
writer.writeheader()
writer.writerows(asdict(l) for l in loans)
print(buffer.getvalue())
```

A field can be left out of the `repr` or of the comparison - for example a long list,
or a note:

```python run
from dataclasses import dataclass, field

@dataclass
class Client:
    client_id: str
    rating: int
    note: str = field(default="", compare=False)
    loan_ids: list = field(default_factory=list, repr=False)


a = Client("C0002", 5, note="called on Monday", loan_ids=["L1", "L2"])
print(a)
print(a == Client("C0002", 5, loan_ids=["L1", "L2"]))     # True: the note is not compared
```

| | `dict` | `namedtuple` | `@dataclass` | a normal class |
|---|---|---|---|---|
| names for the fields | keys | yes | yes | yes |
| can change | yes | no | yes (or `frozen`) | yes |
| methods and properties | no | a few | yes | yes |
| validation | no | no | `__post_init__` | `__init__`, setters |
| best for | rows, lookups, JSON | light records | **records with rules** | complex behaviour |

::: tip Try it
Make a frozen dataclass `Product` with `code`, `name` and `group` (`"retail"` or
`"business"`), and a dictionary `code -> Product` for four products. Try to change the
name of one.
:::

## 8. Objects together: a client and its loans

A client has many loans - one-to-many. In objects: a `Client` has a **list** of `Loan`
objects, and methods that work on all of them:

```python run
from dataclasses import dataclass, field

@dataclass
class Loan:
    loan_id: str
    outstanding: float
    days_past_due: int = 0


@dataclass
class Client:
    client_id: str
    segment: str
    loans: list = field(default_factory=list)

    def add_loan(self, loan):
        self.loans.append(loan)

    @property
    def exposure(self):
        return round(sum(l.outstanding for l in self.loans), 2)

    @property
    def max_days_past_due(self):
        return max((l.days_past_due for l in self.loans), default=0)


client = Client("C0030", "corporate")
client.add_loan(Loan("L000070", 8999760.03))
client.add_loan(Loan("L000241", 4263650.04, 15))
print(client.exposure, client.max_days_past_due, len(client.loans))
```

All clients and loans from the two files - a dictionary of clients by id (session 6),
then each loan is added to its client:

```python run
import csv
from dataclasses import dataclass, field

@dataclass
class Loan:
    loan_id: str
    outstanding: float
    stage: int


@dataclass
class Client:
    client_id: str
    segment: str
    rating: int
    loans: list = field(default_factory=list)

    @property
    def exposure(self):
        return sum(l.outstanding for l in self.loans)

    @property
    def worst_stage(self):
        return max((l.stage for l in self.loans), default=0)


with open("data/clients.csv", encoding="utf-8") as file:
    clients = {r["client_id"]: Client(r["client_id"], r["segment"], int(r["rating"])) for r in csv.DictReader(file)}
with open("data/loans.csv", encoding="utf-8") as file:
    for r in csv.DictReader(file):
        clients[r["client_id"]].loans.append(Loan(r["loan_id"], float(r["outstanding"]), int(r["stage"])))

top = sorted(clients.values(), key=lambda c: c.exposure, reverse=True)[:5]
for c in top:
    print(f"{c.client_id} {c.segment:<10} {len(c.loans):>2} loans {c.exposure:>16,.2f}  worst stage {c.worst_stage}")
print(sum(1 for c in clients.values() if not c.loans), "clients without loans")
```

From the objects, the usual reports - exposure per segment, and the share of the
largest client in each segment:

```python run
import csv
from collections import defaultdict
from dataclasses import dataclass, field

@dataclass
class Client:
    client_id: str
    segment: str
    balances: list = field(default_factory=list)

    @property
    def exposure(self):
        return sum(self.balances)


with open("data/clients.csv", encoding="utf-8") as file:
    clients = {r["client_id"]: Client(r["client_id"], r["segment"]) for r in csv.DictReader(file)}
with open("data/loans.csv", encoding="utf-8") as file:
    for r in csv.DictReader(file):
        clients[r["client_id"]].balances.append(float(r["outstanding"]))

by_segment = defaultdict(list)
for c in clients.values():
    by_segment[c.segment].append(c)

for segment, members in sorted(by_segment.items()):
    total = sum(c.exposure for c in members)
    largest = max(members, key=lambda c: c.exposure)
    print(f"{segment:<10}{total:>18,.2f}  largest {largest.client_id} {largest.exposure / total:6.1%}")
```

The link can go both ways: each loan keeps its **client object**, so `loan.client.rating`
reads the rating through the link - like a join that is done once. The EL of
homework 4 again, 1,140,106.56:

```python run
import csv
from dataclasses import dataclass

@dataclass
class Client:
    client_id: str
    rating: int


@dataclass
class Loan:
    loan_id: str
    client: Client                       # the object, not only the id
    outstanding: float

    def expected_loss(self, pd_of, lgd=0.45):
        return pd_of[self.client.rating] * lgd * self.outstanding


with open("data/rating_scale.csv", encoding="utf-8") as file:
    pd_of = {int(r["rating"]): (float(r["pd_min"]) + float(r["pd_max"])) / 2 for r in csv.DictReader(file)}
with open("data/clients.csv", encoding="utf-8") as file:
    clients = {r["client_id"]: Client(r["client_id"], int(r["rating"])) for r in csv.DictReader(file)}
with open("data/loans.csv", encoding="utf-8") as file:
    loans = [Loan(r["loan_id"], clients[r["client_id"]], float(r["outstanding"])) for r in csv.DictReader(file)]

print(loans[0].client, loans[0].client.rating)
print(f"{sum(l.expected_loss(pd_of) for l in loans):,.2f}")
```

The trap: a loan whose client is not in the clients file. `clients[r["client_id"]]`
stops the whole load with a `KeyError`; `get` and a list of rejects (session 9) keep
going and report it:

```python run
from dataclasses import dataclass, field

@dataclass
class Client:
    client_id: str
    loans: list = field(default_factory=list)


clients = {"C0001": Client("C0001"), "C0002": Client("C0002")}
rows = [("L000001", "C0001"), ("L000002", "C9999"), ("L000003", "C0002")]

rejected = []
for loan_id, client_id in rows:
    client = clients.get(client_id)
    if client is None:
        rejected.append((loan_id, f"unknown client {client_id}"))
        continue
    client.loans.append(loan_id)

print({c.client_id: c.loans for c in clients.values()})
print(rejected)
```

This is the shape of the final project: objects that hold the data and know their
rules. In session 12 the rules themselves - the nomenclatures - become objects.

::: info The same in pandas
In pandas you do not create one object per row: the DataFrame is **one** object for
the whole table, and its methods work on all rows (session 14). Classes are for the
**rules** around the data - nomenclatures, checks, report settings - not for millions
of rows.
:::

::: tip Try it
Add a property `share_late` to `Client`: the share of its outstanding that is in loans
of stage 2 or 3. Print it for the five largest clients.
:::

## 9. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 11-oop-classes/practice/task1-first-class.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-first-class.py` | A `RatingGrade` class: attributes, a method, `__repr__` |
| 2 | `task2-predict-objects.py` | Predict: attributes, class and object attributes, two names for one object |
| 3 | `task3-loan-methods.py` | `Loan` with methods: repaid share, interest, is late, EL, pay |
| 4 | `task4-validation-property.py` | Checks in `__init__`, properties, a setter that validates |
| 5 | `task5-dataclasses.py` | The same with `@dataclass`: defaults, `frozen`, `order`, `__post_init__` |
| 6 | `task6-client-loans.py` (Optional) | `Client` with its loans, built from the two files |

## Summary

| Topic | Remember |
|-------|----------|
| Objects | every value is an object of a class; a class is a blueprint, an object one thing made from it |
| Class | `class Loan:` (CamelCase); `__init__(self, ...)` runs at creation |
| Attributes | `self.x = x` stores per object; read with `obj.x`; `vars(obj)` |
| Methods | functions in the class, first parameter `self`; call `obj.method()`; inside: `self.other()` |
| Text form | `__repr__` for developers (like code), `__str__` for people; write `__repr__` always |
| Class attributes | in the class body, shared by all objects; never a list or a dict there |
| Validation | check in `__init__` (or `__post_init__`) and raise `ValueError` |
| `property` | `@property` - a computed, read-only attribute; `@x.setter` checks every assignment |
| Dataclass | `@dataclass` + fields with types; `field(default_factory=list)`; `frozen=True`; `order=True` |
| Together | a `Client` with a list of `Loan` objects; build from files with a dict by id |

## Homework

1. `11-oop-classes/homework.py` (in the homework repository): **the portfolio as
   objects** - `Loan` and `Client` dataclasses with validation, built from
   `loans.csv`, `clients.csv` and `rating_scale.csv`; the EL of each loan with a method
   (the total must be 1,140,106.56 again), the exposure and the EL per client and per
   segment, and the 10 largest clients. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Show your Git history of homework 10 at the start of the next session.

## Self-study

This part is not covered in class. It is for reading at home: objects that work with
`sorted`, `len`, `in` and `for`, and named codes with `enum`.

### Special methods: objects that work with Python's operators

The methods with two underscores on each side - `__init__`, `__repr__`, `__str__` -
are **special methods**: Python calls them for you. There are many more. With them, a
class works with the built-in functions and operators:

| You write | Python calls |
|---|---|
| `a == b` | `a.__eq__(b)` |
| `a < b`, `sorted(...)` | `a.__lt__(b)` |
| `len(x)` | `x.__len__()` |
| `item in x` | `x.__contains__(item)` |
| `for item in x` | `x.__iter__()` |

A portfolio that behaves like a container of loans:

```python run
from dataclasses import dataclass

@dataclass
class Loan:
    loan_id: str
    outstanding: float


class Portfolio:
    def __init__(self, loans):
        self._loans = {l.loan_id: l for l in loans}

    def __len__(self):
        return len(self._loans)

    def __contains__(self, loan_id):
        return loan_id in self._loans

    def __iter__(self):
        return iter(self._loans.values())

    def __repr__(self):
        return f"Portfolio({len(self)} loans)"


p = Portfolio([Loan("L1", 100.0), Loan("L2", 250.0), Loan("L3", 50.0)])
print(p, len(p), "L2" in p, "L9" in p)
print(sum(l.outstanding for l in p))
print([l.loan_id for l in sorted(p, key=lambda l: l.outstanding)])
```

To compare objects of a normal class, write `__eq__` and `__lt__`;
`functools.total_ordering` writes `<=`, `>`, `>=` from those two:

```python run
from functools import total_ordering

@total_ordering
class Grade:
    ORDER = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]

    def __init__(self, code):
        self.code = code

    def __eq__(self, other):
        return self.code == other.code

    def __lt__(self, other):                       # "better than": earlier in ORDER
        return self.ORDER.index(self.code) < self.ORDER.index(other.code)

    def __repr__(self):
        return f"Grade({self.code!r})"


print(sorted([Grade("B"), Grade("AA"), Grade("CCC")]))
print(Grade("BBB") >= Grade("BB"), Grade("A") == Grade("A"))
```

**Exercises**

1. Add `__getitem__(self, loan_id)` to `Portfolio`, so that `p["L2"]` gives the loan.
2. Give `Portfolio` a `__add__` that returns a new portfolio with the loans of both.

::: details Answer
```python
    def __getitem__(self, loan_id):
        return self._loans[loan_id]          # a KeyError for an unknown id, like a dict

    def __add__(self, other):
        return Portfolio(list(self) + list(other))
```
:::

### `enum`: named codes

Codes like the stage (1, 2, 3) or the segment (`"retail"`, ...) appear all over the
code as bare numbers and strings - a typo (`"retial"`) is not an error, just a wrong
result. An **enumeration** gives each code a name, and only the defined values exist:

```python run
from enum import Enum, IntEnum

class Stage(IntEnum):
    PERFORMING = 1
    UNDERPERFORMING = 2
    NON_PERFORMING = 3

class Segment(Enum):
    RETAIL = "retail"
    SME = "sme"
    CORPORATE = "corporate"


print(Stage(3), Stage(3).name, Stage.NON_PERFORMING.value)
print(Stage(2) > Stage.PERFORMING)                  # IntEnum compares like int
print(Segment("sme"), [s.value for s in Segment])
print(Segment("retial"))                            # ValueError: 'retial' is not a valid Segment
```

The data still has `"sme"` and `3`; convert when you read it (`Segment(row["segment"])`)
and the rest of the code uses the names. In SAS terms: a format with a fixed list of
values, that refuses everything else.

**Exercises**

1. Make an `IntEnum` `Bucket` for the DPD buckets (`CURRENT = 0`, `UP_TO_30 = 1`,
   `UP_TO_90 = 2`, `OVER_90 = 3`) and a function that returns the bucket of a number of
   days.
2. Count the loans of `loans.csv` per `Stage` member with a `Counter`.

::: details Answer
```python
from collections import Counter
from enum import IntEnum
import csv

class Bucket(IntEnum):
    CURRENT = 0
    UP_TO_30 = 1
    UP_TO_90 = 2
    OVER_90 = 3

def bucket_of(days):
    return Bucket.CURRENT if days == 0 else Bucket.UP_TO_30 if days <= 30 else \
           Bucket.UP_TO_90 if days <= 90 else Bucket.OVER_90

with open("data/loans.csv", encoding="utf-8") as file:
    print(Counter(Stage(int(r["stage"])) for r in csv.DictReader(file)))
```
:::

## Read more

- Python tutorial: [Classes](https://docs.python.org/3/tutorial/classes.html) (sections
  9.1 - 9.4 for today)
- Reference: [`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
  [`property`](https://docs.python.org/3/library/functions.html#property),
  [`enum` HOWTO](https://docs.python.org/3/howto/enum.html)
- Real Python: [Object-oriented programming in Python](https://realpython.com/python3-object-oriented-programming/),
  [Data classes in Python](https://realpython.com/python-data-classes/)

**Next session:** OOP in practice - a nomenclature as a class: its codes, its metadata,
its validation rules and its methods, applied in the same way to different datasets.
