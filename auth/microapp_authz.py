# This is a bit of R&D on a possible authorization protocol
# that all microapps would implement.  Each service in a
# microapp could be assigned an authorization URI
# where for each request, the microapp would POST:
#    method,request,referrer and the token passed to it as an argument
# The authorization server would respond with a yes/no
# and possibly some other info, e.g.
#  1. tokens that the microapp could use to defer requests to other microapps
#  2. the ACL that applies, which the microapp could theoretically cache if it wanted
#  
# Currently running `python microapp_authz.py` will run test()
# which tests a run through of the players and what they send to each other
#
# This protocol is a bit more complicated than it could be, because
# I'd like authorization to be potentially stateless.  This is an outline of how it works
#
# 1. Client requests a token from the Auth Server which will expire 'quickly'(< 15 min.)
# 2. Auth Server generates a token, which is an encryption of
#    a. an expiration datetime
#    b. username and group (bit array) info
# 3. With the token, the Client generates its own token
#    a. encryption of the token XOR'd with a client timeout(<30secs) and
#       a hash of the request data using the auth server's public key
# 4. The Client sends the Microapp the request with
#     client token,client timeout, and hash (all as one token separated by ':'s)
# 5. The Microapp passes the token,method,request,referrer to the authz URI
# 6. The Auth Server:
#    a. decrypts the client token with its private key
#    b. XORs off the hash and client timeout ()
#    c. Decrypts the result.  If it's not junk, then the hash and client timeout are confirmed
#    d. Fail if the client timeout or auth timeout have expired
#    e. return to the Microapp whether the user/group data decrypted should allow the request
#
# This is pretty icky, but much of this would be unnecessary in the senario where the Auth
# server is not stateless.  However, the thick client logic should remain to accomodate that
# possibility.
# Please let me know what you think
# (c) Schuyler Duveen 2006
# released under the GNU GPL 2.0

import time
from Crypto.PublicKey import RSA
import Crypto.Util.randpool as rp
from Crypto.Cipher import AES
from base64 import b64encode,b64decode
from Crypto.Hash import MD5


#15 minute timeout
#session is a misnomer, it's more like request timeout
session_timeout = 60*15

#15 seconds for client timeout for client simulation
client_timeout = 15

randfunc = rp.RandomPool().get_bytes

#public key is distributed
key1= RSA.generate(384,randfunc)

#just internal
key2= AES.new(randfunc(32))
#key = RSA.contruct([privateRSA_openssh,'lsh'])



def publickey():
    return key1.publickey()

def get_token(user_group_string):
    timeout = time.time() + session_timeout
    t_string = hex(int(timeout))[2:]
    out_string = (t_string+':'+user_group_string)
    print ('SECRET STRING: '+out_string)
    token = b64encode(key2.encrypt(out_string),'_-')
    print ('TOKEN:  '+token);
    return token

def authorize(crequest):
    """stateless authorization"""
    ctoken, mmss, hash1=crequest.rsplit(':',2)
    client_timeout = list(time.gmtime())
    client_timeout[4] = int(mmss[0:2])
    client_timeout[5] = int(mmss[2:4])
    #timeout should be less than an hour, so we can correct around new day
    if client_timeout < time.mktime(tuple(client_timeout)):
        #fail because we passed the client timeout
        return None
    csecret = key1.decrypt(b64decode(ctoken,'_-'))
    pad = (":%s:%s" % (mmss,hash1)).zfill(44)
    token = XOR(csecret,pad)
    t_string,user_group_string = key2.decrypt(b64decode(token,'_-')).split(':')
    timeout = int(t_string,16)
    if  time.time() > timeout:
        #token timeout
        return None
    print ('SUCCESS: %s %s' % (hex(timeout),user_group_string))
    return real_authorization(user_group_string)

def client_simulation(token):
    """This is really a simulation of the client AND the consumer"""
    message = 'This is my message'
    md5 = MD5.new()
    md5.update(message)
    hash1 = md5.hexdigest()[0:5]
    ctimeout = time.time()+client_timeout
    mmss = time.strftime('%M%S',time.gmtime(ctimeout))

    print ("CLIENT SECRETS: \n  token:%s\n  client timeout:%s\n  hash:%s" % (token,mmss,hash1))
    
    pad = (":%s:%s" % (mmss,hash1)).zfill(44)
    print "PAD: %d, %s" % (len(pad),pad)
    csecret = XOR(token,pad)
    ctoken = b64encode(key1.encrypt(csecret,randfunc(16))[0],'_-')
    print ("CLIENT TOKEN: %s:%s:%s" %(ctoken,mmss,hash1))
    print ("""
    This is passed to the microapp consumer,
    who then sends it to the authorizer.
    The microapp can provide a convention on how the hash 
    is based on the request content and do its own verification
    """)
    return "%s:%s:%s" %(ctoken,mmss,hash1)


def real_authorization(user_group_string):
    return True

def test():
    assert(authorize(client_simulation(get_token('12345670123456701234567'))))
    
def XOR(s1,s2):
    def _xor(c1,c2):
        return chr(ord(c1) ^ ord(c2))
    return ''.join(map(_xor,s1,s2))


test()
