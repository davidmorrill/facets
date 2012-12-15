"""
Defines the MenuBarManager class that realizes itself in a menu bar control.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide \
    import QtGui

from facets.ui.pyface.action.action_manager \
    import ActionManager

#-------------------------------------------------------------------------------
#  'MenuBarManager' class:
#-------------------------------------------------------------------------------

class MenuBarManager ( ActionManager ):
    """ A menu bar manager realizes itself in a menu bar control.
    """

    #-- MenuBarManager Interface -----------------------------------------------

    def create_menu_bar ( self, parent, controller = None ):
        """ Creates a menu bar representation of the manager.
        """
        # If a controller is required it can either be set as a facet on the
        # menu bar manager (the facet is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # facet).
        if controller is None:
            controller = self.controller

        menu_bar = QtGui.QMenuBar( parent )

        # Every item in every group must be a menu manager:
        for group in self.groups:
            for item in group.items:
                menu = item.create_menu( parent, controller )
                menu.menuAction().setText( item.name )
                menu_bar.addMenu( menu )

        return menu_bar

#-- EOF ------------------------------------------------------------------------