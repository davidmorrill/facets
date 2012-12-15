"""
The 'null' backend specific implementation of the tool bar manager.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Bool, Enum, Instance, Tuple

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

    # The size of tool images (width, height).
    image_size = Tuple( ( 16, 16 ) )

    # The orientation of the toolbar.
    orientation = Enum( 'horizontal', 'vertical' )

    # Should we display the name of each tool bar tool under its image?
    show_tool_names = Bool( True )

    # Should we display the horizontal divider?
    show_divider = Bool( True )

    #-- Private interface ------------------------------------------------------

    # Cache of tool images (scaled to the appropriate size).
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

        return None

#-- EOF ------------------------------------------------------------------------