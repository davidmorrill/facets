"""
# File Open With FileInfo Extension #

This demonstrates using the Facets file dialog with a file dialog extension,
in this case, the **FileInfo** extension, which displays information about the
currently selected file, such as:

- File size.
- Date and time last accessed.
- Date and time last modified.
- Date and time last created.

For more information about why you would want to use the Facets file dialog over
the standard OS file dialog, select the *File Open* demo. For a demonstration of
writing a custom file dialog extension, select the
*File Open with Custom Extension* demo.
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
    import open_file, FileInfo

#-- FileDialogDemo Class -------------------------------------------------------

# Demo specific file dialig id:
demo_id = 'facets.ui.demo.standard_editors.file_dialog.file_info'

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
        file_name = open_file( extensions = FileInfo(), id = demo_id )
        if file_name != '':
            self.file_name = file_name

#-- Create the demo ------------------------------------------------------------

demo = FileDialogDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------