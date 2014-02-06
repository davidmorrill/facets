"""
# Simple Enabled When #

This example illustrates the dynamic enabling and disabling of facet editors
based on other facet values in the same user interface.

The **Person** class has facets that apply to all instances: *first_name*,
*last_name* and *age*, and facets that are specific to an age group:
*marital_status* and *registered_voter* for adults, and *legal_guardian* for
children. The adult specific facets are disabled if *age* is less than 18;
otherwise the child specific facets are disabled.

Note: The *enabled_when* expression for a given **Item** must be a condition
involving one or more facets (e.g. *'age >= 18'*) so that the evaluation of the
expression is triggered by one of the referenced facets changing value.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

# Imports:
from facets.core_api \
    import HasFacets, Str, Range, Enum, Bool

from facets.api \
    import Item, Group, View


class Person ( HasFacets ):
    """ Demo class for demonstrating enabling/disabling of facet editors
    """

    first_name       = Str
    last_name        = Str
    age              = Range( 0, 120 )
    marital_status   = Enum( 'single', 'married', 'divorced', 'widowed' )
    registered_voter = Bool
    legal_guardian   = Str

    # Interface for attributes that are always enabled:
    gen_group = Group(
        Item( name = 'first_name' ),
        Item( name = 'last_name' ),
        Item( name = 'age' ),
        label       = 'General Info',
        show_border = True
    )

    # Interface for adult-only attributes:
    adult_group = Group(
        Item( name = 'marital_status' ),
        Item( name = 'registered_voter' ),
        enabled_when = 'age >= 18',
        label        = 'Adults',
        show_border  = True
    )

    # Interface for child-only attribute:
    child_group = Group(
        Item( name         = 'legal_guardian',
              enabled_when = 'age < 18' ),
        label        = 'Minors',
        show_border  = True
    )

    # The view specification is simple, as the group specs have done the work:
    view = View(
        Group(
            gen_group,
            adult_group,
            child_group
        ),
        resizable = True,
        buttons   = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

demo = Person(
    first_name = 'Samuel',
    last_name  = 'Johnson',
    age        = 16
)

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------