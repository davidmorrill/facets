"""
# Twixter #

A fairly complex demo reminiscent of a cross between the old **Twix** arcade
game, a **Slinky** and a **Spirograph**.

The demo consists of three editable triangles:

- A start triangle.
- An end triangle.
- A center triangle.

When you mouse over the main part of the demo view, the editable triangles will
appear drawn in red, with a series of drag handles appearing at their vertex and
center points. You can drag the vertex point handles to move the end points of
any of the lines, or drag the center point to translate the entire triangle.

The demo works by drawing a series of intermediate triangles between the start
triangle and the end triangle, rotating the end points of the intermediate
triangles around the *current* point on the center triangle.

There are also a series of animation settings accessed by clicking the *gear*
icon near the bottom right corner of the view. This displays a pop-up view
containing all of the animation controls.

Please experiment with the various controls to get a better feel for how the
demo operates (that's half the fun).

The code implementing the demo illustrates several important Facets features and
techniques:

- Creating a custom control using the UI *abstraction layer* (**LinesEditor**).
- Creating a custom editor based an a custom control using the
  **CustomControlEditor** *editor factory*.
- Creating a custom **Handler** class to exercise more control over a **View**'s
  life cycle (**TwixterHandler**).
- Use of **Property**-based facets to simplify model design (**Tracker.*point***
  and **Line.*center***).
- Use of the *animate_facet* and *halt_animated_facets* methods to create and
  control animated behavior.
- Creating custom **Group** and **Item** classes by subclassing and overriding
  facet default values in order to simplify **View** creation (**BevelGroup**
  and **RangeItem**).
- Creating a custom facet definition to simplify and better document a design
  (**Point**).

The code is fairly long, but there are a lot of useful techniques to learn
through careful study. Have fun exploring the code and demo!
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt, sin, cos, pi, atan2

from facets.api                                                                \
    import HasFacets, HasPrivateFacets, Tuple, Int, Range, Str, Bool, Color,   \
           List, Instance, Property, Event, View, HGroup, VGroup, Item, UItem, \
           Handler, ScrubberEditor, RangeEditor, RangeSliderEditor,            \
           ThemedButtonEditor, spring, on_facet_set

from facets.ui.pen \
    import Pen

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Colors used for drawing a Tracker object:
TrackerInactivePen   = ( 255, 0, 0,  40 )
TrackerInactiveBrush = ( 255, 0, 0,  20 )
TrackerActivePen     = ( 255, 0, 0, 192 )
TrackerActiveBrush   = ( 255, 0, 0, 128 )

# The width of the Tracker circle edge:
TrackerWidth = 4

# The radius of a Tracker circle:
TrackerRadius = 10

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# A 2D point of the form (x,y):
Point = Tuple( Int, Int )

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def point ( x, y ):
    """ Returns a properly rounded integer (x,y) tuple for *x* and *y*.
    """
    return ( int( round( x ) ), int( round( y ) ) )

#-------------------------------------------------------------------------------
#  'RangeItem' class:
#-------------------------------------------------------------------------------

class RangeItem ( Item ):
    """ Defines a custom Item that uses a RangeEditor for its editor.
    """

    editor = RangeEditor( body_style = 25 )

#-------------------------------------------------------------------------------
#  'BevelGroup' class:
#-------------------------------------------------------------------------------

class BevelGroup ( VGroup ):
    """ Defines a custom VGroup that uses a beveled border theme.
    """

    group_theme = '#themes:toolbar_group'

#-------------------------------------------------------------------------------
#  'TwixterHandler' class:
#-------------------------------------------------------------------------------

class TwixterHandler ( Handler ):
    """ View handler for a Twixter object's main view. Ensures that any active
        animation is stopped when the view is closed.
    """

    def closed ( self, info, is_ok ):
        """ Handles a dialog-based user interface being closed by the user.
        """
        animation = info.object._animation
        if animation is not None:
            animation.stop = True

#-------------------------------------------------------------------------------
#  'Tracker' class:
#-------------------------------------------------------------------------------

class Tracker ( HasPrivateFacets ):
    """ Defines a tracker for allowing a specified 2D point to be selected and
        dragged.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The pen used to draw the tracker:
    pen = Instance( Pen, {
              'color': TrackerInactivePen,
              'width': TrackerWidth } )

    # The brush used to draw the tracker:
    brush = Color( TrackerInactiveBrush )

    # Is the tracker active?
    active = Bool( False )

    # The point being tracked:
    point = Property

    # The object containing the point being tracked:
    target = Instance( HasFacets )

    # The name of the the point within the object being tracked:
    name = Str

    #-- Property Implementations -----------------------------------------------

    def _get_point ( self ):
        return getattr( self.target, self.name )

    def _set_point ( self, point ):
        setattr( self.target, self.name, point )

    #-- Public Methods ---------------------------------------------------------

    def is_in ( self, x, y ):
        """ Returns True if (*x*,*y*) is inside of the Tracker, and False
            otherwise.
        """
        xc, yc = self.point
        dx, dy = x - xc, y - yc

        return (sqrt( (dx * dx) + (dy * dy) ) <= TrackerRadius)

    #-- Facet Event Handlers ---------------------------------------------------

    def _active_set ( self, active ):
        """ Handles the 'active' facet being changed.
        """
        if active:
            self.pen.color = TrackerActivePen
            self.brush     = TrackerActiveBrush
        else:
            self.pen.color = TrackerInactivePen
            self.brush     = TrackerInactiveBrush

#-------------------------------------------------------------------------------
#  'TrianglesEditor' class:
#-------------------------------------------------------------------------------

class TrianglesEditor ( ControlEditor ):
    """ Defines a control for displaying and editing triangle objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of triangles being drawn:
    value = List # ( Triangle )

    # Is editing mode active?
    editing = Bool( False )

    # The active tracker (if any):
    tracker = Instance( Tracker )

    # The current list of trackers:
    trackers = List( Tracker )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Draws the lines in the specified graphics *g*.
        """
        g.anti_alias = True
        editing      = self.editing
        for triangle in self.value:
            if editing or (not triangle.editable):
                g.pen  = Pen( color = triangle.color, width = triangle.width )
                x0, y0 = triangle.p0
                x1, y1 = triangle.p1
                x2, y2 = triangle.p2
                g.draw_line( x0, y0, x1, y1 )
                g.draw_line( x1, y1, x2, y2 )
                g.draw_line( x2, y2, x0, y0 )

        for tracker in self.trackers:
            g.pen   = tracker.pen
            g.brush = tracker.brush
            x, y    = tracker.point
            g.draw_circle( x, y, TrackerRadius )


    def normal_enter ( self, x, y ):
        """ Handles the user moving the mouse pointer into the control.
        """
        trackers = []
        for triangle in self.value:
            if triangle.editable:
                trackers.extend( [
                    Tracker( target = triangle, name = 'p0' ),
                    Tracker( target = triangle, name = 'p1' ),
                    Tracker( target = triangle, name = 'p2' ),
                    Tracker( target = triangle, name = 'center' )
                ] )

        self.trackers = trackers
        self._check_trackers( x, y )
        self.editing = True


    def normal_leave ( self ):
        """ Handles the user moving the mouse pointer out of the control.
        """
        del self.trackers[:]
        self.tracker = None
        self.editing = False


    def normal_motion ( self, x, y ):
        """ Handles the user moving the mouse pointer within the control.
        """
        self._check_trackers( x, y )


    def normal_left_down ( self, x, y ):
        """ Handles the user pressing the left mouse button in the control.
        """
        if self._check_trackers( x, y ) is not None:
            self._last = ( x, y )
            self.state = 'tracking'


    def tracking_left_up ( self ):
        """ Handles the user releasing the left mouse button while dragging a
            Tracker object.
        """
        del self._last
        self.state = 'normal'


    def tracking_motion ( self, x, y ):
        """ Handles the user moving the mouse pointer while dragging a Tracker
            object.
        """
        lx, ly             = self._last
        self._last         = ( x, y )
        px, py             = self.tracker.point
        self.tracker.point = ( px + x - lx, py + y - ly )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'value, editing, tracker' )
    def _update ( self ):
        """ Refreshes the display when the content changes in some way.
        """
        self.refresh()

    #-- Private Methods --------------------------------------------------------

    def _check_trackers ( self, x, y ):
        """ Checks to see if the specified (*x*,*y*) point is located within
            any tracker, and make it the active tracker if it is.
        """
        for tracker in self.trackers:
            if tracker.is_in( x, y ):
                break
        else:
            tracker = None

        current = self.tracker
        if tracker is not current:
            if current is not None:
                current.active = False

            if tracker is not None:
                tracker.active = True

            self.tracker = tracker

        return tracker

#-------------------------------------------------------------------------------
#  'Triangle' class:
#-------------------------------------------------------------------------------

class Triangle ( HasPrivateFacets ):
    """ Defines an editable 2D triangle.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The three points of the triangle:
    p0 = Point( event = 'update' )
    p1 = Point( event = 'update' )
    p2 = Point( event = 'update' )

    # The center point of the triangle:
    center = Property

    # The width of the triangle lines:
    width = Range( 1, 20, 2 )

    # The color of the triangle lines:
    color = Color( 0x000000 )

    # Is the triangle editable?
    editable = Bool( False )

    # The owner of the triangle:
    owner = Instance( HasFacets )

    #-- Property Implementations -----------------------------------------------

    def _get_center ( self ):
        x0, y0 = self.p0
        x1, y1 = self.p1
        x2, y2 = self.p2

        return ( (x0 + x1 + x2) / 3, (y0 + y1 + y2) / 3 )

    def _set_center ( self, point ):
        xc0, yc0 = self.center
        xc1, yc1 = point
        dx, dy   = xc1 - xc0, yc1 - yc0
        x0, y0   = self.p0
        x1, y1   = self.p1
        x2, y2   = self.p2
        self.p0  = ( x0 + dx, y0 + dy )
        self.p1  = ( x1 + dx, y1 + dy )
        self.p2  = ( x2 + dx, y2 + dy )

    #-- Facet Event Handlers ---------------------------------------------------

    def _update_set ( self ):
        """ Handles an 'update' event being fired.
        """
        if self.owner is not None:
            self.owner.update = self

#-------------------------------------------------------------------------------
#  'Twixter' class:
#-------------------------------------------------------------------------------

class Twixter ( HasPrivateFacets ):
    """ Defines a model for managing a collection of animatable triangle
        objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The starting triangle being spun:
    start = Instance( Triangle )

    # The end (i.e. target) triangle that the start triangle 'morphs' into:
    end = Instance( Triangle )

    # The triangle that the triangle points spin around:
    center = Instance( Triangle )

    # The number of triangles drawn from start to end:
    count = Range( 2, 1000, 400, event = 'update' )

    # Total amount of rotation that occurs between start and end around center:
    angle = Range( 0, 3600, 1080, event = 'update' )

    # The width of the triangle lines drawn:
    width_range = Tuple( ( 1, 3 ) )

    # The percentage of triangles to display:
    percent = Range( 1, 100, 20 )

    # The index of the first triangle to display:
    index = Range( 0.0, 1.0, 0.0 )

    # The length of time it takes to cycle through the 'index' range:
    index_time = Range( 1.0, 20.0, 6.0 )

    # Is an animation running?
    animate = Bool( True )

    # The range of 'count' values to animate between:
    count_range = Tuple( ( 100, 300 ) )

    # The length of time it takes to cycle through the 'count range':
    count_time = Range( 1.0, 20.0, 4.0 )

    # The range of 'angle' values to animate between:
    angle_range = Tuple( ( 360, 1800 ) )

    # The amount of time it takes to cycle throught the 'angle range':
    angle_time = Range( 1.0, 20.0, 5.0 )

    # The collection of all triangles currently being drawn:
    triangles = List( Triangle )

    # Event fired when user wants to change animation parameters:
    modify = Event

    #-- Facet View Definitions -------------------------------------------------

    # Defines the main Twixter view:
    facets_view = View(
        UItem( 'triangles',
               editor = CustomControlEditor( klass = TrianglesEditor )
        ),
        HGroup(
            spring,
            Item( 'modify',
                  show_label = False,
                  tooltip    = 'Click to edit the animation parameters',
                  editor     = ThemedButtonEditor(
                                   theme = None,
                                   image = '@icons2:GearExecute',
                                   view  = 'animation_popup' )
            ),
            '_',
            Item( 'count',
                  tooltip = 'The number of triangles drawn between the start '
                            'and end triangles',
                  width   = -35,
                  editor  = ScrubberEditor()
            ),
            '_',
            Item( 'angle',
                  tooltip = 'The amount of rotation (in degrees) between the '
                            'start and end triangles',
                  width   = -35,
                  editor  = ScrubberEditor()
            ),
            group_theme = '@xform:bg?L30'
        ),
        width   = 0.75,
        height  = 0.75,
        handler = TwixterHandler
    )


    # Defines the animation controls pop-up view:
    animation_popup = View(
        BevelGroup(
            RangeItem( 'count_time',
                tooltip = 'The length of time (in seconds) needed to cycle '
                          'through the count range'
            ),
            Item( 'count_range',
                  tooltip = 'The minimum and maximum number of triangles used '
                            'in the animation',
                  width   = -200,
                  editor  = RangeSliderEditor(
                                low = 2, high = 1000, body_style = 25 )
            )
        ),
        BevelGroup(
            RangeItem( 'angle_time',
                tooltip = 'The length of time (in seconds) needed to cycle '
                          'through the angle range'
            ),
            Item( 'angle_range',
                  tooltip = 'The minimum and maximum rotation angles used in '
                            'the animation',
                  width   = -200,
                  editor  = RangeSliderEditor(
                                low = 0, high = 3600, body_style = 25 )
            )
        ),
        BevelGroup(
            RangeItem( 'index_time',
                label   = 'Cycle time',
                tooltip = 'The length of time (in seconds) needed to cycle '
                          'through the sub-range of triangles drawn'
            ),
            RangeItem( 'percent',
                tooltip = 'The percentage of triangles drawn in the sub-range'
            )
        ),
        BevelGroup(
            Item( 'width_range',
                  tooltip = 'The minimum and maximum line widths used in the '
                            'animation',
                  width   = -200,
                  editor  = RangeSliderEditor(
                                low = 1, high = 20, body_style = 25 )
            )
        ),
        BevelGroup(
            Item( 'animate', tooltip = 'Turn the animation on or off' )
        ),
        kind = 'popup'
    )

    #-- Facets Initialization --------------------------------------------------

    def facets_init ( self ):
        self._animate_set()

    #-- Facet Default Values ---------------------------------------------------

    def _start_default ( self ):
        return Triangle(
            p0       = ( 100, 100 ),
            p1       = ( 100, 400 ),
            p2       = ( 350, 250 ),
            color    = 0xFF0000,
            editable = True
        ).set(
            owner    = self
        )


    def _end_default ( self ):
        return Triangle(
            p0       = ( 700, 100 ),
            p1       = ( 700, 400 ),
            p2       = ( 450, 250 ),
            color    = 0xFF0000,
            editable = True
        ).set(
            owner    = self
        )


    def _center_default ( self ):
        return Triangle(
            p0       = ( 250, 350 ),
            p1       = ( 550, 350 ),
            p2       = ( 400, 150 ),
            color    = 0xFF0000,
            editable = True
        ).set(
            owner    = self
        )


    def _triangles_default ( self ):
        return [ self.start, self.end, self.center ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _animate_set ( self ):
        """ Handles the 'animate' facet being changed.
        """
        if self.animate:
            self.animate_facet(
                'count', self.count_time,
                self.count_range[1], self.count_range[0],
                repeat = 0
            )
            self.animate_facet(
                'angle', self.angle_time,
                self.angle_range[1], self.angle_range[0],
                repeat = 0
            )
            self.animate_facet(
                'index', self.index_time, 1.0, 0.0, repeat  = 0
            )
        else:
            self.halt_animated_facets()


    @on_facet_set( 'count_range, angle_range, count_time, angle_time, index_time' )
    def _animation_modified ( self ):
        """ Handles any of the animation related values being changed.
        """
        do_after( 1000, self._restart_animation )


    def _update_set ( self ):
        """ Updates the lines after some type of change has occurred.
        """
        self._generate()

    #-- Private Methods --------------------------------------------------------

    def _restart_animation ( self ):
        """ Restart the animation if it is running.
        """
        if self.animate:
            self.animate = False
            self.animate = True


    def _generate ( self ):
        """ Returns a list of Triangle objects representing the current
            interpolation from 'line' to 'target' rotating around 'center'.
        """
        lx0, ly0   = self.start.p0
        lx1, ly1   = self.start.p1
        lx2, ly2   = self.start.p2
        tx0, ty0   = self.end.p0
        tx1, ty1   = self.end.p1
        tx2, ty2   = self.end.p2
        dx0, dy0   = tx0 - lx0, ty0 - ly0
        dx1, dy1   = tx1 - lx1, ty1 - ly1
        dx2, dy2   = tx2 - lx2, ty2 - ly2
        cx0, cy0   = self.center.p0
        cx1, cy1   = self.center.p1
        cx2, cy2   = self.center.p2
        dcx0, dcy0 = cx1 - cx0, cy1 - cy0
        dcx1, dcy1 = cx2 - cx1, cy2 - cy1
        dcx2, dcy2 = cx0 - cx2, cy0 - cy2
        d0         = sqrt( (dcx0 * dcx0) + (dcy0 * dcy0) )
        d1         = sqrt( (dcx1 * dcx1) + (dcy1 * dcy1) )
        d2         = sqrt( (dcx2 * dcx2) + (dcy2 * dcy2) )
        dt0        = 2.0
        p          = d0 + d1 + d2
        if p > 0.0:
            dt0  = d0 / p
            dt1  = d1 / p
            dt2  = d2 / p
            dt01 = dt0 + dt1

        angle     = (pi * self.angle) / 180.0
        triangles = []
        dt        = 1.0 / (self.count - 1)
        t         = 0.0
        et        = 1.0 + (dt / 2.0)
        while t < et:
            if t <= dt0:
                ncx = cx0 + ((dcx0 * t) / dt0)
                ncy = cy0 + ((dcy0 * t) / dt0)
            elif t <= dt01:
                ncx = cx1 + ((dcx1 * (t - dt0)) / dt1)
                ncy = cy1 + ((dcy1 * (t - dt0)) / dt1)
            else:
                ncx = cx2 + ((dcx2 * (t - dt01)) / dt2)
                ncy = cy2 + ((dcy2 * (t - dt01)) / dt2)

            a        = angle * t
            nx0, ny0 = self._point_for( lx0, ly0, dx0, dy0, ncx, ncy, a, t )
            nx1, ny1 = self._point_for( lx1, ly1, dx1, dy1, ncx, ncy, a, t )
            nx2, ny2 = self._point_for( lx2, ly2, dx2, dy2, ncx, ncy, a, t )

            triangles.append( Triangle(
                p0 = point( nx0, ny0 ),
                p1 = point( nx1, ny1 ),
                p2 = point( nx2, ny2 ),
            ) )
            t += dt

        n      = len( triangles )
        m      = max( 1, int( round( (n * self.percent) / 100.0 ) ) )
        i      = int( round( (n - m) * self.index ) )
        w0, w1 = self.width_range
        dw     = float( w1 - w0 ) / m
        for j in xrange( m ):
            triangles[ i + j ].width = int( round( w0 + (j * dw) ) )

        self.triangles[:-3] = triangles[ i: i + m ]


    def _point_for ( self, x, y, dx, dy, cx, cy, a, t ):
        """ Returns the next point from (*x*,*y*) with vector (*dx*,*dy*) at
            time *t*, rotated *a* around point (*cx*,*cy*).
        """
        dcx = x + (dx * t) - cx
        dcy = y + (dy * t) - cy
        b   = a + atan2( dcy, dcx )
        r   = sqrt( (dcx * dcx) + (dcy * dcy) )

        return ( cx + (r * cos( b )), cy + (r * sin( b )) )

#-- Create the demo ------------------------------------------------------------

demo = Twixter

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
