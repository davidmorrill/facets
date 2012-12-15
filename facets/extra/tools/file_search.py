"""
The File Search tool performs live searches of text files.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import walk, getcwd, listdir

from os.path \
    import basename, dirname, splitext, join, isfile

from time \
    import time

from facets.api \
    import HasFacets, File, Directory, Str, Bool, Button, Int, Float, List,    \
           Enum, Event, Instance, Property, Any, View, VGroup, VSplit, HGroup, \
           Item, UItem, GridEditor, CodeEditor, HistoryEditor, DNDEditor,      \
           ThemedCheckboxEditor, property_depends_on, on_facet_set

from facets.core.facet_base \
    import plural_of

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.i_filter \
    import Filter

from facets.ui.pyface.timer.api \
    import do_later

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

FileTypes = {
    'C':            [ '.c', '.h' ],
    'C++':          [ '.cpp', '.h' ],
    'CoffeeScript': [ 'coffee' ],
    'Java':         [ '.java' ],
    'Python':       [ '.py' ],
    'Ruby':         [ '.rb' ]
 }

#-------------------------------------------------------------------------------
#  'FileSearchGridAdapter' class:
#-------------------------------------------------------------------------------

class FileSearchGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping file search data to a GridEditor.
    """

    columns = [
        ( '#',    'count'     ),
        ( 'Name', 'base_name' ),
        ( 'Path', 'ext_path'  )
    ]
    even_bg_color = 0xF8F8F8

    # Column widths:
    count_width     = Float( 0.050 )
    base_name_width = Float( 0.475 )
    ext_path_width  = Float( 0.475 )

    # Column alignments:
    count_alignment = Str( 'center' )
    count_clicked   = Str( '' )

    #-- Property Implementations -----------------------------------------------

    def base_name_drag ( self ):
        return self.item.full_name


    def count_text ( self ):
        n = len( self.item.matches )

        return ('' if n == 0 else str( n ))


    def count_alias ( self ):
        return ( MatchIndices(
                     matches     = self.item.matches,
                     file_search = self.object
                 ), '' )


    def count_sorter ( self ):
        return (lambda l, r: cmp( len( l.matches ), len( r.matches ) ))


    def base_name_sorter ( self ):
        return (lambda l, r: cmp( l.base_name.lower(), r.base_name.lower() ))


file_search_grid_editor = GridEditor(
    adapter    = FileSearchGridAdapter,
    operations = [ 'sort' ],
    selected   = 'selected',
    filter     = 'filter'
)

#-------------------------------------------------------------------------------
#  'FileSearchFilter' class:
#-------------------------------------------------------------------------------

class FileSearchFilter ( Filter ):

    #-- Facet Definitions ------------------------------------------------------

    # The current search string:
    search = Str

    # Is the search case sensitive?
    case_sensitive = Bool( False )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HGroup(
            Item( 'search',
                  id     = 'search',
                  width  = 120,
                  editor = HistoryEditor( auto_set = True )
            ),
            UItem( 'case_sensitive',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@icons:case_sensitive',
                       off_image   = '@icons:case_insensitive',
                       on_tooltip  = 'Use case sensitive matching',
                       off_tooltip = 'Use case insensitive matching' )
            ),
        ),
        id = 'facets.extra.tools.file_search.file_search_filter'
    )

    #-- IFilter Interface ------------------------------------------------------

    def filter ( self, object ):
        if len( self.search ) == 0:
            return True

        object.update = True

        return (len( object.matches ) > 0)

#-------------------------------------------------------------------------------
#  'MatchIndices' class:
#-------------------------------------------------------------------------------

class MatchIndices ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The matches being indexed:
    matches = List # ( Str )

    # The FileSearch object to update:
    file_search = Any # Instance( FileSearch )

    # The current selected line:
    line = Int

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'matches',
               editor = CodeEditor(
                   line              = 'line',
                   selected_color    = 0xFFFFFF,
                   show_line_numbers = False )
        ),
        width = 600,
        kind  = 'popup'
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _line_set ( self, line ):
        """ Handles the 'line' facet being changed.
        """
        self.file_search.selected_match = line - 1

#-------------------------------------------------------------------------------
#  SourceFile class:
#-------------------------------------------------------------------------------

class SourceFile ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The search object this source file is associated with:
    live_search = Instance( FileSearchFilter )

    # The current root directory being searched:
    root = Directory( getcwd(), entries = 10 )

    # The full path and file name of the source file:
    full_name = File

    # The base file name of the source file:
    base_name = Str

    # The portion of the file path beyond the root search path:
    ext_path = Str

    # The contents of the source file:
    contents = List # ( Str )

    # The list of matches for the current search criteria:
    matches = Property # List( Str )

    # Event fired when the current set of matches should be recomputed:
    update = Event

    #-- Facet View Definitions -------------------------------------------------

    def _base_name_default ( self ):
        return basename( self.full_name )


    def _ext_path_default ( self ):
        return dirname( self.full_name )[ len( self.root ): ]


    def _contents_default ( self ):
        try:
            fh = open( self.full_name, 'rb' )
            contents = fh.readlines()
            fh.close()

            return contents
        except:
            return ''

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'update' )
    def _get_matches ( self ):
        search = self.live_search.search
        if search == '':
            return []

        case_sensitive = self.live_search.case_sensitive
        if case_sensitive:
            return [ '%5d: %s' % ( (i + 1), line.strip() )
                     for i, line in enumerate( self.contents )
                     if line.find( search ) >= 0 ]

        search = search.lower()

        return [ '%5d: %s' % ( (i + 1), line.strip() )
                 for i, line in enumerate( self.contents )
                 if line.lower().find( search ) >= 0 ]

#-------------------------------------------------------------------------------
#  'FindSourceFiles' class:
#-------------------------------------------------------------------------------

class FindSourceFiles ( HasFacets ):

    # The root directory of the source files:
    root = Directory

    # The type of file being searched for:
    file_type = Str

    # Should sub directories be included in the search?
    recursive = Bool

    # The search filter:
    live_search = Instance( FileSearchFilter )

    # The source files iterator:
    iterator = Any

    #-- Public Methods ---------------------------------------------------------

    def source_files ( self ):
        """ Returns the next group of source files.
        """
        files    = []
        end      = time() + 0.1
        iterator = self.iterator
        while time() < end:
            try:
                files.append( iterator.next() )
            except:
                break

        return files

    #-- Facet Default Values ---------------------------------------------------

    def _iterator_default ( self ):
        return self._next_source_file()

    #-- Private Methods --------------------------------------------------------

    def _next_source_file ( self ):
        """ Returns (via a yield) the next valid source file.
        """
        root       = self.root
        file_types = FileTypes[ self.file_type ]
        if self.recursive:
            for dir_path, dir_names, file_names in walk( root ):
                for file_name in file_names:
                    if splitext( file_name )[1] in file_types:
                        yield SourceFile(
                            live_search = self.live_search,
                            root        = root,
                            full_name   = join( dir_path, file_name )
                        )

        else:
            for file_name in listdir( root ):
                if splitext( file_name )[1] in file_types:
                    yield SourceFile(
                        live_search = self.live_search,
                        root        = root,
                        full_name   = join( root, file_name )
                    )

#-------------------------------------------------------------------------------
#  'FileSearch' class:
#-------------------------------------------------------------------------------

class FileSearch ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'File Search' )

    # The current root directory being searched:
    root = Directory( getcwd(), entries = 10, connect = 'to' )

    # Should sub directories be included in the search?
    recursive = Bool( False )

    # The file types to include in the search:
    file_type = Enum( 'Python', 'C', 'C++', 'CoffeeScript', 'Java', 'Ruby' )

    # The live search table filter:
    filter = Instance( FileSearchFilter, () )

    # The current object used to find source files:
    find_source_files = Instance( FindSourceFiles )

    # The current list of source files being searched:
    source_files = List( SourceFile )

    # The currently selected source file:
    selected = Any # Instance( SourceFile )

    # The contents of the currently selected source file:
    selected_contents = Property # List( Str )

    # The currently selected match:
    selected_match = Int

    # The text line corresponding to the selected match:
    selected_line = Property # Int

    # The full name of the currently selected source file:
    selected_full_name = Property(
        connect = 'from: currently selected file name' ) # File

    # The list of marked lines for the currently selected file:
    mark_lines = Property # List( Int )

    # Summary of current number of files and matches:
    summary = Property # Str

    # Description of current selected match:
    current_match = Property

    # Event fired when user wants to go to previous match in selected file:
    previous = Button( '@icons2:ArrowLargeUp' )

    # Event fired when user wants to go to next match in selected file:
    next = Button( '@icons2:ArrowLargeDown' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'root', id = 'root', label = 'Path', springy = True ),
                UItem( 'recursive',
                       padding = -2,
                       editor  = ThemedCheckboxEditor(
                           image       = '@icons2:Reload?H29l2',
                           off_image   = '@icons2:Reload?L12s',
                           on_tooltip  = 'Search subdirectories also',
                           off_tooltip = 'Search just this directory' )
                ),
                Item( 'file_type', label = 'Type' ),
                UItem( 'filter', id = 'filter', style = 'custom' ),
                id          = 'tb1',
                group_theme = '#themes:toolbar'
            ),
            VSplit(
                VGroup(
                    HGroup(
                        UItem( 'summary', style = 'readonly', springy = True ),
                        group_theme = '#themes:title'
                    ),
                    UItem( 'source_files',
                           id     = 'source_files',
                           editor = file_search_grid_editor,
                    ),
                    label = 'Files',
                    dock  = 'tab'
                ),
                VGroup(
                    HGroup(
                        UItem( 'selected_full_name',
                               editor  = DNDEditor(),
                               tooltip = 'Drag this file'
                        ),
                        '_',
                        UItem( 'previous',
                               enabled_when = 'selected_match > 0'
                        ),
                        UItem( 'next',
                               enabled_when = 'selected_match<len(mark_lines)-1'
                        ),
                        '_',
                        UItem( 'current_match',
                               style = 'readonly',
                               width = -45
                        ),
                        '_',
                        UItem( 'selected_full_name',
                               style   = 'readonly',
                               springy = True
                        ),
                        group_theme = '#themes:toolbar'
                    ),
                    UItem( 'selected_contents',
                           style  = 'readonly',
                           editor = CodeEditor(
                               mark_lines    = 'mark_lines',
                               line          = 'selected_line',
                               selected_line = 'selected_line'
                           )
                    ),
                    label = 'Selected',
                    dock  = 'tab'
                ),
                id = 'splitter'
            )
        ),
        title     = 'Live File Search',
        id        = 'facets.extra.tools.file_search',
        width     = 0.75,
        height    = 0.67,
        resizable = True
    )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        self._source_files_modified()

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'selected' )
    def _get_selected_contents ( self ):
        selected = self.selected

        return ('' if selected is None else ''.join( selected.contents))


    @property_depends_on( 'selected' )
    def _get_mark_lines ( self ):
        selected = self.selected

        return ([] if selected is None else
                [ int( match.split( ':', 1 )[0] )
                  for match in selected.matches ])


    @property_depends_on( 'selected, selected_match' )
    def _get_selected_line ( self ):
        selected = self.selected

        return (1 if (selected is None) or (len( selected.matches ) == 0) else
                int( selected.matches[ self.selected_match
                                     ].split( ':', 1 )[0] ))


    @property_depends_on( 'selected' )
    def _get_selected_full_name ( self ):
        selected = self.selected

        return ('' if selected is None else selected.full_name)


    @property_depends_on( 'source_files[], filter:[search, case_sensitive]' )
    def _get_summary ( self ):
        source_files = self.source_files
        search       = self.filter.search
        if search == '':
            return plural_of( len( source_files ), 'A total of %s file%s.', -1 )

        files   = 0
        matches = 0
        for source_file in source_files:
            source_file.update = True
            n = len( source_file.matches )
            if n > 0:
                files   += 1
                matches += n

        return ('A total of %s found with %s containing %d match%s.' % (
            plural_of( len( source_files ), '%s file%s', -1 ),
            plural_of( files, '%s file%s', -1 ),
            matches,
            '' if matches == 1 else 'es'
        ))


    @property_depends_on( 'selected, selected_match' )
    def _get_current_match ( self ):
        selected = self.selected

        return ('' if selected is None else
                '%d of %d' % ( self.selected_match + 1,
                               len( self.mark_lines ) ))

    #-- Facets Event Handlers --------------------------------------------------

    def _selected_set ( self ):
        self.selected_match = 0


    def _previous_set ( self ):
        """ Handles the 'previous' button bieng clicked.
        """
        self.selected_match -= 1


    def _next_set ( self ):
        """ Handles the 'next' button being clicked.
        """
        self.selected_match += 1


    @on_facet_set( 'root, recursive, file_type' )
    def _source_files_modified ( self ):
        root = self.root if self.root != '' else getcwd()
        if isfile( root ):
            root = dirname( root )

        self.find_source_files = FindSourceFiles(
            root        = root,
            file_type   = self.file_type,
            recursive   = self.recursive,
            live_search = self.filter
        )
        self.selected     = None
        self.source_files = []
        do_later( self._get_source_files )

    #-- Private Methods --------------------------------------------------------

    def _get_source_files ( self ):
        """ Adds the next batch of source files to the list.
        """
        files = self.find_source_files.source_files()
        if len( files ) > 0:
            self.source_files.extend( files )
            do_later( self._get_source_files )

#-------------------------------------------------------------------------------
#  Run a stand-alone version of the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    FileSearch().edit_facets()

#-- EOF ------------------------------------------------------------------------