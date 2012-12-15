"""
Defines the ImageTextCell class used for rendering a single text string and/or
an image as an IDataCell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Enum, Property, Event, property_depends_on

from facets.ui.ui_facets \
    import Image, Position, Spacing

from facets.ui.data.api \
    import DataCell

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The size of an empty item:
ZeroSize = ( 0, 0 )

# Targets for '_get_info_for' method:
TheText  = 0
TheImage = 1
TheCell  = 2

# Mapping from alignment to x, dx, y, dy scaling multipliers:
AlignmentMap = {
    'top left':     (  1, 0.0,  1, 0.0 ),
    'top':          ( -1, 0.5,  1, 0.0 ),
    'top right':    ( -1, 1.0,  1, 0.0 ),
    'left':         (  1, 0.0, -1, 0.5 ),
    'center':       ( -1, 0.5, -1, 0.5 ),
    'right':        ( -1, 1.0, -1, 0.5 ),
    'bottom left':  (  1, 0.0, -1, 1.0 ),
    'bottom':       ( -1, 0.5, -1, 1.0 ),
    'bottom right': ( -1, 1.0, -1, 1.0 )
}

#-------------------------------------------------------------------------------
#  'ImageTextCell' class:
#-------------------------------------------------------------------------------

class ImageTextCell ( DataCell ):
    """ Defines the ImageTextCell class used for rendering a single text string
        and/or an image as an IDataCell.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The minimum size needed to render the cell's contents specified as a tuple
    # of the form ( width, height ) (override):
    size = Property # ( Tuple( Int, Int ) )

    # An (optional) image to be drawn:
    image = Image( event = 'updated' )

    # The (optional) text to be displayed:
    text = Str( event = 'updated' )

    # The alignment of the image and text relative to its container:
    alignment = Enum( 'left', 'center', 'right', 'top left', 'top', 'top right',
                      'bottom left', 'bottom', 'bottom right',
                      event = 'updated' )

    # The position of the image relative to the text:
    position = Position( event = 'updated' )

    # The amount of spacing between the image and the text:
    spacing = Spacing( event = 'updated' )

    #-- Private Facets ---------------------------------------------------------

    # An event fired when any display related value changes:
    updated = Event

    # The pixel size of the text:
    text_size = Property # ( Tuple( Int, Int ) )

    # The positioning information of the text relative to its container:
    text_position = Property # ( None or Tuple( Int, Float, Int, Float ) )

    # The positioning information of the image relative to its container:
    image_position = Property # ( None or Tuple( Int, Float, Int, Float ) )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'updated' )
    def _get_size ( self ):
        return self._get_info_for( TheCell )


    @property_depends_on( 'text' )
    def _get_text_size ( self ):
        text = self.text
        if text == '':
            return ZeroSize

        return self.graphics.text_size( text )


    @property_depends_on( 'updated' )
    def _get_text_bounds ( self ):
        return self._get_info_for( TheText )


    @property_depends_on( 'updated' )
    def _get_image_position ( self ):
        return self._get_info_for( TheImage )

    #-- Control Event Handlers -------------------------------------------------

    def paint ( self, g ):
        """ Paints the foreground into the specified graphics object.
        """
        # Get the bounds of the area we are drawing into:
        x, y, dx, dy = self.bounds

        # Draw the image (if any):
        bounds = self.image_position
        if bounds is not None:
            bx, bxm, by, bym = bounds
            g.draw_bitmap( self.image.bitmap,
                           x + int( bxm * dx ) + bx, y + int( bym * dy ) + by )

        # Draw the text (if any):
        bounds = self.text_position
        if bounds is not None:
            bx, bxm, by, bym = bounds
            g.draw_text( self.text,
                         x + int( bxm * dx ) + bx, y + int( bym * dy ) + by )

    #-- Private Methods --------------------------------------------------------

    def _get_info_for ( self, item ):
        """ Returns text and image position and size related information.
        """
        tdx, tdy = self.text_size
        if (tdx == 0) and (item == TheText):
            return None

        image = self.image
        if image is None:
            if item == TheImage:
                return None

            idx, idy = 0, 0
        else:
            idx, idy = image.width, image.height

        if (tdx + idx) == 0:
            return ZeroSize

        spacing  = (tdx != 0) * (idx != 0) * self.spacing
        position = self.position
        if position in ( 'above', 'below' ):
            cdx = max( tdx, bdx )
            cdy = tdy + spacing + bdy
            ix  = (cdx - idx) / 2
            tx  = (cdx - tdx) / 2
            if position == 'above':
                iy = 0
                ty = idy + spacing
            else:
                iy = tdy + spacing
                ty = 0
        else:
            cdx = tdx + spacing + bdx
            cdy = max( tdy, bdy )
            iy  = (cdy - idy) / 2
            ty  = (cdy - tdy) / 2
            if position == 'left':
                ix = 0
                tx = idx + spacing
            else:
                ix = tdx + spacing
                tx = 0

        if item == TheCell:
            return ( cdx, cdy )

        xm, dxm, ym, dym = AlignmentMap[ self.alignment ]
        if item == TheImage:
            return ( ix * xm, dxm, iy * ym, dym )

        return ( tx * xm, dxm, ty * ym, dym )

#-- EOF ------------------------------------------------------------------------
