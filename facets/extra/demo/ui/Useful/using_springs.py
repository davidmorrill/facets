"""
# Using Spring Items #

This demo shows you how to space editors horizontally using *springs*.

It illustrates several different combinations, including a normal, non-spring,
example.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Button, View, VGroup, HGroup, Item, spring

#-- Reusable 'button' definition -----------------------------------------------

button = Item( 'ignore', show_label = False )

#-- SpringDemo Class -----------------------------------------------------------

class SpringDemo ( HasFacets ):

    ignore = Button( 'Ignore' )

    view = View(
               VGroup(
                   HGroup( button, spring, button,
                           show_border = True,
                           label       = 'Left and right justified' ),
                   HGroup( button, button, spring,
                           button, button, spring,
                           button, button,
                           show_border = True,
                           label       = 'Left, center and right justified' ),
                   HGroup( spring, button, button,
                           show_border = True,
                           label       = 'Right justified' ),
                   HGroup( button, button,
                           show_border = True,
                           label       = 'Left justified (no springs)' ),
               ),
               title     = 'Spring Demo',
               buttons   = [ 'OK' ],
               resizable = True
           )

#-- Create the demo ------------------------------------------------------------

demo = SpringDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------