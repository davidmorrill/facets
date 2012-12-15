"""
Defines the concrete Qt4 specific implementation of the Control class for
providing GUI toolkit neutral control support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import drag

from types \
    import MethodType

from PyQt4.QtCore \
    import Qt, QObject, QEvent, QString, QPoint, QUrl, QMimeData, QVariant, \
           SIGNAL

from PyQt4.QtGui \
    import QCursor, QColor, QPalette, QWidget, QMainWindow, QFontMetrics, \
           QPixmap, QDialog, QApplication, QSizePolicy, QComboBox,        \
           QRubberBand, QDrag, QTextEdit, QToolTip

from facets.core_api \
    import HasPrivateFacets, Bool, Any, Instance, cached_property

from facets.core.facet_base \
    import SequenceTypes

from facets.ui.adapters.control \
    import Control

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.ui.qt4.pyface.image_resource \
    import ImageResource

from graphics \
    import QtGraphics, color_for, painter_for

from ui_event \
    import QtUIEvent

from drag \
    import QtDrag, RequestAction, PyMimeData

from layout \
    import QtLayout, adapted_layout

#-------------------------------------------------------------------------------
#  Global data:
#-------------------------------------------------------------------------------

# Mapping of standard cursor names to Qt cursor id's:
CursorNameMap = {
    'arrow':    Qt.ArrowCursor,
    'hand':     Qt.PointingHandCursor,
    'sizing':   Qt.SizeAllCursor,
    'sizens':   Qt.SizeVerCursor,
    'sizeew':   Qt.SizeHorCursor,
    'sizenwse': Qt.SizeFDiagCursor,
    'sizenesw': Qt.SizeBDiagCursor,
    'question': Qt.WhatsThisCursor
}

# Mapping from ToolBar.orientation values to Qt ToolBarArea values:
ToolBarAreaMap = {
    'horizontal': Qt.TopToolBarArea,
    'vertical':   Qt.LeftToolBarArea,
    'top':        Qt.TopToolBarArea,
    'bottom':     Qt.BottomToolBarArea,
    'left':       Qt.LeftToolBarArea,
    'right':      Qt.RightToolBarArea
}

# Mapping from Qt Event types to generic event names:
EventMap = {
    QEvent.Paint:               'paint',
    QEvent.Resize:              'size',
    QEvent.FocusIn:             'get_focus',
    QEvent.FocusOut:            'lose_focus',
    QEvent.KeyPress:            'key_press',
    QEvent.KeyRelease:          'key',
    QEvent.MouseButtonPress:    'down',
    QEvent.MouseButtonRelease:  'up',
    QEvent.MouseButtonDblClick: 'dclick',
    QEvent.MouseMove:           'motion',
    QEvent.Enter:               'enter',
    QEvent.Leave:               'leave',
    QEvent.Wheel:               'wheel',
    QEvent.Close:               'close',
    QEvent.DragEnter:           'drag_enter',
    QEvent.DragLeave:           'drag_leave',
    QEvent.DragMove:            'drag_move',
    QEvent.Drop:                'drag_drop',
    QEvent.WindowActivate:      'activate',
    QEvent.WindowDeactivate:    'deactivate'
}

# The set of mouse related events:
MouseEvents = set( [
    'down', 'up', 'dclick', 'motion', 'enter', 'leave', 'wheel'
] )

# Set of mouse button related events:
MouseButtons = set( [ 'down', 'up', 'dclick' ] )

# Mapping from Qt button identifiers to a generic mouse button name:
MousePrefix = {
    Qt.LeftButton:  'left_',
    Qt.MidButton:   'middle_',
    Qt.RightButton: 'right_'
}

# Mapping of Qt control class names to methods of those classes which handle
# getting or setting the control's 'value':
get_value_method = {
    'QLineEdit':   'text',
    'QTextEdit':   'toPlainText',
    'QPushButton': 'text',
    'QLabel':      'text',
    'QCheckBox':   'isChecked',
    'QMainWindow': 'windowTitle',
    'MainWindow':  'windowTitle',
    'QDialog':     'windowTitle',
    'Dialog':      'windowTitle'
}

set_value_method = {
    'QLineEdit':   'setText',
    'QPushButton': 'setText',
    'QLabel':      'setText',
    'QTextEdit':   'setPlainText',
    'QCheckBox':   'setChecked',
    'QMainWindow': 'setWindowTitle',
    'MainWindow':  'setWindowTitle',
    'QDialog':     'setWindowTitle',
    'Dialog':      'setWindowTitle'
}

# Mapping from facets SizePolicy to Qt QSizePolicy values:
PolicyMap = {
    'fixed':     QSizePolicy.Fixed,
    'expanding': QSizePolicy.MinimumExpanding
}

# Result indicating that no matching event handlers were found:
NoHandlers = []

# Set of events which are never completely handled by user code:
NeverHandledEvents = set( ( 'close', 'lose_focus' ) )

# Set of drag and drop related events:
DragDropEvents = set(
    ( 'drag_enter', 'drag_leave', 'drag_move', 'drag_drop' )
)

# A temporary graphics object used to compute text sizes:
TempGraphics = None

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def adapted_control ( control ):
    """ Returns a correctly adapted version of the specified control.
    """
    if control is None:
        return None

    return control_adapter( control )


def control_adapter ( control ):
    """ Returns the control adapter associated with the specified control.
    """
    adapter = getattr( control, 'adapter', None )
    if adapter is None:
        adapter = QtControl( control )

    return adapter

#-------------------------------------------------------------------------------
#  'QtControl' class:
#-------------------------------------------------------------------------------

class QtControl ( Control ):
    """ Defines the concrete Qt4 specific implementation of the Control class
        for providing GUI toolkit neutral control support.
    """

    #-- Private Facet Definitions ----------------------------------------------

    # Is the mouse currently captured?
    is_mouse_captured = Bool( False )

    #-- Control Property Implementations ---------------------------------------

    def _get_position ( self ):
        return ( self.control.x(), self.control.y() )

    def _set_position ( self, x_y ):
        self.control.move( *x_y )


    def _get_size ( self ):
        size = self.control.frameSize()

        return ( size.width(), size.height() )

    def _set_size ( self, dx_dy ):
        control = self.control
        dx, dy  = dx_dy
        cdx     = control.width()
        cdy     = control.height()
        fs      = control.frameSize()
        fdx     = fs.width()
        fdy     = fs.height()

        if (dx < 0) or (dy < 0):
            if dx < 0:
                dx = cdx

            if dy < 0:
                dy = cdy

        control.resize( dx + (fdx - cdx), dy + (fdy - cdy) )


    def _get_virtual_size ( self ):
        return self.min_size

    def _set_virtual_size ( self, dx_dy ):
        self.min_size = dx_dy


    def _get_bounds ( self ):
        g = self.control.geometry()

        return ( g.x(), g.y(), g.width(), g.height() )

    def _set_bounds ( self, x_y_dx_dy ):
        self.control.setGeometry( *x_y_dx_dy )


    def _get_frame_bounds ( self ):
        g = self.control.frameGeometry()

        return ( g.x(), g.y(), g.width(), g.height() )


    def _get_visible_bounds ( self ):
        rect = self.control.visibleRegion().boundingRect()

        return ( rect.x(), rect.y(), rect.width(), rect.height() )


    def _get_client_size ( self ):
        size = self.control.size()

        return ( size.width(), size.height() )

    def _set_client_size ( self, dx_dy ):
        self.control.resize( *dx_dy )


    def _get_best_size ( self ):
        size = self.control.sizeHint()

        return ( size.width(), size.height() )


    def _get_min_size ( self ):
        return ( self.control.minimumWidth(), self.control.minimumHeight() )

    def _set_min_size ( self, dx_dy ):
        dx, dy = dx_dy

        if dx < 0:
            dx = self.control.minimumWidth()

        if dy < 0:
            dy = self.control.minimumHeight()

        self.control.setMinimumSize( dx, dy )


    def _get_screen_position ( self ):
        pos = self.control.mapToGlobal( QPoint() )

        return ( pos.x(), pos.y() )


    def _get_mouse_position ( self ):
        pos = QCursor.pos()

        return ( pos.x(), pos.y() )


    def _get_visible ( self ):
        return self.control.isVisible()

    def _set_visible ( self, visible ):
        control     = self.control
        was_visible = control.isVisible()
        if self.modal:
            if visible:
                control.exec_()
            else:
                control.setModal( False )
        else:
            control.setVisible( visible )
            if isinstance( control, QDialog ):
                control.layout().parentWidget().setVisible( visible )

        if visible != was_visible:
            self.facet_property_set( 'visible', was_visible, visible )


    def _get_maximized ( self ):
        return ((int( self.control.windowState() ) & Qt.WindowMaximized) != 0)

    def _set_maximized ( self, maximized ):
        state = self.control.windowState()
        if maximized:
            self.control.setWindowState( state | Qt.WindowMaximized )
        else:
            self.control.setWindowState( state & (~Qt.WindowMaximized) )


    def _get_enabled ( self ):
        return self.control.isEnabled()

    def _set_enabled ( self, enabled ):
        was_enabled = self.control.isEnabled()
        if enabled != was_enabled:
            self.control.setEnabled( enabled )
            self.facet_property_set( 'enabled', was_enabled, enabled )


    def _get_checked ( self ):
        return self.control.isChecked()

    def _set_checked ( self, checked ):
        was_checked = self.control.isChecked()
        if checked != was_checked:
            self.control.setChecked( checked )
            self.facet_property_set( 'checked', was_checked, checked )


    def _get_drop_target ( self ):
        return self._drop_target

    def _set_drop_target ( self, drop_target ):
        self._drop_target = drop_target
        self.control.setAcceptDrops( drop_target is not None )

        method = self.set_event_handler
        if drop_target is None:
            method = self.unset_event_handler

        method(
            drag_enter = self._drag_enter,
            drag_leave = self._drag_leave,
            drag_move  = self._drag_move,
            drag_drop  = self._drag_drop
        )

    def _get_layout ( self ):
        control = self.control

        return adapted_layout( getattr( control, '_mw', control ).layout() )

    def _set_layout ( self, adapter ):
        # If we did not receive a GUI toolkit neutral layout manager, convert
        # it to an adapted one (or None):
        if not isinstance( adapter, QtLayout ):
            adapter = adapted_layout( adapter )

        cur_layout = self.layout
        if cur_layout is None:
            if adapter is not None:
                self.control.setLayout( adapter() )

            return

        cur_layout = cur_layout()
        if (adapter is None) or (adapter.layout is not cur_layout):
            # According to the Qt docs, you have to 'delete' the existing
            # layout to remove it, but I don't know how to do a C++ 'delete'
            # from Python. So we instead delete all items from the current
            # layout as the next best thing, and then add the specified layout
            # manager (if any) to the original layout manager:
            while cur_layout.takeAt( 0 ) is not None: pass

            if adapter is not None:
                widget = cur_layout.parentWidget()
                if isinstance( widget, QMainWindow ):
                    layout = adapter()
                    layout.setMargin( 0 )
                    panel = QWidget()
                    panel.setLayout( layout )
                    widget.setCentralWidget( panel )
                else:
                    cur_layout.addItem( adapter() )


    def _get_parent_layout ( self ):
        # fixme: I haven't been able to find a direct way to do this in Qt, so
        # we are using an ad hoc algorithm of searching the parent widget's
        # layout hierarchy for a layout containing this control...
        control = self.control
        parent  = control.parentWidget()
        if parent is not None:
            layout = parent.layout()
            if layout is not None:
                return adapted_layout( self._parent_layout( control, layout ) )

        return None

    def _parent_layout ( self, control, layout ):
        """ Recursively searches a layout tree looking for a specified control.
            Returns either the layout containing the control or None if no
            layout containing the control is found.
        """
        if layout.indexOf( control ) >= 0:
            return layout

        for i in xrange( 0, layout.count() ):
            child_layout = layout.itemAt( i ).layout()
            if child_layout is not None:
                result = self._parent_layout( control, child_layout )
                if result is not None:
                    return result

        return None


    @cached_property
    def _get_parent ( self ):
        return adapted_control( self.control.parentWidget() )


    def _get_content ( self ):
        return adapted_control( self.control.widget() )

    def _set_content ( self, content ):
        self.control.setWidget( content() )


    @cached_property
    def _get_root_parent ( self ):
        parent = self.control
        while parent is not None:
            control = parent
            parent  = control.parentWidget()

        return adapted_control( control )


    def _get_children ( self ):
        return [ adapted_control( child )
                 for child in self.control.children()
                 if isinstance( child, QWidget ) ]


    def _get_value ( self ):
        name   = self.control.__class__.__name__
        method = get_value_method.get( name )
        if method is not None:
            result = getattr( self.control, method )()
        else:
            result = getattr( self, '_get_value_for_' + name )()

        if isinstance( result, QString ):
            return unicode( result )

        return result

    def _get_value_for_QComboBox ( self ):
        return self.control.lineEdit().text()


    def _set_value ( self, value ):
        name   = self.control.__class__.__name__
        method = set_value_method.get( name )
        if method is not None:
            getattr( self.control, method )( value )
        else:
            getattr( self, '_set_value_for_' + name )( value )

    def _set_value_for_QComboBox ( self, value ):
        self.control.lineEdit().setText( value )


    def _get_count ( self ):
        return getattr( self, '_get_count_for_' +
                              self.control.__class__.__name__ )()

    def _get_count_for_QTabWidget ( self ):
        return self.control.count()


    def _get_selection ( self ):
        return getattr( self, '_get_selection_for_' +
                              self.control.__class__.__name__ )()

    def _get_selection_for_QLineEdit ( self ):
        start = self.control.selectionStart()

        return ( start, start + len( self.control.selectedText() ) )

    def _set_selection ( self, selection ):
        method =  getattr( self, '_set_selection_for_' +
            self.control.__class__.__name__, None )
        if method is not None:
            method( selection )

    def _set_selection_for_QLineEdit ( self, selection ):
        start, end = selection
        if start < 0:
            self.control.selectAll()
        else:
            self.control.setSelection( start, end - start )

# The following does not work because QTextEdit has a different signature for
# setSelection: setSelection(startPara, startIndex, endPara, endIndex)
#    def _set_selection_for_QTextEdit ( self, selection ):
#        start, end = selection
#        if start < 0:
#            self.control.selectAll()
#        else:
#            self.control.setSelection( start, end - start )

    def _set_selection_for_QComboBox ( self, selection ):
        control = self.control
        if isinstance( selection, int ):
            control.setCurrentIndex( selection )
        elif isinstance( selection, basestring ):
            control.setCurrentIndex( control.findText( selection ) )
        else:
            control    = control.lineEdit()
            start, end = selection
            if start < 0:
                control.selectAll()
            else:
                control.setSelection( start, end - start )


    def _get_font ( self ):
        return self.control.font()

    def _set_font ( self, font ):
        self.control.setFont( font )


    def _get_graphics ( self ):
        return QtGraphics( painter_for( self.control ) )


    def _get_graphics_buffer ( self ):
        return self.graphics


    def _get_temp_graphics ( self ):
        global TempGraphics

        if TempGraphics is None:
            pixmap       = QPixmap( 1, 1 )
            TempGraphics = QtGraphics(
                painter_for( pixmap ), _temp_graphics = True, _pixmap = pixmap
            )

        return TempGraphics


    def _get_screen_graphics ( self ):
        from facets.ui.toolkit import toolkit

        if self._screen_graphics is None:
            control = self.control
            pixmap  = QPixmap.grabWindow( control.winId() )
            self._sg_control = sg = toolkit().create_control( self )
            sg._pixmap = pixmap
            dx, dy     = self.size
            sg.bounds  = ( 0, 0, dx, dy )
            sg.set_event_handler( paint = self._screen_graphics_paint )
            painter = painter_for( pixmap )
            painter._control = sg.control
            self._screen_graphics = (
                QtGraphics( painter, bitmap = pixmap ), 0, 0
            )

        return self._screen_graphics

    def _set_screen_graphics ( self, value ):
        self._screen_graphics = None
        self._sg_control, sg  = None, self._sg_control
        sg.destroy()


    def _get_image ( self ):
        # Note: The following code works in most cases, but fails when trying to
        # capture a VTK-based widget (the VTK-part of the widget is usually all
        # black), so we use the more involved technique of capturing the part of
        # the screen the widget covers:
        control = self.control
        if not control.isVisible():
            return ImageResource( bitmap = QPixmap.grabWidget( control, 0, 0 ) )

        point = control.mapToGlobal( QPoint() )
        size  = control.size()

        return ImageResource(
            bitmap = QPixmap.grabWindow(
                QApplication.desktop().winId(),
                point.x(), point.y(), size.width(), size.height()
            )
        )


    def _get_tooltip ( self, tooltip ):
        return self.control.tooltip()

    def _set_tooltip ( self, tooltip ):
        self.control.setToolTip( tooltip )
        if tooltip == '':
            QToolTip.hideText()


    def _get_mouse_capture ( self ):
        return self.is_mouse_captured

    def _set_mouse_capture ( self, is_captured ):
        # fixme: According to the qt documentation, it may not be necessary for
        # us to actually capture the mouse at all...
        if is_captured:
            if not self.is_mouse_captured:
                self.control.grabMouse()
        elif self.is_mouse_captured:
            self.control.releaseMouse()

        self.is_mouse_captured = is_captured


    def _get_foreground_color ( self ):
        return self.control.palette().color( QPalette.Foreground )

    def _set_foreground_color ( self, color ):
        self.control.palette().setColor( QPalette.Foreground,
                                         color_for( color ) )


    def _get_background_color ( self ):
        if self.image_slice is not None:
            self._bg_color = self.image_slice.bg_color
        else:
            self._bg_color = self.control.palette().color( QPalette.Window )

        return self._bg_color

    def _set_background_color ( self, color ):
        control   = self.control
        auto_fill = ((color is not self._bg_color) and
                     getattr( control, '_auto_fill', True ))
        qt_color  = color_for( color )
        palette   = control.palette()
        palette.setColor( QPalette.Window, qt_color )
        control.setAutoFillBackground( auto_fill )

        if not auto_fill:
            qt_color = Qt.white

        palette.setColor( QPalette.Base, qt_color )
        control.setPalette( palette )


    def _set_cursor ( self, cursor ):
        # Note: It seems to be necessary to constantly set the cursor value,
        # even if it hasn't changed, in order for Qt to consistently use the
        # correct cursor. This is unlike wxPython, where the cursor only needs
        # to be set when the cursor actually changes:
        self._cursor = cursor
        cursor_name  = CursorNameMap.get( cursor, Qt.ArrowCursor )
        control      = self.control
        if cursor_name != Qt.ArrowCursor:
            control.setCursor( cursor_name )
        else:
            control.unsetCursor()

        # Note: This somewhat bizarre logic seems to fix the problem of changing
        # the cursor when you have the mouse capture, but not the mouse focus.
        # If you do not release/grab the mouse capture in this case, the mouse
        # cursor changes briefly, but after some kind of timeout, reverts back
        # to the shape it had when the mouse capture was last released.
        if self.is_mouse_captured:
            control.releaseMouse()
            control.grabMouse()


    def _set_icon ( self, icon ):
        self.control.setWindowIcon( icon )


    def _set_menubar ( self, menubar ):
        control = self.control
        getattr( control, '_mw', control ).setMenuBar( menubar )


    def _set_toolbar ( self, toolbar ):
        control = self.control
        getattr( control, '_mw', control ).addToolBar(
            ToolBarAreaMap.get( toolbar.tool_bar_manager.orientation,
                                Qt.TopToolBarArea ),
            toolbar
        )


    def _set_frozen ( self, is_frozen ):
        self.control.setUpdatesEnabled( not is_frozen )


    def _get_is_panel ( self ):
        # fixme: I'm not sure what the Qt equivalent of a panel is...
        from facets.extra.helper.debug import log_if
        log_if( 2, 'is_panel query for: %s' % self.control )
        return (self.control.__class__ is QWidget)


    def _set_scroll_vertical ( self, can_scroll ):
        from facets.extra.helper.debug import log_if
        log_if( 2, "control_adapter._set_scroll_vertical called" )


    def _set_scroll_horizontal ( self, can_scroll ):
        from facets.extra.helper.debug import log_if
        log_if( 2, "control_adapter._set_scroll_horizontal called" )

    #-- Control Method Implementation ------------------------------------------

    def refresh ( self, x = None, y = None, dx = None, dy = None ):
        """ Refreshes the specified region of the control. If no arguments
            are specified, the entire control should be refreshed.
        """
        if x is None:
            self.control.update()
        else:
            self.control.update( x, y, dx, dy )


    def update ( self ):
        """ Causes the control to update its layout.
        """
        # fixme: The Qt documentation claims you should not normally need to
        # update layouts manually, so we are comprimising by throwing the
        # request over the wall to the layout adapter to let it decide what to
        # do:
        layout = self.layout
        if layout is not None:
            dx, dy = self.size
            if layout.update( 0, 0, dx, dy ):
                self.refresh()


    def set_focus ( self ):
        """ Sets the keyboard focus on the associated control.
        """
        self.control.setFocus()


    def set_mouse_focus ( self ):
        """ Sets the mouse focus on the associated control.
        """
        # Doesn't need to do anything for Qt.
        pass


    def popup_menu ( self, menu, x, y ):
        """ Pops up the specified context menu at the specified screen position.
        """
        xc, yc = self.screen_position
        menu.show( xc + x, yc + y )


    def bitmap_size ( self, bitmap ):
        """ Returns the size (dx,dy) of the specified toolkit specific bitmap:
        """
        return ( bitmap.width(), bitmap.height() )


    def text_size ( self, text ):
        """ Returns the size (dx,dy) of the specified text string (using the
            current control font).
        """
        rect = QFontMetrics( self.control.font() ).boundingRect( text )

        return ( rect.width(), rect.height() )


    def set_event_handler ( self, **handlers ):
        """ Sets up event handlers for a specified set of events. The keyword
            names correspond to UI toolkit neutral event names, and the values
            are the callback functions for the events. Multiple event handlers
            can be set up in a single call.
        """
        # Perform a quick exit if there is nothing to do:
        if len( handlers ) == 0:
            return

        # Get the EventHandlers object associated with the control. If one does
        # not exist, then create one and install it on the control:
        control        = self.control
        event_handlers = getattr( control, 'event_handlers', None )
        if event_handlers is None:
            control.event_handlers = event_handlers = EventHandlers()
            if not isinstance( control, Widget ):
                control.installEventFilter( event_handlers )

        # For each specified handler, add it to the event map:
        event_map = event_handlers.event_map
        for name, handler in handlers.iteritems():
            # Certain events require the use of the Qt signal/slot mechanism,
            # so check to see if the EventHandlers object has a special method
            # to set up the correct signal/slot for this event (note that in
            # this case the 'event_map' entry is not used).
            method = getattr( self, '_slot_' + name, None )
            if method is not None:
                handler = EventWrapper( handler         = handler,
                                        control_adapter = self ).process_event
                method( handler, True )

            event_map.setdefault( name, [] ).append( handler )


    def unset_event_handler ( self, **handlers ):
        """ Tears down event handlers for a specified set of events. The keyword
            names correspond to UI toolkit neutral event names, and the values
            are the callback functions for the events that should no longer be
            called. Multiple event handlers can be torn down in a single call.
        """
        # Get the EventHandlers object associated with the control. If one does
        # not exist, then nothing can be removed, so exit:
        control        = self.control
        event_handlers = getattr( control, 'event_handlers', None )
        if event_handlers is None:
            return

        # For each specified handler, remove it from the event map:
        event_map = event_handlers.event_map
        for name, handler in handlers.iteritems():
            handlers = event_map.get( name )
            if handlers is not None:
                method = getattr( self, '_slot_' + name, None )
                if ((type( handler ) is MethodType) and
                    (handler.im_self is not None)):
                    for i, handler2 in enumerate( handlers ):
                        # Handle the special case of an EventWrapper object:
                        if method is not None:
                            ew_handler = handler2
                            handler2   = ew_handler.im_self.handler

                        if (isinstance( handler2, MethodType )      and
                            (handler.__name__ == handler2.__name__) and
                            (handler.im_self is handler2.im_self)):
                            del handlers[i]
                            if method is not None:
                                method( ew_handler, False )

                            break

                else:
                    for i, handler2 in enumerate( handlers ):
                        # Handle the special case of an EventWrapper object:
                        if method is not None:
                            if handler is handler2.im_self.handler:
                                method( handler2, False )
                                del handlers[i]
                                break
                        elif handler is handler2:
                            del handlers[i]
                            break

                # If no handlers are left for this event, remove from the map:
                if len( handlers ) == 0:
                    del event_map[ name ]

        # Delete the event listener if the event map is now empty:
        if len( event_map ) == 0:
            if not isinstance( control, Widget ):
                control.removeEventFilter( event_handlers )

            delattr( control, 'event_handlers' )


    def tab ( self, forward = True ):
        """ Moves the keyboard focus to the next/previous control that will
            accept it. If *forward* is True (the default) the next valid control
            is used; otherwise the previous valid control is used.
        """
        # fixme: Not sure how to implement this for Qt. Maybe push a 'Tab' key
        # event into the control's event queue?
        raise NotImplementedError


    def scroll_to ( self, x = None, y = None ):
        """ Scrolls the control so that the point (x,y) is visible. If x or y
            is None, the maximum value for that coordinate is used.
        """
        if (x is None) or (y is None):
            vx, vy = self.content.virtual_size
            if x is None:
                x = vx

            if y is None:
                y = vy

        self.control.ensureVisible( x, y, 0, 0 )


    def scroll_by ( self, x = 0, y = 0 ):
        """ Scrolls the control by the amount specified by *x* and *y*.
        """
        if x != 0:
            sb    = self.control.horizontalScrollBar()
            sb.setValue( min( max( 0, sb.value() + x ), sb.maximum() ) )

        if y != 0:
            sb    = self.control.verticalScrollBar()
            sb.setValue( min( max( 0, sb.value() + y ), sb.maximum() ) )


    def destroy ( self ):
        """ Destroys the control associated with the adapter.
        """
        # Treating dialogs differently seems to be necessary on Windows to
        # prevent a crash.  I think the problem is that this is being called
        # from within the finished() signal handler so we need to do the
        # delete after the handler has returned.
        control = self.control
        if isinstance( control, QDialog ):
            control._closed = True
            control.done( 0 )
        elif isinstance( control, QMainWindow ):
            control._closed = True
            control.close()
        elif not isinstance( control, QRubberBand ):
            layout = self.parent_layout
            if layout is not None:
                layout.remove( self )

            control.setParent( None )


    def clear ( self ):
        """ Clears the current contents of the control.
        """
        getattr( self, 'clear_for_' + self.control.__class__.__name__ )()

    def clear_for_QComboBox ( self ):
        self.control.clear()


    def close ( self ):
        """ Request the control to close itself.
        """
        self.control.close()


    def get_item ( self, index ):
        """ Returns the control's *index*th item, for controls that contain
            items (e.g. list boxes, notebooks).
        """
        return getattr( self, 'get_item_for_' +
                              self.control.__class__.__name__ )( index )

    def get_item_for_Noteboook ( self, index ):
        return adapted_control( self.control.widget( index ) )


    def remove_item ( self, index ):
        """ Removes the control's *index*th item, for controls that contain
            items (e.g. list boxes, notebooks).
        """
        getattr( self, 'remove_item_for_' + self.control.__class__.__name__ )(
            index )

    def remove_item_for_Notebook ( self, index ):
        self.control.removeTab( index )


    def add_item ( self, value ):
        """ Adds the value specified by *value* to the control, and returns the
            index assigned to it.
        """
        return getattr( self, 'add_item_for_' +
                              self.control.__class__.__name__ )( value )

    def add_item_for_QComboBox ( self, value ):
        self.control.addItem( value )

        return (self.control.count() - 1)


    def find_item ( self, value ):
        """ Returns the index of the control item matching the specified
            *value*. If no matching item is found, it returns -1.
        """
        return getattr( self, 'find_item_for_' +
                              self.control.__class__.__name__ )( value )

    def find_item_for_QComboBox ( self, value ):
        return self.control.findText( value )


    def find_control ( self, x, y ):
        """ Finds and returns the topmost control at the specified (x, y )
            location, where ( x, y ) are in the control's local coordinate
            space. If no control is at the specified location, None is return.
        """
        x0, y0 = self.screen_position

        return adapted_control( QApplication.widgetAt( x0 + x, y0 + y ) )


    def add_page ( self, name, control ):
        """ Adds the page defined by *control* with the name *name* to the
            control (which should be some type of notebook control).
        """
        self.control.addTab( control(), name )


    def shrink_wrap ( self ):
        """ Resizes the control so that it fits snugly around its child
            controls.
        """
        # fixme: Not sure how to do this for Qt. Maybe we do not have to do
        # anything? For now we'll just print a message to log the call...
        from facets.extra.helper.debug import log_if

        log_if( 2, 'shrink_wrap called for: %s' % self.control )


    def drag ( self, data, type = None, request = 'copy', image = None ):
        """ Initiates a drag operation with the specified *data*. If *type* is
            **None**, the control will try to determine the kind of data being
            dragged from the data itself. Other than **None**, the legal values
            for *type* are: 'color', 'image', 'text', 'html', 'files', 'urls'
            and 'object'.

            *Request* specifies whether the data is to be copied ('copy'),
            moved ('move') or linked ('link'), with the default request being to
            copy the data.

            *Image* specifies an ImageResource image to be used while dragging
            to provide the user with some indication of what is being dragged.
            This may not be supported with all UI back-ends. If not supported,
            the *image* value is treated as *None*. A value of *None* indicates
            that the default drag image should be used.

            The result is a string indicating the action taken by the receiver
            (if any) of the data at the completion of the drag and drop
            operation. The possible values are: 'copy', 'move', 'link' and
            'ignore'.
        """
        if type is None:
            if isinstance( data, basestring ):
                type = 'text'
            elif isinstance( data, QColor ):
                type = 'color'
            elif isinstance( data, AnImageResource ):
                type = 'image'
                data = data.image
            elif isinstance( data, SequenceTypes ):
                type = 'urls'
                data = [ QUrl( item ) for item in data ]
            else:
                type = 'object'

        mime_data = getattr( self, '_drag_%s' % type,
                             self._drag_object )( data )
        drag      = QDrag( self.control )
        drag.setMimeData( mime_data )

        # Set up the drag image (if one was specified):
        if isinstance( image, AnImageResource ):
            bitmap   = image.bitmap
            idx, idy = image.width, image.height
            ratio    = max( idx, idy ) / 128.0
            if ratio > 1.0:
                # Create a scaled version of the image if it is larger than the
                # maximum nominal size:
                sdx = int( round( idx / ratio ) )
                sdy = int( round( idy / ratio ) )
                pm  = QPixmap( sdx, sdy )
                pm.fill( QColor( 0, 0, 0, 0 ) )
                painter = painter_for( pm )
                painter.drawPixmap( 0, 0, sdx, sdy, bitmap, 0, 0, idx, idy )
                painter.end()
                bitmap, idx, idy = pm, sdx, sdy

            drag.setPixmap( bitmap )
            drag.setHotSpot( QPoint( idx / 2, idy / 2 ) )

        return RequestAction[ drag.exec_() ]


    def _drag_color ( self, color ):
        mime_data = QMimeData()
        mime_data.setColorData( QVariant( color ) )

        return mime_data


    def _drag_image ( self, image ):
        mime_data = QMimeData()
        mime_data.setImageData( QVariant( image ) )

        return mime_data


    def _drag_text ( self, text ):
        mime_data = QMimeData()
        mime_data.setText( text )

        return mime_data


    def _drag_hmtl ( self, html ):
        mime_data = QMimeData()
        mime_data.setHtml( html )

        return mime_data


    def _drag_files ( self, files ):
        mime_data = QMimeData()
        mime_data.setUrls( [ QUrl( file ) for file in files ] )

        return mime_data


    def _drag_urls ( self, urls ):
        mime_data = QMimeData()
        mime_data.setUrls( urls )

        return mime_data


    def _drag_object ( self, object ):
        return PyMimeData( object )


    def activate ( self ):
        """ Makes sure that the control (which should be a top-level window) is
            on top of all other application windows. If it is not, then it will
            brought in front of all other windows.
        """
        self.visible = True
        self.control.raise_()
        self.control.activateWindow()

    #-- Special Signal/Slot Set-up Handlers ------------------------------------

    def _slot_text_change ( self, handler, connect ):
        from facets.extra.helper.debug import log_if
        log_if( 2, 'text change!' )

        control = self.control
        if isinstance( control, QComboBox ):
            control = control.lineEdit()

        signal = 'textEdited(QString)'
        if isinstance( control, QTextEdit ):
            signal = 'textChanged()'

        if connect:
            QObject.connect( control, SIGNAL( signal ), handler )
        else:
            QObject.disconnect( control, SIGNAL( signal ), handler )


    def _slot_text_enter ( self, handler, connect ):
        from facets.extra.helper.debug import log_if
        log_if( 2, 'text enter!' )

        control = self.control
        if isinstance( control, QComboBox ):
            control = control.lineEdit()

        if connect:
            QObject.connect( control, SIGNAL( 'editingFinished()' ), handler )
        else:
            QObject.disconnect( control, SIGNAL( 'editingFinished()' ),
                                handler )


    def _slot_clicked ( self, handler, connect ):
        from facets.extra.helper.debug import log_if
        log_if( 2, 'clicked!' )
        if connect:
            QObject.connect( self.control, SIGNAL( 'clicked()' ), handler )
        else:
            QObject.disconnect( self.control, SIGNAL( 'clicked()' ), handler )


    def _slot_checked ( self, handler, connect ):
        from facets.extra.helper.debug import log_if
        log_if( 2, 'checked!' )
        if connect:
            QObject.connect( self.control, SIGNAL( 'stateChanged(int)' ),
                             handler )
        else:
            QObject.disconnect( self.control, SIGNAL( 'stateChanged(int)' ),
                                handler)


    def _slot_choose ( self, handler, connect ):
        from facets.extra.helper.debug import log_if
        log_if( 2, 'choose!' )
        if connect:
            QObject.connect( self.control, SIGNAL( 'activated(QString)' ),
                             handler )
        else:
            QObject.disconnect( self.control, SIGNAL( 'activated(QString)' ),
                                handler )

    #-- Drag and Drop Event Handlers -------------------------------------------

    def _drag_enter ( self, event ):
        """ Handles a drag operation entering the control.
        """
        handler = getattr( self._drop_target, 'drag_enter', None )
        if handler is not None:
            handler( event )
        else:
            event.result = event.request


    def _drag_leave ( self, event ):
        """ Handles a drag operation leaving the control.
        """
        handler = getattr( self._drop_target, 'drag_leave', None )
        if handler is not None:
            handler( event )


    def _drag_move ( self, event ):
        """ Handles a drag operation moving across the control.
        """
        handler = getattr( self._drop_target, 'drag_move', None )
        if handler is not None:
            handler( event )
        else:
            event.result = event.request


    def _drag_drop ( self, event ):
        """ Handles a drop operation on the control.
        """
        handler = getattr( self._drop_target, 'drag_drop', None )
        if handler is not None:
            handler( event )
        else:
            event.result = event.request

    #-- Facet Event Handlers ---------------------------------------------------

    def _size_policy_set ( self, size_policy ):
        hpolicy, vpolicy = size_policy
        self.control.setSizePolicy( PolicyMap[ hpolicy ],
                                    PolicyMap[ vpolicy ] )

    #-- Private Methods --------------------------------------------------------

    def _erase_background ( self, event ):
        """ Never erase the background. The paint handler will do all of the
            required work.
        """
        pass


    def _screen_graphics_paint ( self, event ):
        """ Handles an overlap screen graphics widget getting a paint event.
        """
        sg = self._sg_control
        if sg is not None:
            painter = painter_for( sg.control )
            painter.drawPixmap( 0, 0, sg._pixmap )

#-------------------------------------------------------------------------------
#  'EventHandlers' class:
#-------------------------------------------------------------------------------

class EventHandlers ( QObject ):
    """ Qt event filter for a control whose event handlers are defined by
        toolkit 'set_event_handler' method calls.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self ):
        """ Initializes the object.
        """
        QObject.__init__( self )

        self.event_map = {}


    def eventFilter ( self, object, event ):
        """ Handles a Qt event by mapping it to a corresponding controller
            method (if any).
        """
        adapter = self.processEvent( object, event )
        if adapter is not None:
            return adapter.handled

        # Pass the request along to the superclass:
        return QObject.eventFilter( self, object, event )


    def processEvent ( self, object, event ):
        """ Handles a Qt event by mapping it to a corresponding controller
            method (if any).
        """
        # Try to convert the Qt event type to a GUI toolkit neutral name:
        name = EventMap.get( event.type(), None )
        if name is not None:
            handlers = []

            # Check to see if this is a mouse related event, which requires some
            # additional processing:
            if name in MouseEvents:
                handlers.extend( self.event_map.get( 'mouse', NoHandlers ) )

                # Now check to see if the name is also mouse button related,
                # which requires some additional qualification:
                if name in MouseButtons:
                    # Try to get the appropriate mouse button name:
                    prefix = MousePrefix.get( event.button(), None )
                    if prefix is None:
                        return None

                    # Create a composite name composed of the button name and
                    # the event type:
                    name = prefix + name

            # See if we have any methods to handle the event:
            handlers.extend( self.event_map.get( name, NoHandlers ) )
            if len( handlers ) > 0:
                from facets.extra.helper.debug import log_if
                log_if( 2 , 'event: %s' % name )

                # Create the right kind of adapted event:
                if name in DragDropEvents:
                    adapter = QtDrag( event, name = name )
                else:
                    adapter = QtUIEvent( event,
                        name            = name,
                        control_adapter = adapted_control( object )
                    )

                # Invoke the handler with the adapted version of the event:
                for handler in handlers:
                    handler( adapter )

                # Return whether or not we completely handled the event or not:
                if name in NeverHandledEvents:
                    adapter.handled = False

                return adapter

        return None

#-------------------------------------------------------------------------------
#  'EventWrapper' class:
#-------------------------------------------------------------------------------

class EventWrapper ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The handler to be invoked when the associated event occurs:
    handler = Any

    # The control adapter this event wrapper was created by:
    control_adapter = Instance( Control )

    #-- Public Methods ---------------------------------------------------------

    def process_event ( self, data = None ):
        self.handler(
            QtUIEvent( None, data            = data,
                             control_adapter = self.control_adapter )
        )

#-------------------------------------------------------------------------------
#  'Widget' class:
#-------------------------------------------------------------------------------

class Widget ( QWidget ):

    #-- Public Methods ---------------------------------------------------------

    def paintEvent ( self, event ):
        return self._processEvent( event )

    def resizeEvent ( self, event ):
        return self._processEvent( event )

    def facusInEvent ( self, event ):
        return self._processEvent( event )

    def focusOutEvent ( self, event ):
        return self._processEvent( event )

    def keyPressEvent ( self, event ):
        return self._processEvent( event )

    def keyReleaseEvent ( self, event ):
        return self._processEvent( event )

    def mousePressEvent ( self, event ):
        return self._processEvent( event )

    def mouseReleaseEvent ( self, event ):
        return self._processEvent( event )

    def mouseDoubleClickEvent ( self, event ):
        return self._processEvent( event )

    def mouseMoveEvent ( self, event ):
        return self._processEvent( event )

    def enterEvent ( self, event ):
        return self._processEvent( event )

    def leaveEvent ( self, event ):
        return self._processEvent( event )

    def wheelEvent ( self, event ):
        return self._processEvent( event )

    def closeEvent ( self, event ):
        return self._processEvent( event )

    def dragEnterEvent ( self, event ):
        return self._processEvent( event )

    def dragLeaveEvent ( self, event ):
        return self._processEvent( event )

    def dragMoveEvent ( self, event ):
        return self._processEvent( event )

    def dropEvent ( self, event ):
        return self._processEvent( event )

    #-- Private Methods --------------------------------------------------------

    def _processEvent ( self, event ):
        event_handlers = getattr( self, 'event_handlers', None )
        if event_handlers is not None:
            event_handlers.processEvent( self, event )

#-- EOF ------------------------------------------------------------------------