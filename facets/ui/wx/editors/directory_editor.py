"""
Defines various directory editor and the directory editor factory for the
    wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from os.path \
    import isdir

from file_editor \
    import FileEditor, PopupFile, SimpleEditor as SimpleFileEditor, \
           CustomEditor as CustomFileEditor

#-------------------------------------------------------------------------------
#  'DirectoryEditor' class:
#-------------------------------------------------------------------------------

class DirectoryEditor ( FileEditor ):
    """ wxPython editor factory for directory editors.
    """

    #--  'Editor' Factory Methods ----------------------------------------------

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

    #-- Public Methods ---------------------------------------------------------

    def create_file_dialog ( self ):
        """ Creates the correct type of file dialog.
        """
        dlg = wx.DirDialog( self.control, message = 'Select a Directory' )
        dlg.SetPath( self._filename.GetValue() )

        return dlg


    def _create_file_popup ( self ):
        """ Creates the correct type of file popup.
        """
        return PopupDirectory( control   = self.control,
                               file_name = self.str_value,
                               filter    = self.factory.filter,
                               height    = 300 )

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( CustomFileEditor ):
    """ Custom style of editor for directories, which displays a tree view of
        the file system.
    """

    #-- Public Methods ---------------------------------------------------------

    def get_style ( self ):
        """ Returns the basic style to use for the control.
        """
        return (wx.DIRCTRL_DIR_ONLY | wx.DIRCTRL_EDIT_LABELS)


    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        if self.control is not None:
            path = self.control.GetPath()
            if isdir( path ):
                self.value = path

#-------------------------------------------------------------------------------
#  'PopupDirectory' class:
#-------------------------------------------------------------------------------

class PopupDirectory ( PopupFile ):

    def get_style ( self ):
        """ Returns the basic style to use for the popup.
        """
        return (wx.DIRCTRL_DIR_ONLY | wx.DIRCTRL_EDIT_LABELS)


    def is_valid ( self, path ):
        """ Returns whether or not the path is valid.
        """
        return isdir( path )

#-- EOF ------------------------------------------------------------------------