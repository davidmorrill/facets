"""
Defines a completely empty editor, intended to be used as a spacer.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import BasicEditorFactory, toolkit

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_NullEditor' class:
#-------------------------------------------------------------------------------

class _NullEditor ( Editor ):
    """ A completely empty editor.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.adapter = control = toolkit().create_control( parent )
        control.set(
            size             = ( 1, 1 ),
            background_color = control.parent.background_color,
            size_policy      = ( 'expanding', 'expanding' )
        )

        control.set_event_handler( paint = self._on_paint )


    def dispose ( self ):
        """ Disposes of the editor.
        """
        self.adapter.unset_event_handler( paint = self._on_paint )

        super( _NullEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        pass

    #-- Control Event Handlers -------------------------------------------------

    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        self.adapter.graphics_buffer.copy()

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

NullEditor = BasicEditorFactory( klass = _NullEditor )

#-- EOF ------------------------------------------------------------------------