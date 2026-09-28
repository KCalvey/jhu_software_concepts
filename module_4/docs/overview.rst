Overview and Setup
==================

GradCafe Analytics is a Flask-based application for collecting, cleaning,
storing, and analyzing graduate admissions data. The application combines
a web interface with an ETL workflow and a PostgreSQL database.

Setup
-----

Python 3.9 or later is required.

Install the required dependencies from the ``module_4`` directory:

.. code-block:: bash

   pip install -r requirements.txt

Database Configuration
----------------------

The application uses PostgreSQL. Set the ``DATABASE_URL`` environment
variable to the appropriate PostgreSQL connection string before running
the application.

Running the Application
-----------------------

The Flask application is located in ``src/app.py``. From the repository
root, run:

.. code-block:: bash

   python3 module_4/src/app.py

Running Tests
-------------

Run the complete Pytest suite with:

.. code-block:: bash

   python3 -m pytest module_4/tests -v

The test suite uses pytest-cov and requires 100% coverage of the source
code in ``module_4/src``.