"""
The wx specific implementation of the tool bar manager.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

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
    """ A tool bar manager realizes itself in errr, a tool bar control.
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
    show_divider = Bool( False )

    #-- Private Facets ---------------------------------------------------------

    # Cache of tool images (scaled to the appropriate size):
    _image_cache = Instance( ImageCache )

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, *args, **facets ):
        """ Creates a new tool bar manager.
        """
        # Base class contructor:
        super( ToolBarManager, self ).__init__( *args, **facets )

        # An image cache to make sure that we only load each image used in the
        # tool bar exactly once:
        self._image_cache = ImageCache( self.image_size[0], self.image_size[1] )

    #-- 'ToolBarManager' Interface ---------------------------------------------

    def create_tool_bar ( self, parent, controller = None ):
        """ Creates a tool bar.
        """
        # If a controller is required it can either be set as a facet on the
        # tool bar manager (the facet is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # facet).
        if controller is None:
            controller = self.controller

        # Determine the wx style for the tool bar based on any optional
        # settings:
        style = wx.NO_BORDER | wx.TB_FLAT | wx.CLIP_CHILDREN

        if self.show_tool_names:
            style |= wx.TB_TEXT

        if self.orientation == 'horizontal':
            style |= wx.TB_HORIZONTAL

        else:
            style |= wx.TB_VERTICAL

        if not self.show_divider:
            style |= wx.TB_NODIVIDER

        # Create the control:
        tool_bar = _ToolBar( self, parent, -1, style = style )

        # fixme: Setting the tool bitmap size seems to be the only way to
        # change the height of the toolbar in wx.
        tool_bar.SetToolBitmapSize( self.image_size )

        # Add all of items in the manager's groups to the tool bar:
        self._wx_add_tools( parent, tool_bar, controller )

        # Make the tools appear in the tool bar (without this you will not see
        # anything):
        tool_bar.Realize()

        # fixme: Without the following hack,  only the first item in a radio
        # group can be selected when the tool bar is first realised 8^()
        self._wx_set_initial_tool_state( tool_bar )

        return tool_bar

    #-- Private Methods --------------------------------------------------------

    def _wx_add_tools ( self, parent, tool_bar, controller ):
        """ Adds tools for all items in the list of groups.
        """
        previous_non_empty_group = None
        for group in self.groups:
            if len( group.items ) > 0:
                # Is a separator required?
                if previous_non_empty_group is not None and group.separator:
                    tool_bar.AddSeparator()

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


    def _wx_set_initial_tool_state ( self, tool_bar ):
        """ Workaround for the wxPython tool bar bug.

            Without this,  only the first item in a radio group can be selected
            when the tool bar is first realised 8^()
        """
        for group in self.groups:
            checked = False
            for item in group.items:
                # If the group is a radio group,  set the initial checked state
                # of every tool in it:
                if item.action.style == 'radio':
                    tool_bar.ToggleTool( item.control_id, item.action.checked )
                    checked = checked or item.action.checked

                # Every item in a radio group MUST be 'radio' style, so we
                # can just skip to the next group:
                else:
                    break

            # We get here if the group is a radio group:
            else:
                # If none of the actions in the group is specified as 'checked'
                # we will check the first one:
                if not checked and len( group.items ) > 0:
                    group.items[ 0 ].action.checked = True

#-------------------------------------------------------------------------------
#  '_ToolBar' class:
#-------------------------------------------------------------------------------

class _ToolBar ( wx.ToolBar ):
    """ The toolkit-specific tool bar implementation.
    """

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, tool_bar_manager, parent, id, style ):
        """ Constructor.
        """
        wx.ToolBar.__init__( self, parent, -1, style = style )

        # Listen for changes to the tool bar manager's enablement and
        # visibility:
        self.tool_bar_manager = tool_bar_manager

        self.tool_bar_manager.on_facet_set(
            self._on_tool_bar_manager_enabled_modified, 'enabled'
        )

        self.tool_bar_manager.on_facet_set(
            self._on_tool_bar_manager_visible_modified, 'visible'
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _on_tool_bar_manager_enabled_modified ( self, obj, facet_name,
                                                old, new ):
        """ Dynamic facet change handler.
        """
        obj.window._wx_enable_tool_bar( self, new )


    def _on_tool_bar_manager_visible_modified ( self, obj, facet_name,
                                                old, new ):
        """ Dynamic facet change handler.
        """
        obj.window._wx_show_tool_bar( self, new )

#-- EOF ------------------------------------------------------------------------