"""
Defines a FilmStripAdapter class for adapting objects to work with the
FilmStripEditor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import basename

from facets.api \
    import HasFacets, HasPrivateFacets, Property, Str, Bool, Tuple, ATheme, \
           Theme, Any, Enum, Image, Disallow

from facets.core.facet_base \
    import SequenceTypes

from facets.ui.menu \
    import Menu, Action

from facets.ui.ui_facets \
    import DragType

from facets.extra.helper.image \
    import hlsa_derived_image, HLSATransform

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# The image display mode:
ImageMode = Enum( 'fit', 'actual', 'zoom', 'popup' )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard HLSA transforms:
SelectedTransform      = HLSATransform( hue        = 0.62,
                                        lightness  = 0.18,
                                        saturation = 0.35 )
HoverTransform         = HLSATransform( lightness  = 0.09 )
HoverSelectedTransform = HLSATransform( hue        = 0.62,
                                        lightness  = 0.27,
                                        saturation = 0.35 )
DownTransform          = HLSATransform( lightness  = 0.18 )
DownSelectedTransform  = HLSATransform( hue        = 0.62,
                                        lightness  = 0.36,
                                        saturation = 0.35 )

#-------------------------------------------------------------------------------
#  'FilmStripAdapter' class:
#-------------------------------------------------------------------------------

class FilmStripAdapter ( HasPrivateFacets ):
    """ Adapter class for converting items into objects that can be displayed in
        a filmstrip editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The FilmStripItem object associated with the current value:
    item = Property

    # The Imageresource object associated with the current value:
    image = Property

    # The image display mode for the current value:
    mode = ImageMode

    # The name of the current value (as it should appear in the UI):
    name = Str

    # Is the current value resizable?
    is_resizable = Bool( False )

    # Does the item have a label to be displayed?
    has_label = Bool( True )

    # The label associated with the current value:
    label = Property

    # The tooltip associated with the current value:
    tooltip = Property

    # The content menu to display when the current value is right-clicked:
    menu = Any # Menu, Action or List( Action )

    # The value to be dragged for the current value:
    drag_value = Property

    # The type of value being dragged for the current value:
    drag_type = DragType

    # The size of the popup view for the current value:
    popup_size = Tuple( ( 400, 400 ) )

    # The popup theme for the current value:
    popup_theme = ATheme( Theme( '@xform:b', content = 6 ) )

    # The basic theme for the current value:
    theme = ATheme( Theme( '@xform:bbd?l20', content = 6 ) )

    # The 'selected' state theme for the current value:
    selected_theme = ATheme

    # The 'hover' state theme for the current value:
    hover_theme = ATheme

    # The 'hover' and 'selected' state theme for the current value:
    hover_selected_theme = ATheme

    # The 'down' state theme for the current value:
    down_theme = ATheme

    # The 'down' and 'selected' state theme for the current value:
    down_selected_theme = ATheme

    #-- Facets Available to Property/Method Implementers -----------------------

    # The current value:
    value = Any

    #-- Private Facets ---------------------------------------------------------

    # The editor this adapter is associated with:
    editor = Any

    # Used to convert values into an ImageResource object:
    _image = Image

    # Cache of attribute handlers:
    _hit_cache = Any( {} )

    #-- Property Implementations -----------------------------------------------

    def _get_item ( self ):
        from facets.ui.editors.filmstrip_editor import FilmStripItem

        value = self.value
        item  = FilmStripItem( editor = self.editor ).set(
            image                = self.get_image( value ),
            mode                 = self.get_mode( value ),
            label                = self.get_label( value ),
            menu                 = self.get_menu( value ),
            tooltip              = self.get_tooltip( value ),
            drag_value           = self.get_drag_value( value ),
            drag_type            = self.get_drag_type( value ),
            popup_size           = self.get_popup_size( value ),
            popup_theme          = self.get_popup_theme( value ),
            normal_theme         = self.get_theme( value ),
            selected_theme       = self.get_selected_theme( value ),
            hover_theme          = self.get_hover_theme( value ),
            hover_selected_theme = self.get_hover_selected_theme( value ),
            down_theme           = self.get_down_theme( value ),
            down_selected_theme  = self.get_down_selected_theme( value )
        ).facet_setq(
            ratio                = self.editor.ratio
        )
        if self.get_is_resizable( value ):
            item.add_tool( self.editor.resizer )

        return item


    def _get_image ( self ):
        self._image = self.value

        return self._image


    def _get_label ( self ):
        image = self.get_image( self.value )
        name  = self.get_name(  self.value )
        if name == '':
            return '(%dx%d)' % ( image.width, image.height )

        return '%s (%dx%d)' % ( name, image.width, image.height )


    def _get_tooltip ( self ):
        return ''


    def _get_drag_value ( self ):
        return self.value

    #-- Adapter Methods --------------------------------------------------------

    def get_item ( self, value ):
        """ Returns the FilmStripItem object for the specified value.
        """
        return self._result_for( 'item', value )


    def get_image ( self, value ):
        """ Returns the ImageResource object for the specified value.
        """
        return self._result_for( 'image', value )


    def get_mode ( self, value ):
        """ Returns the image display mode for the specified value.
        """
        return self._result_for( 'mode', value )


    def get_name ( self, value ):
        """ Returns the UI name for the specified value.
        """
        result = self._result_for( 'name', value )
        if (result == '') and isinstance( value, basestring ):
            result = basename( value )

        return result


    def get_is_resizable ( self, value ):
        """ Returns whether or not the specified value can be resized
        """
        return self._result_for( 'is_resizable', value )


    def get_has_label ( self, value ):
        """ Returns whether or not the specified value has a label.
        """
        return self._result_for( 'has_label', value )


    def get_label ( self, value ):
        """ Returns the label for the specified value.
        """
        if self.get_has_label( value ):
            return self._result_for( 'label', value )

        return ''


    def get_tooltip ( self, value ):
        """ Returns the tooltip for the specified value.
        """
        result = self._result_for( 'tooltip', value )
        if (result == '') and (not self.get_theme( value ).has_label):
            result = self.get_label( value )

        return result


    def get_menu ( self, value ):
        """ Returns the right-click context menu for the specified value.
        """
        result = self._result_for( 'menu', value )
        if isinstance( result, Action ):
            return Menu( Action )

        if isinstance( result, SequenceTypes ):
            return Menu( *result )

        return result


    def get_drag_value ( self, value ):
        """ Returns the value to be dragged for the specified value.
        """
        return self._result_for( 'drag_value', value )


    def get_drag_type ( self, value ):
        """ Returns the type of value to be dragged for the specified value.
        """
        return self._result_for( 'drag_type', value )


    def get_popup_size ( self, value ):
        """ Returns the popup size for the specified value.
        """
        return self._result_for( 'popup_size', value )


    def get_popup_theme ( self, value ):
        """ Returns the popup theme for the specified value.
        """
        return self._result_for( 'popup_theme', value )


    def get_theme ( self, value ):
        """ Returns the base theme for the specified value.
        """
        return self._result_for( 'theme', value )


    def get_selected_theme ( self, value ):
        """ Returns the 'selected' state theme for the specified value.
        """
        return self._get_theme_for( value, 'selected_theme', SelectedTransform )


    def get_hover_theme ( self, value ):
        """ Returns the 'hover' state theme for the specified value.
        """
        return self._get_theme_for( value, 'hover_theme', HoverTransform )


    def get_hover_selected_theme ( self, value ):
        """ Returns the 'hover' and 'selected' state theme for the specified
            value.
        """
        return self._get_theme_for( value, 'hover_selected_theme',
                                    HoverSelectedTransform )


    def get_down_theme ( self, value ):
        """ Returns the 'down' state theme for the specified value.
        """
        return self._get_theme_for( value, 'down_theme', DownTransform )


    def get_down_selected_theme ( self, value ):
        """ Returns the 'down' and 'selected' state theme for the specified
            value.
        """
        return self._get_theme_for( value, 'down_selected_theme',
                                    DownSelectedTransform )

    #-- Private Methods --------------------------------------------------------

    def _get_theme_for ( self, value, name, transform ):
        """ Gets the theme with the specified name (using the specified default
            transform if necessary).
        """
        theme = self._result_for( name, value )
        if theme is None:
            return self._theme_transform( self.get_theme( value ), transform )

        return theme


    def _theme_transform ( self, theme, hlsa_transform ):
        """ Returns a version of the base *theme* with the HLSA transform
            specified by *hlsa_transform* applied.
        """
        return Theme(
            image     = hlsa_derived_image( theme.image, hlsa_transform ),
            border    = theme.border,
            content   = theme.content,
            label     = theme.label,
            alignment = theme.alignment
        )


    def _result_for ( self, attribute, value ):
        """ Returns the value of the specified *attribute* for the specified
            *value*.
        """
        self.value  = value
        value_class = value.__class__
        key         = '%s:%s' % ( value_class.__name__, attribute )
        handler     = self._hit_cache.get( key )
        if handler is not None:
            return handler()

        if isinstance( value, HasFacets ):
            for klass in value_class.__mro__:
                handler = self._get_handler_for(
                              '%s_%s' % ( klass.__name__, attribute ) )
                if (handler is not None) or (klass is HasFacets):
                    break

        if handler is None:
            handler = self._get_handler_for( attribute )

        self._hit_cache[ key ] = handler

        return handler()


    def _get_handler_for ( self, name ):
        """ Returns the handler for a specified facet name (or None if not
            found).
        """
        facet = self.facet( name )
        if (facet is not None) and (facet.handler is not Disallow):
            return lambda: getattr( self, name )

        return getattr( self, name, None )

#-- EOF ------------------------------------------------------------------------
