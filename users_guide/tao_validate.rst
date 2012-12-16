.. _tao_validate:

Validate
========

As a Python developer or user, you're already familiar with the fact that
object attributes do not have fixed types. At one instant an attribute might
have an integer value, and at the next it might have a string value. In many
cases this is a good thing, since it can streamline coding and allows certain
kinds of classes to be easily reused in different contexts.

Some examples of when this flexible typing is a very good thing are the Python
*list*, *tuple*, *dict* and *set* classes, which all work equally well with any
kind of data. In strongly typed languages like C++, C# or Java, creating
flexible *collection* classes like these requires the use of *generics*, which
provide a similar capability but can be much more difficult to write and
implement correctly.

A Simple Python Example
-----------------------

But just because this type flexibility is a good thing in many important cases
does not mean that it is always a good thing. Let's say we are writing a health
application where we need to keep track of the name, age, weight and gender of
various people. In Python, we might start by creating the following class::

    class Person ( object ):

        def __init__ ( name, age, weight, gender ):
            self.name   = name
            self.age    = age
            self.weight = weight
            self.gender = gender

Now, we might intuitively know that a name should be a string, an age should be
a non-negative integer, a weight should be a positive float, and the gender
should either be the string "male" or "female". But as a Python user you know
there is nothing in the above code to enforce this.

We could decide that with our 'leet coding skills this is not a problem, since
we will never, ever make a mistake and assign the wrong kind of value to any of
the object's attributes. That's fine for highly skilled conscientious coders.

Adding Some Python Type Checking
--------------------------------

But what if this class is part of a package you are distributing to other Python
developers, not all of which possess your level of python-fu. Reluctantly, you
decide to add some checking logic to you class::

    class Person ( object ):

        def __init__ ( name, age, weight, gender ):
            if not isinstance( name, basestring ):
                raise ValueError( 'The name argument must be a string')
            if (not isinstance( age, int )) or (age < 0):
                raise ValueError( 'The age argument must be a non-negative integer')
            if (not isinstance( weight, float )) or (float <= 0.0):
                raise ValueError( 'The weight argument must be a positive float')
            if gender not in ( 'male', 'female'):
                raise ValueError( 'The gender argument must be either "male" or "female"')

            self.name   = name
            self.age    = age
            self.weight = weight
            self.gender = gender

Phew! Well, that was a little bit painful, but at least we know now that all of
the inputs to the constructor have been properly validated. So we sit back with
a sigh of relief and start to dig out the XBox controller. Suddenly we remember
that there's nothing preventing our fellow developers from writing::

    p = Person( 'Joe', 48, 165.2, 'male' )
    p.age = 'middle aged'

Groan!

A Simple Facets Example
-----------------------

By now you've probably gotten the point that unrestricted type flexibility may
not always be what we want. So now let's rewrite our example using Facets
*validate* feature::

    class Person ( HasFacets ):
        name   = Str
        age    = Range( 0, None )
        weight = Range( 0.1, None )
        gender = Enum( 'male', 'female' )

The main things to note about this example are:

* We derive our Person class from HasFacets instead of object. This is how we
  access the features that the Facets package provides. There are other base
  classes we can derive from as well, which we'll describe in other chapters;
  but HasFacets is the base class that all Facets-featured classes derive from.
* We define a number of *typed* instance attributes using lines like::

      name = Str

  which can be read as saying "instances of this class have an attribute called
  *name* which must have a *string* (i.e. Str) value".

  The *Str*, *Range* and *Enum* symbols are called *facets* and provide many of
  the same capabilities as a *type* in other programming languages. In
  particular, in this example they provide the type checking (i.e. *validation*)
  we are looking for.

At first glance it might not seem like it, but this Facets class is actually a
functional superset of the second Python example we wrote previously. That is:

* It automatically provides a constructor which ensures that only valid
  arguments are passed and assigned.
* It also catches attempts to assign invalid values to object attributes after
  the constructor has run.

To see this, we'll show the results of an interactive Python interpreter session
using the Facets version of the Person class::

    >>> p = Person( name = 'Joe', age = 48, weight = 165.2, gender = 'male' )
    >>> p.age = 'middle aged'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "C:\Assembla\trunk\facets\core\facet_handlers.py", line 187, in error
        object, name, self.full_info( object, name, value ), value
    facets.core.facet_errors.FacetError: The 'age' facet of a Person instance must
    be an integer >= 0, but a value of middle aged was specified.
    >>> p = Person( name = 'Joe', age = 48, weight = 165.2, gender = 'guy' )
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "C:\Assembla\trunk\facets\core\facet_handlers.py", line 187, in error
        object, name, self.full_info( object, name, value ), value
    facets.core.facet_errors.FacetError: The 'gender' facet of a Person instance must
    be 'male' or 'female', but a value of guy was specified.

Note that the Facets-based Person class caught both:

* The attempt to incorrectly modify an object attribute after the object had
  been constructed.
* The attempt to pass the constructor an invalid argument.

The careful reader might also note the difference in the constructor calls
between the standard Python Person class and the Facets version. Although you
can construct Facets classes that accept unnamed constructor arguments, the
default HasFacets constructor expects only a list of named arguments, each of
which is assigned to their eponymous object attribute.

This means you don't need to create an explicit class constructor for many
Facets classes, although you are free to do so if you like. In later chapters
we'll cover some examples of constructing Facets classes with and without an
explicit constructor method.

Additional Thoughts
-------------------

Some final comments about Facets *validation* before moving on to the next
section:

* Facets does not force you to define a specific type for all object attributes.
  The *Any* Facet can be used to define attributes which accept any Python
  value::

      class NamedValue ( HasFacets ):
          name  = Str
          value = Any

  ::

      nv1 = NamedValue(
          name = 'manager',
          value = Person( name = 'Joe', age = 48, weight = 165.2, gender = 'male' )
      )
      nv2 = NamedValue(
          name  = 'meaning of life'
          value = 42
      )

  You can also use the *Python* Facet, which is like *Any* but has standard
  Python attribute semantics. That is, you must explicity set the associated
  obect attribute before referencing it::

      class NamedPythonValue ( HasFacets ):
          name  = Str
          value = Python

  ::

      >>> nv = NamedPythonValue()
      >>> print nv.name

      >>> print nv.value
      Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
      AttributeError: 'NamedPythonValue' object has no attribute 'value'

  Using Facets gives you the best of both worlds: strongly typed attributes when
  you need them, and flexibly type attributes when you don't.
* You can easily mutate existing Facet types to create new ones. For example,
  let's say you want an attribute that can either be None or an integer in the
  range from 1 to 6. Simply write::

      class DiceRoll ( HasFacets ):
          die_value = Either( None, Range( 1, 6 ) )

  ::

      >>> roll = DiceRoll()
      >>> roll.die_value = 3
      >>> roll.die_value = None
      >>> roll.die_value = 7
      Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "C:\Assembla\trunk\facets\core\facet_handlers.py", line 187, in error
          object, name, self.full_info( object, name, value ), value
      facets.core.facet_errors.FacetError: The 'die_value' facet of a DiceRoll instance
      must be 1 <= an integer <= 6 or None, but a value of 7 was specified.
* You can define your own, new Facet types if the ones you need aren't provided
  by the Facets package. We'll cover this more advanced topic in a later
  chapter.
