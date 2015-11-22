# Introduction #

NQDQ is a Queue/Stack microapp. You can create queues, push items onto them, then pop or shift items off.

# REST API #

The basic structure is

```
 /service/<service>/q/<queue>/
```

The API is roughly:

```
 POST   /service/<service name>/     -- creates that service
 DELETE /service/<service name>/     -- removes that service
 GET    /                            -- lists the services 
 GET    /service/<service name>/     -- lists the queue's for the service
 
 POST   /service/<service name>/q/<queue name>/    -- creates a new queue
 DELETE /service/<service name>/q/<queue name>/    -- removes the queue
 GET    /service/<service name>/q/<queue name>/    -- returns entire contents of queue as JSON array
 
 POST /service/<service name>/q/<queue name>/push (param: 'value')    -- appends value to queue
 POST /service/<service name>/q/<queue name>/unshift (param: 'value') -- inserts value to front of queue 
                                                                         ('unshift' comes from the perl function that does the same)
 
 POST /service/<service name>/q/<queue name>/pop      -- removes item from end of queue and returns it
 POST /service/<service name>/q/<queue name>/shift    -- removes item from the front of the queue and returns it
 GET  /service/<service name>/q/<queue name>/length   -- returns the number of items in the queue
 GET  /service/<service name>/q/<queue name>/peek     -- returns the item on the front of the queue but doesn't remove it
 GET  /service/<service name>/q/<queue name>/end_peek -- returns the item on the end of the queue but doesn't remove it
```


CAVEAT: I couldn't really think of a perfect way to have NQDQ handle popping or shifting from an empty queue. In a normal programming language, this is the kind of thing that would throw an exception. For the microapp version of a queue though, I currently have it just returning an empty string in those situations. This can be a problem if your client application can store empty strings in the queue as you won't be able to tell the difference between empty strings stored on the queue and the end of the queue.


# Requirements #

  * python 2.5
  * setuptools
  * PostgreSQL (though it should also work with any other database that SQLObject supports)

All other requirements are bundled with NQDQ and will be automatically installed with the included `init.sh` script.

# Installation #

(Tested on Ubuntu Linux (Feisty), but should work anywhere that TurboGears
works.)

To install, check out code:

```
  $ svn co http://microapps.googlecode.com/svn/nqdq/trunk/ nqdq
```

initialize a workingenv:

```
  $ cd nqdq
  $ ./init.sh .
```

init.sh takes the directory to put the workingenv in as its only
argument. It will create a workingenv and install all the necessary
(and included) eggs into it.

Edit dev.cfg, prod.cfg, or copy one of those to a different
file and configure to your liking (change port #, database connection string, etc.)

Create a database, activate a workingenv, and initialize the DB schema:

```
  $ createdb nqdq # postgres specific. substitute the appropriate command for your db
  $ source working-env/bin/activate
  $ tg-admin sql create
```

run it:

```
  $ ./start.sh . prod.cfg
```

# Credits #

NQDQ was developed by Anders Pearson at the Columbia Center For New
Media Teaching and Learning (http://ccnmtl.columbia.edu/).
