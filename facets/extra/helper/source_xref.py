#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from cPickle \
    import load, dump

from cStringIO \
    import StringIO

from os \
    import walk, remove

from os.path \
    import join, splitext, basename, exists

from threading \
    import Thread

from tokenize \
    import generate_tokens, ENDMARKER, NAME, OP

from facets.api \
    import HasPrivateFacets, Directory, List, Str, Instance, Any, Bool, Int, \
           Enum, Button, Property, View, HGroup, VGroup, Item, UItem, \
           TreeEditor, TreeNode, on_facet_set

from facets.core.facet_base \
    import read_file

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The name of the file cross-reference data is saved in:
XRefFile = 'xref.data'

# The template used for constructing 'from ... import ...' regex expressions:
ImportTemplate = r'^\s*from\s+%s.+?\s+import\s+(.*?[^\\])$'

# The Python keywords used to start a definition:
DefinitionKeywords = ( 'class', 'def' )

# The set of Python keywords:
PythonKeywords = set( [
    'class', 'def', 'if', 'else', 'elif', 'for', 'in', 'try', 'except',
    'finally', 'from', 'import', 'return', 'break', 'continue', 'while', 'not',
    'and', 'or', 'assert', 'raise', 'del', 'print', 'yield', 'global', 'exec',
    'with', 'as', 'is'
] )

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# Name style to use for RefFile and DefFile 'short_name' values:
NameStyle = Enum( 'demo', 'base', 'partial', 'full' )

#-------------------------------------------------------------------------------
#  'XRef' class:
#-------------------------------------------------------------------------------

class XRef ( HasPrivateFacets ):
    """ Container class for holding a collection of XRefName objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of XRefName objects:
    names = List # ( Instance( XRefName ) )

#-------------------------------------------------------------------------------
#  'XRefName' class:
#-------------------------------------------------------------------------------

class XRefName ( HasPrivateFacets ):
    """ Defines all file references for a particular Facet name.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The Facet name:
    name = Str

    # The list of definitions for the name:
    defs = List # ( Instance( DefFile ) )

    # The list of references for the name:
    refs = List # ( Instance( RefFile ) )

#-------------------------------------------------------------------------------
#  'RefFile' class:
#-------------------------------------------------------------------------------

class RefFile ( HasPrivateFacets ):
    """ Defines a file reference to a cross-reference symbol name.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The fully-qualified file name:
    file_name = Str

    # The short version of the file name (for use in a UI):
    short_name = Str

    # The name style to use for the 'short_name' value:
    style = NameStyle

    # The length of the 'root' directory prefix:
    root_len = Int

    # The source file line the symbol is on (1-based)
    line = Int

    # The source file column the symbol starts in (1-based):
    column = Int

    #-- Facet Default Values ---------------------------------------------------

    def _short_name_default ( self ):
        return getattr( self, '_short_name_' + self.style )()

    def _short_name_demo ( self ):
        return splitext( basename( self.file_name ) )[0].replace( '_', ' ' )

    def _short_name_base ( self ):
        return basename( self.file_name )

    def _short_name_partial ( self ):
        return self.file_name[ self.root_len: ]

    def _short_name_full ( self ):
        return self.file_name

#-------------------------------------------------------------------------------
#  'DefFile' class:
#-------------------------------------------------------------------------------

class DefFile ( RefFile ):
    """ Defines a source file and location for a cross-reference symbol name
        definition.
    """

#-------------------------------------------------------------------------------
#  Define the TreeEditor used to display the cross-reference hierarchy:
#-------------------------------------------------------------------------------

tree_editor = TreeEditor(
    nodes = [
        TreeNode( node_for  = [ XRef ],
                  children  = 'names'
        ),
        TreeNode( node_for  = [ XRefName ],
                  auto_open = False,
                  children  = 'refs',
                  label     = 'name'
        ),
        TreeNode( node_for  = [ RefFile ],
                  label     = 'short_name',
                  icon_item = '@facets:shell_pythonfile?H63S22'
        )
    ],
    editable  = False,
    hide_root = True,
    selected  = 'selected'
)

#-------------------------------------------------------------------------------
#  'SourceXRef' class:
#-------------------------------------------------------------------------------

class SourceXRef ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The root path for the source code the cross-reference is for:
    root = Directory

    # The (optional) package prefix that each 'from ...' statement must have:
    package = Str( 'facets' )

    # The complete list of XRefName objects for the root path:
    names = List # ( Instance( XRefName ) )

    # The filter to apply to the current cross-reference names:
    filter = Str

    # The name style to use for RefFile/DefFile 'short_name' values:
    style = NameStyle

    # The XRef object containing the filtered cross-reference information:
    xref = Instance( XRef, () )

    # The name of the file the cross-reference data is saved in:
    xref_file = Property

    # The currently selected cross-reference entry:
    selected = Any

    # Event fired when the cross-reference data should be refreshed:
    refresh = Button( '@icons2:Refresh' )

    # Event fired when the current filter should be cleared:
    clear = Button( '@icons2:Delete' )

    # Is a thread busy updating the cross_reference data?
    busy = Bool( False )

    # Is the cross-reference data dirty (i.e. needs to be rebuilt)?
    dirty = Bool( False )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'filter',
                      springy = True
                ),
                UItem( 'clear',
                       # fixme: Next line locks up app when button is clicked...
                       #enabled_when = "filter != ''",
                       tooltip      = 'Clear the filter'
                ),
                UItem( 'refresh',
                       enabled_when = 'not busy',
                       tooltip      = 'Refresh the cross-reference information'
                )
            ),
            Item( 'xref', editor = tree_editor ),
            show_labels = False
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def find ( self, name ):
        """ Returns the XRefName (if any) matching the specified *name*. Returns
            None if no match is found.
        """
        for xref_name in self.names:
            if name == xref_name.name:
                return xref_name

        return None


    def select ( self, name ):
        """ Selects the XRefName (if any) matching the specified *name*. Returns
            True if the specified *name* was found, and False otherwise.
        """
        xref_name = self.find( name )
        if xref_name is not None:
            self.selected = xref_name

            return True

        return False

    #-- Property Implementations -----------------------------------------------

    def _get_xref_file ( self ):
        package = self.package
        if package != '':
            package = package.replace( '.', '_' ) + '_'

        return join( self.root, package + XRefFile )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'root, package' )
    def _data_set ( self ):
        """ Handles any facet affecting the underlying cross-reference data in
            the file system being modified.
        """
        if exists( self.root ):
            self.dirty = True


    def _clear_set ( self ):
        """ Handles the 'clear' button being clicked.
        """
        self.filter = ''


    def _refresh_set ( self ):
        """ Handles the 'refresh' button being clicked.
        """
        if exists( self.xref_file ):
            remove( self.xref_file )

        self.dirty = True


    def _dirty_set ( self, dirty ):
        """ Handles the 'dirty' facet being changed.
        """
        if dirty and (not self.busy):
            self.busy = True
            Thread( target = self._update_xref ).start()


    @on_facet_set( 'names, filter' )
    def _xref_modified ( self ):
        """ Handles any facet affecting the filtered XRef object being modified.
        """
        filter = self.filter.strip().lower()
        self.xref = XRef(
            names = [ item for item in self.names
                           if item.name.lower().find( filter ) >= 0 ]
        )

    #-- Private Methods --------------------------------------------------------

    def _update_xref ( self ):
        """ Updates the cross-reference data.
        """
        while self.dirty:
            self.dirty = False
            xref_file  = self.xref_file
            if not exists( xref_file ):
                self._save_xref( xref_file )

            self._load_xref( xref_file )

        self.busy = False


    def _xref_for ( self, name, defs, refs ):
        """ Create a XRefName object for the specified Facet symbol *name* with
            definition files specified by *defs* and referencing files
            specified by *refs*.
        """
        root     = self.root
        style    = self.style
        root_len = len( root ) + 1

        return XRefName(
            name = name,
            defs = [ DefFile(
                         file_name = join( root, file ),
                         line      = line,
                         column    = column,
                         style     = style,
                         root_len  = root_len
                     ) for file, line, column in defs ],
            refs = [ RefFile(
                         file_name = join( root, file ),
                         line      = line,
                         column    = column,
                         style     = style,
                         root_len  = root_len
                     ) for file, line, column in refs ]
        )


    def _load_xref ( self, xref_file ):
        """ Load the data from the cross_reference file specified by
            *xref_file*.
        """
        # Unpickle the data from the cross-reference save file:
        fh        = open( xref_file, 'rb' )
        xref_data = load( fh )
        fh.close()

        # Convert the data into an XRef object:
        xref_for   = self._xref_for
        self.names = [ xref_for( name, defs, refs )
                       for name, defs, refs in xref_data ]


    def _save_xref ( self, xref_file ):
        """ Build the cross-reference data for the current 'root' directory and
            save it in the file specified by *xref_file*.
        """
        # Create the regex pattern used to match 'from ...' statements:
        package = self.package
        if package != '':
            package += '\.'

        regex = re.compile( ImportTemplate % package,
                            re.MULTILINE | re.DOTALL )
        n     = len( self.root ) + 1
        xrefs = {}
        for path, dirs, files in walk( self.root ):
            # Don't process any .svn directories:
            for i, dir in enumerate( dirs ):
                if dir == '.svn':
                    del dirs[ i ]

                    break

            # Process each file in the directory:
            for file in files:
                file_name = join( path, file )

                # Only handle Python files:
                if splitext( file_name )[1] == '.py':
                    # Create a location independent file name:
                    short_file_name = file_name[ n: ]

                    # Find each 'from package.xxx import ...' statement in file:
                    source = read_file( file_name ).replace( '\r\n', '\n'
                                                  ).replace( '\r',   '\n' )
                    names  = {}
                    for match in regex.finditer( source ):
                        line = (len( source[ : match.start() ].split( '\n' ) )
                                + 1)
                        text = match.group( 1 ).replace( '\\', '' )
                        for c in '#;':
                            text = text.split( c, 1 )[0]

                        for name in text.split( ',' ):
                            name = name.split()[0].strip()
                            names.setdefault( name, ( line, 1 ) )

                    # For each unique symbol, add a cross-reference entry to
                    # the current file:
                    for name, location in names.iteritems():
                        entry = xrefs.get( name )
                        if entry is None:
                            xrefs[ name ] = entry = ( [], [] )

                        entry[1].append( ( short_file_name, ) + location )

                    # Add all top-level definitions contained in the file:
                    file_defs = self._find_definitions( source )
                    for name, location in file_defs.iteritems():
                        entry = xrefs.get( name )
                        if entry is None:
                            xrefs[ name ] = entry = ( [], [] )

                        entry[0].append( ( short_file_name, ) + location )

        # Eliminate any entries which have no references:
        for name in xrefs.keys():
            if len( xrefs[ name ][1] ) == 0:
                del xrefs[ name ]

        # Sort all cross-reference symbols case insensitively:
        names = xrefs.keys()
        names.sort( lambda l, r: cmp( l.lower(), r.lower() ) )

        # Pickle the cross-reference data to a save file:
        fh = open( xref_file, 'wb' )
        dump( [ ( name, ) + xrefs[ name ] for name in names ], fh, -1 )
        fh.close()


    def _find_definitions ( self, source ):
        """ Returns all the top-level definitions contained in the specified
            Python *source* text. The result is a dictionary mapping defined
            symbol names to tuples of the form: ( line, column ), where 'line'
            and 'column' are the file line and column (1 based origin) where
            the associated symbol is defined.
        """
        definitions = {}
        def_pending = assign_pending = False
        tokenizer   = generate_tokens( StringIO( source ).readline )
        try:
            for type, token, first, last, line in tokenizer:
                if type == ENDMARKER:
                    break

                if assign_pending:
                    assign_pending = False
                    if (type == OP) and (token == '='):
                        name, line, column  = saved_def
                        definitions[ name ] = ( line, column + 1 )

                if type == NAME:
                    line, column = first
                    if def_pending:
                        def_pending          = False
                        definitions[ token ] = ( line, column + 1 )
                    elif column == 0:
                        if token in DefinitionKeywords:
                            def_pending = True
                        elif token not in PythonKeywords:
                            assign_pending = True
                            saved_def      = ( token, line, column )
        except:
            pass

        return definitions

#-- EOF ------------------------------------------------------------------------
