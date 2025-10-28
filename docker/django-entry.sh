#!/bin/sh

RETRIES=10
START=10
INTERVAL=5

sleep $START
while [ ! $RETRIES -eq 0 ]; do
    pg_isready -U $POSTGRES_USER -d $POSTGRES_DB -h $DATABASE_HOST -p $DATABASE_PORT 
    if [ $? -eq 0 ]; then
        echo "DB CONNECTION SUCCESS"
        uv run manage.py makemigrations && uv run manage.py migrate
        exec "$@"
    fi
    let "RETRIES = RETRIES - 1"
    sleep $INTERVAL
done

echo "DB CONNECTION FAILED"
exit 1