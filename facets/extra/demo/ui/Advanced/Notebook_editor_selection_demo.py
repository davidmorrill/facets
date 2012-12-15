"""
This shows how the currently active notebook tab of a NoteboookEditor can be
controlled using the NotebookEditor's 'selected' facet.

Note the interaction between the spinner control (for the 'index' facet) and
the currently selected notebook tab. Try changing the spinner value, then try
clicking on various notebook tabs.

Also note that rearranging the notebook tabs (using drag and drop) does not
affect the correspondence between the index value and its associated notebook
tab. The correspondence is determined by the contents of the 'people' facet,
and not by the physical layout of the notebook tabs.

Finally, note that the NotebookEditor will automatically scroll the tabs to make
the selected tab completely visible.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasStrictFacets, Str, Int, Regex, List, Instance, Range, View, \
           VGroup, Item, NotebookEditor, ScrubberEditor

#-- Person Class ---------------------------------------------------------------

class Person ( HasStrictFacets ):

    # Facet definitions:
    name  = Str
    age   = Int
    phone = Regex( value = '000-0000', regex = '\d\d\d[-]\d\d\d\d' )

    # Facets view definition:
    facets_view = View( 'name', 'age', 'phone',
                        width   = 0.18,
                        buttons = [ 'OK', 'Cancel' ] )

#-- Sample Data ----------------------------------------------------------------

people = [
    Person( name = 'Dave Chomsky',        age = 39, phone = '555-1212' ),
    Person( name = 'Mike Wakowski',       age = 28, phone = '555-3526' ),
    Person( name = 'Joe Higginbotham',    age = 34, phone = '555-6943' ),
    Person( name = 'Tom Derringer',       age = 22, phone = '555-7586' ),
    Person( name = 'Dick Van Der Hooten', age = 63, phone = '555-3895' ),
    Person( name = 'Harry McCallum',      age = 46, phone = '555-3285' ),
    Person( name = 'Sally Johnson',       age = 43, phone = '555-8797' ),
    Person( name = 'Fields Timberlawn',   age = 31, phone = '555-3547' )
]

#-- NotebookEditorSelectionDemo Class --------------------------------------

class NotebookEditorSelectionDemo ( HasStrictFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # List of people:
    people = List( Person )

    # The currently selected person:
    selected = Instance( Person )

    # The index of the currently selected person:
    index = Range( 0, 7, mode = 'spinner' )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'index',
              editor     = ScrubberEditor(),
              item_theme = '#themes:ScrubberEditor',
              width      = -50
        ),
        '_',
        VGroup(
            Item( 'people@',
                  id         = 'notebook',
                  show_label = False,
                  editor     = NotebookEditor(
                      deletable  = True,
                      dock_style = 'tab',
                      selected   = 'selected',
                      export     = 'DockWindowShell',
                      page_name  = '.name'
                  )
            )
        ),
        id   = 'facets.extra.demo.ui.Advanced.Notebook_editor_selection_demo',
        dock = 'horizontal' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, selected ):
        self.index = self.people.index( selected )

    def _index_set ( self, index ):
        self.selected = self.people[ index ]

#-- Create The Demo ------------------------------------------------------------

demo = NotebookEditorSelectionDemo(
    people = people
). set(
    selected = people[0]
)

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------