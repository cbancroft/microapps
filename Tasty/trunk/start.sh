#!/bin/bash
cd $1
source working-env/bin/activate
exec python start-tasty.py $2

