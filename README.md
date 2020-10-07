# GOA - Online. "The Game Of Amazons"

## Introduction

This is the repository for the web application: Game of Amazons. Inspired by the amazing numberphile video with mathematician 
Elwyn Berlekamp. [video](https://www.youtube.com/watch?v=kjSOSeRZVNg)

![Erwyn](amazons/static/img/elwynamazons.jpg)

## Development

The webapplication could be run locally to play games against someone else on the same screen, but we're planning to bring it live very soon.

To start the Flask web application in development mode, run the following with docker installed.

```sh
git clone https://github.com/Aschwins/webapp_amazons/master

cp .env.example .env

# Create database
docker-compose -f docker-compose.dev.yml up -d --build
```

Happy hunting!

## Production

https://game-of-amazons.org

For the production version of the web application we use a linux server in Amazon Lightsail.

```sh
git clone https://github.com/Aschwins/webapp_amazons/master

cp .env.example .env

# Create database
docker-compose up -d --build

source install.sh
```

### Nginx
We use nginx as a reverse proxy. The config can be found at `/etc/nginx/sites-enabled/amazons`. All requests to http 
(port 80) get rerouted to https (443), which get rerouted to the webapp server on port 8000.
```sudo service nginx reload```


