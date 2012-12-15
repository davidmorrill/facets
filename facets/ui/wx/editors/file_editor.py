"""
Defines file editors and the file editor factoryfor the wxPython user
    interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from os.path \
    import abspath, splitext, isfile, exists

from facets.api \
    import List, Str, Event, Bool, Int, Any, on_facet_set, FacetError, View, \
           Group

from facets.ui.editors.text_editor \
    import TextEditor, SimpleEditor as SimpleTextEditor

from facets.ui.wx.helper \
    import FacetsUIPanel, PopupControl

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Wildcard filter:
filter_facet = List( Str )

#-------------------------------------------------------------------------------
#  'FileEditor' class:
#-------------------------------------------------------------------------------

class FileEditor ( TextEditor ):
    """ wxPython editor factory for file editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Wildcard filter to apply to the file dialog:
    filter = filter_facet

    # Optional extended facet name of the facet containing the list of filters:
    filter_name = Str

    # Should file extension be truncated?
    truncate_ext = Bool( False )

    # Can the user select directories as well as files?
    allow_dir = Bool( False )

    # Is user input set on every keystroke? (Overrides the default) ('simple'
    # style only):
    auto_set = False

    # Is user input set when the Enter key is pressed? (Overrides the default)
    # ('simple' style only):
    enter_set = True

    # The number of history entries to maintain:
    entries = Int( 0 )

    # Optional extended facet name used to notify the editor when the file
    # system view should be reloaded ('custom' style only):
    reload_name = Str

    # Optional extended facet name used to notify when the user double-clicks
    # an entry in the file tree view:
    dclick_name = Str

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View( [ [ '<options>',
                        'truncate_ext{Automatically truncate file extension?}',
                        '|options:[Options]>' ],
                          [ 'filter', '|[Wildcard filters]<>' ] ] )

    extras = Group()

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

class SimpleEditor ( SimpleTextEditor ):
    """ Simple style of file editor, consisting of a text field and a **Browse**
        button that opens a file-selection dialog box. The user can also drag
        and drop a file onto this control.
    """

    #-- Class Constants --------------------------------------------------------

    # Is the editor implementation GUI toolkit neutral?
    is_toolkit_neutral = False

    #-- Facet Definitions ------------------------------------------------------

    # The history control (used if the factory 'entries' > 0):
    history = Any

    # The popup file control (an Instance( PopupFile )):
    popup = Any

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = panel = FacetsUIPanel( parent, -1 )
        sizer        = wx.BoxSizer( wx.HORIZONTAL )
        factory      = self.factory

        if factory.entries > 0:
            from facets.ui.controls.history_control import HistoryControl

            self.history = HistoryControl( entries  = factory.entries,
                                           auto_set = factory.auto_set )
            control      = self.history.create_control( panel )()
            pad          = 3
            button       = wx.Button( panel, -1, '...',
                                      size = wx.Size( 28, -1 ) )
        else:
            if factory.enter_set:
                control = wx.TextCtrl( panel, -1, '',
                                       style = wx.TE_PROCESS_ENTER )
                wx.EVT_TEXT_ENTER( panel, control.GetId(), self.update_object )
            else:
                control = wx.TextCtrl( panel, -1, '' )

            wx.EVT_KILL_FOCUS( control, self.update_object )

            if factory.auto_set:
                wx.EVT_TEXT( panel, control.GetId(), self.update_object )

            button = wx.Button( panel, -1, 'Browse...' )
            pad    = 8

        self._file_name = control
        sizer.Add( control, 1, wx.EXPAND | wx.ALIGN_CENTER )
        sizer.Add( button,  0, wx.LEFT   | wx.ALIGN_CENTER, pad )
        wx.EVT_BUTTON( panel, button.GetId(), self.show_file_dialog )
        panel.SetDropTarget( FileDropTarget( self ) )
        panel.SetSizerAndFit( sizer )
        self._button = button

        self.set_tooltip( control )


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        panel = self.control
        wx.EVT_BUTTON( panel, self._button.GetId(), None )
        self._button = None

        if self.history is not None:
            self.history.dispose()
            self.history = None
        else:
            factory = self.factory
            control, self._file_name = self._file_name, None
            wx.EVT_KILL_FOCUS( control,                None )
            wx.EVT_TEXT_ENTER( panel, control.GetId(), None )
            wx.EVT_TEXT(       panel, control.GetId(), None )

        super( SimpleEditor, self ).dispose()


    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        self._update( self._file_name.GetValue() )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self.history is not None:
            self._no_update    = True
            self.history.value = self.str_value
            self._no_update    = False
        else:
            self._file_name.SetValue( self.str_value )


    def show_file_dialog ( self, event ):
        """ Displays the pop-up file dialog.
        """
        if self.history is not None:
            self.popup = self._create_file_popup()
        else:
            dlg       = self._create_file_dialog()
            rc        = ( dlg.ShowModal() == wx.ID_OK )
            file_name = abspath( dlg.GetPath() )
            dlg.Destroy()
            if rc:
                if self.factory.truncate_ext:
                    file_name = splitext( file_name )[ 0 ]

                self.value = file_name
                self.update_editor()


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self._file_name

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'history:value' )
    def _history_value_modified ( self, value ):
        """ Handles the history 'value' facet being changed.
        """
        if not self._no_update:
            self._update( value )


    @on_facet_set( 'popup:value' )
    def _popup_value_modified ( self, file_name ):
        """ Handles the popup value being changed.
        """
        if self.factory.truncate_ext:
            file_name = splitext( file_name )[ 0 ]

        self.value      = file_name
        self._no_update = True
        self.history.set_value( self.str_value )
        self._no_update = False


    @on_facet_set( 'popup:closed' )
    def _popup_closed_modified ( self ):
        """ Handles the popup control being closed.
        """
        self.popup = None

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if self.history is not None:
            self.history.history = \
                prefs.get( 'history', [] )[ : self.factory.entries ]


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        if self.history is not None:
            return { 'history': self.history.history[:] }

        return None

    #-- Private Methods --------------------------------------------------------

    def _create_file_dialog ( self ):
        """ Creates the correct type of file dialog.
        """
        if len( self.factory.filter ) > 0:
            wildcard = '|'.join( self.factory.filter[ : ] )
        else:
            wildcard = 'All Files (*.*)|*.*'

        dlg = wx.FileDialog( self.control,
                             message  = 'Select a File',
                             wildcard = wildcard )

        dlg.SetFilename( self._get_value() )

        return dlg


    def _create_file_popup ( self ):
        """ Creates the correct type of file popup.
        """
        return PopupFile( control   = self.control,
                          file_name = self.str_value,
                          filter    = self.factory.filter,
                          height    = 300 )


    def _update ( self, file_name ):
        """ Updates the editor value with a specified file name.
        """
        try:
            if self.factory.truncate_ext:
                file_name = splitext( file_name )[ 0 ]

            self.value = file_name
        except FacetError, excp:
            pass


    def _get_value ( self ):
        """ Returns the current file name from the edit control.
        """
        if self.history is not None:
            return self.history.value

        return self._file_name.GetValue()

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleTextEditor ):
    """ Custom style of file editor, consisting of a file system tree view.
    """

    #-- Class Constants --------------------------------------------------------

    # Is the editor implementation GUI toolkit neutral?
    is_toolkit_neutral = False

    #-- Facet Definitions ------------------------------------------------------

    # Is the file editor scrollable? This value overrides the default.
    scrollable = True

    # Wildcard filter to apply to the file dialog:
    filter = filter_facet

    # Event fired when the file system view should be rebuilt:
    reload = Event

    # Event fired when the user double-clicks a file:
    dclick = Event

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        style   = self.get_style()
        factory = self.factory
        if (len( factory.filter ) > 0) or (factory.filter_name != ''):
            style |= wx.DIRCTRL_SHOW_FILTERS

        self.control = wx.GenericDirCtrl( parent, style = style )
        self._tree   = tree = self.control.GetTreeCtrl()
        id           = tree.GetId()
        wx.EVT_TREE_SEL_CHANGED(    tree, id, self.update_object )
        wx.EVT_TREE_ITEM_ACTIVATED( tree, id, self._on_dclick )

        self.filter = factory.filter
        self.sync_value( factory.filter_name, 'filter', 'from', is_list = True )
        self.sync_value( factory.reload_name, 'reload', 'from' )
        self.sync_value( factory.dclick_name, 'dclick', 'to' )

        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        tree, self._tree = self._tree, None
        id = tree.GetId()

        wx.EVT_TREE_SEL_CHANGED(    tree, id, None )
        wx.EVT_TREE_ITEM_ACTIVATED( tree, id, None )

        super( CustomEditor, self ).dispose()


    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        if self.control is not None:
            path = self.control.GetPath()
            if self.factory.allow_dir or isfile( path ):
                if self.factory.truncate_ext:
                    path = splitext( path )[ 0 ]

                self.value = path


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if exists( self.str_value ):
            self.control.SetPath( self.str_value )


    def get_style ( self ):
        """ Returns the basic style to use for the control.
        """
        return wx.DIRCTRL_EDIT_LABELS


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self._tree

    #-- Facet Event Handlers ---------------------------------------------------

    def _filter_set ( self ):
        """ Handles the 'filter' facet being changed.
        """
        self.control.SetFilter( '|'.join( self.filter[ : ] ) )


    def _reload_set ( self ):
        """ Handles the 'reload' facet being changed.
        """
        self.control.ReCreateTree()

    #-- Control Event Handlers -------------------------------------------------

    def _on_dclick ( self, event ):
        """ Handles the user double-clicking on a file name.
        """
        self.dclick = True

#-------------------------------------------------------------------------------
#  'PopupFile' class:
#-------------------------------------------------------------------------------

class PopupFile ( PopupControl ):

    #-- Facet Definitions ------------------------------------------------------

    # The initially specified file name:
    file_name = Str

    # The file name filter to support:
    filter = filter_facet

    # Override of PopupControl facet to make the popup resizable:
    resizable = True

    #-- PopupControl Method Overrides ------------------------------------------

    def create_control ( self, parent ):
        """ Creates the file control and gets it ready for use.
        """
        style = self.get_style()
        if len( self.filter ) > 0:
            style |= wx.DIRCTRL_SHOW_FILTERS

        self._files = files = wx.GenericDirCtrl( parent, style = style,
                                          filter = '|'.join( self.filter ) )
        files.SetPath( self.file_name )
        self._tree  = tree = files.GetTreeCtrl()
        wx.EVT_TREE_SEL_CHANGED( tree, tree.GetId(), self._select_file )

    #-- Public Methods ---------------------------------------------------------

    def dispose ( self ):
        wx.EVT_TREE_SEL_CHANGED( self._tree, self._tree.GetId(), None )
        self._tree = self._files = None


    def get_style ( self ):
        """ Returns the base style for this type of popup.
        """
        return wx.DIRCTRL_EDIT_LABELS


    def is_valid ( self, path ):
        """ Returns whether or not the path is valid.
        """
        return isfile( path )

    #-- Private Methods --------------------------------------------------------

    def _select_file ( self, event ):
        """ Handles a file being selected in the file control.
        """
        path = self._files.GetPath()

        # We have to make sure the selected path is different than the original
        # path because when a filter is changed we get called with the currently
        # selected path, even though no file was actually selected by the user.
        # So we only count it if it is a different path.
        #
        # We also check the last character of the path, because under Windows
        # we get a call when the filter is changed for each drive letter. If the
        # drive is not available, it can take the 'isfile' call a long time to
        # time out, so we attempt to ignore them by doing a quick test to see
        # if it could be a valid file name, and ignore it if it is not:
        if ((path != abspath( self.file_name )) and
            (path[-1:] not in '/\\')            and
            self.is_valid( path )):
            self.value = path

#-------------------------------------------------------------------------------
#  'FileDropTarget' class:
#-------------------------------------------------------------------------------

class FileDropTarget ( wx.FileDropTarget ):
    """ A target for a drag and drop operation, which accepts a file.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, editor ):
        wx.FileDropTarget.__init__( self )
        self.editor = editor


    def OnDropFiles ( self, x, y, file_names ):
        self.editor.value = file_names[-1]
        self.editor.update_editor()

        return True

#-- EOF ------------------------------------------------------------------------