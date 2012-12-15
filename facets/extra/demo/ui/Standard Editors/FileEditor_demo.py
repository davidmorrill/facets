"""
Implementation of a FileEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the FileEditor
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, File

from facets.api \
    import Item, Group, View

#-- FileEditorDemo Class -------------------------------------------------------

class FileEditorDemo ( HasFacets ):
    """ Defines the main FileEditor demo class. """

    # Define a File facet to view:
    file_name = File

    # Display specification (one Item per editor style):
    file_group = Group(
        Item( 'file_name', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'file_name', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'file_name', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'file_name', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        file_group,
        title     = 'FileEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = FileEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------