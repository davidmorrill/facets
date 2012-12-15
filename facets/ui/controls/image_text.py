"""
Defines a themed read-only text string.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Str, Property, ATheme, Theme, Control, \
           toolkit

#-------------------------------------------------------------------------------
#  Class 'ImageText'
#-------------------------------------------------------------------------------

class ImageText ( HasPrivateFacets ):
    """ Defines a text control that displays an ImageSlice in its background.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The underlying control:
    control = Instance( Control )

    # The theme associated with this window:
    theme = ATheme( Theme( '@facets:heading', content = ( 6, 0 ) ) )

    # The text to be displayed:
    text = Str

    # The minimum size of the control:
    min_size = Property

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        self._theme_set()


    def create_control ( self, parent ):
        """ Initializes the object.
        """
        self.control = control = toolkit().create_control( parent )

        # Set up the event handlers:
        control.set_event_handler( paint = self._on_paint )

        control.size_policy = ( 'expanding', 'fixed' )
        control.size        = control.min_size = self.min_size

        self._refresh()

        return control

    #-- Facet Event Handlers ---------------------------------------------------

    def _theme_set ( self ):
        """ Handles the 'theme' facet being changed.
        """
        if self.theme is not None:
            self._image_slice = self.theme.image_slice


    def _text_set ( self ):
        """ Handles the 'text' facet being changed.
        """
        self._refresh()

    #-- Control Event Handlers -------------------------------------------------

    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        control = self.control
        g       = control.graphics_buffer

        if self.theme is not None:
            wdx, wdy = control.client_size
            self._image_slice.fill( g, 0, 0, wdx, wdy )
            g.text_color = self._image_slice.content_color

        g.text_background_color = None
        g.font                  = control.font
        tx, ty, tdx, tdy        = self._get_text_bounds()
        g.draw_text( self.text, tx, ty )
        g.copy()

    #-- Private Methods --------------------------------------------------------

    def _refresh ( self ):
        """ Refreshes the contents of the control.
        """
        if self.control is not None:
            if self._text_size is not None:
                self.control.refresh( *self._get_text_bounds() )
                self._text_size = None

            self.control.min_size = self.min_size
            self.control.refresh( *self._get_text_bounds() )


    def _get_text_size ( self, text = None ):
        """ Returns the text size information for the window.
        """
        if self._text_size is None:
            if text is None:
                text = self.text

            if text.strip() == '':
                text = 'M'

            self._text_size = self.control.text_size( text )

        return self._text_size


    def _get_text_bounds ( self ):
        """ Get the window bounds of where the current text should be
            displayed.
        """
        tdx, tdy = self._get_text_size()
        wdx, wdy = self.control.client_size
        theme    = self.theme
        if theme is None:
            return ( wdx - tdx, (wdy - tdy) / 2, tdx, tdy )

        slice   = self._image_slice
        content = theme.content
        ty      = (wdy + slice.xtop + content.top -
                         slice.xbottom - content.bottom - tdy) / 2

        alignment = theme.alignment[:1]
        if alignment in 'ld':
            tx = slice.xleft + content.left
        elif alignment == 'c':
            tx = (wdx + slice.xleft  + content.left -
                        slice.xright - content.right - tdx) / 2
        else:
            tx = wdx - tdx - slice.xright - content.right

        return ( tx, ty, tdx, tdy )

    #-- Property Implementations -----------------------------------------------

    def _get_min_size ( self ):
        """ Returns the minimum size for the window.
        """
        tdx, tdy = self._get_text_size()
        if self.theme is None:
            return ( tdx + 8, tdy + 4 )

        content = self.theme.content
        tdx    += (content.left + content.right)
        tdy    += (content.top  + content.bottom)
        slice   = self._image_slice

        return ( max( slice.left  + slice.right,
                      slice.xleft + slice.xright + tdx ),
                 max( tdy,
                      min( slice.image.height,
                           max( slice.top   + slice.bottom,
                                slice.xtop  + slice.xbottom + tdy ) ) ) )

#-- EOF ------------------------------------------------------------------------