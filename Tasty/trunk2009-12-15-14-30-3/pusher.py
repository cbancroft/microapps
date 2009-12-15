
def run_unit_tests(pusher):
    codir = pusher.checkout_dir()
    (out,err) = pusher.execute("pushd %s && python nosetests && popd" % codir)
    return ("FAILED" not in out,out,err)

def post_rsync(pusher):
    """ need to restart apache2 """
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/rm","/var/www/tasty/eggs/psycopg2-2.0.6-py2.5-linux-x86_64.egg"])
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/var/www/tasty/init25.sh","/var/www/tasty/"])
    (out2,err2)= pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/ln","-s","/usr/lib/python2.5/site-packages/mx/","/var/www/tasty/working-env/lib/python2.5/"])
    (out3,err3)= pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/ln","-s","/usr/lib/python2.5/site-packages/psycopg2/","/var/www/tasty/working-env/lib/python2.5/"])    
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","sudo","/usr/bin/supervisorctl","restart","tasty"])
    return (True,out,err)
