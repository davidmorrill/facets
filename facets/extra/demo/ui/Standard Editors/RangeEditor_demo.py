"""
# RangeEditor Demo #

This example demonstrates using the various styles of the **RangeEditor**, which
allows the user to select a value within a specified integer or floating point
range of values using a graphical slider.

The **RangeEditor** is the default editor for *Range* facets, but can also be
used with facets having *Int* or *Float* values by explicitly specifying the
range of valid values the editor should use.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Range, Item, Group, View, Tabbed

#-- RangeEditorDemo Class ------------------------------------------------------

class RangeEditorDemo ( HasFacets ):
    """ Defines the RangeEditor demo class.
    """

    # Define a facet for each of four range variants:
    small_int_range  = Range( 1, 16 )
    medium_int_range = Range( 1, 25 )
    large_int_range  = Range( 1, 150 )
    float_range      = Range( 0.0, 150.0 )

    # RangeEditor display for narrow integer Range facets (< 17 wide):
    int_range_group1 = Group(
        Item( 'small_int_range',  style = 'simple',  label = 'Simple' ),
        Item( '_' ),
        Item( 'small_int_range',  style = 'custom',  label = 'Custom' ),
        Item( '_' ),
        Item( 'small_int_range', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'small_int_range', style = 'readonly', label = 'ReadOnly' ),
        label = 'Small Int'
    )

    # RangeEditor display for medium-width integer Range facets (17 to 100):
    int_range_group2 = Group(
        Item( 'medium_int_range', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'medium_int_range', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'medium_int_range', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'medium_int_range', style = 'readonly', label = 'ReadOnly' ),
        label = 'Medium Int'
    )

    # RangeEditor display for wide integer Range facets (> 100):
    int_range_group3 = Group(
        Item( 'large_int_range', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'large_int_range', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'large_int_range', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'large_int_range', style = 'readonly', label = 'ReadOnly' ),
        label = 'Large Int'
    )

    # RangeEditor display for float Range facets:
    float_range_group = Group(
        Item( 'float_range', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'float_range', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'float_range', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'float_range', style = 'readonly', label = 'ReadOnly' ),
        label = 'Float'
    )

    # The view includes one group per data type. These will be displayed
    # on separate tabbed panels:
    view = View(
        Tabbed(
            int_range_group1,
            int_range_group2,
            int_range_group3,
            float_range_group
        ),
        title     = 'RangeEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = RangeEditorDemo

#-- Run the demo (if invoked from the comand line) -----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------