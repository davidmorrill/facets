"""
This demonstrates using the Facets file dialog with a file dialog extension,
in this case, the <b>ImageInfo</b> extension, which displays (if possible) the
contents, width and height information for the currently selected image file
so that the user can quickly verify they are opening the correct file before
leaving the file dialog.

For more information about why you would want to use the Facets file dialog
over the standard OS file dialog, select the <b>File Open</b> demo. For a
demonstration of writing a custom file dialog extension, select the
<b>File Open with Custom Extension</b> demo.

This example also shows setting a file name filter which only allows common
image file formats (i.e. *.png, *.gif, *.jpg, *.jpeg) files to be viewed and
selected.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, File, Button

from facets.api \
    import View, HGroup, Item

from facets.ui.file_dialog \
    import open_file, ImageInfo

#-- FileDialogDemo Class -------------------------------------------------------

# Demo specific file dialig id:
demo_id = 'facets.ui.demo.standard_editors.file_dialog.image_info'

# The image filters description:
filters = [
    'PNG file (*.png)|*.png',
    'GIF file (*.gif)|*.gif',
    'JPG file (*.jpg)|*.jpg',
    'JPEG file (*.jpeg)|*.jpeg'
 ]

class FileDialogDemo ( HasFacets ):

    # The name of the selected file:
    file_name = File

    # The button used to display the file dialog:
    open = Button( 'Open...' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HGroup(
            Item( 'open', show_label = False ),
            '_',
            Item( 'file_name', style = 'readonly', springy = True )
        ),
        width = 0.5
    )

    #-- Facets Event Handlers --------------------------------------------------

    def _open_set ( self ):
        """ Handles the user clicking the 'Open...' button.
        """
        file_name = open_file( extensions = ImageInfo(),
                               filter     = filters,
                               id         = demo_id )
        if file_name != '':
            self.file_name = file_name

#-- Create the demo ------------------------------------------------------------

demo = FileDialogDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------