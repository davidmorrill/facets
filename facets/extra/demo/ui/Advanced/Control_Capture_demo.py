"""
This is a fun little demo illustrating use of the Handler base class and the
FilmStripEditor and ImageZoomEditor editors.

The first thing to note is that the main Demo class derives from UIView instead
of HasFacets. This means the Demo class automatically has its 'ui_info'
attribute set to the view's UIInfo object when the view is opened, providing it
with access to the view's main Control object.

Each time the Refresh button is clicked, we use the UIInfo object to get a
reference to the view's Control object. From this we create a list of all of the
non-overlapping controls contained in the entire application, using the
control's 'root_parent' property to obtain a reference to the topmost Control of
the window.

Finally, we use each resulting Control's 'image' property to obtain a current
screen capture of the control's contents and use the images to populate the
FilmStripEditor displayed in the left-hand part of the view.

Selecting an image in the FilmStripEditor displays the full-size image in the
ImageZoomEditor on the right side of the display, which you can use to
dynamically zoom in and and of the image.

Note that we specifically capture only non-overlapping controls to make sure
each image is a unique section of the complete application view. As a result,
the demo does not capture some parts of the application view, such as
DockWindow tabs, since these are part of a DockWindow control, which contains
(and overlaps with) all of the control it manages.

A careful reader may also note the use of 'do_after' in the 'facets_init'
method. This is done to schedule an initial image capture after the demo has had
a chance to appear on the screen.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, UIView, Tuple, Instance, List, Control, Button, Image, \
           View, HGroup, Item, FilmStripEditor, ImageZoomEditor, spring

from facets.ui.pyface.timer.api \
    import do_after

#-- ControlInfo ----------------------------------------------------------------

class ControlInfo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The control:
    control = Instance( Control )

    # The screen bounds of the control:
    bounds = Tuple

    #-- Facet View Definitions -------------------------------------------------

    def _bounds_default ( self ):
        x, y   = self.control.screen_position
        dx, dy = self.control.size

        return ( x, y, x + dx, y + dy )

    #-- Public Methods ---------------------------------------------------------

    def overlaps ( self, info ):
        xl0, yt0, xr0, yb0 = self.bounds
        xl1, yt1, xr1, yb1 = info.bounds

        return (not ((xl0 >= xr1) or
                     (xl1 >= xr0) or
                     (yt0 >= yb1) or
                     (yt1 >= yb0)))

#-- Demo Class Definition ------------------------------------------------------

class Demo ( UIView ):

    #-- Facet Definitions ------------------------------------------------------

    # The images derived from the current selected control:
    images = List # ( Image )

    # The currently selected image:
    image = Image

    # The event fired when the images should be regenerated:
    refresh = Button( 'Refresh' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HGroup(
            Item( 'images',
                  width  = -200,
                  editor = FilmStripEditor( orientation = 'vertical',
                                            selected    = 'image' )
            ),
            Item( 'image',
                  editor = ImageZoomEditor( channel = 'hue' )
            ),
            show_labels = False,
            group_theme = '#themes:toolbar_group'
        ),
        HGroup(
            spring,
            Item( 'refresh', show_label = False ),
            group_theme = '#themes:toolbar_group'
        ),
        title     = 'Control Capture Demo',
        id        = 'facets.extra.demo.ui.Advanced.Control_Capture_demo',
        width     = 0.50,
        height    = 0.80,
        resizable = True
    )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        do_after( 300, self._refresh_set )

    #-- Facet Event Handlers ---------------------------------------------------

    def _refresh_set ( self ):
        valid = []
        info  = []
        self._info_for( self.ui_info.ui.control.root_parent, info )
        n = len( info )
        for i, item in enumerate( info ):
            for j in xrange( i + 1, n ):
                if item.overlaps( info[ j ] ):
                    break
            else:
                valid.append( item )

        self.images = [ item.control.image for item in valid ]

    #-- Private Methods --------------------------------------------------------

    def _info_for ( self, control, info ):
        if control.visible:
            dx, dy = control.size
            if (dx * dy) != 0:
                info.append( ControlInfo( control = control ) )

            for child in control.children:
                self._info_for( child, info )

#-- Create the demo ------------------------------------------------------------

demo = Demo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
