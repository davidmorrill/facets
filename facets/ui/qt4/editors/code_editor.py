"""
Defines a source code editor and code editor factory, for the PyQt user
interface toolkit, useful for tools such as debuggers.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
    import SIGNAL

from PyQt4.Qsci \
    import QsciScintilla

from facets.api \
    import Instance, Str, List, Int, Color, Enum, Event, Bool, FacetError, \
           EditorFactory

from facets.core.facet_base \
    import SequenceTypes

from facets.ui.colors \
    import SelectionColor

from facets.ui.key_bindings \
    import KeyBindings

from facets.ui.pyface.api \
    import PythonEditor

from facets.ui.qt4.constants \
    import OKColor, ErrorColor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

#-- Marker Line Constants ------------------------------------------------------

# Marks a marked line:
MARK_MARKER = 0

# Marks a line matching the current search:
SEARCH_MARKER = 1

# Marks the currently selected line:
SELECTED_MARKER = 2

#-------------------------------------------------------------------------------
#  'CodeEditor' class:
#-------------------------------------------------------------------------------

class CodeEditor ( EditorFactory ):
    """ PyQt editor factory for code editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Object facet containing list of line numbers to mark (optional):
    mark_lines = Str

    # Background color for marking lines:
    mark_color = Color( 0xECE9D8 )

    # Object facet containing the currently selected line (optional):
    selected_line = Str

    # Object facet containing the currently selected text (optional):
    selected_text = Str

    # Background color for selected lines:
    selected_color = Color( SelectionColor )

    # Where should the search toolbar be placed?
    search = Enum( 'top', 'bottom', 'none' )

    # Background color for lines that match the current search:
    search_color = Color( 0xFFFF94 )

    # Current line:
    line = Str

    # Current column:
    column = Str

    # Should code folding be enabled?
    foldable = Bool( True )

    # Should line numbers be displayed in the margin?
    show_line_numbers = Bool( True )

    # Is user input set on every change?
    auto_set = Bool( True )

    # Should the editor auto-scroll when a new **selected_line** value is set?
    auto_scroll = Bool( True )

    # Optional key bindings associated with the editor:
    key_bindings = Instance( KeyBindings )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SourceEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             readonly    = False )

    def readonly_editor ( self, ui, object, name, description ):
        return SourceEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             readonly    = True )

#-------------------------------------------------------------------------------
#  'SourceEditor' class:
#-------------------------------------------------------------------------------

class SourceEditor ( Editor ):
    """ Editor for source code, which displays a PyFace PythonEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The code editor is scrollable. This value overrides the default:
    scrollable = True

    # Is the editor read only?
    readonly = Bool( False )

    # The currently selected line:
    selected_line = Int

    # The currently selected text:
    selected_text = Str

    # The list of line numbers to mark:
    mark_lines = List( Int )

    # The current line number:
    line = Event

    # The current column:
    column = Event

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        self._editor = editor = PythonEditor(
            parent, show_line_numbers = factory.show_line_numbers
        )
        self.control = control = editor.control

        control.connect( control, SIGNAL( 'lostFocus' ), self.update_object )

        if factory.auto_set:
            editor.on_facet_set(
                self.update_object, 'changed', dispatch = 'ui'
            )

        if factory.key_bindings is not None:
            editor.on_facet_set(
                self.key_pressed, 'key_pressed', dispatch = 'ui'
            )

        if self.readonly:
            control.setReadOnly( True )

        # Define the markers we use:
        control.markerDefine( QsciScintilla.Background, MARK_MARKER )
        control.setMarkerBackgroundColor( factory.mark_color_, MARK_MARKER )

        control.markerDefine( QsciScintilla.Background, SEARCH_MARKER )
        control.setMarkerBackgroundColor( factory.search_color_, SEARCH_MARKER )

        control.markerDefine( QsciScintilla.Background, SELECTED_MARKER )
        control.setMarkerBackgroundColor(
            factory.selected_color_, SELECTED_MARKER
        )

        # Make sure the editor has been initialized:
        self.update_editor()

        # Set up any event listeners:
        self.sync_value(
            factory.mark_lines, 'mark_lines', 'from', is_list = True
        )
        self.sync_value( factory.selected_line, 'selected_line', 'from' )
        self.sync_value( factory.selected_text, 'selected_text', 'to' )
        self.sync_value( factory.line, 'line' )
        self.sync_value( factory.column, 'column' )

        # Check if we need to monitor the line or column position being changed:
        if (factory.line != '') or (factory.column != ''):
            control.connect(
                control,
                SIGNAL( 'cursorPositionChanged(int, int)' ),
                self._position_modified
            )

        self.set_tooltip()


    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        if (not self._locked) and (self.control is not None):
            try:
                value = unicode( self.control.text() )
                if isinstance( self.value, SequenceTypes ):
                    value = value.split()

                self.value = value
                self.control.lexer().setPaper( OKColor )
            except FacetError, excp:
                pass


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self._locked = True
        new_value    = self.value
        if isinstance( new_value, SequenceTypes ):
            new_value = '\n'.join( [ line.rstrip() for line in new_value ] )

        control = self.control
        if control.text() != new_value:
            control.setReadOnly( False )
            vsb          = control.verticalScrollBar()
            l1           = vsb.value()
            line, column = control.getCursorPosition()
            control.setText( new_value )
            control.setCursorPosition( line, column )
            vsb.setValue( l1 )
            control.setReadOnly( self.readonly )
            self._mark_lines_set()
            self._selected_line_set()

        self._locked = False


    def key_pressed ( self, event ):
        """ Handles a key being pressed within the editor.
        """
        self.factory.key_bindings.do( event.event, self.ui.handler,
                                      self.ui.info )


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        if not self.readonly:
            self.control.lexer().setPaper( ErrorColor )


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self.factory.auto_set:
            self._editor.on_facet_set( self.update_object, 'changed',
                                       remove = True )

        if self.factory.key_bindings is not None:
            self._editor.on_facet_set( self.key_pressed, 'key_pressed',
                                       remove = True )

        super( SourceEditor, self ).dispose()

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if self.factory.key_bindings is not None:
            key_bindings = prefs.get( 'key_bindings' )
            if key_bindings is not None:
                self.factory.key_bindings.merge( key_bindings )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return { 'key_bindings': self.factory.key_bindings }

    #-- Facet Event Handlers ---------------------------------------------------

    def _mark_lines_set ( self ):
        """ Handles the set of marked lines being changed.
        """
        lines   = self.mark_lines
        control = self.control
        lc      = control.lines()
        control.markerDeleteAll( MARK_MARKER )
        for line in lines:
            if 0 < line <= lc:
                control.markerAdd( line - 1, MARK_MARKER )


    def _mark_lines_items_set ( self ):
        self._mark_lines_set()


    def _selected_line_set ( self ):
        """ Handles a change in which line is currently selected.
        """
        line    = self.selected_line
        control = self.control
        line    = max( 1, min( control.lines(), line ) ) - 1
        control.markerDeleteAll( SELECTED_MARKER )
        control.markerAdd( line, SELECTED_MARKER )
        _, column = control.getCursorPosition()
        control.setCursorPosition( line, column )
        if self.factory.auto_scroll:
            control.ensureLineVisible( line )


    def _line_set ( self, line ):
        if not self._locked:
            _, column = self.control.getCursorPosition()
            self.control.setCursorPosition( line - 1, column )


    def _column_set ( self, column ):
        if not self._locked:
            line, _ = self.control.getCursorPosition()
            self.control.setCursorPosition( line, column - 1 )

    #-- Qt Event Handlers ------------------------------------------------------

    def _position_modified ( self, line, column ):
        """ Handles the cursor position being changed.
        """
        self._locked       = True
        self.line          = line   + 1
        self.column        = column + 1
        self._locked       = False
        self.selected_text = unicode( self.control.selectedText() )

#-- EOF ------------------------------------------------------------------------