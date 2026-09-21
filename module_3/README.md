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
