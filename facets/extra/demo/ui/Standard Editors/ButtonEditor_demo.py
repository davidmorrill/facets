"""
Implementation of a ButtonEditor demo plugin for Facets UI demo program.

This demo shows each of the two styles of the ButtonEditor
(As of this writing, they are identical.)
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Button, Item, View, Group

#-- ButtonEditorDemo Class -----------------------------------------------------

class ButtonEditorDemo ( HasFacets ):
    """ Defines the main ButtonEditor demo class. """

    # Define a Button facet:
    fire_event = Button( 'Click Me' )

    def _fire_event_set ( self ):
        print 'Button clicked!'

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
    view = View(
        event_group,
        title     = 'ButtonEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = ButtonEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------