"""
# Hierarchical GridEditor Demo #

Demonstrates creating a hierarchical grid using the **GridEditor** in
conjunction with the **HierarchicalGridAdapter**.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from random \
    import randint, choice

from facets.api \
    import HasPrivateFacets, Str, Int, Enum, List, View, Item, GridEditor

from facets.ui.hierarchical_grid_adapter \
    import HierarchicalGridAdapter

#-- Person Class ---------------------------------------------------------------

class Person ( HasPrivateFacets ):

    name     = Str
    age      = Int
    weight   = Int
    gender   = Enum( 'Male', 'Female' )
    children = List # ( Person )

#-- PersonAdapter Class --------------------------------------------------------

class PersonAdapter ( HierarchicalGridAdapter ):

    columns = [
        ( 'Name',   'name'   ),
        ( 'Age',    'age'    ),
        ( 'Weight', 'weight' ),
        ( 'Gender', 'gender' ),
    ]

    def has_children ( self, person ):
        return (len( person.children ) > 0)

    def children ( self, person ):
        return person.children

    def on_children_changed ( self, person, listener, remove ):
        person.on_facet_set( listener, 'children[]', remove )

#-- HierarchicalGridEditorDemo class -------------------------------------------

class HierarchicalGridEditorDemo ( HasPrivateFacets ):

    # The list of people to display:
    people = List( Person )

    view = View(
        Item( 'people',
              show_label = False,
              editor     = GridEditor( adapter    = PersonAdapter,
                                       operations = [] )
        ),
        width  = 0.40,
        height = 0.67
    )

#-- Create the demo ------------------------------------------------------------

vowels     = 'aeiouy'
consonants = 'bcdfghjklmnprstw'

def random_name ( ):
    name = ''
    for i in xrange( randint( 5, 8 ) ):
        if (i % 2) == 0:
            name += choice( consonants )
        else:
            name += choice( vowels )

    return name.capitalize()

def random_person ( ):
    return Person( name   = random_name(),
                   age    = randint( 12, 83 ),
                   weight = randint( 50, 230 ),
                   gender = ( 'Male', 'Female' )[ randint( 0, 1 ) ] )

people = [ random_person() for i in xrange( randint( 10, 30 ) ) ]
for person in people:
    person.children = [ random_person() for i in xrange( randint( 0, 6 ) ) ]
    for child in person.children:
        child.children = [ random_person() for i in xrange( randint( 0, 6 ) ) ]
        for grand_child in child.children:
            grand_child.children = [ random_person()
                                     for i in xrange( randint( 0, 6 ) ) ]

# -- Create the demo -----------------------------------------------------------

demo = HierarchicalGridEditorDemo( people = people )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------
