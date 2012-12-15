"""
Defines the ImageSlice class which represents an image which can be sliced into
regions which can be:

  - Copied verbatim (fixed)
  - Stretched horizontally
  - Stretched vertically
  - Stretched horizontally and vertically

An image can have either a single stretchable region or horizontally and/or
vertically repeating stretchable regions. This idea is illustrated in the
following figure:
                                          <--------- OptionaL --------->
   +-------+---------------------+-------+---------------------+-------+
   | Fixed |     Horizontally    | Fixed |     Horizontally    | Fixed |
   |  1,1  | <-- Stretchable --> |  1,2  | <-- Stretchable --> |  1,3  |
   +-------+---------------------+-------+---------------------+-------+
   | V     |                     | V     |                     | V     |
   | e  S  |                     | e  S  |                     | e  S  |
   | r  t  |     Horizontally    | r  t  |     Horizontally    | r  t  |
   | t  r  |         and         | t  r  |         and         | t  r  |
   | i  e  |      Vertically     | i  e  |      Vertically     | i  e  |
   | c  t  |      Stretchable    | c  t  |      Stretchable    | c  t  |
   | a  c  |                     | a  c  |                     | a  c  |
   | l  h  |                     | l  h  |                     | l  h  |
   +-------+---------------------+-------+---------------------+-------+
   | Fixed |     Horizontally    | Fixed |     Horizontally    | Fixed |
   |  2,1  | <-- Stretchable --> |  2,2  | <-- Stretchable --> |  2,3  |
   +-------+---------------------+-------+---------------------+-------+
   | V     |                     | V     |                     | V     | ___
   | e  S  |                     | e  S  |                     | e  S  |  |
   | r  t  |     Horizontally    | r  t  |     Horizontally    | r  t  |  O
   | t  r  |         and         | t  r  |         and         | t  r  |  p
   | i  e  |      Vertically     | i  e  |      Vertically     | i  e  |  t
   | c  t  |      Stretchable    | c  t  |      Stretchable    | c  t  |  i
   | a  c  |                     | a  c  |                     | a  c  |  o
   | l  h  |                     | l  h  |                     | l  h  |  n
   +-------+---------------------+-------+---------------------+-------+  a
   | Fixed |     Horizontally    | Fixed |     Horizontally    | Fixed |  l
   |  3,1  | <-- Stretchable --> |  3,2  | <-- Stretchable --> |  3,3  |  |
   +-------+---------------------+-------+---------------------+-------+ ___
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Image, Color, Int, toolkit

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The template used to convert an ImageSlice object to a string:
ImageSliceTemplate = """
ImageSlice(
    image      = %r,
    bg_color   = %s,
    text_color = %s,
    lfdx       = %s,
    mfdx       = %s,
    rfdx       = %s,
    sdx        = %s,
    tfdy       = %s,
    mfdy       = %s,
    bfdy       = %s,
    sdy        = %s,
    lfx        = %s,
    mfx        = %s,
    rfx        = %s,
    tfy        = %s,
    mfy        = %s,
    bfy        = %s,
    hsx        = %s,
    vsy        = %s,
    lcdx       = %s,
    rcdx       = %s,
    tcdy       = %s,
    bcdy       = %s
)
"""[1:-1]

#-------------------------------------------------------------------------------
#  'ImageSlice' class:
#-------------------------------------------------------------------------------

class ImageSlice ( HasPrivateFacets ):
    """ Defines a stretchable image consisting of a fixed and horizontally and
        vertically stretchable regions. There may be a single stretchable region
        or horizontally, vertically or horizontally and vertically repeating
        stretchable regions.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The 'stretchable' image:
    image = Image

    # The background color of the horizontally/vertically stretchable region:
    bg_color = Color

    # The default text color used when displaying text in the horizontally and
    # vertically stretchable region:
    text_color = Color

    # The width of the left 'fixed' regions:
    lfdx = Int

    # The width of the (optional) horizontally repeating 'fixed' regions:
    mfdx = Int

    # The width of the right 'fixed' regions:
    rfdx = Int

    # The width of the horizontally 'stretchable' regions:
    sdx = Int

    # The height of the top 'fixed' regions:
    tfdy = Int

    # The height of the (optional) vertically repeating 'fixed' regions:
    mfdy = Int

    # The height of the bottom 'fixed' regions:
    bfdy = Int

    # The height of the vertically 'stretchable' regions:
    sdy = Int

    # The x coordinate of the left 'fixed' regions:
    lfx = Int

    # The x coordinate of the (optional) horizontally repeating 'fixed' regions:
    mfx = Int

    # The x coordinate of the right 'fixed' regions:
    rfx = Int

    # The y coordinate of the top 'fixed' regions:
    tfy  = Int

    # The y coordinate of the (optional) vertically repeating 'fixed' regions:
    mfy  = Int

    # The y coordinate of the bottom 'fixed' regions:
    bfy  = Int

    # The x coordinate of the horizontally 'stretchable' regions:
    hsx  = Int

    # The y coordinate of the vertically 'stretchable' regions:
    vsy  = Int

    # The left content offset:
    lcdx = Int

    # The right content offset:
    rcdx = Int

    # The top content offset:
    tcdy = Int

    # The bottom content offset:
    bcdy = Int

    #-- Object Method Overrides ------------------------------------------------

    def __str__ ( self ):
        """ Returns the string respresentation of the image slice.
        """
        ftc = toolkit().from_toolkit_color

        return ImageSliceTemplate % (
            self.image, ftc( self.bg_color ), ftc( self.text_color ), self.lfdx,
            self.mfdx, self.rfdx, self.sdx, self.tfdy, self.mfdy, self.bfdy,
            self.sdy, self.lfx, self.mfx, self.rfx, self.tfy, self.mfy,
            self.bfy, self.hsx, self.vsy, self.lcdx, self.rcdx, self.tcdy,
            self.bcdy
        )


    def __getstate__ ( self ):
        ftc = toolkit().from_toolkit_color

        return {
            'image':      None if self.image is None else str( self.image ),
            'bg_color':   ftc( self.bg_color ),
            'text_color': ftc( self.text_color ),
            'lfdx':       self.lfdx,
            'mfdx':       self.mfdx,
            'rfdx':       self.rfdx,
            'sdx':        self.sdx,
            'tfdy':       self.tfdy,
            'mfdy':       self.mfdy,
            'bfdy':       self.bfdy,
            'sdy':        self.sdy,
            'lfx':        self.lfx,
            'mfx':        self.mfx,
            'rfx':        self.rfx,
            'tfy':        self.tfy,
            'mfy':        self.mfy,
            'bfy':        self.bfy,
            'hsx':        self.hsx,
            'vsy':        self.vsy,
            'lcdx':       self.lcdx,
            'rcdx':       self.rcdx,
            'tcdy':       self.tcdy,
            'bcdy':       self.bcdy
        }

#-- EOF ------------------------------------------------------------------------
