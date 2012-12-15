"""
I must admit that I wrote this demo because I thought it would be fun to do so,
and it was. And I am pretty happy with the result. One other fun fact that I
hope will inspire you is that the entire program, including this documentation,
was written in under 24 hours, spread across two Starbucks visits and a few
hours in the evening spent half-coding, half-channel hopping TV.

The program is a simple lab for experimenting with animated <i>parametric
equations</i>. Parametric equations are formulas that allow you to express
one set of values in term of another set of values (the parameters).

In this case, the values we wish to express are (x,y) points on a 2D plane
described in terms of a single parameter, <i>t</i>.

The program works as follows:
 - There are two formulas: <i>x(t)</i> and <i>y(t)</i> displayed in the top half
   of the view.
 - The formulas appear as text fields containing numeric expressions written in
   Python (e.g. <b><i>a*sin(b*2*pi*t)</i></b>).
 - You are free to change the formulas as you like. The only restrictions are
   that the formulas can only reference <i>t</i> (the <i>parameter</i>), and the
   five constants: <i>a</i>, <i>b</i>, <i>c</i>, <i>d</i> and <i>e</i>.
 - When writing a formula, you have full access to the entire contents of the
   <b><i>numpy</i></b> module, which provides many common numeric functions
   (e.g. <i>sin</i> and <i>cos</i>) and constants (e.g. <i>pi</i>).
 - The values for the five constants, <i>a</i>, <i>b</i>, <i>c</i>, <i>d</i> and
   <i>e</i>, can be entered using the sliders located above the forumula.

That's most of what you need to know about creating formulas. Next up is what
the program does with the formulas you have entered.

The program creates a set of <i>(x,y)</i> points by evaluating both formulas for
a range of values of the parameter <i>t</i>. The range is determined by the
<i>range slider</i> labeled <i>t</i>. The number of points to create is
specified by the value of the field labeled <i>Steps</i>.

The program then plots the set of points calculated using the <i>x(t)</i> and
<i>y(t)</i> formulas over the range of values for <i>t</i>. One plot displays
individual points, while the other draws lines connecting consecutive points.

The fun starts when the <i>animation</i> feature is turned on (or off) by
clicking the small play/stop button located halfway down the right side of the
view. When the program starts, the animation is already running in order to
give you an immediate sense of what the program does.

The animation is controlled by each of the ten constants: <i>a</i>, <i>b</i>,
<i>c</i>, <i>d</i> and <i>e</i> for the <i>x(t)</i> and <i>y(t)</i> formulas.
As you'll notice, each constant is not a single value, but a range of values.
Initially, each constant is locked, allowing you to easily slide the value up
or down. By clicking the padlock icon located to the right of a slider, you
can unlock the range of the constant. Once unlocked, each end of the constant's
range can be individually adjusted by either dragging or mouse wheel scrolling
while the pointer is over one of the slider ends. The entire range can be
shifted by dragging or mouse wheel scrolling the middle region of the slider.
Clicking the padlock icon again will lock the range, meaning that you can
drag or mouse wheel scroll over any part of the slider to adjust the entire
range, but you can cannot adjust the endpoints of the range separately.

The animation system looks for any constants which have different end point
values and animates the value of the constant over the specified range. Once the
animation reaches the end of the range it reverses and goes back to the start
of the range, and so on until the animation is stopped. The amount of time it
takes to go from one end of the range to the other is specified using the
<i>time scrubber</i> located to the right of the constant value slider.

At every <i>frame</i> of the animation, each constant with an animated range is
evaluated. Then each of the <i>x(t)</i> and <i>y(t)</i> formulas are evaluated
for each value in the <i>t</i> range using the current frame's constant values.
The resulting set of points are then plotted as described previously. The net
effect is a smooth animation of the formulas using the animated constant values.

Some additional things to note are:
 - You can change the formulas while an animation is running. You may notice the
   text entry field turning red while you type. This indicates that the formula
   currently has a syntax error. Just correct the error to continue. At other
   times the animation may appear to stop while the text entry field appears
   normal. This indicates that the formula is synactically valid, but references
   undefined values. Find the invalid value and correct it, and the animation
   will continue with the new formula in effect.
 - If you change a constant's <i>time</i> value while an animation is running,
   the program will wait for a brief interval, then restart the animation using
   the new time value.
 - You can change the value of any non-animated constant while an animation is
   running and see the effect immediately in the animation.
 - You can change the <i>t</i> parameter range or <i>Steps</i> value while an
   animation is running and see the effect immediately.
 - The animated plots at the bottom of the view use a <i>dynamic bounds</i>
   mechanism that automatically keep all plotted points and lines in view. You
   can reset the bounds at any time simply by clicking anywhere in the plot.
   This can be handy if you make some changes to the formulas or constants that
   make the plotted points and lines occupy a much smaller region than they did
   previously.
 - You can enter specific values into a slider or scrubber field by clicking on
   the field and then typing in the numeric value you want. For a range slider,
   separate the numeric values with a comma. Press <i>Enter</i> when done.
 - You can increase or decrease the mouse wheel scrolling sensitivity for a
   slider or scrubber by pressing the <i>Shift</i> key (to increase the rate) or
   <i>Control</i> key (to decrease the rate) while scrolling the mouse wheel.
 - You have to stop the animation to change an animated constant's current
   range. Basically, the animation system <i>owns</i> the constant's value while
   the animation is running.
 - Try setting a small value for <i>Steps</i> (e.g. <i>10</i>) for an
   entertaining change of pace.

Overall, I think you'll find that this little program is a real treasure trove
of useful techniques, and I hope that you'll have as much fun running it and
exploring the code as I did writing it...
"""

#-- Imports --------------------------------------------------------------------

from numpy \
    import arange, amin, amax

from facets.api                                                            \
    import HasFacets, UIView, Tuple, Expression, Array, List, Bool, Range, \
           Str, Float, Any, Instance, ATheme, Image, View, HGroup, VGroup, \
           HSplit, Item, UItem, RangeSliderEditor, ScrubberEditor,         \
           ThemedCheckboxEditor, TextEditor, SyncValue, on_facet_set

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.animation.api \
    import ConcurrentAnimation

from facets.ui.pen \
    import Pen

from facets.ui.pyface.timer.api \
    import do_after

#-- Constants ------------------------------------------------------------------

Coefficients = 'abcde'

#-- SItem class ----------------------------------------------------------------

class SItem ( Item ):
    editor     = ScrubberEditor( increment = 0.1 )
    width      = -40
    item_theme = ATheme( '#themes:ScrubberEditor' )

#-- Data class -----------------------------------------------------------------

class Data ( HasFacets ):

    x = Array
    y = Array

#-- Equation class -------------------------------------------------------------

Coefficient = Tuple(
    0.0, 0.0,
    event  = 'refresh',
    editor = RangeSliderEditor(
        low        = -10.0,
        high       = 10.0,
        increment  = 0.01,
        format_str = '%.2f',
        body_style = 25
    )
)

TimeRange = Range( 1.0, 10.0, 2.0, event = 'restart' )

class Equation ( HasFacets ):

    label    = Str
    equation = Expression( event = 'refresh' )

    a        = Coefficient( ( 1.0, 1.0 ) )
    b        = Coefficient( ( 1.0, 1.0 ) )
    c        = Coefficient
    d        = Coefficient
    e        = Coefficient

    a_locked = Bool( True )
    b_locked = Bool( True )
    c_locked = Bool( True )
    d_locked = Bool( True )
    e_locked = Bool( True )

    a_time   = TimeRange
    b_time   = TimeRange
    c_time   = TimeRange
    d_time   = TimeRange
    e_time   = TimeRange

    def default_facets_view ( self ):
        return View(
            VGroup(
                *self._coefficient_items(),
                group_theme = '@xform:btd?L30',
                label       = self.label
            ),
            VGroup(
                Item( 'equation', editor = TextEditor( font = '14' ) ),
                show_labels = False,
                group_theme = '@xform:b?L23'
            )
        )

    def _coefficient_items ( self ):
        return [ HGroup(
            Item( name,
                  label   = name,
                  springy = True,
                  editor  = RangeSliderEditor(
                              low          = -10.0,
                              high         = 10.0,
                              increment    = 0.01,
                              format_str   = '%.1f',
                              body_style   = 25,
                              range_locked = SyncValue( self, name + '_locked' )
                           )
            ),
            UItem( name + '_locked',
                   editor = ThemedCheckboxEditor(
                       image       = '@icons2:Padlock?l18S11',
                       off_image   = '@icons2:Padlock?L16s',
                       on_tooltip  = 'Parameter range is locked',
                       off_tooltip = 'Parameter range is unlocked' )
            ),
            SItem( name + '_time',
                   show_label = False,
                   tooltip    = 'Animation cycle time'
            ) )
            for name in Coefficients ]

#-- _DataEditor class ----------------------------------------------------------

class _DataEditor ( ControlEditor ):

    x_min = Float(  1e300 )
    x_max = Float( -1e300 )
    y_min = Float(  1e300 )
    y_max = Float( -1e300 )

    def paint_content ( self, g ):
        data = self.value
        if len( data ) == 0:
            return

        g.anti_alias  = True
        for d in data:
            self.x_min = min( self.x_min, amin( d.x ) )
            self.x_max = max( self.x_max, amax( d.x ) )
            self.y_min = min( self.y_min, amin( d.y ) )
            self.y_max = max( self.y_max, amax( d.y ) )

        x_min, y_min = self.x_min, self.y_min
        ddx, ddy     = self.x_max - x_min, self.y_max - y_min
        cdx, cdy     = self.control.client_size
        cdx         -= 30
        cdy         -= 30
        scale        = 1.0
        if (ddx * ddy) != 0.0:
            scale = min( cdx / ddx, cdy / ddy )

        xl = 15 + ((cdx - int( round( ddx * scale ) )) / 2)
        yb = cdy + 15 - ((cdy - int( round( ddy * scale ) )) / 2)

        if self.factory.style == 'line':
            g.pen = Pen( color = 0x000000, width = 3 )
            for d in data:
                x, y = d.x, d.y
                x0   = xl + int( round( (x[0] - x_min) * scale ) )
                y0   = yb - int( round( (y[0] - y_min) * scale ) )
                for i in xrange( 1, len( x ) ):
                    x1 = xl + int( round( (x[ i ] - x_min) * scale ) )
                    y1 = yb - int( round( (y[ i ] - y_min) * scale ) )
                    g.draw_line( x0, y0, x1, y1 )
                    x0, y0 = x1, y1
        else:
            point  = self.factory.point
            dx, dy = point.width / 2, point.height / 2
            point  = point.bitmap
            for d in data:
                x, y = d.x, d.y
                for i in xrange( len( x ) ):
                    x0 = xl + int( round( (x[ i ] - x_min) * scale ) ) - dx
                    y0 = yb - int( round( (y[ i ] - y_min) * scale ) ) - dy
                    g.draw_bitmap( point, x0, y0 )

    def normal_left_down ( self ):
        self.x_min = self.y_min =  1e300
        self.x_max = self.y_max = -1e300

    def _control_set ( self, control ):
        if control is not None:
            control.min_size = ( 70, 70 )

#-- DataEditor -----------------------------------------------------------------

class DataEditor ( CustomControlEditor ):

    klass = _DataEditor
    theme = '@xform:b?L20'
    style = Str( 'line' )
    point = Image( '@icons:red_ball_l?l34s' )

#-- Demo class -----------------------------------------------------------------

class Equations ( UIView ):

    x          = Instance( Equation,
                           { 'label':    'x(t)',
                             'equation': 'a*sin(b*2*pi*t)+c*t',
                             'b':        ( 1.0, 2.4 ),
                             'b_time':   3.0,
                             'c':        ( 0.4, 1.4 ),
                             'c_time':   2.1 } )
    y          = Instance( Equation,
                           { 'label':    'y(t)',
                             'a':        ( 1.4, 2.0 ),
                             'a_time':   2.5,
                             'equation': 'a*cos(b*2*pi*t)' } )
    t          = Coefficient( ( -0.4, 1.6 ) )
    steps      = Range( 2, 500, 350 )
    animate    = Bool( True )
    animation  = Instance( ConcurrentAnimation )
    data       = List( Data )
    numpy      = Any

    def default_facets_view ( self ):
        return View(
            VGroup(
                HGroup(
                    UItem( 'x', style = 'custom' ),
                    UItem( 'y', style = 'custom' ),
                    group_theme = '#themes:toolbar_group'
                ),
                HGroup(
                    SItem( 'steps', editor = ScrubberEditor() ), '_',
                    Item(  't', label = 't', springy = True ), '_',
                    UItem( 'animate',
                           editor = ThemedCheckboxEditor(
                               image       = '@icons2:StopBox',
                               off_image   = '@icons2:PlayBox',
                               on_tooltip  = 'Click to stop the animation',
                               off_tooltip = 'Click to start the animation' )
                    ),
                    group_theme = '#themes:toolbar_group'
                ),
                HSplit(
                     VGroup(
                         UItem( 'data',
                                editor  = DataEditor( style = 'point' ),
                                tooltip = 'Click to reset bounds'
                         ),
                         label = 'Points',
                         dock  = 'tab'
                     ),
                     VGroup(
                         UItem( 'data',
                                editor  = DataEditor( style = 'line' ),
                                tooltip = 'Click to reset bounds'
                         ),
                         label = 'Lines',
                         dock  = 'tab'
                     )
                 )
            ),
            width  = 0.9,
            height = 0.9
        )

    def facets_init ( self ):
        self._animate_set()

    def _numpy_default ( self ):
        import numpy
        return dict( [ ( _, getattr( numpy, _ ) ) for _ in dir( numpy ) ] )

    def _ui_info_set ( self, ui_info ):
        if (ui_info is None) and (self.animation is not None):
            self.animation.halt()

    def _animate_set ( self ):
        if self.animate:
            self.animation = ConcurrentAnimation( items =
                self._animations_for( self.x ) + self._animations_for( self.y )
            ).run()
        else:
            self.animation.halt()
            for fa in self.animation.items:
                setattr( fa.object, fa.name, ( fa.begin[0], fa.end[0] ) )

            self.animation = None

    @on_facet_set( 'x:refresh, y:refresh, t, steps' )
    def _refresh_needed ( self ):
        self._generate_data()

    @on_facet_set( 'x:restart, y:restart' )
    def _restart_needed ( self ):
        if self.animate:
            do_after( 500, self._restart_animation )

    def _restart_animation ( self ):
        self.animate = False
        self.animate = True

    def _generate_data ( self ):
        t0, t1  = self.t
        dt      = (t1 - t0) / ( self.steps - 1)
        context = { 't': arange( t0, t1 + (dt / 2.0), dt ) }
        try:
            self.data = [ Data( x = self._eval( self.x, context ),
                                y = self._eval( self.y, context ) ) ]
        except:
            pass

    def _eval ( self, equation, context ):
        for name in Coefficients:
            context[ name ] = getattr( equation, name )[0]

        return eval( equation.equation_, self.numpy, context )

    def _animations_for ( self, equation ):
        animations = []
        for name in Coefficients:
            v0, v1 = getattr( equation, name )
            if v0 != v1:
                animations.append( equation.animate_facet(
                    name, getattr( equation, name + '_time' ),
                    ( v1, v1 ), ( v0, v0 ),
                    repeat = 0,
                    start  = False
                ) )

        return animations

#-- Create the demo ------------------------------------------------------------

demo = Equations

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
