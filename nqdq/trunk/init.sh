#!/bin/bash
cd $1
rm -rf working-env
python workingenv.py -r requirements.txt working-env
source working-env/bin/activate
easy_install http://kang.ccnmtl.columbia.edu/eggs/PIL-1.1.5-py2.4-linux-i686.egg
