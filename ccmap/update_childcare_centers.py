#!usr/bin/env python3

"""
Update Childcare Centers - Fraser Health
~~~~~~~~~~~~~~~~~~~~~~~~~

This script scrapes childcare facility data from Fraser Health website
and imports into database
"""
import re
import click
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from flask import current_app as app
from flask.cli import with_appcontext
from .util import requests_retry_session
from .models import ChildcareCenter, db

CITIES = [
        'Abbotsford',
        'Agassiz',
        'Aldergrove',
        'Anmore',
        'Burnaby',
        'Chilliwack',
        'Coquitlam',
        'Cultus Lake',
        'Delta',
        'Fort Langley',
        'Harrison Hot Springs',
        'Hope',
        'Langley',
        'Langley City',
        'Langley Township',
        'Maple Ridge',
        'Mission',
        'New Westminster',
        'Pitt Meadows',
        'Port Coquitlam',
        'Port Moody',
        'Rosedale',
        'Surrey',
        'Tsawwassen',
        'White Rock',
        'Yarrow',
        ]
PARSER = 'html.parser'


def get_childcare_centers(query='burnaby'):
    """ Gets a list of childcare centers from Fraser Health
    :param query: (optional) Query to filter the results by during search
    """
    base_url = "https://healthspace.ca"
    url = f"{base_url}/Clients/FHA/FHA_Website.nsf/CCFL-Child-List-All?SearchView"
    payload = {
        'SearchWV': 1,
        'SearchFuzzy': 1,
        'Query': query
    }

    response = requests_retry_session().post(url, data=payload, timeout=10)
    if response.status_code != 200:
        raise RequestException
    data = response.content

    soup = BeautifulSoup(data, PARSER)

    childcare_centers = []
    for row in soup.find_all('tr')[1:]:
        url = base_url + row.contents[0].a['href']
        name = row.contents[0].text.strip()
        phone = row.contents[1].text.strip() if len(row.contents) > 1 else None
        owner = row.contents[2].text.strip() if len(row.contents) > 2 else None

        center = {
            'url': url,
            'name': name,
        }
        if phone:
            center['phone'] = phone
        if owner:
            center['owner'] = owner
        center['address'] = get_address(center.get('url'))
        center['info'] = get_facility_details(center.get('url'))
        app.logger.debug("Adding details: %s, %s, %s, %s, %s",
            center.get('url'), center.get('name'), center.get('phone'),
            center.get('owner'), center.get('address'))
        childcare_centers.append(center)

    return childcare_centers


def get_address(url):
    """ Parse url to get facility address
    :param url: Fraser Health facility details page
    """
    address = None

    response = requests_retry_session().get(url, timeout=10)
    if response.status_code != 200:
        raise RequestException
    data = response.content
    soup = BeautifulSoup(data, PARSER)

    heading = soup.find("b", string=re.compile('Facility Location'))
    lines = str(heading.parent).splitlines()
    for idx, line in enumerate(lines):
        if 'Facility Location' in line:
            address = lines[idx+1].strip()
            app.logger.debug("Found address: %s", address)

    return address


def get_facility_details(url):
    """ Parse url to get facility details
    :param url: Fraser Health facility details page
    """
    facility_details = None

    response = requests_retry_session().get(url, timeout=10)
    if response.status_code != 200:
        raise RequestException
    data = response.content
    soup = BeautifulSoup(data, 'html.parser')

    header = soup.find("tr", string=re.compile('Facility Information'))
    cells = header.find_next_siblings("tr")
    for cell in cells:
        # owner already fetched from list page
        if not cell.string.startswith('Licensee/Owner:'):
            facility_details = cell.string if not facility_details \
                else facility_details + '\n' + cell.string
    app.logger.debug("Facility information: %s", facility_details)

    return facility_details


def update_childcare_centers(childcare_centers):
    """ Update Childcare Centers in the database
    :param childcare_centers: List of childcare centers to update
    """

    if not childcare_centers:
        app.logger.debug('No childcare centers updated')
    else:
        for center in childcare_centers:
            rows = ChildcareCenter.query.filter_by(
                        name=center.get('name'),
                        url=center.get('url')
                    ).count()
            if rows == 0:
                center = ChildcareCenter(name=center.get('name'),
                                         address=center.get('address'),
                                         phone_number=center.get('phone'),
                                         owner=center.get('owner'),
                                         url=center.get('url'),
                                         info=center.get('info'))
                db.session.add(center)
                db.session.commit()
                app.logger.debug('Insert center: %s', center)
            else:
                c_row = ChildcareCenter.query.filter_by(
                    name=center.get('name'),url=center.get('url')).first()
                c_row.address = center.get('address')
                c_row.phone_number = center.get('phone')
                c_row.owner = center.get('owner')
                c_row.info = center.get('info')
                db.session.commit()
                app.logger.debug('Updated center: %s', center)


@click.command('update-centers', help="Updates childcare centers. Default updates all")
@click.option('--queries', help='Comma-delimited list of queries to update centers for. '
              '(eg. burnaby,"Cozy Kids Daycare")')
@with_appcontext
def update_centers_command(queries):
    """Update child-care centers in database"""
    if queries:
        app.logger.debug('List of queries provided: %s', queries)
        queries = queries.split(',')
    else:
        queries = CITIES
        app.logger.debug('Updating centers in all cities')

    for query in queries:
        app.logger.debug('Updating centers in list: %s', query)
        childcare_centers = get_childcare_centers(query=query)
        update_childcare_centers(childcare_centers)

def init_app(application):
    application.cli.add_command(update_centers_command)
