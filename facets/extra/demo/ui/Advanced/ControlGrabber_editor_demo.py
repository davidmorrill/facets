"""
# ControlGrabberEditor Demo #

To use the demo, simply position the mouse pointer over the
**ControlGrabberEditor** icon in the top-left corner of the view, then click and
drag the mouse pointer over any Facets control and see the view update with
information about the control the mouse pointer is over. You can tell when the
ControlGrabberEditor is active because the mouse pointer changes to a question
mark.

The *Mouse Over Control* section of the view displays information about the
control currently being dragged over, while the *Selected Control* section shows
information about the most recent control the mouse pointer was over when the
left mouse button was released.

Note also how the ControlGrabberEditor icon changes to indicate its current
status:

- **Red**:    Inactive.
- **Yellow**: Mouse is hovering over the icon but the mouse button in not
  pressed.
- **Green**:  Active but not positioned over a Facets control.
- **Window**: Active and over a Facets control.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Property, Instance, Control, View, HGroup, VGroup, Item, \
           ControlGrabberEditor, InstanceEditor, property_depends_on

#-- The ControlView class (used to display information about a control) --------

class ControlView ( HasFacets ):

    # The control whose properties are displayed:
    control = Instance( Control )

    # The control properties to display:
    screen_position = Property
    size            = Property
    enabled         = Property

    # The control view to display:
    view = View(
        Item( 'screen_position', style = 'readonly' ),
        Item( 'size',            style = 'readonly' ),
        Item( 'enabled',         style = 'readonly' )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'control' )
    def _get_screen_position ( self ):
        if self.control is None:
            return '-'

        return self.control.screen_position

    @property_depends_on ( 'control' )
    def _get_size ( self ):
        if self.control is None:
            return '-'

        return self.control.size

    @property_depends_on ( 'control' )
    def _get_enabled ( self ):
        if self.control is None:
            return '-'

        return self.control.enabled

#-- Demo Class Definition ------------------------------------------------------

class Demo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The most recent control clicked on with the ControlGrabberEditor:
    selected = Instance( ControlView, () )

    # The most recent control moused over with the ControlGrabberEditor:
    over = Instance( ControlView, () )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HGroup(
            Item( 'object.selected.control',
                  show_label = False,
                  editor = ControlGrabberEditor( over = 'object.over.control' )
            )
        ),
        '_',
        VGroup(
            Item( 'over',
                  show_label = False,
                  style      = 'custom',
                  editor     = InstanceEditor()
            ),
            label = 'Mouse Over Control'
        ),
        VGroup(
            Item( 'selected',
                  show_label = False,
                  style      = 'custom',
                  editor     = InstanceEditor()
            ),
            label = 'Selected Control'
        ),
        title     = 'ControlGrabberEditor Demo',
        id        = 'facets.extra.demo.ui.Advanced.ControlGrabber_editor_demo',
        width     = 0.25,
        height    = 0.25,
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = Demo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------