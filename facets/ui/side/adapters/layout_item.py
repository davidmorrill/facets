"""
Defines a Qt4 specific concrete implementation of the LayoutItem base class that
adapts a Qt4 layout manager item to provide a set of toolkit neutral properties
and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.adapters.layout_item \
    import LayoutItem

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def adapted_layout_item ( layout_item ):
    """ Returns a correctly adapted version of the specified layout mananger
        item.
    """
    if layout_item is None:
        return None

    return layout_item_adapter( layout_item )


def layout_item_adapter ( layout_item ):
    """ Returns the layout item adapter associated with the specified layout
        manager item.
    """
    adapter = getattr( layout_item, 'adapter', None )
    if adapter is not None:
        return adapter

    return QtLayoutItem( layout_item )

#-------------------------------------------------------------------------------
#  'QtLayoutItem' class:
#-------------------------------------------------------------------------------

class QtLayoutItem ( LayoutItem ):
    """ Defines an Qt4 specific concrete implementation of the LayoutItem base
        class that adapts a Qt4 layout manager item to provide a set of toolkit
        neutral properties and methods.
    """

    #-- LayoutItem Property Implementations ------------------------------------

    def _get_control ( self ):
        from control import adapted_control

        return adapted_control( self.layout_item.widget() )


    def _get_layout ( self ):
        from layout import adapted_layout

        return adapted_layout( self.layout_item.layout() )

#-- EOF ------------------------------------------------------------------------