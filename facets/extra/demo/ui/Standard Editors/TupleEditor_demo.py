"""
Implementation of a TupleEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the TupleEditor
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Tuple, Color, Range, Str, Item, Group, View

#-- Demo Class -----------------------------------------------------------------

class TupleEditorDemo ( HasFacets ):
    """ Defines the TupleEditor demo class.
    """

    # Define a facet to view:
    tuple = Tuple( Color, Range( 1, 4 ), Str )

    # Display specification (one Item per editor style):
    tuple_group = Group(
        Item( 'tuple', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'tuple', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'tuple', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'tuple', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        tuple_group,
        title     = 'TupleEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = TupleEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------