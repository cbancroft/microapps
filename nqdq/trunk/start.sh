#!/bin/bash
cd $1
source working-env/bin/activate
exec python nqdq_start.py $2 

