"""
Demonstrates the use of the TitleEditor.

A TitleEditor can be used to dynamically label sections of a user interface.
The text displayed by the TitleEditor is specified by a facet associated with
the view.

This demonstration shows three variations of using a TitleEditor:

 * In the first example, the TitleEditor values are supplied by an Enum facet.
   Simply select a new value for the title from the drop-down list to cause the
   title to change.
 * In the second example, the TitleEditor values are supplied by a Str facet.
   Simply type a new value into the title field to cause the title to change.
 * In the third example, the TitleEditor values are supplied by a Property
   whose value is derived from a calculation on a Float facet. Type a number
   into the value field to cause the title to changed.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Enum, Str, Float, Property, cached_property

from facets.api \
    import View, VGroup, HGroup, Item, TitleEditor

#-- TitleEditorDemo Class ------------------------------------------------------

class TitleEditorDemo ( HasFacets ):

    # Define the selection of titles that can be displayed:
    title = Enum(
        'Select a new title from the drop down list below',
        'This is the TitleEditor demonstration',
        'Acme Widgets Sales for Each Quarter',
        'This is Not Intended to be a Real Application'
    )

    # A user settable version of the title:
    title_2 = Str( 'Type into the text field below to change this title' )

    # A title driven by the result of a calculation:
    title_3 = Property( depends_on = 'value' )

    # The number used to drive the calculation:
    value = Float

    # Define the test view:
    view = View(
        VGroup(
            HGroup(
                Item( 'title',
                      show_label = False,
                      springy    = True,
                      editor     = TitleEditor()
                )
            ),
            Item( 'title' ),
            show_border = True
        ),
        VGroup(
            HGroup(
                Item( 'title_2',
                      show_label = False,
                      springy    = True,
                      editor     = TitleEditor()
                )
            ),
            Item( 'title_2', label = 'Title' ),
            show_border = True
        ),
        VGroup(
            HGroup(
                Item( 'title_3',
                      show_label = False,
                      springy    = True,
                      editor     = TitleEditor()
                )
            ),
            Item( 'value' ),
            show_border = True
        ),
        width = 0.4
    )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_title_3 ( self ):
        try:
            return ( 'The square root of %s is %s' %
                    ( self.value, self.value ** 0.5 ) )
        except:
            return ( 'The square root of %s is %si' %
                    ( self.value, ( -self.value ) ** 0.5 ) )

#-- Create the demo ------------------------------------------------------------

demo = TitleEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------