"""
A feature-enabled tool for editing themes stored in the Facets image library.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, View, Item, ThemeEditor

from facets.extra.helper.image_library_editor \
    import ImageLibraryEditor, ImageLibraryItem

#-------------------------------------------------------------------------------
#  'ImageThemeItem' class:
#-------------------------------------------------------------------------------

class ImageThemeItem ( ImageLibraryItem ):
    """ Represents an ImageInfo object whose Theme is being edited by an
        ImageThemeEditor.
    """

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'theme',
              show_label = False,
              editor     = ThemeEditor()
        )
    )

#-------------------------------------------------------------------------------
#  'ImageThemeEditor' class:
#-------------------------------------------------------------------------------

class ImageThemeEditor ( ImageLibraryEditor ):
    """ Allows a user to edit the Theme associated with ImageInfo objects
        whose corresponding image names are passed to it.
    """

    #-- Overridden ImageLibraryEditor Class Constants --------------------------

    # The persistence id for the image library editor:
    editor_id = 'facets.extra.tools.image_theme_editor.ImageThemeEditor'

    # Editor item factory class:
    item_class = ImageThemeItem

    #-- Overridden ImageLibraryEditor Facets --------------------------------

    # The label/title of the editor for use in the view:
    editor_title = 'Image Theme Editor'

    #-- Facet Definitions ----------------------------------------------------------

    # The name of the tool:
    name = Str( 'Image Theme Editor' )

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    ImageThemeEditor( image_names = [
        '@std:BlackChromeT', '@std:BlackChromeB', '@std:GL5', '@std:GL5TB'
    ] ).edit_facets()

#-- EOF ------------------------------------------------------------------------