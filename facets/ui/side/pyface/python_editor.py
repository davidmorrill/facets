"""
Defines the Qt4 toolkit specific implementation of a PythonEditor.  See the
IPythonEditor interface for the API documentation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from PySide \
    import QtCore, QtGui, Qsci

from facets.core_api \
    import Bool, Event, implements, Unicode

from facets.ui.pyface.i_python_editor \
    import IPythonEditor, MPythonEditor

from facets.ui.pyface.key_pressed_event \
    import KeyPressedEvent

from widget \
    import Widget

#-------------------------------------------------------------------------------
#  'PythonEditor' class:
#-------------------------------------------------------------------------------

class PythonEditor ( MPythonEditor, Widget ):
    """ The toolkit specific implementation of a PythonEditor.  See the
        IPythonEditor interface for the API documentation.
    """

    implements( IPythonEditor )

    #-- 'IPythonEditor' interface ----------------------------------------------

    dirty             = Bool( False )
    path              = Unicode
    show_line_numbers = Bool( True )

    #-- Events -----------------------------------------------------------------

    changed     = Event
    key_pressed = Event( KeyPressedEvent )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, parent, **facets ):
        """ Creates a new pager.
        """
        # Base class constructor:
        super( PythonEditor, self ).__init__( **facets )

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control( parent )

    #-- PythonEditor Interface -------------------------------------------------

    def load ( self, path = None ):
        """ Loads the contents of the editor.
        """
        if path is None:
            path = self.path

        # We will have no path for a new script:
        if len( path ) > 0:
            f = open( self.path, 'r' )
            text = f.read()
            f.close()

        else:
            text = ''

        self.control.setText( text )
        self.dirty = False


    def save ( self, path = None ):
        """ Saves the contents of the editor.
        """
        if path is None:
            path = self.path

        f = file( path, 'w' )
        f.write( self.control.text() )
        f.close()

        self.dirty = False


    def select_line ( self, lineno ):
        """ Selects the specified line.
        """
        llen = self.control.lineLength( lineno )
        if llen > 0:
            self.control.setSelection( lineno, 0, lineno, llen - 1 )

    #-- Facet Event Handlers ---------------------------------------------------

    def _path_set ( self ):
        """ Handle a change to path.
        """
        self._changed_path()

    #-- Private Methods --------------------------------------------------------

    def _create_control ( self, parent ):
        """ Creates the toolkit-specific control for the widget.
        """
        # Base-class constructor:
        self.control = stc = _Scintilla( self, parent )

        # Use the Python lexer with default settings:
        lexer = Qsci.QsciLexerPython( stc )
        stc.setLexer( lexer )

        # Set a monspaced font.  Use the (supposedly) same font and size as the
        # wx version:
        if sys.platform == 'win32':
            fsize = 10
        else:
            fsize = 12

        for sty in range( 128 ):
            if not lexer.description( sty ).isEmpty():
                f = lexer.font( sty )
                f.setFamily( 'courier new' )
                f.setPointSize( fsize )
                lexer.setFont( f, sty )

        # Mark the maximum line size:
        stc.setEdgeMode( Qsci.QsciScintilla.EdgeLine )
        stc.setEdgeColumn( 79 )

        # Display line numbers in the margin:
        if self.show_line_numbers:
            stc.setMarginLineNumbers( 1, True )
            stc.setMarginWidth( 1, 45 )
        else:
            stc.setMarginWidth( 1, 4 )
            stc.setMarginsBackgroundColor( QtCore.Qt.white )

        # Create 'tabs' out of spaces!
        stc.setIndentationsUseTabs( False )

        # One 'tab' is 4 spaces:
        stc.setTabWidth( 4 )

        # Line ending mode:
        stc.setEolMode( Qsci.QsciScintilla.EolUnix )

        stc.connect( stc, QtCore.SIGNAL( 'modificationChanged(bool)' ),
                     self._on_dirty_modified )
        stc.connect( stc, QtCore.SIGNAL( 'textChanged()' ),
                     self._on_text_modified )

        # Load the editor's contents:
        self.load()

        return stc


    def _on_dirty_modified ( self, dirty ):
        """ Called whenever a change is made to the dirty state of the
            document.
        """
        self.dirty = dirty


    def _on_text_modified ( self ):
        """ Called whenever a change is made to the text of the document.
        """
        self.changed = True

#-------------------------------------------------------------------------------
#  '_Scintilla' class:
#-------------------------------------------------------------------------------

class _Scintilla ( Qsci.QsciScintilla ):
    """ A thin wrapper around QScintilla to handle the key_pressed Event.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, editor, parent ):
        """ Initialise.
        """
        Qsci.QsciScintilla.__init__( self, parent )

        self.__editor = editor


    def focusOutEvent ( self, e ):
        """ Reimplemented to emit a signal for FacetsUI.
        """
        Qsci.QsciScintilla.focusOutEvent( self, e )

        self.emit( QtCore.SIGNAL( 'lostFocus' ) )


    def keyPressEvent ( self, e ):
        """ Reimplemented to trap key presses.
        """
        # Pyface doesn't seem to be Unicode aware.  Only keep the key code if
        # it corresponds to a single Latin1 character.
        kstr = e.text().toLatin1()

        if kstr.length() == 1:
            kcode = ord( kstr.at( 0 ) )
        else:
            kcode = 0

        mods = e.modifiers()

        self.__editor.key_pressed = KeyPressedEvent(
            alt_down     = ((mods & QtCore.Qt.AltModifier) ==
                             QtCore.Qt.AltModifier),
            control_down = ((mods & QtCore.Qt.ControlModifier) ==
                            QtCore.Qt.ControlModifier),
            shift_down   = ((mods & QtCore.Qt.ShiftModifier) ==
                            QtCore.Qt.ShiftModifier),
            key_code     = kcode,
            event        = QtGui.QKeyEvent( e )
        )

        Qsci.QsciScintilla.keyPressEvent( self, e )

#-- EOF ------------------------------------------------------------------------