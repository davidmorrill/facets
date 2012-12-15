"""
A tool bar manager realizes itself in a tool palette control.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Bool, Instance, Tuple

from facets.ui.pyface.image_cache \
    import ImageCache

from facets.ui.pyface.action.action_manager \
    import ActionManager

#-------------------------------------------------------------------------------
#  'ToolPaletteManager' class:
#-------------------------------------------------------------------------------

class ToolPaletteManager ( ActionManager ):
    """ A tool bar manager realizes itself in a tool palette bar control.
    """

    #-- 'ToolPaletteManager' interface -----------------------------------------

    # The size of tool images (width, height).
    image_size = Tuple( ( 16, 16 ) )

    # Should we display the name of each tool bar tool under its image?
    show_tool_names = Bool( True )

    #-- Private interface ------------------------------------------------------

    # Cache of tool images (scaled to the appropriate size).
    _image_cache = Instance( ImageCache )

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, *args, **facets ):
        """ Creates a new tool bar manager.
        """
        # Base class contructor:
        super( ToolPaletteManager, self ).__init__( *args, **facets )

        # An image cache to make sure that we only load each image used in the
        # tool bar exactly once:
        self._image_cache = ImageCache( self.image_size[0], self.image_size[1] )

    #-- 'ToolPaletteManager' Interface -----------------------------------------

    def create_tool_palette ( self, parent, controller = None ):
        """ Creates a tool bar.
        """
        return None

#-- EOF ------------------------------------------------------------------------