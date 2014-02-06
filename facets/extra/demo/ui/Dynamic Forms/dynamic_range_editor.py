"""
# Dynamic Range Editor #

This example demonstrates how to set up a range-based facet whose high and low
range end values can be modified at run-time.

The top-most *value* facet can have its range end points changed dynamically by
modifying the *low* and *high* sliders below it.

This demo also illustrates how the range value location and formatting can also
be specified if desired.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Float, Range, SyncValue

from facets.api \
    import View, Item, Label, RangeEditor

#-- DynamicRangeEditor Class ---------------------------------------------------

class DynamicRangeEditor ( HasPrivateFacets ):
    """ Defines an editor for dynamic ranges (i.e. ranges whose bounds can be
        changed at run time).
    """

    # The value with the dynamic range:
    value = Float

    # This determines the low end of the range:
    low = Range( 0.0, 10.0, 0.0 )

    # This determines the high end of the range:
    high = Range( 20.0, 100.0, 20.0 )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            Item( 'value',
                   editor = RangeEditor( low        = SyncValue( self, 'low' ),
                                         high       = SyncValue( self, 'high' ),
                                         format_str = '%.1f' )
            ),
            Item( 'value',
                   editor = RangeEditor( low        = SyncValue( self, 'low' ),
                                         high       = SyncValue( self, 'high' ),
                                         show_value = 'Body',
                                         format_str = '%.2f' )
            ),
            Item( 'value',
                   editor = RangeEditor( low        = SyncValue( self, 'low' ),
                                         high       = SyncValue( self, 'high' ),
                                         show_value = 'None' )
            ),
            '_',
            Item( 'low' ),
            Item( 'high' ),
            '_',
            Label( 'Move the Low and High sliders to change the range of '
                   'Value.' ),
            title     = 'Dynamic Range Editor Demonstration',
            id        = 'facets.extra.demo.ui.Dynamic Forms.'
                        'dynamic_range_editor',
            resizable = True
        )

#-- Create the demo ------------------------------------------------------------

demo = DynamicRangeEditor

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------