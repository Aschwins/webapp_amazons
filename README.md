# GOA - Online. "The Game Of Amazons"

## Introduction

This is the repository for the web application: Game of Amazons. Inspired by the amazing numberphile video with mathematician 
Elwyn Berlekamp. [video](https://www.youtube.com/watch?v=kjSOSeRZVNg)

![Erwyn](amazons/static/img/elwynamazons.jpg)

## Development

The webapplication could be run locally to play games against someone else on the same screen, but we're planning to bring it live very soon.

To start the Flask web application in development mode, run the following with pip and virtualenv installed.

```sh
git clone https://github.com/Aschwins/webapp_amazons/master
cd webapp_amazons

# Install uv by astrall
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv sync
source .venv/bin/activate

# Copy env.example and rename to env and fill in the variables.
cp .env.example .env

# Run the application
flask --app amazons/run run
```

or with docker

```sh
docker compose -f docker-compose.dev.yml up -d --build
```

Happy hunting!

## Production

https://game-of-amazons.org

For the production version of the web application we use a linux server in Amazon Lightsail.


### Supervisor
We're using the [supervisor](http://supervisord.org/) to run gunicorn in the background. The config file for the 
supervisor can be found in `/etc/supervisor/conf.d`. Use 
```sudo supervisorctl reload```
to start the server.

### Nginx
We use nginx as a reverse proxy. The config can be found at `/etc/nginx/sites-enabled/amazons`. All requests to http 
(port 80) get rerouted to https (443), which get rerouted to the webapp server on port 8000.
```sudo service nginx reload```