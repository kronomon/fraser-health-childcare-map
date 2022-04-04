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
