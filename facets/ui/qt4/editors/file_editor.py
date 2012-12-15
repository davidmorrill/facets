"""
Defines file editors and the file editor factory for the PyQt user
interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import splitext, isfile, exists, normpath

from PyQt4.QtCore \
    import QDir, SIGNAL

from PyQt4.QtGui \
    import QDialog, QFileDialog, QDirModel, QTreeView

from facets.api \
    import List, Str, Any, Event, Bool, Int, Unicode, FacetError, View, Group, \
           Item, toolkit, on_facet_set

from facets.ui.editors.text_editor \
    import TextEditor, SimpleEditor as SimpleTextEditor

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Wildcard filter:
filter_facet = List( Unicode )

#-------------------------------------------------------------------------------
#  'FileEditor' class:
#-------------------------------------------------------------------------------

class FileEditor ( TextEditor ):
    """ PyQt editor factory for file editors.
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
    # FIXME: add support
    entries = Int( 10 )

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

    #-- Facet Definitions ------------------------------------------------------

    # The history control (used if the factory 'entries' > 0):
    history = Any

    # The popup file control (an Instance( PopupFile )):
    popup = Any

    # The value assigned using the popup file control:
    popup_file_name = Str

    # The ThemedButton control used when history entries are used:
    themed_button = Any

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        tk              = toolkit()
        self.adapter    = control = tk.create_panel( parent )
        control.layout  = layout  = tk.create_box_layout( False )
        factory         = self.factory
        if factory.entries > 0:
            from facets.ui.controls.history_control import HistoryControl
            from facets.ui.controls.themed_button   import ThemedButton

            pad          = 3
            self.history = HistoryControl(
                entries  = factory.entries,
                auto_set = factory.auto_set
            )
            file_name          = self.history.create_control( control )
            self.themed_button = ThemedButton( image  = '@icons2:Folder',
                                               parent = control )
            button             = self.themed_button()
        else:
            pad       = 8
            file_name = tk.create_text_input( control )
            if factory.auto_set:
                file_name.set_event_handler( text_change = self.update_object )
            else:
                # Assume 'enter_set' is set, otherwise the value will never get
                # updated:
                file_name.set_event_handler( text_enter = self.update_object )

            button = tk.create_button( control, 'Browse...' )
            button.set_event_handler( clicked = self.show_file_dialog )

        self._file_name       = file_name
        file_name.size_policy = ( 'expanding', 'fixed' )
        layout.add( file_name )

        self._button = button
        layout.add( button, left = pad )

        self.set_tooltip( file_name )
        self.set_tooltip( button )


    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        self._update( self._file_name.value )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self._file_name.value = self.str_value


    def dispose ( self ):
        """ Disposes of the editor.
        """
        factory = self.factory
        if factory.entries == 0:
            self._button.unset_event_handler( clicked = self.show_file_dialog )
            if factory.auto_set:
                self._file_name.unset_event_handler(
                    text_change = self.update_object )
            else:
                self._file_name.unset_event_handler(
                    text_enter = self.update_object )

        # Skip our parent class 'dispose', since we use an incompatible
        # implementation:
        super( SimpleTextEditor, self ).dispose()


    @on_facet_set( 'themed_button:clicked' )
    def show_file_dialog ( self, event ):
        """ Displays the pop-up file dialog.
        """
        if self.history is not None:
            self.popup_file_name = self.str_value
            self.edit_facets(
                parent = self._file_name,
                view   = View(
                    Item( 'popup_file_name',
                          style      = 'custom',
                          show_label = False,
                          editor     = self._popup_editor()
                    ),
                    kind   = 'popup',
                    height = 300
                )
            )
        else:
            # We don't used the canned functions because we don't know how the
            # file name is to be used (i.e. an existing one to be opened or a
            # new one to be created):
            dlg = self._create_file_dialog()

            if dlg.exec_() == QDialog.Accepted:
                files = dlg.selectedFiles()

                if len( files ) > 0:
                    file_name = normpath( unicode( files[0] ) )

                    if self.factory.truncate_ext:
                        file_name = splitext( file_name )[0]

                    self.value = file_name
                    self.update_editor()


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self._file_name

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'history:value' )
    def _history_modified ( self ):
        self._update( self.history.value )


    def _popup_file_name_set ( self, file_name ):
        """ Handles the 'popup_file_name' facet being changed.
        """
        self.history.set_value( file_name )

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
        dlg = QFileDialog( self.control.parentWidget() )
        dlg.selectFile( self._file_name.value )

        if len( self.factory.filter ) > 0:
            dlg.setFilters( self.factory.filter )

        return dlg


    def _popup_editor ( self ):
        """ Returns the editor to use when creating a pop-up editor.
        """
        return FileEditor()


    def _update ( self, file_name ):
        """ Updates the editor value with a specified file name.
        """
        if self.factory is not None:
            try:
                file_name = unicode( file_name )
                if self.factory.truncate_ext:
                    file_name = splitext( file_name )[0]

                self.value = file_name
            except FacetError:
                pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleTextEditor ):
    """ Custom style of file editor, consisting of a file system tree view.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the file editor scrollable? This value overrides the default.
    scrollable = True

    # Wildcard filter to apply to the file dialog:
    filter = filter_facet

    # Event fired when the file system view should be rebuilt:
    reload = Event

    # Event fired when the user double-clicks a file:
    dclick = Event

    # The Qt model filter flags to use:
    filters = Any( QDir.AllEntries | QDir.NoDotAndDotDot )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = _TreeView( self )
        self._model  = model = QDirModel()
        model.setFilter( self.filters )
        self.control.setModel( model )
        self.control.setColumnWidth( 0, 300 )

        factory     = self.factory
        self.filter = factory.filter
        self.sync_value( factory.filter_name, 'filter', 'from', is_list = True )
        self.sync_value( factory.reload_name, 'reload', 'from' )
        self.sync_value( factory.dclick_name, 'dclick', 'to' )

        self.set_tooltip()


    def update_object ( self, idx ):
        """ Handles the user changing the contents of the edit control.
        """
        if self.control is not None:
            path = unicode( self._model.filePath( idx ) )

            if self.factory.allow_dir or isfile( path ):
                if self.factory.truncate_ext:
                    path = splitext( path )[0]

                self.value = path


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if exists( self.str_value ):
            self.control.setCurrentIndex( self._model.index( self.str_value ) )


    def _on_dclick ( self, idx ):
        """ Handles the user double-clicking on a file name.
        """
        self.dclick = True

    #-- Facet Event Handlers ---------------------------------------------------

    def _filter_set ( self ):
        """ Handles the 'filter' facet being changed.
        """
        self._model.setNameFilters( self.filter )


    def _reload_set ( self ):
        """ Handles the 'reload' facet being changed.
        """
        self._model.refresh()

#-------------------------------------------------------------------------------
#  '_TreeView' class:
#-------------------------------------------------------------------------------

class _TreeView ( QTreeView ):
    """ This is an internal class needed because QAbstractItemView (for some
        strange reason) doesn't provide a signal when the current index
        changes.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, editor ):

        QTreeView.__init__( self )

        self._editor = editor
        self.connect( self, SIGNAL( 'doubleClicked(QModelIndex)' ),
                      editor._on_dclick )


    def currentChanged ( self, curr, prev ):
        """ Reimplemented to tell the editor when the current index has
            changed.
        """
        QTreeView.currentChanged( self, curr, prev )

        self._editor.update_object( curr )

#-- EOF ------------------------------------------------------------------------