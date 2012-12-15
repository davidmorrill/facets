"""
Implementation of an InstanceEditor demo plugin for the Facets UI demo program.

This demo shows each of the four styles of the InstanceEditor.

Fixme: This version of the demo only shows the old-style InstanceEditor
capabilities.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Range, Bool, Facet, Item, Group, View

#-- SampleClass Class ----------------------------------------------------------

class SampleClass ( HasFacets ):
    """ This Sample class is used to demonstrate the InstanceEditor demo.
    """

    # The actual attributes don't matter here; we just need an assortment to
    # demonstrate the InstanceEditor's capabilities.
    name             = Str
    occupation       = Str
    age              = Range( 21, 65 )
    registered_voter = Bool

    # The InstanceEditor uses whatever view is defined for the class. The
    # default view lists the fields alphabetically, so it's best to define one
    # explicitly:
    view = View( 'name', 'occupation', 'age', 'registered_voter' )

#-- InstanceEditorDemo Class ---------------------------------------------------

class InstanceEditorDemo ( HasFacets ):
    """ This class specifies the details of the InstanceEditor demo.
    """

    # To demonstrate any given Facet editor, an appropriate Facet is required:
    sample_instance  = Facet( SampleClass() )

    # Items are used to define the demo display - one item per
    # editor style:
    inst_group = Group(
        Item( 'sample_instance', style = 'simple', label = 'Simple' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'custom', label = 'Custom' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'text', label = 'Text' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo View:
    view1 = View(
        inst_group,
        title   = 'InstanceEditor',
        buttons = [ 'OK' ]
    )

#-- Create the demo: -----------------------------------------------------------

popup = InstanceEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------