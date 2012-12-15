"""
Another demonstration of the ListCanvasEditor using the ImageBrowser tool.

The ImageBrowser tool uses a ListCanvasEditor to display a collection of
Facets image library images specified by their image name. Each item on
the canvas is an ImageItem object, which represents a single image.

For more information about how this program works, refer to the source code
of the ImageBrowser tool (facets.extra.tools.image_browser.py).

Note: This demo requires the facets.extra package to be installed.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.extra.tools.image_browser \
     import ImageBrowser

from facets.ui.image \
     import ImageLibrary

#-- Get the image library volume called 'std' ----------------------------------

volume = ImageLibrary().catalog[ 'std' ]

#-- Create the demo using a subset of the images available in the 'std' volume -

demo = ImageBrowser(
    image_names = [ image.image_name for image in volume.images ]
)

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------