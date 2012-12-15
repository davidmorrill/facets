"""
Demonstrates using the TreeEditor to display a hierarchically organized data
structure.

In this case, the tree has the following hierarchy:
  - Partner
    - Company
      - Department
        - Employee
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Regex, List, Instance, Item, View, TreeEditor, \
           TreeNode

#-- Employee Class -------------------------------------------------------------

class Employee ( HasFacets ):
    name  = Str( '<unknown>' )
    title = Str
    phone = Regex( regex = r'\d\d\d-\d\d\d\d' )

    def default_title ( self ):
        self.title = 'Senior Engineer'

#-- Department Class -----------------------------------------------------------

class Department ( HasFacets ):
    name      = Str( '<unknown>' )
    employees = List( Employee )

#-- Company Class --------------------------------------------------------------

class Company ( HasFacets ):
    name        = Str( '<unknown>' )
    departments = List( Department )
    employees   = List( Employee )

#-- TreeEditor Definitions -----------------------------------------------------

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
                  add       = [ Department ]
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

jason  = Employee( name  = 'Jason',
                   title = 'Senior Engineer',
                   phone = '536-1057' )
mike   = Employee( name  = 'Mike',
                   title = 'Senior Engineer',
                   phone = '536-1057' )
dave   = Employee( name  = 'Dave',
                   title = 'Senior Software Developer',
                   phone = '536-1057' )
martin = Employee( name  = 'Martin',
                   title = 'Senior Engineer',
                   phone = '536-1057' )
duncan = Employee( name  = 'Duncan',
                   title = 'Consultant',
                   phone = '526-1057' )

#-- Create the demo ------------------------------------------------------------

popup = Partner(
    name    = 'Acme, Inc.',
    company = Company(
        name        = 'Acme',
        employees   = [ dave, martin, duncan, jason, mike ],
        departments = [
            Department(
                name      = 'Business',
                employees = [ jason, mike ]
            ),
            Department(
                name      = 'Scientific',
                employees = [ dave, martin, duncan ]
            )
        ]
    )
)

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup.edit_facets()

#-- EOF ------------------------------------------------------------------------