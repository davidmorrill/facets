"""
# TextEditor Demo #

This example demonstrates using the various styles of the **TextEditor**, which
allows the user to enter text into a single or multi-line text entry control.

In addition, the **TextEditor** can also be configured to display a *read-only*
text value, or perform validation on values entered by the user.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Int, Password, Item, Group, View, Tabbed

#-- Demo Class -----------------------------------------------------------------

class TextEditorDemo ( HasFacets ):
    """ Defines the TextEditor demo class.
    """

    # Define a facet for each of three TextEditor variants:
    string_facet = Str( "sample string" )
    int_facet    = Int( 1 )
    password     = Password

    # TextEditor display without multi-line capability (for various facets):
    text_int_group = Group(
        Item( 'int_facet', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'int_facet', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'int_facet', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'int_facet', style = 'readonly', label = 'ReadOnly' ),
        label = 'Integer'
    )

    # TextEditor display with multi-line capability (for various facets):
    text_str_group = Group(
        Item( 'string_facet', style = 'simple',  label = 'Simple' ),
        Item( '_' ),
        Item( 'string_facet', style = 'custom',  label = 'Custom' ),
        Item( '_' ),
        Item( 'string_facet', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'string_facet', style = 'readonly', label = 'ReadOnly' ),
        label = 'String'
    )

    # TextEditor display with secret typing capability (for Password facets):
    text_pass_group = Group(
        Item( 'password', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'password', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'password', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'password', style = 'readonly', label = 'ReadOnly' ),
        label = 'Password'
    )

    # The view includes one group per data type. These will be displayed on
    # separate tabbed panels:
    view = View(
        Tabbed(
            #text_int_group,
            text_str_group,
            #text_pass_group
        ),
        title   = 'TextEditor',
        buttons = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

demo = TextEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == "__main__":
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------