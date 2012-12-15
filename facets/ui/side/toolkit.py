"""
Defines the concrete implementations of the facets Toolkit interface for
the Qt4 user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide.QtCore \
    import Qt, QObject, QTimer, QMutex, QEventLoop, SIGNAL

from PySide.QtGui                                                            \
    import QLabel, QLineEdit, QTextEdit, QApplication, QWidget, QCheckBox,   \
           QMainWindow, QDialog, QColor, QHBoxLayout, QVBoxLayout, QPalette, \
           QScrollArea, QFrame, QGridLayout, QPushButton, QGroupBox,         \
           QComboBox, QCursor, QPixmap, QImage, QFontDatabase

# Make sure a QApplication object is created early:
_app = None
if QApplication.startingUp():
    import sys
    _app = QApplication( sys.argv )

from facets.core.facet_notifiers \
    import set_ui_handler

from facets.ui.toolkit \
    import Toolkit

from facets.ui.adapters.control \
    import Control, as_toolkit_control

from facets.ui.side.adapters.control \
    import adapted_control, control_adapter, Widget

from facets.ui.side.adapters.layout \
    import adapted_layout, layout_adapter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Horizontal alignment styles for text:
horizontal_alignment_styles = {
    'default': Qt.AlignLeft,
    'left':    Qt.AlignLeft,
    'center':  Qt.AlignHCenter,
    'right':   Qt.AlignRight
}

# Top-level window types:
TopLevelWindows = ( QDialog, QMainWindow )

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# The singleton clipboard object:
the_clipboard = None

# The singleton font database:
the_font_database = None

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def font_database ( ):
    """ Returns the singleton font database object.
    """
    global the_font_database

    if the_font_database is None:
        the_font_database = QFontDatabase()

    return the_font_database

#-------------------------------------------------------------------------------
#  '_CallAfter' class:
#-------------------------------------------------------------------------------

class _CallAfter ( QTimer ):
    """ This class dispatches a handler so that it executes in the main GUI
        thread (similar to the wx function).
    """

    #-- Class Variables --------------------------------------------------------

    # The list of pending calls:
    _calls = []

    # The mutex around the list of pending calls:
    _calls_mutex = QMutex()

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self ):
        QTimer.__init__( self )

        self.connect( self, SIGNAL('timeout()'), self._dispatch )
        self.start( 125 )


    def _queue ( self, handler, args ):
        """ Queue up a work item to be processed on the UI thread later.
        """
        self._calls_mutex.lock()

        self._calls.append( ( handler, args ) )

        self._calls_mutex.unlock()

    #-- Private Methods --------------------------------------------------------

    def _dispatch ( self ):
        """ Invoke all queued handlers.
        """
        self._calls_mutex.lock()

        for handler, args in self._calls:
            handler( *args )

        del self._calls[:]

        self._calls_mutex.unlock()

# The global handler for all queued UI events issued from non-UI threads:
call_after = _CallAfter()

def ui_handler ( handler, *args ):
    """ Handles UI notification handler requests that occur on a thread other
        than the UI thread.
    """
    global call_after

    call_after._queue( handler, args )

# Tell the facets notification handlers to use this UI handler:
set_ui_handler( ui_handler )


def check_parent ( parent ):
    """ Verifies that the parent object is a QWidget; otherwise it returns None
        to prevent constructor errors from Qt.
    """
    parent = as_toolkit_control( parent )

    if isinstance( parent, QWidget ):
        return parent

    return None


def control_adapter_for ( control ):
    """ Returns the adapted form of the control.
    """
    # If the control has a parent already and is not a top-level window, then
    # make it visible, since the top-level caller assumes it is already visible.
    # If it does not have a parent, then it will eventually be added to a
    # layout, which will handle making it visible:
    if ((control.parentWidget() is not None) and
        (not isinstance( control, TopLevelWindows ))):
        control.setVisible( True )

    return control_adapter( control )

#-------------------------------------------------------------------------------
#  'GUIToolkit' class:
#-------------------------------------------------------------------------------

class GUIToolkit ( Toolkit ):
    """ Implementation class for Qt toolkit.
    """

    #-- Create Qt Specific User Interfaces -----------------------------------

    def ui_wizard ( self, ui, parent ):
        """ Creates a Qt wizard dialog user interface using information from the
            specified UI object.
        """
        import facets.ui.side.editors.ui_wizard

        ui_wizard.ui_wizard( ui, parent )


    def show_help ( self, ui, control ):
        """ Shows a help window for a specified UI and control.
        """
        import facets.ui.side.editors.ui_panel

        ui_panel.show_help( ui, control )


    def key_event_to_name ( self, event ):
        """ Converts a keystroke event into a corresponding key name.
        """
        import key_event_to_name as ketn

        return ketn.key_event_to_name( event )


    def hook_events ( self, ui, control, events = None, handler = None ):
        """ Hooks all specified events for all controls in a UI so that they
            can be routed to the correct event handler.
        """
        # fixme: Implement this method. For now just log that is was called...
        from facets.extra.helper.debug import log_if
        log_if( 2, ('hook_events( ui = %s, control = %s, events = %s, '
                    'handler = %s )' % ( ui, control, events, handler )) )


    def route_event ( self, ui, event ):
        """ Routes a "hooked" event to the corrent handler method.
        """
        # fixme: Implement this method...
        raise NotImplementedError


    def event_loop ( self, exit_code = None ):
        """ Enters or exits a user interface event loop. If *exit_code* is
            omitted, a new event loop is started. If *exit_code*, which should
            be an integer, is specified, the most recent event loop started is
            exited with the specified *exit_code* as the result. Control does
            not return from a call to start an event loop until a corresponding
            request to exit an event loop is made. Event loops may be nested.
        """
        if exit_code is None:
            if self._event_loop is None:
                self._event_loop = []

            self._event_loop.append( QEventLoop() )
            result = self._event_loop[-1].exec_()
            self._event_loop.pop()

            return result

        if len( self._event_loop or []) > 0:
            self._event_loop[-1].exit( int( exit_code ) )


    def image_size ( self, image ):
        """ Returns a (width,height) tuple containing the size of a specified
            toolkit image.
        """
        return ( image.width(), image.height() )


    def constants ( self ):
        """ Returns a dictionary of useful constants.

            Currently, the dictionary should have the following key/value pairs:
            - 'WindowColor': the standard window background color in the toolkit
              specific color format.
        """
        return {
            'WindowColor': QPalette().window().color()
        }


    def to_toolkit_color ( self, color ):
        """ Returns a specified GUI toolkit neutral color as a toolkit specific
            color object.
        """
        return QColor( *color )


    def from_toolkit_color ( self, color ):
        """ Returns a toolkit specific color object as a GUI toolkit neutral
            color.
        """
        if isinstance( color, tuple ):
            return color

        alpha = color.alpha()
        if alpha == 255:
            return ( color.red(), color.green(), color.blue() )

        return ( color.red(), color.green(), color.blue(), alpha )


    def beep ( self ):
        """ Makes a beep to alert the user to a situation requiring their
            attention.
        """
        raise QApplication.beep()


    def screen_size ( self ):
        """ Returns a tuple of the form (width,height) containing the size of
            the user's display.
        """
        _geom = QApplication.desktop().availableGeometry()

        return ( _geom.width(), _geom.height() )


    def scrollbar_size ( self ):
        """ Returns a tuple of the form (width,height) containing the standard
            width of a vertical scrollbar, and the standard height of a
            horizontal scrollbar.
        """
        # fixme: Is there a correct way to do this?...
        return ( 18, 18 )


    def mouse_position ( self ):
        """ Returns the current mouse position (in screen coordinates) as a
            tuple of the form: (x,y).
        """
        position = QCursor.pos()

        return ( position.x(), position.y() )


    def mouse_buttons ( self ):
        """ Returns a set containing the mouse buttons currently being pressed.
            The possible set values are: 'left', 'middle', 'right'.
        """
        result = set()
        # fixme: Don't know how to query the current mouse button state in Qt...
        return result


    def control_at ( self, x, y ):
        """ Returns the Control at the specified screen coordinates, or None if
            there is no control at that position.
        """
        return adapted_control( QApplication.widgetAt( x, y ) )


    def is_application_running ( self ):
        """ Returns whether or not the Qt QApplication object has been created
            and is running its event loop.
        """
        global _app

        return ((_app is not None) and hasattr( _app, '_in_event_loop' ))


    def run_application ( self, app_info ):
        """ Runs the application described by the *app_info* object as a Facets
            UI modal application using the Qt toolkit.
        """
        app_info.ui = app_info.view.ui(
            app_info.context,
            kind       = app_info.kind,
            handler    = app_info.handler,
            id         = app_info.id,
            scrollable = app_info.scrollable,
            args       = app_info.args
        )

        if app_info.ui.control is not None:
            app_instance = QApplication.instance()
            app_instance._in_event_loop = True
            QApplication.exec_()


    # fixme: We should be able to delete this after everything is debugged...
    def as_toolkit_adapter ( self, control ):
        """ Returns the GUI toolkit specific control adapter associated with
            *control*.
        """
        if (control is None) or isinstance( control, Control ):
            return control

        return control_adapter( control )


    def clipboard ( self ):
        """ Returns the GUI toolkit specific implementation of the clipboard
            object that implements the Clipboard interface.
        """
        global the_clipboard

        if the_clipboard is None:
            from facets.ui.side.adapters.clipboard import QtClipboard

            the_clipboard = QtClipboard()

        return the_clipboard


    def font_names ( self ):
        """ Returns a list containing the names of all available fonts.
        """
        families   = font_database().families()
        font_names = []
        for i in xrange( families.count() ):
            font_names.append( unicode( families[ i ] ) )

        return font_names


    def font_fixed ( self, font_name ):
        """ Returns **True** if the font whose name is specified by *font_name*
            is a fixed (i.e. monospace) font. It returns **False** if
            *font_name* is a proportional font.
        """
        return font_database().isFixedPitch( font_name )

    #-- GUI Toolkit Dependent Facet Definitions --------------------------------

    def color_facet ( self, *args, **facets ):
        import color_facet as cf

        return cf.QtColor( *args, **facets )


    def rgb_color_facet ( self, *args, **facets ):
        import rgb_color_facet as rgbcf

        return rgbcf.RGBColor( *args, **facets )


    def font_facet ( self, *args, **facets ):
        import font_facet as ff

        return ff.QtFont( *args, **facets )

    #-- 'EditorFactory' Factory Methods ----------------------------------------

    # Code:
    def code_editor ( self, *args, **facets ):
        import facets.ui.side.editors.code_editor as ce

        return ce.CodeEditor( *args, **facets )


    # Directory:
    def directory_editor ( self, *args, **facets ):
        import facets.ui.side.editors.directory_editor as de

        return de.DirectoryEditor( *args, **facets )


    # Drop (drag and drop target):
    def drop_editor ( self, *args, **facets ):
        import facets.ui.side.editors.drop_editor as de

        return de.DropEditor( *args, **facets )


    # Enum(eration):
    def enum_editor ( self, *args, **facets ):
        import facets.ui.side.editors.enum_editor as ee

        return ee.EnumEditor( *args, **facets )


    # File:
    def file_editor ( self, *args, **facets ):
        import facets.ui.side.editors.file_editor as fe

        return fe.FileEditor( *args, **facets )


    # Font:
    def font_editor ( self, *args, **facets ):
        import facets.ui.side.editors.font_editor as fe

        return fe.FontEditor( *args, **facets )


    # Grid:
    def grid_editor ( self, *args, **facets ):
        import facets.ui.side.editors.grid_editor as ge

        return ge.QtGridEditor( *args, **facets )


    # HTML:
    def html_editor ( self, *args, **facets ):
        import facets.ui.side.editors.html_editor as he

        return he.HTMLEditor( *args, **facets )


    # Image enum(eration):
    def image_enum_editor ( self, *args, **facets ):
        import facets.ui.side.editors.image_enum_editor as iee

        return iee.ImageEnumEditor( *args, **facets )


    # List:
    def list_editor ( self, *args, **facets ):
        import facets.ui.side.editors.list_editor as le

        return le.ListEditor( *args, **facets )


    # ListStr:
    def list_str_editor ( self, *args, **facets ):
        import facets.ui.side.editors.list_str_editor as lse

        return lse.ListStrEditor( *args, **facets )


    # Ordered set:
    def ordered_set_editor ( self, *args, **facets ):
        import facets.ui.side.editors.ordered_set_editor as ose

        return ose.OrderedSetEditor( *args, **facets )


    # Plot:
    def plot_editor ( self, *args, **facets ):
        import facets.ui.side.editors.plot_editor as pe

        return pe.PlotEditor( *args, **facets )


    # Tree:
    def tree_editor ( self, *args, **facets ):
        import facets.ui.side.editors.tree_editor as te

        return te.TreeEditor( *args, **facets )

    #-- Create GUI Toolkit Neutral Common Controls -----------------------------

    def create_control ( self, parent, tab_stop = False, handle_keys = False ):
        """ Returns an adapted control suitable for use as a base for creating
            custom controls.
        """
        policy = Qt.NoFocus
        if tab_stop:
            policy = Qt.TabFocus
            if handle_keys:
                policy = Qt.StrongFocus
        elif handle_keys:
            policy = Qt.ClickFocus

        control = Widget( check_parent( parent ) )
        control.setFocusPolicy( policy )
        control.setMouseTracking( True )
        control._auto_fill = False

        from facets.extra.helper.debug import created_from
        created_from( control )

        return control_adapter_for( control )


    def create_frame ( self, parent, style, title = '' ):
        """ Returns an adapted top-level window frame/dialog control. The
            *style* parameter is a set containing values from the following
            list:
            - 'frame':      The result should be a normal top-level window.
            - 'dialog':     The result should be a dialog window.
            - 'resizable':  The window should have a resize border.
            - 'simple':     The window should have a simple border.
            - 'none':       The window should not have any border.
            - 'min_max':    The window should have minimize/maximize buttons.
            - 'float':      The window should float on top of its parent.
            - 'no_taskbar': The window should not appear on the system taskbar.
        """
        layout = QVBoxLayout()

        if 'frame' in style:
            flags = Qt.Window
        else:
            flags = Qt.WindowSystemMenuHint
            if 'min_max' in style:
                flags |= Qt.WindowMinMaxButtonsHint

            if 'resizable' in style:
                flags |= Qt.WindowMinMaxButtonsHint
            elif 'simple' in style:
                flags = Qt.Popup
            elif 'none' in style:
                flags = Qt.FramelessWindowHint

        if 'float' in style:
            flags |= Qt.WindowStaysOnTopHint

        klass     = MainWindow
        is_dialog = ('dialog' in style)
        if is_dialog:
            klass = Dialog

        control = klass( check_parent( parent ), flags )
        control.setWindowTitle( title )

        # Create the main window so we can add toolbars etc:
        if is_dialog:
            control._mw = QMainWindow()
            layout.addWidget( control._mw )
            control.setLayout( layout )
            layout.setContentsMargins( 4, 0, 4, 0 )

        control.setMouseTracking( True )

        return control_adapter_for( control )


    def create_panel ( self, parent ):
        """ Returns an adapted panel control.
        """
        # fixme: Should use the Qt equivalent of a FacetsUIPanel...
        return control_adapter_for( Widget( check_parent( parent ) ) )


    def create_scrolled_panel ( self, parent ):
        """ Returns a panel that can scroll its contents.
        """
        sa = QScrollArea( check_parent( parent ) )
        sa.setFrameShape( QFrame.NoFrame )
        sa.setWidgetResizable( True )

        return control_adapter_for( sa )


    def create_label ( self, parent, label = '', align = 'left' ):
        """ Returns an adapted label control.
        """
        control = QLabel( check_parent( parent ) )
        control.setText( label )
        control.setAlignment( horizontal_alignment_styles[ align ] |
                              Qt.AlignVCenter )

        return control_adapter_for( control )


    def create_text_input ( self, parent, read_only = False, password = False,
                                  handle_enter = False, multi_line = False,
                                  align = 'left' ):
        """ Returns an adapted single or mutli line text input control.
        """
        if multi_line:
            control = QTextEdit( check_parent( parent ) )
        else:
            control = QLineEdit( check_parent( parent ) )
            control.setAlignment( horizontal_alignment_styles[ align ] |
                                  Qt.AlignVCenter )
            if password:
                control.setEchoMode( QLineEdit.Password )

        control.setReadOnly( read_only )

        return control_adapter_for( control )


    def create_button ( self, parent, label = '' ):
        """ Returns an adapted button.
        """
        control = QPushButton( check_parent( parent ) )
        control.setText( label )
        control.setAutoDefault( False )

        return control_adapter_for( control )


    def create_checkbox ( self, parent, label = '' ):
        """ Returns an adapted checkbox control.
        """
        control = QCheckBox( check_parent( parent ) )
        control.setText( label )

        return control_adapter_for( control )


    def create_combobox ( self, parent, editable = False ):
        """ Returns an adapted QComboBox control.
        """
        control = QComboBox( check_parent( parent ) )
        control.setEditable( editable )

        return control_adapter( control )


    def create_separator ( self, parent, is_vertical = True ):
        """ Returns an adapted separator line control.
        """
        control = QFrame()
        control.setFrameShadow( QFrame.Sunken )

        if is_vertical:
            control.setFrameShape( QFrame.VLine )
            control.setMinimumWidth( 5 )
        else:
            control.setFrameShape( QFrame.HLine )
            control.setMinimumHeight( 5 )

        return control_adapter_for( control )

    #-- Create GUI Toolkit Neutral Common Layout Managers ----------------------

    def create_layout ( self, layout ):
        """ Creates a new GUI toolkit neutral layout manager for the specified
            GUI toolkit specific layout manager or implementor of the
            IAbstractLayout interface.
        """
        return layout_adapter( layout )


    def create_box_layout ( self, is_vertical = True, align = '' ):
        """ Returns a new GUI toolkit neutral 'box' layout manager.
        """
        if is_vertical:
            layout    = QVBoxLayout()
            alignment = Qt.AlignTop
            if align == 'bottom':
                alignment = Qt.AlignBottom
            layout.setAlignment( alignment )
        else:
            layout    = QHBoxLayout()
            alignment = Qt.AlignLeft
            if align == 'right':
                alignment = Qt.AlignRight
            layout.setAlignment( alignment )

        layout.setSpacing( 0 )
        ### PYSIDE: layout.setMargin( 0 )

        return layout_adapter( layout, is_vertical )


    def create_groupbox_layout ( self, is_vertical, parent, label, owner ):
        """ Returns a new GUI toolkit neutral vertical layout manager for a
            groupbox.
        """
        gb       = QGroupBox( label, check_parent( parent ) )
        gb.owner = owner
        bl       = self.create_box_layout( is_vertical )
        gb.setLayout( bl() )

        return ( control_adapter_for( gb ), bl )


    def create_flow_layout ( self, is_vertical ):
        """ Returns a new GUI toolkit neutral horizontal or vertical flow
            layout.
        """
        from facets.ui.flow_layout import FlowLayout

        return self.create_layout( FlowLayout( is_vertical = is_vertical ) )


    def create_grid_layout ( self, rows = 0, columns = 1, v_margin = 0,
                                   h_margin = 0 ):
        """ Returns a new GUI toolkit neutral grid layout manager which
            supports a (rows,columns) sized grid, with each grid element
            having (v_margin,h_margin) pixels of space around it.

            If rows is 0, the number of rows is not predefined, but will be
            determined by the actual number of controls added to the layout.
        """
        layout = QGridLayout()
        layout.setHorizontalSpacing( h_margin )
        layout.setVerticalSpacing(   v_margin )
        layout.setAlignment( Qt.AlignTop )
        ### PYSIDE: layout.setMargin( 4 )

        return layout_adapter( layout, columns = columns )

    #-- Create GUI Toolkit Neutral Miscellaneous Objects -----------------------

    def create_bitmap ( self, buffer, width, height ):
        """ Create a GUI toolkit specific bitmap of the specified width and
            height from the specified buffer 'bgra' data in row order.
        """
        return QPixmap.fromImage( QImage( buffer, width, height,
                                          QImage.Format_ARGB32 ) )


    def create_timer ( self, milliseconds, handler ):
        """ Creates and returns a timer which will call *handler* every
            *milliseconds* milliseconds. The timer can be cancelled by calling
            the returned object with no arguments.
        """
        timer = QTimer()
        QObject.connect( timer, SIGNAL( 'timeout()' ), handler )
        timer.start( int( milliseconds ) )

        return timer.stop

    #-- GUI Toolkit Neutral Adapter Methods ------------------------------------

    def adapter_for ( self, item ):
        """ Returns the correct type of adapter (control or layout) for the
            specified item.
        """
        if isinstance( item, QWidget ):
            return adapted_control( item )

        return adapted_layout( item )


    def control_adapter_for ( self, control ):
        """ Returns the GUI toolkit neutral adapter for the specified GUI
            toolkit specific control.
        """
        return adapted_control( control )


    def layout_adapter_for ( self, layout ):
        """ Returns the GUI toolkit neutral adapter for the specified GUI
            toolkit specific layout manager.
        """
        return adapted_layout( layout )

#-------------------------------------------------------------------------------
#  'MainWindow' class:
#-------------------------------------------------------------------------------

class MainWindow ( QMainWindow ):

    #-- Public Methods ---------------------------------------------------------

    def closeEvent ( self, event ):
        """ Handles the user requesting the window to close.
        """
        # If the 'Handler' allowed the window to close, then pass the request
        # along to the standard Qt event handler, which will close the window:
        if getattr( self, '_closed', False ):
            QMainWindow.closeEvent( self, event )

#-------------------------------------------------------------------------------
#  'Dialog' class:
#-------------------------------------------------------------------------------

class Dialog ( QDialog ):

    #-- Public Methods ---------------------------------------------------------

    def closeEvent ( self, event ):
        """ Handles the user requesting the window to close.
        """
        # If the 'Handler' allowed the window to close, then pass the request
        # along to the standard Qt event handler, which will close the window:
        if getattr( self, '_closed', False ):
            QDialog.closeEvent( self, event )

#-- EOF ------------------------------------------------------------------------