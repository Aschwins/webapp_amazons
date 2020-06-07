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

# Create a virtual environment
virtualenv -p python3 venv
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
python3 setup.py

# Run the application
python src/amazons/app.py
```

Happy hunting!
