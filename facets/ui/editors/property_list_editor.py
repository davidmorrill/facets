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
        object = HasFacets_object,
        facet  = facet,
        label  = label,
        editor = editor,
        mode   = mode
    )
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Instance, Str, List, Any, EditorFactory

from facets.core.facet_base \
    import user_name_for

from facets.ui.editors.property_sheet_editor \
    import PropertySheetEditor, _PropertySheetEditor

from facets.ui.property_sheet_adapter \
    import PropertySheetAdapter, EditMode

#-------------------------------------------------------------------------------
#  'PropertyListItem' class:
#-------------------------------------------------------------------------------

class PropertyListItem ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The HasFacets object being edited:
    object = Instance( HasFacets )

    # The name of the object facet being edited:
    name = Str

    # The UI label for the facet being edited:
    label = Str

    # The Editor used to edit the facet:
    editor = Instance( EditorFactory )

    # The editing mode used to edit the facet:
    mode = EditMode

    #-- Facet Default Values ---------------------------------------------------

    def _label_default ( self ):
        return user_name_for( self.name )


    def _editor_default ( self ):
        return self.object.base_facet( self.name ).get_editor()

#-------------------------------------------------------------------------------
#  'PropertyListAdapter' class:
#-------------------------------------------------------------------------------

class PropertyListAdapter ( PropertySheetAdapter ):

    #-- Facet Definitions ------------------------------------------------------

    # The list of PropertyListItem instances used to describe the facets being
    # edited:
    items = List

    # The current PropertyListItem being processed:
    current_item = Instance( PropertyListItem )

    #-- Property Implementations -----------------------------------------------

    def _get_facets ( self ):
        return [ str( i ) for i in xrange( len( self.items ) ) ]


    def get_alias ( self, object, name ):
        """ Returns the ( object, name ) alias to use in place of the specified
            object and facet name.
        """
        self.current_item = item = self.items[ int( name ) ]

        return ( item.object, item.name )


    def get_label ( self, object, name ):
        """ Returns the user interface label to use for the specified object and
            facet name.
        """
        return self.items[ int( name ) ].label


    def get_editor ( self, object, name ):
        """ Returns the editor to use for editing the specified object and
            facet name.
        """
        return self.current_item.editor


    def get_mode ( self, object, name ):
        """ Returns the editing mode to use for the specified object and
            facet name.
        """
        return self.current_item.mode

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