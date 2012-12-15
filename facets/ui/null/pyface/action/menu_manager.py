"""
The 'null' backend specific implementation of a menu manager.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Unicode

from facets.ui.pyface.action.action_manager \
    import ActionManager

from facets.ui.pyface.action.action_manager_item \
    import ActionManagerItem

#-------------------------------------------------------------------------------
#  'MenuManager' class:
#-------------------------------------------------------------------------------

class MenuManager ( ActionManager, ActionManagerItem ):
    """ A menu manager realizes itself in a menu control.

        This could be a sub-menu or a context (popup) menu.
    """

    #-- 'MenuManager' interface ------------------------------------------------

    # The menu manager's name (if the manager is a sub-menu, this is what its
    # label will be).
    name = Unicode

    #-- 'MenuManager' Interface ------------------------------------------------

    def create_menu ( self, parent, controller = None ):
        """ Creates a menu representation of the manager.
        """
        # If a controller is required it can either be set as a facet on the
        # menu manager (the facet is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # facet).
        if controller is None:
            controller = self.controller

        return None

    #-- 'ActionManagerItem' Interface ------------------------------------------

    def add_to_menu ( self, parent, menu, controller ):
        """ Adds the item to a menu.
        """
        pass

    def add_to_toolbar ( self, parent, tool_bar, image_cache, controller ):
        """ Adds the item to a tool bar.
        """
        raise ValueError( 'Cannot add a menu manager to a toolbar.' )

#-- EOF ------------------------------------------------------------------------