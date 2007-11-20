import selector
from pprint import pformat
import Image, cStringIO
import cgi
from imageuploader import Uploader
from simplejson import dumps as jsonify

def partition(piece,total):
    if piece >= total:
        yield (0,total)
        return
    lower = 0
    upper = piece

    while upper < total:
        yield (lower,upper)
        lower = upper + 1
        upper += piece

    yield (lower,total)


def tile(image,size=300):
    (width,height) = image.size
    output = []
    for i,(y1,y2) in enumerate(partition(size,height)):
        row = []
        for j,(x1,x2) in enumerate(partition(size,width)):
            c = image.crop((x1,y1,x2,y2))
            c.format = image.format
            row.append(dict(image=c, width=x2 - x1, height=y2-y1))
        output.append(row)
    return output

    

def upload(parts,filename,upload_uri=""):
    u = Uploader()
    if upload_uri != "":
        u = Uploader(upload_uri)
    (base,ext) = filename.rsplit('.')
    for i,row in enumerate(parts):
        for j,d in enumerate(row):
            img = cStringIO.StringIO()
            d['image'].save(img,d['image'].format)
            d['uri'] = u.upload("%s_%d_%d.%s" % (base,i,j,ext),
                                img.getvalue())
            del d['image']
    return parts



class InputProcessed(object):
    def read(self, *args):
        raise EOFError(
            'The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read

def cgi_get(fs,key,default):
    """ cgi fieldstorage is broken. it pretends to be a dict but doesn't implement
    a get() method. and the thing it returns isn't really a value. :( """
    try:
        return fs[key].file.read()
    except:
        return default


class Root:
    def get_post_form(self,environ):
        input = environ['wsgi.input']
        post_form = environ.get('wsgi.post_form')
        if (post_form is not None and post_form[0] is input):
            return post_form[2]
        fs = cgi.FieldStorage(fp=input,
                              environ=environ,
                              keep_blank_values=1)
        new_input = InputProcessed()
        post_form = (new_input, input, fs)
        environ['wsgi.post_form'] = post_form
        environ['wsgi.input'] = new_input
        return fs

    
    def __call__(self, environ, start_response):
        post_data = self.get_post_form(environ)
        size = 100
        image = post_data['image']
        size = cgi_get(post_data,'size',300)
        upload_uri = cgi_get(post_data,'upload_uri','')
        filename = image.filename
        im = Image.open(image.file)

        parts = tile(im,int(size))
        tiles = upload(parts,filename,upload_uri)

        content_type = image.headers.get('Content-Type','image/jpeg')
        start_response("200 OK", [('Content-Type','application/javascript')])
        yield jsonify(dict(tiles=tiles))
        
urls = selector.Selector()
urls.add('/[{action}]', _ANY_=Root())


