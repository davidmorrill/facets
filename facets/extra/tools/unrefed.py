"""
Defines a tool for viewing the undefined and/or imported but unreferenced
symbols contained in one or more Python source files.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import isdir, isfile, basename, dirname

from ast \
    import ClassDef, FunctionDef, ImportFrom

from facets.api \
    import HasPrivateFacets, Str, File, Float, Instance, Bool, List, Any, \
           Color, View, Tabbed, VGroup, Item, UItem, GridEditor, on_facet_set

from facets.ui.hierarchical_grid_adapter \
    import HierarchicalGridAdapter

from facets.extra.helper.python_module \
    import PythonModule

from facets.extra.helper.file_position \
    import FilePosition

from facets.lib.io.file \
    import File as AFile

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from context types to AST classes:
TypeToAST = {
    'class':    ClassDef,
    'function': FunctionDef
}

#-------------------------------------------------------------------------------
#  'Unreferenced' class:
#-------------------------------------------------------------------------------

class Unreferenced ( HasPrivateFacets ):
    """ Represents an imported but unreferenced symbol from a Python module.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the symbol:
    name = Str

    # The PythonModule the symbol is from:
    module = Instance( PythonModule )

    # The context in which the symbol is imported:
    context = Any # [ ( type, name ), ... ]

    # The top-level AST node associated with the context:
    ast = Any

    # The FilePosition associated with the symbol:
    file_position = Instance( FilePosition )

    #-- Facet Default Values ---------------------------------------------------

    def _ast_default ( self ):
        ast = self.module.ast
        for type, name in self.context:
            klass = TypeToAST[ type ]
            for node in ast.body:
                if isinstance( node, klass ) and (name == node.name):
                    ast = node

                    break
            else:
                break

        return ast


    def _file_position_default ( self ):
        position = FilePosition( file_name = self.module.file_name, line = 1 )
        name     = self.name
        for node in self.ast.body:
            if isinstance( node, ImportFrom ):
                for alias in node.names:
                    if ((alias.asname == name) or
                        ((alias.asname is None) and (alias.name == name))):
                        return position.set( line = node.lineno )

        try:
            position.line = self.ast.lineno
        except:
            pass

        return position

#-------------------------------------------------------------------------------
#  'Undefined' class:
#-------------------------------------------------------------------------------

class Undefined ( Unreferenced ):
    """ Represents a referenced but undefined global symbol from a Python
        module.
    """

    #-- Facet View Definitions -------------------------------------------------

    def _file_position_default ( self ):
        position = FilePosition( file_name = self.module.file_name, line = 1 )

        try:
            position.line = self.ast.lineno
        except:
            pass

        return position

#-------------------------------------------------------------------------------
#  'UnreferencedAdapter'
#-------------------------------------------------------------------------------

class UnreferencedAdapter ( HierarchicalGridAdapter ):
    """ Adapts a PythonModule's 'unreferenced' list for use with the Unrefed
        tool.
    """

    columns = [ ( 'Name', 'name' ), ( 'Attributes', 'attributes' ) ]

    name_width            = Float( 0.33 )
    attributes_width      = Float( 0.67 )
    PythonModule_bg_color = Color( 0xF0F0F0 )

    def PythonModule_name_text ( self ):
        return basename( self.item.file_name )

    def PythonModule_attributes_text ( self ):
        return dirname( self.item.file_name )

    def Unreferenced_name_text ( self ):
        return self.item.name

    def Unreferenced_attributes_text ( self ):
        line     = self.item.file_position.line
        context  = self.item.context
        location = ('' if len( context ) == 0 else
                    ': %s' % ('.'.join( [ item[1] for item in context ] )))

        return ('Line %d%s' % ( self.item.file_position.line, location ))

    def has_children ( self, node ):
        return isinstance( node, PythonModule )

    def children ( self, node ):
        return [
            Unreferenced( name = item[0], module = node, context = item[1] )
            for item in node.unreferenced
        ]

#-------------------------------------------------------------------------------
#  'UndefinedAdapter' class:
#-------------------------------------------------------------------------------

class UndefinedAdapter ( UnreferencedAdapter ):
    """ Adapts a PythonModule's 'undefined' list for use with the Unrefed tool.
    """

    def children ( self, node ):
        result = []
        for name, values in node.undefined.iteritems():
            result.extend( [
                Undefined( name = name, module = node, context = item )
                for item in values
            ] )

        return result

#-------------------------------------------------------------------------------
#  'Unrefed' class:
#-------------------------------------------------------------------------------

class Unrefed ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Unrefed'

    # Name of the Python source file or directory to analyze:
    file_name = File( connect = 'to: Python source file name or directory' )

    # The file position associated with the most recently selected item:
    file_position = Instance( FilePosition, connect = 'from: selected symbol' )

    # The file name associated with the most recently selected item:
    selected_file_name = File( connect = 'from: selected file name' )

    # Should directories be searched recursively?
    recursive = Bool( False, save_state = True )

    # The list of unreferenced symbols found:
    unreferenced = List

    # The list of undefined symbols found:
    undefined = List

    # The most recently selected unreferenced or undefined item:
    selected_symbol = Any

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            Tabbed(
                UItem( 'unreferenced',
                       dock   = 'tab',
                       editor = GridEditor(
                           adapter    = UnreferencedAdapter,
                           selected   = 'selected_symbol',
                           operations = []
                       )
                ),
                UItem( 'undefined',
                       dock   = 'tab',
                       editor = GridEditor(
                           adapter    = UndefinedAdapter,
                           selected   = 'selected_symbol',
                           operations = []
                       )
                ),
                id = 'tabbed'
            ),
            id = 'facets.extra.tools.unrefed.Unrefed'
        )


    options = View(
        VGroup(
            Item( 'recursive', label = 'Recursively search subdirectories' ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'file_name, recursive' )
    def _input_modified ( self ):
        """ Handles the 'file_name' facet being changed.
        """
        file_name    = self.file_name
        unreferenced = []
        undefined    = []
        if isfile( file_name ):
            self._process_file( file_name, unreferenced, undefined )
        elif isdir( file_name ):
            self._process_path( file_name, unreferenced, undefined )

        self.selected_symbol = None
        self.unreferenced    = unreferenced
        self.undefined       = undefined


    def _selected_symbol_set ( self, item ):
        """ Handles the 'selected_symbol' facet being set.
        """
        if isinstance( item, Unreferenced ):
            self.file_position      = item.file_position
            self.selected_file_name = item.module.file_name

    #-- Private Methods --------------------------------------------------------

    def _process_file ( self, file_name, unreferenced, undefined ):
        """ Process the Python source file specified by *file_name*.
        """
        pm = PythonModule( file_name = file_name )
        if len( pm.unreferenced ) > 0:
            unreferenced.append( pm )

        if len( pm.undefined ) > 0:
            undefined.append( pm )


    def _process_path ( self, path, unreferenced, undefined ):
        """ Process all of the Python source files in the directory specified
            by *path*.
        """

        for file in AFile( path ).files_of_type( '.py' ):
            name = file.absolute_path
            if basename( name ) != 'api.py':
                self._process_file( name, unreferenced, undefined )

        if self.recursive:
            for file in AFile( path ).folders:
                self._process_path(
                    file.absolute_path, unreferenced, undefined
                )

#-- EOF ------------------------------------------------------------------------
