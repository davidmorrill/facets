"""
Defines a set up useful, image related classes.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import copy, reshape, fromstring, uint8, zeros

from math \
    import fmod

from facets.api \
    import HasPrivateFacets, Any, Int, Str, Instance, Tuple, Event, Image,  \
           Range, RangeSliderEditor, RangeEditor, View, Item, on_facet_set, \
           property_depends_on

from facets.core.cfacets \
    import hlsa_transform

from facets.core.facet_base \
    import clamp

from facets.ui.pyface.image_resource \
    import ImageResource

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The editor used for double-ended range facets:
range_editor = RangeSliderEditor(
    low = 0.0, high = 1.0, increment = 0.01, body_style = 25
)

# The editor used for simple range facets:
slider_editor = RangeEditor( increment = 0.01, body_style = 25 )

# Mapping from encoded transform/mask value to facet name:
NameMap = {
    'h': 'hue',
    'l': 'lightness',
    's': 'saturation',
    'a': 'alpha'
}

# The names of the mask and transform values to encode/decode:
Names = ( 'hue', 'lightness', 'saturation', 'alpha' )

# Names of the different derived image decode sections (i.e. /tttt~nnnn|mmmm):
TRANSFORM        = 0
TRANSFORM_MASKED = 1
MASK             = 2

#-------------------------------------------------------------------------------
#  'DerivedImage' class:
#-------------------------------------------------------------------------------

class DerivedImage ( ImageResource ):
    """ An ImageResource derived from another ImageResource object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The image this image is derived from:
    base_image = Image

    #-- Facet Event Handlers ---------------------------------------------------

    def _base_image_set ( self ):
        """ Handles the 'base_image' facet being changed.
        """
        self._loaded  = True
        self.modified = True
        self.name     = self.base_image.name

    #-- Property Implementations -----------------------------------------------

    def _get_width ( self ):
        return self.base_image.width


    def _get_height ( self ):
        return self.base_image.height


    @property_depends_on( 'base_image' )
    def _get_pixels ( self ):
        return copy( self.base_image.pixels )

#-------------------------------------------------------------------------------
#  'HLSAMask' class:
#-------------------------------------------------------------------------------

class HLSAMask ( HasPrivateFacets ):
    """ Defines an image mask based on a set of hue, lightness, saturation and
        alpha range constraints.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The hue range being masked:
    hue = Tuple( ( 0.0, 1.0 ) )

    # The lightness range being masked:
    lightness = Tuple( ( 0.0, 1.0 ) )

    # The saturation range being masked:
    saturation = Tuple( ( 0.0, 1.0 ) )

    # The alpha range being masked:
    alpha = Tuple( ( 0.0, 1.0 ) )

    # Event fired when any transform value changes:
    modified = Event

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'hue',        editor = range_editor ),
        Item( 'lightness',  editor = range_editor ),
        Item( 'saturation', editor = range_editor ),
        Item( 'alpha',      editor = range_editor )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'hue, lightness, saturation, alpha' )
    def _value_modified ( self ):
        self.modified = True

#-------------------------------------------------------------------------------
#  'HLSATransform' class:
#-------------------------------------------------------------------------------

class HLSATransform ( HasPrivateFacets ):
    """ Defines an image transform based on a set of hue, lightness, saturation
        and alpha changes.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The hue transform:
    hue = Range( 0.0, 1.0, 0.0 )

    # The lightness transform:
    lightness = Range( -1.0, 1.0, 0.0 )

    # The saturation transform:
    saturation = Range( -1.0, 1.0, 0.0 )

    # The alpha transform:
    alpha = Range( -1.0, 1.0, 0.0 )

    # Event fired when any transform value changes:
    modified = Event

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'hue',        editor = slider_editor ),
        Item( 'lightness',  editor = slider_editor ),
        Item( 'saturation', editor = slider_editor ),
        Item( 'alpha',      editor = slider_editor )
    )

    #-- Public Methods ---------------------------------------------------------

    def transform ( self, xform ):
        """ Returns a new HLSATransform object representing the result of
            applying another HLSATransform specified by *xform* to this
            transform.
        """
        clamp = self.clamp

        return self.__class__(
            hue        = fmod( self.hue + xform.hue, 1.0 ),
            lightness  = clamp( self.lightness  + xform.lightness  ),
            saturation = clamp( self.saturation + xform.saturation ),
            alpha      = clamp( self.alpha      + xform.alpha      ),
        )


    def clamp ( self, value ):
        """ Returns the specified *value* clamped between to the range -1.0 to
            1.0.
        """
        return clamp( value, -1.0, 1.0 )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'hue, lightness, saturation, alpha' )
    def _value_modified ( self ):
        self.modified = True

#-- Standard HLSA transforms ---------------------------------------------------

HoverTransform    = HLSATransform( hue        =  0.1,
                                   lightness  = -0.1,
                                   saturation =  0.1 )
DownTransform     = HLSATransform( hue        =  0.5 )
DisabledTransform = HLSATransform( saturation = -1.0,
                                   lightness  =  0.3 )
OffTransform      = HLSATransform( saturation = -1.0 )
SelectedTransform = HLSATransform( saturation = -1.0,
                                   lightness  =  0.3 )

#-------------------------------------------------------------------------------
#  'HLSADerivedImage' class:
#-------------------------------------------------------------------------------

class HLSADerivedImage ( DerivedImage ):
    """ Defines a ImageResource whose image is derived by applying an
        HLSATransform with optional HLSAMask to the original image.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The HLSATransform to apply to unmasked portions of the original image:
    transform = Instance( HLSATransform, () )

    # The HLSATransform to apply to the masked portions of the original image:
    transform_masked = Instance( HLSATransform, () )

    # The HLSAMask to apply to the original image when performing the transform:
    mask = Instance( HLSAMask, () )

    # The amount of scaling that should be applied to the image:
    scale_factor = Any # None, float or ( int, 0 )

    # The width of the derived image:
    derived_width = Int

    # The height of the derived image:
    derived_height = Int

    # Encoded form of transform/mask values:
    encoded = Str

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object after the facets constructor has run.
        """
        self._derive_image()

    #-- Object Method Overrides ------------------------------------------------

    def __str__ ( self ):
        """ Returns the string representation of the image.
        """
        return ('%s?%s' % ( self.name, self.encoded ))

    #-- Property Implementations -----------------------------------------------

    def _get_width ( self ):
        return self.derived_width


    def _get_height ( self ):
        return self.derived_height


    @property_depends_on( 'base_image, scale_factor' )
    def _get_pixels ( self ):
        if self.scale_factor is None:
            return copy( self.base_image.pixels )

        return zeros( ( self.derived_height, self.derived_width, 4 ), uint8 )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'base_image, transform.modified, transform_masked.modified, mask.modified, scale_factor' )
    def _modified ( self ):
        """ Handles changes made to the transform or mask.
        """
        if self.facets_inited():
            self._derive_image()


    def _derive_image ( self ):
        """ Computes a new image based on the mask and transform values.
        """
        image = self.base_image
        if image is not None:
            if self.scale_factor is not None:
                image = image.scale( self.scale_factor )

            self.derived_width  = image.width
            self.derived_height = image.height
            t                   = self.transform
            tm                  = self.transform_masked
            m                   = self.mask
            pixels              = hlsa_transform(
                image.pixels.tostring(), image.width, image.height,
                 t.hue,  t.lightness,  t.saturation,  t.alpha,
                tm.hue, tm.lightness, tm.saturation, tm.alpha,
                 m.hue,  m.lightness,  m.saturation,  m.alpha
            )

            if pixels is None:
                self.pixels[:,:,:] = image.pixels
            else:
                self.pixels[:,:,:] = reshape( fromstring( pixels, uint8 ),
                                              ( image.height, image.width, 4 ) )

            self._encode_value()

            self.modified = True


    def _encoded_set ( self, code ):
        """ Handles the 'encoded' facet being changed.
        """
        name = self.name
        col  = name.find( '?' )
        if col >= 0:
            name = name[ : col ]

        self.name = '%s?%s' % ( name, code )

        if self._no_update:
            return

        i       = 0
        n       = len( code )
        kind    = None
        section = TRANSFORM
        while i < n:
            c = code[ i ]
            if kind is None:
                i += 1
                if c == '~':
                    if section != TRANSFORM:
                        return

                    section = TRANSFORM_MASKED
                elif c == '|':
                    if section == MASK:
                        return

                    section = MASK
                elif c in 'hHlLsSaAxX':
                    kind  = c
                    value = nvalue = 0
                else:
                    return
            elif c in '0123456789':
                value   = (10 * value) + ord( c ) - 48
                nvalue += 1
                i      += 1
                if (nvalue > 2) and (kind not in 'xX'):
                    return
            else:
                self._decode_value( kind, value, section )
                kind = None

        if kind is not None:
            self._decode_value( kind, value, section )

        if self.facets_inited():
            self._derive_image()

    #-- Private Methods --------------------------------------------------------

    def _decode_value ( self, kind, value, section ):
        """ Assigns a decoded 'encoded' value to the appropriate facet.
        """
        if kind in 'xX':
            self.facet_setq(
                scale_factor = ( value, 0 ) if kind == 'x' else value / 100.0
            )
        else:
            value = float( value ) / 100.0
            name  = NameMap[ kind.lower() ]
            if section != MASK:
                if value == 0.0:
                    value = 1.0

                if kind in 'lsa':
                    value = -value

                if section == TRANSFORM:
                    self.transform.facet_setq( **{ name: value } )
                else:
                    self.transform_masked.facet_setq( **{ name: value } )
            else:
                low, high = getattr( self.mask, name )
                if kind in 'hlsa':
                    if value == 0.0:
                        value = 1.0

                    low = value
                else:
                    high = value

                self.mask.facet_setq( **{ name: ( low, high ) } )


    def _encode_value ( self ):
        """ Computes a new encoding string for the scaling, mask and transforms
            and sets it as the value of the 'encoded' facet.
        """
        chunks    = []
        separator = '~'
        for item in ( self.transform, self.transform_masked ):
            for name in Names:
                value = getattr( item, name )
                if value != 0.0:
                    n = name[:1]
                    if value > 0.0:
                        n = n.upper()
                    else:
                        value = -value

                    chunks.append( n + (('%.2f' % value)[-2:].lstrip( '0' )) )

            chunks.append( separator )
            separator = ''

        chunks = [ ((''.join( chunks )).rstrip( '~' )) + '|' ]

        for name in Names:
            low, high = getattr( self.mask, name )
            if low != 0.0:
                chunks.append( name[:1] + (('%.2f' % low)[-2:].lstrip( '0' )) )

            if high != 1.0:
                chunks.append( name[:1].upper() +
                               (('%.2f' % high)[-2:].lstrip( '0' )) )

        result = (''.join( chunks )).rstrip( '|' )
        if result[:1] == '|':
            result = ''

        # Encode the scaling information (if any):
        extra = ''
        scale = self.scale_factor
        if scale is not None:
            extra = ('X%d' % int( 100.0 * scale ) if isinstance( scale, float )
                     else 'x%d' % scale[0])

        self._no_update = True
        self.encoded    = (extra + result)
        self._no_update = False

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def hlsa_derived_image ( image, transform = None, transform_masked = None ):
    """ Returns a new HLSADerivedImage object created by applying the
        HLSATransform specified by *transform* to the ImageResource specified by
        *image*. If *transform_masked* is not None, then it is applied as a
        transform to the masked_transform of the *specified* image.

        If *image* is None, None is returned.
    """
    if image is None:
        return None

    if transform is None:
        transform = HLSATransform()

    if transform_masked is None:
        transform_masked = HLSATransform()

    if isinstance( image, HLSADerivedImage ):
        return HLSADerivedImage(
            base_image       = image.base_image,
            mask             = image.mask,
            transform        = transform.transform( image.transform ),
            transform_masked = transform_masked.transform(
                                   image.transform_masked )
        )

    return HLSADerivedImage(
        base_image       = image,
        transform        = transform,
        transform_masked = transform_masked
    )

#-- EOF ------------------------------------------------------------------------