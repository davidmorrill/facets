"""
The toolkit specific implementation of a FileDialog. See the IFileDialog
interface for the API documentation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os

from PySide.QtCore \
    import QDir

from PySide.QtGui \
    import QFileDialog

from facets.core_api \
    import Enum, implements, Int, Unicode, List

from facets.ui.pyface.i_file_dialog \
    import IFileDialog, MFileDialog

from dialog \
    import Dialog

#-------------------------------------------------------------------------------
#  'FileDialog' class:
#-------------------------------------------------------------------------------

class FileDialog ( MFileDialog, Dialog ):
    """ The toolkit specific implementation of a FileDialog. See the
        IFileDialog interface for the API documentation.
    """

    implements( IFileDialog )

    #-- 'IFileDialog' interface ------------------------------------------------

    action            = Enum( 'open', 'open files', 'save as' )
    default_directory = Unicode
    default_filename  = Unicode
    default_path      = Unicode
    directory         = Unicode
    filename          = Unicode
    path              = Unicode
    paths             = List( Unicode )
    wildcard          = Unicode
    wildcard_index    = Int( 0 )

    #-- Protected IDialog Interface --------------------------------------------

    def _create_contents ( self, parent ):
        # In Qt this is a canned dialog:
        pass

    #-- IWindow Interface ------------------------------------------------------

    def close ( self ):
        # Get the path of the chosen directory:
        files = self.control.selectedFiles()

        if files:
            self.path  = unicode( files[0] )
            self.paths = [ unicode( file ) for file in files ]
        else:
            self.path  = ''
            self.paths = [ '' ]

        # Extract the directory and filename:
        self.directory, self.filename = os.path.split( self.path )

        # Get the index of the selected filter:
        self.wildcard_index = self.control.filters().indexOf(
                                  self.control.selectedFilter() )

        # Let the window close as normal:
        super( FileDialog, self ).close()

    #-- Protected IWidget Interface --------------------------------------------

    def _create_control ( self, parent ):
        # If the caller provided a default path instead of a default directory
        # and filename, split the path into it directory and filename
        # components.
        if ((len( self.default_path )      != 0) and
            (len( self.default_directory ) == 0) and
            (len( self.default_filename )  == 0)):
            default_directory, default_filename = \
                os.path.split( self.default_path )
        else:
            default_directory = self.default_directory
            default_filename  = self.default_filename

        # Convert the filter:
        keep    = True
        filters = []

        for f in self.wildcard.split( '|' ):
            if keep and f:
                filters.append( f )

            keep = not keep

        # Set the default directory:
        if not default_directory:
            default_directory = QDir.currentPath()

        dlg = QFileDialog( parent, self.title, default_directory )

        dlg.setViewMode( QFileDialog.Detail )
        dlg.selectFile( default_filename )
        dlg.setFilters( filters )

        if self.wildcard_index < filters.count():
            dlg.selectFilter( filters[ self.wildcard_index ] )

        if self.action == 'open':
            dlg.setAcceptMode( QFileDialog.AcceptOpen )
            dlg.setFileMode( QFileDialog.ExistingFile )
        elif self.action == 'open files':
            dlg.setAcceptMode( QFileDialog.AcceptOpen )
            dlg.setFileMode( QFileDialog.ExistingFiles )
        else:
            dlg.setAcceptMode( QFileDialog.AcceptSave )
            dlg.setFileMode( QFileDialog.AnyFile )

        return dlg

    #-- Facet Default Values ---------------------------------------------------

    def _wildcard_default ( self ):
        """ Return the default wildcard.
        """
        return self.WILDCARD_ALL

#-- EOF ------------------------------------------------------------------------