"""
Implementation of a TupleEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the TupleEditor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Tuple, Color, Range, Str, Item, Group, View

#-- TupleEditorDemo Class ------------------------------------------------------

class TupleEditorDemo ( HasFacets ):
    """ This class specifies the details of the TupleEditor demo.
    """

    # To demonstrate any given Facet editor, an appropriate Facet is required:
    tuple = Tuple( Color, Range( 1, 4 ), Str )

    # Display specification (one Item per editor style):
    tuple_group = Group(
        Item( 'tuple', style = 'simple', label = 'Simple' ),
        Item( '_' ),
        Item( 'tuple', style = 'custom', label = 'Custom' ),
        Item( '_' ),
        Item( 'tuple', style = 'text', label = 'Text' ),
        Item( '_' ),
        Item( 'tuple', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view1 = View(
        tuple_group,
        title   = 'TupleEditor',
        buttons = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

popup = TupleEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------