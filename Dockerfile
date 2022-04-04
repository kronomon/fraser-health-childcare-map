FROM python:3

WORKDIR /ccmap

RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev

COPY ./requirements.txt /ccmap/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# https://github.com/flask-extensions/Flask-GoogleMaps/issues/145
# after issue resolved, add back flask-googlemaps to requirements.txt
RUN python3 -m pip install https://github.com/flask-extensions/Flask-GoogleMaps/archive/refs/tags/0.4.1.1.tar.gz

COPY . /ccmap

#ENTRYPOINT [ "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "ccmap:create_app()"]
CMD [ "./run.sh" ]
