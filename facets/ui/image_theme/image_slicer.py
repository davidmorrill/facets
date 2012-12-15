"""
Experimental image slicer for Theming Engine II
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from hashlib \
    import md5

from numpy \
    import reshape, fromstring, int8, abs, zeros

from facets.api \
    import HasPrivateFacets, Any, Tuple, Int, Instance, Str, List, Property, \
           View, Item, NotebookEditor, property_depends_on

from facets.ui.pyface.api \
    import ImageResource

from facets.ui.pyface.i_image_resource \
    import AnImageResource

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The shortest repeating span we are interested in:
MinSpan = 10

# Mapping from 'top/left' to 'horizontal/vertical':
tl_hv_map = { 't': 'v', 'l': 'h' }

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def span ( low_high ):
    """ Returns the size of a specified [ low, high ] span.
    """
    return (low_high[1] - low_high[0] + 1)


def ratio1 ( v1, v2 ):
    """ Returns whether the ratio of two numbers is approximately 1.0.
    """
    return (0.95 <= (v1 / v2) <= 1.05)

#-------------------------------------------------------------------------------
#  'SubImage' class:
#-------------------------------------------------------------------------------

class SubImage ( HasPrivateFacets ):
    """ Defines a sub-image of a larger image being analyzed.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The offset of the sub-image within the main image:
    offset = Tuple( Int, Int )

    # The sub-image data:
    data = Any # 2D numpy RGBA array

    # The list of horizontal slices:
    horizontal = List

    # The list of vertical slices:
    vertical = List

    # The score for the sub-image (higher scores for images with larger
    # horizontal and vertical ranges):
    score = Int

    # The optimal content offset for the image:
    content = Any # Tuple( Int, Int, Int, Int )

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Calculates the lists of significant horizontal and vertical spans
            for the sub-image data.
        """
        data                 = self.data
        rows, columns, depth = data.shape
        horizontal           = []
        vertical             = []

        for i in xrange( rows ):
            self._add_rc( i, data[ i ], horizontal )

        for i in xrange( columns ):
            self._add_rc( i, data[ :, i ], vertical )

        self.horizontal = self._post_process( horizontal, lambda r: data[ r ] )
        self.vertical   = self._post_process( vertical, lambda c: data[ :, c ] )

        if (len( self.horizontal ) == 0) and (len( self.vertical ) == 0):
            horizontal = []
            vertical   = []

            for i in xrange( rows ):
                self._add_rc2( i, data[ i ], horizontal )

            for i in xrange( columns ):
                self._add_rc2( i, data[ :, i ], vertical )

            self.horizontal = self._post_process2( horizontal )
            self.vertical   = self._post_process2( vertical )


    def clean ( self ):
        """ Remove all but the longest span set from the horizontal and vertical
            ranges of the sub-image.
        """
        self.horizontal = self._clean( self.horizontal )
        self.vertical   = self._clean( self.vertical )

    #-- Facet Default Values ---------------------------------------------------

    def _score_default ( self ):
        score = 0
        for items in self.horizontal:
            for item in items:
                score += span( item )

        for items in self.vertical:
            for item in items:
                score += span( item )

        return score


    def _content_default ( self ):
        data = self.data
        rows, columns, depth = data.shape
        left, right = self.vertical[0][0]
        top, bottom = self.horizontal[0][0]
        left   += 1
        right  -= 1
        top    += 1
        bottom -= 1
        xrow    = lambda row:    data[ row, left: right + 1 ]
        xcolumn = lambda column: data[ top: bottom + 1, column ]
        topx    = self._scan( top, -1,       -1, xrow )    + 1
        bottomx = self._scan( bottom, rows,   1, xrow )    - 1
        leftx   = self._scan( left, -1,      -1, xcolumn ) + 1
        rightx  = self._scan( right, columns, 1, xcolumn ) - 1
        dleft   = left    - leftx
        dright  = rightx  - right
        dtop    = top     - topx
        dbottom = bottomx - bottom
        tl      = zeros( ( dtop,    dleft  ), int8 )
        tr      = zeros( ( dtop,    dright ), int8 )
        bl      = zeros( ( dbottom, dleft  ), int8 )
        br      = zeros( ( dbottom, dright ), int8 )
        left1   = left   - 1
        top1    = top    - 1
        right1  = right  + 1
        bottom1 = bottom + 1

        rn = topx - 1
        for c in xrange( dleft ):
            rn = self._scan( top, rn, -1,
                             lambda row: data[ row, left - c - 1: left ] )
            for r in xrange( top1 - rn ):
                tl[ r, c ] += 1

            if rn >= top1:
                break

        rn = topx - 1
        for c in xrange( dright ):
            rn = self._scan( top, rn, -1,
                             lambda row: data[ row, right1: right1 + c + 1 ] )
            for r in xrange( top1 - rn ):
                tr[ r, c ] += 1

            if rn >= top1:
                break

        rn = bottomx + 1
        for c in xrange( dleft ):
            rn = self._scan( bottom, rn, 1,
                             lambda row: data[ row, left - c - 1: left ] )
            for r in xrange( rn - bottom1 ):
                bl[ r, c ] += 1

            if rn <= bottom1:
                break

        rn = bottomx + 1
        for c in xrange( dright ):
            rn = self._scan( bottom, rn, 1,
                             lambda row: data[ row, right1: right1 + c + 1 ] )
            for r in xrange( rn - bottom1 ):
                br[ r, c ] += 1

            if rn <= bottom1:
                break

        cn = leftx - 1
        for r in xrange( dtop ):
            cn = self._scan( left, cn, -1,
                             lambda col: data[ top - r - 1: top, col ] )
            for c in xrange( left1 - cn ):
                tl[ r, c ] += 1

            if cn >= left1:
                break

        cn = leftx - 1
        for r in xrange( dbottom ):
            cn = self._scan( left, cn, -1,
                     lambda col: data[ bottom1: bottom1 + r + 1: bottom, col ] )
            for c in xrange( left1 - cn ):
                bl[ r, c ] += 1

            if cn >= left1:
                break

        cn = rightx + 1
        for r in xrange( dtop ):
            cn = self._scan( right, cn, 1,
                             lambda col: data[ top - r - 1: top, col ] )
            for c in xrange( cn - right1 ):
                tr[ r, c ] += 1

            if cn <= right1:
                break

        cn = rightx + 1
        for r in xrange( dbottom ):
            cn = self._scan( right, cn, 1,
                     lambda col: data[ bottom1: bottom1 + r + 1: bottom, col ] )
            for c in xrange( cn - right1 ):
                br[ r, c ] += 1

            if cn <= right1:
                break

        max_score = -1.0
        content   = ( -1, -1, -1, -1 )
        for t in xrange( dtop ):
            for l in xrange( dleft ):
                if tl[ t, l ] != 2:
                    break

                for r in xrange( dright ):
                    if tr[ t, r ] != 2:
                        break

                    for b in xrange( dbottom - 1, -1, -1 ):
                        if (bl[ b, l ] != 2) or (br[ b, r ] != 2):
                            continue

                        score = (1.33 * (t + b)) + (l + r)
                        if score > max_score:
                            max_score = score
                            content   = ( l, t, r, b )

                        break

        l, t, r, b = content

        return ( left - l - 1, top - t - 1, right + r + 1, bottom + b + 1 )

    #-- Private Methods --------------------------------------------------------

    def _add_rc ( self, index, data, rc ):
        """ Adds the *key* for the *index*th row/column to the row/column
            dictionary specified by *rc*.
        """
        key = md5( data.tostring() ).digest()
        if len( rc ) > 0:
            start, end, key2 = last = rc[-1]
            if key == key2:
                last[1] = index

                return

            if (end - start + 1) <= MinSpan:
                last[0] = last[1] = index
                last[2] = key

                return

        rc.append( [ index, index, key ] )


    def _post_process ( self, items, extract ):
        """ Returns a sorted list of all significant span ranges in the
            dictionary specified by *dic*.
        """
        if span( items[-1] ) < MinSpan:
            del items[-1]

        n = len( items )
        for i in xrange( n - 1 ):
            start, end, key = items[ i ]
            data = extract( start )
            for j in xrange( i + 1, n ):
                start2, end2, key2 = items[ j ]
                if (key != key2) and self._similar( data, extract( start2 ) ):
                    items[ j ][2] = key

        result = []
        keys   = {}
        for start, end, key in items:
            index = keys.get( key )
            if index is None:
                keys[ key ] = index = len( result )
                result.append( [] )

            result[ index ].append( [ start, end ] )

        return result


    def _add_rc2 ( self, index, data, rc ):
        """ Adds the *key* for the *index*th row/column to the row/column
            dictionary specified by *rc*.
        """
        key = md5( data.tostring() ).digest()
        if len( rc ) > 0:
            start, end, key2, data2 = last = rc[-1]
            if self._similar( data, data2 ):
                last[1] = index
                last[3] = data

                return

            if (end - start + 1) <= MinSpan:
                last[0] = last[1] = index
                last[2] = key
                last[3] = data

                return

        rc.append( [ index, index, key, data ] )


    def _post_process2 ( self, items ):
        """ Returns a sorted list of all significant span ranges in the
            dictionary specified by *dic*.
        """
        if span( items[-1] ) < MinSpan:
            del items[-1]

        n = len( items )
        for i in xrange( n - 1 ):
            start, end, key, data = items[ i ]
            for j in xrange( i + 1, n ):
                start2, end2, key2, data2 = items[ j ]
                if self._similar( data, data2 ):
                    items[ j ][2] = key

        result = []
        keys   = {}
        for start, end, key, data in items:
            index = keys.get( key )
            if index is None:
                keys[ key ] = index = len( result )
                result.append( [] )

            result[ index ].append( [ start, end ] )

        return result


    def _similar ( self, x1, x2 ):
        """ Returns True if the values of x1 and x2 are heuristically very close
            to each other; and False if they are not.
        """
        return (abs( x1 - x2 ).sum() <= (0.10 * x1.shape[0]))


    def _scan ( self, first, last, increment, extract ):
        test      = extract( first )
        threshold = 4.0 * test.shape[0]
        for i in xrange( first + increment, last, increment ):
            base, test = test, extract( i )
            if abs( test - base ).sum() > threshold:
                return i

        return last


    def _clean ( self, hv ):
        """ Returns the longest span of items in the horizontal or vertical span
            list specified by *hv*.
        """
        longest = 0
        for items in hv:
            length = reduce( lambda x, y: x + span( y ), items, 0 )
            if length > longest:
                longest = length
                result  = items

        return [ result ]

#-------------------------------------------------------------------------------
#  'ImageSlicer' class:
#-------------------------------------------------------------------------------

class ImageSlicer ( HasPrivateFacets ):
    """ Experimental image slicer for Theming Engine II.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the image file to slice:
    name = Str

    # The ImageResource to slice:
    image = Instance( AnImageResource )

    # The image color data for the current image (an n x m x 4 numpy array):
    data = Property

    # The encoded form of the image slicing data:
    encoded = Str

    #-- Public Methods ---------------------------------------------------------

    def analyze ( self ):
        """ Performs the image analysis.
        """
        data                 = self.data
        main_image           = SubImage( data = data )
        horizontal           = main_image.horizontal
        vertical             = main_image.vertical
        image_type           = self._classify( horizontal, vertical )
        rows, columns, depth = data.shape

        if image_type[:1] == 'l':
            is_vertical_split = (image_type[2] in 'tb')
            if is_vertical_split:
                hv0, hv1 = horizontal
                splitter = self._split_row
            else:
                hv0, hv1 = vertical
                splitter = self._split_column

            low  = splitter( hv0[-1][-1] + 1, data )
            high = splitter( hv1[0][0]   - 1, data )
            while True:
                if (low[0] + 1) >= high[0]:
                    break

                mid = splitter( (low[0] + high[0]) / 2, data )
                if ((max( low[1].score,  mid[1].score ) +
                     max( low[2].score,  mid[2].score )) >=
                    (max( high[1].score, mid[1].score ) +
                     max( high[2].score, mid[2].score ))):
                    high = mid
                else:
                    low = mid

            if ((low[1].score  + low[2].score) >=
                (high[1].score + high[2].score)):
                high = low

            _, sub_image_0, sub_image_1 = high
            sub_image_0.clean()
            sub_image_1.clean()
            self._encode_image_slice( image_type, sub_image_0, sub_image_1 )
        else:
            self._encode_image_slice( image_type, main_image )

    #-- Private Methods --------------------------------------------------------

    def _classify ( self, horizontal, vertical ):
        """ Classify the type of image based on its horizontal and vertical
            spans.
        """
        hn  = len( horizontal )
        vn  = len( vertical )
        hnt = reduce( lambda x, y: x + len( y ), horizontal, 0 )
        vnt = reduce( lambda x, y: x + len( y ), vertical,   0 )
        if (hn * vn) == 0:
            return 'invalid'

        if vnt == 1:
            if hnt == 1:
                return 'b1'

            return self._classify_1( hnt, hn, horizontal, 't', 'b' )

        if hnt == 1:
            return self._classify_1( vnt, vn, vertical, 'l', 'r' )

        if hnt == 2:
            if vnt == 2:
                if (hn == 1) and (vn == 1):
                    rows, columns, depth = self.data.shape
                    h0, h1 = horizontal[0]
                    v0, v1 = vertical[0]
                    h0     = float( span( h0 ) ) / rows
                    h1     = float( span( h1 ) ) / rows
                    v0     = float( span( v0 ) ) / columns
                    v1     = float( span( v1 ) ) / columns
                    if (ratio1( h0, h1 ) and
                        ratio1( v0, v1 ) and
                        ratio1( h0, v0 )):
                        return 'bhv'
                    min_hv = min( h0, h1, v0, v1 )
                    if h0 == min_hv:
                        return 'lht_bh'

                    if h1 == min_hv:
                        return 'lhb_bh'

                    if v0 == min_hv:
                        return 'lvl_bv'

                    return 'lvr_bv'

                return 'unknown'

            if (vnt == 3) and (vn == 2) and (hn == 1):
                v0, v1 = vertical
                if len( v0 ) == 1:
                    if span( v0[0] ) < max( span( v1[0] ), span( v1[1] ) ):
                        return 'lvl_bh'

                    return 'lhr_bv'
                elif v1[0] > v0[1][1]:
                    if span( v1[0] ) < max( span( v0[0] ), span( v0[1] ) ):
                        return 'lvr_bh'

                    return 'lhr_bv'

        if (hnt == 3) and (hn == 2) and (vnt == 2) and (vn == 1):
            h0, h1 = horizontal
            if len( h0 ) == 1:
                return 'lht_bhv'

#                if span( h0[0] ) < max( span( h1[0] ), span( h1[1] ) ):
#                    return 'lht_bv'
#
#                return 'lvb_bh'
            elif h1[0] > h0[1][1]:
                return 'lhb_bhv'
#                if span( h1[0] ) < max( span( h0[0] ), span( h0[1] ) ):
#                    return 'lhb_bv'
#
#                return 'lvt_bh'

        # Unrecognized configuration of sections:
        return 'unknown'


    def _classify_1 ( self, nt, n, spans, tl, br ):
        """ Returns the classification for an image which has a single span in
            one axis, but multiple spans in the other axis.
        """
        s0 = spans[0]
        if nt == 2:
            if n == 2:
                if span( s0[0] ) < span( spans[1][0] ):
                    br = tl

                return ('l1%s_b1' % br)

            if span( s0[0] ) < span( s0[1] ):
                br = tl

            return ('b' + br)

        hv = tl_hv_map[ tl ]
        if nt == 3:
            if n == 1:
                if span( s0[0] ) < span( s0[2] ):
                    br = tl

                return ('l1%s_b%s' % ( br, hv ))

            if n == 2:
                if len( s0 ) == 1:
                    return ('l1%s_b%s' % ( tl, hv ))

                if spans[1][0][0] > s0[-1][1]:
                    return ('l1%s_b%s' % ( br, hv ))

                return 'unknown'

            # Three different sections:
            return 'unknown'

        if (nt == 4) and (n == 2):
            s1 = spans[1]
            if s0[1][1] < s1[0][0]:
                hv = tl_hv_map[ tl ]
                if ((span( s0[0] ) + span( s0[1] )) <
                    (span( s1[0] ) + span( s1[1] ))):
                    br = tl

                return ('l%s%s_b%s' % ( hv, br, hv ))

        return 'unknown'


    def _encode_image_slice ( self, image_type, sub_image1, sub_image2 = None ):
        """ Encodes the image slicing data described by the specified
            *image_type* and the one or two SubImage objects specified by
            *sub_image1* and *sub_image2*.
        """
        if sub_image2 is None:
            encoded = self._encode_image_data( 'M', sub_image1 )
        else:
            side = image_type[2].upper()
            if side in 'BR':
                encoded = '%s\n\n%s' % (
                    self._encode_image_data( side, sub_image2 ),
                    self._encode_image_data( 'M',  sub_image1 ) )
            else:
                encoded = '%s\n\n%s' % (
                    self._encode_image_data( side, sub_image1 ),
                    self._encode_image_data( 'M',  sub_image2 ) )

        self.encoded = encoded


    def _encode_image_data ( self, side, sub_image ):
        """ Returns the encoded form of the image slice data contained in the
            SubImage specified by *sub_image* to the current encoded slicing
            data string. The type of slicing data is specified by *side* which
            can be one of the characters in 'MTLBR' (Main, Top, Left, Bottom,
            Right).
        """
        x0, y0     = sub_image.offset
        dy, dx, dz = sub_image.data.shape
        dx         = int( dx )
        dy         = int( dy )
        data       = [ side + self._encode_tuple( x0, y0, x0 + dx, y0 + dy ) ]
        xs         = []
        ys         = []
        for item in sub_image.horizontal[0]:
            ys.extend( item )

        for item in sub_image.vertical[0]:
            xs.extend( item )

        xl, xr = xs[0], xs[1]
        yt, yb = ys[0], ys[1]

        data.append( 'S' +
            self._encode_tuple( x0 + xl, y0 + yt, x0 + xs[-1], y0 + ys[-1] )
        )
        if len( xs ) > 2:
            data.append( 'H' + self._encode_tuple( x0 + xr, x0 + xs[-2] ) )

        if len( ys ) > 2:
            data.append( 'V' + self._encode_tuple( y0 + yb, y0 + ys[-2] ) )

        cxl, cyt, cxr, cyb = sub_image.content
        data.append(
            'O' + self._encode_tuple( xl - cxl, yt - cyt, cxr - xr, cyb - yb )
        )

        color = sub_image.data[ (yt + yb) / 2, (xl + xr) / 2 ][0:3]
        data.append(
            'C' + self._encode_tuple( *[ (c & 0xFF) for c in color ] )
        )

        return '\n'.join( data )


    def _encode_tuple ( self, *args ):
        """ Returns the list of numeric *args* encoded as a string tuple.
        """
        return ('%s' % ( args, )).replace( ' ', '' )


    def _split_row ( self, row, data ):
        return ( row,
                 SubImage( offset = ( 0, 0 ),   data = data[ :row ] ),
                 SubImage( offset = ( 0, row ), data = data[ row: ] ) )


    def _split_column ( self, column, data ):
        return ( column,
                 SubImage( offset = ( 0, 0 ),      data = data[ :, :column ] ),
                 SubImage( offset = ( column, 0 ), data = data[ :, column: ] ) )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'image' )
    def _get_data ( self ):
        bitmap = self.image.bitmap
        image  = bitmap.toImage()
        bits   = image.bits()
        bits.setsize( image.numBytes() )
        data = reshape( fromstring( bits.asstring(), int8 ),
                        ( bitmap.height(), bitmap.width(), 4 ) )
        data[0:,0:,0:3 ] = data[0:,0:,2:-5:-1]

        return data

    #-- Facet Event Handlers ---------------------------------------------------

    def _name_set ( self, image_name ):
        """ Handles the 'name' facet being changed.
        """
        self.image = ImageResource( image_name )


    def _image_set ( self ):
        """ Handles the 'image' facet being changed.
        """
        self.analyze()

#-------------------------------------------------------------------------------
#  Run the test case:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    from facets.extra.tools.file_stack import FileStack
    from facets.api                    import HSplit

    class ImageSlicerTool ( HasPrivateFacets ):
        browser = Instance( FileStack )
        slicer  = Instance( ImageSlicer, () )
        viewers = Property( List ) # ( ImageSliceViewer )

        #-- Facet Default Values -----------------------------------------------

        view = View(
            HSplit(
                Item( 'browser', style  = 'custom' ),
                Item( 'viewers', editor = NotebookEditor(
                                              page_name = '.name' )
                ),
                id          = 'splitter',
                show_labels = False
            ),
            title     = 'Image Slicer Tool',
            id        = 'image_slicer_tool',
            width     = 0.5,
            height    = 0.5,
            resizable = True
        )

        #-- Facet Default Values -----------------------------------------------

        def _browser_default ( self ):
            browser = FileStack(
                file_name = r'C:\Assembla\trunk\facets\ui\image_theme\images\SlicingTest.png'
            )
            browser.sync_facet( 'file_name', self.slicer, 'name' )

            return browser

        #-- Property Implementations -------------------------------------------

        @property_depends_on( 'slicer.encoded' )
        def _get_viewers ( self ):
            from theme              import Theme
            from image_slice_viewer import ImageSliceViewer

            slicer = self.slicer
            theme  = Theme.decode_image_slice( slicer.encoded, slicer.image )
            result = [
                ImageSliceViewer(
                    name        = name,
                    image_slice = info.image_slice )
                for name, info in (
                    ( ( 'Bottom Label', 'Top Label' )[ theme.on_top ],
                      theme.horizontal ),
                    ( ( 'Right Label', 'Left Label' )[ theme.on_left ],
                      theme.vertical ),
                    ( 'Body', theme.body ) )
                if info is not None
            ]
            result.insert( 0, ImageSliceViewer( name  = 'Original',
                                                image = slicer.image ) )

            return result

    ImageSlicerTool().edit_facets()
else:
    demo = ImageSlicer( name = r'C:\Assembla\trunk\facets_extra\assets\Theming Engine II\SlicingTest.png' )

#-- EOF ------------------------------------------------------------------------
