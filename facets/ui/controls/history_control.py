"""
Defines a text entry field (actually a combobox) with a drop-down list of
values previously entered into the control.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Str, List, Int, Bool, Control, toolkit

from facets.ui.pyface.timer.api \
    import do_later

from facets.ui.colors \
    import OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  'HistoryControl' class:
#-------------------------------------------------------------------------------

class HistoryControl ( HasPrivateFacets ):

    # The underlying control:
    control = Instance( Control )

    # The current value of the control:
    value = Str

    # Should 'value' be updated on every keystroke?
    auto_set = Bool( False )

    # The current history of the control:
    history = List( Str )

    # The maximum number of history entries allowed:
    entries = Int( 10 )

    # Is the current value valid?
    error = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the control.
        """
        self.control = control = toolkit().create_combobox( parent, True )
        for item in self.history:
            control.add_item( item )

        control.value = self.value
        control.set_event_handler(
            choose     = self._update_value,
            lose_focus = self._kill_focus,
            text_enter = self._update_text_value
        )
        if self.auto_set:
            control.set_event_handler( text_change = self._update_value_only )

        return control


    def dispose ( self ):
        """ Disposes of the control at the end of its life cycle.
        """
        control = self.control
        control.unset_event_handler(
            picked     = self._update_value,
            lose_focus = self._kill_focus,
            text_enter = self._update_text_value
        )
        if self.auto_set:
            control.unset_event_handler( text_change = self._update_value_only )


    def set_value ( self, value ):
        """ Sets the specified value and adds it to the history.
        """
        self._update( value )

    #-- Facets Event Handlers --------------------------------------------------

    def _value_set ( self, value ):
        """ Handles the 'value' facet being changed.
        """
        if not self._no_update:
            control = self.control
            if control is not None:
                control.value = value
                self._restore = False


    def _history_set ( self ):
        """ Handles the 'history' being changed.
        """
        if not self._no_update:
            if self._first_time is None:
                self._first_time = False
                if (self.value == '') and (len( self.history ) > 0):
                    self.value = self.history[0]

            self._load_history( select = False )


    def _error_set ( self, error ):
        """ Handles the 'error' facet being changed.
        """
        self.control.background_color = ErrorColor if error else OKColor
        self.control.refresh()

    #-- Control Event Handlers -------------------------------------------------

    def _update_value ( self, event ):
        """ Handles the user selecting something from the drop-down list of the
            combobox.
        """
        self._update( event.value )


    def _update_value_only ( self, event ):
        """ Handles the user typing into the text field in 'auto_set' mode.
        """
        self._no_update = True
        self.value      = event.value
        self._no_update = False


    def _update_text_value ( self, event, select = True ):
        """ Handles the user typing something into the text field of the
            combobox.
        """
        if not self._no_update:
            self._update( self.control.value, select )


    def _kill_focus ( self, event ):
        """ Handles the combobox losing focus.
        """
        self._update_text_value( event, False )
        event.handled = False

    #-- Private Methods --------------------------------------------------------

    def _update ( self, value, select = True ):
        """ Updates the value and history list based on a specified value.
        """
        self._no_update = True

        if value.strip() != '':
            history = self.history
            if (len( history ) == 0) or (value != history[0]):
                if value in history:
                    history.remove( value )

                history.insert( 0, value )
                del history[ self.entries: ]
                self._load_history( value, select )

        self.value = value

        self._no_update = False


    def _load_history ( self, restore = None, select = True ):
        """ Loads the current history list into the control.
        """
        control = self.control
        control.frozen = True

        if restore is None:
            restore = control.value

        control.clear()
        for value in self.history:
            control.add_item( value )

        self._restore = True
        do_later( self._thaw_value, restore, select )


    def _thaw_value ( self, restore, select ):
        """ Restores the value of the combobox control.
        """
        control = self.control
        if control is not None:
            if self._restore:
                control.value = restore

                if select:
                    control.selection = ( 0, len( restore ) )

            control.frozen = False

#-- EOF ------------------------------------------------------------------------