#!/bin/bash
export PYTHON_EGG_CACHE=/var/www/gild/.python-eggs
cd $1
source working-env/bin/activate
exec python start-gild.py $2
