#!/bin/sh

export PGPASSWORD=$POSTGRES_PASSWORD

MAX_RETRIES=10
while ! pg_isready -q -h $POSTGRES_SERVER; do
  sleep 5
  MAX_RETRIES=$((MAX_RETRIES - 1))
  if [[ MAX_RETRIES -eq 0 ]]; then
    echo "Could not connect to database"
    exit
  fi

done

DATABASES=$(psql -h localhost -U postgres -l | grep UTF8 | awk '{print $1}')

if ! echo $DATABASES | grep -w -q molar_main > /dev/null; then 
  molarcli install remote \
    --hostname $POSTGRES_SERVER \
    --postgres-username $POSTGRES_USER \
    --postgres-password $POSTGRES_PASSWORD 
fi

uvicorn molar.backend.main:app
