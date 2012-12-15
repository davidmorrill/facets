"""
Creates a GUI toolkit neutral user interface for a specified UI object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from ui_base \
    import BaseDialog

from ui_panel \
    import panel

from helper \
    import restore_window, save_window

from constants \
    import DefaultTitle

from colors \
    import WindowColor

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  UI Creation Factories:
#-------------------------------------------------------------------------------

def ui_modal ( ui, parent ):
    """ Creates a modal GUI toolkit neutral user interface for a specified UI
        object.
    """
    ui_dialog( ui, parent, True )


def ui_nonmodal ( ui, parent ):
    """ Creates a non-modal GUI toolkit neutral user interface for a specified
        UI object.
    """
    ui_dialog( ui, parent, False )


def ui_dialog ( ui, parent, is_modal ):
    """ Creates a GUI toolkit neutral dialog box for a specified UI object.

        Changes are not immediately applied to the underlying object. The user
        must click **Apply** or **OK** to apply changes. The user can revert
        changes by clicking **Revert** or **Cancel**.
    """
    if ui.owner is None:
        ui.owner = ModalDialog()

    ui.owner.init( ui, parent, is_modal )
    ui.control = ui.owner.control
    # fixme: Why do we need this?...
    ui.control._parent = parent

    try:
        ui.prepare_ui()
    except:
        ui.control.destroy()
        ui.control.ui = None
        ui.control    = None
        ui.owner      = None
        ui.result     = False
        raise

    ui.handler.position( ui.info )
    restore_window( ui )

    ui.control.modal   = is_modal
    ui.control.visible = True

#-------------------------------------------------------------------------------
#  'ModalDialog' class:
#-------------------------------------------------------------------------------

class ModalDialog ( BaseDialog ):
    """ Modal dialog box for Facets-based user interfaces.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, ui, parent, is_modal ):
        self.is_modal = is_modal
        style         = set()
        view          = ui.view
        if view.resizable:
            style.add( 'resizable' )

        title = view.title
        if title == '':
            title = DefaultTitle

        revert = apply = False
        window = ui.control
        if window is not None:
            window.layout = None
            ui.reset()
            if hasattr( self, 'revert' ):
                revert = self.revert.enabled

            if hasattr( self, 'apply' ):
                apply = self.apply.enabled
        else:
            self.ui = ui
            if is_modal:
                style.add( 'dialog' )
                window = toolkit().create_frame( parent, style, title )
            else:
                style.add( 'frame' )
                window = toolkit().create_frame( parent, style, title )

            window.background_color = WindowColor
            self.control            = window
            self.set_icon( view.icon )
            window.set_event_handler(
                close = self._on_close_page,
                key   = self._on_key
            )

            # Create the 'context' copies we will need while editing:
            context     = ui.context
            ui._context = context
            ui.context  = self._copy_context( context )
            ui._revert  = self._copy_context( context )

        # Create the actual facet sheet panel:
        sw_layout = toolkit().create_box_layout()
        sw_layout.add( panel( ui, window ), stretch = 1 )

        buttons  = self.get_buttons( view )
        nbuttons = len( buttons )
        if (nbuttons != 1) or (not self.is_button( buttons[0], '' )):

            # Create the necessary special function buttons:
            sw_layout.add( toolkit().create_separator( window, False ) )
            b_layout = toolkit().create_box_layout( False, align = 'right' )

            for button in buttons:
                if self.is_button( button, 'Apply' ):
                    self.apply = self.add_button( button, b_layout,
                                                  self._on_apply, apply )
                    ui.on_facet_set( self._on_applyable, 'modified',
                                     dispatch = 'ui' )

                elif self.is_button( button, 'Revert' ):
                    self.revert = self.add_button( button, b_layout,
                                                   self._on_revert, revert )

                elif self.is_button( button, 'OK' ):
                    self.ok = self.add_button( button, b_layout, self._on_ok )
                    ui.on_facet_set( self._on_error, 'errors',
                                     dispatch = 'ui' )

                elif self.is_button( button, 'Cancel' ):
                    self.add_button( button, b_layout, self._on_cancel )

                elif self.is_button( button, 'Help' ):
                    self.add_button( button, b_layout, self._on_help )

                elif not self.is_button( button, '' ):
                    self.add_button( button, b_layout )

            sw_layout.add( b_layout, align = 'right', left = 5, right = 5,
                           top = 5, bottom = 5 )

        # Add the menu bar, tool bar and status bar (if any):
        self.add_menubar()
        self.add_toolbar()
        self.add_statusbar()

        # Lay all of the dialog contents out:
        window.layout = sw_layout
        window.shrink_wrap()


    def close ( self, rc = True ):
        """ Closes the dialog window.
        """
        ui = self.ui
        ui.result = rc
        save_window( ui )
        if self.is_modal:
            self.control.result  = rc
            self.control.visible = False

        ui.finish()
        self.ui = self.apply = self.revert = self.help = self.control = None

    #-- Private Methods --------------------------------------------------------

    def _copy_context ( self, context ):
        """ Creates a copy of a *context* dictionary.
        """
        result = {}
        for name, value in context.iteritems():
            if value is not None:
                result[ name ] = value.clone_facets()
            else:
                result[ name ] = None

        return result


    def _apply_context ( self, from_context, to_context ):
        """ Applies the facets in the *from_context* to the *to_context*.
        """
        for name, value in from_context.iteritems():
            if value is not None:
                to_context[ name ].copy_facets( value )
            else:
                to_context[ name ] = None

        if to_context is self.ui._context:
            on_apply = self.ui.view.on_apply
            if on_apply is not None:
                on_apply()

    #-- Control Event Handlers -------------------------------------------------

    def _on_close_page ( self, event ):
        """ Handles the user clicking the window/dialog "close" button/icon.
        """
        if self.ui.view.close_result == True:
            self._on_ok( event )
        else:
            self._on_cancel( event )


    def _on_ok ( self, event = None ):
        """ Closes the window and saves changes (if allowed by the handler).
        """
        if self.ui.handler.close( self.ui.info, True ):
            self._apply_context( self.ui.context, self.ui._context )
            self.close()


    def _on_cancel ( self, event = None ):
        """ Closes the window and discards changes (if allowed by the handler).
        """
        if self.ui.handler.close( self.ui.info, False ):
            self._apply_context( self.ui._revert, self.ui._context )
            self.close( False )


    def _on_help ( self, event ):
        """ Handles the **Help** button being clicked.
        """
        self.ui.handler.show_help( self.ui.info, event.control )


    def _on_key ( self, event ):
        """ Handles the user pressing the Escape key.
        """
        if event.key_code == 'Esc':
            self._on_close_page( event )


    def _on_apply ( self, event ):
        """ Handles a request to apply changes.
        """
        ui = self.ui
        self._apply_context( ui.context, ui._context )
        self.revert.enabled = True
        ui.handler.apply( ui.info )
        ui.modified = False


    def _on_revert ( self, event ):
        """ Handles a request to revert changes.
        """
        ui = self.ui
        self._apply_context( ui._revert, ui.context )
        self._apply_context( ui._revert, ui._context )
        self.revert.enabled = False
        ui.handler.revert( ui.info )
        ui.modified = False


    def _on_applyable ( self, state ):
        """ Handles a change to the "modified" state of the user interface .
        """
        self.apply.enabled = state


    def _on_error ( self, errors ):
        """ Handles editing errors.
        """
        self.ok.enabled = (errors == 0)

#-- EOF ------------------------------------------------------------------------