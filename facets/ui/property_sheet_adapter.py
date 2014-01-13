"""
Defines the base PropertySheetAdapter class used to allow interfacing objects
with facets to the PropertySheetEditor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, HasFacets, Instance, Bool, Enum, Any, Str, \
           Callable, Either, Property, Disallow, Event, ATheme, ViewElement

from facets.core.facet_base \
    import user_name_for

from facets.ui.ui_facets \
    import CellImageAlignment

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# The editing mode to use when editing property sheet values:
EditMode = Either( Str, Callable, Instance( ViewElement ), default = 'inline' )

# The change mode to use when editing property sheet values:
ChangeMode = Enum( 'live', 'defer', 'save' )

#-------------------------------------------------------------------------------
#  'PropertySheetAdapter' class:
#-------------------------------------------------------------------------------

class PropertySheetAdapter ( HasPrivateFacets ):
    """ The base class for adapting objects with facets to values that can be
        edited using the PropertySheetEditor.
    """

    # The list of facets names/groups for the current item:
    facets = Property

    # The user interface label to use for the current item:
    label = Property

    # The user interface labels to use for the current list, tuple or dict
    # item's child items (should be None or an indexed collection):
    labels = Any( None )

    # The formatting function to use for the current item:
    formatter = Callable

    # The editing mode to use for the current item:
    mode = EditMode

    # The editing change mode to use for the current item:
    change_mode = ChangeMode

    # The editor to use for editing the current item:
    editor = Property

    # The alias for the current item (an alias is an alternate ( object, name )
    # pair to substitute for the current one:
    alias = Property

    # The name of the default image to use for a value cell:
    image = Str( None )

    # Horizontal image alignment to use for a value cell:
    image_alignment = CellImageAlignment

    # The custom function to use for rendering a value cell:
    paint = Any # Either( Str, Callable )

    # The theme to use for rendering a value cell:
    theme = ATheme

    # The name of the default image to use for a label cell:
    label_image = Str( None )

    # Horizontal image alignment to use for a label cell:
    label_image_alignment = CellImageAlignment

    # The custom function to use for rendering a label cell:
    label_paint = Any # Either( Str, Callable )

    # The theme to use for rendering a label cell:
    label_theme = ATheme

    # The menu to use for a label cell:
    label_menu = Any

    # The tooltip to display for the current item:
    tooltip = Str

    # The initial open/close state for the current (group) item:
    is_open = Bool( True )

    # Does the current HasFacets, list, tuple or dict item have child items that
    # should be displayed in the property sheet (True) or not (False)?
    show_children = Bool( True )

    # If the current HasFacets, list, tuple or dict item has visible child items
    # (because 'show_children' is True), should the child items be children of
    # a new group representing the current item (True), or simply be added to
    # the items for the current group (False)?
    show_group = Bool( True )

    # Event fired to indicate that the list of facets returned by the
    # get_facets API has changed
    updated = Event

    #-- Facets Available to Property/Method Implementers -----------------------

    # The current object:
    object = Instance( HasFacets )

    # The current facet/group name:
    name = Str

    #-- Private Facet Definitions ----------------------------------------------

    # Cache of attribute handlers:
    _hit_cache = Any( {} )

    #-- Adapter Methods --------------------------------------------------------

    def get_facets ( self, object ):
        """ Returns the list of facets/groups for the specified object.
        """
        return self._result_for( 'facets', object )


    def get_label ( self, object, name ):
        """ Returns the user interface label to use for the specified object and
            facet name.
        """
        return self._result_for( 'label', object, name )


    def get_labels ( self, object, name ):
        """ Returns the user interface labels to use for the specified object
            and facet name's child items (in cases where the value is a list,
            tuple or dict).
        """
        return self._result_for( 'labels', object, name )


    def get_formatter ( self, object, name ):
        """ Returns the formatting function to use for the specified object and
            facet name.
        """
        return self._result_for( 'formatter', object, name )


    def get_mode ( self, object, name ):
        """ Returns the editing mode to use for the specified object and
            facet name.
        """
        return self._result_for( 'mode', object, name )


    def get_change_mode ( self, object, name ):
        """ Returns the editing change mode to use for the specified object and
            facet name.
        """
        return self._result_for( 'change_mode', object, name )


    def get_editor ( self, object, name ):
        """ Returns the editor to use for editing the specified object and
            facet name.
        """
        return self._result_for( 'editor', object, name )


    def get_alias ( self, object, name ):
        """ Returns the ( object, name ) alias to use in place of the specified
            object and facet name.
        """
        return self._result_for( 'alias', object, name )


    def get_image ( self, object, name ):
        """ Returns the value cell image name to use for displaying the
            specified object and facet name.
        """
        return self._result_for( 'image', object, name )


    def get_image_alignment ( self, object, name ):
        """ Returns the value cell image alignment to use for displaying the
            specified object and facet name.
        """
        return self._result_for( 'image_alignment', object, name )


    def get_paint ( self, object, name ):
        """ Returns the value cell painter to use for displaying the specified
            object and facet name.
        """
        return self._result_for( 'paint', object, name )


    def get_theme ( self, object, name ):
        """ Returns the value cell theme to use for displaying the specified
            object and facet name.
        """
        return self._result_for( 'theme', object, name )


    def get_label_image ( self, object, name ):
        """ Returns the label cell image name to use for displaying the
            specified object and facet name.
        """
        return self._result_for( 'label_image', object, name )


    def get_label_image_alignment ( self, object, name ):
        """ Returns the label cell image alignment to use for displaying the
            specified object and facet name.
        """
        return self._result_for( 'label_image_alignment', object, name )


    def get_label_paint ( self, object, name ):
        """ Returns the label cell painter to use for displaying the specified
            object and facet name.
        """
        return self._result_for( 'label_paint', object, name )


    def get_label_theme ( self, object, name ):
        """ Returns the label cell theme to use for displaying the specified
            object and facet name.
        """
        return self._result_for( 'label_theme', object, name )


    def get_label_menu ( self, object, name ):
        """ Returns the label cell menu to use for the specified object and
            facet name.
        """
        return self._result_for( 'label_menu', object, name )


    def get_tooltip ( self, object, name ):
        """ Returns the tooltip to display for the specified object and facet
            name.
        """
        return self._result_for( 'tooltip', object, name )


    def get_is_open ( self, object, name ):
        """ Returns the initial open state to use for the specified object and
            group name.
        """
        return self._result_for( 'is_open', object, name )


    def get_show_children ( self, object, name ):
        """ Returns if the HasFacets, list, tuple or dict object returned by
            getattr(object, name) has child items that should be displayed in
            the property sheet (True) or not (False).
        """
        return self._result_for( 'show_children', object, name )


    def get_show_group ( self, object, name ):
        """ Returns if the HasFacets, list, tuple or dict object returned by
            getattr(object, name) that has visible child items should display
            those items as children of a new group representing that object
            (True), or simply be added to the list of items that the object is
            part of (False).
        """
        return self._result_for( 'show_group', object, name )

    #-- Property Implementations -----------------------------------------------

    def _get_facets ( self ):
        return self.object.editable_facets()


    def _get_label ( self ):
        object = self.object
        name   = self.name
        facet  = object.facet( name )
        if facet is None:
            object, name = self.get_alias( object, name )
            facet        = object.facet( name )

        if facet is not None:
            label = facet.label
            if isinstance( label, basestring ):
                return label

        return user_name_for( name )


    def _get_editor ( self ):
        return self.object.base_facet( self.name ).get_editor()


    def _get_alias ( self ):
        return ( self.object, self.name )

    #-- Facets Default Values --------------------------------------------------

    def _formatter_default ( self ):
        return self._format_value

    #-- 'object' Method Overrides ----------------------------------------------

    def __call__ ( self ):
        """ Allows an adapter to be its own 'factory'.
        """
        return self

    #-- Private Methods --------------------------------------------------------

    def _format_value ( self, value ):
        """ Returns a formatted version of the specified value using the
            'string_value' method associated with the items' object facet.
        """
        return self.object.base_facet( self.name ).string_value(
                                                 self.object, self.name, value )


    def _result_for ( self, attribute, object, name = '' ):
        """ Returns the value of the specified *attribute* for the specified
            *object*  and facet/group *name* item.
        """
        self.object  = object
        self.name    = name
        object_class = object.__class__
        key            = '%s:%s:%s' % ( object_class.__name__, attribute, name )
        handler        = self._hit_cache.get( key )
        if handler is not None:
            return handler()

        for klass in object_class.__mro__:
            handler = self._get_handler_for(
                          '%s_%s_%s' % ( klass.__name__, name, attribute ) )
            if (handler is not None) or (klass is HasFacets):
                break

        if (handler is None) and (len(name) > 0):
            handler = self._get_handler_for( '%s_%s' % ( name, attribute ) )

        if handler is None:
            for klass in object_class.__mro__:
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