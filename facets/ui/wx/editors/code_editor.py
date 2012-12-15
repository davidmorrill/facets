"""
Defines a wxPython specific implementation of a source code editor and factory
useful for tools such as debuggers.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
import wx.stc as stc

from facets.core_api \
    import Instance, Str, List, Int, Color, Enum, Event, Bool, FacetError

from facets.core.facet_base \
    import SequenceTypes

from facets.ui.key_bindings \
    import KeyBindings

from facets.ui.basic_editor_factory \
    import BasicEditorFactory

from facets.ui.pyface.api \
    import PythonEditor

from facets.ui.wx.constants \
    import OKColor, ErrorColor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Marker line constants:

# Marks a marked line:
MARK_MARKER = 0

# Marks a line matching the current search:
SEARCH_MARKER = 1

# Marks the currently selected line:
SELECTED_MARKER = 2

#-------------------------------------------------------------------------------
#  '_CodeEditor' class:
#-------------------------------------------------------------------------------

class _CodeEditor ( Editor ):
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

    # The calltip clicked event:
    calltip_clicked = Event

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory      = self.factory
        self._editor = editor  = PythonEditor( parent,
                                 show_line_numbers = factory.show_line_numbers )
        self.control = control = editor.control

        # There are a number of events which aren't well documented that look
        # to be useful in future implmentations, below are a subset of the
        # events that look interesting:
        #    EVT_STC_AUTOCOMP_SELECTION
        #    EVT_STC_HOTSPOT_CLICK
        #    EVT_STC_HOTSPOT_DCLICK
        #    EVT_STC_DOUBLECLICK
        #    EVT_STC_MARGINCLICK

        control.SetSize( wx.Size( 300, 124 ) )

        # Set up the events:
        wx.EVT_KILL_FOCUS( control, self.wx_update_object )
        stc.EVT_STC_CALLTIP_CLICK( control, control.GetId(),
                                   self._calltip_clicked )

        if factory.auto_scroll and ( factory.selected_line != '' ):
            wx.EVT_SIZE( control, self._update_selected_line )

        if factory.auto_set:
            editor.on_facet_set( self.update_object, 'changed',
                                 dispatch = 'ui' )

        if factory.key_bindings is not None:
            editor.on_facet_set( self.key_pressed, 'key_pressed',
                                 dispatch = 'ui' )

        if self.readonly:
            control.SetReadOnly( True )

        # Define the markers we use:
        control.MarkerDefine( MARK_MARKER, stc.STC_MARK_BACKGROUND,
                              background = factory.mark_color_ )
        control.MarkerDefine( SEARCH_MARKER, stc.STC_MARK_BACKGROUND,
                              background = factory.search_color_ )
        control.MarkerDefine( SELECTED_MARKER, stc.STC_MARK_BACKGROUND,
                              background = factory.selected_color_ )

        # Make sure the editor has been initialized:
        self.update_editor()

        # Set up any event listeners:
        self.sync_value( factory.mark_lines, 'mark_lines', 'from',
                         is_list = True )
        self.sync_value( factory.selected_line, 'selected_line', 'from' )
        self.sync_value( factory.selected_text, 'selected_text', 'to' )
        self.sync_value( factory.line, 'line' )
        self.sync_value( factory.column, 'column' )
        self.sync_value( factory.calltip_clicked, 'calltip_clicked' )

        # Check if we need to monitor the line or column position being changed:
        if (factory.line != '') or (factory.column != ''):
            stc.EVT_STC_UPDATEUI( control, control.GetId(),
                                  self._position_modified )

        self.set_tooltip()


    def wx_update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        self.update_object()
        event.Skip()


    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._locked:
            try:
                value = self.control.GetText()
                if isinstance( self.value, SequenceTypes ):
                    value = value.split()
                self.value = value
                self.control.SetBackgroundColour( OKColor )
                self.control.Refresh()
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
        if control.GetText() != new_value:
            readonly = control.GetReadOnly()
            control.SetReadOnly( False )
            l1  = control.GetFirstVisibleLine()
            pos = control.GetCurrentPos()
            control.SetText( new_value )
            control.GotoPos( pos )
            control.ScrollToLine( l1 )
            control.SetReadOnly( readonly )
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
        self.control.SetBackgroundColour( ErrorColor )
        self.control.Refresh()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self.factory.auto_set:
            self._editor.on_facet_set( self.update_object, 'changed',
                                       remove = True )

        if self.factory.key_bindings is not None:
            self._editor.on_facet_set( self.key_pressed, 'key_pressed',
                                       remove = True )

        wx.EVT_KILL_FOCUS( self.control, None )

        super( _CodeEditor, self ).dispose()

    #-- Facet Event Handlers ---------------------------------------------------

    def _calltip_clicked ( self, event ):
        self.calltip_clicked = True


    def _mark_lines_set ( self ):
        """ Handles the set of marked lines being changed.
        """
        lines   = self.mark_lines
        control = self.control
        lc      = control.GetLineCount()
        control.MarkerDeleteAll( MARK_MARKER )

        for line in lines:
            if 0 < line <= lc:
                control.MarkerAdd( line - 1, MARK_MARKER )

        control.Refresh()


    def _mark_lines_items_set ( self ):
        self._mark_lines_set()


    def _selected_line_set ( self ):
        """ Handles a change in which line is currently selected.
        """
        line    = self.selected_line
        control = self.control
        line    = max( 1, min( control.GetLineCount(), line ) ) - 1
        control.MarkerDeleteAll( SELECTED_MARKER )
        control.MarkerAdd( line, SELECTED_MARKER )
        control.GotoLine( line )
        if self.factory.auto_scroll:
            control.ScrollToLine( line - ( control.LinesOnScreen() / 2 ) )

        control.Refresh()


    def _line_set ( self, line ):
        if not self._locked:
            self.control.GotoLine( line - 1 )


    def _column_set ( self, column ):
        if not self._locked:
            control = self.control
            line    = control.LineFromPosition( control.GetCurrentPos() )
            control.GotoPos( control.PositionFromLine( line ) + column - 1 )

    #-- wx Event Handlers ------------------------------------------------------

    def _position_modified ( self, event ):
        """ Handles the cursor position being changed.
        """
        control      = self.control
        pos          = control.GetCurrentPos()
        line         = control.LineFromPosition( pos )
        self._locked = True
        self.line    = line + 1
        self.column  = pos - control.PositionFromLine( line ) + 1
        self._locked = False
        self.selected_text = control.GetSelectedText()

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
        return {
            'key_bindings': self.factory.key_bindings
        }

#-------------------------------------------------------------------------------
#  'CodeEditor' class:
#-------------------------------------------------------------------------------

class CodeEditor ( BasicEditorFactory ):
    """ wxPython editor factory for code editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to create:
    klass = _CodeEditor

    # Object facet containing list of line numbers to mark (optional):
    mark_lines = Str

    # Background color for marking lines:
    mark_color = Color( 0xECE9D8 )

    # Object facet containing the currently selected line (optional):
    selected_line = Str

    # Object facet containing the currently selected text (optional):
    selected_text = Str

    # Background color for selected lines:
    selected_color = Color( 0xA4FFFF )

    # Where should the search toolbar be placed?
    search = Enum( 'top', 'bottom', 'none' )

    # Background color for lines that match the current search:
    search_color = Color( 0xFFFF94 )

    # The current line:
    line = Str

    # The current column:
    column = Str

    # Should code folding be enabled?
    foldable = Bool( True )

    # Should line numbers be displayed in the margin?
    show_line_numbers = Bool( True )

    # Is user input set on every change?
    auto_set = Bool( True )

    # Should the editor auto-scroll when a new **selected_line** value is set?
    auto_scroll = Bool( True )

    # The optional key bindings associated with the editor:
    key_bindings = Instance( KeyBindings )

    # The calltip clicked event:
    calltip_clicked = Str

#-- EOF ------------------------------------------------------------------------