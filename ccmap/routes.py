from flask import current_app as app
from flask import request, render_template
from flask_googlemaps import Map, get_coordinates
from sqlalchemy import and_
from .models import ChildcareCenter

KM_GCS_CONVERSION = 111 #111km = 1 lat/lng
BURNABY_COORDINATES = {'lat': 49.2488, 'lng': -122.9805 }


@app.route("/", methods=["GET", "POST"])
def mapview():
    ccmap = None
    search_range_km = 5
    user_coordinates = BURNABY_COORDINATES
    app.logger.debug("MAP VIEW REQUESTED")
    if request.method == 'POST':
        user_location = request.form['location'].strip()
        if request.form['search_range_km'].isnumeric():
            search_range_km = int(request.form['search_range_km'])
        if user_location:
            if 'british columbia' not in user_location.lower():
                user_location = user_location + " British Columbia"
            user_coordinates = get_coordinates(app.config['GOOGLEMAPS_KEY'],user_location)
        if not user_coordinates:
            app.logger.error(f"ERROR: No coordinates found from Google Maps API for location: \
                {user_location}")
            user_coordinates = BURNABY_COORDINATES

    ccmap = Map(
            identifier = "ccmap",
            lat = user_coordinates.get('lat'),
            lng = user_coordinates.get('lng'),
            zoom = 13,
            style = "border:0",
            markers = []
            )
    centers = ChildcareCenter.query.filter(and_(
        ChildcareCenter.lat >= user_coordinates.get('lat') - search_range_km/KM_GCS_CONVERSION,
        ChildcareCenter.lat <= user_coordinates.get('lat') + search_range_km/KM_GCS_CONVERSION,
        ChildcareCenter.lng >= user_coordinates.get('lng') - search_range_km/KM_GCS_CONVERSION,
        ChildcareCenter.lng <= user_coordinates.get('lng') + search_range_km/KM_GCS_CONVERSION)
        ).all()

    for center in centers:
        if center.lat and center.lng:
            center_info = center.info.replace("\n","<br>")
            marker = {
                'lat': center.lat,
                'lng': center.lng,
                'infobox': f"<a href=\"{center.url}\">{center.name}</a><br>\
                    Owner: {center.owner}<br>\
                    Phone: {center.phone_number}<br><br>\
                    {center_info}"
            }
            ccmap.markers.append(marker)

    return render_template('mapview.html',
                            ccmap=ccmap,
                            centers=centers,
                            search_range_km=search_range_km)


@app.route("/faq", methods=['GET'])
def faq():
    return render_template('faq.html')
