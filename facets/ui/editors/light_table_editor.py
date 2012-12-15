"""
Defines the LightTableEditor for view, selecting and animating lists of images.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt

from random \
    import choice, shuffle, randint, random

from facets.api \
    import HasPrivateFacets, Any, Bool, Int, Float, Tuple, Image, Callable, \
           Enum, Str, Range, List, Instance, Event, Property, ATheme, Theme, \
           View, VGroup, UItem, ImageEditor, on_facet_set

from facets.core.facet_base \
    import clamp

from facets.ui.constants \
    import scrollbar_dx, scrollbar_dy

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.animation.api \
    import ConcurrentAnimation, CycleTweener, RampTweener, \
           EaseOutEaseInTweener, Linear2DIntPath, Manhattan2DIntPath, \
           Spiral2DIntPath

from facets.lib.io.file \
    import File

from facets.extra.helper.image \
    import hlsa_derived_image, HLSATransform

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.ui.pyface.timer.api \
    import do_later, do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The paths available for animations:
Paths = [ Linear2DIntPath(), Manhattan2DIntPath(), Spiral2DIntPath() ]

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def srandint ( n1, n2 ):
    """ Returns a positive or negative random integer in the range n1..n2.
    """
    if random() < 0.5:
        return -randint( n1, n2 )

    return randint( n1, n2 )

#-------------------------------------------------------------------------------
#  'ThemedImage' class:
#-------------------------------------------------------------------------------

class ThemedImage ( HasPrivateFacets ):
    """ Defines an themed image that can appear on a light table.
    """

    #-- Style Facet Definitions ------------------------------------------------

    # The image display mode:
    mode = Enum( 'fit', 'crop', 'zoom' )

    # Is the image user zoomable?
    zoomable = Bool( False )

    # Should the label be displayed:
    show_label = Bool( False )

    # The normal theme for the item:
    normal_theme = ATheme( Theme( '@xform:photo?L5s|h40H60', content = 10 ) )

    # The 'selected' state theme for the item:
    normal_selected_theme = ATheme

    # The 'hover' state theme for the item:
    hover_theme = ATheme

    # The 'hover' and 'selected' state theme for the item:
    hover_selected_theme = ATheme

    # The 'down' state theme for the item:
    down_theme = ATheme

    # The 'down' and 'selected' state theme for the item:
    down_selected_theme = ATheme

    # The HLSATransform that should be used when automatically creating derived
    # selected themes:
    transform = Instance( HLSATransform, { 'hue': 0.11, 'lightness': -0.16,
                                           'saturation': 0.96 } )

    # The 'lightness' offset that should be used when automatically creating
    # derived 'hover' and 'down' themes:
    lightness = Range( -1.0, 1.0, -0.12 )

    #-- Externally Managed Facet Definitions -----------------------------------

    # The original value used to create the ThemedImage:
    value = Any

    # Is the image selected?
    selected = Bool( False )

    # The position of the image on the light table:
    position = Tuple( Int, Int )

    # The size of the image:
    size = Tuple( Int, Int )

    # The display bounds for the themed image:
    bounds = Property

    # The event fired when the current mouse state of the image is changed:
    mouse_state = Event # ( Str )

    #-- Editor/Application Set Facet Definitions -------------------------------

    # The image being displayed:
    image = Image

    # The label for the image:
    label = Str

    #-- Editor Set Facet Definitions -------------------------------------------

    # The editor associated with the item:
    editor = Any

    #-- Internally Managed Facet Definitions -----------------------------------

    # Is a 'zoomable' image currently zoomed?
    zoomed = Bool( False )

    # An (optional) scaled version of the image:
    scaled_image = Image

    # The scale factor used to create the current scaled image:
    scale = Float

    # The current origin of the image (used when mode = 'crop'):
    origin = Tuple( Float, Float )

    # The current theme state of the item:
    theme_state = Str( 'normal' )

    #-- Public Methods ---------------------------------------------------------

    def __call__ ( self, image ):
        """ Returns a new ThemedImage object for the specified image using this
            class as the template.
        """
        result = self.__class__( **self.get(
            'mode', 'zoomable', 'show_label', 'normal_theme',
            'normal_selected_theme', 'hover_theme', 'hover_selected_theme',
            'down_theme', 'down_selected_theme'
        ) )

        if isinstance( image, File ):
            image = image.absolute_path

        if isinstance( image, ( basestring, AnImageResource ) ):
            result.image = image

        return result.set( value = image )


    def is_in ( self, x, y ):
        """ Returns whether or not the point specified by (*x*,*y*) is in the
            themed image.
        """
        ix, iy, idx, idy = self.bounds

        return ((ix <= x < (ix + idx)) and (iy <= y < (iy + idy)))


    def paint ( self, g, lx, ly ):
        """ Paints the item in the graphics context specified by *g* using the
            logical offset specified by *lx* and *ly*.
        """
        bx, by, bdx, bdy = self.bounds
        bx   += lx
        by   += ly
        theme = getattr( self, self.theme_state + '_theme' )
        theme.fill( g, bx, by, bdx, bdy )
        tx, ty, tdx, tdy = theme.bounds( bx, by, bdx, bdy )
        if self.zoomed:
            self._paint_zoomed( g, tx, ty, tdx, tdy )
        else:
            getattr( self, '_paint_' + self.mode )( g, tx, ty, tdx, tdy )

        if self.show_label and theme.has_label:
            theme.draw_label( g, self.label, None, bx, by, bdx, bdy )

    #-- Facet Default Values ---------------------------------------------------

    def _label_default ( self ):
        return self.image.name


    def _hover_theme_default ( self ):
        return self._theme_for( self.lightness )


    def _down_theme_default ( self ):
        return self._theme_for( 2.0 * self.lightness )


    def _normal_selected_theme_default ( self ):
        return self._theme_for( 0.0, self.transform )


    def _hover_selected_theme_default ( self ):
        return self._theme_for( self.lightness, self.transform )


    def _down_selected_theme_default ( self ):
        return self._theme_for( 2.0 * self.lightness, self.transform )

    #-- Property Implementations -----------------------------------------------

    def _get_bounds ( self ):
        return (self.position + self.size)

    #-- Private Methods --------------------------------------------------------

    def _paint_fit ( self, g, x, y, dx, dy ):
        """ Paints the image in 'fit' mode.
        """
        image    = self.image
        idx, idy = image.width, image.height
        if (idx <= dx) and (idy <= dy):
            g.draw_bitmap( image.bitmap,
                           x + ((dx - idx) / 2), y + ((dy - idy) / 2) )
        else:
            self._draw_scaled( g, x, y, dx, dy )


    def _paint_crop ( self, g, x, y, dx, dy ):
        """ Paints the image in 'crop' mode.
        """
        image    = self.image
        idx, idy = image.width, image.height
        if (idx <= dx) and (idy <= dy):
            g.draw_bitmap( image.bitmap,
                           x + ((dx - idx) / 2), y + ((dy - idy) / 2) )
        else:
            ox, oy = self.origin
            ox     = min( int( round( ox ) ), idx - dx )
            oy     = min( int( round( oy ) ), idy - dy )
            g.blit( x, y, dx, dy, image.bitmap, ox, oy, dx, dy )


    def _paint_zoom ( self, g, x, y, dx, dy ):
        """ Paints the image in 'zoom' mode.
        """
        self._draw_scaled( g, x, y, dx, dy )


    def _paint_zoomed ( self, g, x, y, dx, dy ):
        """ Paints a 'zoomed' image.
        """
        # fixme: Implement this...


    def _draw_scaled ( self, g, x, y, dx, dy ):
        """ Draws an image scaled to fit within the item's client area.
        """
        if (dx > 0) and (dy > 0):
            image    = self.image
            idx, idy = image.width, image.height
            rdx, rdy = float( idx ) / dx, float( idy ) / dy
            if rdx >= rdy:
                ddx, ddy = dx, int( round( idy / rdx ) )
            else:
                ddx, ddy = int( round( idx / rdy ) ), dy
                rdx      = rdy

            if not (0.833 <= rdx <= 1.2):
                if rdx != self.scale:
                    self.scale        = rdx
                    self.scaled_image = image.scale( 1.0 / rdx )

                image    = self.scaled_image
                idx, idy = image.width, image.height

            g.blit( x + ((dx - ddx) / 2), y + ((dy - ddy) / 2), ddx, ddy,
                    image.bitmap, 0, 0, idx, idy )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'theme_state, position, size' )
    def _editor_update ( self ):
        """ Handles some facet requiring the item to be refreshed being changed.
        """
        if self.editor is not None:
            self.editor.update = self


    def _image_set ( self ):
        """ Handles the 'image' facet being changed.
        """
        self.scaled_image = None
        self.scale        = 0.0

        if self.editor is not None:
            self.editor.update = self


    def _mouse_state_set ( self, state ):
        """ Handles the 'mouse_state' event being fired.
        """
        self.theme_state = (state + ( '', '_selected' )[ self.selected ])


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        self.theme_state = (self.theme_state.split( '_' )[0] +
                            ( '', '_selected' )[ selected ])

    #-- Private Methods --------------------------------------------------------

    def _theme_for ( self, lightness = 0.0, transform = None ):
        """ Returns a new theme based upon the 'normal_theme', with the HLSA
            transform adjustment values specified by *lightness* and *selected*
            applied.
        """
        theme = self.normal_theme
        xform = HLSATransform( lightness = clamp( lightness, -1.0, 1.0 ) )
        if transform is not None:
            xform = xform.transform( transform )

        return Theme( hlsa_derived_image( theme.image, xform )
        ).set(
            border    = theme.border,
            content   = theme.content,
            label     = theme.label,
            alignment = theme.alignment
        )

# Create a themed image for the editor to use as a default adapter:
DefaultThemedImage = ThemedImage()

#-------------------------------------------------------------------------------
#  'ImageLayout' class:
#-------------------------------------------------------------------------------

class ImageLayout ( HasPrivateFacets ):
    """ Base class for objects that manage the layout of ThemedImages on a light
        table.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Should images display at their actual size?
    actual_size = Bool( False )

    # Image width (when 'actual_size' is False):
    width = Range( 16, None, 160 )

    # Image display ratio (horizontal/vertical):
    ratio = Range( 0.1, 10.0, 1.0 )

    # Event fired when the layout manager needs to update the layout of all
    # items:
    update = Event

    #-- Public Methods ---------------------------------------------------------

    def layout ( self, editor ):
        """ Performs a complete layout of the contents of the specified
            _LightTableEditor *editor*.
        """
        raise NotImplementedError


    def update_layout ( self, editor, start, added, removed ):
        """ Performs an update to an existing layout that begins at the index
            specified by *start* which involves adding and deleting the number
            of images specified by *added* and *removed* for the specified
            _LightTableEditor *editor*.
        """
        raise NotImplementedError

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'actual_size, width, ratio' )
    def _layout_modified ( self ):
        self.update = True

#-------------------------------------------------------------------------------
#  'GridLayout' class:
#-------------------------------------------------------------------------------

class GridLayout ( ImageLayout ):
    """ Manages the layout of ThemedImages arranged in a grid.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The amount of spacing between images:
    spacing = Range( 0, None, 4 )

    # The amount of margin to leave around the edges of the light table:
    margin = Range( 0, None, 4 )

    # The fixed number of rows (or columns if using a vertical layout) to use.
    # A value of 0 means it is calculated based on the value of 'size':
    rows = Int

    #-- Public Methods ---------------------------------------------------------

    def layout ( self, editor ):
        """ Performs a complete layout of the contents of the specified
            _LightTableEditor *editor*.
        """
        images = editor.images
        count  = len( images )
        rows   = self.rows
        if (rows > 0) and (count > 0):
            tdx, tdy = images[0].normal_theme.bounds()
            _, _, dx, dy, sdx, sdy = editor.layout_bounds
            if sdx:
                self._calculate_width( int( dy * self.ratio ), count, tdx, tdy,
                                       dx, editor.scrollbar_size )
            else:
                self._calculate_width( dx, count, tdy, tdx, dy,
                                       editor.scrollbar_size )

        self._assign_sizes( images )
        self._layout( editor )


    def update_layout ( self, editor, start, added, removed ):
        """ Performs an update to an existing layout that begins at the index
            specified by *start* which involves adding and deleting the number
            of images specified by *added* and *removed* for the specified
            _LightTableEditor *editor*.
        """
        self._assign_sizes( editor.images[ start: start + added ] )
        self._layout( editor )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'spacing, margin' )
    def _update_needed ( self ):
        self.update = True

    #-- Private Methods --------------------------------------------------------

    def _assign_sizes ( self, images ):
        """ Assigns the correct size to each of the specified ThemedImage
            *images* based on the current layout settings.
        """
        last_theme  = None
        actual_size = self.actual_size
        if not actual_size:
            idx = self.width
            idy = int( round( idx / self.ratio ) )

        for ti in images:
            theme = ti.normal_theme
            if theme is not last_theme:
                last_theme = theme
                tdx, tdy   = theme.bounds()

            if actual_size:
                image   = ti.image
                ti.size = ( image.width + tdx, image.height + tdy )
            else:
                ti.size = ( idx + tdx, idy + tdy )


    def _calculate_width ( self, dx, count, tdx, tdy, adxy, sbdxy ):
        """ Calculates the 'width' value for the layout based upon the current
            width or height of the control.
        """
        rows, margin, spacing = self.rows, self.margin, self.spacing
        size  = (dx - (2 * margin) - (rows * (spacing + tdy)) + spacing)
        width = max( 16, size / rows )
        n     = (count + rows - 1) / rows
        need  = (2 * margin) + (n * (width + spacing + tdx)) - spacing
        if need > adxy:
            width = max( 16, (size - sbdxy) / rows )

        self.width = width


    def _layout ( self, editor ):
        """ Performs a grid layout on all of the ThemedImages for the specified
            LightTableEditor *editor*.
        """
        if len( editor.images ) > 0:
            x, y, dx, dy, sdx, sdy = editor.layout_bounds
            if not sdx:
                self._layout_rows( editor, x, y, dx, dy )
            elif not sdy:
                self._layout_columns( editor, x, y, dx, dy )
            else:
                self._layout_square( editor, x, y, dx, dy )


    def _layout_rows ( self, editor, x, y, dx, dy ):
        """ Lays out all of the images for the specified LightTableEditor
            *editor* by rows within a grid at origin (*x*,*y*) with maximum
            width *dx* and an unscrolled height of *dy*
        """
        images          = editor.images
        mdx, mdy        = self._max_size( images )
        margin, spacing = self.margin, self.spacing
        s2m             = spacing - (2 * margin)
        columns         = max( 1, (dx + s2m) / (mdx + spacing) )
        if columns > 1:
            rows = ((len( images ) + columns - 1) / columns) * columns
            if ((rows * (mdy + spacing)) - s2m) > dy:
                columns = max( 1, (dx + s2m - editor.scrollbar_size) /
                                  (mdx + spacing) )

        x    += margin
        y    += margin
        i, x0 = 0, x
        for ti in images:
            idx, idy    = ti.size
            ti.position = ( x0 + ((mdx - idx) / 2), y + ((mdy - idy) / 2) )
            x0 += mdx + spacing
            i  += 1
            if i >= columns:
                i, x0 = 0, x
                y    += mdy + spacing


    def _layout_columns ( self, editor, x, y, dx, dy ):
        """ Lays out all of the images for the specified LightTableEditor
            *editor* by columns within a grid at origin (*x*,*y*) with maximum
            height *dy* and an unscrolled width of *dx*.
        """
        images          = editor.images
        mdx, mdy        = self._max_size( images )
        margin, spacing = self.margin, self.spacing
        s2m             = spacing - (2 * margin)
        rows            = max( 1, (dy + s2m) / (mdy + spacing) )
        if rows > 1:
            columns = ((len( images ) + rows - 1) / rows) * rows
            if ((columns * (mdx + spacing)) - s2m) > dx:
                rows = max( 1, (dy + s2m - editor.scrollbar_size) /
                               (mdy + spacing) )

        x    += margin
        y    += margin
        i, y0 = 0, y
        for ti in images:
            idx, idy    = ti.size
            ti.position = ( x + ((mdx - idx) / 2), y0 + ((mdy - idy) / 2) )
            y0 += mdy + spacing
            i  += 1
            if i >= rows:
                i, y0 = 0, y
                x    += mdx + spacing


    def _layout_square ( self, editor, x, y, dx, dy ):
        """ Lays out all of the images for the specified LightTableEditor
            *editor* in a rough square within a grid at origin (*x*,*y*) and an
            unscrolled area of (*dx*,*dy*).
        """
        images   = editor.images
        mdx, mdy = self._max_size( images )
        columns  = max( 1, int( round( (sqrt( len( images ) ) * mdy) / mdx ) ) )
        self._layout_rows( x, y, (2 * self.margin) +
                           (columns * (mdx + self.spacing )) - self.spacing )


    def _max_size ( self, images ):
        """ Returns the maximum width and height of any of the specifed
            ThemedImage *images*.
        """
        dx = dy = 0
        for ti in images:
            idx, idy = ti.size
            dx, dy   = max( dx, idx ), max( dy, idy )

        return ( dx, dy )

#-- LightTableAnimator Animation Types -----------------------------------------

AnimationTypes = [
    'Random', 'Sequential', 'Rotate left', 'Collapse', 'Explode',
    'Rotate right', 'Swap', 'Cycle', 'Vibrate', 'Reverse'
]

#-------------------------------------------------------------------------------
#  'LightTableAnimator' class
#-------------------------------------------------------------------------------

class LightTableAnimator ( HasPrivateFacets ):
    """ Adds simple animation capabilities to the ThemedImages contained within
        a LightTableEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The length of time an animation should last:
    time = Range( 0.3, None, 1.8 )

    # The duty cycle of the RampTweener:
    cycle = Range( 0.0, 1.0, 0.5 )

    # The level of the RampTweener:
    level = Range( 0.0, 1.0, 0.2 )

    # Event fired when the animation should start:
    start = Event

    # Event fired when the animation should stop:
    stop = Event

    # Should animations run repeatedly or just once?
    repeat = Bool( True )

    # The animation type to run:
    type = Enum( *AnimationTypes )

    # The _LightTableEditor the animator is associated with:
    editor = Any # Instance( _LightTableEditor )

    # Is an animation running currently?
    running = Bool( False )

    # The currently running animation:
    animation = Instance( ConcurrentAnimation )

    # The restore information for the currently running animation:
    restore_info = Any # List( ( ThemedImage, start_position, end_position ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _start_set ( self ):
        """ Handles the 'start' event being fired.
        """
        self._stop_set()
        self.running = True
        self._create_animation()


    def _stop_set ( self ):
        """ Handles the stop event being fired.
        """
        self.running = False
        if self.animation is not None:
            self.animation.stop = True


    @on_facet_set( 'animation:stopped' )
    def _animation_stopped ( self ):
        """ Handles the currently running animation being stopped.
        """
        self.animation = None
        for ti, start, end in self.restore_info:
            ti.position = start

        self.restore_info = None

        if self.running:
            if self.repeat:
                self._create_animation()
            else:
                self.running = False


    def _editor_set ( self, editor ):
        if editor is None:
            self.stop = True

    #-- Private Methods --------------------------------------------------------

    def _create_animation ( self ):
        """ Creates and starts a new animation of the current 'type'.
        """
        if len( self.editor.images ) > 0:
            type = self.type
            last = self._last_type
            if type == 'Random':
                while True:
                    type = choice( AnimationTypes[2:] )
                    if type != last:
                        break
            elif type == 'Sequential':
                i = 2
                if last is not None:
                    i2 = AnimationTypes.index( last ) + 1
                    if i2 < len( AnimationTypes ):
                        i = i2

                type = AnimationTypes[ i ]

            self._last_type   = type
            self.restore_info = getattr(
                self, '_%s_animation' % type.lower().replace( ' ', '_' )
            )()

            time = self.time
            rt   = RampTweener( cycle = self.cycle, level = self.level )
            if type == 'Vibrate':
                tweener = CycleTweener( rt, cycles = 9 )
            else:
                tweener = EaseOutEaseInTweener( rt )

            path = choice( Paths )

            self.animation = ConcurrentAnimation( items = [
                ti.animate_facet(
                    'position', time, end, begin,
                    repeat  = 2,
                    path    = path,
                    tweener = tweener,
                    start   = False
                ) for ti, begin, end in self.restore_info ]
            ).run()


    def _rotate_left_animation ( self ):
        """ Returns the animation data for a 'rotate left' animation.
        """
        n = len( self.editor.images )
        m = randint( 1, min( 5, n ) )
        i = range( n )

        return self._animate_to( i[ -m: ] + i[ : n - m ] )


    def _rotate_right_animation ( self ):
        """ Returns the animation data for a 'rotate right' animation.
        """
        n = len( self.editor.images )
        m = randint( 1, min( 5, n ) )
        i = range( n )

        return self._animate_to( i[ m: ] + i[ : m ] )


    def _vibrate_animation ( self ):
        """ Returns the animation data for a 'vibrate' animation.
        """
        result = []
        for ti in self.editor.images:
            x, y = ti.position
            result.append( ( ti, ti.position, ( x + srandint( 5, 15 ),
                                                y + srandint( 5, 15 ) ) ) )

        return result


    def _collapse_animation ( self ):
        """ Returns the animation data for a 'collapse' animation.
        """
        xl, yt, xr, yb = self._bounds()
        cx, cy         = (xl + xr) / 2, (yt + yb) / 2
        result         = []
        for ti in self.editor.images:
            x, y, dx, dy = ti.bounds
            tx, ty       = cx - (dx / 2), cy - (dy / 2)
            t            = 0.8 + (0.2 * random())
            result.append(
                ( ti, ti.position, ( int( round( x + (t * (tx - x)) ) ),
                                     int( round( y + (t * (ty - y)) ) ) ) )
            )

        return result


    def _explode_animation ( self ):
        """ Returns the animation data for a 'explode' animation.
        """
        xl, yt, xr, yb     = self._bounds()
        x, y, dx, dy, _, _ = self.editor.layout_bounds
        xl, yt             = min( xl, x ), min( yt, y )
        xr, yb             = max( xr, x + dx ), max( yb, y + dy )
        cx, cy             = (xl + xr) / 2, (yt + yb) / 2
        result             = []
        for ti in self.editor.images:
            x, y, dx, dy = ti.bounds
            if x <= (cx - (dx / 2)):
                if y <= (cy - (dy / 2)):
                    if random() < 0.5:
                        x, y = xl - (2 * dx), randint( yt - (2 * dy), cy )
                    else:
                        x, y = randint( xl - (2 * dx), cx ), yt - (2 * dy)
                else:
                    if random() < 0.5:
                        x, y = xl - (2 * dx), randint( cy, yb + dy )
                    else:
                        x, y = randint( xl - (2 * dx), cx ), yb + dy
            else:
                if y <= (cy - (dy / 2)):
                    if random() < 0.5:
                        x, y = xr + dx, randint( yt - (2 * dy), cy )
                    else:
                        x, y = randint( cx, xr + dx ), yt - (2 * dy)
                else:
                    if random() < 0.5:
                        x, y = xr + dx, randint( cy, yb + dy )
                    else:
                        x, y = randint( cx, xr + dx ), yb + dy

            result.append( ( ti, ti.position, ( x, y ) ) )

        return result


    def _swap_animation ( self ):
        """ Returns the animation data for a 'swap' animation.
        """
        indices = range( len( self.editor.images ) )
        indices.reverse()

        return self._animate_to( indices )


    def _reverse_animation ( self ):
        """ Returns the animation data for a 'reverse' animation.
        """
        indices = range( len( self.editor.images ) )
        shuffle( indices )

        return self._animate_to( indices )


    def _cycle_animation ( self ):
        """ Returns the animation data for a 'reverse' animation.
        """
        n       = len( self.editor.images )
        indices = range( n )
        if n >= 2:
            m = randint( 2, min( 5, n ) )
            for i in xrange( 0, n, m ):
                items = indices[ i: i + m ]
                if len( items ) > 1:
                    items2 = items[:]
                    while items == items2:
                        shuffle( items2 )

                    indices[ i: i + m ] = items2

        return self._animate_to( indices )


    def _animate_to ( self, indices ):
        """ Returns the animation data for a mapping of the editor's
            current items animating to the current position of a different
            item as specified by the *indices* list.
        """
        ti = self.editor.images

        return [ ( ti[ i ], ti[ i ].position, ti[ indices[ i ] ].position )
                 for i in xrange( len( ti ) ) ]


    def _bounds ( self ):
        """ Returns the bounding box for all of the items currently
            contained in the editor as a tuple of the form: ( left, top,
            right, bottom ).
        """
        xl  = yt =  1000000000
        xr  = yb = -1000000000
        for ti in self.editor.images:
            ix, iy, idx, idy = ti.bounds
            xl = min( xl, ix )
            yt = min( yt, iy )
            xr = max( xr, ix + idx )
            yb = max( yb, iy + idy )

        return ( xl, yt, xr, yb )

#-------------------------------------------------------------------------------
#  '_LightTableEditor' class:
#-------------------------------------------------------------------------------

class _LightTableEditor ( ControlEditor ):
    """ Defines the LightTableEditor for view, selecting and animating lists of
        images.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The logical size of the control (same as virtual_size, but used when
    # scroll bars are not enabled):
    logical_size = Tuple( Int, Int )

    # The logical offset within the control of the first item being displayed
    # (used when scroll bars are not enabled):
    logical_offset = Tuple( Int, Int )

    # The value the control is editing:
    value = List

    # Event fired when the editor view needs to be updated:
    update = Event

    # The list of ThemedImage objects being displayed:
    images = List

    # The most recent ThemedImage used for a mouse event:
    mouse_image = Instance( ThemedImage )

    # The bounds of the available area for laying out ThemeImage items, which is
    # a tuple of the form: ( x, y, dx, dy, sdx, sdy ), where ( x, y, dx, dy ) is
    # the available layout bounds without scrolling, and sdx and sdy are True
    # if the editor can be scrolled in that direction):
    layout_bounds = Property

    # The size of the scrollbar being used:
    scrollbar_size = Int

    #-- ControlEditor Method Overrides -----------------------------------------

    def init ( self ):
        """ Initializes the control.
        """
        factory              = self.factory
        self.scroll_vertical = (factory.scroll != 'horizontal')
        if factory.show_scrollbars:
            self.virtual_size   = ( 10, 10 )
            self.scrollbar_size = (scrollbar_dx if factory.scroll == 'vertical'
                                   else scrollbar_dy)

        animator = factory.animator
        if animator is not None:
            animator.editor = self

        mode = factory.selection_mode
        if mode != 'none':
            editor = self.editor
            if mode == 'item':
                editor.add_facet( 'selected', Instance( ThemedImage ) )
                editor.add_facet( 'selected_value', Any() )
                editor.on_facet_set( self._selected_modified, 'selected' )
                editor.on_facet_set( self._selected_value_modified,
                                     'selected_value' )
                do_later( self._init_item_sync )
            else:
                editor.add_facet( 'selected', List )
                editor.add_facet( 'selected_value', List )
                editor.on_facet_set( self._selected_updated, 'selected[]' )
                editor.on_facet_set( self._selected_value_updated,
                                     'selected_value[]' )
                do_later( self._init_list_sync )


    def dispose ( self ):
        """ Disposes of the contents of the control.
        """
        factory  = self.factory
        animator = factory.animator
        if animator is not None:
            animator.editor = None

        if self.scroll_control is not None:
            self.scroll_control.unset_event_handler(
                size = self._scroller_resize
            )

        mode = factory.selection_mode
        if mode == 'item':
            self.editor.on_facet_set( self._selected_modified, 'selected',
                                      remove = True )
            self.editor.on_facet_set( self._selected_value_modified,
                                      'selected_value', remove = True )
        elif mode == 'items':
            self.editor.on_facet_set( self._selected_updated, 'selected[]',
                                      remove = True )
            self.editor.on_facet_set( self._selected_value_updated,
                                      'selected_value[]', remove = True )

        super( _LightTableEditor, self ).dispose()


    def scroll_by ( self, x = 0, y = 0 ):
        """ Scrolls the contents of the control by the amount specified by *x*
            and *y*.
        """
        if self.scroll_control is not None:
            super( _LightTableEditor, self ).scroll_by( x, y )

            return

        lx, ly   = self.logical_offset
        ldx, ldy = self.logical_size
        dx, dy   = self.control.client_size
        nx       = min( max( lx - x, dx - ldx ), 0 )
        ny       = min( max( ly - y, dy - ldy ), 0 )
        if (nx != lx) or (ny != ly):
            self.logical_offset = ( nx, ny )
            self.refresh()

    #-- Property Implementations -----------------------------------------------

    def _get_layout_bounds ( self ):
        x = y   = 0
        control = self.scroll_control
        if control is None:
            control = self.control

        dx, dy = control.client_size
        theme  = self.theme
        if theme is not None:
            x, y, dx, dy = theme.bounds( 0, 0, dx, dy )

        scroll = self.factory.scroll
        if scroll == 'vertical':
            return ( x, y, dx, dy, False, True )

        if scroll == 'horizontal':
            return ( x, y, dx, dy, True, False )

        return ( x, y, dx, dy, True, True )

    #-- Paint Handlers ---------------------------------------------------------

    def paint_content ( self, g ):
        """ Paints the contents of the custom control.
        """
        is_visible = self.control.is_visible
        lx, ly     = self.logical_offset
        for image in self.images:
            x, y, dx, dy = image.bounds
            if is_visible( x + lx, y + ly, dx, dy ):
                image.paint( g, lx, ly )

    #-- Resize Event Handler ---------------------------------------------------

    def resize ( self, event ):
        """ Handles the control being resized.
        """
        self._update_layout()

        super( _LightTableEditor, self ).resize( event )

    #-- Mouse Event Handlers ---------------------------------------------------

    def normal_left_down ( self, x, y ):
        """ Handles the user pressing the left mouse button.
        """
        self.mouse_image = image = self._find_image_at( x, y )
        if image is not None:
            image.mouse_state = 'down'
            self._xy   = ( x, y )
            self.state = 'drag_pending'
        else:
            self.state = 'ignoring'


    def normal_motion ( self, x, y ):
        """ Handles the user moving the mouse.
        """
        self.mouse_image = self._find_image_at( x, y )
        self._check_hover( x, y )


    def normal_leave ( self ):
        """ Handles the mouse leaving the control.
        """
        self.mouse_image = None
        self._check_hover( -9999, -9999 )


    def ignoring_left_up ( self, x, y ):
        """ Handles the user releasing the left mouse button.
        """
        self.state = 'normal'
        self.normal_motion( x, y )


    def drag_pending_motion ( self, x, y, event ):
        """ Handles the user moving the mouse.
        """
        x0, y0 = self._xy
        if (abs( x - x0 ) + abs( y - y0 )) > 5:
            items = image = self.mouse_image
            if (self.factory.can_drag and
                (not (event.control_down or event.shift_down))):
                self.control.mouse_capture = False
                if image.selected:
                    items = self.editor.selected

                if not isinstance( items, list ):
                    items = [ items ]

                names = [ item.image.name for item in items ]
                self.control.drag( names, 'files', image = image.image )
                image.mouse_state = self.state = 'normal'
            elif self.factory.selection_mode == 'items':
                if event.control_down:
                    del self.editor.selected[:]

                if image.selected:
                    self._unselect_image( image, 'hover' )
                    self.state = 'unselecting'
                else:
                    self._select_image( image, 'hover' )
                    self.state = 'selecting'
            else:
                self.editor.selected = ( image, None )[ image.selected ]
                self.state = 'picking'


    def drag_pending_left_up ( self, x, y, event ):
        """ Handles the user releasing the left mouse button.
        """
        self.mouse_image, image = self._find_image_at( x, y ), self.mouse_image
        image = self._find_image_at( x, y )
        if (image is self.mouse_image) and (image is not None):
            editor = self.editor
            mode   = self.factory.selection_mode
            if mode == 'item':
                if image.selected:
                    editor.selected = None
                else:
                    editor.selected = image
            elif mode == 'items':
                if event.control_down:
                    editor.selected = [ image ]
                elif image.selected:
                    editor.selected.remove( image )
                else:
                    editor.selected.append( image )

            image.mouse_state = 'hover'

        self.state = 'normal'


    def selecting_motion ( self, x, y ):
        """ Handles the user moving the mouse.
        """
        image = self._find_image_at( x, y )
        if image is not self.mouse_image:
            self.mouse_image = image
            self._select_image( image )
            if image is not None:
                image.mouse_state = 'down'


    def selecting_left_up ( self, x, y ):
        """ Handles the user releasing the left mouse button.
        """
        self.mouse_image = self._find_image_at( x, y )
        self.state = 'normal'


    def unselecting_motion ( self, x, y ):
        """ Handles the user moving the mouse.
        """
        image = self._find_image_at( x, y )
        if image is not self.mouse_image:
            self.mouse_image = image
            self._unselect_image( image )
            if image is not None:
                image.mouse_state = 'down'


    def unselecting_left_up ( self, x, y ):
        """ Handles the user releasing the left mouse button.
        """
        self.selecting_left_up( x, y )


    def picking_motion ( self, x, y ):
        """ Handles the user moving the mouse.
        """
        image = self._find_image_at( x, y )
        if image is not self.mouse_image:
            self.mouse_image = image
            if image is not None:
                self.editor.selected = ( image, None )[ image.selected ]


    def picking_left_up ( self, x, y, event ):
        """ Handles the user releasing the left mouse button.
        """
        self.selecting_left_up( x, y )


    def wheel ( self, event ):
        """ Handles the user scrolling the mouse wheel.
        """
        if self.scroll_control is not None:
            super( _LightTableEditor, self ).wheel( event )

            return

        delta = (-event.wheel_change * self.wheel_rate *
                 (1 + (3 * event.shift_down)))
        cd    = event.control_down ^ (not self.scroll_vertical)
        self.scroll_by( delta * cd, delta * (not cd) )


    def alt_wheel ( self, event ):
        """ Handles the user moving the mouse wheel while holding down the 'Alt'
            key by adjusting the layout width or ratio (if the 'Control' key is
            also being held down).
        """
        layout = self.factory.layout
        delta  = event.wheel_change
        if event.control_down:
            try:
                layout.ratio += delta * 0.1 * (1 + (9 * event.shift_down))
            except:
                try:
                    layout.ratio += delta * 0.1
                except:
                    pass
        else:
            try:
                layout.width += delta * (1 + (9 * event.shift_down))
            except:
                try:
                    layout.width += delta
                except:
                    pass

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self ):
        """ Handles the 'value' facet being changed.
        """
        factory = self.factory
        adapter = factory.adapter
        if adapter is None:
            adapter = DefaultThemedImage

        images = []
        for image in self.value:
            if not isinstance( image, ThemedImage ):
                image = adapter( image )

            images.append( image.set( editor = self ) )

        mode = factory.selection_mode
        if mode == 'item':
            self.editor.selected = None
        elif mode == 'items':
            del self.editor.selected[:]

        self.images = images
        factory.layout.layout( self )
        self._update_size()
        self.refresh()


    def _value_items_set ( self, event ):
        """ Handles items being added to or removed from the 'value' facet.
        """
        editor  = self.editor
        images  = self.images
        index   = event.index
        factory = self.factory
        mode    = factory.selection_mode
        adapter = factory.adapter
        if adapter is None:
            adapter = DefaultThemedImage

        removed = len( event.removed )
        for i in xrange( index, index + removed ):
            image        = images[ i ]
            image.editor = None
            if mode == 'item':
                if editor.selected is image:
                    editor.selected = None
            elif (mode == 'items') and (image in editor.selected):
                editor.selected.remove( image )

        added = []
        for image in event.added:
            if not isinstance( image, ThemedImage ):
                image = adapter( image )

            added.append( image.set( editor = self ) )

        images[ index: index + removed ] = added
        factory.layout.update_layout( self, index, len( added ), removed )
        self._update_size()
        self.refresh()


    @on_facet_set( 'factory:layout:update' )
    def _layout_needed ( self ):
        """ Handles a change to any facet that requires a new layout.
        """
        do_later( self._update_layout )


    def _scroll_control_set ( self, control ):
        """ Handles the 'scroll_control' facet being changed.
        """
        if control is not None:
            control.set_event_handler(
                size = self._scroller_resize
            )


    def _selected_modified ( self, old, new ):
        """ Handles the editor's single selection item being changed.
        """
        if old is not None:
            old.selected = False

        if new is not None:
            new.selected = True

        if not self._ignore_update:
            value = new
            if (new is not None) and (new.value is not None):
                value = new.value

            self._ignore_update        = True
            self.editor.selected_value = value
            self._ignore_update        = False


    def _selected_value_modified ( self, new ):
        """ Handles the user's single selection item being changed.
        """
        if not self._ignore_update:
            self._ignore_update  = True
            self.editor.selected = self._image_for( new )
            self._ignore_update  = False


    def _selected_updated ( self, removed, added ):
        """ Handles the editor's multiple item selection being changed.
        """
        for image in removed:
            image.selected = False

        for image in added:
            image.selected = True

        if not self._ignore_update:
            self._ignore_update = True
            self.editor.selected_value = [
                image.value or image for image in self.editor.selected
            ]
            self._ignore_update = False


    def _selected_value_updated ( self ):
        """ Handles the user's multiple item selection being changed.
        """
        if not self._ignore_update:
            image_for           = self._image_for
            editor              = self.editor
            self._ignore_update = True
            editor.selected     = [ image_for( item )
                                    for item in editor.selected_value ]
            self._ignore_update = False


    def _update_set ( self ):
        """ Handles the 'update' event being fired.
        """
        self.refresh()


    def _mouse_image_set ( self, old, new ):
        """ Handles the 'mouse_image' facet being changed.
        """
        if old is not None:
            old.mouse_state = 'normal'

        if new is not None:
            new.mouse_state = 'hover'

    #-- Private Methods --------------------------------------------------------

    def _find_image_at ( self, x, y ):
        """ Returns the ThemedImage at the location (*x*,*y*). Returns None if
            no image is at the specified location.
        """
        lx, ly = self.logical_offset
        x     -= lx
        y     -= ly
        for image in self.images:
            if image.is_in( x, y ):
                return image

        return None


    def _image_for ( self, value ):
        """ Returns the ThemedImage corresponding to the specified *value*.
        """
        for image in self.images:
            if value == image.value:
                return image

        return None


    def _check_hover ( self, x, y ):
        """ Checks to see if the current image should display a hover popup, or
            if the current hover popup (if any) should be closed.
        """
        hdx, hdy = self.factory.hover_size
        if (hdx > 0) and (hdy > 0):
            if self._hover_info is not None:
                image, hx, hy, ui = self._hover_info
                if (abs( x - hx ) + abs( y - hy )) > 7:
                    self._hover_info = None
                    ui.dispose()

            self._hover_data = None
            image            = self.mouse_image
            if image is not self._hover_last:
                self._hover_last = None
                if image is not None:
                    idx, idy = image.size
                    if (image.image.width > idx) or (image.image.height > idy):
                        self._hover_data = ( image, x, y )
                        do_after( 100, self._hover_pending )


    def _hover_pending ( self ):
        """ Checks to see if the user is still hovering over an image, and if
            so, display the hover popup.
        """
        if self._hover_data is not None:
            image, x, y      = self._hover_data
            self._hover_last = image
            self._hover_data = None
            hdx, hdy         = self.factory.hover_size
            bx, by, bdx, bdy = image.bounds
            lx, ly           = self.logical_offset
            sx, sy           = self.control.screen_position
            self._hover_info = ( image, x, y, image.edit_facets(
                view = View(
                    VGroup(
                        UItem( 'image',
                               width  = -hdx,
                               height = -hdy,
                               editor = ImageEditor()
                        ),
                        group_theme = '@std:popup?l60'
                    ),
                    kind         = 'popup',
                    popup_bounds = ( sx + bx + lx, sy + by + ly, bdx, bdy )
                ) )
            )


    def _scroller_resize ( self, event ):
        """ Handles the scroller control being resized.
        """
        self._update_layout()
        event.handled = False


    def _update_layout ( self ):
        """ Updates the layout of the images being edited.
        """
        self.factory.layout.layout( self )
        self._update_size()
        self.refresh()


    def _update_size ( self ):
        """ Updates the virtual size of the editor canvas based upon the bounds
            of all the items it contains.
        """
        xr = yb = -1000000000
        for image in self.images:
            x, y, dx, dy = image.bounds
            xr = max( xr, x + dx )
            yb = max( yb, y + dy )

        dx, dy = max( 10, xr ), max( 10, yb )

        theme = self.theme
        if theme is not None:
            tdx, tdy = theme.bounds()
            dx      += tdx
            dy      += tdy

        if self.scroll_control is None:
            self.logical_size = ( dx, dy )
            self.scroll_by( 0, 0 )
        else:
            self.virtual_size = ( dx, dy )


    def _select_image ( self, image, state = 'normal' ):
        """ Adds a specified ThemedImage *image* to the editor selection.
        """
        if image is not None:
            image.mouse_state = state
            if not image.selected:
                self.editor.selected.append( image )


    def _unselect_image ( self, image, state = 'normal' ):
        """ Removes a specified ThemedImage *image* from the editor selection.
        """
        if image is not None:
            image.mouse_state = state
            if image.selected:
                self.editor.selected.remove( image )


    def _init_item_sync ( self ):
        self.editor.sync_value( self.factory.selected, 'selected_value' )


    def _init_list_sync ( self ):
        self.editor.sync_value( self.factory.selected, 'selected_value',
                                is_list = True )

#-------------------------------------------------------------------------------
#  'LightTableEditor' class:
#-------------------------------------------------------------------------------

class LightTableEditor ( CustomControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The custom control editor class:
    klass = _LightTableEditor

    # The selection mode to use:
    selection_mode = Enum( 'none', 'item', 'items' )

    # The extended facet name for the current selection:
    selected = Str

    # Are the images draggable (i.e. support "drag and drop")?
    can_drag = Bool( False )

    # Adapter function for converting image names or ImageResource objects to
    # ThemedImages:
    adapter = Callable

    # The image layout manager to use:
    layout = Instance( ImageLayout, GridLayout, () )

    # The animator to use:
    animator = Instance( LightTableAnimator )

    # What directions are the editor scrollable in:
    scroll = Enum( 'vertical', 'horizontal', 'both' )

    # Should scroll bars be displayed?
    show_scrollbars = Bool( True )

    # The size of the hover popup to display when the mouse hovers over an
    # image and the image is larger than the image displayed in the editor. If
    # either the x or y size is <= 0, no hover popup is displayed:
    hover_size = Tuple( Int, Int, facet_value = True )

    # The background theme used by the editor:
    theme = Theme( '@xform:b', content = 0 )

#-- EOF ------------------------------------------------------------------------
