import os,sys

dir = os.path.dirname(__file__)
f = open(os.path.join(dir,"prodpath.py"),"w")
f.write("import sys\n")
f.write("sys.path = " + str(sys.path))

f.close()

