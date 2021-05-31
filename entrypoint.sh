#!/bin/sh

POSTGRES_SERVER=${POSTGRES_SERVER:-localhost}
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-}
EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL:-dummy@molar.com}
SMTP_TLS=${SMTP_TLS:-false}
BACKEND_NUM_WORKERS=${BACKEND_NUM_WORKERS:-2}
BACKEND_PORT=${BACKEND_PORT:-8000}

export PGPASSWORD=$POSTGRES_PASSWORD

MAX_RETRIES=10
N_RETRY=1
while ! pg_isready -q -h $POSTGRES_SERVER; do
  echo "Could not connect to the database, retrying in a few seconds"
  sleep 5
  N_RETRY=$(($N_RETRY + 1))
  if [[ $N_RETRY -eq $MAX_RETRIES ]]; then
    echo "Could not connect to database! Please check your configuration!"
    exit
  fi

done


uvicorn \
  --workers $BACKEND_NUM_WORKERS \
  --host 0.0.0.0 \
  --port $BACKEND_PORT \
  molar.backend.main:app 
