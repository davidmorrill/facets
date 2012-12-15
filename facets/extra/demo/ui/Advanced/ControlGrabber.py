"""
This demonstrates using the <b>ControlGrabberEditor</b> in concert with the
<b>HLSADerivedImageEditor</b>.

Click-drag on the <b>ControlGrabberEditor</b> (represented by the question mark
icon) and release the mouse pointer over another part of the demo (e.g. the tree
view). The <b>ControlGrabberEditor</b> will set its value (the
<b><i>control</i></b> facet of the <b>ControlGrabberDemo</b> object) to the
<i>Control</i> the mouse pointer is over at the time that the mouse button is
released.

The demo code responds by creating a <i>screen capture>/i> of the control's
contents using the <b></i>image</i></b> facet of the control, which is assigned
to the demo's <b><i>image</i></b> facet, which is edited using an
<b>HLSADerivedImageEditor</i>.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Event, Image, View, VGroup, Item

from facets.extra.editors.control_grabber_editor \
    import ControlGrabberEditor

from facets.extra.editors.hlsa_derived_image_editor \
    import HLSADerivedImageEditor

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
