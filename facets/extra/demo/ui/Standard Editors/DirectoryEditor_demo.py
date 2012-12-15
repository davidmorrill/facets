"""
Implementation of a DirectoryEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the DirectoryEditor
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Directory

from facets.api \
    import Item, Group, View

#-- DirectoryEditorDemo Class --------------------------------------------------

class DirectoryEditorDemo ( HasFacets ):
    """ Define the main DirectoryEditor demo class. """

    # Define a Directory facet to view:
    dir_name = Directory


    # Display specification (one Item per editor style):
    dir_group = Group(
        Item( 'dir_name', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'dir_name', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'dir_name', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'dir_name', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        dir_group,
        title     = 'DirectoryEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = DirectoryEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------