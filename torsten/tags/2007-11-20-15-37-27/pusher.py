#def run_unit_tests(pusher):
#    codir = pusher.checkout_dir()
#    (out,err) = pusher.execute("pushd %s && nosetests && popd" % codir)
#    return ("OK" in err,out,err)

def post_rsync(pusher):
    """ need to restart apache2 """
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/var/www/torsten/init.sh","/var/www/torsten/"])
    (out2,err2) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","sudo","/usr/bin/supervisorctl","restart","torsten"])
    out += out2
    err += err2
    return (True,out,err)  
