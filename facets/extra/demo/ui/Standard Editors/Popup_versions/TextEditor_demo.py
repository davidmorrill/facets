"""
Implementation of a TextEditor demo plugin for the Facets UI demo program.

For each of three data types for which TextEditor is used, this demo shows
each of the four styles of the TextEditor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Int, Password, Item, Group, View, Tabbed

#-- TextEditorDemo Class -------------------------------------------------------

class TextEditorDemo ( HasFacets ):
    """ This class specifies the details of the TextEditor demo.
    """

    # Define a facet for each of three variants:
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
        Item( 'string_facet', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'string_facet', style = 'custom',   label = 'Custom' ),
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

    # The view includes one group per data type.  These will be displayed
    # on separate tabbed panels.
    view1 = View(
        Tabbed(
            text_int_group,
            text_str_group,
            text_pass_group
        ),
        title   = 'TextEditor',
        buttons = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

popup = TextEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().configure_facets()

#-- EOF ------------------------------------------------------------------------