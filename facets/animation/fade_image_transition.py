"""
Defines the FadeImageTransition class for animating the transition from one
image to another (as used in videos and web pages) using a 'fade-in' style.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from random \
    import shuffle

from facets.api \
    import Range, Enum, Bool, Property, property_depends_on

from facets.core.facet_base \
    import clamp

from image_transition \
    import ImageTransition

#-------------------------------------------------------------------------------
#  'FadeImageTransition' class:
#-------------------------------------------------------------------------------

class FadeImageTransition ( ImageTransition ):
    """ Defines the FadeImageTransition class for animating the transition from
        one image to another (as used in videos and web pages) using a 'fade-in'
        style.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The style of the fade:
    style = Enum( 'normal', 'black', 'white' )

    # The number of rows in the grid:
    rows = Range( 1, 100 )

    # The number of columns in the grid:
    columns = Range( 1, 100 )

    # The transition order:
    order = Enum( 'normal', 'reverse', 'random' )

    # The delay to the start of the last element:
    delay = Range( 0.0, 1.0, 0.4 )

    # Should a grid overlay be displayed?
    show_grid = Bool( False )

    #-- Private Facets ---------------------------------------------------------

    # The offset to the start of each image element x coordinate:
    offset_x = Property

    # The offset to the start of each image element y coordinate:
    offset_y = Property

    # The element to fade in organized as a list of tuples of the form
    # [ ( row_index, column_index ), ... ]:
    elements = Property

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g, x, y ):
        """ Paints the transition at the current time into the graphics context
            *g* at location (*x*,*y*), which defines the upper-left corner of
            where the images are drawn.
        """
        image     = self.image_0
        time      = self.time
        style     = self.style
        g.opacity = 1.0
        g.pen     = None
        g.brush   = ( 0xFFFFFF, 0x000000 )[ style == 'black' ]
        solid     = False
        if style == 'normal':
            g.draw_bitmap( image.bitmap, x, y )
        else:
            if time < 0.5:
                g.draw_bitmap( image.bitmap, x, y )
                time *= 2.0
                solid = True
            else:
                g.draw_rectangle( x, y, image.width, image.height )
                time = 2.0 * (time - 0.5)

        image     = self.image_1.bitmap
        offset_x  = self.offset_x
        offset_y  = self.offset_y
        elements  = self.elements
        delay     = dt = 0.0
        if len( elements ) > 1:
            delay = self.delay
            dt    = delay / (len( elements ) - 1)

        time_base = 1.0 - delay
        for i, element in enumerate( elements ):
            row, column = element
            g.opacity   = clamp( (time - (i * dt)) / time_base, 0.0, 1.0 )
            x0 = offset_x[ column ]
            y0 = offset_y[ row ]
            dx = offset_x[ column + 1 ] - x0
            dy = offset_y[ row    + 1 ] - y0
            if solid:
                g.draw_rectangle( x + x0, y + y0, dx, dy )
            else:
                g.blit( x + x0, y + y0, dx, dy, image, x0, y0, dx, dy )

        if self.show_grid:
            g.opacity = min( 1.0, 3.0 - (6.0 * abs( time - 0.5 )) )
            dx        = offset_x[-1]
            dy        = offset_y[-1]
            for x0 in offset_x:
                g.draw_line( x + x0, y, x + x0, y + dy )

            for y0 in offset_y:
                g.draw_line( x, y + y0, x + dx, y + y0 )


    def clone ( self ):
        """ Returns a clone of the image transition.
        """
        return self.__class__( **self.get(
            'style', 'rows', 'columns', 'order', 'delay', 'show_grid'
        ) )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'image_0, columns' )
    def _get_offset_x ( self ):
        return self._offset_for( self.image_0.width, self.columns )


    @property_depends_on( 'image_0, rows' )
    def _get_offset_y ( self ):
        return self._offset_for( self.image_0.height, self.rows )


    @property_depends_on( 'rows, columns, order' )
    def _get_elements ( self ):
        elements = []
        columns  = self.columns
        for r in xrange( self.rows ):
            elements.extend( [ ( r, c ) for c in xrange( columns ) ] )

        if self.order == 'reverse':
            elements.reverse()
        elif self.order == 'random':
            shuffle( elements )

        return elements

    #-- Private Methods --------------------------------------------------------

    def _offset_for ( self, dxy, n ):
        """ Returns the x or y axis offsets for the image width or height
            specified by *dxy* with the number of elements specified by *n*.
        """
        delta  = float( dxy ) / n
        xy     = 0.0
        offset = []
        for i in xrange( n ):
            offset.append( int( round( xy ) ) )
            xy += delta

        offset.append( dxy )

        return offset

#-- EOF ------------------------------------------------------------------------
