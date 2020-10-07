#!/bin/bash
# Check if db exist if not create it.
ls /home/amazons/app

DIRECTORY=/home/amazons/app/migrations
if [ -d "$DIRECTORY" ]; then
    echo "$DIRECTORY already exists. Skipping creating database"
    flask db migrate -d "app/migrations" -m "init"
    flask db upgrade -d "app/migrations"
else
    echo "$DIRECTORY doesnt exist, creating database..."
    flask db init -d "app/migrations"
    flask db migrate -d "app/migrations" -m "init"
    flask db upgrade -d "app/migrations"
fi

# Make sure dev database can be accessed from anywhere
chmod 777 app/app.db
chmod -R 777 app/migrations

flask run --host=0.0.0.0
