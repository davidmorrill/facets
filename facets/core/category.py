"""
Adds a "category" capability to Facets-based classes, similar to that provided
by the Cocoa (Objective-C) environment for the Macintosh.

You can use categories to extend an existing HasFacets class, as an alternative
to subclassing. An advantage of categories over subclassing is that you can
access the added members on instances of the original class, without having to
change them to instances of a subclass. Unlike subclassing, categories do not
allow overriding facet attributes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from has_facets \
    import MetaHasFacets, MetaHasFacetsObject

#-------------------------------------------------------------------------------
#  'MetaCategory' class:
#-------------------------------------------------------------------------------

class MetaCategory ( MetaHasFacets ):

    def __new__ ( cls, class_name, bases, class_dict ):

        # Make sure the correct usage is being applied:
        if len( bases ) > 2:
            raise TypeError(
                      'Correct usage is: class FooCategory(Category,Foo):' )

        # Process any facets-related information in the class dictionary:
        MetaCategoryObject( cls, class_name, bases, class_dict, True )

        # Move all remaining items in our class dictionary to the base class's
        # dictionary:
        if len( bases ) == 2:
            category_class = bases[ 1 ]
            for name, value in class_dict.items():
                if not hasattr( category_class, name ):
                    setattr( category_class, name, value )
                    del class_dict[ name ]

        # Finish building the class using the updated class dictionary:
        return type.__new__( cls, class_name, bases, class_dict )

#-------------------------------------------------------------------------------
#  'MetaCategoryObject' class:
#-------------------------------------------------------------------------------

class MetaCategoryObject ( MetaHasFacetsObject ):

    #-- Public Methods ---------------------------------------------------------

    def add_facets_meta_data ( self, bases, class_dict, base_facets,
                               class_facets, instance_facets, prefix_facets,
                               listeners, view_elements, implements_class ):
        """ Adds the facets meta-data to the class.
        """
        if len( bases ) == 2:
            # Update the class and each of the existing subclasses:
            bases[1]._add_facet_category( base_facets, class_facets,
                      instance_facets, prefix_facets, listeners, view_elements,
                      implements_class )
        else:
            MetaHasFacetsObject.add_facets_meta_data( self, bases,
                   class_dict, base_facets, class_facets, instance_facets,
                   prefix_facets, listeners, view_elements, implements_class )

#-------------------------------------------------------------------------------
#  'Category' class:
#-------------------------------------------------------------------------------

class Category ( object ):
    """ Used for defining "category" extensions to existing classes.

        To define a class as a category, specify "Category," followed by the
        name of the base class name in the base class list.

        The following example demonstrates defining a category::

            from facets.core_api import HasFacets, Str, Category

            class Base(HasFacets):
                x = Str("Base x")
                y = Str("Base y")

            class BaseExtra(Category, Base):
                z = Str("BaseExtra z")
    """

    __metaclass__ = MetaCategory

#-- EOF ------------------------------------------------------------------------