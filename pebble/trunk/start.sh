#!/bin/bash
export PYTHON_EGG_CACHE=/var/www/pebble/.python-eggs
cd $1
source working-env/bin/activate
exec python start-pebble.py $2
