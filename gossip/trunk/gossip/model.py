from sqlobject import *
from turbogears.database import PackageHub
from datetime import datetime

soClasses = ["Service","Thread","Comment"]

hub = PackageHub("gossip")
__connection__ = hub

class Service(SQLObject):
    name = UnicodeCol(default=u"",alternateID=True)
    threads = MultipleJoin('Thread',orderBy="name")

class Thread(SQLObject):
    name = UnicodeCol()
    service = ForeignKey('Service',cascade=True)
    added = DateTimeCol(default=datetime.now)
    comments = MultipleJoin('Comment',orderBy="-modified")

    def get_comments(self):
        """ get just the top level replies """
        return list(Comment.select(AND(Comment.q.threadID == self.id,
                                       Comment.q.reply_to == 0),
                                   orderBy="added"))


class Comment(SQLObject):
    thread   = ForeignKey('Thread',cascade=True)
    subject  = UnicodeCol(default=u"")
    body     = UnicodeCol(default=u"")
    reply_to = IntCol(default=0)
    added    = DateTimeCol(default=datetime.now)
    modified = DateTimeCol(default=datetime.now)
	  
    author_id    = UnicodeCol(default=u"")
    author_name  = UnicodeCol(default=u"")
    author_email = UnicodeCol(default=u"")
    author_url   = UnicodeCol(default=u"")
    author_ip    = UnicodeCol(default=u"")
    
    def as_dict(self):
        return dict(thread       = self.thread.name,
                    id           = str(self.id),
                    subject      = self.subject,
                    body         = self.body,
                    reply_to     = self.reply_to,
                    added        = str(self.added),
                    modified     = str(self.modified),
                    author_id    = self.author_id,
                    author_email = self.author_email,
                    author_url   = self.author_url,
                    author_name  = self.author_name,
                    author_ip    = self.author_ip,
                    replies      = [c.as_dict() for c in self.replies()])

    def replies(self):
        """ returns list of comments that are replies to this one """
        return list(Comment.select(Comment.q.reply_to == self.id,
                                   orderBy="added"))

    def delete(self):
        self.delete_replies()
        self.destroySelf()

    def delete_replies(self):
        for r in self.replies():
            r.delete()


    
                    
                    


	  

