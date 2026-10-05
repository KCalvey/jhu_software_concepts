# Module 2
## Responsible Scraping and robots.txt

Before collecting any data, I reviewed The GradCafe's robots.txt file to verify that the pages used for this assignment permit crawler access.

The robots.txt file allows the general `*` user agent to access the site while specifically disallowing several restricted paths, including `/signin`, `/register`, `/forgot-password`, `/reset-password`, `/confirm-password`, `/verify-email`, and `/profile`.

This scraper will access only publicly available GradCafe pages permitted by robots.txt. It will not attempt to access restricted or login-protected pages or bypass CAPTCHAs, rate limits, Cloudflare verification, or other access restrictions. The scraper will also use reasonable delays between page requests and will stop if the website blocks, rate-limits, or otherwise rejects requests.

Evidence of the robots.txt review is included in `screenshot.jpg`.

## Module 2 - GradCafe Web Scraping

This project programmatically collects publicly accessible graduate applicant data from The GradCafe. The final applicant_data.json contains more than 30,000 unique applicant records.

### Scraping Approach
The project uses a hybrid workflow. urllib is used for URL construction and management, while normal browser-rendered pages are captured and parsed with BeautifulSoup. Cursor-based pagination is followed using the site's public Next links. Reasonable delays are used between page requests.

The site's robots.txt was reviewed before scraping. Evidence is included in screenshot.jpg. The workflow does not bypass authentication, CAPTCHAs, rate limits, or other access controls.

### Files
- scrape.py - scraping and applicant-data parsing logic
- capture_pages.py - browser page capture and cursor pagination
- clean.py - data cleaning and standardization
- applicant_data.json - final scraped applicant dataset
- llm_extend_applicant_data.json - cleaned/extended applicant dataset
- screenshot.jpg - robots.txt compliance evidence
- requirements.txt - Python dependencies

### Data Cleaning
The cleaning workflow removes remaining HTML markup, decodes HTML entities, normalizes whitespace, preserves the original program information, and provides standardized program and university fields.

The instructor-provided local LLM hosting files are included in the llm_hosting directory. The submitted clean.py performs deterministic Python cleaning and standardization and saves the resulting dataset as llm_extend_applicant_data.json.

### Requirements
Python 3.10 or later is required.

Install dependencies with:

pip install -r requirements.txt

Run the scraper/capture workflow as documented in the source files, then run:

python clean.py

#  Module 3 - PostgreSQL and SQLAlchemy Analysis

## Overview

This module extends the GradCafe applicant data project by loading the cleaned applicant data into a PostgreSQL database and analyzing the data using both raw SQL and SQLAlchemy ORM.

The project includes SQL queries that analyze applicant counts, nationality classifications, GPA and GRE averages, acceptance rates, degree programs, and universities. It also uses SQLAlchemy to perform selected analyses through an ORM rather than handwritten SQL.

## Module 3 Files

- `load_data.py` - loads the cleaned applicant data into PostgreSQL
- `query_data.py` - performs the required analysis using raw SQL
- `models.py` - defines the SQLAlchemy Applicant model and database connection
- `orm_queries.py` - performs selected analyses using SQLAlchemy ORM
- `app.py` - Flask application used to display analysis results
- `limitations.pdf` - discussion of limitations of self-reported GradCafe data
- `query_results.pdf` - contains the results, SQL queries, and explanations for the 11 analysis questions

## SQL and SQLAlchemy Comparison

For this comparison, I used Question 1, which determines how many applicants applied for Fall 2026.

### Raw SQL

```sql
SELECT COUNT(*)
FROM applicants
WHERE LOWER(term) = 'fall 2026';

### SQLAlchemy
stmt = select(func.count()).select_from(Applicant).where(
    func.lower(Applicant.term) == "fall 2026"
)

count = session.scalar(stmt)
### Raw SQL

```sql
SELECT COUNT(*)
FROM applicants
WHERE LOWER(term) = 'fall 2026';
```

### SQLAlchemy

```python
stmt = select(func.count()).select_from(Applicant).where(
    func.lower(Applicant.term) == "fall 2026"
)

count = session.scalar(stmt)
```

### Comparison

Raw SQL makes the database operation very direct because the exact query being executed is easy to see and understand. SQLAlchemy provides an abstraction layer that allows the same database operation to be expressed using Python objects. The ORM approach can make database code easier to integrate with a larger Python application and maintain as the application grows. For a simple query like this one, raw SQL is more concise, while SQLAlchemy provides the benefit of working directly with the application's Python models.

# Module 4 - Pytest and Sphinx

## Overview

Module 4 extends the GradCafe Analytics application by adding automated
testing, code coverage, continuous integration, and Sphinx documentation.

The test suite verifies the Flask application, button behavior, analysis
formatting, database operations, query functions, and scraping/parsing
functionality. The complete test suite achieves 100% code coverage for
the source code under `module_4/src`.

## Project Structure

- `src/` - Flask application, scraping, cleaning, database, and analysis code
- `tests/` - Pytest test suite
- `docs/` - Sphinx documentation
- `pytest.ini` - Pytest configuration and test markers
- `requirements.txt` - Project dependencies
- `coverage_summary.txt` - Terminal output demonstrating 100% test coverage
- `.github/workflows/tests.yml` - GitHub Actions CI workflow

## Setup

Install the required dependencies:

```bash
pip install -r module_4/requirements.txt

# Module 5 - Software Assurance and Secure SQL

## Overview

Module 5 adds software assurance and security controls to the GradCafe analytics application. The project includes SQL injection defenses, query LIMIT enforcement, environment-based database configuration, least-privilege database access, dependency analysis, Pylint validation, Snyk security scanning, Pytest testing, and GitHub Actions continuous integration.

## Fresh Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```
Install the project dependencies using pip:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Alternatively, install the dependencies using uv:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Environment Variables

Database credentials are loaded from environment variables rather than hard-coded in the source code. Copy `.env.example` and provide the appropriate local database values for `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`. The `.env` file containing actual credentials is excluded from version control.

## Pylint

Run Pylint on the Module 5 source files with:

```bash
pylint src/*.py --fail-under=10
```

All submitted source files are required to achieve a Pylint score of 10.00/10.

## Testing

Run the automated test suite with:

```bash
pytest
```

## SQL Injection Defenses

SQL statements use psycopg SQL composition and parameterized values rather than constructing SQL from user input with string concatenation, f-strings, or `.format()`. SQL statement construction is kept separate from execution, and user-supplied values are passed as parameters to `cursor.execute()`.

## Query LIMIT Enforcement

Database queries include LIMIT clauses to restrict returned data. Dynamic limits are validated with `safe_limit()`, which clamps requested values between 1 and `MAX_LIMIT` (100).

## Least-Privilege Database Access

The `module5_app` PostgreSQL role is configured as a non-superuser without database-creation or role-creation privileges. It receives only the database, schema, and table permissions required by the application. The SQL used to configure the role is included in `least_privilege.sql`.

## Dependency Analysis

The project dependency graph is generated with pydeps and Graphviz:

```bash
pydeps src --noshow -o dependency.svg
```

The generated graph is included as `dependency.svg`.

## Snyk Security Analysis

Dependency security scanning is performed with:

```bash
snyk test
```

The scan output is documented in `snyk_results.txt`, and screenshot evidence is included as `snyk-analysis.png`.

Snyk Code static application security testing was also performed for extra credit with:

```bash
snyk code test
```

The SAST results are included in `snyk_code_results.txt`.

## GitHub Actions CI

The GitHub Actions workflow automatically installs dependencies, initializes the PostgreSQL test database, runs Pylint with the required `--fail-under=10` threshold, executes Pytest, generates and validates `dependency.svg`, and performs a Snyk dependency scan.
