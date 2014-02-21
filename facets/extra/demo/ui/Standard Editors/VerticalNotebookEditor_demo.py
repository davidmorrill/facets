"""
# VerticalNotebookEditor Demo #

This example demonstrates the use of the **VerticalNotebookEditor**, which
allows a list of objects to be displayed and edited using a vertical notebook
style.

Each element in the list is displayed in its own separate notebook *page*. The
pages are organized vertically, and each page can be collapsed or expanded to
hide or show an element's content.

The editor also supports a number of options, such as:

- Whether only a single or multiple elements can be open at the same time.
- Whether a single or double mouse click is used to open or close pages.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Int, Enum, List, View, Item, VerticalNotebookEditor

#-- Person Class -------------------------------------------------------------

class Person ( HasFacets ):

    # The name of the person:
    name = Str

    # The age of the person:
    age = Int

    # The gender of the person:
    gender = Enum( 'Male', 'Female' )

    # The view to display for a person:
    view = View(
        Item( 'name' ),
        Item( 'age' ),
        Item( 'gender' )
    )

#-- Demo Class -----------------------------------------------------------------

class Demo ( HasFacets ):

    # The list of people to be displayed:
    people = List( Person )

    # The view to display of all of the people:
    view = View(
        Item( 'people',
              show_label = False,
              editor = VerticalNotebookEditor(
                  multiple_open = True,
                  scrollable    = True,
                  double_click  = False,
                  page_name     = '.name'
              )
        ),
        title     = 'VerticalNotebookEditor demo',
        width     = 0.20,
        height    = 0.50,
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = Demo( people = [
        Person( name = 'John',   age = 32, gender = 'Male'   ),
        Person( name = 'Alice',  age = 36, gender = 'Female' ),
        Person( name = 'George', age = 46, gender = 'Male'   ),
        Person( name = 'Tom',    age = 24, gender = 'Male'   ),
        Person( name = 'Peggy',  age = 29, gender = 'Female' ),
        Person( name = 'Gina',   age = 52, gender = 'Female' )
    ]
)

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------