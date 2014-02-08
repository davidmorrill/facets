"""
# File Open With Custom Extension #

This demonstrates using the Facets file dialog with a custom written file
dialog extension, in this case an extension called **LineCountInfo**, which
displays the number of text lines in the currently selected file.

For more information about why you would want to use the Facets file dialog over
the standard OS file dialog, select the *File Open* demo.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from os.path \
    import getsize

from facets.core_api \
    import HasFacets, File, Button, Property, cached_property

from facets.api \
    import View, VGroup, HGroup, Item

from facets.ui.file_dialog \
    import open_file, MFileDialogModel

from facets.ui.helper \
    import commatize

#-- LineCountInfo Class --------------------------------------------------------

class LineCountInfo ( MFileDialogModel ):
    """ Defines a file dialog extension that displays the number of text lines
        in the currently selected file.
    """

    # The number of text lines in the currently selected file:
    lines = Property( depends_on = 'file_name' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            Item( 'lines', style = 'readonly' ),
            label       = 'Line Count Info',
            show_border = True
        )
    )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_lines ( self ):
        try:
            if getsize( self.file_name ) > 10000000:
                return 'File too big...'

            fh   = file( self.file_name, 'rb' )
            data = fh.read()
            fh.close()
        except:
            return ''

        if ( data.find( '\x00' ) >= 0 ) or ( data.find( '\xFF' ) >= 0 ):
            return 'File contains binary data...'

        return ( '%s lines' % commatize( len( data.splitlines() ) ) )

#-- FileDialogDemo Class -------------------------------------------------------

# Demo specific file dialig id:
demo_id = ( 'facets.ui.demo.standard_editors.file_dialog.'
           'line_count_info' )

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
        file_name = open_file( extensions = LineCountInfo(), id = demo_id )
        if file_name != '':
            self.file_name = file_name

#-- Create the demo ------------------------------------------------------------

demo = FileDialogDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------