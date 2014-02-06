"""
# Visible When #

This example shows a simple implementation of the dynamic updating of the
visible contents of a **View** on the basis of some facet's assigned value.

The **Person** class has a set of attributes that apply to all instances:
*first_name*, *last_name* and *age*, a set of attributes that apply only
to children (i.e. persons whose age is under 18), and a set of attributes that
apply only to adults.  The view for the Person object is defined in such
a way that the set of visible fields changes accordingly as the value of the
*age* facet crosses the boundary between child and adult.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

# Imports:
from facets.core_api \
    import HasFacets, Str, Range, Bool, Enum

from facets.api \
    import Item, Group, View

class Person ( HasFacets ):

    # General facets:
    first_name = Str
    last_name  = Str
    age        = Range( 0, 120 )

    # Facets for children only:
    legal_guardian = Str
    school         = Str
    grade          = Range( 1, 12 )

    # Facets for adults only:
    marital_status   = Enum( 'single', 'married', 'divorced', 'widowed' )
    registered_voter = Bool( False )
    military_service = Bool( False )

    # Interface for attributes that are always visible in interface:
    gen_group = Group(
        Item( name = 'first_name' ),
        Item( name = 'last_name' ),
        Item( name = 'age' ),
        label       = 'General Info',
        show_border = True
    )

    # Interface for attributes of Persons under 18:
    child_group = Group(
        Item( name = 'legal_guardian' ),
        Item( name = 'school' ),
        Item( name = 'grade' ),
        label        = 'Additional Info',
        show_border  = True,
        visible_when = 'age < 18'
    )

    # Interface for attributes of Persons 18 and over:
    adult_group = Group(
        Item( name = 'marital_status' ),
        Item( name = 'registered_voter' ),
        Item( name = 'military_service' ),
        label        = 'Additional Info',
        show_border  = True,
        visible_when = 'age >= 18'
    )

    # A simple View is sufficient, since the Group definitions do all the work:
    view = View(
        Group(
            gen_group,
            child_group,
            adult_group
        ),
        title     = 'Personal Information',
        resizable = True,
        buttons   = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

demo = Person(
    first_name = "Samuel",
    last_name  = "Johnson",
    age        = 16
)

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------