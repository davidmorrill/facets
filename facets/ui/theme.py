"""
Defines 'theme' related classes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Bool, Any, Tuple, Int, Font, Property, \
           property_depends_on

from toolkit \
    import toolkit

from ui_facets \
    import Image, HasBorder, HasMargin, HorizontalAlignment

from constants \
    import CENTER, LEFT, RIGHT, TOP, BOTTOM, TOP_LEFT, AlignmentMap

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The template used to convert a Theme object to a string:
ThemeTemplate = """
Theme(
    image         = r'%s',
    tiled         = %s,
    origin        = %r,
    border        = %s,
    content       = %s,
    label         = %s,
    alignment     = '%s',
    content_font  = '%s',
    label_font    = '%s',
    content_color = %s,
    label_color   = %s,
    bg_color      = %s
)
"""[1:-1]

#-------------------------------------------------------------------------------
#  'Theme' class:
#-------------------------------------------------------------------------------

class Theme ( HasPrivateFacets ):

    #-- Public Facets ----------------------------------------------------------

    # The background image to use for the theme:
    image = Image

    # Is this theme tiled (True) or stretched (False)?
    tiled = Bool( False )

    # The image origin when using a tiled theme:
    origin = Tuple( Int, Int )

    # The border inset:
    border = HasBorder

    # The margin to use around the content:
    content = HasMargin

    # The margin to use around the label:
    label = HasMargin

    # Does the theme define a label region?
    has_label = Property

    # The alignment to use for positioning the label:
    alignment = HorizontalAlignment( cols = 4 )

    # The image slice used to draw the theme:
    image_slice = Property

    # The font to use for content text:
    content_font = Font

    # The font to use for label text:
    label_font = Font

    # The color to use for content text:
    content_color = Property

    # The color to use for label text:
    label_color = Property

    # The theme background color:
    bg_color = Property

    # The default 'content_color' and 'label_color' to use:
    default_color = Any

    #-- Object Method Overrides ------------------------------------------------

    def __init__ ( self, image = None, **facets ):
        """ Initializes the object.
        """
        if image is not None:
            self.image = image

        super( Theme, self ).__init__( **facets )


    def __str__ ( self ):
        """ Returns the string respresentation of the theme.
        """
        ftc = toolkit().from_toolkit_color

        return ThemeTemplate % (
            self.image, self.tiled, self.origin, self.border, self.content,
            self.label, self.alignment, self.content_font, self.label_font,
            ftc( self.content_color ), ftc( self.label_color ),
            ftc( self.bg_color )
        )


    def __getstate__ ( self ):
        ftc = toolkit().from_toolkit_color

        return {
            'image':         str( self.image ),
            'tiled':         self.tiled,
            'origin':        self.origin,
            'border':        eval( str( self.border  ) ),
            'content':       eval( str( self.content ) ),
            'label':         eval( str( self.label   ) ),
            'alignment':     self.alignment,
            'content_font':  str( self.content_font ),
            'label_font':    str( self.label_font ),
            'content_color': ftc( self.content_color ),
            'label_color':   ftc( self.label_color ),
            'bg_color':      ftc( self.bg_color )
        }

    #-- Public Methods ---------------------------------------------------------

    def fill ( self, g, x, y, dx, dy, transparent = True ):
        if self.tiled:
            self._fill_tiled( g, x, y, dx, dy )
        else:
            self.image_slice.fill( g, x, y, dx, dy, transparent )


    def bounds ( self, x = None, y = None, dx = None, dy = None ):
        """ Returns a tuple of the form ( xp, yp, dxp, dyp ) specifying the
            content bounds for the theme given a specified drawing region
            ( *x*, *y*, *dx*, *dy* ).

            If no arguments are specified, then the result is a tuple of the
            form: ( dxp, dyp ), specifying the extra width and height the theme
            requires to draw content of a known size.

            If *dx* and *dy* are not specified, the result is a tuple of the
            form: ( dxp, dyp ), specifying the size of the content area for a
            region of size ( *x*, *y* ) drawn using the theme.
        """
        if self.tiled:
            if x is None:
                return ( 0, 0 )

            return (( x, y ) if dx is None else ( x, y, dx, dy ))

        slice   = self.image_slice
        content = self.content
        dxl     = slice.xleft   + content.left
        dxr     = slice.xright  + content.right
        dyt     = slice.xtop    + content.top
        dyb     = slice.xbottom + content.bottom

        if x is None:
            return ( dxl + dxr, dyt + dyb )

        if dx is None:
            return ( x - dxr - dxl, y - dyb - dyt )

        xl = x + dxl
        yt = y + dyt

        return ( xl, yt, x + dx - dxr - xl, y + dy - dyb - yt )


    def label_bounds ( self, x, y, dx, dy ):
        """ Returns a tuple of the form ( xp, yp, dxp, dyp ) specifying the
            label bounds for the theme given a specified drawing region
            ( x, y, dx, dy ).
        """
        if self.tiled:
            return ( x, y, 0, 0 )

        slice   = self.image_slice
        label   = self.label
        xl      = x + slice.xleft + label.left
        xr      = x + dx - slice.xright - label.right
        xtop    = slice.xtop
        xbottom = slice.xbottom

        if xtop >= xbottom:
            yt = y + label.top
            yb = y + xtop - label.bottom
        else:
            yt = y + dy - xbottom + label.top
            yb = y + dy - label.bottom

        return ( xl, yt, xr - xl, yb - yt )


    def draw_graphics_text ( self, g, text, x, y, dx, dy, visible = None ):
        """ Draws the GraphicsText object *text* within the content portion of
            the total region *x*, *y*, *dx*, *dy* available to the theme in the
            graphics context *g*. If *visible* is not None, it should be a tuple
            containing the visible bounds of the drawing area in the form:
            (x, y, dx, dy).
        """
        g.text_color = self.content_color
        text.draw( g, *self.bounds( x, y, dx, dy ), visible = visible )


    def draw_graphics_label ( self, g, text, x, y, dx, dy, visible = None ):
        """ Draws the GraphicsText object *text* within the label portion of
            the total region *x*, *y*, *dx*, *dy* available to the theme in the
            graphics context *g*. If *visible* is not None, it should be a tuple
            containing the visible bounds of the drawing area in the form:
            (x, y, dx, dy).

            Returns **True** if the label is drawn and **False** if there is not
            enough room to draw the label.
        """
        # Make sure there is enough room to draw the label:
        tdx, tdy         = text.size( g )
        lx, ly, ldx, ldy = self.label_bounds( x, y, dx, dy )
        if tdy > ldy:
            return False

        g.text_color = self.label_color
        text.draw( g, lx, ly, ldx, ldy, visible = visible )

        return True


    def draw_text ( self, g, text, position, x, y, dx, dy, image = None ):
        """ Draws a specified string within the specified graphics context using
            the specified *position* and theme information, and positioned
            within the region specified by (x, y, dx, dy ). It will also draw an
            optional image to the left of the text using the same alignment as
            the text.

            A *position* value of None is the same as TOP and LEFT.
        """
        # Set the clipping bounds to the drawable interior region of the theme:
        x, y, dx, dy = g.clipping_bounds = self.bounds( x, y, dx, dy )

        # Calculate the size of the text (if any):
        tdx = tdy = 0
        if text != '':
            lines = text.split( '\n' )
            sizes = []
            ts    = g.text_size
            for line in lines:
                if line.strip() == '':
                    ldx, ldy = ts( '|' )
                else:
                    ldx, ldy = ts( line )
                    tdx      = max( tdx, ldx )

                tdy += ldy
                sizes.append( ( ldx, ldy ) )

        # Calculate the size of the image (if any):
        idx = idy = 0
        if image is not None:
            idx = image.width + (4 * (tdx > 0))
            idy = image.height

        # Make sure we have a valid position to use:
        if not isinstance( position, int ):
            position = AlignmentMap.get( position, TOP_LEFT )

        # Use the alignment to calculate the 'x' coordinate to draw at:
        if (position & LEFT) != 0:
            tx = bx = x
        elif (position & RIGHT) != 0:
            bx = x + dx
            tx = bx - tdx - idx
        else:
            bx = x + (dx / 2)
            tx = bx - ((tdx + idx) / 2)

        # Use the alignment to calculate the 'y' coordinate to draw at:
        if (position & TOP) != 0:
            ty = iy = y
        elif (position & BOTTOM) != 0:
            ty  = iy = y + dy
            ty -= tdy
            iy -= idy
        else:
            my = y + (dy / 2) + 1
            ty = my - (tdy / 2) - 2
            iy = my - (idy / 2)

        # Draw the image (if any):
        if idx > 0:
            g.draw_bitmap( image.bitmap, tx, iy )
            tx += idx

        # Draw the text (if any):
        if tdx > 0:
            g.text_color = self.content_color
            if len( lines ) == 1:
                g.draw_text( lines[0], tx, ty )
            else:
                ey = y + dy
                for i, line in enumerate( lines ):
                    ldx, ldy = sizes[ i ]
                    if (i > 0) and (ty + ldy) > ey:
                        break

                    if (position & RIGHT) != 0:
                        tx = bx - ldx
                    elif (position & LEFT) == 0:
                        tx = bx - (ldx / 2)

                    g.draw_text( line, tx, ty )

                    ty += ldy

        # Reset the clipping bounds:
        g.clipping_bounds = None

        # Returns the size of the bounding box for the text and image drawn:
        return ( tdx + idx, max( tdy, idy ) )


    def draw_label ( self, g, text, position, x, y, dx, dy, image = None ):
        """ Draws a specified string within the specified graphics context using
            the specified *position* and theme information, and positioned
            within the region specified by (x, y, dx, dy ). It will also draw an
            optional image to the left of the text using the same alignment as
            the text.

            This is similar to the 'draw_text' method but will only draw a
            single line of text and draws into the label portion of the theme,
            if it has one. If no label area is defined by the theme, then
            nothing is drawn. Returns True if the label was drawn, and False
            otherwise.

            If *position* is None, the default label alignment for the theme is
            used.
        """
        # Get the minimum height needed and exit immediately if there is not
        # enough room to draw the label:
        idx = idy = 0
        if image is not None:
            idx = image.width + 4
            idy = image.height

        g.font   = self.label_font
        tdx, tdy = g.text_size( text )
        mdy      = max( tdy, idy ) + 4
        slice    = self.image_slice
        if (slice is None) or (mdy > max( slice.xtop, slice.xbottom )):
            return False

        label   = self.label
        xtop    = slice.xtop
        xbottom = slice.xbottom
        cl      = x + slice.xleft + label.left
        cr      = x + dx - slice.xright - label.right
        if ((tdy + label.top + label.bottom) <= xtop) and (xtop >= xbottom):
            by = y + (label.top + xtop - label.bottom) / 2
        else:
            by = y + dy + ((label.top - xbottom - label.bottom) / 2)

        # Calculate the x coordinate for the specified alignment type:
        if position is None:
            position = AlignmentMap.get( self.alignment, CENTER )

        if (position & LEFT) != 0:
            tx = cl
        elif (position & RIGHT) != 0:
            tx = cr - tdx - idx
        else:
            tx = (cl + cr - tdx - idx) / 2

        # Draw the (clipped) image and text string (note that we increase the
        # clipping bounds height a small amount because too tight a bounds can
        # cause clipping of text descenders:
        g.clipping_bounds = ( cl, by - (mdy / 2), cr - cl, mdy + 2 )
        if idx > 0:
            g.draw_bitmap( image.bitmap, tx, by - (idy / 2) + 1 )
            tx += idx

        if tdx > 0:
            g.text_color = self.label_color
            g.draw_text( text, tx, by - (tdy / 2) )

        g.clipping_bounds = None

        return True


    def size_for ( self, g, text = None, image = None ):
        """ Returns the size ( dx, dy ) of a region needed to draw the specified
            *text* and optional image using the theme. The *text* may be a
            GraphicsText object, in which case the *image* is ignored, since the
            image should be specified as part of the GraphicsText object.
        """
        from graphics_text import GraphicsText

        if isinstance( text, GraphicsText ):
            tdx, tdy = text.size( g )
        else:
            # Calculate the size of the text (if any):
            tdx, tdy = 0, 0
            if (text is not None) and (text != ''):
                ts = g.text_size
                for line in text.split( '\n' ):
                    if line.strip() == '':
                        ldx, ldy = ts( '|' )
                    else:
                        ldx, ldy = ts( line )
                        tdx      = max( tdx, ldx )

                    tdy += ldy

            # Add in the size of the image (if any):
            if image is not None:
                tdx += (image.width + 4 * (tdx > 0))
                tdy  = max( tdy, image.height )

        content = self.content
        slice   = self.image_slice
        if slice is None:
            return ( content.left + tdx + content.right,
                     content.top  + tdy + content.bottom )

        return ( slice.xleft + content.left + tdx + slice.xright +
                 content.right,
                 slice.xtop + content.top + tdy + slice.xbottom +
                 content.bottom )

    #-- Property Implementations -----------------------------------------------

    def _get_has_label ( self ):
        """ Returns True if the theme has a defined label region, and False if
            it does not.
        """
        image_slice = self.image_slice
        if image_slice is None:
            return False

        return ((image_slice.xtop >= 16) or (image_slice.xbottom >= 16))


    @property_depends_on( 'image' )
    def _get_image_slice ( self ):
        from facets.ui.pyface.image_slice \
            import image_slice_for, default_image_slice

        if self.tiled or (self.image is None):
            return default_image_slice

        return image_slice_for( self.image )


    @property_depends_on( 'image_slice', settable = True )
    def _get_content_color ( self ):
        islice = self.image_slice
        if islice is None:
            return self.default_color

        return islice.content_color


    @property_depends_on( 'image_slice', settable = True )
    def _get_label_color ( self ):
        islice = self.image_slice
        if islice is None:
            return self.default_color

        return islice.label_color


    @property_depends_on( 'image_slice', settable = True )
    def _get_bg_color ( self ):
        islice = self.image_slice
        if islice is None:
            return self.default_color

        return islice.bg_color

    #-- Facet Default Values ---------------------------------------------------

    def _default_color_default ( self ):
        """ Returns the GUI toolkit specific value for the color black.
        """
        return toolkit().to_toolkit_color( ( 0, 0, 0 ) )

    #-- Private Methods --------------------------------------------------------

    def _fill_tiled ( self, g, x, y, dx, dy ):
        """ Fills the region specified by (*x*, *y*, *dx, *dy*) in the graphics
            context specified by *g* by tiling the region using the theme's
            image, starting at the current theme origin.
        """
        image    = self.image
        bitmap   = image.bitmap
        idx, idy = image.width, image.height
        ox, oy   = self.origin
        ox      %= idx
        oy      %= idy
        while dy > 0:
            ady = min( idy - oy, dy )
            tdx = dx
            tox = ox
            x0  = x
            while tdx > 0:
                adx = min( idx - tox, tdx )
                g.blit( x0, y, adx, ady, bitmap, tox, oy, adx, ady )
                x0  += adx
                tdx -= adx
                tox  = 0

            y  += ady
            dy -= ady
            oy  = 0

#-- Create a default theme -----------------------------------------------------

default_theme = Theme()

#-- EOF ------------------------------------------------------------------------