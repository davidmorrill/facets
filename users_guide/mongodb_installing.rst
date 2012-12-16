.. _mongodb_installing:

Installing MongoDB
==================

Because MongoDB is a completely separate tool from Facets, you will need to
install some additional code before being able to use it as part of a Facets
application.

The first thing you will need to install is the MongoDB code itself, which can
be obtained from: 

* http://www.mongodb.org/downloads

Once MongoDB has been installed, you will also need to install the PyMongo
package, which provides the low-level interface from Python to MongoDB that the
MongoDB OML layer is built on. This package can be found at:

* http://pypi.python.org/pypi/pymongo/

Both of these packages are freely available and open source. Of course, you
should also review each package's license details before deciding whether they 
are suitable for your own use.

Depending upon how much low-level control over the MongoDB database your
application needs, you may also want to read the documentation that comes with
each package. In many cases, such as in the example application just presented,
the documentation provided here may be all that you need to know to write your
application code. But having some familiarity with how MongoDB works may also
provide some valuable insight into the best way to structure your application
data model and logic.

