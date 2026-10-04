Architecture
============

The GradCafe Analytics application is organized into three primary layers:
the web layer, ETL layer, and database layer.

Web Layer
---------

The web layer is implemented with Flask in ``app.py``. It provides the
Analysis page and handles requests from the "Pull Data" and
"Update Analysis" buttons. The application uses a Flask application
factory so the application can be configured and tested independently.

ETL Layer
---------

The ETL layer is responsible for collecting, cleaning, and preparing
GradCafe applicant data.

``scrape.py`` contains the scraping and parsing logic used to collect
applicant records.

``capture_pages.py`` handles page capture and pagination.

``clean.py`` cleans and standardizes the collected applicant data.

``load_data.py`` loads the prepared records into the database.

Database Layer
--------------

The database layer uses PostgreSQL for persistent storage and SQLAlchemy
for database interaction.

``models.py`` defines the Applicant model and database structure.

``query_data.py`` performs the analysis queries used by the application.

``orm_queries.py`` provides selected database queries using SQLAlchemy ORM.

Application Flow
----------------

The general application flow is:

1. Applicant data is collected and parsed.
2. The data is cleaned and standardized.
3. Records are loaded into PostgreSQL.
4. Analysis queries retrieve and summarize the stored data.
5. Flask renders the analysis results for the user.