"""
A tool for displaying the Python classes, methods, and functions defined by a
Python source file or string.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import ast

from os.path \
    import basename, splitext

from ast \
    import parse, NodeVisitor

from facets.api \
    import HasPrivateFacets, Str, Int, File, List, Instance, Property, View, \
           UItem, GridEditor

from facets.core.facet_base \
    import read_file

from facets.ui.hierarchical_grid_adapter \
    import HierarchicalGridAdapter

from facets.extra.helper.file_position \
    import FilePosition

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from definition type to grid background color:
TypeBGColor = {
    'Module':          0xD0D0D0,
    'Class':           0xE4E4E4,
    'Method':          0xECF1FF,
    'Function':        0xECF1FF,
    'Symbol':          0xFFFFD2,
    'Import':          0xD3FFAF,
    'ImportName':      0xEFFFE3,
    'SectionFunction': 0xCDDBFF,
    'SectionSymbol':   0xFFFFA8,
    'SectionImport':   0xD3FFAF
}

# Mapping from definition type to sort order:
TypeSortOrder = {
    'Import':   '0',
    'Symbol':   '1',
    'Function': '2',
    'Method':   '2',
    'Class':    '3'
}

#-------------------------------------------------------------------------------
#  'Def' class:
#-------------------------------------------------------------------------------

class Def ( HasPrivateFacets ):
    """ Base class for all Python source file definitions.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The type of definition:
    type = Str

    # The name of the definition:
    name = Str

    # The id of the definition:
    id = Property

    # The line number within the source file of the start of the definition:
    line = Int

    # The children of this definition:
    children = List

    #-- Property Implementations -----------------------------------------------

    def _get_id ( self ):
        return ('%s: %s') % ( self.type, self.name )

#-------------------------------------------------------------------------------
#  'DefAdapter' class:
#-------------------------------------------------------------------------------

class DefAdapter ( HierarchicalGridAdapter ):
    """ Adapts Def objects for use with the Grid Editor.
    """

    columns = [ ( 'Name', 'name' ) ]

    def bg_color ( self ):
        return TypeBGColor.get( self.item.type, 0xFFFFFF )

    def is_open ( self, item, is_open = None ):
        return (item.type == 'Module')

    def has_children ( self, item ):
        return (len( item.children ) > 0)

    def children ( self, item ):
        return item.children

#-------------------------------------------------------------------------------
#  'DefVisitor' class:
#-------------------------------------------------------------------------------

class DefVisitor ( NodeVisitor ):
    """ Custom AST node visitor for extracting class, method function
        definitions.
    """

    #-- Object method overrides ------------------------------------------------

    def __init__ ( self, file_name ):
        """ Initializes the object.
        """
        super( DefVisitor, self ).__init__()

        self.parent = Def(
            type = 'Module',
            name = splitext( basename( file_name ) )[0],
            line = 1
        )

    #-- Node visitor methods ---------------------------------------------------

    def visit_def ( self, node, type ):
        """ Handles a definition.
        """
        parent = self.parent
        child  = Def( type = type, name = node.name, line = node.lineno )
        parent.children.append( child )
        self.parent = child
        self.generic_visit( node )
        child.children = sorted(
            child.children, None,
            lambda x: TypeSortOrder[ x.type ] + x.name.lower()
        )
        self.parent = parent


    def visit_Module ( self, node ):
        """ Handles a Module node.
        """
        self.generic_visit( node )
        groups = {
            'Function': [],
            'Import':   [],
            'Class':    [],
            'Symbol':   []
        }
        for item in self.parent.children:
            groups[ item.type ].append( item )

        item_key = lambda x: x.name.lower()
        items    = sorted( groups[ 'Class' ], None, item_key )
        for name in ( 'Function', 'Symbol', 'Import' ):
            values = groups[ name ]
            if len( values ) > 0:
                items.insert( 0, Def(
                    type     = 'Section' + name,
                    name     = name + 's',
                    line     = -1,
                    children = sorted( values, None, item_key )
                ) )

        self.parent.children = items


    def visit_ClassDef ( self, node ):
        """ Handles a Python class definition.
        """
        self.visit_def( node, 'Class' )


    def visit_FunctionDef ( self, node ):
        """ Handles a Python function or method definition.
        """
        self.visit_def(
            node, 'Method' if self.parent.type == 'Class' else 'Function'
        )


    def visit_Assign ( self, node ):
        """ Handles an assignment statement.
        """
        parent = self.parent
        if parent.type in ( 'Module', 'Class' ):
            for name in node.targets:
                if isinstance( name, ast.Name ):
                    parent.children.append( Def(
                        type = 'Symbol',
                        name = name.id,
                        line = name.lineno
                    ) )

        self.generic_visit( node )


    def visit_ImportFrom ( self, node ):
        """ Handles a 'from ... import ...' statement.
        """
        line    = node.lineno
        parent  = self.parent
        imports = Def(
            type = 'Import',
            name = node.module or '.',
            line = line
        )
        parent.children.append( imports )
        children = [ Def( type = 'ImportName',
                          name = self._alias_name_for( alias ),
                          line = line )
                     for alias in node.names ]
        imports.children = sorted( children, None, lambda x: x.name.lower() )

        self.generic_visit( node )


    def visit_Import ( self, node ):
        """ Handles an 'import ...' statement.
        """
        line = node.lineno
        self.parent.children.extend( [
            Def( type = 'Import',
                 name = self._alias_name_for( alias ),
                 line = line )
            for alias in node.names
        ] )

        self.generic_visit( node )

    #-- Private Methods --------------------------------------------------------

    def _alias_name_for ( self, alias ):
        """ Returns the name to use for the AST *alias* object.
        """
        name = alias.name
        if alias.asname is not None:
            name = '%s -> %s' % ( name, alias.asname )

        return name

#-------------------------------------------------------------------------------
#  'Definitions' class:
#-------------------------------------------------------------------------------

class Definitions ( Tool ):
    """ A tool for displaying the Python classes, methods, and functions defined
        by a Python source file or string.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Definitions' )

    # The current Python source file being processed:
    file_name = File( connect = 'to: Python source file' )

    # The current Python source being processed:
    source = Str( connect = 'to: Python source' )

    # The definitions for the current Python source:
    definitions = List

    # The currently selected definition:
    definition = Instance( Def )

    # The line number of the currently selected definition:
    line = Int( connect = 'from: line number of selected definition' )

    # The file position for the currently selected definition:
    position = Instance( FilePosition,
        connect = 'from: file position of selected definition'
    )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'definitions', editor = GridEditor(
                                 adapter     = DefAdapter,
                                 operations  = [],
                                 selected    = 'definition',
                                 show_titles = False )
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        """ Handles the 'file_name' facet being modified.
        """
        if file_name != '':
            source = read_file( file_name )
            if source is not None:
                self._no_file_name_update = True
                self.source               = source
                self._no_file_name_update = False


    def _source_set ( self, source ):
        """ Handles the 'source' facet being changed.
        """
        if not self._no_file_name_update:
            self.file_name = ''

        try:
            visitor = DefVisitor( self.file_name )
            visitor.visit( parse( source ) )
            self.definitions = [ visitor.parent ]
            self.definition  = None
        except SyntaxError, excp:
            pass
        except:
            import traceback
            traceback.print_exc()


    def _definition_set ( self, definition ):
        """ Handles the 'definition' facet being changed.
        """
        if definition is not None:
            line = definition.line
            if line > 0:
                self.line = line
                if self.file_name != '':
                    self.position = FilePosition(
                        file_name = self.file_name,
                        line      = self.line
                    )

#-- EOF ------------------------------------------------------------------------
