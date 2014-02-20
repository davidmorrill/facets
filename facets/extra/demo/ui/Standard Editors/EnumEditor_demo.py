"""
# EnumEditor Demo #

This example provides some very basic demonstrations of using the various styles
of the **EnumEditor**, which allows a user to select a facet value from one of a
finite set of legal values.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Enum

from facets.api \
    import Item, Group, View

#-- EnumEditorDemo Class -------------------------------------------------------

class EnumEditorDemo ( HasFacets ):
    """ Defines the main EnumEditor demo class. """

    # Define an Enum facet to view:
    name_list = Enum( 'A-495', 'A-498', 'R-1226', 'TS-17', 'TS-18' )

    # Items are used to define the display, one Item per editor style:
    enum_group = Group(
        Item( 'name_list', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'name_list', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'name_list', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'name_list', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        enum_group,
        title     = 'EnumEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = EnumEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------