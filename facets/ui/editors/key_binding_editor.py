"""
Defines the key binding editor for use with the KeyBinding class. This is a
specialized editor used to associate a particular key with a control (i.e.,
the key binding editor).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Event, Bool, Control, \
           BasicEditorFactory, toolkit

from facets.ui.pyface.api \
    import confirm, NO

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Colors used to draw the KeyBindingControl:
FOCUS_COLOR  = ( 255, 0, 0 )
NORMAL_COLOR = ( 0, 0, 0 )

#-------------------------------------------------------------------------------
#  '_KeyBindingEditor' class:
#-------------------------------------------------------------------------------

class _KeyBindingEditor ( Editor ):
    """ An editor for modifying bindings of keys to controls.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Does the editor's control have focus currently?
    has_focus = Bool( False )

    # Keyboard event:
    key = Event

    # Clear field event:
    clear = Event

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        kbc          = KeyBindingCtrl( editor = self )
        self.adapter = adapter = kbc.create_control( parent )
        adapter.size = ( 160, 19 )

        self.set_tooltip()


    # fixme: Is this method even used?
    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        try:
            self.value = value = key_event_to_name( event )
            self._binding.text = value
        except:
            pass


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.adapter.refresh()


    def update_focus ( self, has_focus ):
        """ Updates the current focus setting of the control.
        """
        if has_focus:
            self.object.owner.focus_owner = self._binding

    #-- Facet Event Handlers ---------------------------------------------------

    def _key_set ( self, key ):
        """ Handles a keyboard event.
        """
        binding     = self.object
        key_name    = key.key_code
        cur_binding = binding.owner.key_binding_for( binding, key_name )
        if cur_binding is not None:
            if confirm( None,
                        "'%s' has already been assigned to '%s'.\n"
                        "Do you wish to continue?" % (
                        key_name, cur_binding.description ),
                        'Duplicate Key Definition' ) == NO:
                return

        self.value = key_name


    def _clear_set ( self ):
        """ Handles a clear field event.
        """
        self.value = ''

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

KeyBindingEditor = BasicEditorFactory( klass = _KeyBindingEditor )

#-------------------------------------------------------------------------------
#  'KeyBindingCtrl' class:
#-------------------------------------------------------------------------------

class KeyBindingCtrl ( HasPrivateFacets ):
    """ Control for editing key bindings.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The Control used to implement the control:
    control = Instance( Control )

    # The controlling Editor object:
    editor = Instance( Editor )

    #-- Public Methods ---------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the underlying control.
        """
        self.control = control = toolkit().create_control(
            parent, handle_keys = True
        )
        control.min_size = ( 18, 18 )

        control.set_event_handler(
            paint       = self._paint,
            get_focus   = self._get_focus,
            lose_focus  = self._lose_focus,
            left_down   = self._set_focus,
            left_dclick = self._clear_contents,
            key         = self._on_char
        )

        return control

    #-- Control Event Handlers -------------------------------------------------

    def _on_char ( self, event ):
        """ Handle keyboard keys being pressed.
        """
        self.editor.key = event


    def _paint ( self, event ):
        """ Updates the screen.
        """
        g      = self.control.graphics
        dx, dy = self.control.size
        if self.editor.has_focus:
            g.pen = FOCUS_COLOR
            g.draw_rectangle( 0, 0, dx, dy )
            g.draw_rectangle( 1, 1, dx - 2, dy - 2 )
        else:
            g.pen = NORMAL_COLOR
            g.draw_rectangle( 0, 0, dx, dy )

        g.font = self.control.font
        g.draw_text( self.editor.str_value, 5, 3 )


    def _set_focus ( self, event ):
        """ Sets the keyboard focus to this window.
        """
        self.control.set_focus()


    def _get_focus ( self, event ):
        """ Handles getting the focus.
        """
        self.editor.has_focus = True
        self.control.refresh()


    def _lose_focus ( self, event ):
        """ Handles losing the focus.
        """
        self.editor.has_focus = False
        self.control.refresh()


    def _clear_contents ( self, event ):
        """ Handles the user double clicking the control to clear its contents.
        """
        self.editor.clear = True

#-- EOF ------------------------------------------------------------------------