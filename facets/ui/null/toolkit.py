"""
Defines the concrete implementations of the facets Toolkit interface for
    the 'null' (do nothing) user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.toolkit \
    import Toolkit

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

the_null_editor_factory = None

def null_editor_factory ( ):
    """ Returns the dummy singleton editor factory.
    """
    global the_null_editor_factory

    if the_null_editor_factory is None:
        from facets.ui.editor_factory import EditorFactory

        the_null_editor_factory = EditorFactory()

    return the_null_editor_factory

#-------------------------------------------------------------------------------
#  'GUIToolkit' class:
#-------------------------------------------------------------------------------

class GUIToolkit ( Toolkit ):

    #-- GUI Toolkit Dependent Facet Definitions --------------------------------

    def color_facet ( self, *args, **facets ):
        import facets.ui.null.editors.color_facet as ct

        return ct.NullColor( *args, **facets )


    def rgb_color_facet ( self, *args, **facets ):
        import facets.ui.null.editors.rgb_color_facet as rgbct

        return rgbct.RGBColor( *args, **facets )


    def font_facet ( self, *args, **facets ):
        import facets.ui.null.editors.font_facet as ft

        return ft.NullFont( *args, **facets )


    def kiva_font_facet ( self, *args, **facets ):
        import facets.ui.null.editors.font_facet as ft

        return ft.NullFont( *args, **facets )


    def constants ( self, *args, **facets ):
        return { 'WindowColor': ( 236 / 255.0, 233 / 255.0,
                                  216 / 255.0, 1.0 ) }


    def screen_size ( self ):
        """ Returns a tuple of the form (width,height) containing the size of
            the user's display.
        """
        return ( 0, 0 )


    def scrollbar_size ( self ):
        """ Returns a tuple of the form (width,height) containing the standard
            width of a vertical scrollbar, and the standard height of a
            horizontal scrollbar.
        """
        return ( 0, 0 )


    def is_application_running ( self ):
        """ Returns whether or not the application object has been created and
            is running its event loop.
        """
        return False


    def run_application ( self, app_info ):
        """ Set up a dummy facets UI object that indicates that the requested
            UI returned a False result.
        """
        app_info.ui = DummyUI()

    #-- 'EditorFactory' Factory Methods ----------------------------------------

    def __getattribute__ ( self, attr ):
        """ Return a method that returns null_editor_factory for any request to
            an unimplemented ``*_editor()`` method.

            This must be __getattribute__ to make sure that we override the
            definitions in the superclass which raise NotImplementedError.
        """
        if attr.endswith( '_editor' ):
            return lambda *args, **kwds: null_editor_factory()
        else:
            return super( GUIToolkit, self ).__getattribute__( attr )

#-------------------------------------------------------------------------------
#  'DummyUI' class:
#-------------------------------------------------------------------------------

class DummyUI ( object ):
    """ Simulates a dummy facets ui UI object.
    """

    def __init__ ( self ):
        """ Initializes the object.
        """
        self.result = False

#-- EOF ------------------------------------------------------------------------
