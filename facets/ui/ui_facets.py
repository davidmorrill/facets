"""
Defines common facets and classes used within the facets.ui package.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core.has_facets \
    import HasStrictFacets

from facets.core.facet_defs \
    import Facet

from facets.core.facet_types \
    import Delegate, Str, Instance, Float, List, Enum, Any, Range, Expression

from facets.core.facet_handlers \
    import FacetType, FacetPrefixList

from facets.core.facet_errors \
    import FacetError

from facets.core.facet_base \
    import get_resource_path

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# The type of data being dragged in a drag and drop operation:
DragType = Enum( None, 'color', 'image', 'text', 'html', 'files', 'urls',
                 'object' )

# Orientation facet:
Orientation = Facet( 'vertical',
                     FacetPrefixList( 'vertical', 'horizontal' ) )

# Horizontal alignment facet:
HorizontalAlignment = Enum( 'default', 'left', 'center', 'right' )

# Vertical alignment facet:
VerticalAlignment = Enum( 'default', 'top', 'center', 'bottom' )

# General 2D alignment facet:
Alignment = Enum( 'default', 'top left', 'top right', 'bottom left',
                  'bottom right', 'center', 'left', 'right', 'top', 'bottom' )

# Horizontal image alignment to use for a cell:
CellImageAlignment = Enum( 'default', 'text left', 'text right', 'cell left',
                           'cell right', 'cell center' )

# The position of one object relative to an associated object:
Position = Enum( 'left', 'right', 'above', 'below' )

# The spacing between two items:
Spacing = Range( -32, 32, 3 )

# Styles for user interface elements:
EditorStyle = Facet( 'simple',
                     FacetPrefixList( 'simple', 'custom', 'text', 'readonly' ),
                     cols = 4 )

# Group layout facet:
Layout = Facet( 'normal',
                FacetPrefixList( 'normal', 'split', 'tabbed', 'flow', 'fold',
                                 'toolbar' ) )

# Facet for the default object being edited:
AnObject = Expression( 'object' )

# The default dock style to use:
DockStyle = dock_style_facet = Enum( 'fixed', 'horizontal', 'vertical', 'tab',
                                     desc = 'the default docking style to use' )

# The category of elements dragged out of the view:
ExportType = Str( desc = 'the category of elements dragged out of the view' )

# Delegate a facet value to the object's **container** facet:
ContainerDelegate = container_delegate = Delegate( 'container',
                                                   listenable = False )

# An identifier for the external help context:
HelpId = help_id_facet = Str( desc = 'the external help context identifier' )

# A button to add to a view:
AButton = Facet( '', Str, Instance( 'facets.ui.menu.Action' ) )

# The set of buttons to add to the view:
Buttons = List( AButton,
                desc = 'the action buttons to add to the bottom of the view' )

# View facet specified by name or instance:
AView = Any
#AView = Facet( '', Str, Instance( 'facets.ui.View' ) )

# User interface 'kind' facet. The values have the following meanings:
#
# * 'panel': An embeddable panel. This type of window is intended to be used as
#   part of a larger interface.
# * 'subpanel': An embeddable panel that does not display command buttons,
#   even if the View specifies them.
# * 'modal': A modal dialog box that operates on a clone of the object until
#   the user commits the change.
# * 'nonmodal':  A nonmodal dialog box that operates on a clone of the object
#   until the user commits the change
# * 'live': A nonmodal dialog box that immediately updates the object.
# * 'livemodal': A modal dialog box that immediately updates the object.
# * 'popup': A temporary, frameless popup dialog that immediately updates the
#   object and is active only while the mouse pointer is in the dialog.
# * 'popout': A temporary, frameless popup dialog that immediately updates the
#   object and is active only until the mouse is clicked outside of the dialog.
# * 'popover': A temporary, frameless popup dialog that appears over the
#    invoking control, immediately updates the object and is active only while
#    the mouse pointer is in the dialog
# * 'info': A temporary, frameless popup dialog that immediately updates the
#   object and is active only while the dialog is still over the invoking
#   control.
# * 'editor': A view whose contents together form a single editor for some
#   object facet.
# * 'wizard': A wizard modal dialog box. A wizard contains a sequence of
#   pages, which can be accessed by clicking **Next** and **Back** buttons.
#   Changes to attribute values are applied only when the user clicks the
#   **Finish** button on the last page.
AKind = Enum( 'live', 'panel', 'subpanel', 'modal', 'nonmodal', 'livemodal',
              'popup', 'popout', 'popover', 'info', 'editor', 'wizard',
              desc = 'the kind of view window to create',
              cols = 4 )

#-------------------------------------------------------------------------------
#  'StatusItem' class:
#-------------------------------------------------------------------------------

class StatusItem ( HasStrictFacets ):
    """ Defines a StatusItem, which represents a single field that can appear
        in a View's status bar.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the facet the status information will be synched with:
    name = Str( 'status' )

    # The width of the status field. The possible values are:
    # - abs( width )  > 1.0: Width of the field in pixels = abs( width )
    # - abs( width ) <= 1.0: Relative width of the field when compared to other
    #                        relative width fields.
    width = Float( 0.5 )

#-------------------------------------------------------------------------------
#  'ViewStatus' facet:
#-------------------------------------------------------------------------------

class ViewStatus ( FacetType ):
    """ Defines a facet whose value must be a single StatusItem instance or a
        list of StatusItem instances.
    """

    #-- Class Constants --------------------------------------------------------

    # Define the default value for the facet:
    default_value = None

    # A description of the type of value this facet accepts:
    info_text = ('None, a string, a single StatusItem instance, or a list or '
                 'tuple of strings and/or StatusItem instances')

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        if isinstance( value, basestring ):
            return [ StatusItem( name = value ) ]

        if isinstance( value, StatusItem ):
            return [ value ]

        if value is None:
            return value

        result = []
        if isinstance( value, SequenceTypes ):
            for item in value:
                if isinstance( item, basestring ):
                    result.append( StatusItem( name = item ) )
                elif isinstance( item, StatusItem ):
                    result.append( item )
                else:
                    break
            else:
                return result

        self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'Image' facet:
#-------------------------------------------------------------------------------

image_resource_cache = {}

def image_for ( value, level = 3, cache = True ):
    """ Converts a specified value to an ImageResource if possible.
    """
    global image_resource_cache

    from facets.ui.pyface.image_resource import ImageResource

    if not isinstance( value, basestring ):
        if isinstance( value, tuple ) and (len( value ) == 2):
            return ImageResource( width = value[0], height = value[1] )

        return value

    key             = value
    is_facets_image = (value[:1] == '@')
    if not is_facets_image:
        search_path = get_resource_path( level )
        key         = '%s[%s]' % ( value, search_path )

    result = image_resource_cache.get( key ) if cache else None
    if result is None:
        col = value.rfind( '?' )
        if col >= 0:
            encoded = value[ col + 1: ]
            value   = value[ : col ]
            result  = image_resource_cache.get( value ) if cache else None

        if result is None:
            if is_facets_image:
                try:
                    from facets.ui.image import ImageLibrary

                    result = ImageLibrary().image_resource( value )
                except:
                    import traceback
                    traceback.print_exc()
                    result = None
            else:
                result = ImageResource( value, search_path = [ search_path ] )

        if result is not None:
            result.name = value
            if col >= 0:
                from facets.extra.helper.image import HLSADerivedImage

                if cache:
                    image_resource_cache[ value ] = result

                result = HLSADerivedImage( base_image = result,
                                           encoded    = encoded )

        if cache:
            image_resource_cache[ key ] = result

    return result


class Image ( FacetType ):
    """ Defines a facet whose value must be a PyFace ImageResource or a string
        that can be converted to one.
    """

    #-- Class Constants --------------------------------------------------------

    # Define the default value for the facet:
    default_value = None

    # A description of the type of value this facet accepts:
    info_text = 'an ImageResource or string that can be used to define one'

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = None, cache = True, **metadata ):
        """ Creates an Image facet.

        Parameters
        ----------
        value : string or ImageResource
            The default value for the Image, either an ImageResource object,
            or a string from which an ImageResource object can be derived.
        """
        super( Image, self ).__init__( image_for( value, cache = cache ),
                                       **metadata )

        self._cache = cache


    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        from facets.ui.pyface.i_image_resource import AnImageResource

        if value is None:
            return None

        new_value = image_for( value, 4, self._cache )
        if isinstance( new_value, AnImageResource ):
            return new_value

        self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor to use for a facet.
        """
        from facets.api import ImageZoomEditor

        return ImageZoomEditor( channel = 'hue' )

#-------------------------------------------------------------------------------
#  'ATheme' facet:
#-------------------------------------------------------------------------------

def convert_theme ( value, level = 3, cache = True ):
    """ Converts a specified value to a Theme if possible.
    """
    if not isinstance( value, basestring ):
        return value

    from theme import Theme

    kind = value[:1]
    if kind in '?~#$':
        from facets.core.facet_db import facet_db

        theme = facet_db.get( value, db = 'themes' )
        if isinstance( theme, Theme ):
            return theme

    if (kind == '@') and (value.find( ':' ) >= 2):
        try:
            from facets.ui.image import ImageLibrary

            info = ImageLibrary().image_info( value )
            if info is not None:
                return info.theme
        except:
            info = None

    return Theme( image = image_for( value, level + 1, cache ) )


class ATheme ( FacetType ):
    """ Defines a facet whose value must be a facets UI Theme or a string that
        can be converted to one.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Define the default value for the facet:
    default_value = None

    # A description of the type of value this facet accepts:
    info_text = 'a Theme or string that can be used to define one'

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = None, cache = True, **metadata ):
        """ Creates an ATheme facet.

        Parameters
        ----------
        value : string or Theme
            The default value for the ATheme, either a Theme object, or a
            string from which a Theme object can be derived.
        """
        super( ATheme, self ).__init__( convert_theme( value, cache = cache ),
                                        **metadata )

        self._cache = cache


    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        from theme import Theme

        if value is None:
            return None

        new_value = convert_theme( value, 4, self._cache )
        if isinstance( new_value, Theme ):
            return new_value

        self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'BaseMB' class:
#-------------------------------------------------------------------------------

class BaseMB ( HasStrictFacets ):
    """ Defines a BaseMB, which is an abstract base class used for defining
        the Margin and Border classes used with Theme objects.
    """

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        from facets.ui.api import View, Item, RangeEditor

        slider_editor = RangeEditor( body_style = 25 )

        return View(
            Item( 'left',   editor = slider_editor ),
            Item( 'right',  editor = slider_editor ),
            Item( 'top',    editor = slider_editor ),
            Item( 'bottom', editor = slider_editor )
        )

    #-- object Method Overrides ------------------------------------------------

    def __init__ ( self, *args, **facets ):
        """ Initializes the object.
        """
        n = len( args )
        if n > 0:
            if n == 1:
                left = right = top = bottom = args[0]
            elif n == 2:
                left = right  = args[0]
                top  = bottom = args[1]
            elif n == 4:
                left, right, top, bottom = args
            else:
                raise FacetError(
                    '0, 1, 2 or 4 arguments expected, but %d specified' % n
                )

            self.set( left = left, right = right, top = top, bottom = bottom )

        super( BaseMB, self ).__init__( **facets )


    def __repr__ ( self ):
        """ Returns the string representation of the object.
        """
        return ('%s@%x( left = %d, right = %d, top = %d, bottom = %d )' % (
                self.__class__.__name__, id( self ), self.left, self.right,
                self.top, self.bottom ))


    def __str__ ( self ):
        """ Returns the string representation of the object.
        """
        left, right, top, bottom = self.left, self.right, self.top, self.bottom
        if (left == right) and (top == bottom):
            if left == top:
                return str( left )

            return str( ( left, top ) )

        return str( ( left, right, top, bottom ) )

#-------------------------------------------------------------------------------
#  'Margin' class:
#-------------------------------------------------------------------------------

class Margin ( BaseMB ):
    """ Defines a Margin, which represents a margin or padding area for use
        with a Theme.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The amount of padding/margin at the top:
    top = Range( -64, 64, 0 )

    # The amount of padding/margin at the bottom:
    bottom = Range( -64, 64, 0 )

    # The amount of padding/margin on the left:
    left = Range( -64, 64, 0 )

    # The amount of padding/margin on the right:
    right = Range( -64, 64, 0 )

#-------------------------------------------------------------------------------
#  'Border' class:
#-------------------------------------------------------------------------------

class Border ( BaseMB ):
    """ Defines a Border, which represents the border region around a Themed
        control used when resizing the control using a mouse.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The amount of border at the top:
    top = Range( 0, 64, 0 )

    # The amount of border at the bottom:
    bottom = Range( 0, 64, 0 )

    # The amount of border on the left:
    left = Range( 0, 64, 0 )

    # The amount of border on the right:
    right = Range( 0, 64, 0 )

#-------------------------------------------------------------------------------
#  'HasMargin' facet:
#-------------------------------------------------------------------------------

class HasMargin ( FacetType ):
    """ Defines a facet whose value must be a Margin object or an integer or
        tuple value that can be converted to one.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The desired value class:
    klass = Margin

    # Define the default value for the facet:
    default_value = Margin( 0 )

    # A description of the type of value this facet accepts:
    info_text = ('a Margin instance, or an integer in the range from -32 to 32 '
                 'or a tuple with 1, 2 or 4 integers in that range that can be '
                 'used to define one')

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        if isinstance( value, int ):
            try:
                value = self.klass( value )
            except:
                self.error( object, name, value )
        elif isinstance( value, tuple ):
            try:
                value = self.klass( *value )
            except:
                self.error( object, name, value )

        if isinstance( value, self.klass ):
            return value

        self.error( object, name, value )


    def get_default_value ( self ):
        """ Returns a tuple of the form: ( default_value_type, default_value )
            which describes the default value for this facet.
        """
        dv  = self.default_value
        dvt = self.default_value_type
        if dvt < 0:
            if isinstance( dv, int ):
                dv = self.klass( dv )
            elif isinstance( dv, tuple ):
                dv = self.klass( *dv )

            if not isinstance( dv, self.klass ):
                return super( HasMargin, self ).get_default_value()

            self.default_value_type = dvt = 7
            dv = ( self.klass, (), dv.get() )

        return ( dvt, dv )

#-------------------------------------------------------------------------------
#  'HasBorder' facet:
#-------------------------------------------------------------------------------

class HasBorder ( HasMargin ):
    """ Defines a facet whose value must be a Border object or an integer
        or tuple value that can be converted to one.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The desired value class:
    klass = Border

    # Define the default value for the facet:
    default_value = Border( 0 )

    # A description of the type of value this facet accepts:
    info_text = ('a Border instance, or an integer in the range from 0 to 32 '
                 'or a tuple with 1, 2 or 4 integers in that range that can be '
                 'used to define one')

#-------------------------------------------------------------------------------
#  Other definitions:
#-------------------------------------------------------------------------------

# Types that represent sequences:
SequenceTypes = ( tuple, list )

#-- EOF ------------------------------------------------------------------------