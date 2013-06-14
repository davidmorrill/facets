"""
View of an ActionManager drawn as a rectangle of buttons.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.ui.pyface.widget \
    import Widget

from facets.core_api \
    import Bool, Dict, Int, List, Tuple

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# HTML templates.
# FIXME : Not quite the right color.
HTML = """

<html>
  <body bgcolor='#cccccc'>
    %s
  </body>
</html>

"""


PART = ( '<wxp module="wx" class="Panel"><param name="id" value="%s">'
        '<param name="size" value="%s"></wxp>' )

#-------------------------------------------------------------------------------
#  'ToolPalette' class:
#-------------------------------------------------------------------------------

class ToolPalette ( Widget ):

    #-- Facet Definitions ------------------------------------------------------

    tools = List

    id_tool_map = Dict

    tool_id_to_button_map = Dict

    button_size = Tuple( ( 25, 25 ), Int, Int )

    is_realized = Bool( False )

    tool_listeners = Dict

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

    #-- 'ToolPalette' Interface ------------------------------------------------

    def add_tool ( self, label, bmp, kind, tooltip, longtip ):
        """ Add a tool with the specified properties to the palette.

            Return an id that can be used to reference this tool in the future.
        """
        wxid   = wx.NewId()
        params = ( wxid, label, bmp, kind, tooltip, longtip )
        self.tools.append( params )
        self.id_tool_map[ wxid ] = params

        if self.is_realized:
            self._reflow()

        return wxid


    def toggle_tool ( self, id, checked ):
        """ Toggle the tool identified by 'id' to the 'checked' state.

            If the button is a toggle or radio button, the button will be
            checked if the 'checked' parameter is True; unchecked otherwise. If
            the button is a standard button, this method is a NOP.
        """
        button = self.tool_id_to_button_map.get( id, None )
        if button is not None and hasattr( button, 'SetToggle' ):
            button.SetToggle( checked )


    def enable_tool ( self, id, enabled ):
        """ Enable or disable the tool identified by 'id'.
        """
        button = self.tool_id_to_button_map.get( id, None )
        if button is not None:
            button.SetEnabled( enabled )


    def on_tool_event ( self, id, callback ):
        """ Register a callback for events on the tool identified by 'id'.
        """
        callbacks = self.tool_listeners.setdefault( id, [ ] )
        callbacks.append( callback )


    def realize ( self ):
        """ Realize the control so that it can be displayed.
        """
        self.is_realized = True
        self._reflow()


    def get_tool_state ( self, id ):
        """ Get the toggle state of the tool identified by 'id'.
        """
        button = self.tool_id_to_button_map.get( id, None )
        if hasattr( button, 'GetToggle' ):
            if button.GetToggle():
                state = 1
            else:
                state = 0
        else:
            state = 0

        return state

    #-- Private Methods --------------------------------------------------------

    def _create_control ( self, parent ):

        return wx.html.HtmlWindow( parent, -1, style = wx.CLIP_CHILDREN )


    def _reflow ( self ):
        """ Reflow the layout.
        """
        # Create a bit of html for each tool:
        parts = []
        for param in self.tools:
            parts.append( PART % ( str( param[ 0 ] ), self.button_size ) )

        # Create the entire html page:
        html = HTML % ''.join( parts )

        # Set the HTML on the widget.  This will create all of the buttons:
        self.control.SetPage( html )

        for param in self.tools:
            self._initialize_tool( param )


    def _initialize_tool ( self, param ):
        """ Initialize the tool palette button.
        """
        wxid, label, bmp, kind, tooltip, longtip = param

        panel = self.control.FindWindowById( wxid )
        sizer = wx.BoxSizer( wx.VERTICAL )
        panel.SetSizer( sizer )
        panel.SetAutoLayout( True )
        panel.SetWindowStyleFlag( wx.CLIP_CHILDREN )

        from wx.lib.buttons import GenBitmapToggleButton, GenBitmapButton

        if kind == 'radio':
            button = GenBitmapToggleButton( panel, -1, None,
                                            size = self.button_size )

        else:
            button = GenBitmapButton( panel, -1, None, size = self.button_size )

        self.button_tool_map[ button.GetId() ] = wxid
        self.tool_id_to_button_map[ wxid ] = button
        wx.EVT_BUTTON( panel, button.GetId(), self._on_button )
        button.SetBitmapLabel( bmp )
        button.SetToolTipString( label )
        sizer.Add( button, 0, wx.EXPAND )


    def _on_button ( self, event ):
        button_id = event.GetId()
        tool_id   = self.button_tool_map.get( button_id, None )
        if tool_id is not None:
            for listener in self.tool_listeners.get( tool_id, [ ] ):
                listener( event )

#-- EOF ------------------------------------------------------------------------