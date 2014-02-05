"""
# Auto Update GridEditor Demo #

Demonstrates using a **GridEditor** with the *monitor* feature enabled, which
allows the grid editor to automatically update itself when the content of any
object in the list associated with the editor is modified.

To interact with the demo:

- Select an employee from the list.
- Adjust their salary increase.
- Click the **Give raise** button.
- Observe that the table automatically updates to reflect the employees new
  salary.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Float, List, Instance, Button, View, HGroup, Item, \
           GridEditor, spring

from facets.ui.grid_adapter \
    import GridAdapter

#-- EmployeeAdapter Class ------------------------------------------------------

class EmployeeAdapter ( GridAdapter ):

    columns = [ ( 'Name', 'name' ), ( 'Salary', 'salary' ) ]

#-- Employee Class -------------------------------------------------------------

class Employee ( HasFacets ):

    name   = Str
    salary = Float

#-- Company Class --------------------------------------------------------------

class Company ( HasFacets ):

    employees  = List( Employee )
    employee   = Instance( Employee )
    increase   = Float
    give_raise = Button( 'Give raise' )

    view = View(
        Item( 'employees',
              show_label = False,
              editor     = GridEditor( adapter     = EmployeeAdapter,
                                       operations  = [],
                                       selected    = 'employee',
                                       monitor     = 'selected' )
        ),
        HGroup(
            spring,
            Item( 'increase' ),
            Item( 'give_raise',
                  show_label   = False,
                  enabled_when = 'employee is not None' )
        ),
        title     = 'Auto Update GridEditor demo',
        height    = 0.25,
        width     = 0.30,
        resizable = True
    )

    def _give_raise_set ( self ):
        self.employee.salary += self.increase

#-- Create the demo ------------------------------------------------------------

demo = Company( increase = 1000, employees = [
    Employee( name = 'Fred',   salary = 45000 ),
    Employee( name = 'Sally',  salary = 52000 ),
    Employee( name = 'Jim',    salary = 39000 ),
    Employee( name = 'Helen',  salary = 41000 ),
    Employee( name = 'George', salary = 49000 ),
    Employee( name = 'Betty',  salary = 46000 )
] )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------