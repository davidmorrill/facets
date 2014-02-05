"""
# Puzzle #

Demonstrates another use of some of the various animation **Tweener** and
**Path** classes, in this case creating a simple *puzzle-like* animation that
takes a random image, divides it up into a grid of smaller *pieces*, scrambles
the pieces to form a new grid, and then animates the motion of each of the
pieces back to its original position using a randomly chosen animation path.

The demo uses three of the available 2D integer path animation classes:

- **Linear2DIntPath**: Moves a piece in a straight line from its starting
  position to its ending position.
- **Manhattan2DIntPath**: Moves a piece horizontally, then vertically, from
  its starting position to its ending position.
- **Spiral2DIntPath**: Moves a piece in a circular 180 degree arc from its
  starting position to its ending position rotating around the center point
  halfway between the starting and ending points.

The demo also uses a custom *tweener* to animate the motion of each piece by
*composing* two standard **Tweener** subclasses:

- **EaseInTweener**: Motions starts quickly then slows downs as its nears the
  ending position.
- **RampTweener**: Slows down the motion at the beginning and ends of the path
  using a linear *ramp*.

The images displayed are randomly chosen from the list of images contained in
the facets UI demo's *demo.zip* image library.

You can specify the length of the animation by adjusting the ***Time*** scrubber
setting in the lower right hand corner of the view *prior* to starting a new
animation by clicking the ***Start*** button next to it.

If you read the code for the **Puzzle** class closely you will see that it is
actually over-engineered for this demo and supports a number of additional
*puzzle-solving* abailities not used by the demo. The interested reader is urged
to experiment with changing some of the arguments specified (and unspecified)
for the **Puzzle** constructor in the ***_create_puzzle*** method near the end
of the code.
"""

#-- Imports --------------------------------------------------------------------

from random \
    import shuffle, choice

from math \
    import floor

from facets.api \
    import HasFacets, Tuple, Int, List, Image, Instance, Range, Bool, \
           Property, Button, Theme, View, Item, UItem, HGroup, ScrubberEditor, \
           spring, on_facet_set, property_depends_on

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.animation.api \
    import ConcurrentAnimation, EaseInTweener, RampTweener, Linear2DIntPath, \
           Manhattan2DIntPath, Spiral2DIntPath

from facets.ui.image \
    import ImageLibrary

#-- Constants ------------------------------------------------------------------

PuzzlePaths   = ( Linear2DIntPath(), Manhattan2DIntPath(), Spiral2DIntPath() )
PuzzleTweener = EaseInTweener( RampTweener( cycle = 0.7 ) )
Images        = [
    image.image_name
    for image in ImageLibrary().catalog[ 'demo' ].images
    if image.width >= 400
]

#-- PuzzlePiece class ----------------------------------------------------------

class PuzzlePiece ( HasFacets ):

    current = Tuple( Int, Int )
    solved  = Tuple( Int, Int )

    def _solved_set ( self, solved ):
        self.current = solved

#-- Puzzle class ---------------------------------------------------------------

class Puzzle ( HasFacets ):

    base_image = Image
    image      = Image
    rows       = Range( 4, 25, 8 )
    columns    = Range( 4, 25, 8 )
    count      = Range( 1, None, 5 )
    force      = Range( 0.0, 1.0, .15 )
    time       = Range( 0.1, 10.0, 1.9 )
    paths      = List( PuzzlePaths )

    pieces     = List( PuzzlePiece )
    unsolved   = List
    size       = Tuple( Int, Int )
    frame      = Int
    animation  = Instance( ConcurrentAnimation )
    running    = Bool( False )

    def _image_set ( self, image ):
        rows, columns = self.rows, self.columns
        self.size     = ( image.width / columns, image.height / rows )
        pdx, pdy      = self.size
        pieces        = []
        for x in xrange( columns ):
            for y in xrange( rows ):
                pieces.append( PuzzlePiece( solved = ( x * pdx, y * pdy ) ) )

        self.pieces = pieces
        self.frame  = 0
        self._scramble_pieces()
        self._check_animation()

    def _running_set ( self ):
        self._check_animation()

    @on_facet_set( 'animation:stopped' )
    def _animation_stopped ( self ):
        self.animation = None
        self._check_animation()

    def _create_animation ( self ):
        unsolved = self.unsolved = [ piece for piece in self.unsolved
                                           if piece.current != piece.solved ]
        n = len( unsolved )
        if n > 0:
            shuffle( unsolved )
            path        = choice( self.paths )
            indices     = range( n )
            self.frame += 1
            if self.frame >= self.count:
                force = n - 1
            else:
                force = int( round( self.force * n ) )

            for i in xrange( force ):
                solved = unsolved[ i ].solved
                for j in xrange( i + 1, n ):
                    if unsolved[ indices[ j ] ].current == solved:
                        indices[ i ], indices[ j ] = \
                        indices[ j ], indices[ i ]

                        break

            rest = indices[ force: ]
            shuffle( rest )
            indices[ force: ] = rest

            self.animation = ConcurrentAnimation( items = [
                unsolved[ i ].animate_facet(
                    'current', self.time,
                    unsolved[ indices[ i ] ].current,
                    unsolved[ i ].current,
                    repeat  = 1,
                    path    = path,
                    tweener = PuzzleTweener,
                    start   = False
                ) for i in xrange( n )
            ] ).run()

    def _check_animation ( self ):
        if self.running:
            self._create_animation()

    def _scramble_pieces ( self ):
        unsolved = self.unsolved = self.pieces
        n        = len( unsolved )
        indices  = range( n )
        shuffle( indices )
        for i in xrange( n ):
            if (i == indices[ i ]) and (i < (n - 1)):
                indices[ i ], indices[ i + 1 ] = indices[ i + 1 ], indices[ i ]

            unsolved[ i ].current = unsolved[ indices[ i ] ].solved

#-- _PuzzleEditor class --------------------------------------------------

class _PuzzleEditor ( ControlEditor ):

    virtual_size = ( 10, 10 )

    def paint_content ( self, g ):
        x, y, dx, dy  = self.content_bounds
        puzzle        = self.value
        columns, rows = puzzle.columns, puzzle.rows
        if puzzle.image is None:
            base_image = image = puzzle.base_image
            bidx, bidy = image.width, image.height
            pdx, pdy   = bidx / columns, bidy / rows

            # The constant 0.9 provides some margin around the expanded image:
            incr = int( floor( min( float( (0.95 * dx) - bidx ) / columns,
                                    float( (0.95 * dy) - bidy ) / rows ) ) )
            if incr != 0:
                image = base_image.scale( ( bidx + (incr * columns),
                                            bidy + (incr * rows) ) )

            puzzle.image = image

        g.brush           = None
        image             = puzzle.image
        bdx, bdy          = self.theme.bounds()
        self.virtual_size = ( image.width + bdx, image.height + bdy )
        pdx, pdy          = puzzle.size
        bitmap            = image.bitmap
        x0                = x + ((dx - (pdx * columns)) / 2)
        y0                = y + ((dy - (pdy * rows))    / 2)
        unsolved          = []

        for piece in self.value.pieces:
            if piece.current != piece.solved:
                unsolved.append( piece )
            else:
                cx, cy = piece.current
                sx, sy = piece.solved
                g.blit( x0 + cx, y0 + cy, pdx, pdy, bitmap, sx, sy )

        for piece in unsolved:
            cx, cy = piece.current
            sx, sy = piece.solved
            g.blit( x0 + cx, y0 + cy, pdx, pdy, bitmap, sx, sy )
            g.draw_rectangle( x0 + cx, y0 + cy, pdx, pdy )

    @on_facet_set( 'value:pieces:current' )
    def _needs_update ( self ):
        self.refresh()

    def _value_set ( self ):
        self.virtual_size = ( 10, 10 )

        super( _PuzzleEditor, self )._value_set()

#-- PuzzleEditor class ---------------------------------------------------------

class PuzzleEditor ( CustomControlEditor ):

    klass = _PuzzleEditor
    theme = '@tiles:FibreBoard1.jpg?s10L7'

#-- PuzzleSolver class ---------------------------------------------------------

class PuzzleSolver ( HasFacets ):

    puzzle = Instance( Puzzle )
    count  = Property
    start  = Button( 'Start' )
    time   = Range( 0.1, 10.0, 4.0 )

    view = View(
        UItem( 'puzzle', editor = PuzzleEditor() ),
        HGroup(
            spring,
            Item( 'time',
                  width      = -50,
                  editor     = ScrubberEditor( increment = 0.1 ),
                  item_theme = '#themes:ScrubberEditor'
            ),
            '_',
            UItem( 'start', enabled_when = "count == 0" ),
            group_theme = '@xform:b?L20'
        ),
        width  = 0.50,
        height = 0.80
    )

    def facets_init ( self ):
        self._start_set()

    def _start_set ( self ):
        self._create_puzzle().running = True

    @property_depends_on( 'puzzle.unsolved' )
    def _get_count ( self ):
        return len( self.puzzle.unsolved )

    def _create_puzzle ( self ):
        self.puzzle = Puzzle(
            rows       = 16,
            columns    = 16,
            count      = 1,
            force      = 0.0,
            time       = self.time,
            base_image = choice( Images )
        )

        return self.puzzle

#-- Create the demo ------------------------------------------------------------

demo = PuzzleSolver

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
