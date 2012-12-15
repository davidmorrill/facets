"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Instance

from facets.api \
    import View, VSplit, Item

from facets.extra.tools.image_library_viewer \
     import ImageLibraryViewer

from facets.extra.tools.image_info_editor \
     import ImageInfoEditor

class ImageInfoEditor ( HasFacets ):

    # The image library viewer we are using:
    viewer = Instance( ImageLibraryViewer )

    # The image info editor we are using:
    editor = Instance( ImageInfoEditor, () )

    #-- Facets UI View Definitions -----------------------------------------

    view = View(
        VSplit(
            Item( 'viewer', style = 'custom', dock = 'horizontal' ),
            Item( 'editor', style = 'custom', dock = 'horizontal' ),
            id          = 'splitter',
            show_labels = False
        ),
        title     = 'Image Info Editor',
        id        = 'facets.ui.demo.tools.Image_Info_Editor',
        width     = 0.75,
        height    = 0.75,
        resizable = True
    )

    #-- Default Value Handlers ---------------------------------------------

    def _viewer_default ( self ):
        viewer = ImageLibraryViewer()
        viewer.sync_facet( 'image_names', self.editor )

        return viewer

#-- Create the demo ------------------------------------------------------------

popup = ImageInfoEditor

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------