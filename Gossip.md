# Introduction #

Gossip is a microapp implementation of a discussion board or threaded comment system.

# REST API #

The resources are Services, Threads, and Comments.

The API:

```
  POST   /service/<service name>/    -- create service
  DELETE /service/<service name>/    -- delete service
  GET    /service/<service name>/    -- JSON list of threads in the service
    
  POST   /service/<service name>/thread/<thread name>/                                                  -- create thread
  DELETE /service/<service name>/thread/<thread name>/                                                  -- delete thread
  GET    /service/<service name>/thread/<thread name>/                                                  -- JSON list of comments in thread
  POST   /service/<service name>/thread/<thread name>/reply  
   params: subject, body, author_id, author_email, author_name, author_url, author_ip                   -- add a comment to the thread. returns comment id.
  GET    /service/<service name>/thread/<thread name>/comment/<comment_id>/                             -- returns JSON dictionary of comment attributes including list of replies
  POST   /service/<service name>/thread/<thread name>/comment/<comment_id>/reply (same params as above) -- reply to the comment. returns comment id.
  DELETE /service/<service name>/thread/<thread name>/comment/<comment_id>/                             -- delete comment (and it's replies)
```

anytime a comment is returned, this is the list of fields that it will have: `subject`, `body`, `added` (ISO8601 timestamp for when the comment was added), `modified` (ISO8601 timestamp for when the comment was last modified or replied to), `author_id` (useful if gossip is tied to a system that has a notion of user. if not, it would be recommended to set this to "anonymous" or something), `author_email`, `author_name`, `author_url`, and `author_ip` (useful thing to keep track of if it ever incorporates spam blacklisting).

Future Plans: ability to pull out N newest comments from thread/service (with offset for pagination). edit comment.

# Requirements #

  * python 2.5
  * setuptools
  * PostgreSQL (though it should also work with any other database that SQLObject supports)

All other requirements are bundled with Gossip and will be automatically installed with the included `init.sh` script.

# Installation #

(Tested on Ubuntu Linux (Feisty), but should work anywhere that TurboGears
works.)

To install, check out code:

```
  $ svn co http://microapps.googlecode.com/svn/gossip/trunk/ gossip
```

initialize a workingenv:

```
  $ cd gossip
  $ ./init.sh .
```

init.sh takes the directory to put the workingenv in as its only
argument. It will create a workingenv and install all the necessary
(and included) eggs into it.

Edit dev.cfg, prod.cfg, or copy one of those to a different
file and configure to your liking (change port #, database connection string, etc.)

Create a database, activate a workingenv, and initialize the DB schema:

```
  $ createdb gossip # postgres specific. substitute the appropriate command for your db
  $ source working-env/bin/activate
  $ tg-admin sql create
```

run it:

```
  $ ./start.sh . prod.cfg
```

# Credits #

Gossip was developed by Anders Pearson at the Columbia Center For New
Media Teaching and Learning (http://ccnmtl.columbia.edu/).

