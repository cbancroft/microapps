#!/bin/bash
export PYTHON_EGG_CACHE=/var/www/nqdq/.python-eggs
cd $1
source working-env/bin/activate
exec python start-nqdq.py $2

