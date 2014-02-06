"""
# String List UI Editor #

Another demo showing how to use a **GridEditor** to create a multi-select list
box. This demo creates a reusable **StringListEditor** class and uses that
instead of defining the editor as part of the demo class.

This approach greatly simplifies the actual demo class and shows how to
construct a reusable Facets UI-based editor that can be used in other
applications.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, List, Str, Property, on_facet_set, View, HGroup, \
           Item, GridEditor, UIEditor, BasicEditorFactory

from facets.ui.grid_adapter \
    import GridAdapter

#-- Define the reusable StringListEditor class and its helper classes ----------

# Define the grid adapter used by the Facets UI string list editor:
class MultiSelectAdapter ( GridAdapter ):

    # The columns in the grid (just the string value):
    columns = [ ( 'Value', 'value' ) ]

    # The text property used for the 'value' column:
    value_text = Property

    def _get_value_text ( self ):
        return self.item

#-- Define the actual Facets UI string list editor -----------------------------

class _StringListEditor ( UIEditor ):

    # Indicate that the editor is scrollable/resizable:
    scrollable = True

    # The list of available editor choices:
    choices = List( Str )

    # The list of currently selected items:
    selected = List( Str )

    # The facets UI view used by the editor:
    view = View(
        Item( 'choices',
              show_label = False,
              editor     = GridEditor(
                  adapter        = MultiSelectAdapter,
                  operations     = [],
                  show_titles    = False,
                  selected       = 'selected',
                  selection_mode = 'rows'
              )
        ),
        id        = 'string_list_editor',
        resizable = True
    )

    def init_ui ( self, parent ):

        self.sync_value( self.factory.choices, 'choices', 'from',
                         is_list = True )
        self.selected = self.value

        return self.edit_facets( parent = parent, kind = 'editor' )

    @on_facet_set( ' selected' )
    def _selected_modified ( self ):
        self.value = self.selected

# Define the StringListEditor class used by client code:
class StringListEditor ( BasicEditorFactory ):

    # The editor implementation class:
    klass = _StringListEditor

    # The extended facet name containing the editor's set of choices:
    choices = Str

#-- Define the demo class ----------------------------------------------------

class MultiSelect ( HasPrivateFacets ):
    """ This class demonstrates using the StringListEditor to select a set
        of string values from a set of choices.
    """

    # The list of choices to select from:
    choices = List( Str )

    # The currently selected list of choices:
    selected = List( Str )

    # A dummy result so that we can display the selection using the same
    # StringListEditor:
    result = List( Str )

    # A facets view showing the list of choices on the left-hand side, and
    # the currently selected choices on the right-hand side:
    view = View(
        HGroup(
            Item( 'selected',
                  show_label = False,
                  editor     = StringListEditor( choices = 'choices' )
            ),
            Item( 'result',
                  show_label = False,
                  editor     = StringListEditor( choices = 'selected' )
            )
        ),
        width  = 0.20,
        height = 0.25
    )

#-- Create the demo ------------------------------------------------------------

demo = MultiSelect(
    choices  = [ 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                 'nine', 'ten' ],
    selected = [ 'two', 'five', 'nine' ]
)

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------