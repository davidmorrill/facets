"""
Facets pyface package component
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os

import wx

from facets.core_api \
    import Enum, implements, Unicode, Int, List

from facets.ui.pyface.i_file_dialog \
    import IFileDialog, MFileDialog

from dialog \
    import Dialog

#-------------------------------------------------------------------------------
#  'FileDialog' class:
#-------------------------------------------------------------------------------

class FileDialog ( MFileDialog, Dialog ):
    """ The toolkit specific implementation of a FileDialog.  See the
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

    #-- Protected 'IDialog' Interface ------------------------------------------

    def _create_contents ( self, parent ):
        # In wx this is a canned dialog:
        pass

    #-- 'IWindow' Interface ----------------------------------------------------

    def close ( self ):
        # Get the path of the chosen directory:
        self.path = unicode( self.control.GetPath() )

        # Work around wx bug throwing exception on cancel of file dialog:
        if len( self.path ) > 0:
            self.paths = self.control.GetPaths()
        else:
            self.paths = []

        # Extract the directory and filename:
        self.directory, self.filename = os.path.split( self.path )

        # Get the index of the selected filter:
        self.wildcard_index = self.control.GetFilterIndex()

        # Let the window close as normal:
        super( FileDialog, self ).close()

    #-- Protected 'IWidget' Interface ------------------------------------------

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

        if self.action == 'open':
            style = wx.OPEN | wx.HIDE_READONLY
        elif self.action == 'open files':
            style = wx.OPEN | wx.HIDE_READONLY | wx.MULTIPLE
        else:
            style = wx.SAVE | wx.OVERWRITE_PROMPT

        # Create the actual dialog:
        dialog = wx.FileDialog( parent, self.title,
                    defaultDir  = default_directory,
                    defaultFile = default_filename,
                    style       = style,
                    wildcard    = self.wildcard.rstrip( '|' ) )

        dialog.SetFilterIndex( self.wildcard_index )

        return dialog

    #-- Facet Default Values ---------------------------------------------------

    def _wildcard_default ( self ):
        """ Return the default wildcard.
        """
        return self.WILDCARD_ALL

#-- EOF ------------------------------------------------------------------------