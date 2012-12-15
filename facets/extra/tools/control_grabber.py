"""
A tool for 'grabbing' any Facets UI control and make it available to use with
other tools.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, Str, Property, Control, View, VGroup, HGroup, Item, \
           on_facet_set, property_depends_on

from facets.extra.editors.control_grabber_editor \
    import ControlGrabberEditor

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ControlGrabber' class:
#-------------------------------------------------------------------------------

class ControlGrabber ( Tool ):
    """ Allows you to 'grab' any Facets UI control and make it available to use
        with other tools.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Control Grabber' )

    # The current selected window:
    selected = Instance( Control, connect = 'from: selected control' )

    # The current control being mouse over:
    over = Instance( Control, connect = 'from: moused over control' )

    # The image of the current selected window:
    image = Property( connect = 'from: image of selected control' )

    # Description of the current control being moused over or selected:
    description = Str( 'Drag the icon over a control to select.' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'selected',
                      editor = ControlGrabberEditor( over = 'over' )
                ),
                Item( 'description', style = 'readonly', width = 0.1 ),
                show_labels = False
            ),
            VGroup()
        )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'selected' )
    def _get_image ( self ):
        if self.selected is not None:
            return self.selected.image

        return None

    #-- Facets Event Handlers --------------------------------------------------

    @on_facet_set( 'selected, over' )
    def _control_modified ( self, control ):
        if control is None:
            self.description = ''
            return

        klass    = control().__class__.__name__
        size     = ' (%d x %d)' % control.size
        dx, dy   = control.min_size
        min_size = ' has a min size of (%d, %d)' % ( dx, dy )
        n        = len( control.children )
        if n == 0:
            children = ''
        elif n == 1:
            children = ' with 1 child'
        else:
            children = ' with %d children' % n

        layout = control.layout
        if layout is None:
            layout_info = ''
        else:
            orientation = ( 'horizontal', 'vertical' )[ layout.is_vertical ]
            layout_info = ' and uses a %s %s' % (
                          orientation, layout().__class__.__name__ )

        self.description = '%s%s%s%s%s.' % (
                           klass, size, min_size, children, layout_info )

#-- EOF ------------------------------------------------------------------------