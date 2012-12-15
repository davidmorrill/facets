"""
The wx specific implementation of a menu bar manager.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.ui.pyface.action.action_manager \
    import ActionManager

#-------------------------------------------------------------------------------
#  'MenuBarManager' class:
#-------------------------------------------------------------------------------

class MenuBarManager ( ActionManager ):
    """ A menu bar manager realizes itself in errr, a menu bar control.
    """

    #-- 'MenuBarManager' Interface ---------------------------------------------

    def create_menu_bar ( self, parent, controller = None ):
        """ Creates a menu bar representation of the manager.
        """
        # If a controller is required it can either be set as a facet on the
        # menu bar manager (the facet is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # facet).
        if controller is None:
            controller = self.controller

        menu_bar = wx.MenuBar()

        # Every item in every group must be a menu manager:
        for group in self.groups:
            for item in group.items:
                menu = item.create_menu( parent, controller )
                menu_bar.Append( menu, item.name )

        return menu_bar

#-- EOF ------------------------------------------------------------------------