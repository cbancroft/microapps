
def run_unit_tests(pusher):
    codir = pusher.checkout_dir()
    (out,err) = pusher.execute("pushd %s && python nosetests && popd" % codir)
    return ("FAILED" not in out,out,err)

def post_rsync(pusher):
    """ restart apache2 """
    (out5,err5) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/rm","/var/www/pita/eggs/psycopg2-2.0.6-py2.5-linux-x86_64.egg"])
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/var/www/pita/init.sh","/var/www/pita/"])
    (out3,err3) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/ln","-s","/usr/lib/python2.5/site-packages/mx/","/var/www/pita/working-env/lib/python2.5/"])
    (out4,err4) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/ln","-s","/usr/lib/python2.5/site-packages/psycopg2/","/var/www/pita/working-env/lib/python2.5/"])    
    (out2,err2) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","sudo","/usr/bin/supervisorctl","restart","pita"])
    out += out5 + out4 + out3 + out2
    err += err5 + err4 + err3 + err2
    return (True,out,err)  
