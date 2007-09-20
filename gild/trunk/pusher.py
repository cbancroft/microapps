#def run_unit_tests(pusher):
#    codir = pusher.checkout_dir()
#    (out,err) = pusher.execute("pushd %s && python setup.py testgears && popd" % codir)
#    return ("FAILED" not in out,out,err)

def post_rsync(pusher):
    """ need to restart apache2 """
    (out,err) = pusher.execute(["ssh","frink.ccnmtl.columbia.edu","/var/www/gild/init.sh","/var/www/gild/"])
    (out2,err2) = pusher.execute(["ssh","frink.ccnmtl.columbia.edu","sudo","/usr/local/bin/supervisorctl","restart","gild"])
    out += out2
    err += err2
    return (True,out,err)
