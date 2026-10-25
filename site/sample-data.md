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

From session 7 on, more files of the same made-up portfolio - with the problems of
real data on purpose: messy text, several formats, bad rows, history over time.

| File | Rows | What it is | Sessions |
|---|---|---|---|
| `data/client_register.csv` | 150 | the clients with their text fields as people typed them | 7, 8 |
| `data/loan_comments.csv` | 231 | free-text comments of credit officers about loans | 8 |
| `data/payments_2026-09.csv` | 280 | the payments of September 2026, with some bad rows | 9 |
| `data/report_config.json` | - | the settings of a monthly report | 9 |
| `data/fx_rates.xlsx` | 3 sheets | daily exchange rates, one sheet per month | 9, 14, 16 |
| `data/regions_bg.csv` | 7 | the regions in Bulgarian and English - saved in **cp1251** | 7, 9 |
| `data/ratings_history.csv` | 1800 | the rating of each client at 12 month ends | 12, 13, 16 |
| `data/balances_monthly.csv` | 3992 | the outstanding amount of each loan at 12 month ends | 16 |
| `data/loans_export.csv` | 406 | `loans.csv` as a local export: `;`, decimal comma, `dd.mm.yyyy`, missing values, duplicates | 14, 15 |
| `data/portfolio.db` | 4 tables | an SQLite database: `clients`, `loans`, `rating_scale`, `ratings_history` | 13, 16 |

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

## The files of the later sessions

### client_register.csv

The same 150 clients as `clients.csv`, but the text fields as they were typed into an
old system: `client_id` in many forms (`c0014`, `C 0009`, `C-0026`, `C17`), names in
any case with extra spaces and quotes, legal forms written as `E.A.D.`, EIKs with
spaces or a `BG` in front, IBANs in groups of four or in lower case, e-mails in upper
case or with `" at "`, cities in Latin or Cyrillic, with `gr. ` in front, registration
dates in five formats, and the turnover of companies in Bulgarian and English number
formats. Columns: `client_id`, `name`, `eik`, `iban`, `email`, `city`, `registered`,
`turnover`. The IBANs use made-up bank codes (`DEMO`, `TEST`, `XMPL`, `FAKE`) and the
e-mails the reserved `example.*` domains.

### loan_comments.csv

`loan_id`, `comment_date` (ISO), `comment`: short notes like *"Payment of 1 250,00
EUR received on 15.09.2026."* or *"Disbursement to IBAN BG71 DEMO ... confirmed"* -
amounts, dates, IBANs, EIKs, e-mails and loan ids inside free text.

### payments_2026-09.csv

`payment_id`, `loan_id`, `pay_date`, `amount`, `currency`. Most rows are fine; some are
not: a missing amount, `12O.50` (a letter O), `n/a`, a date that does not exist, an
unknown loan, a negative amount, a field too few or too many, an empty line.

### report_config.json, fx_rates.xlsx, regions_bg.csv

- `report_config.json`: the report date, the LGD, the DPD buckets, the segments and
  the output settings of a monthly report.
- `fx_rates.xlsx`: one sheet per month (`2026-07`, `2026-08`, `2026-09`); columns
  `date`, `USD`, `GBP`, `CHF` - how many units of the currency one euro buys.
- `regions_bg.csv`: `code`, `name_bg`, `name_en` - saved in the Windows Cyrillic
  encoding **cp1251**, like many old exports. Open it with `encoding="cp1251"`.

### ratings_history.csv and balances_monthly.csv

The history of 12 month ends, from 31.10.2025 to 30.09.2026; the last month agrees
with `clients.csv` and `loans.csv`. A client or a loan appears only from the month
it started.

- `ratings_history.csv`: `client_id`, `month_end`, `rating`.
- `balances_monthly.csv`: `loan_id`, `month_end`, `outstanding`, `days_past_due`.

### loans_export.csv

The 400 loans as an export from a local system: the separator is `;`, the decimals
have a comma (`651927,30`), dates are `dd.mm.yyyy`, the column names have spaces
(`Loan ID`), the file starts with a BOM (Excel's "CSV UTF-8"). Some values are
missing - empty, or `.` like a SAS missing value - and 6 rows are duplicated.

### portfolio.db

An SQLite database with four tables: `clients`, `loans`, `rating_scale` and
`ratings_history` - the same data as the CSV files, with primary and foreign keys.

```python run
import sqlite3

con = sqlite3.connect("data/portfolio.db")
for name, sql in con.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'"):
    print(name)
print(con.execute("SELECT COUNT(*), ROUND(SUM(outstanding), 2) FROM loans").fetchone())
con.close()
```

::: tip Without pandas
The first lectures read the files with the standard library (`open`, `csv`), and
pandas comes in session 14. Both ways read the same files.
:::
