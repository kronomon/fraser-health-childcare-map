# Fraser Health Childcare Map
Childcare facilities map for Fraser Health district in Vancouver, BC.

## Description
This project is a web application to display all licensed childcare facilities in a map view.

The motivation behind this project is that we wanted to have an easy way to view search for daycare facilities near us. The Fraser Health website did not have a map-view and only filtered location by cities.

Information on Google Maps can be sparse and some facilities are not registered with Google.

Data is pulled from [Fraser Health's child-care facilities website](https://www.healthspace.ca/Clients/FHA/FHA_Website.nsf/CCFL-Child)

## Usage

Run the webapp locally in development mode:
```
env FLASK_APP=ccmap
env FLASK_ENVIRONMENT=development
flask run
```

Run via Docker on port 8000:
```
docker build -t ccmap .
docker run --name ccmap -dp 8000:8000 -v "$(pwd)"/instance:/ccmap/instance -v "$(pwd)"/logs:/ccmap/logs ccmap
```

## Deployment
Outside of Docker (Python3.6+):
```
# create virtual env
python -m venv <venv-path>
source <venv-path>/bin/activate

# install requirements
pip install -r requirements.txt
python -m pip install https://github.com/flask-extensions/Flask-GoogleMaps/archive/refs/tags/0.4.1.1.tar.gz # remove after https://github.com/flask-extensions/Flask-GoogleMaps/issues/145 bugfix is released

# update configs
cp config.py instance/config.py # replace GOOGLEMAPS_KEY with your API key

# initialize db
flask db init
flask db migrate -m 'Initial migration'

# Deployment options: https://flask.palletsprojects.com/en/2.1.x/deploying/
./run.sh # ex: uses gunicorn option

# Website should now be viewable on browser with an empty map

# populate db
flask upddate-centers
flask geocode

# Website should now show markers of childcare centers
```