"""
# InstanceEditor Demo #

This example demonstrates using the various styles of the **InstanceEditor**,
which allows the user to edit a facet whose value is an object that derives from
**HasFacets**.

This is a very powerful and flexible editor with which you can:

- Dynamically display a custom user interface for a referenced object. Changing
  the object reference will automatically update the view with the user
  interface for the new object reference.
- Allow the user to choose an object value from a set of existing objects.
- Allow the user to create a new object value using a factory (i.e.
  constructor).
- Use any combination of the above.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Str, Range, Bool, Instance

from facets.api \
    import Item, Group, View

#-- SampleClass Class ----------------------------------------------------------

class SampleClass ( HasFacets ):
    """ This Sample class is used to demonstrate the InstanceEditor demo.
    """

    # The actual attributes don't matter here; we just need an assortment
    # to demonstrate the InstanceEditor's capabilities.:
    name             = Str
    occupation       = Str
    age              = Range( 21, 65 )
    registered_voter = Bool

    # The InstanceEditor uses whatever view is defined for the class.  The
    # default view lists the fields alphabetically, so it's best to define one
    # explicitly:
    view = View( 'name', 'occupation', 'age', 'registered_voter' )

#-- InstanceEditorDemo Class ---------------------------------------------------

class InstanceEditorDemo ( HasFacets ):
    """ This class specifies the details of the InstanceEditor demo.
    """

    # Create an Instance facet to view:
    sample_instance = Instance( SampleClass, () )


    # Items are used to define the demo display, one item per editor style:
    inst_group = Group(
        Item( 'sample_instance', style = 'simple',  label = 'Simple' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'custom',  label = 'Custom' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'text',    label = 'Text' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo View:
    view = View(
        inst_group,
        title   = 'InstanceEditor',
        buttons = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = InstanceEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------