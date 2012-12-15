"""
Defines a text editor which displays a text field and maintains a history
of previously entered values.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Int, Bool, on_facet_set, BasicEditorFactory

from facets.ui.pyface.timer.api \
    import do_later

from facets.ui.controls.history_control \
    import HistoryControl

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_HistoryEditor' class:
#-------------------------------------------------------------------------------

class _HistoryEditor ( Editor ):
    """ Simple style text editor, which displays a text field and maintains a
        history of previously entered values, the maximum number of which is
        specified by the 'entries' facet of the HistoryEditor factory.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The history control:
    history = Any

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.history = history = HistoryControl(
            value    = self.value,
            entries  = self.factory.entries,
            auto_set = self.factory.auto_set
        )
        self.adapter = history.create_control( parent )

        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.history.dispose()
        self.history = None

        super( _HistoryEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if not self._dont_update:
            self._dont_update  = True
            self.history.value = self.value
            self.history.error = False
            self._dont_update  = False


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        pass

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        self.history.history = \
            prefs.get( 'history', [] )[ : self.factory.entries ]


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        # If the view closed successfully, try to update the history with the
        # current value:
        if self.ui.result:
            self._dont_update = True
            self.history.set_value( self.value )
            self._dont_update = False

        return { 'history': self.history.history[:] }

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'history:value' )
    def _value_modified ( self, value ):
        """ Handles the history object's 'value' facet being changed.
        """
        if not self._dont_update:
            history = self.history
            try:
                self._dont_update = True
                self.value        = history.value
                history.error     = False
            except:
                history.error = True

            do_later( self.set, _dont_update = False )

#-------------------------------------------------------------------------------
#  'HistoryEditor' class:
#-------------------------------------------------------------------------------

class HistoryEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The class used to construct editor objects:
    klass = _HistoryEditor

    # The number of entries in the history:
    entries = Int( 10 )

    # Should each keystroke update the value (or only the enter key, tab, etc.)?
    auto_set = Bool( False )

#-- EOF ------------------------------------------------------------------------