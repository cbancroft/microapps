#
import dispatch

"""
[base_channel]
ned.async=ned:async_dispatch
ned.sync=ned:sync_dispatch

[ned.sync]
log_sync=ned:log
reponse_dispatch=ned:response_dispatch
pony=ned:pony 

[response_channel]
ned.response=ned:response_channel

[pony]
predicate="request.environ['PATH_INFO']=='/pony/'"

[ned.async]
log_async=ned:log
sys_beep=ned:sys_beep "request.environ['PATH_INFO']=='/pony/'"
ping_url=ned:ping_url "request.environ['PATH_INFO']=='/pony/'"

[ping_url]
predicate="request.environ['PATH_INFO']=='/pony/'"
url=http://mytestservice
add_header="X-annoy"

[sys_beep]
predicate="request.environ['PATH_INFO']=='/pony/'"

"""

import logging
logger = logging.getLogger('ned.fake')

@dispatch.generic()
def sync_dispatch(request):
    """generic for dispatch"""

@dispatch.generic()
def async_dispatch(request):
    """do async dispatch"""

_response_channel=[]
def response_dispatch(request):
    response = make_request(request)
    for func in _response_channel:
        func(request, response)
    return response

_sync_defaults=[]
@sync_dispatch.when(dispatch.DEFAULT)
def run_non_predicated_functions(request):
    for func in _syn_defaults:
        func(request)

def log(request, dispatch=None):
    logger.info("%s %s" %(request, dispatch))

def is_factory(func):
    func.is_factory=True
    return func

@ned.is_factory
def pony(request):
    return "I'm a pony!"

def prep_func(channel, func, predicate=None, **kwargs):
    if predicate is None:
        _sync_defaults.append(func)
        return
    if func.is_factory:
        return channel.when(predicate)(func(**kwargs))
    return channel.when(predicate)(func)

_base_channel = []
def notify(request):
    for channel in _base_channel:
        channel(request)
