#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
mkdir -p staticfiles_build
cp -r staticfiles/* staticfiles_build/ 2>/dev/null || true
