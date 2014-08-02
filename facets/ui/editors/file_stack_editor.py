"""
Facets UI editor for selecting a file name using dual lists: a list of parent
and child directories and a list of current directory files. The user can
quickly navigate up and down through the file system by clicking on
appropriate entries in one of the two lists.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import listdir

from os.path \
    import isdir, isfile, abspath, dirname, basename, join

from facets.api \
    import List, Str, Any, Bool, Enum, UIEditor, View, HSplit, VSplit, UItem, \
           GridEditor, BasicEditorFactory

from facets.core.constants \
    import is_windows

from facets.ui.ui_facets \
    import Orientation

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.pyface.timer.api \
    import do_later

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The special path used to represent the Windows 'root':
WindowsRoot = ' Computer'

# The text color to use for various path types:
TextColor = {
    '.': 0x603030,   # Sub-directory of current path
    '?': 0xFFFFFF    # Access denied
}

# The background color to use for various path types:
BackgroundColor = {
    ' ': 0xC0C0C0,   # Windows root
    '.': 0xF0F0F0,   # Sub-directory of current path
    '?': 0x404040    # Access denied
}

#-------------------------------------------------------------------------------
#  'PathAdapter' class:
#-------------------------------------------------------------------------------

class PathAdapter ( GridAdapter ):

    columns    = [ ( 'Path', 'path' ) ]
    grid_color = 0xD0D0D0

    def path_text_color ( self ):
        return TextColor.get( self.item[:1], 0x000000 )


    def path_bg_color ( self ):
        return BackgroundColor.get( self.item[:1], 0xFFFFFF )


    def path_content ( self ):
        item = self.item
        if item[:1] in ' ?':
            return item[1:]

        if (dirname( item ) == item):
            return item

        return basename( item )

#-------------------------------------------------------------------------------
#  'FileAdapter' class:
#-------------------------------------------------------------------------------

class FileAdapter ( GridAdapter ):

    columns      = [ ( 'Filter', 'file' ) ]
    odd_bg_color = 0xF0F0F0
    grid_color   = 0xD0D0D0
    auto_filter  = True

    def file_content ( self ):
        return basename( self.item )

#-------------------------------------------------------------------------------
#  '_FileStackEditor' class:
#-------------------------------------------------------------------------------

class _FileStackEditor ( UIEditor ):
    """ Facets UI editor for selecting a file name using dual lists: a list of
        parent and child directories and a list of current directory files. The
        user can quickly navigate up and down through the file system by
        clicking on appropriate entries in one of the two lists.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current path:
    cur_path = Str

    # The list of parent directories:
    paths = List

    # The currently selected parent directory:
    path = Any

    # The list of file names in the current directory:
    files = List

    # The currently selected file name:
    file = Any

    # The type of item that can be selected:
    type = Str

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        if self.type == 'path':
            return View( self._path_editor() )

        return View(
            ( HSplit, VSplit )[ self.factory.orientation == 'vertical' ](
                self._path_editor(),
                UItem( 'files',
                       label  = 'File',
                       dock   = 'tab',
                       editor = GridEditor(
                           adapter     = FileAdapter,
                           operations  = [],
                           selected    = 'file',
                           show_titles = self.factory.filter
                       )
                ),
                id = 'splitter'
            )
        )

    #-- Method Definitions -----------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        self.type = self.factory.type

        return self.edit_facets( parent = parent, kind = 'editor' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self._update_path( abspath( self.value ) )

    #-- Private Methods --------------------------------------------------------

    def _update_path ( self, path ):
        """ Updates the various file lists to reflect that *path* has been
            selected.
        """
        file = None
        if isfile( path ):
            file = path
            path = dirname( path )
            if self.type != 'path':
                self.value = file

        if path != self.cur_path:
            files = []
            if path == WindowsRoot:
                from facets.core.facet_base import system_drives

                paths = [ WindowsRoot ] + system_drives()
            elif isdir( path ):
                paths = []
                try:
                    for name in sorted( listdir( path ) ):
                        full_name = join( path, name )
                        if isdir( full_name ):
                            paths.append( '.' + full_name )
                        else:
                            files.append( full_name )
                except:
                    # The user may not have permission to access this path:
                    paths.append( '?Access denied' )

                parent = path
                while True:
                    next_path = parent
                    paths.insert( 0, next_path )
                    parent = dirname( next_path )
                    if parent == next_path:
                        if is_windows:
                            paths.insert( 0, WindowsRoot )

                        break
            else:
                return

            self._ignore_set = True
            self.cur_path    = path
            self.paths       = paths
            self.path        = path
            self.files       = files
            self.file        = file
            if (self.type != 'file') and (file is None):
                self.value = path

            self._ignore_set = False


    def _path_editor ( self ):
        """ Returns the path editor to use in the view.
        """
        return UItem( 'paths',
            label  = 'Path',
            dock   = 'tab',
            editor = GridEditor(
                adapter     = PathAdapter,
                operations  = [],
                selected    = 'path',
                show_titles = False
            )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _path_set ( self, path ):
        if ((not self._ignore_set) and
            (path is not None)     and
            (path[:1] != '?')):
            if path[:1] == '.':
                path = path[1:]

            do_later( self._update_path, path )


    def _file_set ( self, file ):
        if (not self._ignore_set) and (file is not None):
            do_later( self._update_path, file )

#-------------------------------------------------------------------------------
#  'FileStackEditor' class:
#-------------------------------------------------------------------------------

class FileStackEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _FileStackEditor

    # The orientation of the paths and files list relative to each other:
    orientation = Orientation

    # Allow filtering the 'File' column:
    filter = Bool( True )

    # Which item type can be selected:
    type = Enum( 'file', 'path', 'both' )

#-- EOF ------------------------------------------------------------------------
