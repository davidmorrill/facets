#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import splitext

from time \
    import time

from random \
   import uniform, randint, choice

from math \
    import sin, cos, pi, sqrt

from colorsys \
    import rgb_to_hls, hls_to_rgb

from facets.api \
    import HasFacets, Tuple, Float, Int, Any, Str, Range, List, Instance,   \
           Event, Bool, RGBFloat, Image, Theme, Property, Button, View,     \
           Tabbed, HGroup, VGroup, HSplit, Item, UItem, RangeSliderEditor,  \
           RangeEditor, HLSColorEditor, VerticalNotebookEditor, GridEditor, \
           LightTableEditor, property_depends_on, on_facet_set, spring

from facets.core.facet_db \
    import facet_db

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.pen \
    import Pen

from facets.ui.image \
    import ImageLibrary

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.editors.light_table_editor \
    import GridLayout, ThemedImage, HLSATransform

from facets.animation.api \
    import Clock

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Degrees to radians conversion factor:
d2r = (2.0 * pi) / 360.0

# Set of valid image file types:
ImageTypes = ( '.png', '.jpg', '.jpeg' )

# The database key prefix used to identify this application:
ParticlesKey = 'facets.extra.demo.ui.Graphics_and_Animation.Particles'

#-------------------------------------------------------------------------------
#  Global data:
#-------------------------------------------------------------------------------

# Global image cache mapping { ( image, scale ): scaled_image }:
image_cache = {}

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def sitem ( name, low, high, increment = 1 ):
    """ Returns a custom Item using a RangeSliderEditor with the specified
        *low*, *high* and *increment* values.
    """
    return Item( name,
        width  = -100,
        editor = RangeSliderEditor( low = low, high = high,
                                    increment = increment, body_style = 25 )
    )


def ir ( n ):
    """ Returns a float value rounded and converted to the nearest integer
        value.
    """
    return int( round( n ) )


def image_for ( image, scale ):
    """ Returns a version of the specified *image* scaled to the specified
        *scale* value. The result is cached for faster access the next time the
        same image and scale value are needed.
    """
    global image_cache

    key          = ( image, scale )
    scaled_image = image_cache.get( key )
    if scaled_image is None:
        image_cache[ key ] = scaled_image = image.scale( scale / 100.0 )

    return scaled_image

#-------------------------------------------------------------------------------
#  'Particle' class:
#-------------------------------------------------------------------------------

class Particle ( HasFacets ):
    """ Defines a single particle.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Current lifespan time (0.0 .. 1.0):
    t = Property

    # Is the particle still alive?
    alive = Property

    # The current system time:
    time = Float

    # The time the particle was 'born':
    time0 = Float

    # The time the particle will 'die':
    time1 = Float

    # The current position of the particle:
    position = Property

    # The starting position of the particle:
    position0 = Tuple( Float, Float )

    # The velocity vector for the particle:
    velocity = Tuple( Float, Float )

    # The gravity vector for the particle:
    gravity = Tuple( Float, Float )

    # The (optional) image used to render the particle:
    image = Image( '@particles:circle1' )

    # The current color of the particle:
    color = Property

    # The starting color of the particle:
    color0 = Tuple

    # The ending color of the particle:
    color1 = Tuple

    # The current opacity of the particle:
    opacity = Property

    # The starting opacity of the particle:
    opacity0 = Float

    # The ending opacity of the particle:
    opacity1 = Float

    # The current size of the particle:
    size = Property

    # The starting size of the particle:
    size0 = Float

    # The ending size of the particle:
    size1 = Float

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'time' )
    def _get_t ( self ):
        return (self.time - self.time0) / ( self.time1 - self.time0)


    def _get_alive ( self ):
        return (self.time <= self.time1)


    def _get_position ( self ):
        x0, y0 = self.position0
        vx, vy = self.velocity
        gx, gy = self.gravity
        dt     = self.time - self.time0
        return ( x0 + (dt * (vx + (gx * dt))),
                 y0 + (dt * (vy + (gy * dt))) )


    def _get_color ( self ):
        h0, l0, s0 = self.color0
        h1, l1, s1 = self.color1
        t          = self.t
        r, g, b    = hls_to_rgb( h0 + ((h1 - h0) * t),
                                 l0 + ((l1 - l0) * t),
                                 s0 + ((s1 - s0) * t) )
        return ( ir( r * 255.0 ), ir( g * 255.0 ), ir( b * 255.0 ) )


    def _get_opacity ( self ):
        return (self.opacity0 + ((self.opacity1 - self.opacity0) * self.t))


    def _get_size ( self ):
        return (self.size0 + ((self.size1 - self.size0) * self.t))

#-------------------------------------------------------------------------------
#  'ParticleSystem' class:
#-------------------------------------------------------------------------------

class ParticleSystem ( HasFacets ):
    """ Defines a complete system of particles.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current list of active particles:
    particles = Any( [], transient = True )

    # The corners of the rectangle used to generate new particles from:
    position0 = Tuple( 0.0, 0.0 )
    position1 = Tuple( 0.0, 0.0 )

    # The range of velocity angles that new particles can be generated with:
    velocity_angle = Tuple( 60, 120 )

    # The range of velocites that new particles can be generated with:
    velocity = Tuple( 100.0, 150.0 )

    # The range of gravity angles that new particles can be generated with:
    gravity_angle = Tuple( 270, 270 )

    # The range of gravity values that new particles can be generated with:
    gravity = Tuple( 30.0, 30.0 )

    # The range of starting sizes that new particles can be generated with:
    start_size = Tuple( 8.0, 12.0 )

    # The range of ending sizes that new particles can be generated with:
    end_size = Tuple( 15.0, 75.0 )

    # The starting color that new particles are generated with:
    start_color = RGBFloat( 0xFF0000 )

    # The ending color that new particles are generated with:
    end_color = RGBFloat( 0x0000FF )

    # The background color to use for the system:
    bg_color = RGBFloat( 0x000000 )

    # The range of starting opacities that new particles can be generated with:
    start_opacity = Tuple( 0.9, 0.9 )

    # The range of ending opacities that new particles can be generated with:
    end_opacity = Tuple( 0.0, 0.0 )

    # The range of lifetime values that new particles can be generated with:
    lifetime = Tuple( 4.0, 7.0 )

    # The spawn rate for creating new particles (in particles/second):
    spawn_rate = Range( 0, 500, 25 )

    # The name of the most recent image added to the system (via drag and drop):
    image_name = Str

    # The most recent image added to the system (via drag and drop):
    image = Image( transient = True )

    # The list of images that new particles can be generated with:
    images = List

    # The event fired when the user wants to clear out the current image list:
    clear_images = Button( '@icons2:Delete' )

    # The fractional residue for the next created particle:
    residual_spawn = Float( transient = True )

    # The time of the last system update:
    last_time = Float( transient = True )

    # The animation clock used to drive the system:
    clock = Any( Clock(), transient = True )

    # The event fired when the display of the system needs to be refreshed:
    refresh = Event

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            sitem( 'velocity',        0.0, 1000.0, 1.0 ),
            sitem( 'velocity_angle',  0, 360, 1 ),
            '_',
            sitem( 'gravity',         0.0, 1000.0, 1.0 ),
            sitem( 'gravity_angle',   0, 360, 1 ),
            '_',
            sitem( 'start_size',      0.0, 200.0, 1.0 ),
            sitem( 'end_size',        0.0, 200.0, 1.0 ),
            '_',
            Item( 'start_color',
                  editor = HLSColorEditor( edit      = 'hue',
                                           cell_size = 9,
                                           cells     = 5 ) ),
            Item( 'end_color',
                  editor = HLSColorEditor( edit      = 'hue',
                                           cell_size = 9,
                                           cells     = 5 ) ),
            Item( 'bg_color',
                  editor = HLSColorEditor( edit      = 'lightness',
                                           cell_size = 9,
                                           cells     = 5 ) ),
            '_',
            sitem( 'start_opacity',   0.0, 1.0, 0.01 ),
            sitem( 'end_opacity',     0.0, 1.0, 0.01 ),
            '_',
            sitem( 'lifetime',        0.1, 20.0, 0.1 ),
            Item( 'spawn_rate', editor = RangeEditor( body_style = 25 ) ),
            HGroup(
                spring,
                UItem( 'clear_images', tooltip = 'Clear all current images' ),
                group_theme = '@xform:b?L15'
            )
        )

    #-- Facet Default Values ---------------------------------------------------

    def _last_time_default ( self ):
        return self.clock.time

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        self.clock.on_facet_set( self._timer_update, 'time' )

    #-- Public Methods ---------------------------------------------------------

    def clone ( self ):
        """ Returns a clone of the particle system.
        """
        return self.__class__( **self.get( 'position0', 'position1',
            'velocity_angle', 'velocity', 'gravity_angle', 'gravity',
            'start_size', 'end_size', 'start_color', 'end_color', 'bg_color',
            'start_opacity', 'end_opacity', 'lifetime', 'spawn_rate', 'images' )
        )


    def dispose ( self ):
        """ Dispose of the object.
        """
        self.clock.on_facet_set( self._timer_update, 'time', remove = True )
        del self.particles[:]

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'clock:time' )
    def _timer_update ( self ):
        """ Handles the animation clock timer being updated.
        """
        time      = self.clock.time
        particles = self.particles
        for i in xrange( len( particles ) - 1, -1, -1 ):
            particle      = particles[ i ]
            particle.time = time
            if not particle.alive:
                del particles[ i ]

        spawn               = ((self.spawn_rate * (time - self.last_time)) +
                                self.residual_spawn)
        create              = ir( spawn )
        self.residual_spawn = spawn - create
        self.last_time      = time
        for i in xrange( create ):
            particles.append( self._create_particle( time ) )

        self.refresh = True


    def _image_name_set ( self, image_name ):
        """ Handles a new image being dragged and dropped onto the system.
        """
        hue = ''
        h   = '%.2f' % rgb_to_hls( *self.start_color )[0]
        if h != '0.00':
            hue = '?H' + h[-2:].lstrip( '0' )

        self.image = image_name + hue


    def _image_set ( self, image ):
        """ Handles a new image being dragged and dropped onto the system.
        """
        self.images.append( image )


    def _clear_images_set ( self ):
        """ Handles the 'clear_images' event being fired.
        """
        del self.images[:]

    #-- Private Methods --------------------------------------------------------

    def _create_particle ( self, time ):
        """ Creates and returns a new particle to be added to the system.
        """
        particle = Particle(
            time      = time,
            time0     = time,
            time1     = time + uniform( *self.lifetime ),
            position0 = self._random_position(),
            velocity  = self._random_velocity(),
            gravity   = self._random_gravity(),
            color0    = rgb_to_hls( *self.start_color ),
            color1    = rgb_to_hls( *self.end_color ),
            opacity0  = uniform( *self.start_opacity ),
            opacity1  = uniform( *self.end_opacity ),
            size0     = uniform( *self.start_size ),
            size1     = uniform( *self.end_size )
        )
        if len( self.images ) > 0:
            particle.image = choice( self.images )

        return particle


    def _random_position ( self ):
        """ Returns a random starting position for a new particle.
        """
        x0, y0 = self.position0
        x1, y1 = self.position1

        return ( uniform( x0, x1 ), uniform( y0, y1 ) )


    def _random_velocity ( self ):
        """ Returns a random starting velocity for a new particle.
        """
        return self._random_radial( self.velocity_angle, self.velocity )


    def _random_gravity ( self ):
        """ Returns a random gravity vector for a new particle.
        """
        return self._random_radial( self.gravity_angle, self.gravity )


    def _random_radial ( self, angle_range, radius_range ):
        """ Returns a random vector for the range of angles and radii specified
            by *angle_range* and *radius_range*.
        """
        angle  = randint( *angle_range )
        radius = uniform( *radius_range )

        return ( radius * cos( angle * d2r ), -radius * sin( angle * d2r ) )

#-------------------------------------------------------------------------------
#  'ParticleSystems' class:
#-------------------------------------------------------------------------------

class ParticleSystems ( HasFacets ):
    """ Defines a collection of particle systems.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of active particle system:
    systems = List # ( ParticleSystem )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'systems',
               editor = VerticalNotebookEditor( multiple_open = True,
                                                scrollable    = True )
        )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _systems_default ( self ):
        return [ ParticleSystem( position0 = ( 200.0, 250.0 ),
                                 position1 = ( 300.0, 300.0 ) ),
                 ParticleSystem( position0 = ( 500.0, 250.0 ),
                                 position1 = ( 600.0, 300.0 ) ) ]

    #-- Public Methods ---------------------------------------------------------

    def add_system ( self, x, y, system = None ):
        """ Adds a new particle system centered at the specified (x,y) point.
        """
        if system is None:
            system = ParticleSystem( position0 = ( x - 50.0, y - 25.0 ),
                                     position1 = ( x + 50.0, y + 25.0 ) )
        else:
            system = system.clone()

        self.systems.append( system )

        return system


    def remove_system ( self, system ):
        """ Removes the particle system spewcified by *system*.
        """
        self.systems.remove( system )


    def dispose ( self ):
        """ Dispose of the object.
        """
        for system in self.systems:
            system.dispose()

#-------------------------------------------------------------------------------
#  '_ParticleSystemsEditor' class:
#-------------------------------------------------------------------------------

class _ParticleSystemsEditor ( ControlEditor ):
    """ Defines the custom editor control for displaying a ParticleSystems
        object containing multiple particle systems.
    """

    #-- Facet Definitions ------------------------------------------------------

    #virtual_size = ( 1000, 1000 )

    # Should the position of each particle system's creation rectangle be
    # displayed (for editing and drag and drop purposes)?
    show_positions = Bool( False )

    # The current frame/second being displayed:
    fps = Float

    # The current fraction of each second being spent drawing:
    dts = Float

    # The current time the most recent drame starting rendering at:
    time = Float

    # The cumulative time spent in the drawing code:
    draw_time = Float

    # The number of frames rendered since the last frames/second calculation:
    frames = Int

    # The last background color used:
    bg_color = RGBFloat

    # The current particle system creation rectangle being dragged over:
    drop_system = Any

    #-- ThemedWindow Event Handlers --------------------------------------------

    def paint_content ( self, g ):
        """ Paints the contents of the editor control.
        """
        now      = time()
        g.pen    = None
        bg_color = None
        for system in self.value.systems:
            if bg_color is None:
                g.brush = self.bg_color = bg_color = system.bg_color
                g.draw_rectangle( *self.content_bounds )

            for particle in system.particles:
                size = ir( particle.size )
                if size > 0:
                    x, y      = particle.position
                    g.opacity = particle.opacity
                    image     = image_for( particle.image, size )
                    g.draw_bitmap(
                        image.bitmap, ir( x ) - image.width  / 2,
                                      ir( y ) - image.height / 2
                    )

        if bg_color is None:
            g.brush = self.bg_color
            g.draw_rectangle( *self.content_bounds )

        if self.show_positions:
            g.anti_alias = True
            for system in self.value.systems:
                x0, y0, x1, y1 = self._system_bounds( system )
                g.set( opacity = 0.5, brush = None )
                g.pen = Pen( color = 0xC00000, width = 5 )
                g.draw_circle( ir( x0 ), ir( y0 ), 15 )
                g.draw_circle( ir( x1 ), ir( y1 ), 15 )
                g.set(
                    pen     = None,
                    brush   = 0xC00000,
                    opacity = ( 0.3, 0.75 ) [ system == self.drop_system ]
                )
                g.draw_rectangle( x0, y0, x1 - x0, y1 - y0 )

        self.draw_time += (time() - now)


    def paint_label ( self, g ):
        """ Paints the contents of the editor control theme label.
        """
        self.frames += 1
        systems      = self.value.systems
        if len( systems ) > 0:
            time = systems[0].clock.time
            dt   = time - self.time
            if dt > 1.0:
                self.fps       = self.frames / dt
                self.dts       = self.draw_time / dt
                self.frames    = 0
                self.draw_time = 0.0
                self.time      = time

        g.opacity = 1.0
        dx, dy    = self.control.client_size
        n         = reduce( lambda x, y: x + len( y.particles ), systems, 0 )
        self.theme.draw_label( g,
            '%d particles - %.1f frames/second - %.3f' %
            ( n, self.fps, self.dts ), None, 0, 0, dx, dy
        )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'value.systems.refresh' )
    def _need_refresh ( self ):
        """ Handles one of the particle systems requesting a refresh.
        """
        self.refresh()


    def normal_enter ( self ):
        """ Handles the mouse entering the editor control.
        """
        self.show_positions = True
        self.refresh()


    def normal_leave ( self ):
        """ Hoandles the mouse leaving the editor control.
        """
        self.show_positions = False
        self.refresh()


    def normal_left_down ( self, x, y, event ):
        """ Handles the user pressing the left mouse button in the editor
            control.
        """
        for system in self.value.systems:
            if (self._check_point( x, y, system, 'position0' ) or
                self._check_point( x, y, system, 'position1' ) or
                self._check_bounds( x, y, event, system )):
                break


    def normal_right_up ( self, x, y ):
        """ Handles the user releasing the right mouse button in the editor
            control.
        """
        system = self._find_system( x, y )
        if system is None:
            self.value.add_system( x, y )
        else:
            self.value.remove_system( system )


    def dragging_motion ( self, x, y ):
        """ Handles the user dragging some part of a particle system's creation
            rectangle.
        """
        x0, y0, items = self._info
        for system, position in items:
            xp, yp = getattr( system, position )
            setattr( system, position, ( xp + x - x0, yp + y - y0 ) )

        self._info = ( x, y, items )
        self.refresh()


    def dragging_left_up ( self ):
        """ Handles the user releasing the left mouse button at the end of a
            drag operation.
        """
        self.state = 'normal'


    def drag_enter ( self, event ):
        """ Handles some dragged object entering the editor control.
        """
        if self._has_image_files( event ):
            event.result        = event.request
            self.show_positions = True
        else:
            event.result = 'ignore'


    def drag_leave ( self, event ):
        """ Handles a dragged object leaving the editor control.
        """
        self.show_positions = False
        self.drop_system    = None


    def drag_move ( self, event ):
        """ Handles a dragged object being moved over the editor control.
        """
        self.drop_system = self._find_system( event.x, event.y )
        event.result = ( event.request, 'ignore' ) [ self.drop_system is None ]


    def drag_drop ( self, event ):
        """ Handles a dragged object being dropped onto the editor control.
        """
        self.drop_system = None
        system           = self._find_system( event.x, event.y )
        if system is not None:
            for file in event.files:
                if (file[:1] == '@') or (splitext( file )[1] in ImageTypes):
                    if file.startswith( '///' ):
                        file = file[3:]

                    system.image_name = file

    #-- Private Methods --------------------------------------------------------

    def _system_bounds ( self, system ):
        """ Returns the bounds of a specified particle *system*'s creation
            rectangle.
        """
        x0, y0 = system.position0
        x1, y1 = system.position1

        return ( min( x0, x1 ), min( y0, y1 ), max( x0, x1 ), max( y0, y1 ) )


    def _check_point ( self, x, y, system, position ):
        """ Checks for the user starting a drag operation over a specified
            particle *system*'s *position" corner. Returns True if the specified
            (*x*,*y*) position is over the corner, and False otherwise. Also, if
            True, it sets up the drag operation.
        """
        x0, y0 = getattr( system, position )
        if sqrt( ((x0 - x) * (x0 - x)) + ((y0 - y) * (y0 - y)) ) > 15.0:
            return False

        self.state = 'dragging'
        self._info = ( x, y, ( ( system, position ), ) )

        return True


    def _check_bounds ( self, x, y, event, system ):
        """ Checks for the user starting a drag operation over the specified
            particle *system*'s creation rectangle. Returns True if the
            specified (*x*,*y*) point is over the rectangle, and False
            otherwise. If True, it also sets up the drag operation.
        """
        x0, y0, x1, y1 = self._system_bounds( system )
        if (x0 <= x <= x1) and (y0 <= y <= y1):
            self.state = 'dragging'
            if event.control_down:
                system = self.value.add_system( x, y, system )

            self._info = ( x, y, ( ( system, 'position0' ),
                                   ( system, 'position1' ) ) )
            return True

        return False


    def _find_system ( self, x, y ):
        """ Returns the first particle system (if any) whose creation rectangle
            contains the specified (*x*,*y*) point.
        """
        for system in self.value.systems:
            x0, y0, x1, y1 = self._system_bounds( system )
            if (x0 <= x <= x1) and (y0 <= y <= y1):
                return system

        return None


    def _has_image_files ( self, event ):
        """ Returns True if the specified drag and drop *event* contains at
            least one image file, and False otherwise.
        """
        for file in event.files:
            if (file[:1] == '@') or (splitext( file )[1] in ImageTypes):
                return True

        return False

#-------------------------------------------------------------------------------
#  'ParticleSystemsEditor' class:
#-------------------------------------------------------------------------------

class ParticleSystemsEditor ( CustomControlEditor ):
    """ Defines the particle system editor factory using a custom control
        editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The custom control editor class to use:
    klass = _ParticleSystemsEditor

    # The background theme to use for the editor control:
    theme = '@xform:btd?L30'

#-------------------------------------------------------------------------------
#  'PresetsAdapter' class:
#-------------------------------------------------------------------------------

class PresetsAdapter ( GridAdapter ):
    """ Adapts preset names for use with the GridEditor.
    """

    columns     = [ ( 'Preset', 'preset' ) ]
    auto_filter = True
    sorter      = lambda l, r: cmp( l, r )

    def preset_content ( self ):
        return self.item

#-------------------------------------------------------------------------------
#  Light Table Image Adapter:
#-------------------------------------------------------------------------------

light_table_adapter = ThemedImage(
    normal_theme = Theme( '@xform:b?l40', content = 8 ),
    transform    = HLSATransform( hue = 0.56, lightness = 0.2,
                                  saturation = 0.13 ),
    lightness    = 0.12
)

#-------------------------------------------------------------------------------
#  'ParticleSystemsDemo' class:
#-------------------------------------------------------------------------------

class ParticleSystemsDemo ( HasFacets ):
    """ Defines the main class for particle system demonstration.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The set of particle systems to display:
    systems = Instance( ParticleSystems, () )

    # The list of standard particle images:
    particle_images = List # ( Str )

    # The name of the current system:
    name = Str

    # The name of the currently selected system preset:
    preset = Str

    # The list of available presets:
    presets = List

    # The event fired when a preset is to be saved:
    save_preset = Button( '@icons2:Floppy' )

    # The event fired when the selected preset is to be deleted:
    delete_preset = Button( '@icons2:Delete' )

    # Can the current system be saved as a preset?
    preset_saveable = Property

    # Can the current preset be deleted?
    preset_deletable = Property

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HSplit(
            Tabbed(
                UItem( 'systems',
                       style  = 'custom',
                       dock   = 'tab',
                       export = 'DockWindowShell',
                       label  = 'Properties'
                ),
                UItem( 'particle_images',
                       editor = LightTableEditor(
                           selection_mode  = 'items',
                           show_scrollbars = False,
                           can_drag        = True,
                           adapter         = light_table_adapter,
                           layout          = GridLayout(
                               margin = 0, spacing = 0, width = 60
                           )
                       ),
                       dock   = 'tab',
                       export = 'DockWindowShell',
                       label  = 'Images'
                ),
                VGroup(
                    UItem( 'presets',
                           editor = GridEditor(
                               adapter    = PresetsAdapter,
                               operations = [], #[ 'sort' ],
                               selected   = 'preset'
                           )
                    ),
                    HGroup(
                        Item( 'name', springy = True ),
                        UItem( 'save_preset',
                               enabled_when = 'preset_saveable'
                        ),
                        UItem( 'delete_preset',
                               enabled_when = 'preset_deletable'
                        ),
                        group_theme = '@xform:b?L15'
                    ),
                    dock   = 'tab',
                    export = 'DockWindowShell',
                    label  = 'Presets'
                )
            ),
            UItem( 'systems',
                   id     = 'systems1',
                   editor = ParticleSystemsEditor(),
                   dock   = 'tab',
                   export = 'DockWindowShell',
                   label  = 'Particles'
            ),
            id = 'splitter'
        ),
        id     = ParticlesKey,
        width  = 0.80,
        height = 0.80
    )

    #-- Facet Default Values ---------------------------------------------------

    def _particle_images_default ( self ):
        return [
            image_info.image_name
            for image_info in ImageLibrary().catalog[ 'particles' ].images
        ]


    def _presets_default ( self ):
        return facet_db.get( ParticlesKey + ':Presets', [] )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'name' )
    def _get_preset_saveable ( self ):
        return (self.name.strip() != '')


    @property_depends_on( 'name' )
    def _get_preset_deletable ( self ):
        return (self.name.strip() in self.presets)

    #-- Facet Event Handlers ---------------------------------------------------

    def _preset_set ( self, preset ):
        """ Handles a new 'preset' being selected.
        """
        self.name = name = preset
        systems   = facet_db.get( '%s:Preset=%s' % ( ParticlesKey, name ) )
        if systems is not None:
            self.systems.dispose()
            self.systems = systems


    def _delete_preset_set ( self ):
        """ Handles the 'delete_preset' event being fired.
        """
        name = self._preset_name()
        if name in self.presets:
            self.presets.remove( name )
            facet_db.set( ParticlesKey + ':Presets', self.presets )
            facet_db.set( '%s:Preset=%s' % ( ParticlesKey, name ) )


    def _save_preset_set ( self ):
        """ Handles the 'save_preset' event being fired.
        """
        name = self._preset_name()
        facet_db.set( '%s:Preset=%s' % ( ParticlesKey, name ), self.systems )
        if name not in self.presets:
            self.presets.append( name )
            facet_db.set( ParticlesKey + ':Presets', self.presets )

    #-- Private Methods --------------------------------------------------------

    def _preset_name ( self ):
        """ Returns the current preset name.
        """
        return str( self.name.strip() )

#-- Create the demo ------------------------------------------------------------

demo = ParticleSystemsDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
