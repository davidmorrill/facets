"""
A simple demonstration using the <b>StackEditor</b> to display a selectable and
filterable list of text strings.

This demonstration illustrates:
 - Using a custom <b>IStackItem</b> implementation subclassing
   <b>StrStackItem</b> (used to add selection behavior).
 - Selecting (and displaying) an item in the <b>StackEditor</b> (by clicking an
   item in the editor).
 - Filtering the contents of the editor (using the <i>filter</i> control and an
   <b>IFilter</b> implementation subclassing <b>Filter</b>).
 - Dynamically changing the items displayed by the <b>StackEditor</b> (using the
   <i>count</i> control).

Note that changing the <i>count</i> value only indirectly updates the list of
items displayed. When <i>count</i> changes value, an <i>update</i> event is
scheduled for a later time. The <i>items</i> list is a property that depends on
the <i>update</i> event, and so will define a new list, using the current value
of <i>count</i>, when the i>update</i> event fires.

It is possible to make the <i>items</i> property depend directly on the value of
<i>count</i>. However, this can result in slow display updates since the
<i>items</i> list would be reconstructed on each change to <i>count</i>, which
could in turn make the <i>count</i> field's <b>ScrubberEditor</b> appear to
update slowly, especially for large values of <i>count</i>. By decoupling
changes to <i>count</i> from the rebuilding of the <i>items</i> list, it allows
the user interface to be much more responsive to changes in the <i>count</i>
value.

You can verify this for yourself by changing the <i>@property_depends_on</i>
decorator for the <i><b>_get_items</b></i> property getter from 'update' to
'count', and then re-running the demo.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Property, List, Str, Range, Event, \
           View, VGroup, HGroup, Item, StackEditor, ScrubberEditor, \
           property_depends_on

from facets.ui.i_filter \
    import Filter

from facets.ui.i_stack_item \
    import StrStackItem

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  'StringFilter' class:
#-------------------------------------------------------------------------------

class StringFilter ( Filter ):

    #-- Facet Definitions ------------------------------------------------------

    # The string each item must match to satisfy the filter:
    match = Str

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'match', show_label = False )
    )

    #-- Filter Method Overrides ------------------------------------------------

    def filter ( self, item ):
        """ Returns whether or not the specified *item* matches the current
            filter value contained in 'match'.
        """
        return (item.item.find( self.match ) >= 0)

#-------------------------------------------------------------------------------
#  'SimpleStackItem' class:
#-------------------------------------------------------------------------------

class SimpleStackItem ( StrStackItem ):

    #-- StackItem Event Handlers -----------------------------------------------

    def left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        self.selected = True

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, selected ):
        self.theme = ('@facets:stack_item' + ( '', '?H65l7S|l84' )[ selected ])

#-------------------------------------------------------------------------------
#  'StackEditorDemo' class:
#-------------------------------------------------------------------------------

class StackEditorDemo ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The items to display:
    items = Property( List )

    # The number of items to display:
    count = Range( 0, 10000, 5 )

    # The currently selected item:
    selected = Str

    # The filter to apply to the list items:
    filter = Instance( StringFilter, () )

    # Event fired when items list should be updated:
    update = Event

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'count',
                      label  = 'Number of items',
                      width  = -40,
                      editor = ScrubberEditor()
                ),
                '_',
                Item( 'filter',
                      label   = 'Filter',
                      style   = 'custom',
                      springy = True
                ),
                group_theme = '@xform:b?L35'
            ),
            HGroup(
                Item( 'selected',
                      style   = 'readonly',
                      springy = True
                ),
                group_theme = '@xform:b?L35'
            ),
            Item( 'items',
                  editor = StackEditor(
                      adapter  = SimpleStackItem,
                      selected = 'selected',
                      filter   = 'filter' )
            ),
            show_labels = False
        ),
        title  = 'StackEditor Demo',
        width  = 300,
        height = 500
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'update' )
    def _get_items ( self ):
        return [ 'Item %d' % i for i in range( 1, self.count + 1 ) ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _count_set ( self ):
        do_after( 500, self.set, selected = '', update = True )

#-- Create the demo ------------------------------------------------------------

demo = StackEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
