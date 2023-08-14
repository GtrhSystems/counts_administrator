#!/bin/bash

NAME="Administrador_de_cuentas"  # Name of the application
DJANGODIR=/home/counts_adminitration  # Django project directory
DJANGOENVDIR=$DJANGODIR/env  # Django project env
DJANGO_SETTINGS_MODULE=count_admin_project.settings
DJANGO_WSGI_MODULE=count_admin_project.wsgi
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
#export PYTHONPATH=$DJANGODIR:$PYTHONPATH

echo "Starting $NAME as `whoami`"
NUM_WORKERS=5
# Activate the virtual environment

. $DJANGOENVDIR/bin/activate
#source /home/ubuntu/webapp/myproject/proj/.env
#export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start gunicorn
cd $DJANGODIR
exec gunicorn --name $NAME --workers $NUM_WORKERS --bind 0.0.0.0:8000 ${DJANGO_WSGI_MODULE}:application
