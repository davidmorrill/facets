"""
# Animation Tweener Demo #

A demonstration of creating a custom *tweener* class for use with the Facets UI
animation system. Refer to the main *Animation_demo.py* module for a more in
depth discussion of Facets animation support.

In this demo, the main **Demo** class defines a number of identical **Range**
facets with values in the range from 0.0 to 1.0. When the *Start* button is
clicked, each of the facets is animated between its low and high values, with
the associated **RangeEditor** tracking the changes. You can cancel the current
animation at any time by clicking the *Stop* button.

To make the demo more interesting, we define a custom **Cycler** *tweener* class
to control the animation of each value. The Cycler class has a single control,
***n***, which defines the number of times the animation should cycle back and
forth between its start and end values. When the *Start* button is clicked, each
animated facet is set to use a Cycler tweener with an increasing number of
cycles specified.

The heart of the Cycler tweener is the ***at*** method:

    def at ( self, t ):
        v = fmod( t * self.n, 1.0 )
        if v >= 0.50:
            v = 1.0 - v

        return (((tanh( (10.0 * v) - 2.5 ) / tanh( 2.5 )) + 1.0) / 2.0)

The first few lines of the method convert the current time value ***t*** into a
new time value ***v*** which represents the mapping from the main animation
cycle into the current Cycler cycle.

The final *return* statement performs an *ease-in/ease-out* calculation that
slows the animation down as the value approaches either the start or end point,
and speeds it up at positions in between.
"""

#-- Imports --------------------------------------------------------------------

from math \
    import fmod, tanh

from facets.api \
    import UIView, Int, Range, Button, View, VGroup, HGroup, Item, \
           RangeEditor, spring

from facets.animation.api \
    import Tweener

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

        return (((tanh( (10.0 * v) - 2.5 ) / tanh( 2.5 )) + 1.0) / 2.0)

#-- REItem (RangeEditorItem) Class ------------------------------------------

class REItem ( Item ):
    editor = RangeEditor( body_style = 19, format_str = '%.2f' )

#-- Demo Class -----------------------------------------------------------------

DemoRange = Range( 0.0, 1.0 )

class AnimationTweenerDemo ( UIView ):

    #-- Facet Definitions ------------------------------------------------------

    # The values to animate:
    v1 = DemoRange
    v2 = DemoRange
    v3 = DemoRange
    v4 = DemoRange
    v5 = DemoRange
    v6 = DemoRange
    v7 = DemoRange
    v8 = DemoRange

    # The animation controls:
    start = Button( 'Start' )
    stop  = Button( 'Stop' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            REItem( 'v1', label = 'n = 1' ),
            REItem( 'v2', label = 'n = 2' ),
            REItem( 'v3', label = 'n = 3' ),
            REItem( 'v4', label = 'n = 4' ),
            REItem( 'v5', label = 'n = 5' ),
            REItem( 'v6', label = 'n = 6' ),
            REItem( 'v7', label = 'n = 7' ),
            REItem( 'v8', label = 'n = 8' )
        ),
        '_',
        HGroup(
            spring,
            Item( 'start' ),
            Item( 'stop'  ),
            show_labels = False,
        ),
        title     = 'Animation Tweener Demo',
        id        = 'facets.extra.demo.ui.Advanced.Animation_tweener_demo',
        width     = 600,
        resizable = True
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _start_set ( self ):
        """ Start a new animation running.
        """
        self._stop_set()
        for i in xrange( 1, 9 ):
            self.animate_facet(
                'v%d' % i, 20.0, 1.0, 0.0, tweener = Cycler( n = i )
            )

    def _stop_set ( self ):
        """ Make sure any currently running animation has been stopped.
        """
        self.halt_animated_facets()

    def _ui_info_set ( self, ui_info ):
        """ Make sure the animation is stopped when the view closes.
        """
        if ui_info is None:
            self._stop_set()

#-- Create the demo ------------------------------------------------------------

demo = AnimationTweenerDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
