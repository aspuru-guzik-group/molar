DATABASES=$(psql -h localhost -U postgres -l | grep UTF8 | awk '{print $1}')
echo $DATABASES | grep -w -q molar_main
