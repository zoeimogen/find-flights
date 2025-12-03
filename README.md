# Direct Flight Finder, with "working hours" filter

A quick script that simplifies finding flights between groups of airports
on a range of dates, with an additional filter for flights departing after
working hours. (Use of UK Bank Holidays for this is currently hard-coded)

Pulls data from Google Flights using the [google-flights Python module](https://pypi.org/project/google-flights/).

## Running with local Python

You will need to install [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/install/).

Creating a virtual environment is optional but recommended. For Windows:
```sh
python -m venv venv
venv\Scripts\activate
```
And for macOS/Linux:
```sh
python3 -m venv .venv
. .venv/bin/activate
```

Getting and running the code is the same regardless of Operating System:
```sh
# Get a copy of the code (This GitHub repo)
git clone https://github.com/zoeimogen/find-flights.git
cd find-flights

# Copy the example formatting
cp -r static-example static

# Install dependencies. On Windows systems, or if venv is not installed, see
# https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Run
python ./flight_cli.py -h # Shows help
python ./flight_cli.py LON CDG,ORY 2025-12-01 2025-12-07 --no-working-hours

# Alternatively, start a web server available on http://localhost:5001/
python ./flight_server.py
```

## Running with Docker

If you prefer [Docker](https://www.docker.com/products/docker-desktop/). This will start a web server that you can visit at [http://localhost:5001/](http://localhost:5001/).

```sh
docker build . -t find-flights
docker run -d find-flights
```

Or using Docker Compose:

```sh
docker compose up -d --build
```
