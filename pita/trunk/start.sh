#!/bin/bash
cd $1
source working-env/bin/activate
exec python start-pita.py $2 

