"""
Defines the BasicUIEditor class, which allows creating editors that define
their function by creating an embedded Facets UI.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Instance

from facets.ui.ui \
    import UI

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'UIEditor' base class:
#-------------------------------------------------------------------------------

class UIEditor ( Editor ):
    """ An editor that creates an embedded Facets UI.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The Facets UI created by the editor:
    editor_ui = Instance( UI )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.editor_ui = self.init_ui( parent ).set( parent = self.ui )
        self.adapter   = self.editor_ui.control


    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        return self.value.edit_facets(
            view    = self.facet_view(),
            context = { 'object': self.value, 'editor': self },
            parent  = parent,
            kind    = 'editor'
        )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        # Do nothing, since the embedded facets UI should handle the updates
        # itself, without our meddling:
        pass


    def dispose ( self ):
        """ Disposes of the contents of the editor.
        """
        # Make sure the imbedded facets UI is disposed of properly:
        if self.editor_ui is not None:
            self.editor_ui.dispose()
            del self.editor_ui

        super( UIEditor, self ).dispose()


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self.editor_ui.get_error_controls()

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        self.editor_ui.set_prefs( prefs )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return self.editor_ui.get_prefs()

#-- EOF ------------------------------------------------------------------------