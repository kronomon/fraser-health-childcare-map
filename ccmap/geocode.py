#!usr/bin/env python3

"""
Geocoder
~~~~~~~~

Updates longitude/latitude coordinates for childcare centers from their addresses
"""
import json
import urllib
import click
from flask import current_app as app
from flask.cli import with_appcontext
from requests.exceptions import RequestException
from sqlalchemy import or_

from .models import ChildcareCenter, db
from .util import requests_retry_session

def get_coordinates(address):
    '''
    Returns long/lat coordinates from a given address string
    '''
    lat = None
    lng = None
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": urllib.parse.quote_plus(address),
        "key": app.config['GOOGLEMAPS_KEY']
    }

    app.logger.debug(f"Sending request: {url} {params}")
    response = requests_retry_session().get(url, params=params)
    if response.status_code != 200:
        raise RequestException(f"Failed API request: {response.status_code} {response.content}")
    data = response.content

    try:
        json_data = json.loads(data)
        if json_data.get('status') != "OK":
            app.logger.error(f'API request not OK: {json_data}')
        elif json_data.get('results'):
            lat = json_data.get('results')[0].get('geometry',{}).get('location',{}).get('lat')
            lng = json_data.get('results')[0].get('geometry',{}).get('location',{}).get('lng')
            app.logger.debug(f'Location for {address}: {lat} lat, {lng} lng')
        else:
            app.logger.error(f'No results found for address: {address}')
    except Exception as err:
        raise ValueError(f"Error parsing json response: {err} {data}") from err

    return (lng, lat)

@click.command('geocode')
@click.option('--center_name', help='Name of center to update')
@click.option('--center_id', help='ID of center to update')
@with_appcontext
def geocode_command(center_name, center_id):
    '''
    Updates geocodes for centers in the database.
    Default updates all centers without existing geocodes
    '''
    centers_to_update = None

    app.logger.debug('Updating coordinates start')
    if center_name:
        centers_to_update = ChildcareCenter.query.filter_by(name=center_name).all()
    elif center_id:
        centers_to_update = ChildcareCenter.query.filter_by(id=center_id).all()
    else:
        centers_to_update = ChildcareCenter.query.filter(
            or_(ChildcareCenter.lat is not None, ChildcareCenter.lng is not None)).all()

    for center in centers_to_update:
        app.logger.debug(f"Updating: {center}")
        lng, lat = get_coordinates(center.address)
        if not lng or not lat:
            app.logger.error(f"No coordinates found for {center.name}, {center.address}")
            continue
        if center.lat == lat and center.lng == lng:
            app.logger.debug(f'{center.name} has latest coordinates')
        else:
            center.lat = lat
            center.lng = lng
            db.session.commit()
            app.logger.debug(f'Updated center: {center.name} at {center.address} \
                with lat: {lat}, lng: {lng}')

    app.logger.debug('Updating coordinates complete')

def init_app(application):
    application.cli.add_command(geocode_command)
