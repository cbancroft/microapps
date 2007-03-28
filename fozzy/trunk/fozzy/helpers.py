from fozzy.model import *
import os
from turbogears.database import PackageHub

hub = PackageHub("fozzy")
__connection__ = hub

def create_tables():
    Application.createTable(ifNotExists=True)
    Document.createTable(ifNotExists=True)

#def setup():
#    create_tables()
#    setup_tsearch2()

def dropTables():
    Document.dropTable(ifExists=True)
    Application.dropTable(ifExists=True)

def setup_tsearch2():
    dbname = Application._connection.sqlmeta.db
    dbuser = Application._connection.sqlmeta.user
    os.system("psql %s -U %s < fozzy/sql/tsearch2.sql" % (dbname,dbuser))
    Document._connection.query("""alter table document add column vectors tsvector""")
    Document._connection.query("""create index body_index on document using gist(vectors)""")
    Document._connection.query("""update document set vectors = to_tsvector(body)""")
