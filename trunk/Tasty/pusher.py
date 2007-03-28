
def run_unit_tests(pusher):
    codir = pusher.checkout_dir()
    (out,err) = pusher.execute("pushd %s && python nosetests && popd" % codir)
    return ("FAILED" not in out,out,err)

def post_rsync(pusher):
    """ need to restart apache2 """
    (out,err) = pusher.execute(["ssh","frink.ccnmtl.columbia.edu","/var/www/tasty/init.sh","/var/www/tasty/"])
    (out,err) = pusher.execute(["ssh","frink.ccnmtl.columbia.edu","sudo","/usr/local/bin/supervisorctl","restart","tasty"])
    return (True,out,err)
