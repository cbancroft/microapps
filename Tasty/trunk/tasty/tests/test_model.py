from turbogears import testutil as util
from tasty.model import *
import unittest,cherrypy

from turbogears import database
database.set_db_uri("sqlite:///:memory:")
from tasty.helpers import sqlobject_to_strings, xmlify, htmlify

def createTables():
    Service.createTable(ifNotExists=True)
    User.createTable(ifNotExists=True)
    Item.createTable(ifNotExists=True)
    Tag.createTable(ifNotExists=True)
    UserItemTag.createTable(ifNotExists=True)

def dropTables():
    UserItemTag.dropTable(ifExists=True)
    Tag.dropTable(ifExists=True)
    Item.dropTable(ifExists=True)
    User.dropTable(ifExists=True)
    Service.dropTable(ifExists=True)

class TestModel(unittest.TestCase):
    def setUp(self):
        createTables()
        self.service = Service(name="testservice")
        self.user = User(username="testuser",service=self.service)
        self.item = Item(name="testitem",service=self.service)
        self.tag = Tag(name="testtag",service=self.service)


        self.users = dict([(username,User(username=username,service=self.service)) for username in ["anders","jonah","eric","sky","maurice","marc"]])
        self.items = dict([(name,Item(name=name,service=self.service)) for name in ["fernandez fierro","in flames","mastodon","covenant"]])
        self.tags = dict([(name,Tag(name=name,service=self.service)) for name in ["tango","metal","swedish","argentinian","industrial"]])

    def tearDown(self):
        dropTables()

    def test_basics(self):
        assert self.service.name == "testservice"
        assert self.user.username == "testuser"
        assert self.item.name == "testitem"
        assert self.tag.name == "testtag"

    def test_unicode(self):
        s = Service(name=u"\u738b\u83f2")
        assert s.name == u"\u738b\u83f2"
        u = User(username=u"\u738b\u83f2",service=s)
        assert u.username == u"\u738b\u83f2"
        i = Item(name=u"\u738b\u83f2",service=s)
        assert i.name == u"\u738b\u83f2"
        t = Tag(name=u"\u738b\u83f2",service=s)
        assert t.name == u"\u738b\u83f2"

    def test_build_all(self):
        u = self.users
        i = self.items
        t = self.tags
        # anders tags 'fernandez fierro' as tango
        build_all_relationships([u['anders']],[i['fernandez fierro']],[t['tango']])
        assert i['fernandez fierro'] in u['anders'].items
        assert t['tango']            in u['anders'].tags
        assert u['anders']           in i['fernandez fierro'].users
        assert t['tango']            in i['fernandez fierro'].tags
        assert u['anders']           in t['tango'].users
        assert i['fernandez fierro'] in t['tango'].items

        # anders tags 'in flames' as metal and swedish
        build_all_relationships([u['anders']],[i['in flames']],[t['metal'],t['swedish']])
        assert i['in flames'] in t['metal'].items
        assert i['in flames'] in t['swedish'].items
        assert u['anders']    in t['metal'].users
        assert u['anders']    in t['swedish'].users

        # anders tags 'in flames' and 'covenant' as swedish

        # anders tags 'in flames' and 'amon amarth' as swedish and metal

    def test_add_uit(self):
        pass


    def test_construct_where_clause(self):
        tango = self.tags['tango']
        metal = self.tags['metal']
        q = construct_where_clause([(Tag,[tango])])
        assert q == 'tag_id in (%d)' % tango.id
        q = construct_where_clause([(Tag,[tango,metal])])
        assert q == 'tag_id in (%d,%d)' % (tango.id,metal.id)

    def test_fixed_len(self):
        i1 = (User,[1])
        i2 = (User,[2,2])
        i3 = (User,[3,3,3])
        assert fixed_len([i1,i1]) == 1
        assert fixed_len([i1,i2]) == 2
        assert fixed_len([i2,i1]) == 2
        assert fixed_len([i2,i2]) == 2
        assert fixed_len([i2,i3,i2]) == 3

    def test_filter_query(self):
        u = self.users
        i = self.items
        t = self.tags
        # anders tags 'fernandez fierro' as tango
        build_all_relationships([u['anders']],[i['fernandez fierro']],[t['tango']])

        # anders tags 'in flames' as metal and swedish
        build_all_relationships([u['anders']],[i['in flames']],[t['metal'],t['swedish']])

        # /service/testservice/
        r = filter_query(self.service,[],[],[],[],[],[])
        assert r.has_key('users')
        assert r.has_key('items')
        assert r.has_key('tags')
        assert r.has_key('user_item_tags')
        assert u['anders'] in r['users']
        assert i['in flames'] in r['items']
        assert t['metal'] in r['tags']
        assert (u['anders'],i['in flames'],t['metal']) in r['user_item_tags']

        # /service/testservice/user/anders/
        r = filter_query(self.service,[u['anders']],[],[],[],[],[])
        assert r.has_key('tag_items')
        assert (t['metal'],i['in flames']) in r['tag_items']
        assert r.has_key('tags')
        assert r.has_key('items')
        assert t['metal'] in r['tags']
        assert i['in flames'] in r['items']

        # /service/testservice/item/in%20flames/
        r = filter_query(self.service,[],[i['in flames']],[],[],[],[])
        assert r.has_key('tag_users')
        assert (t['metal'],u['anders']) in r['tag_users']
        assert r.has_key('tags')
        assert r.has_key('users')
        assert t['metal'] in r['tags']
        assert u['anders'] in r['users']

        # /service/testservice/tag/metal/
        r = filter_query(self.service,[],[],[t['metal']],[],[],[])
        assert r.has_key('user_items')
        assert (u['anders'],i['in flames']) in r['user_items']
        assert r.has_key('users')
        assert r.has_key('items')
        assert u['anders'] in r['users']
        assert i['in flames'] in r['items']

        # /service/testservice/tag/metal/tag/swedish/
        r = filter_query(self.service,[],[],[t['metal'],t['swedish']],[],[],[])
        assert r.has_key('user_items')
        assert (u['anders'],i['in flames']) in r['user_items']
        assert r.has_key('users')
        assert r.has_key('items')
        assert u['anders'] in r['users']
        assert i['in flames'] in r['items']


        # /service/testservice/user/anders/tag/metal/
        r = filter_query(self.service,[u['anders']],[],[t['metal']],[],[],[])
        assert i['in flames'] in r['items']

        # /service/testservice/user/anders/tag/metal/tag/swedish/
        r = filter_query(self.service,[u['anders']],[],[t['metal'],t['swedish']],[],[],[])
        assert i['in flames'] in r['items']

        # /service/testservice/user/anders/item/in%20flames/tag/metal/
        r = filter_query(self.service,[u['anders']],[i['in flames']],[t['metal'],t['swedish']],[],[],[])
        assert r == "invalid"

    def test_negatives(self):
        u = self.users
        i = self.items
        t = self.tags
        # anders tags 'fernandez fierro' as tango
        build_all_relationships([u['anders']],[i['fernandez fierro']],[t['tango']])

        # anders tags 'in flames' as metal and swedish
        build_all_relationships([u['anders']],[i['in flames']],[t['metal'],t['swedish']])
        # anders tags 'covenant' as swedish industrial
        build_all_relationships([u['anders']],[i["covenant"]],[t['swedish'],t['industrial']])

        # /service/testservice/user/anders/tag/swedish/tag/-metal/
        r = filter_query(self.service,[u['anders']],[],[t['swedish']],[],[],[t['metal']])
        assert i['covenant'] in r['items']
        assert i['in flames'] not in r['items']

        # /service/testservice/tag/-metal/
        r = filter_query(self.service,[],[],[],[],[],[t['metal']])
        assert i['in flames'] not in r['items']
        assert u['anders'] not in r['users']
        assert (u['anders'],i['in flames'],t['metal']) not in r['user_item_tags']

    def test_delete(self):
        u = self.users
        i = self.items
        t = self.tags

        # anders tags 'fernandez fierro' as tango
        build_all_relationships([u['anders']],[i['fernandez fierro']],[t['tango']])

        # anders tags 'in flames' as metal and swedish
        build_all_relationships([u['anders']],[i['in flames']],[t['metal'],t['swedish']])
        # anders tags 'covenant' as swedish industrial
        build_all_relationships([u['anders']],[i["covenant"]],[t['swedish'],t['industrial']])

        # DELETE /service/testservice/user/anders/item/fernandez fierro/tag/tango/
        delete_rels(self.service,[u['anders']],[i['fernandez fierro']],[t['tango']],[],[],[])

        # anders should still have some tags

        assert len(u['anders'].items) > 0
        assert len(u['anders'].tags) > 0

        # anders tags 'fernandez fierro' as tango
        build_all_relationships([u['anders']],[i['fernandez fierro']],[t['tango']])
        # DELETE /service/testservice/user/anders/item/fernandez fierro/tag/tango/
        delete_rels(self.service,[],[i['fernandez fierro']],[t['tango']],[],[],[])

        assert len(u['anders'].items) > 0
        assert len(u['anders'].tags) > 0
        assert len(t['tango'].items) == 0

    def test_cloud(self):
        u = self.users
        i = self.items
        t = self.tags

        # anders tags 'in flames' as metal and swedish
        build_all_relationships([u['anders']],[i['in flames']],[t['metal'],t['swedish']])
        # anders tags 'covenant' as swedish industrial
        build_all_relationships([u['anders']],[i["covenant"]],[t['swedish'],t['industrial']])

        r = cloud(self.service,[],[],[])

        assert {'tag' : 'swedish','count' : 2} in r['tags']
        assert {'user' : 'anders','count' : 4} in r['users']

        r = cloud(self.service,[u['anders']],[],[])

        assert {'tag' : 'swedish','count' : 2} in r['tags']
        assert {'item' : 'covenant','count' : 2} in r['items']
        assert not r.has_key('users')

        r = cloud(self.service,[u['anders']],[i['covenant']],[])

        assert r.has_key('tags')
        assert not r.has_key('users')
        assert not r.has_key('items')

        assert {'tag' : 'swedish','count' : 1} in r['tags']

    def test_sqlobject_to_strings(self):
        assert sqlobject_to_strings(self.service)

    def test_xmlify(self):
        assert xmlify(('a','b')) == '<a>b</a>'
        assert xmlify(1) == '1'

    def test_htmlify(self):
        assert htmlify(('a','b')) == '<span class="a">b</span>'
        assert htmlify(1) == '1'
