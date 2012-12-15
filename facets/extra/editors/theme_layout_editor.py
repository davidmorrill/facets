"""
Defines a custom ThemeLayoutEditor editor for testing what a layout using a
specified theme will look like.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Range, Str, Color, Image, on_facet_set

from facets.ui.theme \
    import LEFT

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

#-------------------------------------------------------------------------------
#  '_ThemeLayoutEditor' class:
#-------------------------------------------------------------------------------

class _ThemeLayoutEditor ( ControlEditor ):
    """ Defines a custom control used to implement the ThemeLayoutEditor for
        testing what a layout using a specified theme will look like.
    """

    #-- ThemedWindow Method Overrides ------------------------------------------

    def paint ( self, g ):
        """ Draws the contents of the control in the graphics context specified
            by *g*.
        """
        factory      = self.factory
        theme        = self.value
        cdx, cdy     = self.control.client_size
        x0           = factory.left_margin
        adx          = cdx - x0 - factory.right_margin
        y            = factory.top_margin
        ady          = cdy - y - factory.bottom_margin
        hdx, vdy     = factory.horizontal_spacing, factory.vertical_spacing
        rows         = factory.rows
        columns      = factory.columns
        icon         = factory.icon
        text         = factory.text.replace( '\\n', '\n' )
        label        = factory.label
        calc_size    = (icon is not None) or (text != '')
        tdx          = (adx - ((columns - 1) * hdx)) / columns
        content_font = theme.content_font
        label_font   = theme.label_font

        if calc_size:
            g.font = content_font
            _, tdy = theme.size_for( g, text, icon )
            rows = (ady + tdy + (2 * vdy) - 1) / (tdy + vdy)
        else:
            tdy = (ady - ((rows - 1) * vdy)) / rows

        g.pen   = None
        g.brush = factory.bg_color
        g.draw_rectangle( 0, 0, cdx, cdy )

        for r in xrange( rows ):
            x = x0
            for c in xrange( columns ):
                theme.fill( g, x, y, tdx, tdy )
                g.font = content_font
                theme.draw_text( g, text, LEFT, x, y, tdx, tdy, icon )
                if theme.has_label:
                    g.font = label_font
                    theme.draw_label( g, label, None, x, y, tdx, tdy, icon )

                x += (tdx + hdx)

            y += (tdy + vdy)

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:[rows, columns, vertical_spacing, horizontal_spacing, left_margin, right_margin, top_margin, bottom_margin, text, label, icon, bg_color]' )
    def _factory_modified ( self ):
        """ Handles any of the factory facets affecting the appearance of the
            control being changed.
        """
        self.refresh()


    @on_facet_set( 'value.[image.modified, border:-, content.-, label:-, alignment, content_color, label_color]' )
    def _theme_modified ( self ):
        """ Handles any of the theme facets affecting thr appearance of the
            control being changed.
        """
        self.refresh()


    def _control_set ( self, control ):
        """ Handles the 'control' facet being changed.
        """
        if control is not None:
            control.min_size = ( 100, 100 )

#-------------------------------------------------------------------------------
#  'ThemeLayoutEditor'
#-------------------------------------------------------------------------------

class ThemeLayoutEditor ( CustomControlEditor ):
    """ Defines a custom ThemeLayoutEditor editor for testing what a layout
        using a specified theme will look like.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The custom control class to be instantiated:
    klass = _ThemeLayoutEditor

    # The number of rows of theme layout items to display:
    rows = Range( 1, None, 1, facet_value = True )

    # The number of columns of theme layout items to display:
    columns = Range( 1, None, 1, facet_value = True )

    # The amount of vertical spacing between rows of items:
    vertical_spacing = Range( 0, None, 0, facet_value = True )

    # The amount of horizontal spacing between columns of items:
    horizontal_spacing = Range( 0, None, 0, facet_value = True )

    # The left margin to use in the editor:
    left_margin = Range( 0, None, 0, facet_value = True )

    # The right margin to use in the editor:
    right_margin = Range( 0, None, 0, facet_value = True )

    # The top margin to use in the editor:
    top_margin = Range( 0, None, 0, facet_value = True )

    # The bottom margin to use in the editor:
    bottom_margin = Range( 0, None, 0, facet_value = True )

    # The text to display in each layout item:
    text = Str( facet_value = True )

    # The label text to display in each layout item:
    label = Str( facet_value = True )

    # The icon to display to the left of the text in each layout item:
    icon = Image( facet_value = True )

    # The background color to use:
    bg_color = Color( 0x404040, facet_value = True )

#-- Run the text case (if invoked from the command line) -----------------------

if __name__ == '__main__':

    from facets.api import HasFacets, ATheme, View, UItem

    class Test ( HasFacets ):

        theme = ATheme( '@xform:li?H61L18S36|l61L66' )

        view = View(
            UItem( 'theme',
                   editor = ThemeLayoutEditor(
                       rows               = 12,
                       columns            = 1,
                       horizontal_spacing = 0,
                       vertical_spacing   = 0,
                       left_margin        = 0,
                       right_margin       = 0,
                       top_margin         = 1,
                       bottom_margin      = 0,
                       bg_color           = 0xB0B0B0,
                       text               = 'This is a sample\nwith multiple lines',
                       image              = '@icons2:Clock_1'
                   )
            ),
            width  = 0.6,
            height = 0.6
        )

    Test().edit_facets()

#-- EOF ------------------------------------------------------------------------
