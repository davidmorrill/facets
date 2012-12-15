"""
Defines various directory editor and the directory editor factory for the
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
    import QDir

from PyQt4.QtGui \
    import QFileDialog

from file_editor \
    import FileEditor, SimpleEditor as SimpleFileEditor, \
           CustomEditor as CustomFileEditor

#-------------------------------------------------------------------------------
#  'DirectoryEditor' class:
#-------------------------------------------------------------------------------

class DirectoryEditor ( FileEditor ):
    """ PyQt editor factory for directory editors.
    """

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

    def custom_editor ( self, ui, object, name, description ):
        return CustomEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( SimpleFileEditor ):
    """ Simple style of editor for directories, which displays a text field
        and a **Browse** button that opens a directory-selection dialog box.
    """

    #-- Private Methods --------------------------------------------------------

    def _create_file_dialog ( self ):
        """ Creates the correct type of file dialog.
        """
        dlg = QFileDialog( self.control.parentWidget() )
        dlg.selectFile( self._file_name.value )
        dlg.setFileMode( QFileDialog.Directory )

        return dlg


    def _popup_editor ( self ):
        """ Returns the editor to use when creating a pop-up editor.
        """
        return DirectoryEditor()

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( CustomFileEditor ):
    """ Custom style of editor for directories, which displays a tree view of
        the file system.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The Qt model filter flags to use:
    filters = QDir.AllDirs | QDir.Drives | QDir.NoDotAndDotDot

    #-- Public Methods ---------------------------------------------------------

    def update_object ( self, idx ):
        """ Handles the user changing the contents of the edit control.
        """
        if self._model.isDir( idx ):
            self.value = unicode( self._model.filePath( idx ) )

#-- EOF ------------------------------------------------------------------------