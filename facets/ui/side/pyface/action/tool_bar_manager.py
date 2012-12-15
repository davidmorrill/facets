"""
Defines a ToolBarManager class that realizes itself in a tool bar control.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide \
    import QtCore, QtGui

from facets.core_api \
    import Bool, Enum, Instance, Str, Tuple

from facets.ui.pyface.image_cache \
    import ImageCache

from facets.ui.pyface.action.action_manager \
    import ActionManager

#-------------------------------------------------------------------------------
#  'ToolBarManager' class:
#-------------------------------------------------------------------------------

class ToolBarManager ( ActionManager ):
    """ A tool bar manager realizes itself in a tool bar control.
    """

    #-- 'ToolBarManager' interface ---------------------------------------------

    # Is the tool bar enabled?
    enabled = Bool( True )

    # Is the tool bar visible?
    visible = Bool( True )

    # The size of tool images (width, height):
    image_size = Tuple( ( 16, 16 ) )

    # The toolbar name (used to distinguish multiple toolbars):
    name = Str( 'ToolBar' )

    # The orientation of the toolbar:
    orientation = Enum( 'horizontal', 'vertical' )

    # Should we display the name of each tool bar tool under its image?
    show_tool_names = Bool( True )

    # Should we display the horizontal divider?
    show_divider = Bool( True )

    #-- Private interface ------------------------------------------------------

    # Cache of tool images (scaled to the appropriate size).
    _image_cache = Instance( ImageCache )

    #-- object Interface -------------------------------------------------------

    def __init__ ( self, *args, **facets ):
        """ Creates a new tool bar manager.
        """
        # Base class contructor:
        super( ToolBarManager, self ).__init__( *args, **facets )

        # An image cache to make sure that we only load each image used in the
        # tool bar exactly once:
        self._image_cache = ImageCache( self.image_size[0], self.image_size[1] )

    #-- ToolBarManager Interface -----------------------------------------------

    def create_tool_bar ( self, parent, controller = None ):
        """ Creates a tool bar.
        """
        # If a controller is required it can either be set as a facet on the
        # tool bar manager (the facet is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # facet).
        if controller is None:
            controller = self.controller

        # Create the control:
        tool_bar = _ToolBar( self, parent )

        tool_bar.setObjectName( self.id )

        if self.show_tool_names:
            tool_bar.setToolButtonStyle( QtCore.Qt.ToolButtonTextUnderIcon )

        if self.orientation == 'horizontal':
            tool_bar.setOrientation( QtCore.Qt.Horizontal )
        else:
            tool_bar.setOrientation( QtCore.Qt.Vertical )

        # We would normally leave it to the current style to determine the icon
        # size:
        tool_bar.setIconSize( QtCore.QSize( *self.image_size ) )

        # Add all of items in the manager's groups to the tool bar.
        self._side_add_tools( parent, tool_bar, controller )

        return tool_bar

    #-- Private Interface ------------------------------------------------------

    def _side_add_tools ( self, parent, tool_bar, controller ):
        """ Adds tools for all items in the list of groups.
        """
        previous_non_empty_group = None
        for group in self.groups:
            if len( group.items ) > 0:
                # Is a separator required?
                if previous_non_empty_group is not None and group.separator:
                    tool_bar.addSeparator()

                previous_non_empty_group = group

                # Create a tool bar tool for each item in the group:
                for item in group.items:
                    item.add_to_toolbar(
                        parent,
                        tool_bar,
                        self._image_cache,
                        controller,
                        self.show_tool_names
                    )

#-------------------------------------------------------------------------------
#  '_ToolBar' class:
#-------------------------------------------------------------------------------

class _ToolBar ( QtGui.QToolBar ):
    """ The toolkit-specific tool bar implementation.
    """

    #-- object Interface -------------------------------------------------------

    def __init__ ( self, tool_bar_manager, parent ):
        """ Initializes the object.
        """
        QtGui.QToolBar.__init__( self, parent )

        # Listen for changes to the tool bar manager's enablement and
        # visibility:
        self.tool_bar_manager = tool_bar_manager

        tool_bar_manager.on_facet_set(
            self._on_tool_bar_manager_enabled_modified, 'enabled'
        )

        tool_bar_manager.on_facet_set(
            self._on_tool_bar_manager_visible_modified, 'visible'
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _on_tool_bar_manager_enabled_modified ( self, obj, facet_name,
                                                old, new ):
        """ Dynamic facet change handler.
        """
        self.setEnabled( new )


    def _on_tool_bar_manager_visible_modified ( self, obj, facet_name,
                                                old, new ):
        """ Dynamic facet change handler.
        """
        self.setVisible( new )

#-- EOF ------------------------------------------------------------------------