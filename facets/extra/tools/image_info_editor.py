"""
A feature-enabled tool for editing the information associated with images
stored in the Facets image library.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import View, HGroup, VGroup, HSplit, Item, Label, ListStrEditor

from facets.extra.helper.image_library_editor \
    import ImageLibraryEditor, ImageLibraryItem

from facets.extra.helper.themes \
    import InsetTheme

#-------------------------------------------------------------------------------
#  'ImageInfoItem' class:
#-------------------------------------------------------------------------------

class ImageInfoItem ( ImageLibraryItem ):
    """ Represents an ImageInfo object whose information is being edited by an
        ImageInfoEditor.
    """

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            VGroup(
                HGroup( Item( 'name',     springy = True ),
                        Item( 'category', springy = True ),
                        group_theme = InsetTheme ),
                VGroup(
                    Item( 'description', style = 'custom' ),
                    group_theme = InsetTheme
                ),
                VGroup(
                    Item( 'copyright',
                          label = '   Copyright',
                          style = 'custom' ),
                    group_theme = InsetTheme
                ),
                group_theme = '@std:GL5',
            ),
            VGroup(
                HSplit(
                    VGroup(
                        Label( 'Keywords', InsetTheme ),
                        Item( 'keywords',
                              editor = ListStrEditor( auto_add = True ) ),
                        group_theme = '@std:XG1',
                        show_labels = False,
                    ),
                    VGroup(
                        Label( 'License', InsetTheme ),
                        Item( 'license', style = 'custom' ),
                        group_theme = '@std:XG1',
                        show_labels = False,
                    ),
                    id = 'splitter'
                ),
                group_theme = '@std:GL5',
            ),
            group_theme = '@std:XG0',
        ),
        id = 'facets.extra.tools.image_info_editor.ImageInfoItem'
    )

#-------------------------------------------------------------------------------
#  'ImageInfoEditor' class:
#-------------------------------------------------------------------------------

class ImageInfoEditor ( ImageLibraryEditor ):
    """ Allows a user to edit the information associated with ImageInfo objects
        whose corresponding image names are passed to it.
    """

    #-- Overridden ImageLibraryEditor Class Constants --------------------------

    # The label/title of the editor for use in the view:
    editor_title = 'Image Information Editor'

    # The persistence id for the image library editor:
    editor_id = 'facets.extra.tools.image_info_editor.ImageInfoEditor'

    # Editor item factory class:
    item_class = ImageInfoItem

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    ImageInfoEditor( image_names = [
        '@std:BlackChromeT', '@std:BlackChromeB', '@std:notebook_open',
        '@std:notebook_close'
    ] ).edit_facets()

#-- EOF ------------------------------------------------------------------------