"""
# List Editors Demo #

This shows three different types of editor that can be applied to a list of
objects:

- Grid
- List
- Tabbed Notebook

Each editor style is editing the exact same list of objects. Note that any
changes made in one editor are automatically reflected in the others.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasStrictFacets, Str, Int, Float, Regex, List, Instance, View, \
           Item, Tabbed, GridEditor, ListEditor, NotebookEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- Person Class ---------------------------------------------------------------

class Person ( HasStrictFacets ):

    # Facet definitions:
    name  = Str
    age   = Int
    phone = Regex( value = '000-0000', regex = '\d\d\d[-]\d\d\d\d' )

    # Facets view definition:
    facets_view = View(
        'name', 'age', 'phone',
        width   = 0.18,
        buttons = [ 'OK', 'Cancel' ]
    )

#-- Sample data ----------------------------------------------------------------

people = [
   Person( name = 'Dave',   age = 39, phone = '555-1212' ),
   Person( name = 'Mike',   age = 28, phone = '555-3526' ),
   Person( name = 'Joe',    age = 34, phone = '555-6943' ),
   Person( name = 'Tom',    age = 22, phone = '555-7586' ),
   Person( name = 'Dick',   age = 63, phone = '555-3895' ),
   Person( name = 'Harry',  age = 46, phone = '555-3285' ),
   Person( name = 'Sally',  age = 43, phone = '555-8797' ),
   Person( name = 'Fields', age = 31, phone = '555-3547' )
]

#-- Grid Editor Definition -----------------------------------------------------

class ListAdapter ( GridAdapter ):

    columns = [ ( 'Name', 'name' ), ( 'Age', 'age' ), ( 'Phone', 'phone' ) ]

    name_width  = Float( 0.4 )
    age_width   = Float( 0.2 )
    phone_width = Float( 0.4 )

#-- ListFacetTest Class --------------------------------------------------------

class ListFacetTest ( HasStrictFacets ):

    # Facet definitions:
    people = List( Instance( Person, () ) )

    # Facets view definitions:
    facets_view = View(
        Tabbed(
            Item( 'people',
                  label  = 'Grid',
                  id     = 'grid',
                  editor = GridEditor( adapter = ListAdapter )
            ),
            Item( 'people@',
                  label  = 'List',
                  id     = 'list',
                  editor = ListEditor( style = 'custom', rows  = 5 )
            ),
            Item( 'people@',
                  label  = 'Notebook',
                  id     = 'notebook',
                  editor = NotebookEditor( deletable = True,
                                           export    = 'DockShellWindow',
                                           page_name = '.name',
                                           layout    = 'columns',
                                           max_items = 3 )
            ),
            id          = 'splitter',
            show_labels = False
        ),
        id        = 'facets.extra.demo.ui.Advanced.List_editors_demo',
        dock      = 'horizontal',
        width     = 0.50,
        height    = 0.75,
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = ListFacetTest( people = people )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------