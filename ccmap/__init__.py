import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_googlemaps import GoogleMaps

'''
Flask web application to search for childcare centers near an area in Metro Vancouver, BC, Canada.
Contains a map-view to show centers near a specified location
'''

db = SQLAlchemy()
migrate = Migrate()
logging.basicConfig(filename='logs/ccmap.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s: %(message)s')
# TODO: Change to file config

def create_app(test_config=None):
    """Construct the core application"""
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_pyfile("config.py")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{app.instance_path}/\
        {app.config['SQLALCHEMY_DATABASE_NAME']}"
    from . import scraper, geocode
    db.init_app(app)
    scraper.init_app(app)
    geocode.init_app(app)
    migrate.init_app(app, db)
    GoogleMaps(app)

    # reduce large log streams when debugging
    wz_log = logging.getLogger('werkzeug')
    wz_log.setLevel(logging.ERROR)
    wd_log = logging.getLogger('watchdog')
    wd_log.setLevel(logging.ERROR)

    with app.app_context():
        from . import routes

        db.create_all()
        return app
