"""
# Web Color Picker #

Defines a tool for picking *web* style colors and placing the color in the
system clipboard for easy pasting into other applications. It supports HTML
style (i.e. #RRGGBB), CSS style (i.e. rgb(R,G,B)) and Hex (i.e. 0xRRGGBB)
formats.

Demonstrates use of:

 - The **HLSColorEditor**.
 - The **NotebookEditor**.
 - Accessing the system clipboard object via *toolkit().clipboard()*.

Multiple color pickers can be created by clicking the plus icon located in the
lower right hand corner of the main view. This creates a clone of the currently
selected color picker. This can be handy when experimenting with different color
variations such as changing saturation or hue. The individual color pickers can
also be easily reorganized by dragging their tabs or splitter bars. Pickers can
even dragged out of the main view to operate as stand-alone desktop windows.

Each color picker also has the ability to accept text colors from the system
clipboard in any of the three formats (i.e. #RRGGBB, rgb(r,g,b) or 0xRRGGBB).
To paste a color, click on the clipboard icon located in the lower left hand
corner of each color picker.

Besides being a nice simple demo, it is also a handy tool that was originally
written by the author when he needed to enter a bunch of web color values into
a file being edited. It was also later used interactively with Firebug in the
Firefox web browser to tune the CSS style sheet colors used in the Facets
documentation.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, RGBInt, Enum, Button, List, Instance, Property,  \
           View, VGroup, HGroup, UItem, Item, HLSColorEditor, NotebookEditor, \
           property_depends_on, spring, toolkit

#-------------------------------------------------------------------------------
#  'WebColorPicker' class:
#-------------------------------------------------------------------------------

class WebColorPicker ( HasPrivateFacets ):
    """ Defines the WebColorPicker class for picking 'web' style colors (i.e.
        #RRGGBB) and placing the color in the system clipboard for easy pasting
        into other applications.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current color:
    color = RGBInt( 0x9090FF )

    # The presentation style to use:
    style = Enum( 'HTML', 'CSS', 'Hex' )

    # The current color (in #RRGGBB format):
    html_color = Property

    # The current color (in rgb(R,G,B) format):
    css_color = Property

    # The current color (in 0xRRGGBB format):
    hex_color = Property

    # The current color in the selected style:
    web_color = Property

    # The event fired when the 'Paste from Clipboard' button is clicked:
    paste = Button( '@icons2:ClipboardPaste' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HGroup(
            UItem( 'color',
                   springy = True,
                   editor  = HLSColorEditor(
                                  cell_size = 16, space = 0, edit = 'all' )
            ),
            UItem( 'color',
                   width  = -52,
                   editor = HLSColorEditor( cell_size = 40, edit = 'any' )
            ),
            group_theme = '#themes:tool_options_group'
        ),
        HGroup(
            UItem( 'paste' ),
            '_',
            Item( 'style' ),
            '_',
            UItem( 'web_color', style = 'readonly', springy = True ),
            group_theme = '#themes:toolbar'
        )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'color' )
    def _get_html_color ( self ):
        return ('#%02X%02X%02X' % self.color )


    @property_depends_on( 'color' )
    def _get_css_color ( self ):
        return ('rgb(%d,%d,%d)' % self.color )


    @property_depends_on( 'color' )
    def _get_hex_color ( self ):
        return ('0x%02X%02X%02X' % self.color )


    @property_depends_on( 'color, style' )
    def _get_web_color ( self ):
        if self.style == 'Hex':
            return self.hex_color

        return (self.html_color if self.style == 'HTML' else self.css_color)

    #-- Public Methods ---------------------------------------------------------

    def update_clipboard ( self ):
        """ Copies the current color to the system clipboard.
        """
        toolkit().clipboard().text = self.web_color

    #-- Facet Event Handlers ---------------------------------------------------

    def _web_color_set ( self ):
        """ Handles the 'web_color' facet being changed.
        """
        self.update_clipboard()


    def _paste_set ( self ):
        """ Handles the 'paste' button being clicked.
        """
        text = toolkit().clipboard().text
        if text.startswith( '#' ):
            try:
                self.color = int( text[1:], 16 )
            except:
                pass
        elif text.startswith( 'rgb(' ):
            try:
                rgb = [ int( c ) for c in text[4:].strip( ')' ).split( ',' ) ]
                if len( rgb ) == 3:
                    self.color = (rgb[0] * 65536) + (rgb[1] * 256) + rgb[2]
            except:
                pass
        elif text.lower().startswith( '0x' ):
            try:
                self.color = int( text[2:], 16 )
            except:
                pass

#-------------------------------------------------------------------------------
#  'WebColors' class:
#-------------------------------------------------------------------------------

class WebColors ( HasPrivateFacets ):
    """ Defines the WebColors class for creating an organizable collection of
        WebColorPicker objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current collection of WebColorPicker objects:
    pickers = List

    # The currently selected WebColorPicker:
    selected = Instance( WebColorPicker )

    # The event fired when the user wants to clone the current color picker:
    clone = Button( '@icons2:Add_2' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            UItem( 'pickers',
                   editor = NotebookEditor(
                       deletable = True,
                       export    = 'DockShellWindow',
                       selected  = 'selected',
                       layout    = 'columns',
                       max_items = 1 )
            ),
            HGroup(
                spring,
                UItem( 'clone',
                       tooltip = 'Create a copy of the current color picker',
                       enabled_when = 'selected is not None'
                ),
                group_theme = '@xform:b?L25'
            )
        ),
        title     = 'Web Color Picker',
        id        = 'facets.extra.demo.ui.Applications.web_color_picker',
        width     = 0.33,
        height    = 0.50,
        resizable = True
    )

    #-- Facet Default Values ---------------------------------------------------

    def _pickers_default ( self ):
        return [ WebColorPicker() ]


    def _selected_default ( self ):
        return self.pickers[0]

    #-- Facet Event Handlers ---------------------------------------------------

    def _clone_set ( self ):
        """ Handles the clone button being clicked.
        """
        selected = self.selected
        self.pickers.append( WebColorPicker(
            color = selected.color,
            style = selected.style
        ) )
        self.selected = self.pickers[-1]


    def _selected_set ( self, selected ):
        """ Handles the current color picker being changed.
        """
        if selected is not None:
            selected.update_clipboard()

#-- Create the demo ------------------------------------------------------------

demo = WebColors

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
