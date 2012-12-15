"""
Define an editor that displays a string value as a title.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import ATheme, Theme, BasicEditorFactory, on_facet_set

from facets.ui.controls.image_text \
    import ImageText

from facets.ui.editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_TitleEditor' class:
#-------------------------------------------------------------------------------

class _TitleEditor ( Editor ):

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._control = ImageText( theme = self.factory.theme )
        self.adapter  = self._control.create_control( parent )

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        self._control.text = self.str_value

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:theme' )
    def _theme_modified ( self ):
        self._control.theme = self.factory.theme

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

class TitleEditor ( BasicEditorFactory ):
    """ Editor factory for title editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the Editor class to be instantiated:
    klass = _TitleEditor

    # The theme to use for displaying the title:
    theme = ATheme( Theme( '@facets:heading', content = ( 6, 0 ) ),
                    facet_value = True )

#-- EOF ------------------------------------------------------------------------