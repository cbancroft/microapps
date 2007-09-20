#!/bin/bash
export PYTHON_EGG_CACHE=/var/www/gossip/.python-eggs
cd $1
source working-env/bin/activate
exec python start-gossip.py $2
