Operational Notes
=================

Busy-State Policy
-----------------

The application uses a busy-state mechanism to prevent conflicting
operations from running at the same time.

While a data pull is in progress, requests that could interfere with the
active operation are rejected. The automated tests verify this behavior
without using arbitrary sleep delays.

Idempotency and Uniqueness
--------------------------

The data-loading workflow is designed so that pulling overlapping data
does not create duplicate database records.

Tests verify that repeated pulls remain consistent with the application's
uniqueness policy.

Database Configuration
----------------------

PostgreSQL connections are configured using the ``DATABASE_URL``
environment variable. This allows the database configuration to be
overridden for testing and avoids hard-coding credentials in the
application.

Testing Strategy
----------------

Tests use fake or mocked dependencies where appropriate so the test suite
does not rely on live internet access or long-running scraping operations.

This keeps the tests deterministic and allows the complete suite to run
quickly.

Troubleshooting
---------------

If tests fail locally, verify that all required packages from
``requirements.txt`` are installed and that the appropriate
``DATABASE_URL`` is configured.

If Sphinx documentation fails to build, verify that Sphinx and the
Read the Docs theme are installed and that the documentation configuration
can locate the modules under ``module_4/src``.

If database-related tests fail, verify that PostgreSQL is available and
that the configured test database can be reached.