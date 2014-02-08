"""
# File Open With TextInfo Extension #

This demonstrates using the Facets file dialog with a file dialog extension,
in this case, the **TextInfo** extension, which displays (if possible) the
contents of the currently selected file in a read-only text editor so the user
can quickly verify they are opening the correct file before leaving the file
dialog.

For more information about why you would want to use the Facets file dialog
over the standard OS file dialog, select the *File Open* demo. For a
demonstration of writing a custom file dialog extension, select the
*File Open with Custom Extension* demo.

This example also shows setting a file name filter which only allows Python
source (i.e. *\*.py*) files to be viewed and selected.
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
    import open_file, TextInfo

#-- FileDialogDemo Class -------------------------------------------------------

# Demo specific file dialig id:
demo_id = 'facets.ui.demo.standard_editors.file_dialog.text_info'

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
        file_name = open_file( extensions = TextInfo(),
                               filter     = 'Python file (*.py)|*.py',
                               id         = demo_id )
        if file_name != '':
            self.file_name = file_name

#-- Create the demo ------------------------------------------------------------

demo = FileDialogDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------