# Introduction #

Pita is a small microapp implementing simple data pockets.

Basically, it's a dictionary/hashtable available over http.

# REST API #

A sample curl session demonstrating how Pita works (assuming Pita is running on pita.example.com):

```
 $ curl -X PUT -d "value=this is some data to be stored" \
   http://pita.example.com/service/example/item/sample/
 ok
 $ curl http://localhost:9980/service/example/item/sample/
 this is some data to be stored
 $ curl -X DELETE http://localhost:9980/service/example/item/sample/ \
 ok
```

There's not much more to it than that.

Like many other microapps, there is a 'service' layer at the top that basically just acts as a namespace so multiple applications can use the same pita server without stomping on each others data.

Other than that, you PUT data to an 'item', do a GET on the item to retrieve it, and DELETE an item to clear it.

# Requirements #

  * python 2.5
  * setuptools
  * PostgreSQL (though it should also work with any other database that SQLObject supports)

All other requirements are bundled with Pita and will be automatically installed with the included `init.sh` script.

# Installation #

(Tested on Ubuntu Linux (Feisty), but should work anywhere that TurboGears
works.)

To install, check out code:

```
  $ svn co http://microapps.googlecode.com/svn/pita/trunk/ pita
```

initialize a workingenv:

```
  $ cd pita
  $ ./init.sh .
```

init.sh takes the directory to put the workingenv in as its only
argument. It will create a workingenv and install all the necessary
(and included) eggs into it.

Edit dev.cfg, prod.cfg, or copy one of those to a different
file and configure to your liking (change port #, database connection string, etc.)

Create a database, activate a workingenv, and initialize the DB schema:

```
  $ createdb pita # postgres specific. substitute the appropriate command for your db
  $ source working-env/bin/activate
  $ tg-admin sql create
```

run it:

```
  $ ./start.sh . prod.cfg
```

# Credits #

Pita was developed by Anders Pearson at the Columbia Center For New
Media Teaching and Learning (http://ccnmtl.columbia.edu/).