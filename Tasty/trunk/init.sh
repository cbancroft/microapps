#!/bin/bash
cd $1
rm -rf working-env
python workingenv.py -r requirements.txt working-env
