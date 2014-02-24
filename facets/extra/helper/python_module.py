"""
Defines the PythonModule class which represents useful information about the
structure and semantics of a Python module.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import os
import ast
import symtable

from os.path \
    import abspath, basename, isfile, join, splitext

from facets.api \
    import HasPrivateFacets, List, Str, Int, Bool, Code, Tuple, Any, File, \
           Property, ASTEditor, property_depends_on

from facets.core.facet_base \
   import read_file

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The set of standard Python symbols:
GlobalSymbols = set( [
    'None', 'True', 'False', 'getattr', 'setattr', 'hasattr', 'delattr', 'len',
    'eval', 'globals', 'locals', 'object', 'super', 'type', 'max', 'min',
    'isinstance', 'int', 'long', 'bool', 'float', 'complex', 'str',
    'basestring', 'unicode', 'list', 'tuple', 'dict', 'set', 'range', 'xrange',
    'round', 'abs', 'enumerate', 'round', 'id', 'reduce', 'cmp', 'sorted',
    'repr', 'dir', 'open', 'file', 'classmethod', 'staticmethod', 'execfile',
    'compile', 'callable', 'map', 'chr', 'ord', 'zip', 'hash', 'issubclass',
    'slice', 'property', '__import__', '__file__', '__name__',
    'NotImplementedError', 'AttributeError', 'IndexError', 'TypeError',
    'ValueError', 'SyntaxError', 'IOError', 'ImportError', 'RuntimeError',
    'SystemError', 'OSError', 'WindowsError', 'Exception', 'StopIteration'
] )

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def table_for ( st ):
    """ Returns an appropriate ...SymbolTable adapted instance for the symbol
        table specified by *st*.
    """
    return SymbolTables[ st.get_type() ]( st = st )

#-------------------------------------------------------------------------------
#  'ModuleSymbolTable' class:
#-------------------------------------------------------------------------------

class ModuleSymbolTable ( HasPrivateFacets ):
    """ Base class for adapting a Python symbol table object as a HasFacets
        object. This is also the concrete class for a module symbol table.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The type of the symbol table:
    type = Property( Str )

    # The id of the symbol table:
    id = Property( Int )

    # The name of the symbol table:
    name = Property( Str )

    # The first line in the block this table represents:
    line = Property( Int )

    # Can the locals in this table be optimized?
    is_optimized = Property( Bool )

    # Is the block a nested class or function?
    is_nested = Property( Bool )

    # Does the block contained nest namespaces?
    has_children = Property( Bool )

    # Does the block use 'exec'?
    has_exec = Property( Bool )

    # Does the block use a starred from import (i.e. from ... import *)?
    has_import_star = Property( Bool )

    # The list of names in the table:
    identifiers = Property( List )

    # The list of symbols in the table:
    symbols = Property( List )

    # The listed of nested symbol tables:
    children = Property( List )

    # The Python symbol table being adapted:
    st = Any # Instance( symtable.SymbolTable )

    # Mapping from name to Symbol object:
    symbol_map = Any # Dict( Str, Instance( Symbol ) )

    #-- Property Implementations -----------------------------------------------

    def _get_type            ( self ): return self.st.get_type()
    def _get_id              ( self ): return self.st.get_id()
    def _get_name            ( self ): return self.st.get_name()
    def _get_line            ( self ): return self.st.get_lineno()
    def _get_is_optimized    ( self ): return self.st.is_optimized()
    def _get_is_nested       ( self ): return self.st.is_nested()
    def _get_has_children    ( self ): return self.st.has_children()
    def _get_has_exec        ( self ): return self.st.has_exec()
    def _get_has_import_star ( self ): return self.st.has_import_star()

    @property_depends_on( 'st' )
    def _get_identifiers ( self ):
        return self.st.get_identifiers()

    @property_depends_on( 'st' )
    def _get_symbols ( self ):
        return [ Symbol( sym = symbol ) for symbol in self.st.get_symbols() ]

    @property_depends_on( 'st' )
    def _get_children ( self ):
        return [ table_for( child ) for child in self.st.get_children() ]

    #-- Facet Default Values ---------------------------------------------------

    def _symbol_map_default ( self ):
        return dict( [ ( symbol.name, symbol ) for symbol in self.symbols ] )

    #-- Public Methods ---------------------------------------------------------

    def lookup ( self, name ):
        """ Lookup name in the table and return a Symbol instance.
        """
        return self.symbol_map[ name ]

#-------------------------------------------------------------------------------
#  'FunctionSymbolTable' class:
#-------------------------------------------------------------------------------

class FunctionSymbolTable ( ModuleSymbolTable ):
    """ An adapted namespace for a function or method.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The names of the parameters to this function:
    parameters = Property( Tuple )

    # The names of the locals in this function:
    locals = Property( Tuple )

    # The names of the globals in this function:
    globals = Property( Tuple )

    # The names of the free variables in this function:
    frees = Property( Tuple )

    #-- Property Implementations -----------------------------------------------

    def _get_parameters ( self ): return self.st.get_parameters()
    def _get_locals     ( self ): return self.st.get_locals()
    def _get_globals    ( self ): return self.st.get_globals()
    def _get_frees      ( self ): return self.st.get_frees()

#-------------------------------------------------------------------------------
#  'ClassSymbolTable' class:
#-------------------------------------------------------------------------------

class ClassSymbolTable ( ModuleSymbolTable ):
    """ An adapted namespace for a class.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The methods declared in the class:
    methods = Property( List )

    #-- Property Implementations -----------------------------------------------

    def _get_methods ( self ): return self.st.get_methods()

# Mapping from symbol table type to corresponding HasFacets adapter class:
SymbolTables = {
    'module':   ModuleSymbolTable,
    'class':    ClassSymbolTable,
    'function': FunctionSymbolTable
}

#-------------------------------------------------------------------------------
#  'Symbol' class:
#-------------------------------------------------------------------------------

class Symbol ( HasPrivateFacets ):
    """ Adapts a symtable.Symbol to a HasFacets object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the symbol:
    name = Property( Str )

    # Is the symbol used in its block?
    is_referenced = Property( Bool )

    # Is the symbol created from an import statement?
    is_imported = Property( Bool )

    # Is the symbol a parameter?
    is_parameter = Property( Bool )

    # Is the symbol a global?
    is_global = Property( Bool )

    # Is the symbol declared using a global statement?
    is_declared_global = Property( Bool )

    # Is the symbol local to its block?
    is_local = Property( Bool )

    # Is the symbol referenced but not assigned to in its block?
    is_free = Property( Bool )

    # Is the symbol assigned to in its block?
    is_assigned = Property( Bool )

    # Is the symbol bound to a new namespace?
    is_namespace = Property( Bool )

    # The Python symbol being adapted:
    sym = Any # Instance( symtable.Symbol )

    #-- Property Implementations -----------------------------------------------

    def _get_name               ( self ): return self.sym.get_name()
    def _get_is_referenced      ( self ): return self.sym.is_referenced()
    def _get_is_imported        ( self ): return self.sym.is_imported()
    def _get_is_parameter       ( self ): return self.sym.is_parameter()
    def _get_is_global          ( self ): return self.sym.is_global()
    def _get_is_declared_global ( self ): return self.sym.is_declared_global()
    def _get_is_local           ( self ): return self.sym.is_local()
    def _get_is_free            ( self ): return self.sym.is_free()
    def _get_is_assigned        ( self ): return self.sym.is_assigned()
    def _get_is_namespace       ( self ): return self.sym.is_namespace()

#-------------------------------------------------------------------------------
#  'PythonModule' class:
#-------------------------------------------------------------------------------

class PythonModule ( HasPrivateFacets ):
    """ Defines the PythonModule class which represents useful information about
        the structure and semantics of a Python module.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the file containing the Python source module:
    file_name = File

    # The list of paths used to resolve the package the file is part of:
    path = List # ( Str )

    # The package the module is part of:
    package = Str

    # The name of the module:
    module = Str

    # The source code defining the module:
    source = Code

    # The compiled code for the module:
    code = Property

    # The root of the abstract syntax tree (AST) for the module:
    ast = Property( editor = ASTEditor() ) # Instance( ast.AST )

    # The top (module) level symbol table for the module:
    symbol_table = Property # Instance( xxxSymbolTable )

    # The list of all top-level symbols defined by the module:
    defined = Property( List )

    # The list of all undefined global symbol references:
    undefined = Property( List )

    # The list of all imported, but unreferenced, symbols:
    unreferenced = Property( List )

    # A description of the current module status:
    status = Str

    # The line number of the error for a module that could not be parsed:
    line = Int

    # The column number of the error for a module that could not be parsed:
    column = Int

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'source' )
    def _get_code ( self ):
        return self._process(
            lambda code: compile( code, self.file_name or '<string>', 'exec' )
        )


    @property_depends_on( 'source' )
    def _get_ast ( self ):
        return self._process( lambda code: ast.parse( code ) )


    @property_depends_on( 'source' )
    def _get_symbol_table ( self ):
        return self._process( lambda code: table_for(
            symtable.symtable( code, self.file_name or '<string>', 'exec' )
        ) )


    @property_depends_on( 'symbol_table' )
    def _get_defined ( self ):
        if self.symbols is not None:
            return [ symbol for symbol in self.symbols.symbols
                            if symbol.is_assigned ]

        return []


    @property_depends_on( 'symbol_table' )
    def _get_undefined ( self ):
        symbol_table = self.symbol_table
        if symbol_table is None:
            return []

        defined = set( [
            symbol.name for symbol in symbol_table.symbols
                        if symbol.is_imported or
                           (symbol.is_local and symbol.is_assigned)
        ] )

        undefined = dict( [ ( symbol.name, [ () ] )
            for symbol in symbol_table.symbols
            if symbol.is_global and symbol.is_referenced and
               (symbol.name not in GlobalSymbols)
        ] )

        for child in symbol_table.children:
            self._check_undefined( child, defined, undefined, [] )

        return undefined


    @property_depends_on( 'symbol_table' )
    def _get_unreferenced ( self ):
        symbol_table = self.symbol_table
        if symbol_table is None:
            return []

        module_unreferenced = set( [
            symbol.name for symbol in symbol_table.symbols
                        if symbol.is_imported and (not symbol.is_referenced)
        ] )
        local_unreferenced = []

        for child in symbol_table.children:
            self._check_references(
                child, module_unreferenced, local_unreferenced, []
            )

        return sorted(
            [ ( name, [] ) for name in module_unreferenced ] +
            local_unreferenced,
            None, lambda x: x[0].lower()
        )

    #-- Facet Default Values ---------------------------------------------------

    def _path_default ( self ):
        return sys.path

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        """ Handles the 'file_name' facet being changed.
        """
        source = read_file( file_name )
        if source is not None:
            file_name = splitext( abspath( file_name ) )[0]
            module    = basename( file_name )
            package   = ''
            for path in self.path:
                path = abspath( path )
                if file_name.startswith( path ):
                    base = file_name[ len( path ): ].strip( os.sep )
                    for path_element in base.split( os.sep )[:-1]:
                        path = join( path, path_element )
                        if not isfile( join( path, '__init__.py' ) ):
                            break
                    else:
                        module  = base.replace( os.sep, '.' )
                        package = module.rsplit( '.', 1 )[0]

                        break

            self.package = package
            self.module  = module
            self.source  = source

    #-- Public Methods ---------------------------------------------------------

    def execute ( self, global_dic = None, local_dic = None ):
        """ Executes the code for the module.
        """
        if global_dic is None:
            global_dic = globals()

        if local_dic is None:
            local_dic = global_dic

        eval( self.code, global_dic, local_dic )

    #-- Private Methods --------------------------------------------------------

    def _process ( self, func ):
        """ Returns the result of applying the specified *func* to the current
            module source code. It handles any exceptions that occur by
            saving the exception and returning None as the result.
        """
        status = ''
        line   = column = -1
        try:
            return func( self.source )
        except SyntaxError, excp:
            status, line, column = excp.msg, excp.lineno, excp.offset
        except Exception, excp:
            status = str( excp )
        finally:
            self.status = status
            self.line   = line
            self.column = column


    def _check_references ( self, symbol_table, module_unreferenced,
                                  local_unreferenced, context ):
        """ Checks all symbols and namespaces contained in the symbol table
            specified by *symbol_table* for global references and removes them
            from the *module_unreferenced* set if present. Any local imported
            but unreferenced symbols are added to the *local_unreferenced* list
            along with their local context information as a tuple of the
            form: ( name, [ ( context, cname ), ( context, cname ), ... ] ),
            where context is the symbol table type, and cname is the symbol
            table name.
        """
        my_unreferenced = {}
        for symbol in symbol_table.symbols:
            if symbol.is_global and symbol.is_referenced:
                module_unreferenced.discard( symbol.name )
            elif symbol.is_imported and (not symbol.is_referenced):
                my_unreferenced[ symbol.name ] = 0
            elif symbol.is_free and symbol.is_referenced:
                symbol_name = symbol.name
                for type, name, unreferenced in context:
                    count = unreferenced.get( symbol_name )
                    if count is not None:
                        unreferenced[ symbol_name ] = count + 1

                        break

        if symbol_table.has_children:
            context = context[:]
            context.append(
                ( symbol_table.type, symbol_table.name, my_unreferenced )
            )
            for child in symbol_table.children:
                self._check_references(
                    child, module_unreferenced, local_unreferenced, context
                )

        if len( my_unreferenced ) > 0:
            location = [ item[:2] for item in context ]
            for name, count in my_unreferenced.iteritems():
                if count == 0:
                    local_unreferenced.append( ( name, location ) )


    def _check_undefined ( self, symbol_table, defined, undefined, context ):
        """
        """
        context = context[:]
        context.append( ( symbol_table.type, symbol_table.name ) )

        for symbol in symbol_table.symbols:
            if (symbol.is_global             and
                symbol.is_referenced         and
                (symbol.name not in defined) and
                (symbol.name not in GlobalSymbols)):
                undefined.setdefault( symbol.name, [] ).append( context )

        for child in symbol_table.children:
            self._check_undefined( child, defined, undefined, context )

#-- EOF ------------------------------------------------------------------------
