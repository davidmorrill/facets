"""
Creates a GUI toolkit neutral user interface for a specified UI object, where
the UI is "live", meaning that it immediately updates its underlying object(s).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt

from facets.core_api \
    import HasPrivateFacets, Instance, Int, Bool, Any

from facets.ui.adapters.layout \
    import Layout

from facets.ui.pyface.timer.api \
    import do_later

from ui_base \
    import BaseDialog

from ui_panel \
    import panel

from undo \
    import UndoHistory

from constants \
    import DefaultTitle

from colors \
    import WindowColor

from helper \
    import restore_window, save_window

from ui \
    import UI

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Types of supported windows:
NONMODAL = 0
MODAL    = 1
POPUP    = 2
POPOUT   = 3
POPOVER  = 4
INFO     = 5

# Types of 'popup' dialogs:
Popups = set( ( POPUP, POPOUT, POPOVER, INFO ) )

#-------------------------------------------------------------------------------
#  Creates a 'live update' GUI toolkit neutral user interface for a specified
#  UI object:
#-------------------------------------------------------------------------------

def ui_live ( ui, parent ):
    """ Creates a live, non-modal GUI toolkit neutral user interface for a
        specified UI object.
    """
    ui_dialog( ui, parent, NONMODAL )


def ui_livemodal ( ui, parent ):
    """ Creates a live, modal GUI toolkit neutral user interface for a
        specified UI object.
    """
    ui_dialog( ui, parent, MODAL )


def ui_popup ( ui, parent ):
    """ Creates a live, temporary popup GUI toolkit neutral user interface for
        a specified UI object.
    """
    ui_dialog( ui, parent, POPUP )


def ui_popout ( ui, parent ):
    """ Creates a live, temporary popup GUI toolkit neutral user interface for
        a specified UI object.
    """
    ui_dialog( ui, parent, POPOUT )


def ui_popover ( ui, parent ):
    """ Creates a live, temporary popup GUI toolkit neutral user interface for
        a specified UI object.
    """
    ui_dialog( ui, parent, POPOVER )


def ui_info ( ui, parent ):
    """ Creates a live, temporary popup GUI toolkit neutral user interface for
        a specified UI object.
    """
    ui_dialog( ui, parent, INFO )


def ui_dialog ( ui, parent, style ):
    """ Creates a live GUI toolkit neutral user interface for a specified UI
        object.
    """
    if ui.owner is None:
        ui.owner = LiveWindow()

    ui.owner.init( ui, parent, style )
    ui.control = control = ui.owner.control
    ui.control._parent   = parent

    try:
        ui.prepare_ui()
    except:
        ui.control.destroy()
        # fixme: Who sets 'ui' and why?...
        ui.control().ui = None
        ui.control      = None
        ui.owner        = None
        ui.result       = False
        raise

    ui.handler.position( ui.info )
    restore_window( ui, is_popup = (style in Popups) )

    from facets.extra.helper.debug import log_if
    log_if( 2, ui.control )

    control.update()

    control.modal = (style == MODAL)
    control.activate()

#-------------------------------------------------------------------------------
#  'LiveWindow' class:
#-------------------------------------------------------------------------------

class LiveWindow ( BaseDialog ):
    """ User interface window that immediately updates its underlying object(s).
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, ui, parent, style ):
        self.is_modal = (style == MODAL)
        self.rc       = None
        window_style  = set()
        view          = ui.view

        title = view.title
        if title == '':
            title = DefaultTitle

        history = ui.history
        window  = ui.control
        if window is not None:
            if history is not None:
                history.on_facet_set( self._on_undoable, 'undoable',
                                      remove = True )
                history.on_facet_set( self._on_redoable, 'redoable',
                                      remove = True )
                history.on_facet_set( self._on_revertable, 'undoable',
                                      remove = True )
            window.layout = None
            ui.reset()
        else:
            self.ui = ui
            if style == MODAL:
                if view.resizable:
                    window_style.add( 'resizable' )
                    window_style.add( 'min_max' )

                window_style.add( 'dialog' )
                window = toolkit().create_frame( parent, window_style, title )
            elif style == NONMODAL:
                if parent is not None:
                    window_style.add( 'non_modal_child' )

                window_style.add( 'frame' )
                window = toolkit().create_frame( parent, window_style, title )
            else:
                if len( window_style ) == 0:
                    window_style.add( 'simple' )

                # Only use the parent if it is part of a modal window; otherwise
                # just make it a top-level window:
                while parent is not None:
                    if parent.modal:
                        break

                    parent = parent.parent

                window = toolkit().create_frame( parent, window_style )
                window.set_event_handler( deactivate = self._on_close_popup )
                window.kind   = ui.kind
                self._monitor = None
                if style != POPOUT:
                    self._monitor = MouseMonitor( ui = ui )

            # Set the correct default window background color:
            window.background_color = WindowColor

            self.control = window
            window.set_event_handler(
                close = self._on_close_page,
                key   = self._on_key
            )

        self.set_icon( view.icon )
        buttons     = self.get_buttons( view )
        nbuttons    = len( buttons )
        no_buttons  = ((nbuttons == 1) and self.is_button( buttons[0], '' ))
        has_buttons = ((not no_buttons) and (nbuttons > 0))
        if has_buttons or ((view.menubar is not None) and (not view.undo)):
            if history is None:
                history = UndoHistory()
        else:
            history = None

        ui.history = history

        # Create the actual facets UI panel:
        sw = panel( ui, window )

        # Attempt an optimization that prevents creating nested vertical box
        # layouts:
        if isinstance( sw, Layout ) and sw.is_vertical:
            sw_layout = sw
        else:
            sw_layout = toolkit().create_box_layout()
            sw_layout.add( sw, stretch = 1 )

        # Check to see if we need to add any of the special function buttons:
        if (not no_buttons) and has_buttons:
            sw_layout.add( toolkit().create_separator( window, False ) )
            b_layout = toolkit().create_box_layout( False, align = 'right' )

            # Create a button for each button action:
            for button in buttons:
                button = self.coerce_button( button )
                if self.is_button( button, 'Undo' ):
                    self.undo = self.add_button( button, b_layout,
                                                 self._on_undo, False )
                    self.redo = self.add_button( button, b_layout,
                                                 self._on_redo, False, 'Redo' )
                    history.on_facet_set( self._on_undoable, 'undoable',
                                          dispatch = 'ui' )
                    history.on_facet_set( self._on_redoable, 'redoable',
                                          dispatch = 'ui' )
                    if history.can_undo:
                        self._on_undoable( True )

                    if history.can_redo:
                        self._on_redoable( True )

                elif self.is_button( button, 'Revert' ):
                    self.revert = self.add_button( button, b_layout,
                                                   self._on_revert, False )
                    history.on_facet_set( self._on_revertable, 'undoable',
                                          dispatch = 'ui' )
                    if history.can_undo:
                        self._on_revertable( True )

                elif self.is_button( button, 'OK' ):
                    self.ok = self.add_button( button, b_layout,
                                               self._on_ok_button )
                    ui.on_facet_set( self._on_error, 'errors',
                                     dispatch = 'ui' )

                elif self.is_button( button, 'Cancel' ):
                    self.add_button( button, b_layout, self._on_cancel_button )

                elif self.is_button( button, 'Help' ):
                    self.add_button( button, b_layout, self._on_help )

                elif not self.is_button( button, '' ):
                    self.add_button( button, b_layout )

            sw_layout.add( b_layout, fill = False, align = 'right',
                           left = 5, right = 5, top = 5, bottom = 5 )

        # Set the layout for the window:
        window.layout = sw_layout

        # Add the menu bar, tool bar and status bar (if any):
        self.add_menubar()
        self.add_toolbar()
        self.add_statusbar()

        # Lay out all of the dialog contents:
        window.shrink_wrap()


    def close ( self, rc = True ):
        """ Closes the dialog window.
        """
        control = self.control
        control.unset_event_handler(
            close = self._on_close_page,
            key   = self._on_key
        )
        ui        = self.ui
        ui.result = rc
        save_window( ui )
        if self.is_modal:
            control.result  = rc
            control.visible = False

        ui.finish()
        self.ui = self.undo = self.redo = self.revert = self.control = None

    #-- Control Event Handlers -------------------------------------------------

    def _on_ok_button ( self, event ):
        """ Handles the OK button being clicked.
        """
        self.rc = True
        self.control.close()


    def _on_cancel_button ( self, event ):
        """ Handles the Cancel button being clicked.
        """
        self.rc = False
        self.control.close()


    def _on_close_page ( self, event ):
        """ Handles the user clicking the window/dialog "close" button/icon.
        """
        rc = self.rc
        if rc is None:
            # If there is no explicit result code, use the default result
            # code specified by the view:
            rc = self.ui.view.close_result

        if rc is False:
            self._on_cancel( event )
        else:
            self._on_ok( event )

        # Reset the result code in case the ui handler cancelled the close,
        # so that it won't affect the result if the user next clicks the
        # window 'close' button:
        self.rc = None


    def _on_close_popup ( self, event ):
        """ Handles the user giving focus to another window for a 'popup' view.
        """
        self.close_popup()


    def close_popup ( self ):
        # Close the window if it has not already been closed:
        ui = getattr( self, 'ui', None )
        if (ui is not None) and (ui.info.ui is not None):
            if self._on_ok() and (self._monitor is not None):
                self._monitor.stop()
                self._monitor = None


    def _on_ok ( self, event = None ):
        """ Handles the user clicking the **OK** button.
        """
        if self.ui.handler.close( self.ui.info, True ):
            self.control.unset_event_handler(
                deactivate = self._on_close_popup
            )
            self.close()

            return True

        return False


    def _on_key ( self, event ):
        """ Handles the user pressing the Escape key.
        """
        if event.key_code == 'Esc':
            self._on_close_page( event )


    def _on_cancel ( self, event ):
        """ Handles a request to cancel all changes.
        """
        if self.ui.handler.close( self.ui.info, False ):
            self._on_revert( event )
            self.close( False )

            return True

        return False


    def _on_error ( self, errors ):
        """ Handles editing errors.
        """
        self.ok.enabled = (errors == 0)

#-------------------------------------------------------------------------------
#  'MouseMonitor' class:
#-------------------------------------------------------------------------------

class MouseMonitor ( HasPrivateFacets ):
    """ Monitors a specified window and closes it the first time the mouse
        pointer leaves the window.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The Facets UI being monitored:
    ui = Instance( UI )

    # Has the associated pop-up been activated yet:
    is_activated = Bool( False )

    # Is the associated pop-up an 'info' popup?
    is_info = Bool( False )

    # The width of the trembling hand 'dead zone':
    border = Int( 3 )

    # The initial distance of the mouse pointer from the control:
    distance = Int( 0 )

    # The initial mouse position:
    mouse = Any

    # The timer associated with this monitor:
    timer = Any

    #-- Public Methods ---------------------------------------------------------

    def stop ( self ):
        """ Stops the mouse monitor.
        """
        self.timer()
        self.timer = self.ui = None

    #-- Private Methods --------------------------------------------------------

    def facets_init ( self ):
        """ Completes the initialization of the object.
        """
        kind              = self.ui.view.kind
        self.is_activated = self.is_info = (kind == 'info')
        if kind == 'popup':
            self.border = 10

        self.timer = toolkit().create_timer( 100, self._timer_pop )

    #-- Event Handlers ---------------------------------------------------------

    def _timer_pop ( self ):
        """ Handles the timer popping.
        """
        ui      = self.ui
        control = ui.control
        if control is None:
            # Looks like someone forgot to tell us that the ui has been closed:
            self.stop()

            return

        # Make sure that the initial distance of the mouse pointer to the
        # control has been set:
        mx, my = toolkit().mouse_position()
        if self.mouse is None:
            self.mouse    = ( mx, my )
            self.distance = self._distance( mx, my )

        if self.is_activated:
            # Don't close the popup if any mouse buttons are currently pressed:
            if len( toolkit().mouse_buttons() ) > 0:
                return

            # Check for the special case of the mouse pointer having to be
            # within the original bounds of the object the popup was created
            # for:
            if self.is_info:
                parent = control._parent
                if isinstance( parent, tuple ):
                    px, py, pdx, pdy = parent
                else:
                    px,  py  = parent.screen_position
                    pdx, pdy = parent.size

                if ((mx < px) or (mx >= (px + pdx)) or
                    (my < py) or (my >= (py + pdy))):
                    do_later( ui.owner.close_popup )
                    self.is_activated = False
            else:
                # Allow for a 'dead zone' border around the window to allow for
                # small motor control problems:
                if self._distance( mx, my ) > self.border:
                    control_at = toolkit().control_at( mx, my )
                    while control_at is not None:
                        if control_at is control:
                            return

                        control_at = control_at.parent

                    do_later( ui.owner.close_popup )
                    self.is_activated = False
        else:
            distance = self._distance( mx, my )
            if distance == 0:
                # If the pointer is now in the popup view, activate it:
                self.is_activated = True
            elif (distance > (self.distance + 25)):
                # If the mouse has moved too far away from the popup view, then
                # close it:
                do_later( ui.owner.close_popup )

    #-- Public Methods ---------------------------------------------------------

    def _distance ( self, x, y ):
        """ Returns the distance of a specified point to the control. A result
            of 0 indicates that the point is inside of the control.
        """
        control  = self.ui.control
        cx, cy   = control.screen_position
        cdx, cdy = control.size
        dx       = max( 0, cx - x, x - (cx + cdx) )
        dy       = max( 0, cy - y, y - (cy + cdy) )

        return int( sqrt( (dx * dx) + (dy * dy) ) )

#-- EOF ------------------------------------------------------------------------
