FROM postgres:14.2-alpine

COPY create_schema.sql /docker-entrypoint-initdb.d/create_schema.sql

ENV PGDATA=/data