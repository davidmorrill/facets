"""
Implementation of a ButtonEditor demo plugin for Facets UI demo program.

This demo shows each of the two styles of the ButtonEditor.
(As of this writing, they are identical.)
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Button, Item, View, Group

from facets.ui.message \
    import message

#-- ButtonEditorDemo Class -----------------------------------------------------

class ButtonEditorDemo ( HasFacets ):
    """ This class specifies the details of the ButtonEditor demo.
    """

    # To demonstrate any given Facet editor, an appropriate Facet is required:
    fire_event = Button( 'Click Me' )

    # Facet event handler:
    def _fire_event_set ( ):
        message( "Button clicked!" )

    # ButtonEditor display:
    # (Note that Text and ReadOnly versions are not applicable)
    event_group = Group(
        Item( 'fire_event', style = 'simple', label = 'Simple' ),
        Item( '_' ),
        Item( 'fire_event', style = 'custom', label = 'Custom' ),
        Item( '_' ),
        Item( label = '[text style unavailable]' ),
        Item( '_' ),
        Item( label = '[read only style unavailable]' )
    )

    # Demo view:
    view1 = View(
        event_group,
        title   = 'ButtonEditor',
        buttons = [ 'OK' ],
        width   = 250
    )

#-- Create the demo ------------------------------------------------------------

popup = ButtonEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------