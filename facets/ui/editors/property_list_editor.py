"""
Defines a PropertyListEditor class, which is an editor which works like a
property sheet and whose input is a sequence of tuples of the form:

    ( HasFacets_object, name [, label] [, editor] [, mode] )

where:
    HasFacets_object: A HasFacets instance.
    name:             The name of the 'HasFacet_object' facet to edit.
    label:            The UI label to display (defaults to using 'name').
    editor:           The Editor used to edit the facet (defaults to the
                      default editor for 'HasFacets_object.name').
    mode:             The editing mode to use (defaults to 'inline'). Refer to
                      the PropertySheetAdapter for more information.

As an alternative to using the simple tuple form described above, instances of
PropertyListItem can also be used:

    PropertyListItem(
        object                = Instance( HasFacets ),
        name                  = Str,
        label                 = Str,
        editor                = Instance( EditorFactory ),
        mode                  = EditMode,
        formatter             = Callable,
        image                 = Str,
        image_alignment       = CellImageAlignment,
        paint                 = Either( Str, Callable ),
        theme                 = ATheme,
        label_image           = Str,
        label_image_alignment = CellImageAlignment,
        label_paint           = Either( Str, Callable ),
        label_theme           = ATheme,
        label_menu            = Any,
        tooltip               = Str,
        is_open               = Bool,
        show_children         = Bool,
        show_group            = Bool
    )

    Using an explicit PropertyListItem provides greater flexibility than using
    a simple tuple, but can be somewhat more verbose. Note that internal to the
    PropertyListEditor, all items are represented using PropertyListItem
    instances.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Instance, Str, List, Any, ATheme, Bool, Callable, \
           EditorFactory

from facets.core.facet_base \
    import user_name_for

from facets.ui.editors.property_sheet_editor \
    import PropertySheetEditor, _PropertySheetEditor

from facets.ui.property_sheet_adapter \
    import PropertySheetAdapter, EditMode

from facets.ui.ui_facets \
    import CellImageAlignment

#-------------------------------------------------------------------------------
#  'PropertyListItem' class:
#-------------------------------------------------------------------------------

class PropertyListItem ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The HasFacets object being edited:
    object = Instance( HasFacets )

    # The name of the object facet being edited:
    name = Str

    # The UI label to use:
    label = Str

    # The Editor to use:
    editor = Instance( EditorFactory )

    # The editing mode to use:
    mode = EditMode

    # The formatting function to use:
    formatter = Callable

    # The name of the default image to use:
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

    #-- Facet Default Values ---------------------------------------------------

    def _label_default ( self ):
        return user_name_for( self.name )


    def _editor_default ( self ):
        return self.object.base_facet( self.name ).get_editor()


    def _formatter_default ( self ):
        return self._format_value

    #-- Private Methods --------------------------------------------------------

    def _format_value ( self, value ):
        """ Returns a formatted version of the specified value using the
            'string_value' method associated with the items' object facet.
        """
        return self.object.base_facet( self.name ).string_value(
                                                 self.object, self.name, value )

#-------------------------------------------------------------------------------
#  'PropertyListAdapter' class:
#-------------------------------------------------------------------------------

class PropertyListAdapter ( PropertySheetAdapter ):

    #-- Facet Definitions ------------------------------------------------------

    # The list of PropertyListItem instances used to describe the facets being
    # edited:
    items = List

    # Mapping from ( object, name ) tuples to PropertyListItem's:
    item_map = Any( {} )


    #-- Property Implementations -----------------------------------------------

    def _get_facets ( self ):
        return [ str( i ) for i in xrange( len( self.items ) ) ]


    def get_label ( self, object, name ):
        """ Returns the user interface label to use for the specified object and
            facet name.
        """
        return self.items[ int( name ) ].label


    def get_alias ( self, object, name ):
        """ Returns the ( object, name ) alias to use in place of the specified
            object and facet name.
        """
        item                    = self.items[ int( name ) ]
        result                  = ( item.object, item.name )
        self.item_map[ result ] = item

        return result


    def get_editor ( self, *args ):
        """ Returns the editor to use for editing the specified object and
            facet name.
        """
        return self.item_map[ args ].editor


    def get_mode ( self, *args ):
        """ Returns the editing mode to use for the specified object and
            facet name.
        """
        return self.item_map[ args ].mode


    def get_formatter ( self, *args ):
        """ Returns the formatting function to use for the specified object and
            facet name.
        """
        return self.item_map[ args ].formatter


    def get_image ( self, *args ):
        """ Returns the value cell image name to use for displaying the
            specified object and facet name.
        """
        return self.item_map[ args ].image


    def get_image_alignment ( self, *args ):
        """ Returns the value cell image alignment to use for displaying the
            specified object and facet name.
        """
        return self.item_map[ args ].image_alignment


    def get_paint ( self, *args ):
        """ Returns the value cell painter to use for displaying the specified
            object and facet name.
        """
        return self.item_map[ args ].paint


    def get_theme ( self, *args ):
        """ Returns the value cell theme to use for displaying the specified
            object and facet name.
        """
        return self.item_map[ args ].theme


    def get_label_image ( self, *args ):
        """ Returns the label cell image name to use for displaying the
            specified object and facet name.
        """
        return self.item_map[ args ].label_image


    def get_label_image_alignment ( self, *args ):
        """ Returns the label cell image alignment to use for displaying the
            specified object and facet name.
        """
        return self.item_map[ args ].label_image_alignment


    def get_label_paint ( self, *args ):
        """ Returns the label cell painter to use for displaying the specified
            object and facet name.
        """
        return self.item_map[ args ].label_paint


    def get_label_theme ( self, *args ):
        """ Returns the label cell theme to use for displaying the specified
            object and facet name.
        """
        return self.item_map[ args ].label_theme


    def get_label_menu ( self, *args ):
        """ Returns the label cell menu to use for the specified object and
            facet name.
        """
        return self.item_map[ args ].label_menu


    def get_tooltip ( self, *args ):
        """ Returns the tooltip to display for the specified object and facet
            name.
        """
        return self.item_map[ args ].tooltip


    def get_is_open ( self, *args ):
        """ Returns the initial open state to use for the specified object and
            group name.
        """
        return self.item_map[ args ].is_open


    def get_show_children ( self, *args ):
        """ Returns if the HasFacets, list, tuple or dict object returned by
            getattr(object, name) has child items that should be displayed in
            the property sheet (True) or not (False).
        """
        return self.item_map[ args ].show_children


    def get_show_group ( self, *args ):
        """ Returns if the HasFacets, list, tuple or dict object returned by
            getattr(object, name) that has visible child items should display
            those items as children of a new group representing that object
            (True), or simply be added to the list of items that the object is
            part of (False).
        """
        return self.item_map[ args ].show_group

#-------------------------------------------------------------------------------
#  '_PropertyListEditor' class:
#-------------------------------------------------------------------------------

# A dummy object used as the editor 'target':
dummy = HasFacets()

class _PropertyListEditor ( _PropertySheetEditor ):

    #-- '_PropertySheetEditor' Method Overrides --------------------------------

    def init_data ( self ):
        """ Initializes internal editor data.
        """
        item_for                    = self._property_list_item_for
        self.property_sheet_adapter = PropertyListAdapter(
            items = [ item_for( item ) for item in self.value ]
        )
        self.target = dummy


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """

    #-- Private Methods --------------------------------------------------------

    def _property_list_item_for ( self, item ):
        """ Returns the PropertyListItem corresponding to the specified *item*.
        """
        if isinstance( item, PropertyListItem ):
            return item

        result = PropertyListItem( object = item[0], name = item[1] )

        for i in xrange( 2, len( item ) ):
            value = item[ i ]
            if isinstance( value, basestring ):
                result.label = value
            elif isinstance( value, EditorFactory ):
                result.editor = value
            else:
                result.mode = value

        return result

#-------------------------------------------------------------------------------
#  'PropertyListEditor' class:
#-------------------------------------------------------------------------------

class PropertyListEditor ( PropertySheetEditor ):

    # The class used to construct editor objects:
    klass = _PropertyListEditor

#-- EOF ------------------------------------------------------------------------