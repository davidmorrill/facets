"""
Defines the subimage tool that extracts the bounds of subimages contained within
an input image. The output is a list of regions of the form: ( x, y, dx, dy )
that contain independent subimages within the input image. A subimage is a
connected, rectangular area of non-transparent pixels surrounded by a "clear"
area of transparent or solid color, such as pure white.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import zeros, any, all, int16

from threading \
    import Thread

from facets.api \
    import Any, Enum, Bool, Color, Image, List, SyncValue, View, HGroup, \
           VGroup, Item, UItem, ImageZoomEditor, HLSColorEditor, spring

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'SubImage' class:
#-------------------------------------------------------------------------------

class SubImage ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'SubImage'

    # The channel data to display in the ImageZoomEditor:
    channel = Enum( 'hue', [ 'none', 'red', 'green', 'blue', 'alpha',
                             'hue', 'lightness', 'saturation' ],
                    save_state = True )

    # Should delta information be displayed:
    delta = Bool( False, save_state = True )

    # The background color to use for the ImageZoomEditor:
    bg_color = Color( 0x303030, save_state = True )

    # The image from which the subimage regions are being extracted from:
    image = Image( cache = False )

    # The item external tools connect to provide the image to view:
    value = Any( connect = 'to' )

    # The list of regions extracted from the input image ([(x,y,dx,dy),...]):
    regions = List( connect = 'from' )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'image',
                   editor = ImageZoomEditor(
                                channel    = SyncValue( self, 'channel'  ),
                                delta      = SyncValue( self, 'delta'    ),
                                overlays   = SyncValue( self, 'regions'  ),
                                bg_color   = SyncValue( self, 'bg_color' ),
                                allow_drop = True )
            )
        )


    options = View(
        VGroup(
            HGroup(
                Item( 'channel' ),
                Item( 'delta', label = 'Show delta' ),
                Item( 'bg_color',
                      label  = 'Background color',
                      width  = -350,
                      editor = HLSColorEditor(
                          edit  = 'lightness',
                          cells = 15
                      )
                ),
                spring
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self, value ):
        """ Handles the 'value' facet being changed.
        """
        self.regions = []

        if isinstance( value, ( list, tuple ) ) and (len( value ) > 0):
            value = value[0]

        if isinstance( value, ( basestring, AnImageResource ) ):
            self.image = value
        else:
            self.image = '@std:alert16'


    def _image_set ( self ):
        """ Handles the 'image' facets being changed by determining the set of
            connected regions contained in the new image value.
        """
        Thread(
            target = self._process_image,
            args   = ( self.image, self.image.pixels )
        ).start()

    #-- Private Methods --------------------------------------------------------

    def _process_image ( self, image, pixels ):
        """ Determines the set of connected regions contained in the *pixels*
            image array.
        """
        regions     = [ ( 0, 0, 0, 0 ) ] # Dummy region[0] = no region
        equivalence = [ set() ]
        idy, idx    = pixels.shape[:2]
        border      = pixels[0,0]

        # Creae a bitmap to contain the labeled region each pixel belongs to:
        labels = zeros( ( idy + 1, idx + 2 ), int16 )

        # Create a bitmap where each value is True if it is part of a region,
        # and False if it is a background (i.e. border) color:
        bitmap = zeros( ( idy + 1, idx + 2 ) )
        if ((border[-1] == 0)               or
            (any( border != pixels[0,-1] )) or
            (any( border != pixels[-1,0] )) or
            (any( border != pixels[-1,-1] ))):
            bitmap[ 1: idy + 1, 1: idx + 1 ] = 1 * (pixels[:,:,-1] != 0)
        else:
            bitmap[ 1: idy + 1, 1: idx + 1 ] = \
                1 - all( pixels[:,:,:] == border, 2 )

        ytb = 1
        while ytb <= idy:
            if not all( bitmap[ytb,:] == 0 ):
                break

            ytb += 1

        ybb = idy + 1
        while ybb > (ytb + 1):
            ybb -= 1
            if not all( bitmap[ybb,:] == 0 ):
                ybb += 1

                break

        xlb = 1
        while xlb <= idx:
            if not all( bitmap[ytb:ybb,xlb] == 0 ):
                break

            xlb += 1

        xrb = idx + 1
        while xrb > (xlb + 1):
            xrb -= 1
            if not all( bitmap[ytb:ybb,:xrb] == 0 ):
                xrb += 1

                break

        # Process each pixel and add it to a labeled region based on its
        # connectivity with other neighboring pixels:
        xl = xr = yt = yb = 0
        for y in xrange( ytb, ybb ):
            if image is not self.image:
                return

            row = bitmap[ y, xlb: xrb ]
            if all( row == 0 ):
                continue

            y1     = y - 1
            label0 = labels[ y1, 0 ]
            label1 = labels[ y1, 1 ]
            region = last_region = 0
            for x in xrange( xlb, xrb ):
                x1     = x - 1
                label2 = labels[ y1, x + 1 ]
                if row[ x - xlb ]:
                    matches = set( [ label0, label1, label2, region ] )
                    matches.discard( 0 )
                    if len( matches ) == 0:
                        labels[ y, x ] = region = len( regions )
                        equivalence.append( set( [ region ] ) )
                        regions[ last_region ] = xl, yt, xr, yb
                        xl = xr = x1
                        yt = yb = y1
                        regions.append( None )  # Placeholder, updated later
                    else:
                        labels[ y, x ] = region = min( matches )
                        if region != last_region:
                            regions[ last_region ] = xl, yt, xr, yb
                            xl, yt, xr, yb         = regions[ region ]

                        xl = min( xl, x1 )
                        xr = max( xr, x1 )
                        yt = min( yt, y1 )
                        yb = max( yb, y1 )

                        if len( matches ) > 1:
                            matches = list( matches )
                            for i in xrange( len( matches ) - 1 ):
                                region1 = matches[ i ]
                                for j in xrange( i + 1, len( matches ) ):
                                    region2 = matches[ j ]
                                    equivalence[ region1 ].add( region2 )
                                    equivalence[ region2 ].add( region1 )

                    last_region = region
                else:
                    region = 0

                label0 = label1
                label1 = label2

            regions[ last_region ] = xl, yt, xr, yb

        # Collapse all equivalent labeled regions into the single lowest
        # numbered region:
        for i in xrange( len( equivalence ) - 1, 1, -1 ):
            j = sorted( equivalence[ i ] )[0]
            if i > j:
                xl1, yt1, xr1, yb1 = regions[ j ]
                xl2, yt2, xr2, yb2 = regions[ i ]
                regions[ j ] = ( min( xl1, xl2 ), min( yt1, yt2 ),
                                 max( xr1, xr2 ), max( yb1, yb2 ) )
                del regions[ i ]

        # Collapse overlapping regions into the smallest enclosing region:
        i = 1
        while i < (len( regions ) - 1):
            xl1, yt1, xr1, yb1 = regions[ i ]
            j      = i + 1
            merged = False
            while j < len( regions ):
                xl2, yt2, xr2, yb2 = regions[ j ]
                if (xr2 < xl1) or (xl2 > xr1) or (yb2 < yt1) or (yt2 > yb1):
                    j += 1
                else:
                    xl1, yt1, xr1, yb1 = (
                        min( xl1, xl2 ), min( yt1, yt2 ),
                        max( xr1, xr2 ), max( yb1, yb2 )
                    )
                    merged = True
                    del regions[ j ]

            if merged:
                regions[ i ] = ( xl1, yt1, xr1, yb1 )
            else:
                i += 1

        # Convert all surviving regions from ( xl, yt, xr, yb ) format to
        # ( xl, yt, dx, dy ) format:
        for i in xrange( 1, len( regions ) ):
            xl, yt, xr, yb = regions[ i ]
            regions[ i ]   = ( xl, yt, xr - xl + 1, yb - yt + 1 )

        # Update the tool state with the resulting set of regions:
        if image is self.image:
            self.regions = regions[1:]

#-- EOF ------------------------------------------------------------------------