"""
Defines the source code cross reference tool.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import List, Str, Any, Directory, Instance, View, VGroup, VSplit, Item, \
           TextEditor, GridEditor, on_facet_set

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.helper.source_xref \
    import SourceXRef, XRefName, RefFile

from facets.extra.helper.file_position \
    import FilePosition

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The list of valid Python symbol characters:
SymbolCharacters = ('abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')

#-------------------------------------------------------------------------------
#  'DefinitionGridAdapter' class:
#-------------------------------------------------------------------------------

class DefinitionGridAdapter ( GridAdapter ):
    """ Adapts DefRef object for use with the GridEditor.
    """

    columns       = [ ( 'Definitions', 'short_name' ) ]
    can_edit      = False
    even_bg_color = 0xF8F8F8

#-------------------------------------------------------------------------------
#  'CrossReference' class:
#-------------------------------------------------------------------------------

class CrossReference ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Cross Reference'

    # The source code root directory:
    root = Directory( save_state = True )

    # The package prefix used to restrict the cross_reference data:
    package = Str( 'facets', save_state = True )

    # The name of a symbol to look up or use as a filter:
    symbol = Str( connect = 'to' )

    # The most recently selected cross_reference file or definition:
    file_name = Instance( FilePosition, connect = 'from: selected file' )

    # The list of definitions associated with the most recently selected item:
    definitions = List # ( Instance( DefFile ) )

    # The most recently selected definition:
    selected = Any # Instance( DefFile )

    # The SourceXRef object containing the cross-reference data:
    xref = Instance( SourceXRef )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        VSplit(
            Item( 'xref',
                  show_label = False,
                  style      = 'custom'
            ),
            Item( 'definitions',
                  show_label = False,
                  editor     = GridEditor(
                      adapter    = DefinitionGridAdapter,
                      operations = [],
                      selected   = 'selected' )
            ),
            id = 'splitter'
        ),
        id = 'facets.extra.tools.cross_reference.CrossReference'
    )


    options = View(
        VGroup(
            Item( 'root',
                  label = 'Root directory',
                  width = -350
            ),
            Item( 'package',
                  label  = 'Package prefix',
                  editor = TextEditor( auto_set = False )
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _xref_default ( self ):
        return SourceXRef(
            package = self.package,
            style   = 'partial' ).facet_set(
            root    = self.root
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _package_set ( self, package ):
        """ Handles the 'package' facet being changed.
        """
        self.xref.package = package


    def _root_set ( self, root ):
        """ Handles the 'root' facet being changed.
        """
        self.xref.root = root


    @on_facet_set( 'xref:selected' )
    def _xref_modified ( self ):
        """ Handles a SourceXRef item being selected.
        """
        selected = self.xref.selected
        if isinstance( selected, XRefName ):
            self.definitions = defs = selected.defs
            if len( defs ) > 0:
                self.selected = defs[0]
            else:
                self.selected = None
        else:
            self.selected = None
            del self.definitions[:]
            if isinstance( selected, RefFile ):
                self.file_name = self._position_for( selected )


    def _symbol_set ( self, symbol ):
        """ Handles the 'symbol' facet being changed.
        """
        if self._is_symbol( symbol) and (not self.xref.select( symbol )):
            self.xref.filter = symbol


    def _selected_set ( self, selected ):
       """ Handles the 'selected' facet being changed.
       """
       if isinstance( selected, RefFile ):
           self.file_name = self._position_for( selected )

    #-- Private Methods --------------------------------------------------------

    def _position_for ( self, ref_file ):
        """ Returns a FilePosition object for the specified RefFile object
            specified by *ref_file*.
        """
        return FilePosition(
            file_name = ref_file.file_name,
            line      = ref_file.line,
            column    = ref_file.column
        )


    def _is_symbol ( self, symbol ):
        """ Returns whether or not the specified *symbol* is a valid Python
            symbol.
        """
        if len( symbol ) > 0:
            for c in symbol:
                if c not in SymbolCharacters:
                    break
            else:
                return True

        return False

#-- EOF ------------------------------------------------------------------------
