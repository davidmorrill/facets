"""
Defines the ASTEditor class for viewing the contents of a Python Abstract Syntax
Tree (AST).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from ast \
    import AST, parse

from facets.api \
    import HasPrivateFacets, Str, Bool, Instance, List, Float, Property,    \
           Constant, View, UItem, UIEditor, BasicEditorFactory, GridEditor, \
           property_depends_on

from facets.ui.hierarchical_grid_adapter \
    import HierarchicalGridAdapter

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def xrepr ( value ):
   """ Returns the extended 'repr' value of *value*, which limits the maximum
       length string returned.
   """
   result = repr( value )
   if len( result ) <= 50:
       return result

   return '%s...%s' % ( result[:25], result[-25:] )

#-------------------------------------------------------------------------------
#  'ASTAdapter' class:
#-------------------------------------------------------------------------------

class ASTAdapter ( HierarchicalGridAdapter ):
    """ Adapts AST nodes for display using a Hierarchical Grid Editor.
    """

    columns = [
        ( 'Name = Value', 'value' ),
        ( 'Line',         'line'  ),
        ( 'Col',          'col'   )
    ]

    line_width     = Float( 35 )
    col_width      = Float( 35 )
    line_alignment = Str( 'right' )
    col_alignment  = Str( 'right' )

    def is_open ( self, object, is_open = None ):
        return self.object.factory.auto_open

    def has_children ( self, node ):
        return (len( node.children ) > 0)

    def children ( self, node ):
        return node.children

#-------------------------------------------------------------------------------
#  'ASTNode' class:
#-------------------------------------------------------------------------------

class ASTNode ( HasPrivateFacets ):
    """ Wrapper class for Python AST module nodes.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The AST node this item is a wrapper for:
    node = Instance( AST )

    # The name of this item:
    name = Str

    # The value of this item:
    value = Property

    # The line number for this item:
    line = Property

    # The column number for this item:
    col = Property

    # The child nodes for this node:
    children = Property

    # The sub nodes of this item:
    sub_nodes = Property

    #-- Property Implementations -----------------------------------------------

    def _get_value ( self ):
        return ('%s = %s( %s )' % (
                self.name,
                self.node.__class__.__name__,
                ', '.join( [ node.value for node in self.sub_nodes
                                       if isinstance( node, ASTValue ) ] ) ))


    def _get_line ( self ):
         return str( getattr( self.node, 'lineno', '' ) )


    def _get_col ( self ):
        try:
            return str( self.node.col_offset + 1 )
        except:
            return ''


    def _get_children ( self ):
        return [ node for node in self.sub_nodes
                      if isinstance( node, ASTNode ) ]


    @property_depends_on( 'node' )
    def _get_sub_nodes ( self ):
        nodes  = []
        values = []
        node   = self.node
        for name in node._fields:
            value = getattr( node, name )
            if isinstance( value, AST ):
                nodes.append( ASTNode( node = value, name = name ) )
            elif isinstance( value, list ):
                if (len( value ) > 0) and isinstance( value[0], AST ):
                    nodes.extend( [
                        ASTNode( node = value[i],
                                 name = '%s[%d]' % ( name, i ) )
                        for i in xrange( len( value ) )
                    ] )
                else:
                    values.append(
                        ASTValue( value = '%s = %s' % ( name, xrepr( value ) ) )
                    )
            else:
                values.append(
                    ASTValue( value = '%s = %s' % ( name, xrepr( value ) ) )
                )

        return (values + nodes)

#-------------------------------------------------------------------------------
#  'ASTValue' class:
#-------------------------------------------------------------------------------

class ASTValue ( HasPrivateFacets ):
    """ Wrapper class for simple AST fields whose values are not other nodes.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The value of this item:
    value = Str

    # The line number for this item:
    line = Constant( '' )

    # The column number for this item:
    col = Constant( '' )

    # The child nodes for this node:
    children = Property

    #-- Property Implementations -----------------------------------------------

    def _get_children ( self ):
        return []

#-------------------------------------------------------------------------------
#  '_ASTEditor' class:
#-------------------------------------------------------------------------------

class _ASTEditor ( UIEditor ):
    """ Defines the implementation of the editor class for viewing the contents
        of a Python Abstract Syntax Tree (AST).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The root node for the current AST hierarchy being edited:
    root = List # ( ASTNode )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'root', editor = GridEditor( adapter    = ASTAdapter,
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
                value = parse( value )
            except SyntaxError, excp:
                value = str( excp )
            except:
                pass

        if isinstance( value, AST ):
            root = ASTNode( node = value, name = 'root' )
        elif isinstance( value, basestring ):
            root = ASTValue( value = value )
        else:
            root = ASTValue( value = '<invalid>' )

        self.root = [ root ]

#-------------------------------------------------------------------------------
#  'ASTEditor' class:
#-------------------------------------------------------------------------------

class ASTEditor ( BasicEditorFactory ):
    """ Defines an editor class for viewing the contents of a Python Abstract
        Syntax Tree (AST).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ASTEditor

    # Should AST nodes be automatically opened?
    auto_open = Bool( False, facet_value = True )

#-- EOF ------------------------------------------------------------------------
