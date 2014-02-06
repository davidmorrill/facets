"""
# ValueEditor Demo #

This example demonstrates use of the **ValueEditor**, which displays a
tree-structured view of an arbitrary Python object. The ValueEditor is useful
mainly as a debugging aid, since it allows the user to interactively explore the
contents of an object. It is not as useful for more generaL application use
since it does not provide any means for filtering or formatting the object
values displayed.

In this demo, a ValueEditor is used to display the contents of the singleton
**ImageLibrary** object, which contains information about the various image
volumes available to a Facets application.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Constant, View, VGroup, Item, ValueEditor

from facets.ui.image \
    import ImageLibrary

#-- Demo Class Definition ------------------------------------------------------

class Demo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # A reference to the system image library displayed by the ValueEditor:
    library = Constant( ImageLibrary() )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            Item( 'library',
                  show_label = False,
                  editor     = ValueEditor()
            ),
        ),
        title     = 'ValueEditor Demo',
        id        = 'facets.extra.demo.ui.Advanced.ValueEditor_demo',
        width     = 0.25,
        height    = 0.25,
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = Demo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
