"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

import sys
import code

from PySide.QtCore \
    import QCoreApplication, Qt

from PySide.QtGui \
    import QTextEdit, QTextOption, QTextCursor, QLayout, QKeySequence, \
           QApplication

from facets.core_api \
    import Event, implements

from facets.lib.util.clean_strings \
    import python_name

from facets.ui.side.adapters.drag \
    import PyMimeData

from facets.ui.pyface.i_python_shell \
    import IPythonShell, MPythonShell

from facets.ui.pyface.key_pressed_event \
    import KeyPressedEvent

from widget \
    import Widget

#-------------------------------------------------------------------------------
#  'PythonShell' class:
#-------------------------------------------------------------------------------

class PythonShell ( MPythonShell, Widget ):
    """ The toolkit specific implementation of a PythonShell.  See the
        IPythonShell interface for the API documentation.
    """

    implements( IPythonShell )

    #-- IPythonShell Interface -------------------------------------------------

    command_executed = Event
    key_pressed      = Event( KeyPressedEvent )

    #-- object Interface -------------------------------------------------------

    # FIXME v3: Either make this API consistent with other Widget sub-classes
    # or make it a sub-class of HasFacets.
    def __init__ ( self, parent, **facets ):
        """ Creates a new pager.
        """
        # Base class constructor.
        super( PythonShell, self ).__init__( **facets )

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control( parent() )

        # Set up to be notified whenever a Python statement is executed:
        self.control.exec_callback = self._on_command_executed

    #-- IPythonShell Interface -------------------------------------------------

    def interpreter ( self ):
        return self.control.interpreter

    def execute_command ( self, command, hidden = True ):
        self.control.run( command, hidden )

    #-- Protected IWidget Interface --------------------------------------------

    def _create_control ( self, parent ):
        # FIXME v3: Note that we don't (yet) support the zoom(?) of the wx
        # version.
        return PyShell( parent )

#-------------------------------------------------------------------------------
#  'PyShell' class:
#-------------------------------------------------------------------------------

class PyShell ( QTextEdit ):
    """ A simple GUI Python shell until we do something more sophisticated.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, parent = None ):
        """ Initialise the instance.
        """
        if isinstance( parent, QLayout ):
            parent = None

        QTextEdit.__init__( self, parent )

        self.setAcceptDrops( True )
        self.setAcceptRichText( False )
        self.setWordWrapMode( QTextOption.WrapAnywhere )

        self.interpreter = code.InteractiveInterpreter()

        self.exec_callback = None

        ### PYSIDE: self._line        = QString()
        self._line        = ''
        self._lines       = []
        self._more        = False
        self.history      = []
        self.historyIndex = 0
        self._reading     = False
        self._point       = 0

        # Interpreter prompts.
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "

        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "

        # Interpreter banner:
        self.write( 'Python %s on %s.\n' % ( sys.version, sys.platform ) )
        self.write( 'Type "copyright", "credits" or "license" for more '
                    'information.\n' )
        self.write( sys.ps1 )


    def flush ( self ):
        """ Emulate a file object.
        """
        pass


    def isatty ( self ):
        """ Emulate a file object.
        """
        return 1


    def readline ( self ):
        """ Emulate a file object.
        """
        self._reading = True
        self._clear_line()
        self.moveCursor( QTextCursor.EndOfLine )

        while self._reading:
            QCoreApplication.processEvents()

        if self._line.length():
            return str( self._line )

        return '\n'


    def write ( self, text ):
        """ Emulate a file object.
        """
        self.insertPlainText( text )
        self.ensureCursorVisible()


    def writelines ( self, text ):
        """ Emulate a file object.
        """
        map( self.write, text )


    def run ( self, command, hidden = False ):
        """ Run a (possibly partial) command without displaying anything.
        """
        self._lines.append( command )
        source = '\n'.join( self._lines )

        if not hidden:
            self.write( source + '\n' )

        # Save the current std* and point them here:
        old_stdin, old_stdout, old_stderr = sys.stdin, sys.stdout, sys.stderr
        sys.stdin = sys.stdout = sys.stderr = self

        self._more = self.interpreter.runsource( source )

        # Restore std* unless the executed changed them:
        if sys.stdin is self:
            sys.stdin = old_stdin

        if sys.stdout is self:
            sys.stdout = old_stdout

        if sys.stderr is self:
            sys.stderr = old_stderr

        if not self._more:
            self._lines = []

            if self.exec_callback:
                self.exec_callback()

        if not hidden:
            self.historyIndex = 0
            ### PYSIDE: self.history.append( QString( command ) )
            self.history.append( command )

            self._clear_line()

            if self._more:
                self.write( sys.ps2 )
            else:
                self.write( sys.ps1 )


    def dragEnterEvent ( self, e ):
        """ Handle a drag entering the widget.
        """
        if self._dragged_object( e ) is not None:
            # Make sure the users knows we will only do a copy.
            e.setDropAction( Qt.CopyAction )
            e.accept()


    def dragMoveEvent ( self, e ):
        """ Handle a drag moving across the widget.
        """
        if self._dragged_object( e ) is not None:
            # Make sure the users knows we will only do a copy.
            e.setDropAction( Qt.CopyAction )
            e.accept()


    def dropEvent ( self, e ):
        """ Handle a drop on the widget.
        """
        obj = self._dragged_object( e )
        if obj is None:
            return

        # If we can't create a valid Python identifier for the name of an
        # object we use this instead:
        name = 'dragged'

        if hasattr( obj, 'name' ) \
           and isinstance( obj.name, basestring ) and len( obj.name ) > 0:
            py_name = python_name( obj.name )

            # Make sure that the name is actually a valid Python identifier:
            try:
                if eval( py_name, { py_name : True } ):
                    name = py_name
            except:
                pass

        self.interpreter.locals[ name ] = obj
        self.run( name )
        self.setFocus()

        e.setDropAction( Qt.CopyAction )
        e.accept()


    @staticmethod
    def _dragged_object ( e ):
        """Return the Python object being dragged or None if there isn't one.
        """
        md = e.mimeData()

        if isinstance( md, PyMimeData ):
            obj = md.instance()
        else:
            obj = None

        return obj


    def keyPressEvent ( self, e ):
        """ Handle user input a key at a time.
        """
        text = e.text()

        if text.length() and (32 <= ord( text.toAscii()[0] ) < 127):
            self._insert_text( text )

            return

        key = e.key()

        if e.matches( QKeySequence.Copy ):
            text = self.textCursor().selectedText()
            if not text.isEmpty():
                QApplication.clipboard().setText( text )
        elif e.matches( QKeySequence.Paste ):
            self._insert_text( QApplication.clipboard().text() )
        elif key == Qt.Key_Backspace:
            if self._point:
                cursor = self.textCursor()
                cursor.deletePreviousChar()
                self.setTextCursor( cursor )

                self._point -= 1
                self._line.remove( self._point, 1 )
        elif key == Qt.Key_Delete:
            cursor = self.textCursor()
            cursor.deleteChar()
            self.setTextCursor( cursor )

            self._line.remove( self._point, 1 )
        elif key in ( Qt.Key_Return, Qt.Key_Enter ):
            self.write( '\n' )
            if self._reading:
                self._reading = False
            else:
                self.run( str( self._line ) )
        elif key == Qt.Key_Tab:
            self._insert_text( text )
        elif e.matches( QKeySequence.MoveToPreviousChar ):
            if self._point:
                self.moveCursor( QTextCursor.Left )
                self._point -= 1
        elif e.matches( QKeySequence.MoveToNextChar ):
            if self._point < self._line.length():
                self.moveCursor( QTextCursor.Right )
                self._point += 1
        elif e.matches( QKeySequence.MoveToStartOfLine ):
            while self._point:
                self.moveCursor( QTextCursor.Left )
                self._point -= 1
        elif e.matches( QKeySequence.MoveToEndOfLine ):
            self.moveCursor( QTextCursor.EndOfBlock )
            self._point = self._line.length()
        elif e.matches( QKeySequence.MoveToPreviousLine ):
            if len( self.history ):
                if self.historyIndex == 0:
                    self.historyIndex = len( self.history )
                self.historyIndex -= 1
                self._recall()
        elif e.matches( QKeySequence.MoveToNextLine ):
            if len( self.history ):
                self.historyIndex += 1
                if self.historyIndex == len( self.history ):
                    self.historyIndex = 0
                self._recall()
        else:
            e.ignore()


    def focusNextPrevChild ( self, next ):
        """ Suppress tabbing to the next window in multi-line commands.
        """
        if next and self._more:
            return False

        return QTextEdit.focusNextPrevChild( self, next )


    def mousePressEvent ( self, e ):
        """ Keep the cursor after the last prompt.
        """
        if e.button() == Qt.LeftButton:
            self.moveCursor( QTextCursor.EndOfLine )


    def contentsContextMenuEvent ( self, ev ):
        """ Suppress the right button context menu.
        """
        pass


    def _clear_line ( self ):
        """ Clear the input line buffer.
        """
        self._line.truncate( 0 )
        self._point = 0


    def _insert_text ( self, text ):
        """ Insert text at the current cursor position.
        """
        self.insertPlainText( text )
        self._line.insert( self._point, text )
        self._point += text.length()


    def _recall ( self ):
        """ Display the current item from the command history.
        """
        self.moveCursor( QTextCursor.EndOfBlock )

        while self._point:
            self.moveCursor( QTextCursor.Left, QTextCursor.KeepAnchor )
            self._point -= 1

        self.textCursor().removeSelectedText()

        self._clear_line()
        self._insert_text( self.history[ self.historyIndex ] )

#-- EOF ------------------------------------------------------------------------