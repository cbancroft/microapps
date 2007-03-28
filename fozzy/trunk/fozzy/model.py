from sqlobject import *
from sqlobject.converters import sqlrepr
from turbogears.database import PackageHub

hub = PackageHub("fozzy")
__connection__ = hub

soClasses = ['Application', 'Document']

class Application(SQLObject):
    name = UnicodeCol(length=256,alternateID=True)
    docs = MultipleJoin('Document')

    def search(self,q):
        sql = """select key,headline(body,q),rank(vectors,q)
        from document, to_tsquery(%s) as q where vectors @@ q
        AND application_id = %d order by rank(vectors,q) DESC""" % \
        (sqlrepr(q,"postgres").encode('utf8'),self.id)
        results = self._connection.queryAll(sql)
        return results

class Document(SQLObject):
    application = ForeignKey('Application',cascade=True)
    key         = UnicodeCol(length=1024)
    body        = UnicodeCol(default="")

    def update(self,text):
        self.body = text
        self._connection.query("""update document set vectors = to_tsvector(body) where id = %d""" % self.id)


