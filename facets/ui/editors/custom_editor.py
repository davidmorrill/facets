"""
Defines the editor and editor factory used to wrap a non-Facets based custom
control.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Callable, Tuple, toolkit, EditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The colors used to mark a custom control that failed to initialize correctly:
ErrorBackground = ( 255, 0, 0 )
ErrorForeground = ( 255, 255, 255 )

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( EditorFactory ):
    """ Editor factory for custom editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Factory function used to create the custom control:
    factory = Callable

    # Arguments to be passed to the user's custom editor factory:
    args = Tuple

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, *args, **facets ):
        if len( args ) >= 1:
            self.factory = args[0]
            self.args    = args[1:]

        super( CustomEditor, self ).__init__( **facets )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return _CustomEditor( factory     = self,
                              ui          = ui,
                              object      = object,
                              name        = name,
                              description = description )


    def custom_editor ( self, ui, object, name, description ):
        return _CustomEditor( factory     = self,
                              ui          = ui,
                              object      = object,
                              name        = name,
                              description = description )


    def text_editor ( self, ui, object, name, description ):
        return _CustomEditor( factory     = self,
                              ui          = ui,
                              object      = object,
                              name        = name,
                              description = description )


    def readonly_editor ( self, ui, object, name, description ):
        return _CustomEditor( factory     = self,
                              ui          = ui,
                              object      = object,
                              name        = name,
                              description = description )

#-------------------------------------------------------------------------------
#  '_CustomEditor' class:
#-------------------------------------------------------------------------------

class _CustomEditor ( Editor ):
    """ Wrapper for a custom editor control.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory.factory
        if factory is not None:
            self.control = factory( *(( parent, self ) + self.factory.args) )

        if self.control is None:
            self.adapter = control = toolkit().create_label(
                parent,
                'An error occurred creating a custom editor.\nPlease contact '
                'the developer.'
            )
            control.background_color = ErrorBackground
            control.foreground_color = ErrorForeground

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        pass

#-- EOF ------------------------------------------------------------------------