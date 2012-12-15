"""
The 'null' specific implementations of the action manager internal classes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Any, Bool, HasFacets

#-------------------------------------------------------------------------------
#  '_MenuItem' class:
#-------------------------------------------------------------------------------

class _MenuItem ( HasFacets ):
    """ A menu item representation of an action item. """

    #-- '_MenuItem' interface --------------------------------------------------

    # Is the item checked?
    checked = Bool( False )

    # A controller object we delegate taking actions through (if any).
    controller = Any

    # Is the item enabled?
    enabled = Bool( True )

    # Is the item visible?
    visible = Bool( True )

    # The radio group we are part of (None if the menu item is not part of such
    # a group).
    group = Any

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, parent, menu, item, controller ):
        """ Creates a new menu item for an action item.
        """
        self.item       = item
        self.control_id = 1
        self.control    = None

        if controller is not None:
            self.controller = controller
            controller.add_to_menu( self )

#-------------------------------------------------------------------------------
#  '_Tool' Class:
#-------------------------------------------------------------------------------

class _Tool ( HasFacets ):
    """ A tool bar tool representation of an action item.
    """

    #-- '_Tool' interface ------------------------------------------------------

    # Is the item checked?
    checked = Bool( False )

    # A controller object we delegate taking actions through (if any).
    controller = Any

    # Is the item enabled?
    enabled = Bool( True )

    # Is the item visible?
    visible = Bool( True )

    # The radio group we are part of (None if the tool is not part of such a
    # group).
    group = Any

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, parent, tool_bar, image_cache, item, controller,
                 show_labels ):
        """ Creates a new tool bar tool for an action item.
        """
        self.item     = item
        self.tool_bar = tool_bar

        # Create an appropriate tool depending on the style of the action:
        action  = self.item.action

        # If the action has an image then convert it to a bitmap (as required
        # by the toolbar):
        if action.image is not None:
            image = action.image.create_image()
            path  = action.image.absolute_path
            bmp   = image_cache.get_bitmap( path )
        else:
            from facets.ui.pyface.api import ImageResource

            image = ImageResource( 'foo' )
            bmp   = image.create_bitmap()

        self.control_id = 1
        self.control    = None
        if controller is not None:
            self.controller = controller
            controller.add_to_toolbar( self )

#-------------------------------------------------------------------------------
#  '_PaletteTool' class:
#-------------------------------------------------------------------------------

class _PaletteTool ( HasFacets ):
    """ A tool palette representation of an action item.
    """

    #-- '_PaletteTool' interface -----------------------------------------------

    # The radio group we are part of (None if the tool is not part of such a
    # group).
    group = Any

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, tool_palette, image_cache, item, show_labels ):
        """ Creates a new tool palette tool for an action item. """
        self.item         = item
        self.tool_palette = tool_palette

#-- EOF ------------------------------------------------------------------------