"""
Defines the Theme class which defines a stretchable region for rendering
variable amounts of content using a custom background image 'theme'. A Theme can
render two different types of content: label cells and body cells.

A Theme supports the following configuration of label cells:
  - No label cells
  - A single label cell
  - A horizontal repeating row of label cells
  - A vertically repeating column of label cells
  - Both a horizontal repeating row and vertical repeating column of label cells

Vertical labels cells can appear on either the left or right of the body cells,
while horizontal labels cells can appear either above or below the body cells.

A Theme supports the following configuration of body cells:
  - A single body cell
  - A horizontal repeating row of body cells
  - A vertically repeating column of body cells
  - A horizontally and vertically repeating grid of body cells

A Theme is based on the use of 'stretchable' images, described by ImageSlice
objects. Body cells are described by one ImageSlice object, while horizontal and
vertical label cells are described by separate ImageSlice objects. As a result,
a single Theme may use from one to three ImageSlice objects, depending upon the
configuration of body and label cells.

Note that, in general, all ImageSlice objects used by a single Theme will be
based upon different regions of a single physical image, although it is possible
for each ImageSlice object to use a different image. The division of the image
into the different ImageSlice regions is typically performed using the
ImageSlicer tool.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Bool

from facets.ui.ui_facets \
    import HasBorder

from image_slice \
    import ImageSlice

from image_slice_info \
    import ImageSliceInfo

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# A map from encoded image slice data types to tuples of the form: (
#   kind:  -1, 0, 1, 2, 3, 4 (-1 = Invalid, 0..4 = Result slot index),
#   index: 0..5 (index within the 'slots' list),
#   count: 2, 3, 4 (number of integer values in following tuple) ):
TypeMap = {
    'T': ( 0, 0, 4 ),
    'B': ( 1, 0, 4 ),
    'L': ( 2, 0, 4 ),
    'R': ( 3, 0, 4 ),
    'M': ( 4, 0, 4 ),
    'S': ( 0, 1, 4 ),
    'H': ( 0, 2, 2 ),
    'V': ( 0, 3, 2 ),
    'O': ( 0, 4, 4 ),
    'C': ( 0, 5, 3 )
}

# The TypeMap value for an unrecognized character code:
InvalidType = ( -1, 0, 0 )

# The content values used when no 'content' value is found in encoded image
# slice data:
NoContent = ( 0, 0, 0, 0 )

# The background color used when no 'color' value is found in encoded image
# slice data:
NoColor = ( 255, 255, 255 )

# The template used to convert a Theme object to a string:
ThemeTemplate = """
Theme(
    body = %s,
    horizontal = %s,
    vertical = %s,
    on_top  = %s,
    on_left = %s,
    inset   = %s,
    width   = %s
)
"""[1:-1]

#-------------------------------------------------------------------------------
#  'Theme' class:
#-------------------------------------------------------------------------------

class Theme ( HasPrivateFacets ):
    """ Defines the Theme class which defines a stretchable region for rendering
        variable amounts of body and optional label cell content using a custom
        background image 'theme'.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ImageSliceInfo object used to render body cells:
    body = Instance( ImageSliceInfo )

    # The ImageSliceInfo object used to render horizontal label cells:
    horizontal = Instance( ImageSliceInfo )

    # The ImageSliceInfo object used to render vertical label cells:
    vertical = Instance( ImageSliceInfo )

    # Are horizontal label cells rendered above (i.e. on top) of body cells
    # (True) or below (False)?
    on_top = Bool( True )

    # Are vertical label cells rendered to the left of body cells (True) or to
    # the right (False)?
    on_left = Bool( True )

    # The logical inset of the border from the outermost edge of the theme:
    inset = HasBorder

    # The logical width of the border along each edge of the theme:
    width = HasBorder

    #-- Object Method Overrides ------------------------------------------------

    def __str__ ( self ):
        """ Returns the string respresentation of the theme.
        """
        return ThemeTemplate % (
            self.body, self.horizontal, self.vertical, self.on_top,
            self.on_left, self.inset, self.width
        )

    #-- Public Class Methods ---------------------------------------------------

    @classmethod
    def decode_image_slice ( cls, data, image = None ):
        """ Returns a new Theme object obtained by decoding the encoded string
            *data* containing slice data. *Image* is an optional AnImageResource
            object which will be associated with each ImageSlice object created.
        """
        data   = data.strip().upper()
        index  = 0
        n      = len( data )
        slices = [ None ] * 5
        type   = None
        while index < n:
            c = data[ index ]
            if c in '\n\t ':
                index += 1

                continue

            kind, slot, count = TypeMap.get( c, InvalidType )
            if kind < 0:
                raise ValueError( 'Unrecognized field type: ' + data[ index ] )

            if slot == 0:
                if type is not None:
                    slices[ type ] = cls._create_image_slice_info( slots,
                                                                   image )

                type  = kind
                slots = [ None ] * 6

            index, slots[ slot ] = cls._parse_tuple( data, index + 1, count )

        if type is not None:
            slices[ type ] = cls._create_image_slice_info( slots, image )

        return cls(
            body       = slices[4],
            horizontal = slices[0] or slices[1],
            vertical   = slices[2] or slices[3],
            on_top     = slices[0] is not None,
            on_left    = slices[2] is not None
        )

    #-- Private Class Methods --------------------------------------------------

    @classmethod
    def _parse_tuple ( cls, data, index, count ):
        """ Parse the contents of the string specified by *data* starting at the
            character index specified by *index* for a tuple of *count* integer
            values of the form: ( ddd, ddd, ..., ddd ).

            It returns a tuple containing the index of the first character in
            *data* following the end of the parsed tuple, and the tuple of
            integers contained in the parsed tuple.

            Raises a ValueError if *data* does not contain a tuple of the
            required form.
        """
        end = -1
        if data[ index ] == '(':
            end = data.find( ')', index + 1 )
            if end >= 0:
                try:
                    result = [ int( item )
                               for item in data[ index + 1: end ].split( ',' ) ]
                    if len( result ) == count:
                        return ( end + 1, tuple( result ) )
                except:
                    pass

        end += 1
        if end <= 0:
            end = len( data )

        raise ValueError(
            "Expected tuple of form '(%s)', but received '%s' instead" %
            ( ','.join( [ 'n' ] * count ), data[ index: end ] )
        )


    @classmethod
    def _create_image_slice_info ( cls, slots, image ):
        """ Returns the ImageSliceInfo object for the ImageSlice object defined
            by the series of tuples contained in the *slots* list and for the
            image specified by *image*.
        """
        # Extract the component data from the slots list:
        outer, slice, hrepeat, vrepeat, content, bg_color = slots

        # Validate the component data:
        if outer is None:
            raise ValueError( 'No image bounds specified' )

        if slice is None:
            raise ValueError( 'No image slice points specified' )

        if content is None:
            content = NoContent

        if bg_color is None:
            bg_color = NoColor

        # Extract the individual elements from the component data:
        oxl, oyt, oxr, oyb     = outer
        sxl, syt, sxr, syb     = slice
        lcdx, tcdy, rcdx, bcdy = content
        hsx, sdx  = sxl, sxr - sxl
        vsy, sdy  = syt, syb - syt
        mfx = mfy = mfdx = mfdy = -1

        # If there is repeated horizontal slice data, adjust the values:
        if hrepeat is not None:
            mfx, hxr = hrepeat
            mfdx     = hxr - mfx
            sdx      = mfx - sxl
            sdx2     = sxr - hxr
            if sdx2 > sdx:
                sdx = sdx2
                hsx = hxr

        # If there is repeated vertical slice data, adjust the values:
        if vrepeat is not None:
            mfy, vyb = vrepeat
            mfdy     = vyb - mfy
            sdy      = mfy - syt
            sdy2     = syb - vyb
            if sdy2 > sdy:
                sdy = sdy2
                vsy = vyb

        # Return the ImageSlice object using the computed values:
        return ImageSliceInfo( image_slice =
            ImageSlice(
                image    = image,
                bg_color = bg_color,
                lfdx     = sxl - oxl,
                rfdx     = oxr - sxr,
                tfdy     = syt - oyt,
                bfdy     = oyb - syb,
                lfx      = oxl,
                rfx      = sxr,
                tfy      = oyt,
                bfy      = syb,
                lcdx     = lcdx,
                tcdy     = tcdy,
                rcdx     = rcdx,
                bcdy     = bcdy,
                hsx      = hsx,
                vsy      = vsy,
                sdx      = sdx,
                sdy      = sdy,
                mfx      = mfx,
                mfy      = mfy,
                mfdx     = mfdx,
                mfdy     = mfdy
            )
        )

#-- EOF ------------------------------------------------------------------------
