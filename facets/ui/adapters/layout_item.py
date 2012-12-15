"""
Defines an LayoutItem base class that each GUI toolkit backend must provide a
concrete implementation of.

The LayoutItem class adapts a GUI toolkit layout manager item to provide a set
of toolkit neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Any, Property

#-------------------------------------------------------------------------------
#  'LayoutItem' class:
#-------------------------------------------------------------------------------

class LayoutItem ( HasPrivateFacets ):
    """ Abstract adapter base class that allows a GUI toolkit specific layout
        manager item to provide a set of toolkit neutral properties and methods.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The GUI toolkit specific layout manager item being adapted:
    layout_item = Any

    # The adapted control associated with this item:
    control = Property

    # The adapted layout associated with this item:
    layout = Property

    # The children of this item:
    children = Property

    #-- Method Implementations -------------------------------------------------

    def __init__ ( self, layout_item, **facets ):
        """ Initializes the object by saving the layout manager item being
            adapted.
        """
        super( LayoutItem, self ).__init__( **facets )

        self.layout_item    = layout_item
        layout_item.adapter = self


    def __call__ ( self ):
        """ Returns the layout manager item being adapted.
        """
        return self.layout_item


    def destroy ( self ):
        """ Destroys the associated layout manager item.
        """
        item = self.control or self.layout
        if item is not None:
            item.destroy()

    #-- Property Implementations -----------------------------------------------

    def _get_control ( self ):
        raise NotImplementedError


    def _get_layout ( self ):
        raise NotImplementedError


    def _get_children ( self ):
        item = self.control or self.layout
        if item is not None:
            return item.children

        return []

#-- EOF ------------------------------------------------------------------------