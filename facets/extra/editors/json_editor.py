"""
Defines the JSONEditor class for viewing the contents of a Python JSON object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from json \
    import loads

from facets.api \
    import HasPrivateFacets, Any, Str, Bool, List, Float, Property, Constant, \
           View, UItem, UIEditor, BasicEditorFactory, GridEditor,             \
           property_depends_on

from facets.ui.hierarchical_grid_adapter \
    import HierarchicalGridAdapter

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def item_for ( name, data ):
    """ Returns the JSONxxx item corresponding to the specified *name* and
        *value*.
    """
    if isinstance( data, dict ):
        return JSONDict( name = name, data = data )

    if isinstance( data, list ):
        return JSONList( name = name, data = data )

    return JSONValue( name = name, data = data )

#-------------------------------------------------------------------------------
#  'JSONAdapter' class:
#-------------------------------------------------------------------------------

class JSONAdapter ( HierarchicalGridAdapter ):
    """ Adapts JSON object elements for display using a Hierarchical Grid
        Editor.
    """

    columns = [
        ( 'Name',  'name'  ),
        ( 'Value', 'value' )
    ]

    name_width  = Float( 0.33 )
    value_width = Float( 0.67 )

    def is_open ( self, object, is_open = None ):
        return self.object.factory.auto_open

    def has_children ( self, item ):
        return (len( item.children ) > 0)

    def children ( self, item ):
        return item.children

#-------------------------------------------------------------------------------
#  'JSONDict' class:
#-------------------------------------------------------------------------------

class JSONDict ( HasPrivateFacets ):
    """ Wrapper class for a JSON dictionary item.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The data this item is a wrapper for:
    data = Any

    # The name of this item:
    name = Str

    # The value of this item:
    value = Constant( '{...}' )

    # The child nodes for this node:
    children = Property

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'data' )
    def _get_children ( self ):
        return [ item_for( name, data )
                 for name, data in self.data.iteritems() ]


#-------------------------------------------------------------------------------
#  'JSONList' class:
#-------------------------------------------------------------------------------

class JSONList ( JSONDict ):
    """ Wrapper class for a JSON list item.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The value of this item:
    value = Constant( '[...]' )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'data' )
    def _get_children ( self ):
        return [ item_for( '[%d]' % i, data )
                 for i, data in enumerate( self.data ) ]

#-------------------------------------------------------------------------------
#  'JSONValue' class:
#-------------------------------------------------------------------------------

class JSONValue ( JSONDict ):
    """ Wrapper class for a JSON value item.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The value of this item:
    value = Property

    #-- Property Implementations -----------------------------------------------

    def _get_value ( self ):
        result = repr( self.data )
        if len( result ) <= 80:
            return result

        return ('[%d] %s...%s' %  ( len( result ), result[:40], result[-40:] ))


    def _get_children ( self ):
        return []

#-------------------------------------------------------------------------------
#  '_JSONEditor' class:
#-------------------------------------------------------------------------------

class _JSONEditor ( UIEditor ):
    """ Defines the implementation of the editor class for viewing the contents
        of a Python JSON object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The root node for the current JSON object being edited:
    root = List # ( JSONxxxx )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'root', editor = GridEditor( adapter    = JSONAdapter,
                                            operations = [] )
        )
    )

    #-- Editor Method Overrides ------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        return self.edit_facets( parent = parent, kind = 'editor' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        value = self.value
        if isinstance( value, basestring ):
            try:
                value = loads( value )
            except:
                pass

        self.root = [ item_for( 'JSON', value ) ]

#-------------------------------------------------------------------------------
#  'JSONEditor' class:
#-------------------------------------------------------------------------------

class JSONEditor ( BasicEditorFactory ):
    """ Defines an editor class for viewing the contents of a Python JSON
        object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _JSONEditor

    # Should JSON nodes be automatically opened?
    auto_open = Bool( False, facet_value = True )

#-- EOF ------------------------------------------------------------------------
