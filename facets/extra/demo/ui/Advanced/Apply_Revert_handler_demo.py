"""
# Apply Revert Handler Demo #

This program demonstrates hows how to add an event handler which performs an
action when the *Apply* or *Revert* buttons are pressed.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, List, Item, View, Handler, HGroup, VGroup, \
           GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- GridAdapter and GridEditor used to displays list values --------------------

class ListAdapter ( GridAdapter ):

    columns = [ 'value' ]

    def value_text ( self ):
        return self.item

list_editor = GridEditor(
    adapter     = ListAdapter,
    operations  = [],
    show_titles = False
)

#-- 'ApplyRevert_Handler' Class ------------------------------------------------

class ApplyRevert_Handler ( Handler ):

    def apply ( self, info ):
        object = info.object
        object.stack.insert( 0, object.input )
        object.queue.append( object.input )

    def revert ( self, info ):
        print 'revert called...'

#-- 'ApplyRevertDemo' Class ----------------------------------------------------

class ApplyRevertDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    input = Str
    stack = List
    queue = List

    #-- Facet View Definitions -------------------------------------------------

    facets_view = View(
        VGroup(
            Item( 'input' ),
            HGroup(
                VGroup(
                    Item( 'stack', show_label = False, editor = list_editor ),
                    label = 'Stack'
                ),
                VGroup(
                    Item( 'queue', show_label = False, editor = list_editor ),
                    label = 'Queue'
                )
            )
        ),
        title   = 'Apply/Revert example',
        buttons = [ 'Apply', 'Revert' ],
        kind    = 'modal',
        handler = ApplyRevert_Handler
    )

#-- Create the demo ------------------------------------------------------------

modal_popup = ApplyRevertDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    modal_popup().edit_facets()

#-- EOF ------------------------------------------------------------------------