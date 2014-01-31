"""
Defines the SlideshowEditor for displaying a series of images using a slide show
format.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from random \
    import randint, shuffle

from facets.api \
    import Image, Instance, Str, Int, Float, Bool, List, Either, Enum, Any, \
           Property, ATheme, Theme, on_facet_set

from facets.animation.api \
    import FacetAnimation, ImageTransition, PushImageTransition, \
           WipeImageTransition, FadeImageTransition

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.pyface.timer.api \
    import do_later

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The maximum allowed number of entries in the editor history:
MaxHistory = 20

# Default transitions:
fade_black = FadeImageTransition( style     = 'black' )
fade_white = FadeImageTransition( style     = 'white' )
push_left  = PushImageTransition( direction = 'left'  )
push_right = PushImageTransition( direction = 'right' )
push_up    = PushImageTransition( direction = 'up'    )
push_down  = PushImageTransition( direction = 'down'  )

# Mapping from string names to standard image transitions:
StandardTransitions = {
    'fade':       FadeImageTransition(),
    'fade_black': fade_black,
    'fade_white': fade_white,
    'black':      fade_black,
    'white':      fade_white,
    'push_left':  push_left,
    'push_right': push_right,
    'push_up':    push_up,
    'push_down':  push_down,
    'left':       push_left,
    'right':      push_right,
    'up':         push_up,
    'down':       push_down,
    'wipe_left':  WipeImageTransition( direction = 'left'  ),
    'wipe_right': WipeImageTransition( direction = 'right' ),
    'wipe_up':    WipeImageTransition( direction = 'up'    ),
    'wipe_down':  WipeImageTransition( direction = 'down'  )
}

# The default list of ImageTransitions to use if the user doesn't specify any:
default_transitions = [
    'fade_black', 'push_left',   'fade_black', 'push_down',
    'fade_black', 'push_right',  'fade_black', 'push_up'
]

#-------------------------------------------------------------------------------
#  '_SlideshowEditor' class:
#-------------------------------------------------------------------------------

class _SlideshowEditor ( ControlEditor ):
    """ Defines the SlideshowEditor for displaying a series of images using a
        slide show format.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of images to display in the slide show:
    value = List # ( Image )

    # The current 'source' image (original and scaled/cropped):
    original_image_0 = Image
    image_0          = Image

    # The current 'destination' image (original and scaled/cropped):
    original_image_1 = Image
    image_1          = Image

    # The current image transition being used:
    image_transition = Instance( ImageTransition )

    # The list of available image transitions:
    transitions = Property

    # The animation object driving the image transition:
    animation = Instance( FacetAnimation )

    # The current list of image indices being shown:
    image_indices = List # ( Int )

    # The current list of image transition indices being used:
    transition_indices = List # ( Int )

    # The history of images displayed:
    history = List # ( Int )

    # The current index into the history:
    history_index = Int

    # The index of the current image being displayed:
    current_index = Int

    # The current 'image_indices' index:
    image_index = Int

    # The current 'transition_indices' index:
    transition_index = Int

    # The current 'hold' animation time:
    time = Float

    # Are we currently holding?
    holding = Bool( False )

    # Is the slideshow currently paused?
    paused = Bool( False )

    # Can an image be selected?
    selectable = Bool( False )

    # The current button state:
    button = Enum( None, 'previous', 'pause', 'next', 'link', 'over' )

    # The current nominal button size:
    button_size = Int

    # Is a value recalibration pending?
    value_pending = Bool( False )

    # Is a resize recalibration pending?
    resize_pending = Bool( False )

    # Temporary image used when rescaling images:
    temp_image = Image

    # The current bounds of the image transition region:
    image_bounds = Any # Tuple( Int, Int, Int, Int )

    # The images used to draw the various slideshow buttons:
    button_rounded  = Image
    button_previous = Image
    button_next     = Image
    button_pause    = Image
    button_play     = Image
    button_link     = Image

    #-- Property Implementations -----------------------------------------------

    def _get_transitions ( self ):
        transitions = self.factory.transitions
        if isinstance( transitions, basestring ):
            transitions = [ item.strip() for item in transitions.split( ',' ) ]

        if isinstance( transitions, list ) and (len( transitions ) > 0):
            return transitions

        return default_transitions

    #-- Public Methods ---------------------------------------------------------

    def dispose ( self ):
        self._stop_animation()

        super( _SlideshowEditor, self ).dispose()

    #-- Paint Handler ----------------------------------------------------------

    def paint_content ( self, g ):
        """ Paints the contents of the custom control.
        """
        self._value_update()
        self._resize_update()

        frame        = self.factory.frame
        x, y, dx, dy = self.content_bounds
        frame.fill( g, x, y, dx, dy )
        if frame.has_label:
            image = self.original_image_0
            if self.image_transition.time >= 0.5:
                image = self.original_image_1

            frame.draw_label( g, image.name, None, x, y, dx, dy )

        ix, iy, idx, idy = self.image_bounds = frame.bounds( x, y, dx, dy )
        self.image_transition.paint( g, ix, iy )
        button = self.button
        if button is not None:
            bs = self.button_size
            yt = iy + ((idy - bs) / 2)
            xm = ix + ((idx - bs) / 2)
            self._draw_button( g, xm, yt, ( self.button_pause,
                                            self.button_play ) [ self.paused ],
                               button == 'pause' )
            if self.paused:
                self._draw_button( g, ix + idx - bs - 2, yt, self.button_next,
                                   button == 'next' )

                if self.history_index > 0:
                    self._draw_button( g, ix + 2, yt, self.button_previous,
                                       button == 'previous' )

                if self.selectable:
                    self._draw_button( g, xm, iy + idy - bs - 2,
                                       self.button_link, button == 'link' )

    #-- Resize Handler ---------------------------------------------------------

    def resize ( self, event ):
        """ Handles the control being resized.
        """
        self.resize_pending = True

        super( _SlideshowEditor, self ).resize( event )

    #-- Mouse Event Handlers ---------------------------------------------------

    def motion ( self, x, y ):
        """ Handles the mouse moving within the control.
        """
        button           = None
        ix, iy, idx, idy = self.image_bounds
        if self._is_in( x, y, ix, iy, idx, idy ):
            self.button_size = bs = self._button_size( idx, idy )
            if bs > 0:
                button = 'over'
                yt     = iy + ((idy - bs) / 2)
                xm     = ix + ((idx - bs) / 2)
                if self._is_in( x, y, xm, yt, bs, bs ):
                    button = 'pause'
                elif self.paused:
                    if self._is_in( x, y, ix + idx - bs - 2, yt, bs, bs ):
                        button = 'next'
                    elif self._is_in( x, y, ix + 2, yt, bs, bs ):
                        if self.history_index > 0:
                            button = 'previous'
                    elif (self.selectable and
                          self._is_in( x, y, xm, iy + idy - bs - 2, bs, bs )):
                        button = 'link'

        self.button = button


    def left_up ( self, x, y ):
        """ Handles the user releasing the left mouse button.
        """
        self.motion( x, y )
        handler = getattr( self, '_click_%s' % self.button, None )
        if handler is not None:
            handler()

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the 'control' facet being changed.
        """
        if control is not None:
            self.selectable = (self.factory.selected != '')
            if self.selectable:
                self.editor.add_facet(  'selected', Any )
                self.editor.sync_value( self.factory.selected, 'selected' )


    def _value_set ( self ):
        """ Handles the 'value' facet being changed.
        """
        del self.history[:]
        self.history_index = 0
        self.value_pending = True


    @on_facet_set( 'image_transition:time' )
    def _time_modified ( self ):
        self.refresh()


    @on_facet_set( 'animation:stopped' )
    def _animation_done ( self ):
        """ Handles the current animation being completed.
        """
        do_later( self._next_animation )


    def _button_set ( self ):
        """ Handles the 'button' facet being changed.
        """
        self.refresh()


    def _button_size_set ( self, bs ):
        """ Handles the current nominal 'button_size' facet being changed.
        """
        if bs > 0:
            bs2 = int( round( 0.8 * bs ) )
            bf  = self._button_for
            bf( 'rounded', bs )
            for button in ( 'previous', 'next', 'pause', 'play', 'link' ):
                bf( button, bs2 )

    #-- Private Methods --------------------------------------------------------

    def _next_animation ( self ):
        """ Initiates the next animation cycle.
        """
        if not self.paused:
            if self.holding:
                self._start_transition()
            else:
                self._start_hold()


    def _value_update ( self ):
        """ Performs required updates after the editor value has changed.
        """
        if self.value_pending:
            self.value_pending = False
            self._stop_animation()
            self.current_index = self.image_index = self.transition_index = -1
            self._prepare_images()
            self._prepare_transitions()
            self._next_image()
            self._start_hold()


    def _resize_update ( self ):
        """ Performs required updates after the control is resized.
        """
        if self.resize_pending:
            self.resize_pending = False
            self.image_0        = self._resize_image( self.original_image_0 )
            self.image_1        = self._resize_image( self.original_image_1 )
            self._init_image_transition()


    def _prepare_images ( self ):
        """ Prepares the images for display.
        """
        factory       = self.factory
        image_indices = range( len( self.value ) )
        if factory.image_order == 'shuffle':
            shuffle( image_indices )

        self.image_indices = image_indices

        return 0


    def _next_image ( self ):
        """ Selects the next image to use.
        """
        history = self.history
        if self.history_index < (len( history ) - 1):
            self.history_index += 1
            self._select_image_at( history[ self.history_index ] )
        else:
            n = len( self.image_indices )
            if self.factory.image_order == 'random':
                image_index = randint( 0, n - 1 )
            else:
                image_index = self.image_index + 1
                if image_index >= n:
                    image_index = self._prepare_images()

                self.image_index = image_index

            index = self.image_indices[ image_index ]
            if (index == self.current_index) and (n > 1):
                self._next_image()
            else:
                self._select_image_at( index )
                history.append( index )
                if len( history ) > MaxHistory:
                    del history[ : -MaxHistory ]

                self.history_index = len( history ) - 1


    def _select_image_at ( self, index ):
        """ Selects the image at the specified *index*.
        """
        self.current_index    = index
        self.original_image_0 = self.original_image_1
        self.original_image_1 = self.value[ index ]
        self.image_0          = self.image_1
        self.image_1          = self._resize_image( self.original_image_1 )


    def _prepare_transitions ( self ):
        """ Prepares the image transitions to use.
        """
        transition_indices = range( len( self.transitions ) )
        if self.factory.transition_order == 'shuffle':
            shuffle( transition_indices )

        self.transition_indices = transition_indices

        return 0


    def _next_transition ( self ):
        """ Selects the next image transition to use.
        """
        n = len( self.transition_indices )
        if self.factory.transition_order == 'random':
            transition_index = randint( 0, n - 1 )
        else:
            transition_index = self.transition_index + 1
            if transition_index >= n:
                transition_index = self._prepare_transitions()

        self.transition_index = transition_index
        transition = self.transitions[
                         self.transition_indices[ transition_index ] ]
        if isinstance( transition, basestring ):
            transition = StandardTransitions.get( transition, fade_black )

        self.image_transition = transition.clone()
        self._init_image_transition()


    def _init_image_transition ( self ):
        """ Initializes the current image transition.
        """
        self.image_transition.set(
            image_0 = self.image_0,
            image_1 = self.image_1
        )


    def _resize_image ( self, image ):
        """ Resizes the specified *image* to fit within the current slideshow
            image frame.
        """
        if image is not None:
            factory      = self.factory
            idx, idy     = image.width, image.height
            x, y, dx, dy = factory.frame.bounds( *self.content_bounds )
            scale        = min( float( dx ) / idx, float( dy ) / idy )
            if (scale < 1.0) or ((scale > 1.0) and (factory.mode == 'zoom')):
                image = image.scale( scale )

            idx, idy = image.width, image.height
            if (idx != dx) or (idy != dy):
                self.temp_image = ( dx, dy )
                g       = self.temp_image.graphics
                g.pen   = None
                g.brush = factory.frame.bg_color
                g.draw_rectangle( 0, 0, dx, dy )
                g.draw_bitmap( image.bitmap, (dx - idx) / 2, (dy - idy) / 2 )
                image = self.temp_image

        return image


    def _start_hold ( self ):
        """ Starts the 'hold' animation cycle.
        """
        self._next_image()
        self._next_transition()
        self.holding   = True
        self.animation = self.animate_facet(
            'time', self.factory.hold, 1.0, 0.0
        )


    def _start_transition ( self ):
        """ Starts the 'transition' animation cycle.
        """
        self.holding   = False
        self.animation = self.image_transition.animate_facet(
            'time', self.factory.transition, 1.0, 0.0
        )


    def _stop_animation ( self ):
        """ Stops any currently running editor animation.
        """
        animation = self.animation
        if animation is not None:
            self.animation = None
            animation.halt()


    def _button_size ( self, dx, dy ):
        """ Computes the nominal 'button' size for the control based upon the
            specified size (*dx*,*dy*).
        """
        size = (min( dx, dy ) / 3) - 4

        return (min( size, 96 ) * (size >= 20))


    def _is_in ( self, x, y, xl, yt, dx, dy ):
        """ Returns whether or not the point (*x*,*y) is contained in the region
            specified by (*xl*,*yt*,*dx*,*dy*).
        """
        return ((xl <= x < (xl + dx)) and (yt <= y < (yt + dy)))


    def _button_for ( self, name, size ):
        """ Creates a new button image for the button named *name* at the size
            specified by *size*.
        """
        self.temp_image = '@xform:%s%s' % (
                          name, ( '?L50', '?H57S62' )[ name != 'rounded' ] )
        setattr( self, 'button_' + name, self.temp_image.scale( ( 0, size ) ) )


    def _draw_button ( self, g, x, y, image, hover ):
        """ Draws the specified *image* button at the specified (*x*,*y*)
            location. If *hover* is True, the button is drawn as the current
            button the mouse is hovering over.
        """
        bs = self.button_size
        if hover:
            g.opacity = 1.0
            g.draw_bitmap( self.button_rounded.bitmap, x, y )
        else:
            g.opacity = 0.33

        g.draw_bitmap( image.bitmap, x + ((bs - image.width)  / 2),
                                     y + ((bs - image.height) / 2) )


    def _click_pause ( self ):
        """ Handles the user clicking the 'pause/play' button.
        """
        self.paused = not self.paused
        self.refresh()
        self._next_animation()


    def _click_link ( self ):
        """ Handles the user clicking the 'link' button.
        """
        self.editor.selected = self.original_image_0


    def _click_next ( self ):
        """ Handles the user clicking the 'next' button.
        """
        self._next_image()
        self._init_image_transition()
        self.refresh()


    def _click_previous ( self ):
        """ Handles the user clicking the 'previous' button.
        """
        self.history_index -= 1
        self._select_image_at( self.history[ self.history_index ] )
        self._init_image_transition()
        self.refresh()

#-------------------------------------------------------------------------------
#  'SlideshowEditor' class:
#-------------------------------------------------------------------------------

class SlideshowEditor ( CustomControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The custom control editor class:
    klass = _SlideshowEditor

    # The extended facet name for the currently selected image:
    selected = Str

    # The theme to use for the background:
    theme = Theme( '@tiles:FibreBoard1.jpg', content = 20, tiled = True )

    # The theme to use for the image frame:
    frame = ATheme( Theme( '@xform:photob?L5s|h40H60',
                           content = 5,
                           label   = ( -8, -8, 1, 5 ) ) )

    # The list of ImageTransition objects to use for switching between images:
    transitions = Either( Str, List ) # ( ImageTransition )

    # The transition time between images:
    transition = Float( 0.5 )

    # The hold time between images:
    hold = Float( 1.5 )

    # The order in which to display the images:
    image_order = Enum( 'normal', 'random', 'shuffle' )

    # The order in which to use the image transitions:
    transition_order = Enum( 'normal', 'random', 'shuffle' )

    # Are images always scaled to fit the frame (zoom) or only downscaled when
    # necessary (fit):
    mode = Enum( 'fit', 'zoom' )

#-- EOF ------------------------------------------------------------------------
