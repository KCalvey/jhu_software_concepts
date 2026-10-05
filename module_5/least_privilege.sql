-- Module 5 least-privilege PostgreSQL application role

CREATE ROLE module5_app
WITH LOGIN
PASSWORD 'replace_with_secure_password'
NOSUPERUSER
NOCREATEDB
NOCREATEROLE
NOINHERIT;

GRANT CONNECT ON DATABASE module3_db TO module5_app;
GRANT USAGE ON SCHEMA public TO module5_app;

GRANT SELECT, INSERT, UPDATE
ON ALL TABLES IN SCHEMA public
TO module5_app;

REVOKE CREATE ON SCHEMA public FROM module5_app;