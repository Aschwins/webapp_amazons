#!/bin/bash
sleep 5

flask db init
flask db migrate -m "init"
flask db upgrade

gunicorn --worker-class eventlet -b localhost:5000 -w 1 amazons:app
