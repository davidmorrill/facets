"""
A feature-enabled tool for editing image-based themes.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Any, Image, Theme, ATheme, View, UItem, \
           ThemeEditor as TheThemeEditor

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ThemeEditor' class:
#-------------------------------------------------------------------------------

class ThemeEditor ( Tool ):
    """ Allows a user to edit a theme (or image that is automatically converted
        to a theme.
    """

    #-- Facet Definitions ----------------------------------------------------------

    # The name of the tool:
    name = Str( 'Theme Editor' )

    # A value to convert to a theme to edit:
    value = Any( connect = 'to: image used to define a theme' )

    # An image to use as the basis for the theme to edit:
    image = Image

    # The theme being edited by the tool:
    theme = ATheme( '@xform:li', connect = 'both: theme being edited' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( UItem( 'theme', editor = TheThemeEditor() ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self, value ):
        """ Handles the 'value' facet being changed.
        """
        if isinstance( value, ( list, tuple ) ) and (len( value ) > 0):
            value = value[0]

        if isinstance( value, ( basestring, AnImageResource ) ):
            self.image = value
        else:
            self.image = '@xform:b'


    def _image_set ( self, image ):
        """ Handles the 'image' facet being changed.
        """
        self.theme = Theme( image, border = 0, content = 0, label = 0 )

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    ThemeEditor( value = '@std:GL5TB' ).edit_facets()

#-- EOF ------------------------------------------------------------------------
