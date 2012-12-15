"""
Implementation of a CodeEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the CodeEditor
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Code

from facets.api \
    import Item, Group, View

#-- CodeEditorDemo Class -------------------------------------------------------

class CodeEditorDemo ( HasFacets ):
    """ Defines the CodeEditor demo class.
    """

    # Define a facet to view:
    code_sample = Code( 'import sys\n\nsys.print("hello world!")' )

    # Display specification:
    code_group = Group(
        Item( 'code_sample', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'code_sample', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'code_sample', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'code_sample', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        code_group,
        title   = 'CodeEditor',
        buttons = [ 'OK' ] )


#-- Create the demo ------------------------------------------------------------

demo = CodeEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------