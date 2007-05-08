from itertools import chain
from sqlobject import *
from turbogears.database import PackageHub
from datetime import datetime as DateTime

hub = PackageHub("tasty")
__connection__ = hub

class Service(SQLObject):
    name = UnicodeCol(alternateID=True, length=255)
    users = MultipleJoin('User')
    items = MultipleJoin('Item')
    tags  = MultipleJoin('Tag')

    def all_rels(self, minus):
        return [(uid.user,uid.item,uid.tag) for uid in UserItemTag.select(
            AND(UserItemTag.q.userID == User.q.id,
                User.q.serviceID == self.id,
                UserItemTag.q.itemID == Item.q.id,
                Item.q.serviceID == self.id,
                UserItemTag.q.tagID == Tag.q.id,
                Tag.q.serviceID == self.id))
                if uid.user not in minus and uid.item not in minus and uid.tag not in minus]

class Orphanable:
    def delete_if_orphan(self):
        """ delete this object if there are no more references to it
        in the user_item_tags table. 
        """

        if len(list(self.uits)) == 0:
            self.delete_me()
        else:
            pass
        return
            
    def possible_orphans(self):
        return set(chain(self.users, self.items, self.tags))

    def del_users(self):
        for u in self.users:
            self.removeUser(u)

    def del_items(self):
        for i in self.items:
            self.removeItem(i)

    def del_tags(self):
        for t in self.tags:
            self.removeTag(t)

    def delete_me(self):
        self.del_users()
        self.del_items()
        self.del_tags()
        self.destroySelf()

    def __hash__(self):
        return "%s:%s" % (self.sqlmeta.table, self.id)

class User(SQLObject, Orphanable):
    class sqlmeta:
        table = "users"
    service = ForeignKey('Service', cascade=True)
    username = UnicodeCol(length=255)
    tags = RelatedJoin('Tag')
    items = RelatedJoin('Item')
    users = []
    uits = MultipleJoin('UserItemTag', joinColumn="user_id")    

    username_index = DatabaseIndex('username')

    fname_s = "username"
    name_s = "user"
    field_s = "user_id"

class Tag(SQLObject, Orphanable):
    name = UnicodeCol(length=255)
    service = ForeignKey('Service', cascade=True)
    users = RelatedJoin('User')
    items = RelatedJoin('Item')
    tags = []
    uits = MultipleJoin('UserItemTag')

    name_index = DatabaseIndex('name')
    
    fname_s = "name"
    name_s = "tag"
    field_s = "tag_id"

class Item(SQLObject, Orphanable):
    name = UnicodeCol(length=255)
    service = ForeignKey('Service', cascade=True)
    users = RelatedJoin('User')
    tags = RelatedJoin('Tag')
    items = []
    uits = MultipleJoin('UserItemTag')

    name_index = DatabaseIndex('name')
    
    fname_s = "name"
    name_s = "item"
    field_s = "item_id"

class UserItemTag(SQLObject):
    user = ForeignKey('User', cascade=True)
    item = ForeignKey('Item', cascade=True)
    tag  = ForeignKey('Tag', cascade=True)

    user_item_tag_index = DatabaseIndex('user','item','tag')

def add_uit(user, tag, item):
    r = list(UserItemTag.select(AND(UserItemTag.q.userID == user.id,
                                    UserItemTag.q.tagID  == tag.id,
                                    UserItemTag.q.itemID == item.id)))
    if len(r) == 0:
        return UserItemTag(user=user, tag=tag, item=item)
    else:
        return r[0]

def build_all_relationships(users, items, tags):
    users, items, tags = map(list, (users, items, tags))
    pending_uit = set()

    for t in tags:
        for u in users:
            if u not in t.users:
                t.addUser(u)
            for i in items:
                if i not in u.items:
                    u.addItem(i)
                pending_uit.add((u, i, t))
        for i in items:
            if i not in t.items:
                t.addItem(i)

    for u, i, t in pending_uit:
        add_uit(u, t, i)

def count_zeros(*lists):
    return sum([int(len(l) == 0) for l in lists])

def del_user_item(user,item):
    r = UserItemTag.select(AND(UserItemTag.q.userID == user.id,
                               UserItemTag.q.itemID == item.id))
    for uit in r:
        uit.destroySelf()
    user.removeItem(item)
    user.delete_if_orphan()
    item.delete_if_orphan()

def del_user_tag(user,tag):
    r = UserItemTag.select(AND(UserItemTag.q.userID == user.id,
                               UserItemTag.q.tagID == tag.id))
    for uit in r:
        uit.destroySelf()
    user.removeTag(tag)
    user.delete_if_orphan()
    tag.delete_if_orphan()

def del_item_tag(item,tag):
    r = UserItemTag.select(AND(UserItemTag.q.itemID == item.id,
                               UserItemTag.q.tagID == tag.id))
    for uit in r:
        uit.destroySelf()
    item.removeTag(tag)
    item.delete_if_orphan()
    tag.delete_if_orphan()

def delete_rels_zero(users, items, tags):
    possible_orphans = set(chain(users, items, tags))

    for u in users:
        for i in items:
            for t in tags:
                possible_orphans.update(set([u, i, t]))
                r = UserItemTag.select(AND(UserItemTag.q.userID == u.id,
                                           UserItemTag.q.itemID == i.id,
                                           UserItemTag.q.tagID  == t.id))
                
                for uit in r:
                    uit.destroySelf()

    for i in possible_orphans:
        i.delete_if_orphan()

def delete_rels_one(users, items, tags):
    for user in users:
        for item in items:
            del_user_item(user, item)
        for tag in tags:
            del_user_tag(user, tag)
    for item in items:
        for tag in tags:
            del_item_tag(item, tag)

def delete_rels(service,users,items,tags,nusers,nitems,ntags):
    # TODO: minus stuff is ignored
    users, items, tags, nusers, nitems, ntags = map(list, (users, items, tags, nusers, nitems, ntags))
    zeros = count_zeros(users,items,tags)

    # only delete the most specific relationship
    if zeros == 0:
        return delete_rels_zero(users, items, tags)

    if zeros == 1:
        # 2-dimensions
        return delete_rels_one(users, items, tags)
    
    possible_orphans = set()

    for thing in chain(users, items, tags):
        possible_orphans.update(thing.possible_orphans())
        thing.delete_me()

    for i in possible_orphans:
        i.delete_if_orphan()

    return

def build_minus(nusers,nitems,ntags):
    nusers, nitems, ntags = map(list, (nusers, nitems, ntags))
    minus = []
    for u in nusers:
        minus += u.items
        minus += u.tags
    for i in nitems:
        minus += i.users
        minus += i.tags
    for t in ntags:
        minus += t.users
        minus += t.items
    return minus

def filter_query(service,users,items,tags,nusers,nitems,ntags):
    zeros = count_zeros(users,items,tags)

    if zeros == 0:
        # a query with ALL axis fixed
        # this is either invalid, or i guess
        # we could return a boolean
        return "invalid"

    res = {}
    if zeros == 1:
        # two axis fixed
        res = filter_one_variable(users, items, tags, 
                                  build_minus(nusers, nitems, ntags))

    if zeros == 2:
        # one axis fixed
        res = filter_two_variables(users, items, tags,
                                   build_minus(nusers, nitems, ntags))

    if zeros == 3:
        # return everything for the whole service
        res = filter_three_variables(service, users, items, tags,
                                     build_minus(nusers, nitems, ntags))
    return res


def construct_where_clause(fixed):
    clauses = [t.field_s + " in (" + ",".join([str(d.id) for d in a]) + ")" 
               for (t, a) in fixed]
    w = ") AND (".join(clauses)
    return w

def fixed_len(fixed):
    return max([len(a) for (t, a) in fixed])


def construct_query(vars, fixed):
    s = ",".join([d.field_s for d in vars])
    where = construct_where_clause(fixed)
    return  ("SELECT " + s + " FROM user_item_tag WHERE (" 
             + where + ") GROUP BY " + s + " HAVING count(id) = " + 
             str(fixed_len(fixed)))

def filter_one_variable(users, items, tags, minus):
    var = None
    fixed = []

    for (t, a) in [(Tag, tags), (User, users), (Item, items)]:
        if len(a) == 0:
            var = t
        else:
            fixed.append((t, a))

    q = construct_query([var], fixed)

    res = UserItemTag._connection.queryAll(q)
    return {var.name_s + "s" : [v for v in [var.get(i[0]) for i in res] if v not in minus]}

def filter_just_two(var, fixed):
    if len(fixed) == 0: return
    s = set()
    for (typ, l) in fixed:
        for f in l:
            if var == Item:
                for i in f.items:
                    s.add(i)
            if var == User:
                for u in f.users:
                    s.add(u)
            if var == Tag:
                for t in f.tags:
                    s.add(t)
    return list(s)


def filter_two_variables(users, items, tags, minus):
    fixed = None
    vars = []

    for (t, a) in [(Tag, tags), (User, users), (Item, items)]:
        if len(a) != 0:
            fixed = (t, a)
        else:
            vars.append(t)

    q = construct_query(vars, [fixed])
    res = UserItemTag._connection.queryAll(q)

    rdict = {vars[0].name_s + "_" + vars[1].name_s + "s" : [(a ,b) for a ,b in [(vars[0].get(i[0]),vars[1].get(i[1])) for i in res]
                                                            if a not in minus and b not in minus]}
    for v in vars:
        rdict[v.name_s + "s"] = [x for x in filter_just_two(v,[fixed]) if x not in minus]
    return rdict

def filter_three_variables(service,users,items,tags,minus):
    users = [u for u in User.select(User.q.serviceID == service.id) 
             if u not in minus]
    items = [i for i in Item.select(Item.q.serviceID == service.id) 
             if i not in minus]
    tags =  [t for t in Tag.select(Tag.q.serviceID == service.id) 
             if t not in minus]
    res =  {'users' : users,
            'items' : items,
            'tags' : tags,
            'user_item_tags' : service.all_rels(minus)}
    return res

def related_items(items, limit):
    ids = ",".join([str(i.id) for i in items])
    items_tags_subselect = """select tag_id from item_tag where item_id in (%s)""" % ids
    items_users_subselect = """select users_id from item_users where item_id in (%s)""" % ids
    q = """select u.item_id, count(*) as cnt
    from user_item_tag u where (u.tag_id in (%s) or
    u.user_id in (%s)) AND u.item_id not in (%s) group by u.item_id order by cnt desc
    limit %d""" % (items_tags_subselect,items_users_subselect,ids,limit)

    return [Item.get(id) for (id, cnt) in UserItemTag._connection.queryAll(q)]

def related_tags(tags, limit):
    ids  = ",".join([str(t.id) for t in tags])
    tags_items_subselect = """select item_id from item_tag where tag_id in (%s)""" % ids
    tags_users_subselect = """select users_id from tag_users where tag_id in (%s)""" % ids
    q = """select u.tag_id, count(*) as cnt
    from user_item_tag u where (u.item_id in (%s) or
    u.user_id in (%s)) AND u.tag_id NOT IN (%s) group by u.tag_id order by cnt desc
    limit %d""" % (tags_items_subselect,tags_users_subselect,ids,limit)

    return [Tag.get(id) for (id, cnt) in UserItemTag._connection.queryAll(q)]        

def related_users(users, limit):
    ids = ",".join([str(u.id) for u in users])
    users_items_subselect = """select item_id from item_users where users_id in (%s)""" % ids
    users_tags_subselect = """select tag_id from tag_users where users_id in (%s)""" % ids
    q = """select u.user_id, count(*) as cnt
    from user_item_tag u where (u.item_id in (%s) or
    u.tag_id in (%s)) AND u.user_id NOT IN (%s) group by u.user_id order by cnt desc
    limit %d""" % (users_items_subselect,users_tags_subselect,ids,limit)

    return [User.get(id) for (id, cnt) in UserItemTag._connection.queryAll(q)]
    

def related(service, users, items, tags, nusers, nitems, ntags, limit=10):

    related = {'items' : [], 'users' : [], 'tags' : []}

    if items:
        related['items'] = related_items(items, limit)
    if tags:
        related['tags'] = related_tags(tags, limit)
    if users:
        related['users'] = related_users(users, limit)

    return related

def cloud_one(users, items, tags):
    var = None
    fixed = []
    for (t, a) in [(User, users), (Item, items), (Tag, tags)]:
        if len(a) == 0:
            var = t
        else:
            fixed.append((t, a))
    q = """select u.%s, count(*) as cnt from user_item_tag uit, %s u
    where uit.%s = u.id AND uit.%s in (%s) and uit.%s in (%s) group by uit.%s,u.%s order by upper(u.%s) ASC""" \
    % (var.fname_s, var.sqlmeta.table, var.field_s, fixed[0][0].field_s,
       ",".join([str(i.id) for i in fixed[0][1]]), fixed[1][0].field_s,
       ",".join([str(i.id) for i in fixed[1][1]]), var.field_s,var.fname_s,var.fname_s)
    return {var.name_s + "s" : [{var.name_s : uit[0], 'count' : uit[1]} for uit in UserItemTag._connection.queryAll(q)]}

def cloud_two(users, items, tags):
        # TODO: currently returns cloud of the union of multiple
        # items/users/tags should be intersection to be consistent
        # with the rest of the interface
        var = []
        fixed = None
        for (t, a) in [(User, users), (Item, items), (Tag, tags)]:
            if len(a) == 0:
                var.append(t)
            else:
                fixed = (t, a)

        r = {}

        for t in var:
            q = """select u.%s, count(*) as cnt from user_item_tag uit, %s u
            where uit.%s = u.id and uit.%s in (%s) group by uit.%s,u.%s order by upper(u.%s) ASC""" \
            % (t.fname_s,t.sqlmeta.table,t.field_s,fixed[0].field_s,
               ",".join([str(i.id) for i in fixed[1]]),t.field_s,t.fname_s,t.fname_s)
            r[t.name_s + "s"] = [{t.name_s : uit[0], 'count' : uit[1]} for uit in UserItemTag._connection.queryAll(q)]
        return r

def cloud_three(service):
    r = {}
    for t in [User, Item, Tag]:
        q = """select u.%s, count(*) as cnt from user_item_tag uit, %s u
        where uit.%s = u.id and u.service_id = %d group by uit.%s,u.%s order by upper(u.%s) ASC""" \
        % (t.fname_s,t.sqlmeta.table,t.field_s,service.id,t.field_s,t.fname_s,t.fname_s)
        r[t.name_s + "s"] = [{t.name_s : uit[0], 'count' : uit[1]} for uit in UserItemTag._connection.queryAll(q)]
    return r
    

def cloud(service, users, items, tags):
    zeros = count_zeros(users, items, tags)

    if zeros == 0:
        # can't really produce a cloud for this request
        return "invalid"

    if zeros == 1:
        # two dimensions specified
        return cloud_one(users,items,tags)
    
    if zeros == 2:
        # one dimension specified
        return cloud_two(users,items,tags)
    
    if zeros == 3:
        # /service/<service>/cloud
        # return tag, user, and item clouds
        return cloud_three(service)


