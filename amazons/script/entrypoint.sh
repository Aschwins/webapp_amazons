#!/bin/bash
sleep 5

flask db init
flask db migrate -m "init"
flask db upgrade

gunicorn -b 0.0.0.0:5000 -w 1 app:app
