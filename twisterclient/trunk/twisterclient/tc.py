# Copyright (c) 2007, Columbia Center For New Media Teaching And Learning (CCNMTL)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the CCNMTL nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY CCNMTL ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL CCNMTL BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
twister client

a convenient python library for accessing a twister server
"""

from restclient import GET
from simplejson import loads as json_to_py

class TwisterResponse:
    """ The response object converted from json back to a
    more convenient python object. """
    def __init__(self,json):
        self.json   = json
        d           = json_to_py(json)
        self.seed   = d['seed']
        self.values = d['values']
        self.params = d['params']
        self.n      = d['n']
        self.next_seed = d['next_seed']

def rest(func):
    """ decorator that does most of the heavy lifting."""
    
    def wrapper(*args,**kwargs):
        self = args[0]
        seed = kwargs.get('seed',None)
        # handle seed chaining
        if seed is None and self.chain:
            seed = self.next_seed
        n    = kwargs.get('n',1)
        (d,paramlist) = func(self,**kwargs)
        params = slice_dict(kwargs,paramlist)
        url = self.base + d
        if seed is not None:
            params['seed'] = seed
        if 'lambd' in params:
            # handle the special case (damn keywords)
            params['lambda'] = params['lambd']
            del params['lambd']
        params['n'] = n
        r = GET(url,params=params)
        tr = TwisterResponse(r)
        self.next_seed = tr.next_seed
        return tr
    return wrapper

def slice_dict(d,keys):
    """ makes a new dictionary using only the keys
    specified in keys """
    n = d.fromkeys(keys)
    for k in n.keys():
        n[k] = d[k]
    return n

class TwisterClient:
    def __init__(self,base=None,chain=False):
        self.base = base
        self.chain = chain
        self.next_seed = None

    @rest
    def beta(self,**kwargs):
        return ('beta',['alpha','beta'])

    @rest
    def expo(self,**kwargs):
        return ('expo',['lambd'])

    @rest
    def gamma(self,**kwargs):
        return ('gamma',['alpha','beta'])

    @rest
    def gauss(self,**kwargs):
        return ('gauss',['mu','sigma'])

    @rest
    def lognormal(self,**kwargs):
        return ('lognormal',['mu','sigma'])

    @rest
    def pareto(self,**kwargs):
        return ('pareto',['alpha'])

    @rest
    def uniform(self,**kwargs):
        return ('uniform',['a','b'])

    @rest
    def randint(self,**kwargs):
        return ('randint',['a','b'])

    @rest
    def vormises(self,**kwargs):
        return ('vormises',['mu','kappa'])

    @rest
    def weibull(self,**kwargs):
        return ('weibull',['alpha','beta'])

