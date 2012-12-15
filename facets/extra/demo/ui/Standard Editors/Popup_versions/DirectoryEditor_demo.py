"""
Implementation of a DirectoryEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the DirectoryEditor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Directory, Item, Group, View

#-- DirectoryEditorDemo Class --------------------------------------------------

class DirectoryEditorDemo ( HasFacets ):
    """ This class specifies the details of the DirectoryEditor demo.
    """

    # To demonstrate any given Facet editor, an appropriate Facet is required:
    dir_name = Directory

    # Display specification (one Item per editor style):
    dir_group = Group(
        Item( 'dir_name', style = 'simple', label = 'Simple' ),
        Item( '_' ),
        Item( 'dir_name', style = 'custom', label = 'Custom' ),
        Item( '_' ),
        Item( 'dir_name', style = 'text', label = 'Text' ),
        Item( '_' ),
        Item( 'dir_name', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view1 = View(
        dir_group,
        title   = 'DirectoryEditor',
        width   = 400,
        buttons = [ 'OK' ]
    )


#-- Create the demo ------------------------------------------------------------

popup = DirectoryEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------