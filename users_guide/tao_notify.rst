.. _tao_notify:

Notify
======

The Facets *notify* feature makes any change to an object attribute an
*observable event*. Notify is what makes Facets *reactive* and is the heart and
soul of its model-driven design, user interface system, tool framework and
animation system. Understanding what notify does and how to use it is one of the
keys to unlocking the full power of Facets.

Put simply, any time an attribute of a HasFacets derived class changes value,
Facets notifies any and all interested parties of the change. This is the
Facets version of the well known *observer* and *publish/subscribe* design
patterns.

Subscribing to an object attribute change notification (more commonly referred
to as a *facets change notification*) can be done in several ways:

 * Implicitly, using a well defined method naming convention.
 * Descriptively, via the *on_facets_change* and *property_depends_on* method
   decorators.
 * Explicity, using the *on_facet_change* method call.

Let's start with a simple example implemented using each of the three basic
techniques.

Using Implicit Notification
---------------------------

::

    class Margins ( HasFacets ):
        left   = Float( 1.0 )
        right  = Float( 7.5 )
        center = Float( 4.25 )

        def _left_changed ( self ):
            self.center = (self.left + self.right) / 2.0

        def _right_changed ( self ):
            self.center = (self.left + self.right) / 2.0

::

    >>> m = Margins()
    >>> m.center
    4.25
    >>> m.left = 2.5
    >>> m.center
    5.0
    >>> m.right = 5.0
    >>> m.center
    3.75

In this example we've defined a *Margins* class for keeping track of a
document's left, right and center margin points. We are using the *implicit*
technique of subscribing to a change notification by virtue of the special names
used for the ``_left_changed`` and ``_right_changed`` methods. If a class has a
facet called ``foo`` and a method called ``_foo_changed``, then the
``_foo_changed`` method is implicitly assumed to be a change notification
handler (i.e. subscriber) to the ``foo`` attribute.

The implicit naming technique can only be used to define notification handlers
for attributes defined on the same class (or one of its superclasses) containing
the implicitly named handler.

Using Descriptive Notification
------------------------------

::

    class Margins ( HasFacets ):
        left   = Float( 1.0 )
        right  = Float( 7.5 )
        center = Float( 4.25 )

        @on_facet_change( 'left, right' )
        def _margins_modified ( self ):
            self.center = (self.left + self.right) / 2.0

Here we arrive at the same result, but use the *descriptive* form of defining
change handlers by means of the *on_facet_change* method decorator. The
on_facet_change decorator takes a description of the object attributes the
following method subscribes to. In this case it leads to a more compact and
descriptive class definition than the previous example since we don't need to
duplicate the code for computing the center margin.

As we'll see in a later chapter, the *on_facet_change* and *property_depends_on*
decorators both accept a powerful and succinct *mini-language* for describing
object attributes. This often makes setting up complex sets of notification
handlers much easier than using the implicit or explicit approach.

Using Explicit Notification
---------------------------

::

    class Margins ( HasFacets ):
        left   = Float( 1.0 )
        right  = Float( 7.5 )
        center = Float( 4.25 )

        def facets_init ( self ):
            self.on_facet_change( self._margins_modified, 'left, right' )

        def _margins_modified ( self ):
            self.center = (self.left + self.right) / 2.0

This is the same example using the explict mechanism for setting up change
notification handlers based on calling the *on_facet_change* method. Notice that
the *on_facet_change* method uses the same descriptive *mini-language* for
describing object attributes used in the previous example's *on_facet_change*
method decorator.

Also note the use of the special *facets_init* method to set up the explicit
notification handler. Since subclasses of HasFacets seldom need to have an
explicit *__init__* class constructor method, the *facets_init* method is
provided to handle any post constructor initialization that might be needed. The
method has no arguments, and all attribute initialization performed by the class
constructor has already been performed by the time it is called. Thus it is a
good candidate for performing tasks such as setting up explict change
notification handlers.

For this example, the explicit form of setting up a change handler is not the
simplest solution. However, there are more complex cases where setting up a
change handler depends upon dynamic state changes that can't readily be handled
by the implicit or descriptive approach (although you might be surprised at how
many cases the descriptive approach can handle).

Using the Facets Tao
--------------------

Finally, we show the same example using a fourth approach that best illustrates
the true Facets *tao*::

    class Margins ( HasFacets ):
        left   = Float( 1.0 )
        right  = Float( 7.5 )
        center = Property( Float )

        @property_depends_on( 'left, right' )
        def _get_center ( self ):
            return (self.left + self.right) / 2.0

In this case we've changed the definition of the *center* facet to be a
Property rather than a Float. In addition, we use the *property_depends_on*
method decorator to indicate that the value of the *center* property (as
computed by its *_get_center* getter method) depends upon the value of the
*left* and *right* facets.

At first glance this might seem similar to a solution using a standard Python
*property*, but it is better for several reasons:

* If either the *left* or *right* facet changes value, so does the *center*
  facet. So if there are any change handlers listening to the *center* facet,
  they will be notified of the change.
* The *_get_center* method, which computes the value of the center property, is
  **not** called when either the *left* or *right* facet changes value. It is
  only called when some code requests the value of the *center* facet. From an
  efficiency point of view this is much better than any of the solutions we've
  looked at so far, since each of them recompute the *center* value as soon as
  either the *left* or *right* facet changes value.
* The value of the *center* property is not computed each time its value is
  requested. It is computed the first time its value is requested *after* a
  change to either the *left* or *right* facet. In effect its computed value is
  cached, and the cache is automatically flushed each time the *left* or *right*
  facet changes value.

In this section we've given you only a very small taste of what *notify* is. In
the next section we'll introduce you to the Facets user interface (UI) system
which leverages *notify* to create highly interactive and responsive user
interfaces.
