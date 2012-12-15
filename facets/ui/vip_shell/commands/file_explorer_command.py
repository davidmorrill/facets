"""
Defines the FileExplorerCommand shell command that allows the user to view a
hierarchical file system view in-line within the shell history.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import isdir, split, join

from facets.api \
    import Str, View, Item, SyncValue, FileSystemEditor

from facets.ui.vip_shell.items.view_item \
    import ViewItem

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The help message for the command:
HELP = """
Adds a file explorer view to the shell history using [[options]] as the root
path. [[Options]] may contain wildcard characters (e.g. <<*.py>>). You can
double-click directories or files in the file explorer view to make them
available as standard shell history items.

If no [[options]] are specified, the current shell working directory is used.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'FileExplorerCommand' class:
#-------------------------------------------------------------------------------

class FileExplorerCommand ( ShellCommand ):
    """ Defines the 'fx' file explorer shell command.
    """

    #-- Facet Definitions ------------------------------------------------------

    summary = 'Displays a file explorer view using [[options]] as the root.'
    help    = HELP
    options_type = 'path'

    # The name of the view:
    name = Str( 'File Explorer' )

    # The root of the file system to use:
    root = Str

    # The 'glob' pattern to use when matching files:
    glob = Str

    # The name of the current selected file (not used):
    file_name = Str

    # The name of the most recently double-clicked on file name:
    double_clicked = Str

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            Item( 'file_name',
                  show_label = False,
                  editor     = FileSystemEditor(
                      root           = SyncValue( self, 'root' ),
                      glob           = SyncValue( self, 'glob' ),
                      double_clicked = SyncValue( self, 'double_clicked' ) )
            )
        )

    #-- ShellCommand Interface -------------------------------------------------

    def execute ( self ):
        """ Creates a file explorer view using the specified options as the
            root.
        """
        root = self.options
        if root == '':
            root = self.shell.cwd

        if isdir( root ):
            glob = '*.py'
        else:
            root, glob = split( root )

        self.root, self.glob = root, glob

        return self.shell.history_item_for(
            ViewItem, self, lod = 1, height = 300
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _double_clicked_set ( self, path ):
        """ Handles the 'double_clicked' facet being changed.
        """
        if isdir( path ):
            path = join( path, self.glob )

        self.shell.do_command( '/ls ' + path )

#-- EOF ------------------------------------------------------------------------
