"""
The base definitions for an image resource.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import maximum, minimum, choose, uint8, alltrue, ones, compress

from os.path \
    import abspath, split

from facets.lib.resource.resource_path \
    import resource_path

from facets.core_api \
    import HasPrivateFacets, Event, List, Unicode, Property, \
           cached_property, property_depends_on

from facets.core.cfacets \
    import image_transform

from facets.core.facet_base \
    import clamp as clamped

from resource_manager \
    import resource_manager

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

OneThird  = 1.0 / 3.0
OneSixth  = 1.0 / 6.0
TwoThirds = 2.0 / 3.0

# Mapping from image filter name to image filter index:
filter_map = {
    'Bell':              0,
    'Box':               1,
    'CatmullRom':        2,
    'Cosine':            3,
    'CubicConvolution':  4,
    'CubicSpline':       5,
    'Hermite':           6,
    'Lanczos3':          7,
    'Lanczos8':          8,
    'Mitchell':          9,
    'Quadratic':        10,
    'QuadraticBSpline': 11,
    'Triangle':         12
}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def validate ( value ):
    """ Returns a specified array as a numpy 'uint8' array.
    """
    if value.dtype == uint8:
        return value

    return (255.0 * clamp( value )).astype( uint8 )


def clamp ( value ):
    """ Returns an array whose values are clamped in the range: [0.0...1.0].
    """
    return maximum( 0.0, minimum( 1.0, value ) )


def convert ( hue, lightness, saturation, m1, m2 ):
    """ Returns one channel of an HSL to RGB conversion.
    """
    hue = hue % 1.0
    dm  = m2 - m1

    return (choose( saturation == 0.0, [
                choose( hue < OneSixth, [
                    choose( hue < 0.5, [
                        choose( hue < TwoThirds, [
                            m1,
                            m1 + (dm * (TwoThirds - hue) * 6.0) ] ),
                        m2 ] ),
                    m1 + (dm * hue * 6.0) ] ),
                lightness ] ) * 255.0).astype( uint8 )


def image_from_pixels ( pixels ):
    """ Returns a new ImageResource object containing an image derived from
        the array of RGBA pixels specified by *pixels*.
    """
    from facets.api import toolkit
    from facets.ui.pyface.image_resource import ImageResource

    dy, dx, _ = pixels.shape
    bits      = pixels.tostring()
    image     = ImageResource( bitmap = toolkit().create_bitmap( bits, dx, dy ) )

    # Save the pixel data to avoid it being garbage collected:
    image._buffer = bits

    return image

#-------------------------------------------------------------------------------
#  'AnImageResource' abstract base class:
#-------------------------------------------------------------------------------

class AnImageResource ( HasPrivateFacets ):
    """ The base class that contains common code for toolkit specific
        implementations of ImageResource.
    """

    #-- 'ImageResource' Interface ----------------------------------------------

    # The name of the image:
    name = Unicode

    # The toolkit specific image:
    image = Property

    # The toolkit specific bitmap representation of the image:
    bitmap = Property

    # A monochrome version of the toolkit specific representation of the image:
    mono_bitmap = Property

    # The toolkit specific icon representation of the image:
    icon = Property

    # The width of the image in pixels:
    width = Property

    # The height of the image in pixels:
    height = Property

    # A graphics object that can be used to draw on the image:
    graphics = Property

    # Event to fire when the image 'pixels' have been modified to rebuild the
    # associated images:
    modified = Event

    # The pixel data for the image:
    pixels = Property

    # The raw 'red' component on the image:
    r = Property

    # The raw 'green' component of the image:
    g = Property

    # The raw 'blue' component of the image:
    b = Property

    # The raw 'alpha' component of the image:
    a = Property

    # The 'red' component on the image:
    red = Property

    # The 'green' component of the image:
    green = Property

    # The 'blue' component of the image:
    blue = Property

    # The 'alpha' component' of the image:
    alpha = Property

    # The 'hue' component of the image:
    hue = Property

    # The 'lightness' component of the image:
    lightness = Property

    # The 'saturation' component of the image:
    saturation = Property

    #-- Private Facet Definitions ----------------------------------------------

    # The maximum value of the red, green and blue components:
    max_rgb = Property

    # The minimum value of the red, green and blue components:
    min_rgb = Property

    # The difference between the maximum and minimum rgb values:
    minus = Property

    # The sum of the maximum and minimum rgb values:
    plus = Property

    #-- Object Method Overrides ------------------------------------------------

    def __str__ ( self ):
        """ Returns the string representation of the image.
        """
        return str( self.name )

    #-- Public Methods ---------------------------------------------------------

    def create_image ( self, size = None ):
        """ Creates a toolkit specific image for this resource.
        """
        raise NotImplementedError


    def create_bitmap ( self, size = None ):
        """ Creates a toolkit specific bitmap for this resource.
        """
        raise NotImplementedError


    def create_icon ( self, size = None ):
        """ Creates a toolkit-specific icon for this resource.
        """
        raise NotImplementedError


    def create_bitmap_from_pixels ( self ):
        """ Creates a toolkit specific bitmap from the 'pixels' for this
            resource.
        """
        raise NotImplementedError


    def create_icon_from_pixels ( self ):
        """ Creates a toolkit specific icon from the 'pixels' for this resource.
        """
        raise NotImplementedError


    def save ( self, file_name ):
        """ Saves the image to the specified *file_name*. The *file_name*
            extension determines the format the file is saved in, and may be
            '.png', '.jpg' or '.jpeg', although other file formats may be
            supported, depending upon the underlying GUI toolkit implementation.
        """
        raise NotImplementedError

    #-- Concrete Method Implementations ----------------------------------------

    def create_image_from_pixels ( self ):
        """ Creates a toolkit specific image from the 'pixels' for this
            resource.
        """
        from facets.api import toolkit

        # Note that we keep a reference to the pixel data buffer because some
        # toolkit implementations do not take ownership of the buffer data when
        # creating the bitmap. This can result in a hard crash if we do not keep
        # the reference for them:
        pixels       = self.pixels
        self._buffer = pixels.tostring()
        height, width, channels = pixels.shape

        return toolkit().create_bitmap( self._buffer, width, height )


    def create_bitmap_from_pixels ( self ):
        """ Creates a toolkit specific bitmap from the 'pixels' for this
            resource.
        """
        from facets.api import toolkit

        # Note that we keep a reference to the pixel data buffer because some
        # toolkit implementations do not take ownership of the buffer data when
        # creating the bitmap. This can result in a hard crash if we do not keep
        # the reference for them:
        pixels       = self.pixels
        self._buffer = pixels.tostring()
        height, width, channels = pixels.shape

        return toolkit().create_bitmap( self._buffer, width, height )


    def rgba ( self, red = None, green = None, blue = None, alpha = None ):
        """ Sets a new set of pixel values from a specified set of red, green,
            blue and alpha components. Any omitted component uses the current
            value of the same component.
        """
        pixels = self.pixels

        if red is not None:
            pixels[:,:,2] = validate( red )

        if blue is not None:
            pixels[:,:,0] = validate( blue )

        if green is not None:
            pixels[:,:,1] = validate( green )

        if alpha is not None:
            pixels[:,:,3] = validate( alpha )

        self.modified = True


    def hlsa ( self, hue = None, lightness = None, saturation = None,
                     alpha = None ):
        """ Sets a new set of pixel values from a specified set of hue,
            lightness, saturation and alpha components. Any omitted component
            uses the current value of the same component.
        """
        if hue is None:
            hue = self.hue
        else:
            hue = hue % 1.0

        if lightness is None:
            lightness = self.lightness
        else:
            lightness = clamp( lightness )

        if saturation is None:
            saturation = self.saturation
        else:
            saturation = clamp( saturation )

        if alpha is None:
            alpha = self.alpha

        m2 = choose( lightness <= 0.5, [
                     lightness + saturation - (lightness * saturation),
                     lightness * (1.0 + saturation) ] )
        m1 = (2.0 * lightness) - m2

        pixels        = self.pixels
        pixels[:,:,0] = convert( hue - OneThird, lightness, saturation, m1, m2 )
        pixels[:,:,1] = convert( hue,            lightness, saturation, m1, m2 )
        pixels[:,:,2] = convert( hue + OneThird, lightness, saturation, m1, m2 )
        pixels[:,:,3] = validate( alpha )

        self.modified = True


    def scale ( self, size, filter = 'Lanczos3' ):
        """ Returns a new ImageResource object derived from this one which has
            been scaled to the size specified by *size* using the image filter
            specified by *filter*.

            *Size* may either be a tuple of the form (width, height) specifying
            the target image width and height in pixels (e.g. (100,80)), or a
            single float value representing the image scaling factor (e.g. 0.5).

            If the tuple form is used, one of the two values may be zero (e.g.
            (100,0)). In this case, the zero value will be replaced by the
            scaled width or height needed to preserve the current aspect ratio
            of the image based on the other, non-zero value specified. This
            could be useful when trying to create thumbnail images with a
            common width (or height) for example.

            *filter* specifies the optional name of the image filter to use
            while scaling the image. The possible values are:
              - Bell
              - Box
              - CatmullRom
              - Cosine
              - CubicConvolution
              - CubicSpline
              - Hermite
              - Lanczos3 (default)
              - Lanczos8
              - Mitchell
              - Quadratic
              - QuadraticBSpline
              - Triangle
        """
        global filter_map
        from facets.api import toolkit
        from facets.ui.pyface.image_resource import ImageResource

        if isinstance( size, tuple ):
            width, height = size
            if width == 0:
                width = round( float( self.width * height ) / self.height )
            elif height == 0:
                height = round( float( self.height * width ) / self.width )
        else:
            width  = round( self.width  * size )
            height = round( self.height * size )

        width  = clamped( int( width ),  1, 8192 )
        height = clamped( int( height ), 1, 8192 )
        if (width == self.width) and (height == self.height):
            return self

        pixels = image_transform(
            self.pixels.tostring(),
            self.width, self.height, width, height, filter_map[ filter ]
        )

        image = ImageResource(
            bitmap = toolkit().create_bitmap( pixels, width, height )
        )

        # Save the pixel data to avoid it being garbage collected:
        image._buffer = pixels

        return image


    def crop ( self, x = 0, y = 0, dx = -1, dy = -1 ):
        """ Returns a new ImageResource object derived from this one by cropping
            it to the size specified by the rectangle (x,y,dx,dy). The default
            value for *x* and *y* is 0, while the default value for *dx* (width)
            and *dy* (height) is -1. If *x* or *y* is less than 0, 0 is used.
            If *dx* or *dy* is less than 0, the full image width (or height) is
            used. If the resulting cropping rectangle size has a 0 width or
            height, None is returned.
        """
        # Perform sanity checks on all inputs:
        x, y = max( 0, x ), max( 0, y )

        if dx < 0:
            dx = self.width

        if dy < 0:
            dy = self.height

        dx = min( dx, self.width  - x )
        dy = min( dy, self.height - y )

        if (dx <= 0) or (dy <= 0):
            return None

        return image_from_pixels( self.pixels[ y: (y + dy), x: (x + dx) ] )


    def trim ( self, level = 0.0 ):
        """ Returns a new copy of the image with all external edges having alpha
            levels <= *level* trimmed off.
        """
        if isinstance( level, float ):
            level = int( 255.0 * level )

        level = clamped( level, 0, 255 )
        a     = self.a

        for x1 in xrange( 0, self.width ):
            if not alltrue( a[ :, x1 ] <= level ):
                break

        for x2 in xrange( self.width - 1, x1 - 1, -1 ):
            if not alltrue( a[ :, x2 ] <= level ):
                break

        x2 += 1

        for y1 in xrange( 0, self.height ):
            if not alltrue( a[ y1, x1: x2 ] <= level ):
                break

        for y2 in xrange( self.height - 1, y1 - 1, -1 ):
            if not alltrue( a[ y2, x1: x2 ] <= level ):
                break

        return self.crop( x1, y1, x2 - x1, y2 - y1 + 1 )


    def squeeze ( self, amount = 20, tolerance = 0.4 ):
        """ Returns a new copy of the image with all duplicate row and column
            ranges in excess of *amount* removed. This can be useful for
            creating screen shots with the boring bits removed, and possibly
            saving the need to resize a window manually to achieve the same
            effect. The additional *tolerance* factor can also be used to help
            define what constitutes a duplicate row or column. A *tolerance* of
            0.0 means the rows or columns must be identical, with icreasing
            values providing a more tolerant measure of equality. This value
            may require some experimentation to achieve the best results.
        """
        pixels    = self.pixels.copy()
        amount    = max( 1, amount )
        tolerance = max( 0.0, tolerance )

        # Process the image from left to right:
        end      = self.width
        last     = end - amount
        i        = 0
        ps       = pixels[ :, 0 ]
        keep     = ones( ( end, ) )
        max_diff = tolerance * end
        while True:
            if i >= last:
                break

            for i1 in xrange( i + 1, end ):
                ps1 = pixels[ :, i1 ]
                if (maximum( ps1, ps ) - minimum( ps1, ps )).sum() > max_diff:
                    break

                ps = ps1
            else:
                i1 = end

            if i1 - i > amount:
                keep[ i + amount: i1 ] = 0

            i  = i1
            ps = ps1

        pixels = compress( keep, pixels, 1 )

        # Process the image from top to bottom:
        end      = self.height
        last     = end - amount
        i        = 0
        ps       = pixels[ 0, : ]
        keep     = ones( ( end, ) )
        max_diff = tolerance * end
        while True:
            if i >= last:
                break

            for i1 in xrange( i + 1, end ):
                ps1 = pixels[ i1, : ]
                if (maximum( ps1, ps ) - minimum( ps1, ps )).sum() > max_diff:
                    break

                ps = ps1
            else:
                i1 = end

            if i1 - i > amount:
                keep[ i + amount: i1 ] = 0

            i  = i1
            ps = ps1

        return image_from_pixels( compress( keep, pixels, 0 ) )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'modified' )
    def _get_image ( self ):
        if self._loaded is None:
            image        = self.create_image()
            self._loaded = True

            return image

        return self.create_image_from_pixels()


    @property_depends_on( 'modified', settable = True )
    def _get_bitmap ( self ):
        if self._loaded is None:
            bitmap       = self.create_bitmap()
            self._loaded = True

            return bitmap

        return self.create_bitmap_from_pixels()


    @property_depends_on( 'modified' )
    def _get_mono_bitmap ( self ):
        raise NotImplementedError


    @property_depends_on( 'modified' )
    def _get_icon ( self ):
        if self._loaded is None:
            icon         = self.create_icon()
            self._loaded = True

            return icon

        return self.create_icon_from_pixels()


    def _get_width ( self ):
        raise NotImplementedError


    def _get_height ( self ):
        raise NotImplementedError


    def _get_graphics ( self ):
        raise NotImplementedError


    def _get_pixels ( self ):
        raise NotImplementedError


    @property_depends_on( 'modified' )
    def _get_r ( self ):
        return self.pixels[:,:,2]


    @property_depends_on( 'modified' )
    def _get_g ( self ):
        return self.pixels[:,:,1]


    @property_depends_on( 'modified' )
    def _get_b ( self ):
        return self.pixels[:,:,0]


    @property_depends_on( 'modified' )
    def _get_a ( self ):
        return self.pixels[:,:,3]


    @property_depends_on( 'modified' )
    def _get_red ( self ):
        return (self.r / 255.0)


    @property_depends_on( 'modified' )
    def _get_green ( self ):
        return (self.g / 255.0)


    @property_depends_on( 'modified' )
    def _get_blue ( self ):
        return (self.b / 255.0)


    @property_depends_on( 'modified' )
    def _get_alpha ( self ):
        return (self.a / 255.0)


    @property_depends_on( 'modified' )
    def _get_hue ( self ):
        max_rgb = self.max_rgb
        rc      = (max_rgb - self.red)   / self.minus
        gc      = (max_rgb - self.green) / self.minus
        bc      = (max_rgb - self.blue)  / self.minus
        h       = (choose( max_rgb == self.red, [
                           choose( max_rgb == self.green, [
                                   4.0 + gc - rc,
                                   2.0 + rc - bc ] ),
                           bc - gc ] ) / 6.0) % 1.0

        return choose( self.minus == 0.0, [ h, 0.0 ] )


    @property_depends_on( 'modified' )
    def _get_lightness ( self ):
        return (self.plus / 2.0)


    @property_depends_on( 'modified' )
    def _get_saturation ( self ):
        return choose( self.minus == 0.0, [
                       choose( self.lightness <= 0.5, [
                               self.minus / (2.0 - self.plus),
                               self.minus / self.plus ] ),
                       0.0 ] )


    @property_depends_on( 'modified' )
    def _get_max_rgb ( self ):
        return maximum( self.red, maximum( self.green, self.blue ) )


    @property_depends_on( 'modified' )
    def _get_min_rgb ( self ):
        return minimum( self.red, minimum( self.green, self.blue ) )


    @property_depends_on( 'modified' )
    def _get_minus ( self ):
        return (self.max_rgb - self.min_rgb)


    @property_depends_on( 'modified' )
    def _get_plus ( self ):
        return (self.max_rgb + self.min_rgb)

#-------------------------------------------------------------------------------
#  'MImageResource' abstract base class:
#-------------------------------------------------------------------------------

class MImageResource ( AnImageResource ):
    """ The abstract base class that contains common code for toolkit specific
        implementations of ImageResource items that come from external
        resources.
    """

    #-- Class Variables --------------------------------------------------------

    # The "image not found": image:
    _image_not_found = None

    #-- 'MImageResource' Interface ---------------------------------------------

    # The absolute path to the image.
    absolute_path = Property( Unicode )

    # A list of directories, classes or instances that will be used to search
    # for the image (see the resource manager for more details).
    search_path = List

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, name = '', search_path = None, bitmap = None,
                   width = None, height = None, **facets ):
        """ Initializes the object.
        """
        self.name = name

        if (width is not None) and (height is not None) and (bitmap is None):
            from facets.api import toolkit

            bits         = '\x00' * (width * height * 4)
            bitmap       = toolkit().create_bitmap( bits, width, height )
            bitmap._bits = bits

        if bitmap is not None:
            self.bitmap = bitmap

        if search_path is not None:
            self.search_path = search_path
        else:
            search_path, name = split( name )
            if search_path != '':
                self.name        = name
                self.search_path = [ search_path ]
            else:
                self.search_path = [ resource_path() ]

        super( MImageResource, self ).__init__( **facets )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_absolute_path ( self ):
        # FIXME: This doesn't quite wotk the new notion of image size. We
        # should find out who is actually using this facet, and for what!
        # (AboutDialog uses it to include the path name in some HTML.)
        ref = self._get_ref()
        if ref is not None:
            return abspath( self._ref.filename )

        return self._get_image_not_found().absolute_path

    #-- 'ImageResource' Interface ----------------------------------------------

    def create_image ( self, size = None ):
        """ Creates a toolkit specific image for this resource.
        """
        ref = self._get_ref( size )
        if ref is not None:
            image = ref.load()
            if image is not None:
                return image

        return self._get_image_not_found_image()

    #-- Private Methods --------------------------------------------------------

    def _get_ref ( self, size = None ):
        """ Return the resource manager reference to the image.
        """
        if self._ref is None:
            self._ref = resource_manager.locate_image( self.name,
                                                       self.search_path, size )

        return self._ref


    def _get_image_not_found_image ( self ):
        """ Returns the 'image not found' image.
        """
        not_found = self._get_image_not_found()

        if not_found is not None:
            return not_found.image

        raise ValueError( "cannot locate the file for 'image_not_found'" )


    @classmethod
    def _get_image_not_found ( cls ):
        """ Returns the 'image not found' image resource.
        """
        if cls._image_not_found is None:
            from facets.ui.ui_facets import image_for

            cls._image_not_found = image_for( '@facets:image_not_found' )

        return cls._image_not_found

#-- EOF ------------------------------------------------------------------------