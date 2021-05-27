DATABASES=$(psql -h localhost -U postgres -l | grep UTF8 | awk '{print $1}')


if [[ ! $(echo $DATABASES | grep -w -q molar_main) ]]; then 
  molarcli install remote \
    --hostname $POSTGRES_SERVER \
    --postgres-username $POSTGRES_USER \
    --postgres-password $POSTGRES_PASSWORD 
fi


uvicorn molar.backend.main:app
