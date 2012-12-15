"""
Defines a GraphicsText class designed to be used with AbstractGraphicsContext
and Theme objects to perform fast and efficient text and optional image
rendering, including support for multi-color text strings.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Str, Any, Color, Callable

from facets.ui.ui_facets \
    import Image, Alignment

from constants \
    import LEFT, RIGHT, TOP, BOTTOM, TOP_LEFT, AlignmentMap

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The strings used within a GraphicsText object to mark color codes and tables:
ColorCode      = '\x00'
TagCode        = '\x01'
ColorTableCode = '\x02'
TagRefCode     = '\x03'

# Added to text strings to ensure that a color/tag code is always found:
Sentinel = (ColorCode + TagCode)

# The mapping from color codes to color table indices:
ColorMap = {
     '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
     '9': 9,
     'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15, 'g': 16, 'h': 17,
     'i': 18, 'j': 19, 'k': 20, 'l': 21, 'm': 22, 'n': 23, 'o': 24, 'p': 25,
     'q': 26, 'r': 27, 's': 28, 't': 29, 'u': 30, 'v': 31, 'w': 32, 'x': 33,
     'y': 34, 'z': 35,
     'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17,
     'I': 18, 'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24, 'P': 25,
     'Q': 26, 'R': 27, 'S': 28, 'T': 29, 'U': 30, 'V': 31, 'W': 32, 'X': 33,
     'Y': 34, 'Z': 35,
}

# Index names for the GraphicsText 'info' tuple values:
INFO_START = 0    # Text fragment starting index
INFO_END   = 1    # Text fragment ending index
INFO_Y     = 2    # Text y location
INFO_DX    = 3    # Text fragement width
INFO_DY    = 4    # Text fragement height
INFO_TDX   = 5    # Text line total width (or negative index)
INFO_COLOR = 6    # Text fragment color table index
INFO_TAG   = 7    # Text fragment tag index

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def color_tag_for ( color, tag = None, offset = 0 ):
    """ Returns a color/tag code for the specified *color* and optional *tag*.
        *Color* should be a character digit or letter specifying a color index,
        and *tag* can be either a number specifying the tag index or a list,
        in which case the current length of the list will be used as the tag
        index.
    """
    if tag is None:
        return (ColorCode + color)

    if not isinstance( tag, int ):
        tag = len( tag ) + offset

    return ('%s%s%04X' % ( TagCode, color, tag ))


def tag_ref_for ( tag ):
    """ Returns a tag reference for the specified *tag*. When a graphics text
        object is rendered, the tag reference will be replaced by the contents
        of the specified tag. Since the contents of the tag can vary over time,
        this provides a mechanism for dynamically updating the contents of a
        graphics text object.
    """
    return ('%s%04X' % ( TagRefCode, tag ))


def has_no_content ( tag_index ):
    """ Default handler for the GraphicsText 'content' facet.
    """
    return ''

#-------------------------------------------------------------------------------
#  'GraphicsText' class:
#-------------------------------------------------------------------------------

class GraphicsText ( HasPrivateFacets ):
    """ Defines a GraphicsText class designed to be used with
        AbstractGraphicsContext and Theme objects to perform fast and efficient
        text and optional image rendering, including support for multi-color
        text strings.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The text to be rendered:
    text = Str

    # The optional image to be rendered:
    image = Image

    # The alignment of the text and optional image:
    alignment = Alignment

    # A callable that returns the string content of a specified tag index:
    tag_content = Callable( has_no_content )

    #-- Private Facets ---------------------------------------------------------

    # The text to be rendered (after performing tag reference substitution):
    full_text = Str

    # The size of the bounding box for the rendered text and image:
    bounds = Any # Tuple( Int, Int )

    # The list of colors used when rendering text (None if no color codes are
    # used):
    colors = Any # List( Color )

    # Information about the text fragments to be rendered. This is a list of
    # tuples. Each tuple in the list contains information about a particular
    # text fragment to be rendered, and has the form: ( text_index, text_length,
    # y, dx, dy, tdx, color_index, tag_index ), where:
    # - text_start: The starting index within 'text' of the text fragment.
    # - text_end: The ending index of the text fragment + 1.
    # - y:   The y coordinate of where to draw the text within 'bounds'.
    # - dx:  The text fragment width (in pixels).
    # - dy:  The text fragment height (in pixels).
    # - tdx: The total line width (in pixels). If negative, it indicates the
    #       relative index to the starting item for this line.
    # - color_index: The index within 'colors' of the text color to use (None
    #       if no color codes are used).
    # - tag_index: The tag index associated with the item, or None if no tag
    #       index is used by the item.
    info = Any # List( Tuple( Int, Int, Int, Int, Int, Int, Int, Int ) )

    # The list of tag ids and bounding boxes for all of the 'tagged' items
    # associated with the rendered text. Each tuple has the form:
    # ( tag_id, x0, y0, x1, y1 ), which defines the top-left and bottom-right
    # corners of the area bounded by the tag specified by tag_id:
    tags = Any( [] ) # List( ( tag_id, x0, y0, x1, y1 ) )

    # Used to convert numbers to colors:
    color = Color

    #-- Public Methods ---------------------------------------------------------

    def draw ( self, g, x, y, dx, dy, visible = None ):
        """ Renders the text (and optional image) using the graphics context *g*
            within the bounds specified by *x*, *y*, *dx*, *dy*. If *visible*
            is not None, it should be a tuple containing the visible bounds of
            the drawing area in the form: (x, y, dx, dy).
        """
        # If we have not yet analyzed the text, do so now:
        if self.info is None:
            self._analyze( g )

        self.tags = tags = []
        end_y     = y + dy
        info      = self.info
        low, high = 0, len( info )
        if (visible is not None) and (high > 0):
            # If there is a visible bounds specified, find the range of visible
            # text fragments we have to render:
            _, vy, _, vdy = visible
            low   = self._info_at( vy - y )
            high  = self._info_at( vy + vdy - y + info[0][ INFO_DY ] )
            end_y = min( end_y, vy + vdy )

        # Get everything ready to go:
        g.clipping_bounds = x, y, dx, dy
        text              = self.full_text
        colors            = self.colors
        alignment         = AlignmentMap.get( self.alignment, TOP_LEFT )

        # Draw the image (if any):
        image = self.image
        if image is not None:
            if alignment & TOP:
                iy = y
            elif alignment & BOTTOM:
                iy = y + dy - image.height
            else:
                iy = y + ((dy - image.height) / 2)

            g.draw_bitmap( image.bitmap, x, iy )
            x += (image.width + 4)

        # Calculate the text starting y point based on the alignment:
        bdy = self.bounds[1]
        if alignment & BOTTOM:
            y += dy - bdy
        elif (alignment & TOP) == 0:
            y += (dy - bdy - 1) / 2

        # Render all of the selected text fragments:
        for i in xrange( low, high ):
            start, end, fy, fdx, fdy, tdx, color_index, tag_index = info[ i ]

            # Get the text y coordinate and exit if we are past the end of the
            # region being drawn into:
            ty = y + fy
            if ty >= end_y:
                break

            # Check for the start of a new line:
            if tdx >= 0:
                cdx = tdx
                cx  = 0

            # Calculate the x coordinate based on the alignment of the text:
            if alignment & LEFT:
                tx = x + cx
            elif alignment & RIGHT:
                tx = x + dx - cdx + cx
            else:
                tx = x + cx + ((dx - cdx) / 2)

            # Set the correct text color (if necessary), then draw the fragment:
            if color_index is not None:
                g.text_color = colors[ color_index ]

            g.draw_text( text[ start: end ], tx, ty )

            # Create the 'tags' table entry (if necessary):
            if tag_index is not None:
                if tag_index >= 0:
                    tags.append( ( tag_index, tx, ty, tx + fdx, ty + fdy ) )

                    # Draw an underline to identify it is a tag:
                    g.opacity = 0.38
                    y0        = ty + fdy - 1
                    g.draw_line( tx, y0, tx + fdx - 1, y0 )
                    g.opacity = 1.0
                else:
                    # Handle the case of a 'separator':
                    y0 = ty + (fdy / 2) + 1
                    g.draw_line( x, y0, x + dx - 1, y0 )

            # Advance to the next text fragment on this line:
            cx += fdx

        # Reset the clipping bounds:
        g.clipping_bounds = None


    def size ( self, g ):
        """ Returns the rendered size of the text (and optional image) using the
            graphics context *g*.
        """
        if self.info is None:
            self._analyze( g )

        return self.bounds


    def tag_at ( self, x, y ):
        """ Returns the index of the tagged item that contains the specified
            (x,y) coordinate, or -1 if no match is found.
        """
        for tag_id, x0, y0, x1, y1 in self.tags:
            if (y0 <= y < y1) and (x0 <= x < x1):
                return tag_id

        return -1

    #-- Private Methods --------------------------------------------------------

    def _analyze ( self, g ):
        """ Generate the internal data by analyzing the text.
        """
        text = self.text

        # Replace all tag references with their corresponding tag contents:
        i = 0
        while True:
            i = text.find( TagRefCode, i )
            if i < 0:
                break

            j = i + 5
            if j > len( text ):
                break

            text = text.replace(
                text[ i: j ],
                str( self.tag_content( int( text[ i + 1: j ], 16 ) ) )
            )

        # Save the fully expanded version of the text:
        self.full_text = text

        # Compute the text bounds. Do a full analysis if the text contains any
        # color codes, otherwise just do a simple analysis:
        if ((text[:1] == ColorTableCode)  or
            (text.find( ColorCode ) >= 0) or
            (text.find( TagCode )   >= 0)):
            bdx, bdy = self._color_analyze( g )
        else:
            bdx, bdy = self._simple_analyze( g )

        # Adjust the bounds if there is an associated image:
        image = self.image
        if image is not None:
            bdx += (image.width + (4 * (bdx > 0)))
            bdy  = max( bdy, image.height )

        # Save the computed bounds:
        self.bounds = ( bdx, bdy )


    def _simple_analyze ( self, g ):
        """ Generates the internal data by analyzing the text in the simple case
            where the text does not contain any color codes.
        """
        text      = self.full_text
        self.info = info = []
        tdx       = tdy  = 0
        ts        = g.text_size
        n         = len( text )
        j         = -1
        while True:
            i = j + 1
            j = text.find( '\n', i )
            if j < 0:
                j = n

            line = text[ i: j ]
            if line.strip() == '':
                ldx = 0
                ldy = ts( '|' )[1]
            else:
                ldx, ldy = ts( line )
                tdx      = max( tdx, ldx )

            info.append( ( i, j, tdy, ldx, ldy, ldx, None, None ) )
            tdy += ldy

            if j >= n:
                break

        return ( tdx, tdy )


    def _color_analyze ( self, g ):
        """ Generates the internal data by analyzing the text in the case where
            the text contains one or more color codes.
        """
        text        = self.full_text
        n           = len( text )
        i           = self._color_table()
        mdx         = g.text_size( 'm' )[0]
        self.info   = info = []
        color_index = 0
        tdx         = tdy = 0
        while True:
            j = text.find( '\n', i )
            if j < 0:
                j = n

            ldx, ldy, color_index, items = self._color_line( g, i, j, tdy,
                                                             color_index, mdx )
            tdx  = max( tdx, ldx )
            tdy += ldy
            info.extend( items )

            if j >= n:
                break

            i = j + 1

        return ( tdx, tdy )


    def _color_line ( self, g, start, end, y, color_index, mdx ):
        """ Analyzes a single line of text possibly containing embedded color
            code and returns a tuple of the form ( tdx, tdy, color_index,
            tag_index, items ), where 'tdx' and 'tdy' are the size of the line
            in pixels, 'color_index' is the last color index in effect for the
            line and 'items' are a list of tuples representing the 'info' data
            for that line.
        """
        info      = []
        ts        = g.text_size
        colors    = self.colors
        tdx       = tdy = 0
        text      = self.full_text[ start: end ] + Sentinel
        tag_index = None
        n         = end - start
        i         = 0
        while True:
            # Find the next color or tag code:
            j       = text.find( ColorCode, i )
            j2      = text.find( TagCode, i )
            has_tag = (j2 < j)
            j       = min( j, j2 )

            # If the text fragment the previous tag applies to is not empty,
            # then create an entry for it:
            if i < j:
                fragment = text[ i: j ] + 'm'
                fdx, fdy = ts( fragment )
                fdx     -= mdx
                tdx     += fdx
                tdy      = max( tdy, fdy )
                info.append( [ start + i, start + j, y, fdx, fdy, -len( info ),
                               color_index, tag_index ] )

            # If we have reached the end of the text, then we are done:
            if j >= n:
                break

            # Handle the error case of a color/tag code with no color index data
            # occurring at the very end of the line:
            i = j + 2
            if i > n:
                color_index = 0

                break

            # Get the new color index from the color/tag code we just found:
            color_index = ColorMap.get( text[ i - 1: i ], 0 )
            if color_index >= len( colors ):
                self.color = 0
                colors.extend( [ self.color ] *
                               (color_index - len( colors ) + 1) )

            # If the color code has a tag index, extract it (if possible):
            tag_index = None
            if has_tag:
                i += 4
                if i > n:
                    break

                tag_index = int( text[ i - 4: i ], 16 )

        # Patch the total line width value for the first info item generated:
        if len( info ) == 0:
            if n == 0:
                tdy       = ts( ' ' )[1]
                tag_index = None
            else:
                # Handle the special case of a line containing only color codes:
                tdy       = 10
                tag_index = -1

            info.append(
                ( start, start, y, tdx, tdy, tdx, color_index, tag_index )
            )
        else:
            info[0][ INFO_TDX ] = tdx

        return ( tdx, tdy, color_index, info )


    def _color_table ( self ):
        """ Extracts the color table embedded at the beginning of the text and
            returns a  tuple of the form ( index, color_table ), where 'index'
            is the index in the text of the first character after the color
            table, and 'color_table' is the list of colors found within the
            embedded color table.
        """
        # Create a default color table:
        self.color  = 0
        self.colors = [ self.color ]

        # If there is no color table defined, then use the default one:
        text = self.full_text
        if text[:1] != ColorTableCode:
            return 0

        # Otherwise, find the end of the color table:
        end = text.find( '.', 1 )
        if (end < 0) or (((end - 1) % 6) != 0):
            # If no end marker found or the result has the wrong length, use
            # the default table:
            return 1

        # Convert the color table data into an actual color table:
        cf          = self._color_for
        self.colors = [ cf( text[ i: i + 6 ] ) for i in xrange( 1, end, 6 ) ]

        # Return the next text index after the end of the color table:
        return (end + 1)


    def _color_for ( self, color ):
        """ Returns the color corresponding to *color*, which should be a six
            character string of the form: RRGGBB.
        """
        try:
            value = int( color, 16 )
        except:
            value = 0

        self.color = value

        return self.color


    def _info_at ( self, y ):
        """ Returns the index of the first info item for a text line containing
            a specified y location using a binary search. If the y value is
            outside the bounds of any item, the index of the nearest text line's
            first info item is returned.
        """
        info = self.info
        low   = 0
        high  = len( info ) - 1
        if y < info[ low ][ INFO_Y ]:
            return low

        item = info[ high ]
        if y >= (item[ INFO_Y ] + item[ INFO_DY ]):
            return (high + 1)

        while True:
            mid  = (low + high) / 2
            item = info[ mid ]
            iy   = item[ INFO_Y ]
            if y < iy:
                high = mid - 1
            elif y >= (iy + item[ INFO_DY ]):
                low = mid + 1
            else:
                return (mid + min( 0, item[ INFO_TDX ] ))

#-- EOF ------------------------------------------------------------------------
