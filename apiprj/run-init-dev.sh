#!/bin/bash

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

python manage.py makemigrations
python manage.py migrate

echo yes | python manage.py collectstatic

python manage.py createsuperuser

gunicorn main.wsgi:application --bind 0.0.0.0:8000
