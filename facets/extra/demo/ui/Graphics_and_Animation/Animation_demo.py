"""
# Animation Demo #

A demonstration illustrating the use of some of the Facets UI animation classes.

This demonstration contains two distinct animations:

- One which animates the change of a specified object facet from one value to
  another over some period of time. In this case, the animated facet value is
  the 'counter' facet of the main **Demo** object.
- Another which animates the position and size of a Control object over a
  period of time.

In the demo, the animated control objects are a series of **Traveller** class
instances. Each Traveller object displays the current value of the main Demo
'counter' facet, so you can watch each Traveller count in perfect sync with the
Demo object.

The demo provides a number of values you can use to control the animation:

- **Target**: The value the 'counter' facet should count up to.
- **Travellers**: The number of Traveller objects that should be created.
- **Time**: The amount of time (in seconds) that each section of the
  animation should last.
- **Repeat**: The number of times the animation cycle should repeat before
  stopping.
- **Reverse**: If checked, the first animation cycle goes from the start
  value to the end value. The next cycle goes from the end value back to the
  start value, and so on. If not checked, each cycle simply runs from the start
  value to the end value.

If you want to watch some Traveller objects fly around your screen, first set
the number of Traveller objects you want, then click the *Create* button. The
demo creates the specified number of objects and arranges them in a vertical
column on your screen. Their initial location and size defines their *start*
bounds. Feel free to move them around and resize them to set start bounds of
your own choosing.

To start the animation going, click the *Start* button. The Demo 'counter' will
start counting up to the *Target* value, and the Traveller objects will start
moving to a point near the top-left corner of your display while also changing
their size.

If *Reverse* is checked, and *Repeat* is greater than one, the counter and
Traveller objects will animate back to their starting value and positions. The
animation will continue until the specified number of Repeat cycles have been
completed. If you grow bored, you can click the *Stop* button to immediately
stop the animation in progress.

The *Counter* value displayed at the top of the main view (and in each
Traveller object) shows the current value of the Demo 'counter' facet. The
*Elapsed* value displays the total amount of time that has elapsed in the
current animation.

The animation system provided by Facets is based on several class categories:

- **animation**: These are classes that implement the **IAnimatable** interface
  and perform the actual animation.
- **path**: These are classes that define a *path* (i.e. set of values) going
  from a *start* value to an *end* value over a specified time. These are not
  required by the IAnimatable interface, but are used by many of the concrete
  animation classes provided with the package. They are usually expressed as
  parametric functions of time ***t*** for ***t*** in the interval from 0.0
  (start time) to 1.0 (end time).
- **tweener**: These are classes that define a mapping from ***t*** to ***t'***
  for ***t*** and ***t'*** in the interval [0.0,1.0]. In essence, they provide a
  mechanism for controlling the passage of time within the animation.

The distinction between *path* and *tweener* might seem confusing at first.
Basically, a path defines a mapping from time to values that can be assigned to
an animatable value, whereas a tweener is a mapping from time back to time that
is used to control how the animation travels along the path during the animation
period. In essence:

    animation_value(t) = path(tweener(t)) for t in [0.0,1.0]

For example, you might define a **CirclePath** class that traces out values
along the perimeter of a circle such that:

    x(t) = xc + r*cos(2*pi/t)
    y(t) = yc + r*sin(2*pi/t)

For a given center point (xc,rc) and radius r, this would always trace out the
same path around the specified circle.

However, when combined with the appropriate tweener, the behavior can be
modified in a number of ways. For example:

    t'(t) = fmod(t+c,1.0)

would define a tweener that allows the start/end point of the CirclePath to be
changed depending upon the value of the constant ***c***. Another tweener
definition might allow the CirclePath to go half way around the circle, then
retrace its path back to the start point.

Of course, a path and tweener could be collapsed into a single composite
function, but in practice keeping them separate allows us to create a number of
useful predefined, independent and reusable path and tweener classes.

The core *facets.animation* package defines the following useful animation
classes:

- **Animation**: Base class for creating your own animation classes.
- **FacetAnimation**: For animating an arbitrary object facet value.
- **ConcurrentAnimation**: For managing a series of concurrently executing
  animations.
- **SequentialAnimation**: For managing a series of sequentially executing
  animations.

For paths, the following classes are provided:

- **Path**: Defines a base class for creating your own path classes.
- **LinearPath**: Defines a linear path between the *start* and
  *end* values.
- **LinearIntPath**: Defines a linear path with integer values between the
  *start* and *end* values.

Finally, the provided tweener classes are:

- **Tweener**: Defines a base class for creating your own tweener classes.
- **LinearTweener**: Defines a linear tween between the start and end time.
- **NoEasing**: A predefined instance of LinearTweener.
- **EaseInTweener**: Defines a tweener that eases (slows) into the end
  value.
- **EaseIn**: A predefined instance of EaseInTweener.
- **EaseOutTweener**: Defines a tweener that eases out of the start value.
- **EaseOut**: A predefined instance of EaseOutTweener.
- **EaseOutEaseInTweener**: Defines a tweener that eases out of the start
  value and eases into the end value.
- **EaseOutEaseIn**: A prefined instance of EaseOutEaseInTweener.

Note that *easing* refers to a traditional animation effect that tends to make
various types of animation look more *natural* than a strictly linear animation
would. For example, the demo uses EaseOutEaseIn with the Traveller objects to
make their movements and size changes appear smoother.
"""

#-- Imports --------------------------------------------------------------------

from time \
    import time

from facets.api \
    import HasFacets, UIView, Int, Bool, Range, Any, Button, Property, ATheme, \
           View, HGroup, VGroup, Item, ScrubberEditor, spring, \
           property_depends_on

from facets.animation.api \
    import ConcurrentAnimation, EaseOutEaseIn

#-- SEItem (ScrubberEditorItem) Class ------------------------------------------

class SEItem ( Item ):
    editor     = ScrubberEditor()
    item_theme = ATheme( '#themes:ScrubberEditor' )

#-- Traveller Class ------------------------------------------------------------

class Traveller ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    owner = Any

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'object.owner.counter',
                  style      = 'readonly',
                  width      = 90,
                  item_theme = '@std:LB?l10'
             ),
             group_theme = '@std:XG0'
        ),
        title = 'Traveller'
    )

#-- Demo Class -----------------------------------------------------------------

class AnimationDemo ( UIView ):

    #-- Facet Definitions ------------------------------------------------------

    counter    = Int
    target     = Range( 10, 10000, 100 )
    travellers = Range( 1, 20, 6 )
    time       = Range( 0.0, 20.0, 1.0 )
    repeat     = Range( 0, 50, 6 )
    reverse    = Bool( True )
    start      = Button( 'Start' )
    stop       = Button( 'Stop' )
    create     = Button( 'Create' )
    begin      = Property
    elapsed    = Property

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'counter', style = 'readonly' ),
            Item( 'elapsed', style = 'readonly' ),
            group_theme = '@xform:b6?L35'
        ),
        VGroup(
            SEItem( 'target' ),
            SEItem( 'travellers' ),
            SEItem( 'time' ),
            SEItem( 'repeat' ),
            Item(   'reverse' ),
            group_theme = '@xform:b6?L35'
        ),
        HGroup(
            spring,
            Item( 'start'  ),
            Item( 'stop'   ),
            Item( 'create' ),
            show_labels = False,
            group_theme = '@xform:b6?L35'
        )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'start' )
    def _get_begin ( self ):
        return time()

    @property_depends_on( 'begin, counter' )
    def _get_elapsed ( self ):
        return ('%.2f' % (time() - self.begin))

    #-- Facet Event Handlers ---------------------------------------------------

    def _start_set ( self ):
        self._stop_set()
        self.animate_facet(
            'counter', self.time, self.target, 0,
            repeat  = self.repeat,
            reverse = self.reverse
        )
        if self._uis is not None:
            controls = [ ui.control
                         for ui in self._uis if ui.control is not None ]
            if len( controls ) > 0:
                self._animation = ConcurrentAnimation(
                    repeat  = 0,
                    reverse = False,
                    items   = [ control.animate_facet(
                        'bounds', self.time, ( 20, 40, 400, 100 ),
                        repeat  = self.repeat,
                        reverse = self.reverse,
                        tweener = EaseOutEaseIn,
                        start   = False
                    ) for control in controls ]
                ).run()

    def _stop_set ( self ):
        self.halt_animated_facets()
        if self._animation is not None:
            self._animation.halt()

    def _create_set ( self ):
        if self._animation is not None:
            self._animation.halt()

        self._clean_up()

        self._travellers = [ Traveller( owner = self )
                             for i in range( self.travellers ) ]

        self._uis = [ traveller.edit_facets( parent = self.ui_info.ui.control )
                      for traveller in self._travellers ]
        for i, ui in enumerate( self._uis ):
            ui.control.position = ( 600, (90 * i) + 30 )

    def _ui_info_set ( self, ui_info ):
        if ui_info is None:
            self._clean_up()

    #-- Private Methods --------------------------------------------------------

    def _clean_up ( self ):
        if self._uis is not None:
            for ui in self._uis:
                ui.dispose()

        self._uis = None

#-- Create the demo ------------------------------------------------------------

demo = AnimationDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
