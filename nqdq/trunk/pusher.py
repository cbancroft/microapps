#def run_unit_tests(pusher):
#    codir = pusher.checkout_dir()
#    (out,err) = pusher.execute("pushd %s && nosetests && popd" % codir)
#    return ("OK" in err,out,err)

def post_rsync(pusher):
    (out,err) = pusher.execute(["ssh","frink.ccnmtl.columbia.edu","/var/www/nqdq/init.sh","/var/www/nqdq/"])
    (out2,err2) = pusher.execute(["ssh","frink.ccnmtl.columbia.edu","sudo","/usr/local/bin/supervisorctl","restart","nqdq"])
    out += out2
    err += err2
    return (True,out,err)  
