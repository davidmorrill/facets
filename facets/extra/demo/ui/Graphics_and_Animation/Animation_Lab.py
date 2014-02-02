"""
# Animation Lab #

A laboratory environment for trying out the various animation system
*tweeners* and *paths*.

The Facets *animation* system consists mainly of ***Tweener***, ***Path*** and
***Animation*** objects. In this demo we focus on the behavior of the different
standard **Tweener** and **Path** classes available by creating a simple
environment for you to try them out in. There are also options to have a hand at
creating and trying out your own custom paths and tweeners.

The demo is divided into five main sections:
 - ***Animation Lab***: This is where you try out the various paths and tweeners
   available.
 - ***Custom Path***: This tab allows you to create your own custom **Path**
   class by modifying a code template.
 - ***Custom Tweener***: This tab allows you to create a custom **Tweener**
   class by modifying the provided code template.
 - ***Path Graphs***: This tabs shows you two views of the current **Path** you
   have selected. One view shows you the raw path data, while the other shows
   you the path data after having applied the current composite tweener.
 - ***Tweener Graphs***: Similar to the ***Path Graphs*** tab, but showing the
   graphs for the individual tweeners as well as the final tweener resulting
   from compositing the three individual tweeners.

The main ***Animation Lab*** tab is occupied by a canvas containing two animated
boxes. The boxes simply animate from their location to the location of the other
box using the ***Path*** and ***Tweener*** objects you select and modify in the
column on the left.

The objects in this column are selected using the drop-down lists which show the
various standard types of **2D Path** and **Tweener** classes available. If a
selected **Path** or **Tweener** class has parameters, the parameters appear
below the selected item.

You can start and stop the animation using the *gear* icon in the bottom center
of the view, as well as change the length of time it takes to complete a single
animation cycle using the ***Time*** scrubber that appears next to it.

You can also change the position of the two animated boxes by dragging them,
although the animation needs to be stopped in order to do this. Once you have
moved the boxes to new positions, restarting the animation will cause the boxes
to animate back and forth between their new positions.

Note that there are three **Tweener** objects in the column on the left because
tweeners are *composable*, which allows their behaviors to be combined to create
new tweeners. Although any number of tweeners can be composed together, the demo
is limited to three, which are composed as follows:

    tweener = Tweener1( Tweener2( Tweener3 ) )

Be sure to experiment with combining different tweeners in different orders to
see what types of new animation effects you can come up with.

This demo includes the standard Facets *animation*, **Path** and **Tweener**
classes. However it also allows you to create and try out custom **Path** and
**Tweener** classes using the ***Custom Path*** and ***Custom Tweener*** tabs.
Each tab contains a text editor that is initialized with a basic template for
defining a **Path** or **Tweener** subclass. You can modify the code then click
the *gear* icon in the bottom right corner of the view to load the code into the
demo.

If there are no syntax errors, you can try out your custom **Path** or
**Tweener** by selecting ***Custom*** from the appropriate drop-down list in the
***Animation Tab***. The animation will be automatically updated to use your
custom class.

For more advanced experimentation, you can try adding one or more parameters to
your custom class to allow varying its behavior. Simply define the required
*facets* in the code template and reference them in your code. Some additional
things to keep in mind when doing this:

- Add ***event = 'modified'*** metadata to each facet you add to your class.
  This will allow the demo to automatically update the *path* or *tweener*
  graphs whenever you modify the parameter.
- Be sure to update the ***view*** for your class to include the new facets you
  added. Doing so will allow you to edit your custom class in the main
  ***Animation Lab*** tab. If the new facet is an integer range, you can simply
  add an ***IRange*** item to the view. If it is a float range, use an
  ***FRange*** item instead. For example:

  ```
  view = View( IRange( 'cycles' ), FRange( 'amplitude' ) )
  ```

Creating new classes is actually fairly simple, since there is only a single
***at*** method that needs to be overridden for each **Path** or **Tweener**
class. If interested, please look at the *facets.animation.py* package or some
of the other demos in this section for more information and examples on how to
create your own custom **Path** and **Tweener** classes.

Also, don't forget that the individual tabs can be dragged into new arragments
to allow you to see more than one view at a time if desired.
"""

#-- Imports --------------------------------------------------------------------

from numpy \
    import arange

from facets.api                                                                \
    import HasFacets, Tuple, Int, List, ATheme, Instance, Bool, Enum, Any,     \
           Range, Image, View, HGroup, VGroup, VFold, Tabbed, Item, UItem,     \
           InstanceEditor, ScrubberEditor, ThemedCheckboxEditor, on_facet_set, \
           spring

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.pen \
    import Pen

from facets.animation.api                                                      \
    import ConcurrentAnimation, Tweener, LinearTweener, EaseInTweener,         \
           EaseOutTweener, EaseOutEaseInTweener, EasyTweener, CycleTweener,    \
           RampTweener, RetrogradeTweener, BounceTweener, Path,                \
           Linear2DIntPath, Manhattan2DIntPath, Spiral2DIntPath,               \
           Ricochet2DIntPath, Snake2DIntPath, Overshoot2DIntPath

from facets.extra.helper.live_code \
    import LiveCode

#-- Path Subclass Template -----------------------------------------------------

PathTemplate = """
from facets.api import View
from facets.animation.api import Linear2DIntPath, IRange, FRange
from math import *

class CustomPath ( Linear2DIntPath ):

    def at ( self, v0, v1, t ):
        x0, y0 = v0
        x1, y1 = v1
        return ( int( round( x0 + ((x1 - x0) * t) ) ),
                 int( round( y0 + ((y1 - y0) * t) ) ) )

    view = View()
"""[1:-1]

#-- Path Live Code object for testing new custom paths -------------------------

PathLiveCode = LiveCode(
    code   = PathTemplate,
    target = 'CustomPath',
    klass  = Linear2DIntPath
)

#-- CustomPath class -----------------------------------------------------------

class CustomPath ( Linear2DIntPath ):

    live_code = Any( PathLiveCode )

    view = View(
        UItem( 'object.live_code.object',
               style  = 'custom',
               editor = InstanceEditor()
        )
    )

    def at ( self, v0, v1, t ):
        path = self.live_code.object
        if path is not None:
            return path.at( v0, v1, t )

        return super( CustomPath, self ).at( v0, v1, t )

    @on_facet_set( 'live_code.object.modified' )
    def live_code_modified ( self ):
        self.modified = True

#-- Tweener Subclass Template --------------------------------------------------

TweenerTemplate = """
from facets.api import View
from facets.animation.api import Tweener, IRange, FRange
from math import *

class CustomTweener ( Tweener ):

    def at ( self, t ):
        return t

    view = View()
"""[1:-1]

#-- Tweener Live Code object for testing new custom tweeners -------------------

TweenerLiveCode = LiveCode(
    code   = TweenerTemplate,
    target = 'CustomTweener',
    klass  = Tweener
)

#-- CustomTweener class --------------------------------------------------------

class CustomTweener ( Tweener ):

    live_code = Any( TweenerLiveCode )

    view = View(
        UItem( 'object.live_code.object',
               style  = 'custom',
               editor = InstanceEditor()
        )
    )

    def at ( self, t ):
        tweener = self.live_code.object
        if tweener is not None:
            return tweener.at( t )

        return super( CustomTweener, self ).at( t )

    @on_facet_set( 'live_code.object.modified' )
    def live_code_modified ( self ):
        self.modified = True

#-- Constants ------------------------------------------------------------------

ItemSize = 60  # The size of a LabItem

PathType = Enum(
    'Linear', 'Manhattan', 'Spiral', 'Ricochet', 'Snake', 'Overshoot', 'Custom'
)

PathMap = {  # Mapping from path types to Path classes
    'Linear':    Linear2DIntPath,
    'Manhattan': Manhattan2DIntPath,
    'Spiral':    Spiral2DIntPath,
    'Ricochet':  Ricochet2DIntPath,
    'Snake':     Snake2DIntPath,
    'Overshoot': Overshoot2DIntPath,
    'Custom':    CustomPath
}

TweenerType = Enum(
    'Linear', 'Ease In', 'Ease Out', 'Ease Out Ease In', 'Easy', 'Cycle',
    'Ramp', 'Retrograde', 'Bounce', 'Custom'
)

TweenerMap = {  # Mapping from tweener types to Tweener classes
    'Linear':           LinearTweener,
    'Ease In':          EaseInTweener,
    'Ease Out':         EaseOutTweener,
    'Ease Out Ease In': EaseOutEaseInTweener,
    'Easy':             EasyTweener,
    'Cycle':            CycleTweener,
    'Ramp':             RampTweener,
    'Retrograde':       RetrogradeTweener,
    'Bounce':           BounceTweener,
    'Custom':           CustomTweener
}

#-- Helper functions -----------------------------------------------------------

def sitem ( name, increment = 1 ):
    return Item( name,
          width      = -40,
          editor     = ScrubberEditor( increment = increment ),
          item_theme = '#themes:ScrubberEditor'
    )

def pplot ( name, label ):
    return VGroup(
         UItem( name, editor = PathPlotEditor() ),
         label = label
    )

def tplot ( name, label ):
    return VGroup(
         UItem( name, editor = TweenerPlotEditor() ),
         label = label
    )

def ptitem ( name, label ):
    return VGroup(
        UItem( name + '_type', width = -120 ),
        UItem( name, style = 'custom' ),
        show_labels = False,
        label       = label,
        group_theme = '@xform:btd?L30'
    )

#-- LabItem class --------------------------------------------------------------

class LabItem ( HasFacets ):

    position = Tuple( Int, Int, event = 'refresh' )
    saved    = Tuple( Int, Int )
    theme    = ATheme( '@std:BH5?H37l16S42|h60H64' )

    def paint ( self, g ):
        px, py = self.position
        self.theme.fill( g, px, py, ItemSize, ItemSize )

    def is_in ( self, x, y ):
        px, py = self.position

        return ((px <= x < (px + ItemSize)) and (py <= y < (py + ItemSize)))

#-- LabItems class -------------------------------------------------------------

class LabItems ( HasFacets ):

    items = List

    def _items_default ( self ):
        return [
            LabItem( position = (  10,  10 ) ),
            LabItem( position = ( 250, 250 ) )
        ]

#-- _AnimationLabEditor class --------------------------------------------------

class _AnimationLabEditor ( ControlEditor ):

    drag_item = Instance( LabItem )

    def paint_content ( self, g ):
        for item in self.value.items:
            item.paint( g )

    def normal_left_down ( self, x, y ):
        for item in self.value.items:
            if item.is_in( x, y ):
                self.drag_item = item
                self._x, self._y, self.state = x, y, 'dragging'
                break

    def dragging_motion ( self, x, y ):
        dx, dy = x - self._x, y - self._y
        if (dx != 0) or (dy != 0):
            self._x, self._y = x, y
            px, py = self.drag_item.position
            self.drag_item.position = ( px + dx, py + dy )

    def dragging_left_up ( self ):
        self.state = 'normal'

    @on_facet_set( 'value:items:refresh' )
    def _needs_update ( self ):
        self.refresh()

#-- AnimationLabEditor class ---------------------------------------------------

class AnimationLabEditor ( CustomControlEditor ):

    klass = _AnimationLabEditor
    theme = '@xform:b?L10'

#-- _TweenerPlotEditor class ---------------------------------------------------

class _TweenerPlotEditor ( ControlEditor ):

    def paint_content ( self, g ):
        g.anti_alias     = True
        bx, by, bdx, bdy = self.content_bounds
        bx  += 2
        by  += 2
        bdx -= 4
        bdy -= 4

        g.pen = 0x505050
        g.draw_rectangle( bx - 1, by - 1, bdx + 2, bdy + 2 )

        points = self.value
        n      = len( points )
        iy     = by + bdy
        if n >= 2:
            g.pen  = Pen( color = 0xE00000, width = 1 )
            x0, y0 = points[0]
            ix0    = int( round( bx  + (x0 * bdx) ) )
            iy0    = iy - int( round( y0 * bdy ) )
            for i in xrange( 1, n ):
                x1, y1 = points[ i ]
                ix1    = int( round( bx  + (x1 * bdx) ) )
                iy1    = iy - int( round( y1 * bdy ) )
                g.draw_line( ix0, iy0, ix1, iy1 )
                ix0, iy0 = ix1, iy1

#-- TweenerPlotEditor class ---------------------------------------------------

class TweenerPlotEditor ( CustomControlEditor ):

    klass = _TweenerPlotEditor

#-- _PathPlotEditor class ---------------------------------------------------

class _PathPlotEditor ( ControlEditor ):

    dot = Image( '@icons:red_ball' )

    def paint_content ( self, g ):
        g.anti_alias     = True
        bx, by, bdx, bdy = self.content_bounds

        g.pen = 0x505050
        g.draw_rectangle( bx + 1, by + 1, bdx - 2, bdy - 2 )

        bx  += 8
        by  += 8
        bdx -= 16
        bdy -= 16
        if (bdx <= 1) or (bdy <= 0):
            return

        points = self.value
        min_x  = min_y =  1000000
        max_x  = max_y = -1000000
        for x, y in points:
            min_x, min_y = min( min_x, x ), min( min_y, y )
            max_x, max_y = max( max_x, x ), max( max_y, y )

        ddx, ddy = max( 1, max_x - min_x ), max( 1, max_y - min_y )
        scale    = min( float( bdx ) / ddx, float( bdy ) / ddy )
        sdx, sdy = int( round( scale * ddx ) ), int( round( scale * ddy ) )
        ix       = bx + ((bdx - sdx) / 2)
        iy       = by + ((bdy - sdy) / 2)

        dot = self.dot.bitmap
        for x, y in points:
            xc = ix + int( round( scale * (x - min_x) ) )
            yc = iy + int( round( scale * (y - min_y) ) )
            g.draw_bitmap( dot, xc - 8, yc - 8 )

#-- PathPlotEditor class ---------------------------------------------------

class PathPlotEditor ( CustomControlEditor ):

    klass = _PathPlotEditor

#-- AnimationLab class ---------------------------------------------------------

class AnimationLab ( HasFacets ):

    items          = Instance( LabItems, () )
    path_type      = PathType
    path           = Instance( Path, Linear2DIntPath, () )
    tweener1_type  = TweenerType
    tweener1       = Instance( Tweener )
    tweener2_type  = TweenerType
    tweener2       = Instance( Tweener )
    tweener3_type  = TweenerType
    tweener3       = Instance( Tweener )
    tweener1_data  = List
    tweener2_data  = List
    tweener3_data  = List
    tweener_data   = List
    path_raw_data  = List
    path_data      = List
    custom_path    = Instance( LiveCode )
    custom_tweener = Instance( LiveCode )
    time           = Range( 0.1, 10.0, 1.0 )
    animation      = Instance( ConcurrentAnimation )
    animate        = Bool( False )

    def default_facets_view ( self ):
        return View(
            Tabbed(
                HGroup(
                    VGroup(
                        ptitem( 'path',     'Path' ),
                        ptitem( 'tweener1', 'Tweener 1' ),
                        ptitem( 'tweener2', 'Tweener 2' ),
                        ptitem( 'tweener3', 'Tweener 3' ),
                    ),
                    VGroup(
                        UItem( 'items', editor = AnimationLabEditor() ),
                        HGroup(
                            spring,
                            UItem( 'animate',
                                   editor = ThemedCheckboxEditor(
                                       image = '@icons2:GearExecute' )
                            ),
                            sitem( 'time', 0.1 ),
                            spring,
                            group_theme = '@xform:b?L20'
                        )
                    ),
                    dock  = 'tab',
                    label = 'Animation Lab'
                ),
                UItem( 'custom_path',
                       style = 'custom',
                       dock  = 'tab',
                       label = 'Custom Path'
                ),
                UItem( 'custom_tweener',
                       style = 'custom',
                       dock  = 'tab',
                       label = 'Custom Tweener'
                ),
                VFold(
                    pplot( 'path_raw_data', 'Path' ),
                    pplot( 'path_data',     'Tweened Path' ),
                    dock  = 'tab',
                    label = 'Path Graphs'
                ),
                VFold(
                    tplot( 'tweener1_data', 'Tweener 1' ),
                    tplot( 'tweener2_data', 'Tweener 2' ),
                    tplot( 'tweener3_data', 'Tweener 3' ),
                    tplot( 'tweener_data',  'Tweener Composite' ),
                    dock  = 'tab',
                    label = 'Tweener Graphs'
                )
            ),
            width  = 0.8,
            height = 0.8
        )

    def facets_init ( self ):
        self._tweener1_type_set()
        self._tweener2_type_set()
        self._tweener3_type_set()
        self.animate = True

    def dispose ( self ):
        self.animate = False

    def _custom_path_default ( self ):
        return PathLiveCode

    def _custom_tweener_default ( self ):
        return TweenerLiveCode

    @on_facet_set( 'animation:stopped' )
    def _restart_animation ( self ):
        li1, li2       = self.items.items[0], self.items.items[1]
        li1.position   = li1.saved
        li2.position   = li2.saved
        self.animation = None
        if self.animate:
            self._create_animation()

    @on_facet_set( 'time, path, tweener1, tweener2, tweener3' )
    def _animation_modified ( self ):
        if self.animate and (self.animation is not None):
            self.animation.stop = True

    @on_facet_set( 'path.modified, tweener1.modified, tweener2.modified, tweener3.modified' )
    def _tweeners_modified ( self ):
        self.tweener1_data = self._tweener_data_for( self.tweener1 )
        self.tweener2_data = self._tweener_data_for( self.tweener2 )
        self.tweener3_data = self._tweener_data_for( self.tweener3 )
        self.tweener_data  = self._tweener_data_for()
        self.path_raw_data, self.path_data = self._path_data_for()

    def _path_type_set ( self ):
        self.path = PathMap[ self.path_type ]()

    def _tweener1_type_set ( self ):
        self.tweener1 = TweenerMap[ self.tweener1_type ]()

    def _tweener2_type_set ( self ):
        self.tweener2 = TweenerMap[ self.tweener2_type ]()

    def _tweener3_type_set ( self ):
        self.tweener3 = TweenerMap[ self.tweener3_type ]()

    def _animate_set ( self ):
        if self.animate:
            self._create_animation()
        else:
            self.animation.halt()

    def _create_animation ( self ):
        li1, li2              = self.items.items[0], self.items.items[1]
        li1.saved             = li1.position
        li2.saved             = li2.position
        self.tweener2.compose = self.tweener3
        self.tweener1.compose = self.tweener2
        self.animation        = ConcurrentAnimation( items = [
            self._animation_item_for( li1, li2 ),
            self._animation_item_for( li2, li1 ),
        ] ).run()

    def _animation_item_for ( self, item1, item2 ):
        return item1.animate_facet(
            'position', self.time, item2.position, item1.position,
            repeat  = 1,
            path    = self.path,
            tweener = self.tweener1,
            start   = False
        )

    def _tweener_data_for ( self, tweener = None ):
        if tweener is None:
            tweener = self.tweener1
        else:
            tweener = tweener.at

        return [ ( t, tweener( t ) ) for t in arange( 0.0, 1.001, 0.01 ) ]

    def _path_data_for ( self ):
        pat, tweener = self.path.at, self.tweener1
        items        = self.items.items
        v0, v1       = items[0].position, items[1].position
        if self.animate:
            v0, v1 = items[0].saved, items[1].saved

        return (
            [ pat( v0, v1, t )            for t in arange( 0.0, 1.001, 0.04 ) ],
            [ pat( v0, v1, tweener( t ) ) for t in arange( 0.0, 1.001, 0.04 ) ]
        )

#-- Create the demo ------------------------------------------------------------

demo = AnimationLab

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
