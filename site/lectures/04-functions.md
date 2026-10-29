---
title: 4. Functions
---

# 4. Functions

<div class="lecture-meta">
  <span>Session 4</span><span>practice: <code>04-functions/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- define your own functions with `def`, and call them;
- pass values to a function: by position, by name, with default values, and in any
  number with `*args` and `**kwargs`;
- return one or several results with `return` - and see why `print` is not `return`;
- understand where a name is visible (scope), and why a function should get its
  data through parameters;
- document a function with a docstring and type hints;
- pass functions as values, write short ones with `lambda`, and sort by a key;
- replace a SAS macro with a Python function, and build a small library of
  functions for the loan portfolio.

From SAS to Python - the same reusable piece of logic, two ways:

```sas
%macro interest(outstanding, rate);
    (&outstanding * &rate / 100)
%mend;

data _null_;
    yearly = %interest(651927.30, 5.44);
    put yearly=;
run;
```

```python run
def interest(outstanding, rate):
    """The interest for one year: outstanding * rate / 100."""
    return outstanding * rate / 100


print(interest(651927.30, 5.44))
print(interest(1044231.30, 8.83))
```

## 1. What is a function?

A **function** is a **named block of code** that does one task. You define it once,
and **call** it - run it - as many times as you need, with different values. A good
picture is a recipe in a cookbook: written once, cooked many times, with different
amounts.

You already call functions every day: `print()`, `len()`, `round()`, `sum()`,
`sorted()`, `int()`. Today you write your own.

Functions help to:

- **split a big task into small ones** - each function does one thing and has a
  name that says what;
- **not repeat yourself** - the same calculation in one place: a fix there fixes it
  everywhere (the "DRY" rule: *don't repeat yourself*);
- **test** - a function with inputs and a result is easy to check (that is how the
  tasks of this course check your work).

A program made of functions looks like this:

```python
### the functions
def read_data():
    pass

def clean_data():
    pass

def make_report():
    pass

### the main program
read_data()
clean_data()
make_report()
```

### Functions and SAS macros

| | SAS macro | SAS `PROC FCMP` function | Python function |
|---|---|---|---|
| Defined with | `%macro name(...); ... %mend;` | `function name(...); ... endsub;` | `def name(...):` |
| What it does | **writes SAS code** (text) that SAS then runs | calculates a value | runs code, **returns a value** |
| Parameters | text: `&param` | values | any objects: numbers, lists, tables, other functions |
| Variables inside | `%local` / `%global` | local | local by default (section 6) |
| Used for | repeating steps, generating code | calculations in a DATA step | everything |

A macro is a text generator: `%interest(651927.30, 5.44)` is replaced by the text
`(651927.30 * 5.44 / 100)`. A Python function is not text - it runs, and gives back
a value. You do not need `&`, `%str()` or quoting rules: a parameter is just a
name for the value.

SQL has user-defined functions too (`CREATE FUNCTION`), but in analysis work they are
rare. In Python, functions are everywhere.

## 2. Defining a function

### Syntax

```text
def function_name(parameters):
    """docstring"""
    block
    return expression
```

- `def` - the keyword that starts the definition.
- `function_name` - a valid name (session 1): `snake_case`, a verb that says what
  the function does - `calculate_interest`, `read_loans`, `is_late`.
- `parameters` - optional: the names that will get the input values. The **brackets
  are required**, even when there are no parameters.
- `"""docstring"""` - optional: a text that documents the function (section 8).
- `block` - the **body** of the function, indented. At least one statement.
- `return expression` - optional: the result of the function (section 5).

The simplest definition:

```python run
def calculate_sum():
    pass
```

`pass` (session 2) is a body that does nothing - for a function you will write
later. A full definition:

```python run
def calculate_sum(number1, number2):
    """Take two numbers and return their sum.

    Parameters:
        number1 (int / float): the first number
        number2 (int / float): the second number

    Returns:
        int / float: the sum of number1 and number2
    """
    total_sum = number1 + number2
    return total_sum

print(calculate_sum(2, 3))
```

### A definition does not run the body

```python run
def greet():
    """Just print hello."""
    print("Hello!")
```

Nothing is printed: `def` only **creates** the function and gives it a name. The body
runs when the function is **called**.

## 3. Calling a function

```text
function_name(arguments)
```

The brackets are required - even when there are no arguments:

```python run
def greet():
    """Just print hello."""
    print("Hello!")

greet()          # the call: now the body runs
greet()          # and again
print(greet)     # without brackets: the function object itself, not a call
```

A function must be **defined before** it is called. Python runs a file from top to
bottom; at the call, the name must already exist:

```python run
greet()

def greet():
    print("Hello!")
```

That is why a script puts its functions at the top and the main code at the bottom
(section 12). (Inside a function body, you can call a function that is defined lower
in the file - the body runs only later, when all `def`s are done.)

## 4. Parameters and arguments

### Why parameters

A function that always works with the same values is not very useful:

```python run
def add():
    print(2 + 3)

add()
add()
```

It is better to give it the values at each call - `add(20, 22)`, `add(123, 321)`.
That is what **parameters** are for:

- A **parameter** is a name in the definition: `def add(x, y):`. Inside the function
  it is a local variable.
- An **argument** is the value given in the call: `add(20, 22)`. At the call, each
  parameter is bound to its argument.

```python run
def add(x, y):
    print(x + y)

add(20, 22)
add(123, 321)
add(16, 10)
```

::: info Animation
**Function calls step by step:** [1. A call and a return](../animations/functionCalls.html#1){target="_blank"}
:::

### Positional arguments

By default, arguments are given **by position**: the first argument to the first
parameter, the second to the second, and so on. The number must match, or it is a
`TypeError`:

```python run
def sub(x, y):
    """Subtract y from x and print the result."""
    print(x - y)

sub(99, 3)
sub(3, 99)        # the order matters
sub(99)           # TypeError: missing 1 required positional argument: 'y'
```

### Default values

A parameter can have a **default value**, used when the call gives no argument for it:

```python run
def greet(name="Nobody"):
    """Greet a user."""
    print("Hello", name)

greet("Maria")
greet()
```

On the portfolio - the most common term as a default:

```python run
def annuity_payment(amount, yearly_rate, years=5):
    """The monthly payment of an annuity loan."""
    r = yearly_rate / 12 / 100
    n = years * 12
    return amount * r / (1 - (1 + r) ** -n)

print(round(annuity_payment(20000, 6), 2))          # 5 years
print(round(annuity_payment(20000, 6, 10), 2))      # 10 years
```

Parameters with defaults must come **after** the ones without - otherwise Python
cannot know which argument is which:

```python run
def greet(msg="Hi", name):
    print(f"{msg} {name}!")
```

The right way:

```python run
def greet(name, msg="Hi"):
    print(f"{msg} {name}!")

greet("Maria")
greet("Maria", "Good morning")
```

### Keyword arguments

In the call, you can name the parameter: `name=value`. Then the order does not
matter - and the call says what each value means:

```python run
def greet(msg, name):
    print(f"{msg} {name}!")

greet(name="Maria", msg="Hi")
greet("Hi", name="Maria")        # positional first, then keywords
```

Keyword arguments must come **after** the positional ones:

```python run
def greet(msg, name):
    print(f"{msg} {name}!")

greet(name="Maria", "Hi")
```

Keyword arguments make calls with several numbers readable - compare:

```python run
def annuity_payment(amount, yearly_rate, years=5):
    r = yearly_rate / 12 / 100
    return amount * r / (1 - (1 + r) ** -(years * 12))

print(annuity_payment(20000, 6, 10))                              # which is which?
print(annuity_payment(amount=20000, yearly_rate=6, years=10))     # clear
```

You know this from SAS macros with keyword parameters: `%report(data=loans, limit=90)`,
and from `print(..., sep=";", end="")`.

### A trap: a list as a default value

The default value is created **once**, when the `def` runs - not at every call. If it is
a list, all calls share **the same list**:

```python run
def add_loan(loan_id, loans=[]):
    loans.append(loan_id)
    return loans

print(add_loan("L000001"))
print(add_loan("L000002"))        # ['L000001', 'L000002'] - the list remembers!
```

The rule: never use a mutable value (a list, a dict, a set) as a default. Use `None`,
and create the list inside:

```python run
def add_loan(loan_id, loans=None):
    if loans is None:
        loans = []
    loans.append(loan_id)
    return loans

print(add_loan("L000001"))
print(add_loan("L000002"))
```

::: info Animation
**Function calls step by step:** [6. A list as a default value (advanced)](../animations/functionCalls.html#6){target="_blank"}
:::

### Any number of positional arguments: `*args`

A parameter with a star `*` collects **all the extra positional arguments** into a
**tuple**. By custom it is called `*args`, but the name can be any:

```python run
def foo(*args):
    print(args)

foo(1)
foo(1, 2)
foo(1, 2, 3)
foo()
```

`print()`, `max()` and `min()` work like this: `max(3, 8, 5)` takes any number of
values. Your own:

```python run
def total_exposure(*amounts):
    """The sum of any number of amounts."""
    total = 0
    for amount in amounts:
        total += amount
    return total

print(total_exposure(1044231.30))
print(total_exposure(1044231.30, 651927.30, 644.25))
```

`*args` comes **after** the normal parameters. A parameter written after `*args` can
only be given **by name** (a *keyword-only* parameter):

```python run
def greet(*args, first_name):
    print(f"Hello, {first_name}!")

greet("Alice", "Bob", "Charlie")      # all go into args - first_name gets nothing
```

```python run
def greet(first_name, *args):
    print(f"Hello, {first_name}!")
    for other_name in args:
        print(f"Hello, {other_name}!")

greet("Alice", "Bob", "Charlie", "Diana")
```

```python run
def count_over(*values, limit):
    """How many values are over the limit."""
    count = 0
    for value in values:
        if value > limit:
            count += 1
    return count

print(count_over(0, 35, 120, 200, 5, limit=90))
print(count_over(0, 35, 120, 200, 5, limit=30))
```

### Any number of keyword arguments: `**kwargs`

Two stars `**` collect **all the extra keyword arguments** into a **dictionary**
(dictionaries: session 6 - here, pairs of a name and a value):

```python run
def foo(**kwargs):
    print(kwargs)

foo(a=1, b=2)
```

```python run
def print_user_data(**kwargs):
    print(f"Data for user {kwargs['name']}:")
    for key, value in kwargs.items():
        print(f"  {key} - {value}")

print_user_data(name="Ada", age=28)
print_user_data(name="Maria", age=30, town="London")
```

A typical use is a function with many optional settings:

```python run
def report_settings(**options):
    print("Report settings:")
    for setting, value in options.items():
        print(f" - {setting}: {value}")

report_settings(report_date="2026-09-30", currency="EUR", decimals=2)
```

The order of the parameters in a definition, when you use all kinds:

```text
def f(positional, with_default=1, *args, keyword_only, **kwargs):
```

### Unpacking in a call: `*` and `**`

The stars work the other way round in a **call**: `*` unpacks a list or a tuple into
positional arguments, `**` unpacks a dictionary into keyword arguments:

```python run
def my_func(p1, p2, p3):
    print(p1, p2, p3)

data = [1, 2, 3]
my_func(*data)                  # the same as my_func(data[0], data[1], data[2])
my_func(data)                   # TypeError: the whole list goes to p1
```

```python run
def menu_print(fruit, price):
    print(f"{fruit:.<20s}{price:.2f}")

data = {"price": 2.5, "fruit": "apple"}
menu_print(**data)              # the same as menu_print(fruit="apple", price=2.5)
```

A record from a file, straight into a function:

```python run
def describe(loan_id, product, outstanding):
    print(f"{loan_id}: {product}, {outstanding:,.2f}")

record = ("L000002", "investment", 651927.30)
describe(*record)
```

::: details Advanced: keyword-only `*` and positional-only `/`
A bare `*` in a definition means "everything after this must be given by name". It
makes calls readable and safe - nobody can mix up two numbers by position:

```python run
def expected_loss(pd_value, lgd, ead, *, rounded=False):
    el = pd_value * lgd * ead
    return round(el, 2) if rounded else el

print(expected_loss(0.02, 0.45, 100000))
print(expected_loss(0.02, 0.45, 100000, rounded=True))
```

`sorted(items, key=..., reverse=True)` is defined this way: `key` and `reverse` are
keyword-only. A `/` means "everything before this must be given by position" - you see
it in the help of many built-in functions, like `len(obj, /)`.
:::

## 5. Return values

### `return`

`return` ends the function and gives a value back to the caller. The call itself is
then an **expression** with that value: you can print it, give it a name, use it in a
calculation, or pass it to another function.

```python run
def add(x, y):
    return x + y

print(add(2, 4) ** 2)          # 36
result = add(2, 3) + add(4, 5)
print(result)
```

`return` **ends** the function - code after it never runs:

```python run
def add(x, y):
    return x + y
    print("after return")      # never runs

print(add(2, 4))
```

### Without `return`: `None`

A function without `return` (or with a bare `return`) returns `None`. In Python every
function returns something:

```python run
def foo():
    print("foo() was executed!")

def bar():
    print("bar() was executed!")
    return "End"

print(foo())
print(bar())
```

### `print` is not `return`

The most common mistake with functions: `print` **shows** a value on the screen, but
the caller gets nothing. `return` **gives** the value to the caller - and shows nothing.

```python run
def interest_print(outstanding, rate):
    print(outstanding * rate / 100)

def interest_return(outstanding, rate):
    return outstanding * rate / 100

a = interest_print(1000, 5)        # prints 50.0 ...
b = interest_return(1000, 5)       # prints nothing ...
print(a, b)                        # ... but a is None, b is 50.0
print(b * 2)
print(a * 2)                       # TypeError: None * 2
```

Rule: a function that **calculates** returns its result. Printing is the job of the
code that called it - or of a separate function that only prints. That way the same
function can be used in a report, in a file, in a test.

### Several values: a tuple

`return a, b` returns a **tuple** (session 3) - and the caller can unpack it:

```python run
def split_days(days_past_due):
    """Days past due as whole months of 30 days and the days left."""
    return days_past_due // 30, days_past_due % 30

result = split_days(125)
print(result)

months, days = split_days(125)
print(months, "months and", days, "days")
```

```python run
def min_max_average(*values):
    return min(values), max(values), sum(values) / len(values)

low, high, average = min_max_average(5.44, 8.83, 4.79, 8.35)
print(low, high, round(average, 2))
```

### Return early

A function can have several `return` statements - the first one that runs ends the
function. Returning early for the special cases keeps the main logic flat:

```python run
def dpd_bucket(days_past_due):
    """The bucket of days past due, like CASE WHEN."""
    if days_past_due == 0:
        return "current"
    if days_past_due <= 30:
        return "1-30"
    if days_past_due <= 90:
        return "31-90"
    return "90+"

for days in [0, 15, 45, 200]:
    print(days, dpd_bucket(days))
```

No `elif` is needed: after a `return`, the rest does not run.

## 6. Scope: where a name is visible

### Namespaces and scopes

- A **namespace** keeps the names and the objects they are bound to (inside, it is a
  dictionary). It exists while the program runs: the global namespace is created when
  a file is loaded; the local namespace of a function is created **at each call**, and
  deleted when the call ends.
- A **scope** is the part of the code where a namespace is directly visible. Python
  decides scopes from the text of the code, before it runs.

In simple words: the scope of a name is the part of the program where you can use it.

### Local names

Names created **inside a function** - its parameters, and every name assigned in its
body - are **local**: they exist only during the call, and only inside the function.

```python run
def f1():
    y = 2
    print(f"y = {y} inside f1")

f1()
print(f"y = {y} outside f1")        # NameError: y is not defined here
```

### Global names

A name defined **outside any function**, at the top level of a file, is **global** to
the file: every function of the file can read it.

```python run
x = 10

def foo():
    print(f"x = {x} inside foo()")

foo()
print(f"x = {x} outside foo()")
```

### See the namespaces: `locals()` and `globals()`

```python run
x = 10                    # a global name

def foo():
    x = 20                # a local name
    print("local:", locals())
    print("global x:", globals()["x"])

foo()
```

(`globals()` shows many more names - the built-in ones of the module, like
`__name__`.)

### An assignment makes a local name

When a name is **assigned** inside a function, it is local - even if a global name
with the same name exists. They are two different variables:

```python run
x = 1

def foo():
    x = 99                # a new, local x
    print(f"x = {x} inside foo")

foo()
print(f"x = {x} outside foo")        # the global x did not change
```

The same for parameters - a parameter is a local name. A new value for it does not
change the variable of the caller:

```python run
def change(x):
    x = 4
    print("inside:", x)

x = 2
change(x)
print("outside:", x)
```

::: info Animation
**Function calls step by step:** [2. Local and global](../animations/functionCalls.html#2){target="_blank"}
:::

And a trap: if a function **assigns** a name anywhere in its body, the name is local in
the **whole** body - also on the lines before the assignment:

```python run
total = 0

def add(amount):
    total = total + amount        # UnboundLocalError: the local total has no value yet
    return total

add(100)
```

::: info Animation
**Function calls step by step:** [3. `UnboundLocalError`](../animations/functionCalls.html#3){target="_blank"}
:::

### Nested functions

A function can be defined inside another one. Each has its own local names:

```python run
def outer():
    x = 2
    def inner():
        x = 3
        print(f"x = {x} in inner")
    inner()
    print(f"x = {x} in outer")

x = 1
outer()
print(f"x = {x} in global")
```

### `global` and `nonlocal`

`global name` says: "in this function, `name` means the **global** name" - an
assignment changes the global variable:

```python run
def outer():
    x = 2
    def inner():
        global x
        x = 3               # changes the global x
        print(f"x = {x} in inner")
    inner()
    print(f"x = {x} in outer")

x = 1
outer()
print(f"x = {x} in global")
```

`nonlocal name` means the name of the **nearest enclosing function** (not the global
one):

```python run
def outer():
    x = 2
    def inner():
        nonlocal x
        x = 3               # changes the x of outer
        print(f"x = {x} in inner")
    inner()
    print(f"x = {x} in outer")

x = 1
outer()
print(f"x = {x} in global")
```

Use them rarely. A function that changes global variables is hard to understand and to
test: you cannot see from the call what it changes. Prefer: **values in through the
parameters, results out through `return`**.

```python run
total = 0

def add(total, amount):           # in: through the parameters
    return total + amount         # out: through return

total = add(total, 100)
total = add(total, 250)
print(total)
```

### How Python finds a name: LEGB

When a name is used, Python looks for it in four places, **in this order**, and takes
the first one it finds:

1. **L**ocal - the function that runs now;
2. **E**nclosing - the functions around it, from the nearest one out;
3. **G**lobal - the top level of the file (module);
4. **B**uilt-in - the names of Python itself: `print`, `len`, `sum`, ...

If the name is nowhere, it is a `NameError`.

![Four nested boxes: Built-in around Global around Enclosing around Local, with example names; Python looks for a name from the inside out](/diagrams/scope-legb.svg){.diagram width=920 height=400}

This is also why you should not use built-in names for your variables: `sum = 0`
**hides** the built-in `sum()` in that scope (a common habit from other languages):

```python run
sum = 0                      # a global name sum hides the built-in sum
for n in [1, 2, 3]:
    sum += n
print(sum)
print(sum([1, 2, 3]))        # TypeError: 'int' object is not callable
```

| SAS | Python |
|---|---|
| `%local x;` - a macro variable only in this macro | an assignment in a function (the default) |
| `%global x;` | a name at the top level of the file; `global x` to assign it in a function |
| `%let` outside macros | a global variable - use it for constants only |

## 7. Arguments are references

A parameter is bound to **the same object** as the argument - Python does not copy
it (session 3: names and references). For numbers and strings it makes no
difference, because they cannot change. A **list** passed to a function **can** be
changed by the function - and the caller sees the change:

```python run
def add_fee(amounts):
    amounts.append(10)            # changes the caller's list!

fees = [5, 7]
add_fee(fees)
print(fees)
```

::: info Animation
**Function calls step by step:** [5. A list passed to a function](../animations/functionCalls.html#5){target="_blank"}
:::

Sometimes that is what you want (a function that fills a list). Usually it is a
surprise. The safe default: do not change the arguments - build and **return a new
list**:

```python run
def with_fee(amounts, fee=10):
    """A new list: each amount plus the fee. The input is not changed."""
    result = []
    for amount in amounts:
        result.append(amount + fee)
    return result

fees = [5, 7]
new_fees = with_fee(fees)
print(fees, new_fees)
```

## 8. Docstrings and type hints

### Docstrings

A **docstring** is a string right after the `def` line, in triple quotes. It says what
the function does, what it takes and what it returns - for the people who will use it
(you, in three months). Tools show it: `help()`, and VS Code when you hover over the
name.

```python run
def expected_loss(pd_value, lgd, ead):
    """Return the expected loss of one exposure: EL = PD * LGD * EAD.

    pd_value: the probability of default, 0 ... 1
    lgd: the loss given default, 0 ... 1
    ead: the exposure at default, in EUR
    """
    return pd_value * lgd * ead

help(expected_loss)
print(expected_loss.__doc__.splitlines()[0])
```

The conventions ([PEP 257](https://peps.python.org/pep-0257/)): the first line is a
short sentence that says what the function does; then an empty line and the details.

### Type hints

**Type hints** document the types of the parameters and of the result:

```python run
def expected_loss(pd_value: float, lgd: float, ead: float) -> float:
    """Return the expected loss of one exposure: EL = PD * LGD * EAD."""
    return pd_value * lgd * ead

def is_late(days_past_due: int, limit: int = 30) -> bool:
    return days_past_due > limit

def total(amounts: list[float]) -> float:
    return sum(amounts)

def find_loan(loan_id: str, loans: list[tuple[str, float]]) -> tuple[str, float] | None:
    for loan in loans:
        if loan[0] == loan_id:
            return loan
    return None

print(expected_loss(0.02, 0.45, 100000))
print(is_late(45), total([1.5, 2.5]))
print(find_loan("L2", [("L1", 100.0), ("L2", 250.0)]))
```

| Hint | Means |
|---|---|
| `int`, `float`, `str`, `bool` | one value of this type |
| `list[float]` | a list of floats |
| `tuple[str, float]` | a tuple of a string and a float |
| `str \| None` | a string or `None` (since Python 3.10) |
| `-> None` | the function returns nothing |

Python does **not check** type hints when the code runs - they are documentation:

```python run
def is_late(days_past_due: int) -> bool:
    return days_past_due > 30

print(is_late(45.5))       # works: hints are not checked at run time
```

But editors and tools do check them: **Pylance** in VS Code underlines a call with a
wrong type before you run anything, and [mypy](https://mypy-lang.org/) checks a
whole project. In data work, hints are most useful on the functions that other people
call.

::: info Newer Python versions
Python 3.12 added the `type` statement for type aliases: `type Amount = float`. Python
3.14 (the Python of this site) evaluates annotations only when they are needed, so a
hint can name a class that is defined later in the file. Neither is needed in this
course - the hints above work in 3.12 and in every newer version.
:::

## 9. Functions are values

### First-class functions

In Python a function is an **object**, like a number or a list. So a function can be:

- bound to another name, or stored in a list or a dictionary;
- passed as an argument to another function;
- returned as a value from another function.

```python run
def greet(name):
    print(f"Hello, {name}")

foo = greet          # no brackets: the function itself, not a call
greet("Maria")
foo("Maria")         # the same function, another name
print(foo is greet)
```

### A function as an argument

```python run
def apply_function(func, value):
    """Apply a function to a value."""
    return func(value)

def square(x):
    return x * x

def cube(x):
    return x ** 3

print(apply_function(square, 5))
print(apply_function(cube, 5))
```

A function that takes or returns a function is a **higher-order function**. You
already know some: `sorted`, `min` and `max` take a function as `key` (section 10). A
report that can use any rounding rule:

```python run
import math

def total(amounts, rounding):
    result = 0
    for amount in amounts:
        result += rounding(amount)
    return result

amounts = [10.4, 20.6, 30.5]
print(total(amounts, round))
print(total(amounts, math.floor))
print(total(amounts, math.ceil))
```

### A function that returns a function

```python run
def multiply_by(n):
    """Return a function that multiplies its input by n."""
    def multiply(x):
        return x * n
    return multiply

double = multiply_by(2)
to_bgn = multiply_by(1.95583)      # the fixed BGN rate of the euro

print(double(5))
print(round(to_bgn(100), 2))
```

The inner function **remembers** `n` from the call that made it, even after that call
has ended. Such a function is called a **closure**.

### Functions in a dictionary

```python run
def add(x, y):
    return x + y

def sub(x, y):
    return x - y

operations = {"add": add, "sub": sub}
print(operations["add"](4, 2))
print(operations["sub"](4, 2))
```

A dictionary of functions replaces a long `if` / `elif` chain: the key chooses the
function (a *dispatch table*).

### Pure functions

Ideas from **functional programming** that make code easier to trust:

- A **pure function** always returns the same result for the same arguments, and
  does nothing else: it does not print, does not change its arguments or global
  variables, does not write files. `expected_loss(pd, lgd, ead)` is pure.
- Anything else a function does is a **side effect**: printing, writing a file,
  changing a list it got. A program needs side effects - but keep them in a few
  clear places.
- **Immutable** data (tuples, strings) cannot be changed by mistake.

Pure functions are easy to test (call, compare the result), easy to reuse, and safe
to run again on new data - exactly what a monthly report needs.

## 10. `lambda`

### Small functions without a name

A **lambda expression** creates a small function without a name, in one line:

```text
lambda parameters: expression
```

It can have any number of parameters, but only **one expression** - its value is the
result. No `return`, no statements.

```python run
double = lambda x: x * 2
print(double(5))

# the same as:
def double(x):
    return x * 2
print(double(5))
```

```python run
greet = lambda: "Hello, World!"          # no parameters
print(greet())

calc = {
    "add": lambda x, y: x + y,
    "sub": lambda x, y: x - y,
    "mul": lambda x, y: x * y,
    "div": lambda x, y: x / y if y != 0 else "Error: division by zero",
}
print(calc["add"](4, 2), calc["sub"](4, 2), calc["mul"](4, 2), calc["div"](4, 2), calc["div"](4, 0))
```

Do not give a lambda a name in real code (`double = lambda ...`) - that is what `def`
is for, and `def` gives the function a real name in error messages
([PEP 8](https://peps.python.org/pep-0008/#programming-recommendations)). A lambda is
for a function you need **once, right here** - most often as the `key` of a sort.

### Sorting by a key

`sorted()` and `list.sort()` take a `key`: a function that is called for each item,
and the items are sorted by its result. This is `ORDER BY` with any expression:

```python run
data = [(1, "Z"), (2, "Y"), (3, "X")]
print(sorted(data, key=lambda t: t[1]))         # by the second value
```

```python run
loans = [
    ("L000001", "investment", 1044231.30),
    ("L000002", "investment", 651927.30),
    ("L000003", "credit_card", 644.25),
    ("L000004", "overdraft", 5875.11),
]

# ORDER BY outstanding DESC
for loan in sorted(loans, key=lambda loan: loan[2], reverse=True):
    print(loan)

# ORDER BY product, loan_id: a tuple as the key
print(sorted(loans, key=lambda loan: (loan[1], loan[0]))[0])
```

`key` also works with `min` and `max` - the loan with the largest outstanding amount,
not only the amount:

```python run
loans = [("L000001", 1044231.30), ("L000002", 651927.30), ("L000003", 644.25)]
print(max(loans, key=lambda loan: loan[1]))
print(min(loans, key=lambda loan: loan[1]))
```

A list of dictionaries (session 6), sorted by one key:

```python run
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
]
print(sorted(users, key=lambda user: user["age"]))

products = {"apple": 3, "coffee": 2.5, "beer": 4.20}
print(sorted(products.items(), key=lambda item: item[1]))
```

A named function works as a key too - `key=len`, `key=str.lower`:

```python run
print(sorted(["banana", "Cherry", "apple"]))                   # capitals first
print(sorted(["banana", "Cherry", "apple"], key=str.lower))    # ignore the case
print(sorted(["cherry", "fig", "banana"], key=len))
```

Sorting is covered in depth in session 5. Reference:
[Sorting techniques](https://docs.python.org/3/howto/sorting.html).

## 11. Decorators

::: info Advanced
Decorators are not needed for the tasks of this course, but you will meet them in
libraries (`@property` and `@dataclass` in session 11, `@pytest.fixture`, `@app.get` in
web frameworks). This section explains the `@` you will see.
:::

### The idea

A **decorator** is a function that takes a function and returns a new, "decorated"
function: it adds something **before and after** the original, without changing its
code. `decorated = decorator(original)`:

```python run
def stars_decorator(f):
    def wrapper():
        print("*" * 30)
        f()
        print("*" * 30)
    return wrapper

def greet():
    print("Howdy World!")

greet = stars_decorator(greet)       # decorate
greet()
```

### The `@` syntax

`@decorator` above a `def` is a short way to write `name = decorator(name)`:

```python run
def stars_decorator(f):
    def wrapper():
        print("*" * 30)
        f()
        print("*" * 30)
    return wrapper

@stars_decorator
def greet():
    print("Howdy World!")

greet()
```

### Arguments and the return value

The wrapper must pass the arguments on, and return the result of the original.
`*args, **kwargs` (section 4) take any arguments; `functools.wraps` keeps the name and
the docstring of the original. A useful decorator - how long each step of a report
takes:

```python run
import functools
import time

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.4f} s")
        return result
    return wrapper

@timed
def total_outstanding(path):
    total = 0.0
    with open(path, encoding="utf-8") as file:
        file.readline()
        for line in file:
            total += float(line.split(",")[7])
    return total

print(f"{total_outstanding('data/loans.csv'):,.2f}")
```

Read more: [Primer on Python decorators](https://realpython.com/primer-on-python-decorators/)
(Real Python).

## 12. From macros to functions: a small library

### One task, many small functions

The portfolio rules of sessions 1 and 2, as functions. Each one does one thing, has a
docstring, and returns its result:

```python run
def annuity_payment(amount: float, yearly_rate: float, years: int) -> float:
    """The monthly payment of an annuity loan, rounded to cents."""
    r = yearly_rate / 12 / 100
    n = years * 12
    return round(amount * r / (1 - (1 + r) ** -n), 2)


def expected_loss(pd_value: float, lgd: float, ead: float) -> float:
    """EL = PD * LGD * EAD."""
    return pd_value * lgd * ead


def dpd_bucket(days_past_due: int) -> str:
    """The bucket of days past due."""
    if days_past_due == 0:
        return "current"
    if days_past_due <= 30:
        return "1-30"
    if days_past_due <= 90:
        return "31-90"
    return "90+"


def stage(days_past_due: int, rating: int) -> int:
    """The IFRS 9 stage of the sample data."""
    if days_past_due > 90 or rating == 10:
        return 3
    if days_past_due > 30 or rating >= 7:
        return 2
    return 1


print(annuity_payment(20000, 6, 5))
print(expected_loss(0.02, 0.45, 100000))
print(dpd_bucket(45), stage(45, 5), stage(0, 10))
```

A function can call other functions - each call gets its own local names, and
returns to the line that called it:

::: info Animation
**Function calls step by step:** [4. A function calls a function](../animations/functionCalls.html#4){target="_blank"}
:::

### A script made of functions

The structure of a script that you can run again every month: the imports and the
constants at the top, then the functions, and the main code at the bottom.

```python run
"""Outstanding amount and number of loans by days-past-due bucket."""

LOANS_FILE = "data/loans.csv"
BUCKETS = ("current", "1-30", "31-90", "90+")


def dpd_bucket(days_past_due):
    if days_past_due == 0:
        return "current"
    if days_past_due <= 30:
        return "1-30"
    if days_past_due <= 90:
        return "31-90"
    return "90+"


def read_loans(path):
    """The loans of a file as a list of (loan_id, outstanding, days_past_due)."""
    loans = []
    with open(path, encoding="utf-8") as file:
        file.readline()
        for line in file:
            fields = line.strip().split(",")
            loans.append((fields[0], float(fields[7]), int(fields[9])))
    return loans


def bucket_totals(loans, bucket):
    """The number and the outstanding sum of the loans in one bucket."""
    count, total = 0, 0.0
    for loan_id, outstanding, days_past_due in loans:
        if dpd_bucket(days_past_due) == bucket:
            count += 1
            total += outstanding
    return count, total


def print_report(loans):
    print(f"{'bucket':<10}{'loans':>7}{'outstanding':>18}")
    for bucket in BUCKETS:
        count, total = bucket_totals(loans, bucket)
        print(f"{bucket:<10}{count:>7}{total:>18,.2f}")


loans = read_loans(LOANS_FILE)
print_report(loans)
```

Compare it with the first example of session 2: the same result, but now each part
has a name, can be tested alone, and can be reused - `read_loans` in the next report,
`dpd_bucket` in a check of the data.

In a file that is run as a script, the main code is often put under
`if __name__ == "__main__":` - so that the functions can be imported by another file
without running the report. Modules and `import` of your own files are the topic of
session 10.

## 13. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 04-functions/practice/task1-first-functions.py
```

In these tasks you write **functions**; the checks call them with many different
values.

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-first-functions.py` | Small functions: interest, repaid share, is late, monthly rate |
| 2 | `task2-defaults-keywords.py` | Default values and keyword arguments: payment, Bulgarian number format |
| 3 | `task3-args-and-tuples.py` | `*args`, several return values: total, min / max / average, months and days |
| 4 | `task4-portfolio-rules.py` | The rules of the portfolio as functions: bucket, stage, grade, product group |
| 5 | `task5-predict-scope.py` | Predict the values: local and global names, a list passed to a function |
| 6 | `task6-lambda-sorting.py` | Sort and find with `key` and `lambda`; remove duplicates, keep the order |

## Summary

| Topic | Remember |
|-------|----------|
| Define, call | `def name(params):` + an indented body; `name(args)` runs it - the brackets are required |
| Parameters | positional; defaults after the others; `name=value` in the call; `*args` a tuple, `**kwargs` a dictionary |
| Defaults | never a list or a dict as a default - use `None` |
| `return` | ends the function and gives a value; no `return` -> `None`; `return a, b` gives a tuple |
| `print` / `return` | `print` shows, `return` gives - calculating functions return |
| Scope | names assigned in a function are local; LEGB: local, enclosing, global, built-in; avoid `global` |
| References | a list passed to a function can be changed by it - return a new list instead |
| Documentation | a docstring in triple quotes; type hints `x: float -> float` are not checked at run time |
| Functions as values | pass them, store them, return them; `lambda x: ...` for a short `key` |
| Sorting | `sorted(items, key=lambda item: item[2], reverse=True)` - `ORDER BY` any expression |
| SAS macros | a macro writes code; a function runs and returns a value |

## Homework

1. `04-functions/homework.py` (in the homework repository): **a library of portfolio
   functions** - read the loans and the rating scale from the files, find the PD of a
   rating, the expected loss of a loan, and the totals by stage. Every check must print
   `OK`.
2. The practice tasks you did not finish in class.
3. Optional: a **loan calculator** made of functions - the same program as the
   optional homework of session 2, but organised like this:
   `get_user_data()` reads and checks the input (amount > 0, rate 0 - 50, years 1 -
   30; ask again while a value is wrong) and returns a tuple; `calc_payment(amount,
   rate, years)` returns the payment; `print_schedule(amount, rate, years)` prints the
   schedule. Write a separate function for each check: `is_valid_amount()`,
   `is_valid_rate()`, `is_valid_years()`, each returning `True` or `False`.

## Read more

- Python tutorial: [Defining functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions),
  [More on defining functions](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions)
  (defaults, keyword arguments, `*args`, `**kwargs`, `lambda`, docstrings, annotations)
- [Scopes and namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
  in the tutorial; [Namespaces and scope in Python](https://realpython.com/python-namespaces-scope/)
  (Real Python)
- [Defining your own Python function](https://realpython.com/defining-your-own-python-function/)
  (Real Python)
- Type hints: [typing - the basics](https://docs.python.org/3/library/typing.html),
  [the mypy cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- Videos: [Python tutorial for beginners 8: functions](https://www.youtube.com/watch?v=9Os0o3wzS_I)
  (Corey Schafer), [Python lambda functions](https://www.youtube.com/watch?v=j6FCewxjrBM)
  (Visually Explained)

**Next session:** lists, advanced - list comprehensions, sorting with `key`, `zip`,
`enumerate`, `map` and `filter`, and a table as a list of rows.
