.PHONY: web
web:
	FLASK_APP=ccmap \
	FLASK_ENV=development \
	flask run
