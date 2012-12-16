.. _tao_delegate:

Delegate
========

Anyone familiar with OOD (Object Oriented Design) is probably familiar with the
argument that says *composition* and *delegation* are often more powerful than
*inheritance*. Facets provides special support for delegation through the
*DelegatesTo* and *PrototypedFrom* facets.

Using Explicit Delegation
-------------------------

As a somewhat trivial example, let's say we are writing a graphics application
containing *Circle*, *Rectangle* and *Polygon* classes. Each of these classes
has some common characteristics like *fill_color*, *outline_color* and
*outline_width*.

We would like to encapsulate these drawing attributes into a common *Style*
object that each object can refer to::

    class Style ( HasFacets ):
        fill_color    = Color( 'white' )
        outline_color = Color( 'black' )
        outline_width = Range( 0, 20 )

Now we could write our code so that the delegation is explicit. For example::

    class Circle ( HasFacets ):
        style = Instance( Style )

        def draw ( self, graphics ):
            graphics.init( self.style.fill_color,
                           self.style.outline_color,
                           self.style.outline_width )
            graphics.draw_circle( ... )

Using PrototypedFrom Delegation
-------------------------------

There is nothing wrong with this approach, other than the extra level of
referencing needed to get to the drawing attributes. Another approach, using
the *PrototypedFrom* facet, might look like::

    class Circle ( HasFacets ):
        style         = Instance( Style )
        fill_color    = PrototypedFrom( 'style' )
        outline_color = PrototypedFrom( 'style' )
        outline_width = PrototypedFrom( 'style' )

        def draw ( self, graphics ):
            graphics.init( self.fill_color,
                           self.outline_color,
                           self.outline_width )
            graphics.draw_circle( ... )

This code defines the drawing attributes as parts of the Circle class that
*prototype* their values from the Style object referenced by the object's
*style* attribute. This simplifies the *draw* method code but adds additional
attribute definitions to the Circle class.

However, there are several important additional differences:

* The drawing attributes in the Circle class do not require any additional
  storage initially. Each attribute reference automatically looks up the
  corresponding object attribute reference in the Circle's *style* object.
* If any drawing attribute is assigned a new value, the value is saved in the
  Circle object and does not affect the Circle's *style* object. However, any
  future reference to that attribute uses the Circle object's value rather than
  the *style* object's value used initially. This characteristic is where the
  *PrototypedFrom* name comes from.
* If the same drawing attribute is later deleted (e.g.
  `del circle.outline_color`), the drawing attribute's value reverts back to
  using the corresponding value from the *style* object.

With this behavior in mind, we now see that the PrototypedFrom version is
actually quite different from the explicit delegation approach. In the explicit
delegation version, if all Circle objects share the same Style object, then
changing any attribute in the Style object affects all Circle objects.

In the PrototypedFrom version, the case is quite different:

* If we change one of a Circle object's drawing attributes, it only affects that
  Circle object.
* If we change one of the shared Style object's attributes, it only affects
  those Circle objects with no local value set for the attribute.

It's Your Choice
----------------

Neither approach is inherently better than the other; it simply depends upon
which fits your design best. If the PrototypedFrom version seems like a better
fit, then its good to know that the PrototypedFrom facet is saving you a lot of
tedious coding::

    def draw ( self, graphics ):
        graphics.init(
            getattr( self, 'fill_color',    self.style.fill_color ),
            getattr( self, 'outline_color', self.style.outline_color ),
            getattr( self, 'outline_width', self.style.outline_width )
        )
        graphics.draw_circle( ... )

If we had used DelegatesTo instead of PrototypedFrom in our example, all
references to a Circle object's drawing attributes would *always* redirect to
the Circle object's *style* object, even when setting an attribute. So using the
DelegatesTo facet would be the same as the explicit delegation version, but with
simpler attribute references (i.e. ``circle.fill_color`` instead of
``circle.style.fill_color``).

Use of delegation is a design choice. However, once the decision is made to use
it, Facets provides several options on the best way for you to implement it in
your application.

