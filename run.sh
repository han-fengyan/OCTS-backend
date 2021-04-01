#!/bin/sh
python manage.py makemigrations
python manage.py makemigrations goods
python manage.py migrate
python manage.py runserver 0.0.0.0:80

