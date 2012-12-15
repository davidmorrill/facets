"""
The Qt specific implementation of a menu manager.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide.QtCore \
    import QPoint

from PySide.QtGui \
    import QMenu

from facets.core_api \
    import Unicode

from facets.ui.pyface.action.action_manager \
    import ActionManager

from facets.ui.pyface.action.action_manager_item \
    import ActionManagerItem

from facets.ui.pyface.action.group \
    import Group

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

    #-- MenuManager Interface --------------------------------------------------

    def create_menu ( self, parent, controller = None ):
        """ Creates a menu representation of the manager. """

        # If a controller is required it can either be set as a facet on the
        # menu manager (the facet is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # facet).
        if controller is None:
            controller = self.controller

        return _Menu( self, parent, controller )

    #-- ActionManagerItem Interface --------------------------------------------

    def add_to_menu ( self, parent, menu, controller ):
        """ Adds the item to a menu. """

        submenu = self.create_menu( parent, controller )
        submenu.menuAction().setText( self.name )
        menu.addMenu( submenu )


    def add_to_toolbar ( self, parent, tool_bar, image_cache, controller ):
        """ Adds the item to a tool bar. """

        raise ValueError( "Cannot add a menu manager to a toolbar." )

#-------------------------------------------------------------------------------
#  '_Menu' class:
#-------------------------------------------------------------------------------

class _Menu ( QMenu ):
    """ The toolkit-specific menu control.
    """

    #-- object Interface -------------------------------------------------------

    def __init__ ( self, manager, parent, controller ):
        """ Creates a new tree.
        """
        # Base class constructor:
        QMenu.__init__( self, parent )

        # The parent of the menu:
        self._parent = parent

        # The manager that the menu is a view of:
        self._manager = manager

        # The controller:
        self._controller = controller

        # Create the menu structure:
        self.refresh()

        # Listen to the manager being updated:
        self._manager.on_facet_set( self.refresh, 'changed' )
        self._manager.on_facet_set( self._on_enabled_modified, 'enabled' )

    #-- _Menu Interface --------------------------------------------------------

    def is_empty ( self ):
        """ Is the menu empty?
        """
        return self.isEmpty()


    def refresh ( self ):
        """ Ensures that the menu reflects the state of the manager.
        """
        self.clear()

        manager = self._manager
        parent  = self._parent

        previous_non_empty_group = None

        for group in manager.groups:
            previous_non_empty_group = self._add_group(
                parent, group, previous_non_empty_group
            )


    def show ( self, x, y ):
        """ Show the menu at the specified location.
        """
        self.popup( QPoint( x, y ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _on_enabled_modified ( self, obj, facet_name, old, new ):
        """ Dynamic facet change handler. """

        self.setEnabled( new )

        return

    #-- Private Methods --------------------------------------------------------

    def _add_group ( self, parent, group, previous_non_empty_group = None ):
        """ Adds a group to a menu. """

        if len( group.items ) > 0:
            # Is a separator required?
            if (previous_non_empty_group is not None) and group.separator:
                self.addSeparator()

            # Create actions and sub-menus for each contribution item in
            # the group:
            for item in group.items:
                if isinstance( item, Group ):
                    if len( item.items ) > 0:
                        self._add_group( parent, item,
                                         previous_non_empty_group )

                        if ((previous_non_empty_group is not None) and
                            previous_non_empty_group.separator     and
                            item.separator):
                            self.addSeparator()

                        previous_non_empty_group = item

                else:
                    item.add_to_menu( parent, self, self._controller )

            previous_non_empty_group = group

        return previous_non_empty_group

#-- EOF ------------------------------------------------------------------------