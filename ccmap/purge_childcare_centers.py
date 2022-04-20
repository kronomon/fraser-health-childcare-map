#!usr/bin/env python3

"""
Purge Childcare Centers
~~~~~~~~~~~~~~~~~~~~~~~~~

Purges stale childcare centers in the database
"""
import click
from flask import current_app as app
from flask.cli import with_appcontext
from .util import requests_retry_session
from .models import ChildcareCenter, db


def purge_stale_childcare_centers():
    """ Remove stale Childcare Centers in the database
    """
    num_removed_centers = 0
    childcare_centers = ChildcareCenter.query.all()
    for center in childcare_centers:
        if center.url:
            response = requests_retry_session().get(center.url, timeout=10)
            if response.status_code == 404:
                app.logger.error(f"404 Error found for {center.url}")
                db.session.delete(center)
                db.session.commit()
                app.logger.debug(f"Removed childcare center: {center}")
                num_removed_centers += 1

    return num_removed_centers


@click.command('purge-centers', help="Purge stale childcare centers")
@click.option('--center_name', help='Name of center to remove')
@click.option('--center_id', help='ID of center to remove')
@with_appcontext
def purge_centers_command(center_name, center_id):
    """Remove stale child-care centers in database"""
    center_to_remove = None
    num_removed_centers = 0

    if center_name:
        app.logger.debug(f'Purge centers called with center name: {center_name}')
        if ChildcareCenter.query.filter_by(name=center_name).count() > 1:
            raise ValueError(f"More than one center named {center_name}. Please specify center_id instead")
        center_to_remove = ChildcareCenter.query.filter_by(name=center_name).first()
    elif center_id:
        app.logger.debug(f'Purge centers called with center id: {center_id}')
        center_to_remove = ChildcareCenter.query.filter_by(id=center_id).first()
    else:
        app.logger.debug('Purging stale childcare centers start')
        num_removed_centers = purge_stale_childcare_centers()
        app.logger.debug('Purging stale childcare centers complete')

    if center_to_remove:
        db.session.delete(center_to_remove)
        db.session.commit()
        app.logger.debug(f"Removed childcare center: {center_to_remove}")
        num_removed_centers += 1

    app.logger.debug(f"Number of centers removed: {num_removed_centers}")


def init_app(application):
    application.cli.add_command(purge_centers_command)
