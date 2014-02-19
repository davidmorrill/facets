"""
# CheckListEditor Demo #

This examples demonstrates using the various styles of the **CheckListEditor**,
which can be used as a type of *set* editor for facets whose values are lists
of unique values chosen from a specified universe of possible values.

For example, you could use a CheckListEditor to select a jury from a specified
pool of possible jurors.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Item, Group, View, Tabbed, CheckListEditor

#-- CheckListEditorDemo Class --------------------------------------------------

class CheckListEditorDemo ( HasFacets ):
    """ Define the main CheckListEditor demo class. """

    # Define a facet for each of three formations:
    checklist_4col = List( editor = CheckListEditor(
                           values = [ 'one', 'two', 'three', 'four' ],
                           cols   = 4 ) )

    checklist_2col = List( editor = CheckListEditor(
                           values = [ 'one', 'two', 'three', 'four' ],
                           cols   = 2 ) )

    checklist_1col = List( editor = CheckListEditor(
                           values = [ 'one', 'two', 'three', 'four' ],
                           cols   = 1 ) )

    # CheckListEditor display with four columns:
    cl_4_group = Group(
        Item( 'checklist_4col', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'checklist_4col', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'checklist_4col', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'checklist_4col', style = 'readonly', label = 'ReadOnly' ),
        label = '4-column'
    )

    # CheckListEditor display with two columns:
    cl_2_group = Group(
        Item( 'checklist_2col', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'checklist_2col', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'checklist_2col', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'checklist_2col', style = 'readonly', label = 'ReadOnly' ),
        label = '2-column'
    )

    # CheckListEditor display with one column:
    cl_1_group = Group(
        Item( 'checklist_1col', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'checklist_1col', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'checklist_1col', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'checklist_1col', style = 'readonly', label = 'ReadOnly' ),
        label = '1-column'
    )

    # The view includes one group per column formation.  These will be displayed
    # on separate tabbed panels.
    view1 = View(
        Tabbed(
            cl_4_group,
            cl_2_group,
            cl_1_group,
        ),
        title     = 'CheckListEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = CheckListEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------