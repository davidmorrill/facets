"""
A just for fun Puzzle tool that turns arbitrary images into animated puzzles. It
is based on the Puzzle.py demo in the Graphics and Animation section of the
Facets UI demo.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from random \
    import randint, shuffle, choice

from facets.api \
    import HasFacets, Tuple, Int, List, Image, Instance, Range, Bool, Button, \
           Color, Event, Theme, View, UItem, HToolbar, HLSColorEditor,        \
           SyncValue, on_facet_set

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.animation.api \
    import ConcurrentAnimation, EaseIn, Linear2DIntPath, Manhattan2DIntPath, \
           Spiral2DIntPath

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The margin around the borders of the puzzle:
Margin = 50

# The animation paths used to animate the puzzle pieces:
PuzzlePaths = ( Linear2DIntPath(), Manhattan2DIntPath(), Spiral2DIntPath() )

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# A tuple of the form: ( int, int ) used to represent 2D positions and sizes:
IntTuple = Tuple( Int, Int )

#-------------------------------------------------------------------------------
#  'PuzzlePiece' class:
#-------------------------------------------------------------------------------

class PuzzlePiece ( HasFacets ):
    """ Describes the current and final positions of an individual puzzle piece.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current position of the piece:
    current = IntTuple

    # The final (solved) position of the piece:
    solved  = IntTuple

    # The size of the puzzle piece:
    size = IntTuple

    #-- Facet Event Handlers ---------------------------------------------------

    def _solved_set ( self, solved ):
        """ Handles the 'solved' facet being changed.
        """
        self.current = solved

#-------------------------------------------------------------------------------
#  '_PuzzleEditor' class:
#-------------------------------------------------------------------------------

class _PuzzleEditor ( ControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The scaled version of the input image being converted into puzzle pieces:
    image = Image

    # The list of puzzle pieces the images is divided into:
    pieces = List( PuzzlePiece )

    # The list of puzzle pieces not yet in their 'solved' position:
    unsolved = List

    # The concurrent animation used to drive the puzzle animation:
    animation = Instance( ConcurrentAnimation )

    # Event fired when the animation should begin running:
    running = Bool( False )

    # Indicate that the editor should support scrolling:
    virtual_size = ( 10, 10 )

    #-- ControlEditor Method Overrides -----------------------------------------

    def paint_all ( self, g ):
        """ Paints the set of puzzle pieces in their current positions.
        """
        cdx, cdy = self.control.size
        g.brush  = self.factory.bg_color
        g.pen    = None
        g.draw_rectangle( 0, 0, cdx, cdy )

        image = self.image
        if image is not None:
            bitmap, idx, idy = image.bitmap, image.width, image.height
            x, y, dx, dy     = self.content_bounds
            x0, y0           = x + ((dx - idx) / 2), y + ((dy - idy) / 2)

            for piece in self.pieces:
                cx, cy = piece.current
                sx, sy = piece.solved
                dx, dy = piece.size
                g.blit( x0 + cx, y0 + cy, dx, dy, bitmap, sx, sy )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'pieces:current, factory:bg_color' )
    def _needs_update ( self ):
        """ Handles any of the puzzle pieces changing their current position.
        """
        self.refresh()


    def _value_set ( self, image ):
        """ Handles the input image being changed.
        """
        do_later( self._start_animation )


    @on_facet_set( 'factory:start' )
    def _start_modified ( self ):
        """ Handles the factory 'start' facet being fired.
        """
        self._start_animation()


    @on_facet_set( 'animation:stopped' )
    def _animation_stopped ( self ):
        """ Handles the animation's 'stopped' facet being changed.
        """
        self.animation       = None
        self.factory.running = False

    #-- Mouse Event Handlers ---------------------------------------------------

    def left_up ( self ):
        """ Handles the left mouse button being released.
        """
        self._start_animation()

    #-- Private Methods --------------------------------------------------------

    def _init_puzzle ( self ):
        """ Initializes the puzzle.
        """
        image = self.value
        if image is not None:
            factory  = self.factory
            size     = factory.size
            cdx, cdy = self.control.size
            cdx      = max( 64, cdx - Margin )
            cdy      = max( 64, cdy - Margin )
            idx, idy = image.width, image.height
            if (idx > 0) and (idy > 0):
                scale = min( float( cdx ) / idx, float( cdy ) / idy, 2.0 )
                idx   = int( scale * idx )
                idy   = int( scale * idy )
                nx    = int( round( float( idx ) / size ) )
                ny    = int( round( float( idy ) / size ) )
                pdx   = float( idx ) / nx
                pdy   = float( idy ) / ny
                xs    = [ 0 ]
                x     = 0.0
                for i in xrange( nx ):
                    x += pdx
                    xs.append( int( round( x ) ) )

                ys = [ 0 ]
                y  = 0.0
                for i in xrange( ny ):
                    y += pdy
                    ys.append( int( round( y ) ) )

                self.image        = image.scale( ( idx, idy ) )
                self.virtual_size = ( idx + Margin, idy + Margin )
                pieces            = []
                for i in xrange( nx ):
                    x  = xs[ i ]
                    dx = xs[ i + 1 ] - x
                    for j in xrange( ny ):
                        pieces.append(
                            PuzzlePiece( solved = ( x, ys[ j ] ),
                                         size   = ( dx, ys[ j + 1 ] - ys[ j ] )
                        ) )

                self.pieces          = pieces
                self.factory.running = False


    def _start_animation ( self ):
        """ Creates a concurrent animation for all of the puzzle pieces.
        """
        if self.animation is not None:
            self.animation.halt()

        self._init_puzzle()
        self._scramble_pieces()
        path = choice( self.factory.paths )
        time = self.factory.time
        self.animation = ConcurrentAnimation( items = [
            piece.animate_facet(
                'current', time, piece.solved, piece.current,
                repeat  = 1,
                path    = path,
                tweener = EaseIn,
                start   = False
            ) for piece in self.pieces
        ] ).run()
        self.factory.running = True


    def _scramble_pieces ( self ):
        """ Scrambles the position of all the puzzle pieces.
        """
        unsolved = self.unsolved = self.pieces
        if randint( 0, 1 ) == 0:
            cdx, cdy = self.control.size
            size     = self.factory.size
            size2    = size / 2
            for piece in unsolved:
                side = randint( 0, 3 )
                if side <= 1:
                    x = randint( -size2, cdx - size2 )
                    y = (-size2) if side == 0 else cdy
                else:
                    x = (-size2) if side == 2 else cdx
                    y = randint( -size2, cdy - size2 )

                piece.current = ( x, y )

            return

        n        = len( unsolved )
        indices  = range( n )
        shuffle( indices )
        for i in xrange( n ):
            if (i == indices[ i ]) and (i < (n - 1)):
                indices[ i ], indices[ i + 1 ] = indices[ i + 1 ], indices[ i ]

            unsolved[ i ].current = unsolved[ indices[ i ] ].solved

#-- PuzzleEditor class ---------------------------------------------------------

class PuzzleEditor ( CustomControlEditor ):

    # The class of the editor created:
    klass = _PuzzleEditor

    # The available list of paths to use for the puzzle pieces:
    paths = List( PuzzlePaths )

    # The length of time the puzzle animation should run:
    time = Range( 0.1, 10.0, 1.9, facet_value = True )

    # The size of each puzzle piece square:
    size = Range( 20, 150, 100, facet_value = True )

    # Event fired when the puzzle animation should start:
    start = Event( facet_value = True )

    # Value is True while animation is running:
    running = Bool( False, facet_value = True )

    # The background color for the editor:
    bg_color = Color( 0xD0D0D0, facet_value = True )

#-------------------------------------------------------------------------------
#  'Puzzle' class:
#-------------------------------------------------------------------------------

class Puzzle ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Puzzle'

    # The current image to run a puzzle animation on:
    image = Image( connect = 'to' )

    # The length of time the puzzle animation should run:
    time = Range( 0.1, 10.0, 1.9, save_state = True )

    # The size of each puzzle piece square:
    size = Range( 20, 150, 100, save_state = True )

    # Event fired when the puzzle animation should start:
    start = Button( '@icons2:Gear' )

    # Indicates when a puzzle animation is running:
    running = Bool( False )

    # The background color for the editor:
    bg_color = Color( 0xD0D0D0, save_state = True )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'image', editor = PuzzleEditor(
                                time     = SyncValue( self, 'time' ),
                                size     = SyncValue( self, 'size' ),
                                start    = SyncValue( self, 'start' ),
                                running  = SyncValue( self, 'running' ),
                                bg_color = SyncValue( self, 'bg_color' ) )
            ),
            id     = 'facets.extra.tools.puzzle.Puzzle',
            width  = 0.50,
            height = 0.80
        )


    options = View(
        HToolbar(
            UItem( 'bg_color',
                   editor  = HLSColorEditor( edit = 'lightness' ),
                   springy = True
            ),
            Scrubber( 'size', 'Size of each puzzle piece (in pixels)',
                width     = 50,
                increment = 10
            ),
            Scrubber( 'time', 'Duration of puzzle animation (in seconds)',
                width     = 50,
                increment = 0.1
            ),
            '_',
            UItem( 'start',
                   tooltip      = 'Start puzzle animation',
                   enabled_when = 'not running'
            ),
            group_theme = Theme( '@xform:b?L10', content = ( 4, 0, 4, 4 ) ),
            id          = 'tb'
        ),
        id = 'facets.extra.tools.puzzle.Puzzle.options'
    )

#-- EOF ------------------------------------------------------------------------
