"""
# Animation Color Demo #

Another demonstration of using a custom *tweener* class with the Facets
animation system. Refer to the main *Animation_demo.py* module for a more in
depth discussion of Facets animation support, and to the
*Animation_tweener_demo.py* module for additional discussion of creating
custom *tweener* classes.

In this demo, the main **AnimationColorDemo** class has an
**HLSADerivedImage** object assigned to its ***image*** facet, which is
displayed using an **ImageZoomEditor**.

When the *Start* button is clicked, each of the ***hue***, ***lightness*** and
***saturation*** facets of the HLSADerivedImage object's ***transform*** facet's
**HLSATransform** object is animated through a range of values, with the
ImageZoomEditor displaying the changes.

You can cancel the current animation at any time by clicking the *Stop* button.

The demo uses a custom **Cycler** *tweener* class to control the animation of
each value. The Cycler class has a single parameter, ***n***, which defines the
number of times the animation cycles back and forth between its start and end
values. When the *Start* button is clicked, each animated facet is set up to use
a Cycler tweener with a different number of cycles specified.

The heart of the Cycler tweener is the ***at*** method:

    def at ( self, t ):
        v = fmod( t * self.n, 1.0 )
        if v >= 0.50:
            v = 1.0 - v

        return (2.0 * v)

The method converts the current time value ***t*** into a new time value which
represents the mapping from the main animation cycle into the current Cycler
cycle.

Note that the ImageZoomEditor still performs its normal functions while the
demo animation is running. Try zooming into the image with the mouse wheel and
panning while dragging the right mouse button. Also, be sure to drag select a
region of the image with the left mouse button and zoom in so that you can see
the display of the numeric color values for each of the individual pixels in the
selected region.

Finally, try double-clicking the image to auto-zoom into or out of the image.
This auto-zoom feature is part of the ImageZoomEditor definition and uses the
animation system to perform the animated zoom effect. Note how both the zoom
and color cycling animations work together concurrently.
"""

#-- Imports --------------------------------------------------------------------

from math \
    import fmod

from facets.api \
    import UIView, Int, Image, Button, View, HGroup, VGroup, Item, spring, \
           ImageZoomEditor

from facets.animation.api \
    import Tweener

from facets.extra.helper.image \
    import HLSADerivedImage

#-- Cycler Class ---------------------------------------------------------------

class Cycler ( Tweener ):

    #-- Facet Definitions ------------------------------------------------------

    # The number of cycles to perform:
    n = Int( 1 )

    #-- Tweener Method Overrides -----------------------------------------------

    def at ( self, t ):
        v = fmod( t * self.n, 1.0 )
        if v >= 0.50:
            v = 1.0 - v

        return (2.0 * v)

#-- AnimationColorDemo Class ---------------------------------------------------

class AnimationColorDemo ( UIView ):

    #-- Facet Definitions ------------------------------------------------------

    # The image to animate:
    image = Image

    # The animation controls:
    start = Button( 'Start' )
    stop  = Button( 'Stop' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'image', editor = ImageZoomEditor( channel = 'hue' ) ),
            '_',
            HGroup(
                spring,
                Item( 'start' ),
                Item( 'stop'  ),
                show_labels = False,
            ),
            show_labels = False
        ),
        title     = 'Animation Color Demo',
        id        = 'facets.extra.demo.ui.Advanced.Animation_color_demo',
        width     = 400,
        height    = 400,
        resizable = True
    )

    #-- Facet Default Values ---------------------------------------------------

    def _image_default ( self ):
        return HLSADerivedImage( base_image = '@demo:Facets_power' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _start_set ( self ):
        """ Start a new animation running.
        """
        self._stop_set()
        transform = self.image.transform
        transform.animate_facet(
            'hue', 60.0, 1.0, 0.0, tweener = Cycler( n = 2 )
        )
        transform.animate_facet(
            'lightness', 60.0, 0.1, -0.1, tweener = Cycler( n = 5 )
        )
        transform.animate_facet(
            'saturation', 60.0, 0.4, -0.2, tweener = Cycler( n = 3 )
        )

    def _stop_set ( self ):
        """ Make sure any currently running animation has been stopped.
        """
        self.image.transform.halt_animated_facets()

    def _ui_info_set ( self, ui_info ):
        """ Make sure the animation is stopped when the view closes.
        """
        if ui_info is None:
            self._stop_set()

#-- Create the demo ------------------------------------------------------------

demo = AnimationColorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo(
        image = HLSADerivedImage( base_image = '@facets:hs_color_map' )
    ).edit_facets()

#-- EOF ------------------------------------------------------------------------
