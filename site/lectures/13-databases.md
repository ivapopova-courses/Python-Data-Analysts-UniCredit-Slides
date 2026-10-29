---
title: 13. Working with databases
---

# 13. Working with databases

<div class="lecture-meta">
  <span>Session 13</span><span>practice: <code>13-databases/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- connect to a database from Python, run SQL and read the result - with the
  standard interface that works for every database;
- pass values to a query safely, with **parameters** - never by gluing text;
- write tables, and keep changes safe with **transactions**;
- decide what the database should do and what Python should do;
- read the result of a query straight into a **DataFrame**, with pandas and
  SQLAlchemy;
- connect to your own database (Oracle, MS SQL Server, PostgreSQL, ...) without a
  password in the code.

You know SQL. This session is about **Python talking to a database** - the SQL is the
one you write every day. From SAS to Python - a query with a parameter, two ways:

```sas
%let stage = 3;
proc sql;
    select loan_id, client_id, outstanding
    from db.loans
    where stage = &stage
    order by outstanding desc;
quit;
```

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
rows = con.execute(
    "SELECT loan_id, client_id, outstanding FROM loans WHERE stage = ? ORDER BY outstanding DESC",
    (3,),
).fetchall()
con.close()

print(len(rows), "loans in stage 3; the largest:")
for row in rows[:3]:
    print(row)
```

The file `data/portfolio.db` (new today) is an **SQLite** database with the tables of
the sample data: `clients`, `loans`, `rating_scale` and `ratings_history`.

## 1. Databases from Python

### The picture

```text
 your code      driver (a Python package)     the database
 ---------      -------------------------     ------------
 connect()  ->  opens a connection        ->  checks the user, the password
 execute()  ->  sends the SQL text        ->  runs the query
 fetch...() <-  turns rows into tuples    <-  sends the rows back
 close()    ->  closes the connection
```

- A **driver** is a package that knows the network protocol of one kind of database:
  `oracledb` for Oracle, `pyodbc` for MS SQL Server, `psycopg` for PostgreSQL.
- All drivers follow the same standard, the **DB-API** (PEP 249): `connect`,
  `cursor`, `execute`, `fetchall`, `commit`, `close`. What you learn today with SQLite
  works with your database too - only the `connect` line changes (section 7).
- **SQLite** is a database in a single file. The module `sqlite3` comes with Python -
  nothing to install, no server. Perfect for learning, for tests and for small local
  data marts.

| SAS | Python |
|---|---|
| `LIBNAME db ORACLE user=... path=...;` | `con = oracledb.connect(...)` |
| `PROC SQL; CONNECT TO ORACLE (...);` (pass-through) | `con.execute("... SQL of the database ...")` |
| a libref `db.loans` | a table name in the SQL text |

### What is in the database?

SQLite keeps its catalogue in the table `sqlite_master` (other databases have
`information_schema` or `ALL_TABLES`):

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
for name, sql in con.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'"):
    print(name)
    print("   ", " ".join(sql.split())[:110], "...")
con.close()
```

The column names and types of one table - `PRAGMA table_info` (in SAS: `PROC
CONTENTS`):

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
for cid, name, col_type, notnull, default, pk in con.execute("PRAGMA table_info(loans)"):
    print(f"{name:<15}{col_type:<9}{'NOT NULL' if notnull else '':<10}{'PK' if pk else ''}")
con.close()
```

The number of rows of every table - the table names come from **your** fixed list, so
they can be put into the SQL text (values never - section 3):

```python run
import sqlite3

TABLES = ["clients", "loans", "rating_scale", "ratings_history"]
con = sqlite3.connect("data/portfolio.db")
for table in TABLES:
    n, = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    print(f"{table:<16}{n:>6}")
con.close()
```

How the tables are linked - the **foreign keys** of `loans` (each loan points to a
client), and its indexes:

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
for row in con.execute("PRAGMA foreign_key_list(loans)"):
    print("foreign key:", row[3], "->", row[2] + "." + row[4])
print("indexes:", [row[1] for row in con.execute("PRAGMA index_list(loans)")])
con.close()
```

::: warning A typo in the file name creates a new, empty database
`sqlite3.connect` **creates** the file if it does not exist. A wrong path gives no
error at the connect - only later, "no such table". To open an existing file only (and
read-only), use a URI with `mode=ro`:

```python run
import sqlite3
from pathlib import Path

con = sqlite3.connect("data/portfolo.db")                      # typo: a new, empty file
try:
    con.execute("SELECT COUNT(*) FROM loans")
except sqlite3.OperationalError as error:
    print("OperationalError:", error)
con.close()
Path("data/portfolo.db").unlink()                              # remove the empty file again

try:
    sqlite3.connect("file:data/portfolo.db?mode=ro", uri=True)   # read-only, must exist
except sqlite3.OperationalError as error:
    print("OperationalError:", error)
```
:::

::: tip Try it
Change the second example to show the columns of `ratings_history`. Which columns
form its primary key?
:::

## 2. Connect and query

### A connection, a cursor, the rows

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")        # open the connection
cur = con.cursor()                                # a cursor runs SQL and holds the result
cur.execute("SELECT COUNT(*), ROUND(SUM(outstanding), 2) FROM loans")
print(cur.fetchone())                              # one row, a tuple

cur.execute("SELECT loan_id, product, outstanding FROM loans ORDER BY outstanding DESC LIMIT 3")
print(cur.fetchall())                              # all rows: a list of tuples
con.close()                                        # close it at the end
```

- `fetchone()` - the next row, or `None` at the end;
- `fetchall()` - all (remaining) rows as a list;
- `fetchmany(n)` - the next `n` rows (for big results, Self-study).

`con.execute(...)` is a shortcut of SQLite: it creates the cursor for you and returns
it. With other drivers, use `con.cursor()` first.

### Loop over the rows

A cursor is iterable - loop over it like over a file (session 2): one row at a time,
little memory:

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
total = 0.0
for loan_id, outstanding in con.execute("SELECT loan_id, outstanding FROM loans WHERE currency = 'USD'"):
    total += outstanding
print(f"USD loans: {total:,.2f}")
con.close()
```

The values come back **typed**: `outstanding` is a `float`, `stage` an `int` - no
`float(row[7])` as with a CSV file.

`fetchmany(n)` takes the next `n` rows; a new `execute` on the same cursor starts a new
result:

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
cur = con.execute("SELECT loan_id FROM loans ORDER BY loan_id")
print(cur.fetchmany(3))
print(cur.fetchmany(2))                     # the next two
cur.execute("SELECT COUNT(*) FROM clients")  # a new query: the old result is gone
print(cur.fetchone())
con.close()
```

A mistake in the SQL is an exception like any other (session 9) - in SQLite an
`OperationalError`, with the message of the database:

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
try:
    con.execute("SELECT loan_id, outstandingg FROM loans")
except sqlite3.OperationalError as error:
    print("SQL error:", error)
con.close()
```

Rows straight into the dataclasses of session 11 - `*row` unpacks the tuple into the
fields:

```python run
import sqlite3
from dataclasses import dataclass

@dataclass
class Loan:
    loan_id: str
    product: str
    outstanding: float
    stage: int


con = sqlite3.connect("data/portfolio.db")
loans = [Loan(*row) for row in con.execute("SELECT loan_id, product, outstanding, stage FROM loans")]
con.close()
print(len(loans), loans[0])
print(sum(l.outstanding for l in loans if l.stage == 3))
```

### The column names

`cursor.description` describes the columns of the last query; its first item per
column is the name:

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
cur = con.execute("SELECT client_id, segment, rating FROM clients LIMIT 2")
columns = [d[0] for d in cur.description]
rows = cur.fetchall()
print(columns)
print([dict(zip(columns, row)) for row in rows])
con.close()
```

Or let SQLite give each row **by name** - `row_factory = sqlite3.Row`:

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
con.row_factory = sqlite3.Row
row = con.execute("SELECT * FROM clients WHERE client_id = 'C0002'").fetchone()
print(row["segment"], row["region"], row["rating"])
print(row.keys())
print(dict(row))
con.close()
```

### Close the connection - always

A connection holds resources on the database server (and a lock on an SQLite file).
Close it also when the query fails: `try` / `finally` (session 9), or
`contextlib.closing` in a `with`:

```python run
import sqlite3
from contextlib import closing

with closing(sqlite3.connect("data/portfolio.db")) as con:
    n = con.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
print(n, "clients; the connection is closed")
```

::: warning `with sqlite3.connect(...)` does not close
For `sqlite3`, `with con:` is a **transaction** (section 4), not a close. Use
`closing(...)` - or `con.close()` in `finally` - to close. The short examples below
write `with sqlite3.connect(...) as con:` to save a line: the connection is closed
when the example ends. In a script that runs for a long time, close it yourself.
:::

### Types in SQLite

SQLite has few types: `INTEGER`, `REAL`, `TEXT`, `BLOB` and `NULL`. **Dates are text**
(ISO, `2026-09-30`) - they sort and compare correctly as text (session 2), and you
convert them in Python when you need dates:

```python run
import sqlite3
from datetime import date

with sqlite3.connect("data/portfolio.db") as con:
    start, = con.execute("SELECT MIN(start_date) FROM loans").fetchone()
print(start, type(start))
print((date(2026, 9, 30) - date.fromisoformat(start)).days, "days")
```

(`start, = ...` unpacks a tuple of one value.) `NULL` comes back as `None`:

```python run
import sqlite3

with sqlite3.connect("data/portfolio.db") as con:
    print(con.execute("SELECT client_id, industry FROM clients WHERE segment = 'retail' LIMIT 2").fetchall())
```

::: tip Try it
Write a query for the 5 clients with the most loans (`GROUP BY client_id`), and print
them with `row_factory = sqlite3.Row` as `C0030: 5 loans`.
:::

## 3. Parameterised queries

### `?` - the value goes separately

A query with a value from your program - a stage, a region, a report date. Write a `?`
in the SQL, and pass the values as a **tuple**, separately:

```python run
import sqlite3

region = "Varna"
with sqlite3.connect("data/portfolio.db") as con:
    rows = con.execute(
        "SELECT client_id, segment, rating FROM clients WHERE region = ? AND rating >= ? ORDER BY rating DESC",
        (region, 7),
    ).fetchall()
print(rows)
```

A one-value tuple needs the comma: `(3,)`. With many parameters, named ones are easier
to read - `:name` and a dictionary:

```python run
import sqlite3

params = {"segment": "sme", "min_amount": 500000}
with sqlite3.connect("data/portfolio.db") as con:
    n, total = con.execute(
        """SELECT COUNT(*), ROUND(SUM(l.outstanding), 2)
           FROM loans l JOIN clients c ON c.client_id = l.client_id
           WHERE c.segment = :segment AND l.outstanding >= :min_amount""",
        params,
    ).fetchone()
print(n, total)
```

(Other drivers use other placeholders: `%s` for psycopg and pyodbc's `?`, `:name` for
oracledb. The idea is the same.)

Dates go as ISO text into SQLite (other drivers accept `date` objects directly), and
`LIKE` patterns are values too:

```python run
import sqlite3
from datetime import date

report_date = date(2026, 9, 30)
with sqlite3.connect("data/portfolio.db") as con:
    n_old, = con.execute("SELECT COUNT(*) FROM loans WHERE start_date < ?",
                         (date(2020, 1, 1).isoformat(),)).fetchone()
    n_month, = con.execute("SELECT COUNT(*) FROM ratings_history WHERE month_end = ?",
                           (report_date.isoformat(),)).fetchone()
    first_ids = con.execute("SELECT loan_id FROM loans WHERE loan_id LIKE ? ORDER BY loan_id",
                            ("L00000%",)).fetchall()
print(n_old, n_month, len(first_ids))
```

A query with parameters inside a function is a reusable report - the function of
session 4, the SQL of today:

```python run
import sqlite3

def stage_report(con, report_month_end, currency):
    sql = """SELECT l.stage, COUNT(*), ROUND(SUM(l.outstanding), 2)
             FROM loans l WHERE l.currency = ? AND l.start_date <= ?
             GROUP BY l.stage ORDER BY l.stage"""
    return {stage: (n, total) for stage, n, total in con.execute(sql, (currency, report_month_end))}

with sqlite3.connect("data/portfolio.db") as con:
    print(stage_report(con, "2026-09-30", "USD"))
    print(stage_report(con, "2025-12-31", "USD"))
```

::: warning `("C0002")` is not a tuple
Without the comma, the brackets do nothing: the parameter is the **string**, and a
string is a sequence of 5 characters - 5 values for one `?`:

```python run
import sqlite3

with sqlite3.connect("data/portfolio.db") as con:
    print(con.execute("SELECT segment FROM clients WHERE client_id = ?", ("C0002",)).fetchone())
    con.execute("SELECT segment FROM clients WHERE client_id = ?", ("C0002"))
# ProgrammingError: Incorrect number of bindings supplied. The current statement uses 1, and there are 5 supplied.
```
:::

### Why never an f-string: SQL injection

It is tempting to build the SQL text with an f-string. Do not - with values from
outside (a file, a form, a parameter of a script), the text can **change the query**:

```python run
import sqlite3

client_id = "C0001' OR '1'='1"                     # a "client id" from an input file

with sqlite3.connect("data/portfolio.db") as con:
    unsafe = f"SELECT COUNT(*) FROM clients WHERE client_id = '{client_id}'"
    print(unsafe)
    print("f-string:  ", con.execute(unsafe).fetchone())        # all 150 clients!
    print("parameter: ", con.execute("SELECT COUNT(*) FROM clients WHERE client_id = ?",
                                     (client_id,)).fetchone())  # 0: no such id
```

With a parameter, the driver sends the value **as a value** - it can never become SQL.
Parameters also handle quotes in names (`O'Neil`), dates and numbers correctly, and
let the database reuse the query plan.

| SAS | Python |
|---|---|
| `where region = "&region"` (macro text) | `WHERE region = ?`, `(region,)` |
| `%superq`, quoting functions | not needed: the value is never text of the query |

::: danger Values: parameters. Names: your own code only
Parameters work for **values**. Table and column names cannot be parameters - if a
script must choose a table, take the name from a fixed list in your code, never
directly from an input.
:::

A parameter in the place of a **name** does not fail - it is worse: `ORDER BY ?` sorts
by the constant text `"outstanding"`, which is the same for every row, so the order is
not what you asked for:

```python run
import sqlite3

with sqlite3.connect("data/portfolio.db") as con:
    print(con.execute("SELECT loan_id FROM loans ORDER BY ? DESC LIMIT 3", ("outstanding",)).fetchall())
    print(con.execute("SELECT loan_id FROM loans ORDER BY outstanding DESC LIMIT 3").fetchall())
```

### `IN` lists

`WHERE x IN (?)` with a list does not work - one `?` is one value. Make one `?` per
item:

```python run
import sqlite3

products = ["mortgage", "consumer", "credit_card"]
placeholders = ", ".join("?" for _ in products)            # "?, ?, ?"
sql = f"SELECT product, COUNT(*) FROM loans WHERE product IN ({placeholders}) GROUP BY product"
print(sql)

with sqlite3.connect("data/portfolio.db") as con:
    print(con.execute(sql, products).fetchall())
```

The f-string builds only the **placeholders** - the values still go as parameters.
(For thousands of values, `itertools.batched` of session 10 cuts the list into
pieces.)

### The same query, many values: `executemany`

```python run
import sqlite3

with sqlite3.connect(":memory:") as con:                     # a database in memory, for tests
    con.execute("CREATE TABLE watch_list (loan_id TEXT PRIMARY KEY, reason TEXT)")
    con.executemany("INSERT INTO watch_list VALUES (?, ?)",
                    [("L000002", "late"), ("L000070", "large"), ("L000246", "large")])
    print(con.execute("SELECT * FROM watch_list").fetchall())
```

`":memory:"` creates a database that lives only while the connection is open - for
examples and tests.

::: tip Try it
Write a function `loans_of(con, client_id)` that returns the loan ids of a client,
sorted, with a parameter. Call it with `"C0030"` and with `"C0001' OR '1'='1"`.
:::

## 4. Writing and transactions

### Work on a copy

Never practise writes on a real database - and not on `data/portfolio.db` either. Make
a copy: `con.backup` copies a whole SQLite database, even into memory:

```python run
import sqlite3

source = sqlite3.connect("data/portfolio.db")
work = sqlite3.connect(":memory:")
source.backup(work)                                # a full copy of all tables
source.close()

print(work.execute("SELECT COUNT(*) FROM loans").fetchone())
work.close()
```

### Create a table, insert rows, commit

```python run
import sqlite3

source = sqlite3.connect("data/portfolio.db")
con = sqlite3.connect(":memory:")
source.backup(con)
source.close()

con.execute("""CREATE TABLE IF NOT EXISTS late_loans (
                   loan_id TEXT PRIMARY KEY,
                   days_past_due INTEGER NOT NULL,
                   noted_on TEXT NOT NULL)""")
late = con.execute("SELECT loan_id, days_past_due FROM loans WHERE days_past_due > 90").fetchall()
con.executemany("INSERT INTO late_loans VALUES (?, ?, '2026-09-30')", late)
con.commit()                                       # make the changes permanent

print(con.execute("SELECT COUNT(*), MAX(days_past_due) FROM late_loans").fetchone())
con.close()
```

`INSERT INTO ... SELECT` works too - the database does it all without sending the rows
to Python:

```python run
import sqlite3

source = sqlite3.connect("data/portfolio.db")
con = sqlite3.connect(":memory:")
source.backup(con)
source.close()

con.execute("CREATE TABLE stage3 AS SELECT loan_id, client_id, outstanding FROM loans WHERE stage = 3")
con.commit()
print(con.execute("SELECT COUNT(*), ROUND(SUM(outstanding), 2) FROM stage3").fetchone())
con.close()
```

### Transactions: all or nothing

A **transaction** groups changes: either **all** of them are saved (`commit`) or
**none** (`rollback`). The DB-API starts a transaction by itself before the first
change; nothing is saved until `commit()`:

```python run
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE balances (loan_id TEXT PRIMARY KEY, outstanding REAL NOT NULL)")
con.executemany("INSERT INTO balances VALUES (?, ?)", [("L1", 1000.0), ("L2", 500.0)])
con.commit()

con.execute("UPDATE balances SET outstanding = outstanding - 300 WHERE loan_id = 'L1'")
print("before rollback:", con.execute("SELECT * FROM balances").fetchall())
con.rollback()                                     # undo everything since the last commit
print("after rollback: ", con.execute("SELECT * FROM balances").fetchall())
con.close()
```

### `with con:` - commit or roll back by itself

For `sqlite3`, a connection used in `with` **commits** at the end of the block - or
**rolls back** if an exception happens inside. A payment run that must not be half
done:

```python run
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE payments (payment_id TEXT PRIMARY KEY, loan_id TEXT, amount REAL NOT NULL)")
con.commit()

batch = [("P1", "L000002", 100.0), ("P2", "L000003", 50.0), ("P1", "L000004", 75.0)]   # P1 twice!
try:
    with con:                                       # one transaction
        con.executemany("INSERT INTO payments VALUES (?, ?, ?)", batch)
except sqlite3.IntegrityError as error:
    print("rolled back:", error)

print(con.execute("SELECT COUNT(*) FROM payments").fetchone())    # 0: none of the three
con.close()
```

The duplicate `P1` broke the **primary key**; the whole batch was rolled back - not
two rows of three. In a monthly load, this is what you want: the table is either
updated completely, or not at all.

A `NOT NULL` column refuses a missing value - the database checks the data too:

```python run
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE fx (day TEXT NOT NULL, currency TEXT NOT NULL, rate REAL NOT NULL)")
try:
    with con:
        con.execute("INSERT INTO fx VALUES (?, ?, ?)", ("2026-09-30", "USD", None))
except sqlite3.IntegrityError as error:
    print(error)
con.close()
```

`executemany` also takes **dictionaries** with named parameters - the rows of
`csv.DictReader` (session 6) go straight into a table:

```python run
import csv
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE rating_scale (rating INTEGER, grade TEXT, pd_min REAL, pd_max REAL, description TEXT)")
with open("data/rating_scale.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))
with con:
    con.executemany("INSERT INTO rating_scale VALUES (:rating, :grade, :pd_min, :pd_max, :description)", rows)
print(con.execute("SELECT grade, pd_max FROM rating_scale WHERE rating >= 8").fetchall())
con.close()
```

A log table with an automatic id - `INTEGER PRIMARY KEY` numbers the rows; `lastrowid`
gives the id of the row just inserted:

```python run
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE run_log (run_id INTEGER PRIMARY KEY, report TEXT, status TEXT)")
with con:
    cur = con.execute("INSERT INTO run_log (report, status) VALUES (?, ?)", ("monthly", "started"))
    run_id = cur.lastrowid
    con.execute("UPDATE run_log SET status = ? WHERE run_id = ?", ("finished", run_id))
print(run_id, con.execute("SELECT * FROM run_log").fetchall())
con.close()
```

To keep a changed copy, write it to a **file** - `backup` into a new database file:

```python run
import sqlite3
from pathlib import Path

Path("out").mkdir(exist_ok=True)
source = sqlite3.connect("data/portfolio.db")
target = sqlite3.connect("out/portfolio_work.db")
source.backup(target)
source.close()
with target:
    target.execute("DELETE FROM loans WHERE stage = 3")
print(target.execute("SELECT COUNT(*) FROM loans").fetchone(), Path("out/portfolio_work.db").stat().st_size, "bytes")
target.close()
```

| SQL / SAS | Python DB-API |
|---|---|
| `COMMIT;` | `con.commit()` |
| `ROLLBACK;` | `con.rollback()` |
| a failed `PROC APPEND` leaves the table as it was | `with con:` + an exception |
| a constraint violation | `sqlite3.IntegrityError` (other drivers: their own `IntegrityError`) |

### `UPDATE` and `DELETE` with parameters

```python run
import sqlite3

source = sqlite3.connect("data/portfolio.db")
con = sqlite3.connect(":memory:")
source.backup(con)
source.close()

with con:
    cur = con.execute("UPDATE loans SET stage = 2 WHERE days_past_due > ? AND stage = 1", (15,))
    print(cur.rowcount, "loans moved to stage 2 (a stricter rule: more than 15 days)")
    cur = con.execute("DELETE FROM loans WHERE outstanding < ?", (500,))
    print(cur.rowcount, "small loans deleted")
con.close()
```

`cursor.rowcount` is the number of rows the statement changed - check it: an `UPDATE`
that changes 0 rows (or 40,000) is often a bug.

::: tip Try it
In a copy of the database, create a table `client_flags (client_id, flag)` and insert
the clients with rating 8 or worse with the flag `"watch"`, in one `with con:` block.
Then try to insert one of them again: what happens to the transaction?
:::

## 5. What to do in SQL, what in Python

### Let the database do the heavy work

With a real database, the data is on a server, often millions of rows. Moving all rows
to your laptop to filter them there is slow. The rule: **filter, join and aggregate in
SQL**; take only the result into Python - the same idea as SAS pass-through.

The totals by stage, two ways - the same numbers:

```python run
import sqlite3
from collections import defaultdict

with sqlite3.connect("data/portfolio.db") as con:
    in_sql = con.execute("""SELECT stage, COUNT(*), ROUND(SUM(outstanding), 2)
                            FROM loans GROUP BY stage ORDER BY stage""").fetchall()

    totals = defaultdict(lambda: [0, 0.0])                 # in Python: every row comes over
    for stage, outstanding in con.execute("SELECT stage, outstanding FROM loans"):
        totals[stage][0] += 1
        totals[stage][1] += outstanding

print(in_sql)
print([(s, n, round(t, 2)) for s, (n, t) in sorted(totals.items())])
```

`HAVING` and `CASE WHEN` - the SQL of session 2 and 6, run by the database:

```python run
import sqlite3

sql = """
SELECT CASE WHEN days_past_due = 0 THEN 'current'
            WHEN days_past_due <= 30 THEN '1-30'
            WHEN days_past_due <= 90 THEN '31-90'
            ELSE '90+' END AS bucket,
       COUNT(*) AS loans, ROUND(SUM(outstanding), 2) AS outstanding
FROM loans
GROUP BY bucket
HAVING COUNT(*) >= 10
ORDER BY loans DESC
"""
with sqlite3.connect("data/portfolio.db") as con:
    for row in con.execute(sql):
        print(row)
```

How much faster is the database? A small test - with 400 rows the difference is small,
with millions on a server it is minutes against seconds:

```python run
import sqlite3
import time

with sqlite3.connect("data/portfolio.db") as con:
    start = time.perf_counter()
    in_sql = con.execute("SELECT client_id, SUM(outstanding) FROM loans GROUP BY client_id").fetchall()
    t_sql = time.perf_counter() - start

    start = time.perf_counter()
    totals = {}
    for client_id, outstanding in con.execute("SELECT client_id, outstanding FROM loans"):
        totals[client_id] = totals.get(client_id, 0) + outstanding
    t_python = time.perf_counter() - start

print(len(in_sql), len(totals), f"SQL {t_sql * 1000:.2f} ms, Python {t_python * 1000:.2f} ms")
```

### A join in SQL

The expected loss of the portfolio - the number of homework 4, 6 and 11 - in **one**
query, with two joins:

```python run
import sqlite3

sql = """
SELECT ROUND(SUM((s.pd_min + s.pd_max) / 2 * 0.45 * l.outstanding), 2) AS el
FROM loans l
JOIN clients c      ON c.client_id = l.client_id
JOIN rating_scale s ON s.rating = c.rating
"""
with sqlite3.connect("data/portfolio.db") as con:
    print(con.execute(sql).fetchone())
```

1,140,106.56 again: loops (4), dictionaries (6), objects (11) and SQL agree.

### The rating migration: a self join

Which clients changed their rating from August to September? A join of
`ratings_history` with itself:

```python run
import sqlite3

sql = """
SELECT a.rating AS from_rating, b.rating AS to_rating, COUNT(*) AS clients
FROM ratings_history a
JOIN ratings_history b ON b.client_id = a.client_id
WHERE a.month_end = :before AND b.month_end = :after AND a.rating <> b.rating
GROUP BY a.rating, b.rating
ORDER BY a.rating, b.rating
"""
with sqlite3.connect("data/portfolio.db") as con:
    moves = con.execute(sql, {"before": "2026-08-31", "after": "2026-09-30"}).fetchall()

worse = sum(n for f, t, n in moves if t > f)
better = sum(n for f, t, n in moves if t < f)
print(moves)
print(worse, "clients downgraded,", better, "upgraded")
```

(Session 16 turns this into a full **migration matrix** with pandas.)

### Step by step: `WITH`

A long query reads better in named steps - a **common table expression** (`WITH`), like
a chain of `PROC SQL` steps that create temporary tables. The share of the 10 largest
clients in the portfolio:

```python run
import sqlite3

sql = """
WITH exposure AS (                          -- step 1: one row per client
    SELECT client_id, SUM(outstanding) AS outstanding
    FROM loans GROUP BY client_id
),
top10 AS (                                  -- step 2: the 10 largest
    SELECT * FROM exposure ORDER BY outstanding DESC LIMIT 10
)
SELECT ROUND((SELECT SUM(outstanding) FROM top10) / (SELECT SUM(outstanding) FROM exposure), 4)
"""
with sqlite3.connect("data/portfolio.db") as con:
    print(con.execute(sql).fetchone())
```

### When Python is the better place

- logic that is hard in SQL: text cleaning with regex (8), nomenclature classes (12),
  checks with clear error messages (9);
- combining data from several sources: a database, a CSV, an Excel file;
- the report itself: Excel, charts, files.

A common pattern: SQL for the **data** (filter, join, aggregate), Python for the
**rules** and the **report**.

Two sources together: the exposure per client from the database, the names from the
register file of session 7 - joined in Python with a dictionary:

```python run
import csv
import sqlite3

with sqlite3.connect("data/portfolio.db") as con:
    top = con.execute("""SELECT client_id, ROUND(SUM(outstanding), 2) FROM loans
                         GROUP BY client_id ORDER BY 2 DESC LIMIT 3""").fetchall()

with open("data/client_register.csv", encoding="utf-8") as file:
    name_of = {row["client_id"].strip().upper(): " ".join(row["name"].split()) for row in csv.DictReader(file)}

for client_id, exposure in top:
    print(f"{client_id} {name_of.get(client_id, '?'):<28}{exposure:>16,.2f}")
```

The names are as they were typed into the register - the `clean_name` of session 7
would fix them. That is the Python part of the job.

::: tip Try it
Write one SQL query for the outstanding per segment and stage (`GROUP BY` two
columns). Then compare one number with homework 6.
:::

## 6. pandas and SQLAlchemy

### The result of a query as a DataFrame

`pd.read_sql(sql, connection)` runs the query and returns a **DataFrame** - a table
with named, typed columns. pandas is the topic of the next three sessions; today, only
how the result arrives:

```python run
import sqlite3
import pandas as pd

with sqlite3.connect("data/portfolio.db") as con:
    df = pd.read_sql("SELECT loan_id, product, outstanding, stage FROM loans", con)

print(type(df), df.shape)          # rows, columns
print(list(df.columns))
df.head()
```

The last line is shown as a table: `head()` gives the first 5 rows. Parameters work
the same way:

```python run
import sqlite3
import pandas as pd

sql = """SELECT c.segment, l.stage, COUNT(*) AS loans, ROUND(SUM(l.outstanding), 2) AS outstanding
         FROM loans l JOIN clients c ON c.client_id = l.client_id
         WHERE l.currency = ?
         GROUP BY c.segment, l.stage"""
with sqlite3.connect("data/portfolio.db") as con:
    df = pd.read_sql(sql, con, params=("EUR",))
df
```

`parse_dates` turns the text dates of SQLite into real dates:

```python run
import sqlite3
import pandas as pd

with sqlite3.connect("data/portfolio.db") as con:
    df = pd.read_sql("SELECT loan_id, start_date, maturity_date FROM loans", con,
                     parse_dates=["start_date", "maturity_date"])
print(df.dtypes)
print(df["maturity_date"].max())
```

(pandas 3 shows text columns as `str` and dates as `datetime64[us]`; pandas 2.2 shows
`object` and `datetime64[ns]`. The data is the same - session 14 explains the types.)

A DataFrame goes back to Python rows when you need them - `to_dict("records")` gives
a list of dictionaries (session 6):

```python run
import sqlite3
import pandas as pd

with sqlite3.connect("data/portfolio.db") as con:
    df = pd.read_sql("SELECT grade, pd_min, pd_max FROM rating_scale WHERE rating <= 3", con)
print(df.to_dict("records"))
```

### SQLAlchemy: one way to connect to every database

**SQLAlchemy** (in `requirements.txt`) is a library on top of the drivers: one
**engine** object, made from a URL, for any database. pandas works best with it - for
SQLite a plain connection is fine, for other databases pandas expects an engine:

```python run
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///data/portfolio.db")      # the URL: dialect:///file

df = pd.read_sql(text("SELECT segment, COUNT(*) AS clients FROM clients GROUP BY segment"), engine)
print(df)

with engine.connect() as con:                               # also without pandas
    result = con.execute(text("SELECT COUNT(*) FROM loans WHERE stage = :stage"), {"stage": 2})
    print(result.scalar())
engine.dispose()
```

A DataFrame from the engine with **named** parameters - `text()` and a dictionary:

```python run
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///data/portfolio.db")
sql = text("""SELECT loan_id, product, outstanding FROM loans
              WHERE stage = :stage AND outstanding > :min_outstanding ORDER BY outstanding DESC""")
df = pd.read_sql(sql, engine, params={"stage": 3, "min_outstanding": 100000})
engine.dispose()
df
```

- `create_engine(url)` - the URL names the database kind and where it is (section 7).
- `text(...)` marks a string as SQL; parameters are `:name`.
- `engine.dispose()` closes the connections of the engine when you are done.

SQLAlchemy can also **look into** a database - the tables and their columns, for any
database kind:

```python run
from sqlalchemy import create_engine, inspect

engine = create_engine("sqlite:///data/portfolio.db")
inspector = inspect(engine)
print(inspector.get_table_names())
print([c["name"] for c in inspector.get_columns("ratings_history")])
print(inspector.get_pk_constraint("ratings_history")["constrained_columns"])
engine.dispose()
```

With an engine, pandas reads a whole table by its name:

```python run
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///data/portfolio.db")
scale = pd.read_sql_table("rating_scale", engine)
print(scale.shape)
print(scale[["grade", "pd_max"]].tail(3))
engine.dispose()
```

### Write a DataFrame to a table: `to_sql`

```python run
import sqlite3
import pandas as pd

work = sqlite3.connect(":memory:")
regions = pd.DataFrame({"code": ["SOF", "VAR"], "name_en": ["Sofia", "Varna"]})
regions.to_sql("regions", work, index=False, if_exists="replace")
print(work.execute("SELECT * FROM regions").fetchall())
work.close()
```

`if_exists="replace"` drops and recreates the table; `"append"` adds rows; `"fail"`
(the default) stops if the table exists.

The trap of `"append"`: run the load twice - the second run of the same month - and
every row is there twice. Delete the month first (one transaction), then append:

```python run
import sqlite3
import pandas as pd

work = sqlite3.connect(":memory:")
month = pd.DataFrame({"month_end": ["2026-09-30"] * 2, "loan_id": ["L1", "L2"], "outstanding": [100.0, 50.0]})

for run in (1, 2):                                       # the script runs twice
    month.to_sql("balances", work, index=False, if_exists="append")
print(work.execute("SELECT COUNT(*) FROM balances").fetchone())       # 4 rows - doubled

with work:
    work.execute("DELETE FROM balances WHERE month_end = ?", ("2026-09-30",))
month.to_sql("balances", work, index=False, if_exists="append")
print(work.execute("SELECT COUNT(*) FROM balances").fetchone())       # 2 rows
work.close()
```

::: info pandas 2 and pandas 3
`pd.read_sql` with a `sqlite3` connection works in both. With any **other** DB-API
connection (oracledb, pyodbc), pandas shows a `UserWarning` and asks for an SQLAlchemy
engine - use one.
:::

::: tip Try it
Read `ratings_history` for `2026-09-30` into a DataFrame with a parameter, and print
its `shape`. Then `df["rating"].value_counts()` - a preview of session 14.
:::

## 7. Your database: drivers and passwords

### The drivers

On this page everything is SQLite. At work, the same code runs against your database -
with its driver and its connection string. The common ones:

| Database | Driver (`pip install`) | SQLAlchemy URL |
|---|---|---|
| Oracle | `oracledb` | `oracle+oracledb://user:pw@host:1521/?service_name=ORCL` |
| MS SQL Server | `pyodbc` (+ the Microsoft ODBC driver) | `mssql+pyodbc://@server/db?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes` |
| PostgreSQL | `psycopg` | `postgresql+psycopg://user:pw@host:5432/db` |
| Teradata | `teradatasql` (+ `teradatasqlalchemy`) | `teradatasql://user:pw@host` |
| SQLite | (comes with Python) | `sqlite:///path/to/file.db` |

The DB-API calls of sections 2 - 4 are the same; the differences are the placeholder
style (`?`, `%s`, `:name`) and the SQL dialect of the database. Your IT department
says which driver and which server; on a corporate laptop the driver may need to be
installed by IT.

```python
# Oracle, without SQLAlchemy (not runnable here)
import os
import oracledb

con = oracledb.connect(user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
                       dsn="dbhost.example.com:1521/RISKDB")
cur = con.cursor()
cur.execute("SELECT COUNT(*) FROM loans WHERE report_date = :d", {"d": "2026-09-30"})
print(cur.fetchone())
con.close()
```

```python
# MS SQL Server with Windows login, through SQLAlchemy (not runnable here)
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("mssql+pyodbc://@risk-sql01/RiskMart"
                       "?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes")
df = pd.read_sql("SELECT TOP 10 * FROM dbo.loans", engine)
```

### Never a password in the code

A password in a script, a notebook or a config file ends up in Git, in e-mails and in
backups (session 10). Ways to keep it out:

- **Windows login** (trusted connection, Kerberos) - no password at all, if your
  database supports it; the best option.
- **environment variables** (session 10) - set per user, read with `os.environ`.
- the **keyring** package - stores the password in the Windows Credential Manager.
- a `.env` file **listed in `.gitignore`**, read with the `python-dotenv` package.

```python run
import os

os.environ.setdefault("DB_USER", "risk_reader")       # on this page: pretend it is set
user = os.environ["DB_USER"]
password = os.getenv("DB_PASSWORD")                   # None if it is not set
if password is None:
    print(f"DB_PASSWORD is not set for {user} - ask for it, never write it into the script")
```

::: code-group
```powershell [Windows]
$env:DB_USER = "risk_reader"
$env:DB_PASSWORD = Read-Host -MaskInput "Password"
python report.py
```
```bash [Linux / macOS]
export DB_USER=risk_reader
read -s -p "Password: " DB_PASSWORD && export DB_PASSWORD
python report.py
```
:::

SQLAlchemy builds a URL from its parts - and hides the password when the URL is
printed (into a log, say):

```python run
from sqlalchemy.engine import URL

url = URL.create("postgresql+psycopg", username="risk_reader", password="s3cret",
                 host="dbhost.example.com", port=5432, database="riskmart")
print(url)                                            # the password is masked
print(url.render_as_string(hide_password=True))
```

The path of the database is a setting too: from an environment variable, with a
default - the script runs unchanged on another computer:

```python run
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

db_path = Path(os.getenv("PORTFOLIO_DB", "data/portfolio.db"))
url = URL.create("sqlite", database=str(db_path))
print(url)

engine = create_engine(url)
with engine.connect() as con:
    print(con.execute(text("SELECT COUNT(*) FROM clients")).scalar())
engine.dispose()
```

Ask for a **read-only** account for analysis: a script with a bug can then never
change the data of the bank.

::: tip Try it
Write a function `connection_url(kind, host, database)` that returns the SQLAlchemy URL
for `"postgresql"` and `"sqlite"` from the table above, with the user taken from
`os.environ["DB_USER"]` and **no** password in the result.
:::

## 8. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 13-databases/practice/task1-first-queries.py
```

The tasks read `data/portfolio.db`; the ones that write work on a copy in memory.

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-first-queries.py` | Connect, count, fetch rows, column names, `sqlite3.Row` |
| 2 | `task2-parameters.py` | Parameterised queries, `IN` lists, injection-safe functions |
| 3 | `task3-aggregate-join.py` | `GROUP BY` and `JOIN` in SQL; the same numbers in Python |
| 4 | `task4-write-transaction.py` | A copy, a new table, `executemany`, a rollback that keeps the table clean |
| 5 | `task5-read-sql.py` | `pd.read_sql` with parameters; shape, columns, a total |
| 6 | `task6-migration.py` (Optional) | Rating migration between two month ends with a self join |

## Summary

| Topic | Remember |
|-------|----------|
| DB-API | `connect` -> `cursor` / `execute` -> `fetchone` / `fetchall` / loop -> `close`; the same for all databases |
| SQLite | a database in a file; `sqlite3` comes with Python; `:memory:` for tests; dates are ISO text |
| Rows | tuples, typed; `cursor.description` for names; `row_factory = sqlite3.Row` for rows by name |
| Close | `closing(...)` or `finally`; `with con:` in sqlite3 is a transaction, not a close |
| Parameters | `?` or `:name` + a tuple / dict; never f-strings with values (SQL injection); `IN` with one `?` per item |
| Writing | `executemany`; `commit()`; `rowcount`; work on a copy (`con.backup`) |
| Transactions | all or nothing; `rollback()`; `with con:` commits or rolls back; `IntegrityError` |
| SQL or Python | filter, join, aggregate in SQL; rules, cleaning and the report in Python |
| pandas | `pd.read_sql(sql, con, params=..., parse_dates=...)` -> a DataFrame; `df.to_sql(...)` |
| SQLAlchemy | `create_engine(url)`, `text("... :name")`; needed by pandas for non-SQLite databases |
| Passwords | never in code: Windows login, environment variables, keyring; a read-only account |

## Homework

1. `13-databases/homework.py` (in the homework repository): **a monthly report from
   the database** - parameterised by the report date: the exposure and the EL by
   segment and stage in SQL, the clients that moved to a worse rating since the month
   before, and a table of rule breaks written in one transaction to a copy of the
   database. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: find out which database your team uses, which Python driver it needs,
   and whether you can get a read-only account - we use the answer in session 16.

## Self-study

This part is not covered in class. It is for reading at home: tables too big for
memory, and window functions - `LAG`, `RETAIN` and `FIRST.` of SAS, in SQL.

### Big tables: in pieces

A query that returns 50 million rows does not fit into a list or a DataFrame on a
laptop. Read it **in pieces**, and keep only what you need from each piece:

```python run
import sqlite3

with sqlite3.connect("data/portfolio.db") as con:
    cur = con.execute("SELECT month_end, outstanding FROM (SELECT * FROM loans, "
                      "(SELECT DISTINCT month_end FROM ratings_history))")      # 400 x 12 rows
    pieces, total, rows = 0, 0.0, 0
    while True:
        chunk = cur.fetchmany(1000)              # at most 1000 rows in memory
        if not chunk:
            break
        pieces += 1
        rows += len(chunk)
        total += sum(outstanding for _, outstanding in chunk)
print(pieces, "pieces,", rows, "rows,", f"{total:,.2f}")
```

pandas does the same with `chunksize`: `read_sql` then returns the DataFrames one by
one:

```python run
import sqlite3
import pandas as pd

with sqlite3.connect("data/portfolio.db") as con:
    totals = None
    for chunk in pd.read_sql("SELECT client_id, rating FROM ratings_history", con, chunksize=500):
        counts = chunk["rating"].value_counts()
        totals = counts if totals is None else totals.add(counts, fill_value=0)
print(totals.sort_index().astype(int).to_dict())
```

Better still: let the database aggregate (section 5) - then the result is small.

**Exercises**

1. Count the rows of `ratings_history` per month with `fetchmany(200)` and a
   `Counter`.
2. Why is `SELECT month_end, COUNT(*) ... GROUP BY month_end` better?

::: details Answer
1.
```python
from collections import Counter
counts = Counter()
with sqlite3.connect("data/portfolio.db") as con:
    cur = con.execute("SELECT month_end FROM ratings_history")
    while chunk := cur.fetchmany(200):          # := gives the result a name (3.8+)
        counts.update(m for (m,) in chunk)
print(sorted(counts.items()))
```
2. The database sends 12 rows instead of 1,800 - and it uses its indexes. Pieces are
for when you really need every row (an export, a model).
:::

### Window functions: `LAG`, `RETAIN` and `FIRST.` in SQL

SQLite (3.25+), Oracle, MS SQL Server and PostgreSQL have **window functions**: a
value from **other rows** of the same group, without collapsing the rows like `GROUP
BY` does. Three SAS habits in SQL:

```python run
import sqlite3

sql = """
SELECT client_id, month_end, rating,
       LAG(rating) OVER (PARTITION BY client_id ORDER BY month_end)        AS previous,   -- LAG
       rating - LAG(rating) OVER (PARTITION BY client_id ORDER BY month_end) AS change,
       ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY month_end)       AS n           -- FIRST. = n 1
FROM ratings_history
WHERE client_id = ?
ORDER BY month_end
"""
with sqlite3.connect("data/portfolio.db") as con:
    for row in con.execute(sql, ("C0132",)):
        print(row)
```

A running total per client - `RETAIN` with `BY`:

```python run
import sqlite3

sql = """
SELECT client_id, loan_id, outstanding,
       ROUND(SUM(outstanding) OVER (PARTITION BY client_id ORDER BY loan_id), 2) AS running_total
FROM loans WHERE client_id IN ('C0030', 'C0099') ORDER BY client_id, loan_id
"""
with sqlite3.connect("data/portfolio.db") as con:
    for row in con.execute(sql):
        print(row)
```

**Exercises**

1. With `LAG`, find all (client, month) rows where the rating got **worse** by 2 or
   more notches in one month.
2. With `ROW_NUMBER() ... ORDER BY outstanding DESC`, keep only the largest loan of
   each client (the `FIRST.` of a sorted BY group).

::: details Answer
1.
```sql
SELECT * FROM (
  SELECT client_id, month_end, rating,
         rating - LAG(rating) OVER (PARTITION BY client_id ORDER BY month_end) AS change
  FROM ratings_history)
WHERE change >= 2
```
2.
```sql
SELECT * FROM (
  SELECT client_id, loan_id, outstanding,
         ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY outstanding DESC) AS n
  FROM loans)
WHERE n = 1
```
Run them with `con.execute(...).fetchall()`.
:::

## Read more

- Reference: [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) (with a good
  tutorial at the top), [PEP 249 - DB-API 2.0](https://peps.python.org/pep-0249/)
- pandas: [`read_sql`](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html),
  [`to_sql`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html)
- SQLAlchemy: [Establishing connectivity - the engine](https://docs.sqlalchemy.org/en/20/tutorial/engine.html),
  [Database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)
- Drivers: [python-oracledb](https://python-oracledb.readthedocs.io/),
  [pyodbc](https://github.com/mkleehammer/pyodbc/wiki),
  [psycopg](https://www.psycopg.org/psycopg3/docs/)
- SQLite: [Window functions](https://www.sqlite.org/windowfunctions.html)

**Next session:** NumPy and pandas - arrays that calculate a whole column at once, and
the DataFrame: read CSV and Excel files, and look at a dataset the way `PROC CONTENTS`,
`PROC MEANS` and `PROC FREQ` do.
