"""
Abstract base class for all action manager items.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Bool, HasFacets, Instance, Str

#-------------------------------------------------------------------------------
#  'ActionManagerItem' class:
#-------------------------------------------------------------------------------

class ActionManagerItem ( HasFacets ):
    """ Abstract base class for all action manager items.

        An action manager item represents a contribution to a shared UI resource
        such as a menu bar, menu or tool bar.

        Action manager items know how to add themselves to menu bars, menus and
        tool bars.  In a tool bar a contribution item is represented as a tool
        or a separator.  In a menu bar a contribution item is a menu, and in a
        menu a contribution item is a menu item or separator.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The item's unique identifier ('unique' in this case means unique within
    # its group):
    id = Str

    # The group the item belongs to:
    parent = Instance( 'facets.ui.pyface.action.api.Group' )

    # Is the item enabled?
    enabled = Bool( True )

    # Is the item visible?
    visible = Bool( True )

    #-- 'ActionManagerItem' Interface ------------------------------------------

    def add_to_menu ( self, parent, menu, controller ):
        """ Adds the item to a menu.
        """
        raise NotImplementedError


    def add_to_toolbar ( self, parent, tool_bar, image_cache, controller ):
        """ Adds the item to a tool bar.
        """
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------