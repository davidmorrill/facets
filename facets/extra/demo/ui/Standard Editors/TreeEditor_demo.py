"""
# TreeEditor Demo #

This example demonstrates using a **TreeEditor**, which is typically used for
displaying, selecting and editing collections of values which can be organized
hierarchically.

In this example, we are displaying a tree representing the organization of a
small company:

    - Partner
      - Company
        - Department
          - Employee
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Str, Regex, List, Instance

from facets.api \
    import Item, View, TreeEditor, TreeNode

#-- Employee Class -------------------------------------------------------------

class Employee ( HasFacets ):
    """ Defines a company employee. """

    name  = Str( '<unknown>' )
    title = Str( 'Senior Engineer' )
    phone = Regex( regex = r'\d\d\d-\d\d\d\d' )

#-- Department Class -----------------------------------------------------------

class Department ( HasFacets ):
    """ Defines a department with employees. """

    name      = Str( '<unknown>' )
    employees = List( Employee )

#-- Company Class --------------------------------------------------------------

class Company ( HasFacets ):
    """ Defines a company with departments and employees. """

    name        = Str( '<unknown>' )
    departments = List( Department )
    employees   = List( Employee )

#-- Tree Editor Definitions ----------------------------------------------------

# Create an empty view for objects that have no data to display:
no_view = View()

# Define the TreeEditor used to display the hierarchy:
tree_editor = TreeEditor(
    nodes = [
        TreeNode( node_for  = [ Company ],
                  auto_open = True,
                  children  = '',
                  label     = 'name',
                  view      = View( [ 'name' ] )
        ),
        TreeNode( node_for  = [ Company ],
                  auto_open = True,
                  children  = 'departments',
                  label     = '=Departments',
                  view      = no_view,
                  add       = [ Department ],
        ),
        TreeNode( node_for  = [ Company ],
                  auto_open = True,
                  children  = 'employees',
                  label     = '=Employees',
                  view      = no_view,
                  add       = [ Employee ]
        ),
        TreeNode( node_for  = [ Department ],
                  auto_open = True,
                  children  = 'employees',
                  label     = 'name',
                  view      = View( [ 'name' ] ),
                  add       = [ Employee ]
        ),
        TreeNode( node_for  = [ Employee ],
                  auto_open = True,
                  label     = 'name',
                  view      = View( [ 'name', 'title', 'phone' ] )
        )
    ]
)

#-- Partner Class --------------------------------------------------------------

class Partner ( HasFacets ):
    """ Defines a business partner."""

    name    = Str( '<unknown>' )
    company = Instance( Company )

    view = View(
        Item( name       = 'company',
              editor     = tree_editor,
              show_label = False
        ),
        title     = 'Company Structure',
        buttons   = [ 'OK' ],
        resizable = True,
        style     = 'custom',
        width     = .3,
        height    = .3
    )

#-- Create an example data structure -------------------------------------------

dave    = Employee( name  = 'Dave',
                    title = 'Senior Software Developer',
                    phone = '536-1053' )
martine = Employee( name  = 'Martine',
                    title = 'Senior Engineer',
                    phone = '536-1054' )
ralph   = Employee( name  = 'Ralph',
                    title = 'Consultant',
                    phone = '526-1055' )
dilbert = Employee( name  = 'Dilbert',
                    title = 'Senior Engineer',
                    phone = '536-1051' )
mike    = Employee( name  = 'Mike',
                    title = 'Senior Engineer',
                    phone = '536-1052' )

#-- Create the demo ------------------------------------------------------------

demo = Partner(
    name    = 'Acme, Inc.',
    company = Company(
        name        = 'Acme',
        employees   = [ dave, martine, ralph, dilbert, mike ],
        departments = [
            Department(
                name      = 'Business',
                employees = [ dilbert, mike ]
            ),
            Department(
                name      = 'Advertising',
                employees = [ dave, martine, ralph ]
            )
        ]
    )
)

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------