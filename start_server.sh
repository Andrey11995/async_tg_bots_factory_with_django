#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

export DJANGO_SETTINGS_MODULE=bots_factory.settings

python manage.py migrate --noinput

python manage.py collectstatic --noinput

gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 bots_factory.asgi:application
