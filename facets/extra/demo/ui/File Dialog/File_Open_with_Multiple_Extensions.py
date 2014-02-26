"""
# File Open With Multiple Extensions #

This demonstrates using the Facets file dialog with multiple file dialog
extensions, in this case, the **FileInfo**, **TextInfo** and **ImageInfo**
extensions.

For more information about why you would want to use the Facets file dialog
over the standard OS file dialog, select the *File Open* demo. For a
demonstration of writing a custom file dialog extension, select the
*File Open with Custom Extension* demo.

Suggestion: Try resizing the dialog and dragging the various file dialog
extensions around to create a better arrangement than the rather cramped
default vertical arrangement. Close the dialog, then re-open it to see that your
new arrangement has been correctly restored. Try a different file dialog demo to
verify that the customizations are not affected by any of the other demos
because this demo specifies a custom id when invoking the file dialog.
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
    import open_file, FileInfo, TextInfo, ImageInfo

#-- FileDialogDemo Class -------------------------------------------------------

# Demo specific file dialig id:
demo_id = 'facets.ui.demo.standard_editors.file_dialog.multiple_info'

# The list of file dialog extensions to use:
extensions = [ FileInfo(), TextInfo(), ImageInfo() ]

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
        file_name = open_file( extensions = extensions, id = demo_id )
        if file_name != '':
            self.file_name = file_name

#-- Create the demo ------------------------------------------------------------

demo = FileDialogDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------