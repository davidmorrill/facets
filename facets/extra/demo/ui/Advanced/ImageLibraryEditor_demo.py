"""
# ImageLibraryEditor Demo #

Demonstrates use of the **ImageLibraryEditor**. The ImageLibraryEditor is a
specialized editor that allows a user to browse and select images from the
singleton Facets **ImageLibrary** object.

The editor is divided into two drop-down lists:

- **Volumes**: Lists all of the the image volumes contained in the ImageLibrary.
- **Image**: Lists all of the images contained in the currently selected image
  volume.

In the demo, the currently selected image in the ImageLibraryEditor at the top
of the view is used to create an **HLSADerivedImage**, which is then edited
using the **HLSADerivedImageEditor** displayed in the bottom part of the view.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Image, Theme, View, VGroup, Item, ImageLibraryEditor, \
           HLSADerivedImageEditor

from facets.extra.helper.image \
    import HLSADerivedImage

#-- Demo Class -----------------------------------------------------------------

class Demo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The currently selected image:
    image = Image

    # The derived version being edited using the HLSADerivedImageEditor"
    derived = Image

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'image',
                  editor = ImageLibraryEditor()
            ),
            Item( 'derived',
                  id        = 'derived',
                  editor    = HLSADerivedImageEditor(),
                  height    = 600,
                  resizable = True
            ),
            show_labels = False,
            group_theme = Theme( '@xform:bg?L30', content = -5 )
        ),
        title     = 'ImageLibraryEditor Demo',
        id        = 'facets.extra.demo.ui.Advanced.ImageLibraryEditor_demo',
        width     = 0.50,
        height    = 0.75,
        resizable = True
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _image_set ( self, image ):
        self.derived = HLSADerivedImage( base_image = image )

#-- Create The Demo ------------------------------------------------------------

demo = Demo( image = '@xform:bg' )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == "__main__":
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------
