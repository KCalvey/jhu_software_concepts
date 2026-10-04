Testing Guide
=============

The GradCafe Analytics project uses Pytest for automated testing and
pytest-cov to verify 100% source-code coverage.

Running the Full Test Suite
---------------------------

From the repository root, run:

.. code-block:: bash

   python3 -m pytest module_4/tests -v

The project is configured through ``module_4/pytest.ini`` to measure
coverage for code under ``module_4/src`` and require 100% coverage.

Pytest Markers
--------------

Tests are organized using the following markers:

``web``
   Flask route and page-rendering tests.

``buttons``
   Tests for the "Pull Data" and "Update Analysis" endpoints and busy-state
   behavior.

``analysis``
   Tests for analysis labels and percentage formatting.

``db``
   Database schema, insert, and query tests.

``integration``
   End-to-end application flow tests.

Marked tests can be run with:

.. code-block:: bash

   python3 -m pytest module_4/tests -m "web or buttons or analysis or db or integration" -v

Test Doubles and Fixtures
-------------------------

The test suite uses Flask's test client along with fake or mocked database,
scraper, loader, and query behavior so tests remain fast and deterministic.

Tests do not depend on live internet access or long-running scraping jobs.

Stable Selectors
----------------

The Flask page uses stable ``data-testid`` selectors for interactive
elements such as the Pull Data and Update Analysis buttons. These selectors
allow UI behavior to be tested without manual browser interaction.

Coverage
--------

The complete test suite achieves 100% coverage of the Python source files
under ``module_4/src``.

A terminal coverage summary is stored in:

``module_4/coverage_summary.txt``