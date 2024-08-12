#!/bin/bash
NAME="Administrador_de_cuentas"                                  # Name of the application
NUM_WORKERS=49
DJANGODIR=/home/counts_administrator            # Django project directory
DJANGO_SETTINGS_MODULE=count_admin_project.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=count_admin_project.wsgi
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
echo "Starting $NAME as `whoami`"
# Activate the virtual environment
. $DJANGODIR/env/bin/activate
#export PYTHONPATH=$DJANGODIR:$PYTHONPATH
cd $DJANGODIR
#exec gunicorn ${DJANGO_WSGI_MODULE}:application --name $NAME  --threads=1 --workers $NUM_WORKERS --bind 0.0.0.0:8001
exec gunicorn ${DJANGO_WSGI_MODULE}:application --name $NAME --workers $NUM_WORKERS  --bind 0.0.0.0:8001
