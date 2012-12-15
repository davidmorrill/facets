"""
This demo illustrates some simple uses of a <b>DrawableCanvas</b> and its
associated <b>DrawableCanvasEditor</b>. In particular, the demo illustrates
several ways in which <b>DrawableCanvas</b> items can easily be animated to
produce interesting visual effects.

A <b>DrawableCanvas</b> is basically a container for <i>drawable</i> items. The
order of the items in the canvas's <b><i>content</i></b> facet determines the
order in which the item's are drawn. The first item in the list is drawn first
and the last item is drawn last.

The demo is set up so that initially a single randomly selected demo is
displayed. Several different demos are available and the current demo can be
changed by selecting a different item from the <i>Demo</i> dropdown located
in the bottom right corner of the display.

You can create additional demo instances by clicking the <i>plus</i> icon in the
bottom right corner. This adds a new instance with a randomly selected demo to
the display. You can use the standard drag and splitter controls to adjust the
size and position of the new demo. You can change the demo by selecting the
demo's tab and then selecting a new demo using the dropdown selector. Click any
demo tab's <i>close</i> icon to remove the demo from the display.
"""

#-- Imports --------------------------------------------------------------------

import facets.ui.drawable.drawable

from math \
    import sin, cos, pi

from random \
    import randint, shuffle, choice

from os.path \
    import splitext

from facets.api \
    import HasFacets, Instance, List, Enum, Button, Color, Theme, View,       \
           VGroup, HGroup, Item, UItem, DrawableCanvasEditor, NotebookEditor, \
           ColorPaletteEditor, on_facet_set

from facets.animation.api \
    import RampTweener, Path, Spiral2DIntPath, PolyPath, EaseIn, EaseOutEaseIn

from facets.ui.pen \
    import Pen

from facets.ui.drawable.api \
    import DrawableCanvas, Point, Text, ThemedText, Line, Circle, Rectangle, \
           Polygon

from facets.ui.pyface.timer.api \
    import do_later, do_after

from facets.lib.io.file \
    import File

#-- Constants ------------------------------------------------------------------

A2R    = pi / 180.0
dsin   = lambda a: sin( A2R * a )
dcos   = lambda a: cos( A2R * a )
RGBCMY = [ 0xFF0000, 0x00FF00, 0x0000FF, 0x00FFFF, 0xFF00FF, 0xFFFF00 ]
demos  = ( 'Morphing boxes', 'Line plot', 'Bar chart', 'Scatter plot',
           'Resizing circles', 'Resizing boxes', 'Source code', 'Star burst',
           'Cats Cradle' )

#-- Helper functions -----------------------------------------------------------

def grid ( x0, x1, xs, y0, y1, ys ):
    for x in xrange( x0, x1, xs ):
        for y in xrange( y0, y1, ys ):
            yield ( x, y )

def rand_pt ( x, y, dx, dy ):
    return ( randint( x, max( x, x + dx ) ), randint( y, max( y, y + dy ) ) )

def ramped ( items, name, time, end, cycle = 0.5, reverse = True, start = 0.0 ):
    scale = (1.0 - (2.0 * start)) / len( items )
    for i in xrange( len( items ) ):
        items[ i ].animate_facet(
            name, time, end,
            repeat  = 0,
            reverse = reverse,
            tweener = RampTweener( start = start + (scale * i), cycle = cycle )
        )

    return items

def gen_ys ( n, y0, y1, dy ):
    y1 = max( y1, y0 )
    ys = [ randint( y0, y1 ) ]
    for i in xrange( n - 1 ):
        ys.append( min( max( ys[-1] + randint( -dy, dy ), y0 ), y1 ) )

    return ys

def plot_grid ( x0, x1, dx, y0, y1, dy, color ):
    return ([
        Line( p0 = ( x, y0 ), p1 = ( x, y1 ), pen = color, anti_alias = False )
        for x in xrange( x0, x1 + 1, dx ) ] + [
        Line( p0 = ( x0, y ), p1 = ( x1, y ), pen = color, anti_alias = False )
        for y in xrange( y0, y1 + 1, dy ) ]
    )

def two_colors ( ):
    return ( choice( RGBCMY[:3] ), choice( RGBCMY[3:] ) )

#-- SourcePath class -----------------------------------------------------------

class SourcePath ( Path ):

    def at ( self, v0, v1, t ):
        n = int( t * (len( v0 ) - 5 ))
        return (v0[:5] + v0[5:5 + n])

#-- DemoItem class -------------------------------------------------------------

class DemoItem ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The DrawableCanvas used for each demo:
    canvas = Instance( DrawableCanvas, () )

    # The list of currently active animations:
    animations = List

    # The name of the current demo:
    demo = Enum( *demos )

    # The color to use for the current demo:
    color = Color

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'canvas',
               editor = DrawableCanvasEditor( theme = '@xform:bg?l50' )
        )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _demo_default ( self ):
        return choice( demos )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        do_later( self.reset_demo )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'animations[]' )
    def _animations_modified ( self, removed ):
        for item in removed:
            item.halt_animated_facets()

    def _demo_set ( self ):
        self.reset_demo()

    def _color_set ( self, color ):
        for item in self.canvas.content:
            if item._set_brush:
                item.brush = color

    @on_facet_set( 'canvas:bounds' )
    def _bounds_modified ( self ):
        """ Handles the 'bounds' of the canvas being changed.
        """
        do_after( 100, self.reset_demo )

    #-- Public Methods ---------------------------------------------------------

    def reset_demo ( self ):
        self.canvas.content = self.current_demo()

    #-- Demo Methods -----------------------------------------------------------

    def morphing_boxes ( self ):
        s               = 68
        x, y, dx, dy    = self.canvas.bounds
        self.animations = items = [
            Rectangle(
                origin     = ( ix, iy ),
                size       = ( s, s ),
                radius     = 1,
                anti_alias = True,
                pen        = None,
                brush      = choice( RGBCMY )
            ) for ix, iy in grid( x, x + dx, s + 2, y, y + dy, s + 2 )
        ]
        for item in items:
            item._set_brush = (item.brush is RGBCMY[0])
        path    = Spiral2DIntPath()
        tweener = RampTweener( EaseOutEaseIn, cycle = 0.97 )
        indices = range( len( items ) )
        shuffle( indices )
        for i in xrange( len( items ) ):
            item = items[i]
            item.animate_facet( 'radius', 3.5, s / 2,
                repeat  = 0,
                tweener = tweener
            )
            item.animate_facet( 'origin', 3.5, items[ indices[i] ].origin,
                repeat  = 0,
                path    = path,
                tweener = tweener
            )

        return items

    def star_burst ( self ):
        x, y, dx, dy = self.canvas.bounds
        items        = []
        r            = 105
        for i in xrange( 9 ):
            x1, y1 = rand_pt( x + r, y + r, dx - (2 * r), dy - (2 * r) )
            x2, y2 = rand_pt( x + r, y + r, dx - (2 * r), dy - (2 * r) )
            items.append(
                self.circle_at( x1, y1, x2, y2, choice( RGBCMY ), i < 3 )
            )

        bars = [ Rectangle( origin = ( ix + 20, y ), size = ( 20, dy ),
                            pen = None, brush = 0x000000, opacity = 0.3 )
                 for ix in xrange( x, dx, 40 ) ]
        for bar in bars:
            bar.animate_facet( 'opacity', 4.0, 0.0, repeat = 0,
                               tweener = RampTweener( cycle = 0.1 ) )

        self.animations.extend( bars )
        return (items + bars)

    def resizing_circles ( self ):
        radius       = 30
        step         = int( 1.4 * radius )
        brush        = choice( RGBCMY )
        x, y, dx, dy = self.canvas.bounds
        self.animations = items = ramped(
            [ Circle( origin     = ( ix, iy ),
                      radius     = 0.5,
                      pen        = None,
                      brush      = brush,
                      _set_brush = True )
              for ix, iy in grid( x, x + dx + radius, step,
                                  y, y + dy + radius, step ) ],
            'radius', 2.5, radius, 0.67
        )
        return items

    def resizing_boxes ( self ):
        x, y, dx, dy = self.canvas.bounds
        size         = 40
        brush        = choice( RGBCMY )
        self.animations = ramped(
            [ Rectangle( origin     = ( ix, iy ),
                         size       = ( size, size ),
                         pen        = None,
                         brush      = brush,
                         _set_brush = True )
              for ix, iy in grid( x, x + dx + size - 1, size,
                                  y, y + dy + size - 1, size ) ],
            'size', 4.0, ( -size, -size ), 0.5
        )

        return self.animations

    def scatter_plot ( self ):
        n            = 240
        cn           = len( RGBCMY )
        x, y, dx, dy = self.plot_bounds()
        dxf, dyf     = (2 * dx) / 5, (2 * dy) / 5
        cx, cy       = x + (dx / 2), y + (dy / 2)
        radius       = 1 + int( min( dx, dy ) / 110 )
        points       = [ rand_pt( x, y, dx - dxf, dy - dyf )
                         for i in xrange( len( RGBCMY ) ) ]
        self.animations = items = [
            Circle( origin     = ( cx, cy ),
                    radius     = radius,
                    pen        = None,
                    brush      = RGBCMY[ i % cn ],
                    _set_brush = (i % cn) == 0 )
            for i in xrange( n )
        ]

        scale = 0.6 / n
        for i in xrange( n ):
            cx, cy = points[ i % cn ]
            items[i].animate_facet(
                'origin', 3.0, rand_pt( cx, cy, dxf, dyf ),
                repeat = 0, reverse = True,
                tweener = RampTweener( EaseIn, start = 0.3 + (scale * i),
                                               cycle = 0.3 )
            )

        return (items + plot_grid( x, x + dx, 50, y, y + dy, 50, 0x808080 ))

    def line_plot ( self ):
        c1, c2       = two_colors()
        x, y, dx, dy = self.plot_bounds()
        return ([ self.make_line( c1, 1.0, True  ),
                  self.make_line( c2, 0.7, False ) ] +
                plot_grid( x, x + dx, 50, y, y + dy, 50, 0x808080 ))

    def bar_chart ( self ):
        c1, c2       = two_colors()
        x, y, dx, dy = self.plot_bounds()
        return (self.make_bar( c1, 0.00, 0.55, True  ) +
                self.make_bar( c2, 0.40, 0.55, False ) +
                plot_grid( x, x + dx, dx, y, y + dy, 50, 0xB0B0B0 ))

    def source_code ( self ):
        lines = [ line for line in File(
            splitext( facets.ui.drawable.drawable.__file__ )[0] + '.py'
        ).lines if line.strip() != '' ]
        x, y, dx, dy = self.canvas.bounds
        tdy = 20
        n   = (dy + tdy - 1) / tdy
        ci  = 0
        nci = reduce( lambda x, y: x + (y.strip()[:1] == '#'), lines[:n], 0 )
        indices = []
        for i in xrange( n ):
            if lines[i].strip()[:1] == '#':
                indices.append( ci )
                ci += 1
            else:
                indices.append( nci )
                nci += 1
        themes = ( Theme( '@xform:b?L30', content_font = 'Courier 10' ),
                   Theme( '@xform:b?L15', content_font = 'Courier 10' ) )
        items  = [
            ThemedText(
                theme  = themes[ lines[i].strip()[:1] == '#' ],
                origin = ( x, y + (tdy * i) ),
                size   = ( dx, tdy ),
                text   = '%3d| %s' % ( i + 1, lines[i] )
            ) for i in xrange( n )
        ]
        self.animations.extend( items )
        path    = SourcePath()
        tweener = RampTweener( EaseOutEaseIn, start = 0.95, cycle = 0.4 )
        scale   = 0.9 / max( n, 1 )
        for i in xrange( len( items ) ):
            item = items[i]
            item.animate_facet( 'origin', 3.5, items[ indices[i] ].origin,
                repeat  = 0,
                tweener = tweener
            )
            item.animate_facet( 'text', 3.5,
                end     = '',
                repeat  = 0,
                path    = path,
                tweener = RampTweener( start = 0.05 + (scale * i), cycle = 0.5 )
            )
        return ([Rectangle( origin = ( x, y ), size  = (dx, dy ),
                            pen    = None,     brush = 0xD0D0D0 ) ] + items)

    def cats_cradle ( self ):
        n            = 8
        time         = 4.5
        x, y, dx, dy = self.canvas.bounds
        dx2, dy2     = dx / 2, dy / 2
        mindxy       = int( min( dx, dy ) )
        radius       = mindxy / 16
        path1        = PolyPath()
        path2        = PolyPath( points = [ ( 0.2, -0.3 ), ( 0.4, -0.4 ),
                                            ( 0.6,  0.4 ), ( 0.8,  0.3 ) ] )
        paths        = ( path2, path1, path1 )
        tweener      = RampTweener( EaseOutEaseIn, cycle = 0.99 )
        pen          = Pen( color = 0xFFFF00, width = max( mindxy / 90, 1 ) )
        animations   = self.animations
        lines        = []
        circles      = []
        points       = [ rand_pt( x + ((dx2 / 2) * (i / 2)) + 35,
                                  y + (dy2 * (i % 2)) + 35,
                                  (dx2 / 2) - 70, dy2 - 70 )
                         for i in xrange ( n ) ]
        for i in xrange( n ):
            begin  = points[ i ]
            end    = points[ (i + 5) % n ]
            begins = ( begin, begin, end )
            ends   = ( end, end, begin )
            for j in xrange( 3 ):
                line = Line( p0 = begin, p1 = end, pen = pen )
                line.animate_facet(
                    'p0', time, ends[j], begin = begins[j],
                    repeat = 0, path = path1, tweener = tweener
                )
                line.animate_facet(
                    'p1', time, ends[2-j], begin = begins[2-j],
                    repeat = 0, path = path1 if j == 0 else path2,
                    tweener = tweener
                )
                animations.append( line )
                lines.append( line )

            for j in xrange( 3 ):
                circle = Circle( origin = begin, radius = radius,
                                 pen = None, brush = RGBCMY[ j ],
                                 _set_brush = (j == 0) )
                circle.animate_facet(
                    'origin', time, end = ends[j], begin = begins[j],
                    repeat  = 0, path = paths[j], tweener = tweener )
                animations.append( circle )
                circles.append( circle )

        return (lines + circles)

    #-- Helper Methods ---------------------------------------------------------

    def current_demo ( self ):
        time = 1.3
        x, y, dx, dy = self.canvas.bounds
        ty = y + dy - 70
        bg = ThemedText(
            theme   = '@std:heading2?L12S58?L12S58',
            origin  = ( x - 3, ty - 7 ),
            size    = ( dx + 6, 56 ),
            opacity = 0.0
        )
        text = Text(
            text    = self.demo,
            font    = '23',
            opacity = 0.0,
            color   = 0xF0F0F0,
            origin  = ( x + dx + 5, ty )
        )
        tweener1 = RampTweener( EaseIn, cycle = 0.7 )
        tweener2 = RampTweener( EaseIn, cycle = 0.4 )
        text.animate_facet(
            'origin', time, ( x + 24, ty ), repeat = 2, tweener = tweener1
        )
        text.animate_facet(
            'opacity', time, 1.0, repeat = 2, tweener = tweener2
        )
        bg.animate_facet(
            'opacity', time, 1.0, repeat = 2, tweener = tweener2
        )
        del self.animations[:]
        result = (getattr( self, self.demo.lower().replace( ' ', '_' ) )() +
                  [ bg, text ])
        self.animations.append( text )
        return result

    def plot_bounds ( self, size = 50 ):
        x, y, dx, dy = self.canvas.bounds
        pdx, pdy     = ((dx - 7) / size) * size, ((dy - 7) / size) * size
        return ( x + ((dx - pdx) / 2), y + ((dy - pdy) / 2), pdx, pdy )

    def circle_at ( self, cx1, cy1, cx2, cy2, color, set_brush ):
        start, end    = [], []
        r1, r2, da, i = 3, ( 30, 100 ), 15, 0
        for a in xrange( 0, 360, da ):
            start.append( Point( cx1 + (r1 * dcos( a )),
                                 cy1 + (r1 * dsin( a )) ) )
            end.append( ( cx2 + (r2[i] * dcos( a )),
                          cy2 + (r2[i] * dsin( a )) ) )
            i = 1 - i

        self.animations.extend( start )
        for i in xrange( 0, len( end ) ):
            start[i].animate_facet(
                'xy', 2.0, end[i], repeat = 0, tweener = EaseOutEaseIn
            )

        return Polygon(
            points     = start,
            pen        = None,
            brush      = color,
            opacity    = 0.75,
            _set_brush = set_brush
        )

    def make_line ( self, color = 0xFF0000, opacity = 1.0, set_brush = False ):
        n            = 100
        x, y, dx, dy = self.plot_bounds()
        by           = y + dy
        idx          = float( dx ) / (n - 1)
        rx           = x + (idx * (n - 1))
        ys           = gen_ys( n, y, by, 30 )
        pts = (
            [ Point( x, by ) ] +
            [ Point( x + (idx * i), by ) for i in xrange( n ) ] +
            [ Point( rx, by ) ]
        )
        self.animations.extend( pts )
        scale = 0.6 / n
        for i in xrange( 1, len( pts ) - 1 ):
            pts[i].animate_facet( 'xy', 2.5, ( pts[i].xy[0], ys[i-1] ),
                repeat  = 0,
                tweener = RampTweener( EaseIn, start = 0.2 + (scale * (i-1)),
                                       cycle = 0.4 )
            )
        return Polygon(
            points     = pts,
            pen        = None,
            opacity    = opacity,
            brush      = color,
            _set_brush = set_brush
        )

    def make_bar ( self, color = 0xFF0000, offset = 0.0, width = 1.0,
                         set_brush = False ):
        n            = 20
        x, y, dx, dy = self.plot_bounds()
        by           = y + dy
        sdx          = dx / n
        bdx          = int( round( width  * sdx ) )
        x           += int( round( offset * sdx ) )
        rx           = x + (sdx * n)
        ys           = gen_ys( n, 10, dy - 10, 100 )
        bars = [
            Rectangle(
                origin     = ( ix, by ),
                size       = ( bdx, 0 ),
                brush      = color,
                _set_brush = set_brush )
            for ix in xrange( x, rx, sdx )
        ]
        self.animations.extend( bars )
        scale = 0.6 / n
        for i in xrange( n ):
            bars[i].animate_facet( 'size', 2.2, ( bdx, -ys[i] ),
                repeat  = 0,
                tweener = RampTweener( EaseIn, start = 0.2 + (scale * (i-1)),
                                       cycle = 0.25 )
            )
        return bars

#-- DrawableCanvasEditorDemo class ---------------------------------------------

class DrawableCanvasEditorDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    items    = List # ( DemoItem )
    add      = Button( '@icons2:Add_2' )
    reset    = Button( '@icons2:Reload' )
    selected = Instance( DemoItem )
    demo     = Enum( *demos )
    color    = Color

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            VGroup(
                UItem( 'items',
                       editor = NotebookEditor(
                           deletable  = True,
                           dock_style = 'tab',
                           layout     = 'columns',
                           max_items  = 2,
                           selected   = 'selected',
                           page_name  = '.demo' )
                ),
                group_theme = '#themes:tool_options_group'
            ),
            HGroup(
                UItem( 'color',
                       springy = True,
                       editor  = ColorPaletteEditor(
                                     cell_rows = 1, cell_size = 16 )
                ),
                Item( 'demo',
                      tooltip      = 'Select the demo to display',
                      enabled_when = 'selected is not None'
                ),
                '_',
                UItem( 'reset',
                       tooltip      = 'Click to reset current demo',
                       enabled_when = 'selected is not None'
                ),
                UItem( 'add',
                       tooltip = 'Click to add a new demo item'
                ),
                group_theme = '#themes:toolbar_group'
            )
        ),
        width  = 0.8,
        height = 0.8
    )

    #-- Facet Default Values ---------------------------------------------------

    def _items_default ( self ):
        return [ DemoItem() ]

    def _selected_default ( self ):
        return self.items[0]

    def _demo_default ( self ):
        return self.selected.demo

    #-- Facet Event Handlers ---------------------------------------------------

    def _add_set ( self ):
        demo = DemoItem()
        self.items.append( demo )
        self.selected = demo

    def _reset_set ( self ):
        self.selected.reset_demo()

    def _selected_set ( self, selected ):
        if selected is not None:
            self.demo = selected.demo

    def _demo_set ( self, demo ):
        if self.selected is not None:
            self.selected.demo = demo

    def _color_set ( self, color ):
        if self.selected is not None:
            self.selected.color = color

    @on_facet_set( 'items[]' )
    def _items_modified ( self, removed ):
        if len( removed ) > 0:
            for item in removed:
                del item.animations

            if len( self.items ) > 0:
                if self.selected in removed:
                    self.selected = self.items[-1]
            else:
                self.selected = None

    #-- Public Methods ---------------------------------------------------------

    def dispose ( self ):
        del self.items[:]

#-- Create the demo ------------------------------------------------------------

demo = DrawableCanvasEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
