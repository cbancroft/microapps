#!/bin/bash
cd $1
rm -rf working-env
python workingenv.py working-env
source working-env/bin/activate
easy_install -H None -f eggs eggs/*.egg
ln -s /usr/lib/python2.5/site-packages/PIL working-env/lib/python2.5/
ln -s /usr/lib/python2.5/site-packages/PIL.pth working-env/lib/python2.5/
