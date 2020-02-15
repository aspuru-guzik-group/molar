#!/bin/sh

DB_HOST=${DB_HOST:-localhost}
DB_USER=${DB_USER:-postgres}
DB_PASSWD=${PGPASSWORD}
DB_NAME=${DB_NAME:-mdb}


setup_database() {
    local db_host=$1
    local db_user=$2
    local db_name=$3
    local db_passwd=$4
    PGPASSWORD=${db_passwd} psql -U ${db_user}  -h ${db_host} -c "CREATE DATABASE ${db_name};"
    PGPASSWORD=${db_passwd} psql -U ${db_user}  -h ${db_host} -d ${db_name} -c "CREATE EXTENSION \"uuid-ossp\";"
    PGPASSWORD=${db_passwd} psql -U ${db_user} -a -d ${db_name} -h ${db_host} -f pgsql/structure.sql
    PGPASSWORD=${db_passwd} psql -U ${db_user} -a -d ${db_name} -h ${db_host} -f pgsql/event_sourcing.sql
}


setup_database ${DB_HOST} ${DB_USER} ${DB_NAME} ${DB_PASSWD}
