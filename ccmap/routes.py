from flask import current_app as app
from flask import request, render_template
from flask_googlemaps import Map, get_coordinates
from sqlalchemy import and_, or_
from .models import ChildcareCenter

KM_GCS_CONVERSION = 111 #111km = 1 lat/lng
BURNABY_COORDINATES = {'lat': 49.2488, 'lng': -122.9805 }
EXPECTED_MIN_NUM_CENTRES = 20 # low number of centres found may mean location is in another health region

'''
301 - Group Child Care (Under 36 Months)
302 - Group Child Care (30 Months to School Age)
303 - Preschool (30 Months to School Age)
304 - Family Child Care
305 - Group Child Care (School Age)
306 - School Age Care on School Grounds
307 - Recreational Care
308 - Occasional Child Care
310 - Multi-Age Child Care
311 - In-Home Multi-Age Child Care
312 - Child-Minding
    as per: https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/Health-Topics/Child-care/2021_Oct_25_CCFL_Application_for_Licence_Child_Care.pdf?rev=be4dec8a53e34f4cba340eeabe323186
'''
AGE_TO_SERVICE_TYPES = {
    'under_36m': ['301'],
    '30m_to_school_age': ['302','303'],
    'school_age': ['305','306'],
}
MULTIAGE_SERVICE_TYPES = ['304','310','311']

@app.route("/", methods=["GET", "POST"])
def mapview():
    ccmap = None
    search_range_km = 5
    user_coordinates = BURNABY_COORDINATES
    service_types = ['under_36m','30m_to_school_age','school_age']
    if request.method == 'POST':
        user_location = request.form['location'].strip()
        if request.form['search_range_km'].isnumeric():
            search_range_km = int(request.form['search_range_km'])
        if user_location:
            if 'british columbia' not in user_location.lower():
                user_location = user_location + ", British Columbia"
            user_coordinates = get_coordinates(app.config['GOOGLEMAPS_KEY'],user_location)
        if not user_coordinates:
            app.logger.error(f"ERROR: No coordinates found from Google Maps API for location: \
                {user_location}")
            user_coordinates = BURNABY_COORDINATES
        service_types = request.form.getlist('service_types')

    ccmap = Map(
            identifier = "ccmap",
            lat = user_coordinates.get('lat'),
            lng = user_coordinates.get('lng'),
            zoom = 13,
            style = "height:450;width:600;border:0;",
            markers = []
            )
    query = ChildcareCenter.query.filter(and_(
        ChildcareCenter.lat >= user_coordinates.get('lat') - search_range_km/KM_GCS_CONVERSION,
        ChildcareCenter.lat <= user_coordinates.get('lat') + search_range_km/KM_GCS_CONVERSION,
        ChildcareCenter.lng >= user_coordinates.get('lng') - search_range_km/KM_GCS_CONVERSION,
        ChildcareCenter.lng <= user_coordinates.get('lng') + search_range_km/KM_GCS_CONVERSION)
        )

    if not len(service_types):
        query = query.filter(False)
    elif len(service_types) < len(AGE_TO_SERVICE_TYPES):
        conditions = []
        for service_id in MULTIAGE_SERVICE_TYPES:
            conditions.append(ChildcareCenter.info.regexp_match(f'Service Type.*{service_id}'))
        for service in service_types:
            for service_id in AGE_TO_SERVICE_TYPES.get(service):
                conditions.append(ChildcareCenter.info.regexp_match(f'Service Type.*{service_id}'))
        query = query.filter(or_(*conditions))
    centers = query.all()

    for center in centers:
        if center.lat and center.lng:
            center_info = center.info.replace("\n","<br>")
            marker = {
                'lat': center.lat,
                'lng': center.lng,
                'infobox': f"<a href=\"{center.url}\" target=\"_blank\">{center.name}</a><br>\
                    Owner: {center.owner}<br>\
                    Phone: {center.phone_number}<br><br>\
                    {center_info}"
            }
            ccmap.markers.append(marker)

    return render_template('mapview.html',
                            GOOGLE_ANALYTICS_KEY=app.config.get('GOOGLE_ANALYTICS_KEY', None),
                            ccmap=ccmap,
                            centers=centers,
                            search_range_km=search_range_km,
                            service_types=service_types,
                            show_other_health_regions=True if len(centers) <= EXPECTED_MIN_NUM_CENTRES else False)


@app.route("/faq", methods=['GET'])
def faq():
    return render_template('faq.html',
                            GOOGLE_ANALYTICS_KEY=app.config.get('GOOGLE_ANALYTICS_KEY', None))
