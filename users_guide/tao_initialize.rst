.. _tao_initialize:

Initialize
==========

One of the keys to creating a good object model is ensuring that your objects
always have a valid, consistent state. And part of that process is making sure
that objects are always correctly initialized.

A Simple Python Example
-----------------------

In Python, object attributes are not defined until they are assigned a value.
Thus it is a common practice for the class constructor to initialize all object
attributes. This was the practice we followed in our first standard Python
Person class implementation in the previous section::

    class Person ( object ):

        def __init__ ( name, age, weight, gender ):
            self.name   = name
            self.age    = age
            self.weight = weight
            self.gender = gender

In some cases, we may decide not to pass in all of the initial object state in
the class constructor. In such cases it is still a good idea to initialize each
of the object's attributes::

    class Person_2 ( object ):

        def __init__ ( self ):
            self.name   = ''
            self.age    = 0
            self.weight = 0.1
            self.gender = 'female'

A Simple Facets Example
-----------------------

Facets simplifies this process by allowing you to define the initial value for
an object attribute as part of its facet's *declaration*::

    class Person ( HasFacets ):
        name   = Str( '' )
        age    = Range( 0, None, value = 0 )
        weight = Range( 0.1, None, value = 0.1 )
        gender = Enum( 'male', [ 'male', 'female' ] )

Every Facet has a predefined default value. If you do not specify an initial
value when defining an object attribute, the default value associated with the
facet is used as the initial value for the object attribute. This is the feature
we took advantage of when we wrote our original Facets version of the Person
class::

    class Person ( HasFacets ):
        name   = Str
        age    = Range( 0, None )
        weight = Range( 0.1, None )
        gender = Enum( 'male', 'female' )

To see that this in indeed what is happening, look at the following shell
session::

    >>> p=Person()
    >>> p.name
    ''
    >>> p.age
    0
    >>> p.weight
    0.1
    >>> p.gender
    'male'

Facets automatic initialization of object attributes is very useful for several
reasons:

* Specifying the initial attribute value in the facet declaration (or using the
  default facet value) provides useful documentation to anyone reading the code
  later. They don't have to look at the class constructor method to see what
  value was initially assigned to the attribute.
* Ensuring each attribute has an initial value provides another reason why
  Facets-based classes seldom need explicit class constructors. Since we know
  all attributes have an initial value, we don't have to write code in the class
  constructor to set them.

Additional Thoughts
-------------------

Some other interesting things to note about the Facets *initialization* feature:

* Initialization is *smart*. For example, we could write::

      class Schedule ( HasFacets ):
          events = Any( [] )

  We've defined the default value for the *events* attribute to be an empty
  list, so we don't have to assign an empty list to *events* in the class
  constructor. Facets is smart enough to make sure that each new *Schedule*
  instance has a new, empty list assigned to its *events* attribute, not the
  original, empty list we used in the attribute's facet declaration.

  Anyone familiar with the common Python *gotcha* of::

      def add_item ( item, target = [] ):
          target.append( item )
          return target

  will appreciate this.

  .. note:

     If you are not familiar with this, the problem is that all invocations of
     the *add_item* function use the same list whenever the *target* argument is
     ommitted. While the list is originally empty, over time it accumulates all
     the items passed in to *add_item*. This is not usually what you want.

* Initialization is *really smart*. Unlike the Python class constructor
  initialization approach, Facets doesn't actually initialize the object
  attribute until its value is fetched the first time. This *deferred
  initialization* means your code is more efficient. For example::

      class Schedule ( HasFacets ):
          events = Any( [] )

      s = Schedule( events = [ 'Breakfast meeting at 10:00 AM' ] )

  In this example we never have to create an initial empty list value because
  the constructor for *s* ends up setting *events* to a non-empty list before we
  ever need to fetch the value of *events*.

* The initial value for an object attribute can be computed dynamically.
  Sometimes the initial value for an attribute depends upon other object or
  environmental state that isn't known until the object is created.

  Facets ability to define initial values dynamically again helps you to write
  and execute more efficiently, since:

  * You don't need to write class constructor code to compute the dynamic value,
    which again may eliminate the need for you to write a class constructor at
    all.
  * The Facets code to compute the initial value is only called if needed (i.e.
    in cases where the object attribute is not explicitly set before use).

  Creating dynamic initial facet values is an advanced topic which we'll see
  examples of in later chapters.
