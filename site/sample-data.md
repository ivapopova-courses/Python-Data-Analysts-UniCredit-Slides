# Sample data

The examples on these pages and the tasks in the Homework repository use the same
small, **made-up** loan portfolio. Nothing in it comes from a real bank: the
clients, the loans and all values are invented. Only the shape is typical:
a table of clients, a table of loans that points to the clients, and a
nomenclature (the rating scale).

| File | Rows | What it is |
|---|---|---|
| `data/clients.csv` | 150 | one row per client |
| `data/loans.csv` | 400 | one row per loan; `client_id` points to `clients.csv` |
| `data/rating_scale.csv` | 10 | the rating scale: one row per rating grade, with its PD band |

The same files are in the `data/` folder of the Homework repository. On these
pages they are in `data/` of every runnable example.

## clients.csv

| Column | Example | Meaning |
|---|---|---|
| `client_id` | `C0002` | the id of the client |
| `segment` | `sme` | `retail`, `sme` or `corporate` |
| `region` | `Ruse` | the region of the client |
| `industry` | `M` | an industry code (a letter, like the sections of NACE); empty for retail clients |
| `rating` | `5` | the internal rating, 1 (best) to 10 (default) - see `rating_scale.csv` |
| `client_since` | `2014-06-08` | the start of the relationship (ISO date) |

```python run
import pandas as pd

clients = pd.read_csv("data/clients.csv")
clients.head()
```

## loans.csv

| Column | Example | Meaning |
|---|---|---|
| `loan_id` | `L000001` | the id of the loan |
| `client_id` | `C0080` | the client (see `clients.csv`) |
| `product` | `investment` | `mortgage`, `consumer`, `credit_card`, `overdraft`, `working_capital`, `investment`, `project_finance` |
| `currency` | `EUR` | `EUR` or `USD` |
| `start_date`, `maturity_date` | `2026-01-22` | ISO dates |
| `amount` | `1156900.00` | the original amount |
| `outstanding` | `1044231.30` | the amount still to be paid on the report date (30.09.2026) |
| `interest_rate` | `8.83` | in percent per year |
| `days_past_due` | `0` | days the payments are late |
| `stage` | `1` | 1, 2 or 3 - stage 3 means more than 90 days past due or rating 10 |

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.groupby("product")["outstanding"].sum().round(2)
```

## rating_scale.csv

A nomenclature: one row per rating, with its grade and the band of the
probability of default (PD).

| Column | Example | Meaning |
|---|---|---|
| `rating` | `4` | 1 to 10 |
| `grade` | `BBB` | the letter grade |
| `pd_min`, `pd_max` | `0.0025`, `0.006` | the PD band of the grade (0.0025 = 0.25%) |
| `description` | `moderate risk` | |

```python run
import csv

with open("data/rating_scale.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["rating"], row["grade"], row["description"])
```

::: tip Without pandas
The first lectures read the files with the standard library (`open`, `csv`), and
pandas comes in session 14. Both ways read the same files.
:::
