"""
# ControlGrabber #

This demonstrates using the **ControlGrabberEditor** in concert with the
**HLSADerivedImageEditor**.

Click-drag on the **ControlGrabberEditor** (represented by the question mark
icon) and release the mouse pointer over another part of the demo (e.g. the tree
view). The **ControlGrabberEditor** will set its value (the ***control*** facet
of the **ControlGrabberDemo** object) to the *Control* the mouse pointer is over
at the time that the mouse button is released.

The demo code responds by creating a *screen capture>/i> of the control's
contents using the ***image*** facet of the control, which is assigned to the
demo's ***image*** facet, which is edited using an **HLSADerivedImageEditor*.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Event, Image, View, VGroup, Item, ControlGrabberEditor, \
           HLSADerivedImageEditor

#-- ControlGrabber Class -------------------------------------------------------

class ControlGrabber ( HasFacets ):

    # Facet definitions:
    control = Event
    image   = Image( '@std:alert16' )

    # Facet view definitions:
    view = View(
        VGroup(
            Item( 'control',
                  editor  = ControlGrabberEditor(),
                  tooltip = 'Drag this icon over another control and release.'
            ),
            '_',
            Item( 'image', editor = HLSADerivedImageEditor() ),
            show_labels = False
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        if control is not None:
            self.image = control.image

#-- Create The Demo ------------------------------------------------------------

demo = ControlGrabber

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
