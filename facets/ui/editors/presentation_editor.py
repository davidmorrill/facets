"""
Defines the PresentationEditor class for viewing the contents of a string as a
series of one or more presentation 'slides'.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from os.path \
    import join, splitext, isfile

from random \
    import randint, choice

from facets.api \
    import HasFacets, HasPrivateFacets, SingletonHasFacets, Any, Bool, Int, \
           Instance, Str, Range, Enum, Code, Event, Font, List, Directory,  \
           Property, ATheme, Theme, Image, View, VGroup, UItem, Editor,     \
           BasicEditorFactory, GridEditor, on_facet_set, inn

from facets.core.facet_base \
    import read_file

from facets.ui.ui_facets \
    import HorizontalAlignment, HasMargin

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.editors.drawable_canvas_editor \
    import DrawableCanvasControl

from facets.ui.drawable.api \
    import DrawableCanvas, Drawable, ThemedText, Value2D

from facets.animation.api \
    import ConcurrentAnimation, RampTweener, EaseIn, EaseOut

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from command names to attribute names:
CommandNameMap = {
    'ht': 'header_theme',
    'hi': 'header_image',
    'hf': 'header_font',
    'hc': 'header_content',
    'ha': 'header_alignment',
    'ft': 'footer_theme',
    'fi': 'footer_image',
    'ff': 'footer_font',
    'fc': 'footer_content',
    'fa': 'footer_alignment',
    'bt': 'bullet_theme',
    'bi': 'bullet_image',
    'bf': 'bullet_font',
    'bm': 'bullet_margin',
    'it': 'indented_theme',
    'ii': 'indented_image',
    'if': 'indented_font',
    'im': 'indented_margin',
    'mt': 'multiline_theme',
    'mi': 'multiline_image',
    'mf': 'multiline_font',
    'mm': 'multiline_margin',
    'ct': 'code_theme',
    'ci': 'code_image',
    'cf': 'code_font',
    'cm': 'code_margin',
    'pt': 'picture_theme',
    'pm': 'picture_margin',
    'gt': 'background_theme',
    'fb': 'file_base',
    'sa': 'slide_advance',
    'st': 'slide_transition',
    'vs': 'vertical_space',
    'xf': 'execute_file',
    'xc': 'execute_code',
    'xu': 'execute_user',
    'xo': 'export_object',
    '*':  'kind_none',
    '-':  'kind_fade',
    '<':  'kind_left',
    '>':  'kind_right',
    '/':  'kind_up',
    '\\': 'kind_down'
}

# Long form of the command names:
LongCommandNames = set( CommandNameMap.values() )

# Command names that need to evaluate their data before being assigned or used:
Evaluate = set( [ 'vertical_space',   'bullet_margin', 'indented_margin',
                  'multiline_margin', 'code_margin',   'picture_margin' ] )

# Command names that correspond to executable methods:
Execute = { 'execute_file', 'execute_code', 'execute_user', 'export_object' }

# The characters use for the slide item 'kind':
KindChars = '*-<>/\\?|'

# Regex pattern to match integer strings:
Digits = re.compile( '^[0-9]+$' )

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# The transition used when a slide advances:
SlideTransition = Enum( 'left', 'right', 'up', 'down', 'all', 'fade', 'hide' )

# The method used to handle an item/slide advance:
SlideAdvance = Enum( 'item', 'slide' )

#-------------------------------------------------------------------------------
#  'DummyObject' class:
#-------------------------------------------------------------------------------

class DummyObject ( SingletonHasFacets ):

    view = View()

#-------------------------------------------------------------------------------
#  'SlideText' class:
#-------------------------------------------------------------------------------

class SlideText ( ThemedText ):
    """ Represents a text-based slide item.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The margin around the item:
    margin = HasMargin

    # The kind of animation used to add the item to the slide:
    kind = Str( '-' )

    # The saved origins of the item (used for animation start/stop points):
    alt_origin = Any # ( (x_begin, y_begin), (x_end, y_end) )

#-------------------------------------------------------------------------------
#  'SlideImage' class:
#-------------------------------------------------------------------------------

class SlideImage ( Drawable ):
    """ Draws an image with a themed background.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The themed image origin:
    origin = Value2D( event = 'notify_owner' )

    # The size of the themed image:
    size = Value2D( None, event = 'notify_owner' )

    # The theme to use for the background:
    theme = ATheme( '@xform:b', event = 'notify_owner' )

    # The image to draw:
    image = Image( event = 'notify_owner' )

    # Should the image automatically be scaled to fit the specified size?
    auto_scale = Bool( False )

    # The margin around the item:
    margin = HasMargin

    # The horizontal alignment of the image:
    alignment = HorizontalAlignment

    # The (optional) label text to draw:
    label = Str( event = 'notify_owner' )

    # The kind of animation used to add the item to the slide:
    kind = Str( '-' )

    # The saved origins of the item (used for animation start/stop points):
    alt_origin = Any # ( (x_begin, y_begin), (x_end, y_end) )

    #-- Drawable Method Overrides ----------------------------------------------

    def paint ( self, g ):
        """ Draws a themed text object.
        """
        theme = self.theme
        idx   = idy = 50
        image = self.image
        if image is not None:
            idx, idy = image.width, image.height

        if self.size is None:
            tdx, tdy  = theme.bounds()
            self.size = ( tdx, + idx, tdy + idy )

        dx, dy = self.size
        x,  y  = self.origin
        theme.fill( g, x, y, dx, dy )

        if image is not None:
            tx, ty, tdx, tdy = theme.bounds( x, y, dx, dy )
            if self.auto_scale:
                scale = min( float( tdx ) / idx, float( tdy ) / idy )
                if scale != self._scale:
                    self._scale        = scale
                    self._scaled_image = image.scale( scale )

                image    = self._scaled_image
                idx, idy = image.width, image.height

            if self.alignment == 'center':
                tx += (tdx - idx) / 2

            g.draw_bitmap( image.bitmap, tx, ty + ((tdy - idy) / 2) )

        if self.label != '':
            g.font = theme.label_font
            theme.draw_label( g, self.label, None, x, y, dx, dy )

#-------------------------------------------------------------------------------
#  'Slide' class:
#-------------------------------------------------------------------------------

class Slide ( HasPrivateFacets ):
    """ Represents a single presentation 'slide'.
    """

    # The title of the slide:
    title = Str

    # The header item for the slide:
    header = Any

    # The items comprising the body of the slide:
    body = List

    # The footer item for the slide:
    footer = Any

    # The list of all non-vertical space body items:
    body_content = List

    # The list of all slide items:
    content = List

    # Executable Python code associated with the slide:
    code = Code

    # Should the Python code automatically be executed when the slide is loaded?
    auto_execute = Bool( True )

    # The list of objects that have been exported by this slide:
    objects = List

    # The transition used when the slide is finished:
    slide_transition = SlideTransition

    # The background theme for the slide:
    background_theme = ATheme

    # The method used to handle an item/slide advance:
    slide_advance = SlideAdvance

    # The index of the current item:
    index = Int

    # The currently running transition animations:
    animation = Instance( ConcurrentAnimation )

    # The PresentationEditor this slide belongs to:
    editor = Any # Instance( _PresentationEditor )

    # The bounds of the slide:
    bounds = Property

    # Is there only a single image item in the body?
    only_image = Property

    #-- Facet Default Values ---------------------------------------------------

    def _body_content_default ( self ):
        return [ item for item in self.body if not isinstance( item, int ) ]


    def _content_default ( self ):
        content = self.body_content[:]
        if self.header is not None:
            content.insert( 0, self.header )

        if self.footer is not None:
            content.append( self.footer )

        return content

    #-- Property Implementations -----------------------------------------------

    def _get_bounds ( self ):
        return self.editor.canvas.bounds


    def _get_only_image ( self ):
        return ((len( self.body_content ) == 1) and
                isinstance( self.body_content[0], SlideImage ))

    #-- Public Methods ---------------------------------------------------------

    def slide_display ( self, show_all ):
        """ Does the initial display of a slide.
        """
        # Cancel any previously running transition animations immediately:
        self.animation = None

        x, y, dx, dy   = self.bounds
        header, footer = self.header, self.footer
        ay, ady        = y, dy
        items          = []

        if footer is not None:
             fdy = self._size_for( footer, dx, ady )
             self._add_at( footer, x, y + dy - fdy )
             ady -= fdy
             items.append( footer )

        if header is not None:
             hdy = self._size_for( header, dx, ady )
             self._add_at( header, x, y )
             ady -= hdy
             ay  += hdy
             items.append( header )

        body = self.body
        if self.only_image:
            item            = body[0]
            item.auto_scale = True
            item.alignment  = 'center'
            item.size       = ( dx - item.margin.left - item.margin.right, ady )
            self._add_at( item, x, ay, True )
            items.insert( 0, item )
        else:
            for item in body:
                if isinstance( item, int ):
                    ady -= item
                    ay  += item
                else:
                    idy = (self._size_for( item, dx, ady ) +
                           item.margin.top + item.margin.bottom)
                    self._add_at( item, x, ay, True )
                    ady -= idy
                    ay  += idy
                    items.insert( 0, item )

        self.editor.canvas.content.extend( items )

        content = self.body_content
        n = m   = len( content )
        if (self.slide_advance == 'item') and (not show_all):
           m = min( 1, m )

        self.index = m - 1
        if m > 0:
            time  = 0.5 + (0.17 * (m - 1))
            cycle = 0.5 / time
            scale = 1.0 / m
            for i in xrange( m ):
                self._animate( content[ i ], time, cycle, scale * i )

            for i in xrange( m, n ):
                content[ i ].visible = False

        if self.auto_execute:
            self.run_code()


    def slide_remove ( self ):
        """ Handles a slide being removed from the canvas.
        """
        inn( self.header ).remove()
        inn( self.footer ).remove()

        handler = getattr( self, '_slide_transition_' + self.slide_transition )
        items   = []
        for item in self.body_content:
            item.halt_animated_facets()
            if item.visible:
                animation = handler( item )
                if animation is not None:
                    items.append( animation )
            else:
                item.remove()

        if len( items ) > 0:
            self.animation = ConcurrentAnimation( items = items ).run()

        # Clean up any objects created by code attached to the slide:
        if len( self.objects ) > 0:
            self.editor.export_object( DummyObject() )

        for object in self.objects:
            inn( object, 'dispose' )()

        del self.objects[:]


    def advance_item ( self, forward ):
        """ Advances to the next slide item based upon the direction specified
            by *forward*, which is **True** if the next item should be displayed
            and **False** if the previous item should be displayed. The slide's
            'slide_advance' value also affects how advancing occurs.
        """
        if self.slide_advance == 'slide':
            return (1 if forward else -1)

        content = self.body_content
        index   = self.index
        if forward:
            index += 1
            if index >= len( content ):
                return 1

            self.index = index
            self._animate( content[ index ] )
        elif index > 0:
            self.index = index - 1
            self._animate( content[ index ], reverse = True )
        else:
            return -1

        return 0


    def run_code ( self ):
        """ Runs the code associated with the slide.
        """
        if self.code != '':
            context = self.editor.global_dict.copy()
            context[ 'export' ] = self._export_object
            try:
                exec self.code in context
            except:
                import traceback
                traceback.print_exc()


    def resize ( self ):
        """ Handles the associated canvas being resized.
        """
        x, y, dx, dy = self.bounds
        for item in self.content:
            idx, idy  = item.size
            item.size = ( dx - item.margin.left - item.margin.right, idy )

        footer = self.footer
        if footer is not None:
            footer.origin = ( footer.origin[0], y + dy - footer.size[1] )
            dy -= footer.size[1]

        if self.only_image:
            if self.header is not None:
                dy -= self.header.size[1]

            self.body[0].size = ( dx, dy )

        for item in self.body_content:
            self._add_at( item, x, None, True )

    #-- Facet Event Handlers ---------------------------------------------------

    def _animation_set ( self, old ):
        """ Handles an active animation being replaced by a new one.
        """
        if old is not None:
            old.halt()


    @on_facet_set( 'animation:stopped' )
    def _animation_stopped ( self ):
        """ Handles the transition animations running to completion.
        """
        self.animation = None
        for item in self.body_content:
            item.remove()

    #-- Private Methods --------------------------------------------------------

    def _slide_transition_left ( self, item ):
        """ Moves a slide item off stage left.
        """
        x, y, dx, dy = self.bounds

        return self._animate_to( item, x - dx, item.origin[1] )


    def _slide_transition_right ( self, item ):
        """ Moves a slide item off stage right.
        """
        x, y, dx, dy = self.bounds

        return self._animate_to( item, x + dx, item.origin[1] )


    def _slide_transition_up ( self, item ):
        """ Moves a slide item off stage up.
        """
        x, y, dx, dy = self.bounds
        x0, y0       = item.origin

        return self._animate_to( item, x0, y0 - dy )


    def _slide_transition_down ( self, item ):
        """ Moves a slide item off stage down.
        """
        x, y, dx, dy = self.bounds
        x0, y0       = item.origin

        return self._animate_to( item, x0, y0 + dy )


    def _slide_transition_all ( self, item ):
        """ Moves a slide item off the stage in a random direction.
        """
        x, y, dx, dy = self.bounds
        xt, yt       = randint( x, x + dx ), randint( y, y + dy )
        direction    = randint( 0, 3 )
        if direction == 0:
            xt = x - dx
        elif direction == 1:
            xt = x + dx
        elif direction == 2:
            yt = item.origin[1] - dy
        else:
            yt = item.origin[1] + dy

        return self._animate_to( item, xt, yt )


    def _slide_transition_fade ( self, item ):
        """ Moves a slide item off the stage by fading it.
        """
        return item.animate_facet( 'opacity', 0.6, 0.0, start = False )


    def _slide_transition_hide ( self, item ):
        """ Moves a slide item off the stage by hiding it.
        """
        item.remove()

        return None


    def _animate_to ( self, item, x, y ):
        """ Animates movement of *item* to the position (*x*,*y*).
        """
        return item.animate_facet( 'origin', 0.50, ( x, y ), start = False )


    def _animate ( self, item, time = 0.5, cycle = 1.0, start = 0.0,
                               reverse = False ):
        """ Animates the specified *item* based on its 'kind' facet and the
            specified animation parameters.
        """
        item.visible = ((item.kind != '*') or (not reverse))
        item.opacity = 1.0
        opacity      = (item.kind == '-')
        tweener      = RampTweener( EaseOut if (reverse or opacity) else EaseIn,
                                    start = start, cycle = cycle )
        if opacity:
            end = 1.0 - reverse
            item.animate_facet( 'opacity', time, end, begin = 1.0 - end,
                                tweener = tweener )
        else:
            begin, end = item.alt_origin
            if reverse:
                begin, end = end, begin

            item.animate_facet( 'origin', time, end,
                                begin   = begin, tweener = tweener )


    def _size_for ( self, item, dx, dy ):
        """ Computes and sets the size needed for the specified *item* and
            returns the resulting height.
        """
        theme = item.theme
        dx   -= (item.margin.left + item.margin.right)
        if isinstance( item, SlideImage ):
            tdx, tdy  = theme.bounds()
            item.size = ( dx, tdy + item.image.height )
        else:
            g         = self.editor.adapter.temp_graphics
            g.font    = theme.content_font
            idx, idy  = theme.size_for( g, item.text )
            item.size = ( dx, idy )

        return item.size[1]


    def _add_at ( self, item, x, y = None, animate = False  ):
        """ Sets up the specified *item* so that it will appear on the canvas
            at the position specified by (*x*,*y*). If *animate* is **True** it
            also sets up the 'alt_origin' value for the item based on the item's
            'kind' value in preparation for animating the item.
        """
        if y is None:
            y = item.origin[1]
        else:
            y += item.margin.top

        xo          = x + item.margin.left
        item.origin = ( xo, y )
        if animate:
            x0, y0, dx, dy = self.bounds
            xb, yb         = xo, y
            kind           = item.kind
            if kind == '<':
                xb = x + dx
            elif kind == '>':
                xb = x - item.size[0]
            elif kind == '\\':
                yb = y0 - item.size[1]
            elif kind == '/':
                yb = y0 + dy

            item.alt_origin = ( ( xb, yb ), ( xo, y ) )


    def _export_object ( self, object ):
        """ Exports the object specified by *object* to the presentation editor.
        """
        if isinstance( object, HasFacets ):
            self.objects.append( object )
            self.editor.export_object( object )

#-------------------------------------------------------------------------------
#  'PresentationCanvas' class:
#-------------------------------------------------------------------------------

class PresentationCanvas ( DrawableCanvas ):
    """ Custom canvas for use with the PresentationEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor the canvas is associated with:
    editor = Any # Instance( _PresentationEditor )

    #-- Mouse Event Handlers ---------------------------------------------------

    def wheel ( self, event ):
        """ Handles a mouse wheel event.
        """
        self.editor.wheel( event )


    def left_up ( self, event ):
        """ Handles a left mouse button up event.
        """
        editor       = self.editor
        x, y, dx, dy = self.bounds
        ex, ey       = event.x, event.y
        xdx2, ydy2   = x + (dx / 2), y + (dy / 2)
        dx10, dy10   = dx / 10, dy / 10
        if (((xdx2 - dx10) <= ex <= (xdx2 + dx10)) and
            ((ydy2 - dy10) <= ey <= (ydy2 + dy10))):
            editor.select_slide( ex, ey )
        else:
            top_half = (ey <= ydy2)
            if ex <= xdx2:
                if top_half:
                    editor.first_slide()
                else:
                    editor.previous_slide()
            elif top_half:
                editor.last_slide()
            else:
                editor.next_slide()


    def right_up ( self, event ):
        """ Handles a right mouse button up event.
        """
        self.editor.run_code()

#-------------------------------------------------------------------------------
#  'TitlesAdapter' class:
#-------------------------------------------------------------------------------

class TitlesAdapter ( GridAdapter ):
    """ Adapts the PresentationEditor's list of titles for use with the
        GridEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    columns = [ ( 'Title', 'title' ) ]

    def title_text ( self ):
        return self.item

#-------------------------------------------------------------------------------
#  '_PresentationEditor' class:
#-------------------------------------------------------------------------------

class _PresentationEditor ( Editor ):
    """ Defines the implementation of the editor class for displaying a string
        as a series of one or more presentation 'slide'.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Indicate the editor is scrollable:
    scrollable = True

    # The canvas used for displaying the current slide:
    canvas = Instance( DrawableCanvas )

    # The CanvasControl used to display the canvas:
    canvas_control = Instance( DrawableCanvasControl )

    # The list of slides contained in the presentation:
    slides = List # ( Slide )

    # The list of all slide titles:
    titles = List # ( Str )

    # The current slide being constructed:
    build_slide = Instance( Slide )

    # The current slide being displayed:
    display_slide = Instance( Slide )

    # The title of the current slide:
    selected = Str

    # Should all slide items be displayed at once?
    show_all = Bool( True )

    # The global code execution context:
    global_dict = Any( {} )

    # The code to be executed globally before the first slide is displayed:
    global_code = Str

    # The current slide header:
    header = Any

    # The current slide footer:
    footer = Any

    # The content to use for the header and footer:
    header_content = Str
    footer_content = Str

    # The images to use for various slide items:
    header_image    = Str
    footer_image    = Str
    bullet_image    = Str
    indented_image  = Str
    multiline_image = Str
    code_image      = Str

    # The alignment to use for header and footer text:
    header_alignment = HorizontalAlignment( 'left' )
    footer_alignment = HorizontalAlignment( 'right' )

    # The themes used for various slide items:
    background_theme = ATheme( '@xform:bg?l50' )
    picture_theme    = ATheme( Theme( '@xform:bg?l50', content = 10 ) )
    header_theme     = ATheme( Theme( '@xform:b?l10S60', content = ( 10, 2 ),
                                      content_font = '30' ) )
    footer_theme     = ATheme( Theme( '@xform:b?l10S60', content = ( 5, 2 ),
                                      content_font = '10' ) )
    bullet_theme     = ATheme( Theme( '@xform:b?l70', content = ( 5, 2 ),
                                      content_font = '20' ) )
    indented_theme   = ATheme( Theme( '@xform:b?l35', content_font = '16',
                                      content = ( 25, 5, 2, 2 ) ) )
    multiline_theme  = ATheme( Theme( '@xform:b?l35', content_font = '20',
                                      content = ( 5, 2 ) ) )
    code_theme       = ATheme( Theme( '@xform:b?l20', content = ( 14, 4 ),
                                      content_font = 'Courier 14' ) )
    error_theme      = ATheme( Theme( '@xform:b?S99', content = ( 5, 2 ),
                                      content_font = '20' ) )

    # The fonts used for various slide items:
    header_font    = Font( '30' )
    footer_font    = Font( '10' )
    bullet_font    = Font( '20' )
    indented_font  = Font( '16' )
    multiline_font = Font( '20' )
    code_font      = Font( 'Courier 14' )

    # The margins used for various slide items:
    bullet_margin    = HasMargin
    indented_margin  = HasMargin
    multiline_margin = HasMargin
    code_margin      = HasMargin
    picture_margin   = HasMargin

    # The method used to handle an item/slide advance:
    slide_advance = SlideAdvance

    # The transition to use when a slide advances:
    slide_transition = SlideTransition

    # The base directory to look for referenced files in:
    file_base = Str

    # Amount of vertical space that a blank line inserts into a slide:
    vertical_space = Int( 15 )

    # Mapping of slide items to equivalent slide items:
    kind_none  = Str( '*' )
    kind_fade  = Str( '-' )
    kind_left  = Str( '<' )
    kind_right = Str( '>' )
    kind_up    = Str( '/' )
    kind_down  = Str( '\\' )

    #-- Facet Default Values ---------------------------------------------------

    def _canvas_default ( self ):
        return PresentationCanvas( editor = self )

    #-- Editor Method Overrides ------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.canvas_control = control = DrawableCanvasControl(
            parent = parent,
            theme  = self.background_theme
        )
        self.adapter   = control()
        control.canvas = self.canvas
        factory        = self.factory
        self.sync_value( factory.titles,   'titles',   'to', is_list = True )
        self.sync_value( factory.selected, 'selected', 'both' )
        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        # Save the title of the currently selected slide so that we can attempt
        # to re-sync the editor with that slide after creating the new slides:
        title = self.selected

        # Reset editor values back to their defaults:
        for name in [
            'global_dict', 'global_code', 'header', 'footer', 'header_content',
            'footer_content', 'header_alignment', 'footer_alignment',
            'background_theme', 'header_theme', 'footer_theme', 'bullet_theme',
            'indented_theme', 'multiline_theme', 'code_theme', 'header_image',
            'footer_image', 'bullet_image', 'indented_image', 'multiline_image',
            'code_image', 'header_font', 'footer_font', 'bullet_font',
            'indented_font', 'multiline_font', 'code_font', 'bullet_margin',
            'indented_margin', 'multiline_margin', 'code_margin',
            'picture_margin', 'slide_advance', 'slide_transition',
            'vertical_space', 'build_slide', 'kind_none', 'kind_fade',
            'kind_left', 'kind_right', 'kind_up', 'kind_down' ]:
            delattr( self, name )

        del self.slides[:]
        del self.canvas.content[:]

        self.file_base      = self.factory.file_base
        self.header_content = '%title'
        self.footer_content = 'Slide %index of %count'

        self._parse_slides( self.value )
        self._trim_text()
        self._process_headers()
        self._exec_global_code()
        slides           = self.slides
        self.titles      = [ slide.title for slide in slides ]
        self.build_slide = self.display_slide = None
        if len( slides ) > 0:
            display_slide = slides[0]
            if title != '':
                for slide in slides:
                    if title == slide.title:
                        display_slide = slide

                        break

            self.show_all      = False
            self.display_slide = display_slide
            self.show_all      = True

    #-- Public Methods ---------------------------------------------------------

    def next_slide ( self ):
        """ Shows the next slide after the current one if possible.
        """
        self._show_slide_at( 1 )


    def previous_slide ( self ):
        """ Shows the previous slide before the current one if possible.
        """
        self._show_slide_at( -1 )


    def first_slide ( self ):
        """ Shows the first slide.
        """
        if len( self.slides ) > 0:
            self.display_slide = self.slides[0]


    def last_slide ( self ):
        """ Shows the last slide.
        """
        if len( self.slides ) > 0:
            self.display_slide = self.slides[-1]


    def select_slide ( self, x, y ):
        """ Allow the user to select the slide to display from a pop-up list
            of slide titles.
        """
        sx, sy = self.adapter.screen_position
        self.edit_facets(
            view = View(
                VGroup(
                    UItem( 'titles',
                           editor = GridEditor(
                               adapter     = TitlesAdapter,
                               operations  = [],
                               show_titles = False,
                               selected    = 'selected' )
                    ),
                    group_theme = '@std:popup'
                ),
                kind         = 'popover',
                popup_bounds = ( sx + x - 100, sy + y - 150, 1, 1 ),
                width        = 200,
                height       = 300
            )
        )


    def run_code ( self ):
        """ Runs any code associated with the current slide.
        """
        inn( self.display_slide ).run_code()


    def export_object ( self, object ):
        """ Exports the object specified by *object*.
        """
        self.factory.object = object

    #-- Private Methods --------------------------------------------------------

    def _parse_slides ( self, text ):
        """ Parses the current editor value into a series of slide objects.
        """
        errors = 0
        for line in text.split( '\n' ):
            errors += self._parse_line( line )
            if errors >= 5:
                break

        return errors


    def _parse_line ( self, line ):
        """ Parses the line of text specified by *line* into a corresponding
            presentation item.
        """
        sline  = line.strip()
        prefix = sline[:1]
        if prefix == '#':
            pass

        elif prefix == '':
            self._add_gap( self.vertical_space )

        elif Digits.match( sline ):
            self._add_gap( eval( sline ) )

        elif sline[:2] == '--':
            self._new_slide( line )

        elif prefix == ':':
            items     = line[1:].strip().split( ' ', 1 )
            raw_data  = '' if len( items ) < 2 else items[1]
            data      = raw_data.strip()
            try:
                name = items[0]
                if name not in LongCommandNames:
                    name = CommandNameMap[ name ]

                if ((name in Evaluate) or
                    (name.endswith( '_theme' ) and
                    (data.find( 'Theme(' ) >= 0))):
                    data = eval( data )

                if name in Execute:
                    if getattr( self, '_' + name )( raw_data ):
                        return self._invalid_line( line )
                else:
                    setattr( self, name, data )
            except:
                return self._invalid_line( line )

        else:
            if self.build_slide is None:
                self._new_slide( '<Unnamed Slide>' )

            if prefix not in KindChars:
                line = '%s* %s' % ( ' '[ line[:1] != ' ': ], sline )

            self._parse_item( line )

        return 0


    def _parse_item ( self, line ):
        """ Parses the specified *line* into a display item for the current
            slide.
        """
        sline = line.strip()
        kind  = sline[:1]
        if kind not in '?|':
            kind = getattr( self, CommandNameMap[ kind ] )

        if kind == '?':
            kind = choice( KindChars[:-2] ) # Don't include '?|'
        elif kind not in KindChars:
            kind = '<'

        content  = sline[1:]
        indented = (line[:1] == ' ')
        body     = self.build_slide.body
        if kind == '|':
            kind = '*'
            if (len( body ) > 0) and isinstance( body[-1], SlideText ):
                return self._as_code(
                    body[-1], content,
                    self.code_theme  if indented else self.multiline_theme,
                    self.code_image  if indented else self.multiline_image,
                    self.code_margin if indented else self.multiline_margin
                )

        content = content.lstrip()
        if (len( content ) > 0) and (content[:1] in '@!'):
            item = SlideImage(
                image  = self._file_name_for( content ),
                theme  = self.picture_theme,
                margin = self.picture_margin
            )
        else:
            item = SlideText(
                text   = content,
                theme  = self.indented_theme if indented else
                         self.bullet_theme,
                image  = self._image_for( self.indented_image if indented else
                                          self.bullet_image ),
                margin = self.indented_margin if indented else
                         self.bullet_margin
            )

        body.append( item.set( kind = kind ) )


    def _file_name_for ( self, value ):
        """ Returns the fully qualified file name based on the specified
            *value*.
        """
        file_name = value.strip()
        if file_name[:1] != '@':
            file_name = join( self.file_base, file_name.lstrip( '!' ).lstrip() )
            if splitext( file_name )[1] == '':
                fn = file_name + '.png'
                if isfile( fn ):
                    file_name = fn
                else:
                    fn = file_name + '.jpg'
                    if isfile( fn ):
                        file_name = fn
                    else:
                        file_name += '.jpeg'

        return file_name


    def _as_code ( self, item, code, theme, image, margin ):
        """ Adds the specified *code* to the specified slide *item*.
        """
        item.theme  = theme
        item.image  = self._image_for( image )
        item.margin = margin
        text        = item.text.lstrip( '\n' )
        ltext       = text.lstrip()
        item.text   = ('%s\n%s' %
                      ( text, code if code[:1] != ' ' else code[1:] ))


    def _invalid_line ( self, line ):
        """ Handles an unrecognized *line*.
        """
        if self.build_slide is None:
            self._new_slide( 'Invalid line' )

        self.build_slide.body.append( SlideText(
            text  = 'Invalid line: %s' % line,
            theme = self.error_theme
        ) )

        return 1


    def _add_gap ( self, vertical_space ):
        """ Adds some vertical space to the current slide.
        """
        slide = self.build_slide
        if (slide is not None) and (len( slide.body ) > 0):
            if isinstance( slide.body[-1], int ):
                slide.body[-1] += vertical_space
            else:
                slide.body.append( vertical_space )


    def _new_slide ( self, line ):
        """ Starts the creation of a new slide.
        """
        title = line.strip( '-' ).strip()
        if title == '':
            title = 'Slide %d' % (len( self.slides ) + 1)

        self.build_slide = slide = Slide(
            title            = title,
            header           = self.header,
            footer           = self.footer,
            slide_transition = self.slide_transition,
            background_theme = self.background_theme,
            slide_advance    = self.slide_advance,
            editor           = self
        )
        self.slides.append( slide )


    def _trim_text ( self ):
        """ Trims trailing white space from all slide text items.
        """
        for slide in self.slides:
            for item in slide.body:
                if isinstance( item, SlideText ):
                    item.text = item.text.rstrip()


    def _process_headers ( self ):
        """ Performs post-parsing initialization of slide headers and footers
            by substituting presentation variables.
        """
        n = len( self.slides )
        for i, slide in enumerate( self.slides ):
            self._substitute( slide, 'header', i, n )
            self._substitute( slide, 'footer', i, n )


    def _substitute ( self, slide, name, i, n ):
        """ Substitutes %values in a slide's header or footer.
        """
        hf = getattr( slide, name )
        if (hf is not None) and isinstance( hf, SlideText ):
            text = hf.text.replace( '%title', slide.title
                         ).replace( '%index', str( i + 1 )
                         ).replace( '%count', str( n ) )
            if text != hf.text:
                new_hf = SlideText()
                new_hf.copy_facets( hf )
                setattr( slide, name, new_hf.set( text = text ) )


    def _exec_global_code ( self ):
        """ Executes any global code for the presentation and uses it to
            initialize the global execution context.
        """
        if self.global_code != '':
            try:
                exec self.global_code in self.global_dict
            except:
                import traceback
                traceback.print_exc()


    def _show_slide_at ( self, increment ):
        """ Shows the slide at the specified *increment* from the current slide.
        """
        index = self.slides.index( self.display_slide ) + increment
        if (index >= 0) and (index < len( self.slides )):
            self.display_slide = self.slides[ index ]


    def _image_for ( self, name ):
        """ Returns the image corresponding to the specified image *name*.
        """
        return (None if name == '' else self._file_name_for( name ))

    #-- Executable Command Methods ---------------------------------------------

    def _execute_file ( self, file_name ):
        """ Attempts to load and execute the file specified by *file_name*.
        """
        text = read_file( self._file_name_for( file_name.strip() ) )

        return (1 if text is None else self._parse_slides( text ))


    def _execute_code ( self, code ):
        """ Adds executable code to the current slide being built.
        """
        if self.build_slide is not None:
            self.build_slide.code += ('\n' + code)
        else:
            self.global_code += ('\n' + code)


    def _execute_user ( self, ignore ):
        """ Defers execution of any Python code for the slide until the user
            requests it to be executed.
        """
        if self.build_slide is not None:
            self.build_slide.auto_execute = False


    def _export_object ( self, code ):
        """ Adds code to export a HasFacets object to the current slide being
            built.
        """
        self._execute_code( '\nexport(%s)' % code )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:file_base' )
    def _file_base_modified ( self ):
        """ Handles the factory 'file_base' being changed.
        """
        self.update_editor()


    @on_facet_set( 'header_font, footer_font, bullet_font, indented_font, multiline_font, code_font' )
    def _font_modified ( self, facet, new ):
        """ Handles one of the presentation fonts being changed.
        """
        theme     = facet[:-4] + 'theme'
        new_theme = Theme()
        new_theme.copy_facets( getattr( self, theme ) )
        new_theme.content_font = new
        setattr( self, theme, new_theme )


    @on_facet_set( 'header_theme, footer_theme' )
    def _theme_modified ( self, facet, new ):
        """ Handles the preseentation header/footer theme being changed.
        """
        base = facet[:-6]
        item = getattr( self, base )
        if item is not None:
            item.theme = new


    @on_facet_set( 'header_content, footer_content, header_image, footer_image, header_alignment, footer_alignment' )
    def _content_modified ( self, facet ):
        """ Handles the presentation header/footer content or alignment being
            changed.
        """
        base      = facet.split( '_', 1 )[0]
        theme     = getattr( self, base + '_theme' )
        alignment = getattr( self, base + '_alignment' )
        content   = getattr( self, base + '_content' )
        if content[:1] in '@!':
            item = SlideImage(
                theme     = theme,
                image     = self._file_name_for( content ),
                alignment = alignment
            )
        else:
            item = SlideText(
                theme     = theme,
                image     = self._image_for( getattr( self, base + '_image' ) ),
                text      = content,
                alignment = alignment
            )

        setattr( self, base, item )


    @on_facet_set( 'canvas:bounds' )
    def _bounds_modified ( self ):
        """ Handles the canvas bounds being changed.
        """
        if self.display_slide is not None:
            self.display_slide.resize()


    def _display_slide_set ( self, old, new ):
        """ Handles the 'display_slide' facet being changed.
        """
        if new is not None:
            if old is not None:
                old.slide_remove()

            self.canvas_control.theme = new.background_theme
            new.slide_display( self.show_all )
            self._no_update = True
            self.selected   = new.title
            self._no_update = False
        else:
            self.selected = ''


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if not self._no_update:
            for item in self.slides:
                if selected == item.title:
                    self.display_slide = item

                    break

    #-- Mouse Event Handlers ---------------------------------------------------

    def wheel ( self, event ):
        """ Handles a mouse wheel event.
        """
        if event.wheel_change != 0:
            slide = self.display_slide
            if slide is not None:
                direction = slide.advance_item( event.wheel_change < 0 )
                if direction < 0:
                    self.previous_slide()
                elif direction > 0:
                    self.show_all = False
                    self.next_slide()
                    self.show_all = True

#-------------------------------------------------------------------------------
#  'PresentationEditor' class:
#-------------------------------------------------------------------------------

class PresentationEditor ( BasicEditorFactory ):
    """ Defines an editor class for viewing the contents of a string as a series
        of one or more presentation 'slides.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _PresentationEditor

    # Event fired when the presentation should update in some way (the possible
    # values are 'next slide', 'previous slide', 'first slide', 'next item',
    # 'previous item', 'slide show'):
    update = Event( facet_value = True )

    # A HasFacets object created by the presentation as the result of an 'xo'
    # command:
    object = Event( facet_value = True )

    # The extended facet name of the currently selected 'slide':
    selected = Str

    # The extended facet name of the list of all 'slide' titles:
    titles = Str

    # The name of the directory to use as the default presentation file base:
    file_base = Directory( facet_value = True )

    # The hold time between slides when displaying a slide show:
    hold_time = Range( 0.5, 60.0, 2.0, facet_value = True )

#-- EOF ------------------------------------------------------------------------
