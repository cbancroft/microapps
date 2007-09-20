
def run_unit_tests(pusher):
    codir = pusher.checkout_dir()
    (out,err) = pusher.execute("pushd %s && nosetests && popd" % codir)
    return ("Failed" not in err,out,err)

def post_rsync(pusher):
    """ need to restart apache2 """
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/rm","/var/www/gossip/eggs/psycopg2-2.0.6-py2.5-linux-x86_64.egg"])
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/var/www/gossip/init.sh","/var/www/gossip/"])
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/ln","-s","/usr/lib/python2.5/site-packages/mx/","/var/www/gossip/working-env/lib/python2.5/"])
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/ln","-s","/usr/lib/python2.5/site-packages/psycopg2/","/var/www/gossip/working-env/lib/python2.5/"])    
    (out2,err2) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","sudo","/usr/bin/supervisorctl","restart","gossip"])
    out += out2
    err += err2
    return (True,out,err)  
