"""
View of an ActionManager drawn as a rectangle of buttons.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.pyface.widget \
    import Widget

from facets.core_api \
    import Bool, Dict, Int, List, Tuple

#-------------------------------------------------------------------------------
#  'ToolPalette' class:
#-------------------------------------------------------------------------------

class ToolPalette ( Widget ):

    #-- Facet Definitions ------------------------------------------------------

    tools                 = List
    id_tool_map           = Dict
    tool_id_to_button_map = Dict
    button_size           = Tuple( ( 25, 25 ), Int, Int )
    is_realized           = Bool( False )
    tool_listeners        = Dict

    # Maps a button id to its tool id:
    button_tool_map = Dict

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, parent, **facets ):
        """ Creates a new tool palette.
        """
        # Base class constructor:
        super( ToolPalette, self ).__init__( **facets )

        # Create the toolkit-specific control that represents the widget:
        self.control = self._create_control( parent )

    #-- ToolPalette Interface --------------------------------------------------

    def add_tool ( self, label, bmp, kind, tooltip, longtip ):
        """ Add a tool with the specified properties to the palette.

            Return an id that can be used to reference this tool in the future.
        """
        return 1


    def toggle_tool ( self, id, checked ):
        """ Toggle the tool identified by 'id' to the 'checked' state.

            If the button is a toggle or radio button, the button will be
            checked if the 'checked' parameter is True; unchecked otherwise.
            If the button is a standard button, this method is a NOP.
        """
        pass


    def enable_tool ( self, id, enabled ):
        """ Enable or disable the tool identified by 'id'.
        """
        pass


    def on_tool_event ( self, id, callback ):
        """ Register a callback for events on the tool identified by 'id'.
        """
        pass


    def realize ( self ):
        """ Realize the control so that it can be displayed.
        """
        pass


    def get_tool_state ( self, id ):
        """ Get the toggle state of the tool identified by 'id'.
        """
        return 0

    #-- Private interface ------------------------------------------------------

    def _create_control ( self, parent ):
        return None

#-- EOF ------------------------------------------------------------------------