"""
Demonstration of the <b>SetEditor</b> and the various combinations of the
editor's <i>ordering</i> and <i>separate</i> facets, which control how the
visual elements of the editor are ordered and whether the included set elements
are kept visually separate from the currently excluded elements.

A <b>SetEditor</b> can be used to edit <i>sets</i>, <i>lists</i> and
<i>tuples</i> whose elements are unique (i.e. only occur one time in the value)
and which are taken from a well-defined set of values.

The editor displays both the currently included elements of the set being edited
and the currently excluded elements. Excluded elements are those items from the
specified set of all possible values which are not currently part of the value
being edited. Included and excluded elements have different appearances. In the
demo, included elements are light gray, and excluded elements are a darker grey.

You can include or exclude an element from the current value by clicking on it,
which reverses its current inclusion/exclusion state. You can also include or
exclude a range of elements by click dragging over several elements. The inverse
of the initially clicked on element's initial status is used to determine the
new state of all dragged over elements.

The demo illustrates two facets which affect how the editor behaves:

 - <b>ordering</b>: Specifies how elements are visually ordered in the editor.
 - <b>separate</b>: Specifies whether included elements are kept visually
   separate from excluded elements.

The possible values for <i>ordering</i> are:

 - <i>'sort'</i>: Elements should appear in sort order (the default). You can
   modify the default sort order by specifying one or both of the editor's
   <i>compare</i> and <i>key</i> facets.
 - <i>'user'</i>: The user can change the order of the included and excluded
   elements by dragging the icon displayed on the right side of all elements up
   or down within the editor list.
 - <i>'value'</i>: The elements are displayed in the order they appear in the
   set value. If the value is a <i>set</i> object, the implicit order defined
   the set is used.

If the <i>separate</i> editor facet is <b><i>True</i></b> (the default), the
included elements are displayed before all excluded elements. If <i>separate</i>
is <b><i>False</i></b>, the included and excluded elements can appear intermixed
in the editor list.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Property, Theme, View, HGroup, Item, UItem, \
           property_depends_on, spring

from facets.ui.editors.set_editor \
     import SetItem, SetEditor

from facets.ui.ui_facets \
    import image_for

#-- Definitions for alternate SetItem classes ----------------------------------

class TestItem1 ( SetItem ):
    images = ( '@icons2:EditTab', '@icons2:EditTab' )
    themes = (
        Theme( '@xform:b4?H10L30S30', content = ( 5, 1, 1, 0 ) ),
        Theme( '@xform:b4?H47L35S14', content = ( 5, 1, 1, 0 ) )
    )
    def init ( self ):
        self.label = str( name2num[ self.item ] )

class TestItem2 ( SetItem ):
    images     = ( '@icons2:EditTab', '@icons2:EditTab' )
    drag_image = image_for( '@icons2:Synchronize?H24' )
    def init ( self ):
        self.label = self.item + '\nItem'

class TestItem3 ( SetItem ):
    images = ( '@icons:dot3?L90a97', '@icons:dot3' )
    themes = (
        Theme( '@xform:bg?L45', content       = ( 5, 1, 1, 3 ),
                                content_color = 0xA0A0A0 ),
        Theme( '@xform:bg?L45', content = ( 5, 1, 1, 3 ) )
    )
    def init ( self ):
        self.label = str( name2num[ self.item ] )

#-- Define a mapping from literal number names to their values (for sorting) ---

name2num = {
    'One': 1, 'Two':   2, 'Three': 3, 'Four': 4, 'Five': 5,
    'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten':  10
}

def name_to_num ( item ):
    return name2num[ item ]

#-- Define all valid set values ------------------------------------------------

number_values = (
    'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
    'Ten'
)

#-- SetEditorDemo class --------------------------------------------------------

class SetEditorDemo ( HasFacets ):
    items = List      # The current set of values begin edited
    total = Property  # The total of all current items

    view = View(
        HGroup(
            Item( 'total', style = 'readonly' ),
            spring,
            group_theme = '#themes:tool_options_group'
        ),
        HGroup(
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'user',
                       separate = True
                   )
            ),
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'user',
                       separate = False
                   )
            ),
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'value',
                       separate = True
                   )
            ),
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'value',
                       separate = False
                   )
            ),
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'sort',
                       separate = True,
                       key      = name_to_num,
                       adapter  = TestItem1
                   )
            ),
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'sort',
                       separate = False,
                       key      = name_to_num,
                       adapter  = TestItem1
                   )
            ),
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'user',
                       separate = True,
                       adapter  = TestItem2
                   )
            ),
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'sort',
                       separate = True,
                       key      = name_to_num,
                       adapter  = TestItem3
                   )
            ),
            UItem( 'items',
                   editor = SetEditor(
                       values   = number_values,
                       ordering = 'sort',
                       separate = False,
                       key      = name_to_num,
                       adapter  = TestItem3
                   )
            )
        ),
        title  = 'SetEditor Demo',
        width  = 750,
        height = 370
    )

    def _items_default ( self ):
        return [ 'One', 'Four', 'Nine', 'Six' ]

    @property_depends_on( 'items' )
    def _get_total ( self ):
        return reduce( lambda x, y: x + name2num[ y ], self.items, 0 )

#-- Create the demo ------------------------------------------------------------

demo = SetEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
