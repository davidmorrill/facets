"""
Defines an editor for plotting histograms.
"""

#-------------------------------------------------------------------------------
#  todo: Add (optional) mouse drag cursor
#  todo: Tooltips showing current data values (value, label, index)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import floor, ceil, log10

from facets.api \
    import Any, Color, Enum, List, Tuple, Bool, Int, Float, Str, Instance, \
           Theme, ATheme, Font, BasicEditorFactory, on_facet_set

from facets.core.facet_base \
    import xgetattr

from facets.ui.editors.drawable_canvas_editor \
    import _DrawableCanvasEditor

from facets.ui.drawable.drawable \
    import DrawableCanvas, Text, ThemedText, Line, Rectangle

from facets.animation.api \
    import RampTweener, EaseIn

#-------------------------------------------------------------------------------
#  'HistogramBar' class:
#-------------------------------------------------------------------------------

class HistogramBar ( Rectangle ):

    #-- Facet Definitions ------------------------------------------------------

    # The value associated with the histogram bar:
    value = Any

    # The label associated with the histogram bar:
    label = Str

    # The index of the value within the data set:
    index = Int

    # The tooltip for the histogram bar:
    tooltip = Str

    #-- Facet Default Values ---------------------------------------------------

    def _tooltip_default ( self ):
        return 'Value: %s\nLabel: %s\nIndex: %d' % (
            self.value, self.label, self.index
        )

    #-- Mouse Event Handlers ---------------------------------------------------

    def motion ( self, x, y ):
        owner = self.owner
        if self.value is not None:
            tooltip  = self.tooltip
            subtitle = owner.subtitle
            if subtitle is not None:
                subtitle.text = owner.factory.subtitle % (
                    '(%s)' % tooltip.replace( '\n', ', ' )
                )
            else:
                owner.tooltip = tooltip

        cursor = owner.cursor
        if cursor is not None:
            x0, x1    = cursor.p0[0], cursor.p1[0]
            cursor.p0 = ( x0, y )
            cursor.p1 = ( x1, y )

#-------------------------------------------------------------------------------
#  'HistogramCanvas' class:
#-------------------------------------------------------------------------------

class HistogramCanvas ( DrawableCanvas ):
    """ Defines a DrawableCanvas for plotting histograms.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The sequence of data values to create the histogram from:
    data = Any # List, Tuple, numpy array

    # The labels used for the histogram:
    labels = List # ( Str )

    # The editor factory containing the histogram attributes to use:
    factory = Any # Instance( EditorFactory )

    # Dummy Text object used for text size calculations:
    text = Instance( Text )

    # The Line representing the mouse cursor:
    cursor = Instance( Line )

    # The ThemedText used for the subtitle if it contains a '%s':
    subtitle = Instance( ThemedText )

    # The graphics context to use for drawing/calculations:
    graphics = Any # Instance( Graphics )

    # The height of a text label:
    label_height = Int

    # The y-axis range (as a tuple of the form: ( min, max, increment )):
    y_range = Tuple( Float, Float, Float )

    # The y-coordinates of all y-axis label centerpoints:
    y_ticks = List # ( Int )

    #-- Default Facet Values ---------------------------------------------------

    def _text_default ( self ):
        return Text( font = self.factory.font )


    def _label_height_default ( self ):
        return self.text.set( text = 'M' ).text_size( self.graphics )[1]


    def _y_range_default ( self ):
        data_min = min( min( self.data ), 0.0 )
        data_max = max( self.data )
        data_dy  = data_max - data_min
        dy       = 10.0 ** int( 0.999 * log10( data_dy ) )
        steps    = data_dy / dy
        if steps < 8.0:
            if steps >= 4.0:
                dy /= 2.0
            else:
                dy = dy / 4.0 if steps >= 2.0 else dy / 5.0

        return ( dy * floor( data_min / dy ), dy * ceil( data_max / dy ), dy )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Paints the contents of the canvas in the graphics context specified
            by *g*.
        """
        if len( self.content ) == 0:
            self.graphics = g
            self._create_histogram()
            self.graphics = None

        super( HistogramCanvas, self ).paint( g )

    #-- Private methods --------------------------------------------------------

    def _create_histogram ( self ):
        """ Create the list of drawable items constituting the histogram using
            the current 'data' and 'labels' values.
        """
        x, y, dx, dy = self.bounds
        factory      = self.factory

        # Create the title (if requested):
        titles = []
        title  = factory.title
        if title != '':
            tdy = self.label_height + 12
            titles.append( ThemedText(
                text      = title,
                alignment = 'center',
                origin    = ( x, y ),
                size      = ( dx, tdy ),
                theme     = Theme( '@xform:bg?l10' )
            ) )
            y  += tdy
            dy -= tdy

        # Create the subtitle (if requested):
        subtitle = factory.subtitle
        if subtitle != '':
            tdy = self.label_height + 4
            subtitle_item = ThemedText(
                text      = subtitle,
                alignment = 'center',
                origin    = ( x, y + dy - tdy ),
                size      = ( dx, tdy ),
                theme     = Theme( '@xform:bg?L27', content = ( 5, 5, 2, 0 ) )
            )
            titles.append( subtitle_item )
            if subtitle.find( '%s' ) >= 0:
                self.subtitle      = subtitle_item
                subtitle_item.text = subtitle % ''

            dy -= tdy

        # Add and animate any titles:
        self._animate_items( titles )
        self.content.extend( titles )

        # Get the height of the x-axis:
        x_axis_dy = self.label_height + 4

        # Margin at top of histogram:
        y_top = (self.label_height / 2) + 3

        # Get the height of the y-axis:
        y_axis_dy = dy - x_axis_dy - y_top - 2

        # Add the plot background:
        self.content.append( Rectangle(
            origin     = ( x, y ),
            size       = ( dx, dy ),
            pen        = None,
            brush      = factory.bg_color,
            anti_alias = False
        ) )

        # Create the y-axis and get its resulting width:
        y_axis_dx = self._create_y_axis( x + 4, y + y_top, dx / 8, y_axis_dy )

        # Add the rightmost vertical plot line:
        self.content.append( Line(
            p0         = ( x + dx - 6, y + y_top ),
            p1         = ( x + dx - 6, y + y_top + y_axis_dy - 1 ),
            pen        = factory.label_color,
            anti_alias = False
        ) )

        # Create the y-axis tick marks:
        x_tick    = x + y_axis_dx + 4
        x_tick_dx = dx - y_axis_dx - 10
        self._create_ticks( x_tick, x_tick_dx )

        # Create the histogram bars:
        label_x, label_dx = self._create_bars(
            x + y_axis_dx + 4, y + y_top,
            dx - y_axis_dx - 10, dy - x_axis_dy - y_top - 3
        )

        # Create the x_axis:
        self._create_x_axis(
            x + y_axis_dx + 3, y + y_top + y_axis_dy - 1,
            dx - y_axis_dx - 9, x_axis_dy, label_x, label_dx
        )

        # Create the Line used for the mouse cursor (if requested):
        if factory.show_cursor:
            self.cursor = Line(
                p0         = ( x_tick, -1000 ),
                p1         = ( x_tick + x_tick_dx - 1, -1000 ),
                pen        = 0xFF0000,
                anti_alias = False
            )
            self.content.append( self.cursor )


    def _create_y_axis ( self, x, y, dx, dy ):
        """ Create the drawable items representing the y-axis within the bounds
            specified by *x*, *y*, *dx*, *dy* ) and returns the width of the
            resulting axis.
        """
        # Give up if there is no room to draw the y-axis:
        if dy <= 0:
            return 0

        # Create all of the y-axis labels:
        y_min, y_max, y_incr = self.y_range
        if y_incr == float( int( y_incr ) ):
            y_min, y_max, y_incr = int( y_min ), int( y_max ), int( y_incr )

        n        = int( round( (y_max - y_min) / y_incr ) )
        label_dy = float( dy - 1 ) / n
        tdx      = dx - 5
        tdy      = self.label_height + 2
        dy2      = self.label_height / 2.0
        yt       = y_last = y + dy - 1.0
        y_end    = y + dy2 + 5
        y_units  = self.factory.y_units
        y_ticks  = []
        max_dx   = 0
        y_labels = []
        if yt > y_end:
            text, tdxc  = self._text_for( '%s%s' % ( y_min, y_units ), tdx )
            max_dx      = tdxc
            text.origin = ( x, int( round( yt - dy2 ) ) )
            y_labels.append( ( text, tdxc ) )

        while n > 0:
            n     -= 1
            y_min += y_incr
            yt    -= label_dy
            if (((y_last - yt) >= tdy) and (yt > y_end)) or (n == 0):
                y_last      = yt
                text, tdxc  = self._text_for( '%s%s' % ( y_min, y_units ), tdx )
                max_dx      = max( tdxc, max_dx )
                text.origin = ( x, int( round( yt - dy2 ) ) )
                y_labels.append( ( text, tdxc ) )
                y_ticks.append( int( round( yt ) ) )

        # Adjust the x coordinate of all text labels to right align them:
        for text, tdxc in y_labels:
            lx, ly      = text.origin
            text.origin = ( lx + (max_dx - tdxc), ly )

        # Get all the labels to add to the canvas content:
        items = [ item[0] for item in y_labels ]

        # Add the y-axis line:
        items.append( Line(
            p0         = ( x + max_dx + 5, y ),
            p1         = ( x + max_dx + 5, y + dy - 1 ),
            pen        = self.factory.label_color,
            anti_alias = False
        ) )

        # Animate and add all items to the graphics context:
        self._animate_items( items )
        self.content.extend( items )

        # Save the y-axis tick marks/lines y_coordinates:
        self.y_ticks = y_ticks

        # Return the actual width of the y_axis:
        return (max_dx + 6)


    def _create_x_axis ( self, x, y, dx, dy, label_x, label_dx ):
        """ Creates the drawable items representing the x-axis within the bounds
            specified by *x*, *y*, *dx*, *dy* ), and whose first label is
            centered at *label_x*, with labels spaced every *label_dx* pixels.
        """
        # Add the x-axis line:
        self.content.append( Line(
            p0         = ( x, y ),
            p1         = ( x + dx - 1, y ),
            pen        = self.factory.label_color,
            anti_alias = False
        ) )

        # Create the labels:
        labels = []
        last_x = x - 4
        for label in self.labels:
            text, text_dx = self._text_for( label, label_dx - 4 )
            lx            = int( round( label_x - (text_dx / 2.0) ) )
            if (lx - 4) >= last_x:
                text.origin = ( lx, y + 3 )
                labels.append( text )
                last_x = lx + text_dx

            label_x += label_dx

        # Add and animate the labels:
        self._animate_items( labels )
        self.content.extend( labels )


    def _create_bars ( self, x, y, dx, dy ):
        """ Creates the drawable items representing the histogram bars within
            the bounds specified by *x*, *y*, *dx*, *dy* ).
        """
        factory = self.factory
        data    = self.data
        n       = len( data )
        spacing = factory.spacing
        if 0.0 < spacing < 1.0:
            bar_dx = ((1.0 - spacing) * dx) / (spacing + n)
            gap    = (spacing * bar_dx) / (1.0 - spacing)
        else:
            bar_dx = (( dx - spacing ) / n) - spacing
            gap    = spacing

        bdx = bar_dx + gap
        if dy > 0:
            bars            = []
            xc              = x + gap
            y_min, y_max, _ = self.y_range
            y_range         = y_max - y_min
            y0              = y + dy
            brush           = factory.bar_color
            ibar_dx         = int( round( bar_dx ) )
            labels          = self.labels
            show_tooltip    = factory.show_tooltip
            for i, value in enumerate( data ):
                bar_dy = int( round( ((value - y_min) * dy) / y_range ) )
                if bar_dy > 0:
                    bars.append(
                        HistogramBar(
                            origin     = ( int( round( xc ) ), y0 - bar_dy ),
                            size       = ( ibar_dx, bar_dy + 1 ),
                            brush      = brush,
                            anti_alias = False
                        )
                    )
                    if show_tooltip:
                        bars[-1].set(
                            value = value,
                            label = labels[ i ],
                            index = i
                        )

                xc += bdx

            self._animate_bars( bars )
            self.content.extend( bars )

        return ( x + gap + (bar_dx / 2.0), bdx )


    def _create_ticks ( self, x, dx ):
        """ Creates the y-axis tick marks/lines.
        """
        pen   = self.factory.line_color
        x1    = x + dx - 1
        lines = [
            Line( p0 = ( x, y), p1 = ( x1, y), pen = pen, anti_alias = False )
            for y in self.y_ticks
        ]
        lines[-1].pen = self.factory.label_color

        # Add and animate the tick marks/lines:
        self._animate_items( lines )
        self.content.extend( lines )

        del self.y_ticks[:]


    def _text_for ( self, text, dx ):
        """ Returns a drawable Text object for *text* which will have a width
            <= dx.
        """
        # fixme: Implement this completely...
        text_item = Text(
            text  = text,
            font  = self.factory.font,
            color = self.factory.label_color
        )

        return ( text_item, text_item.text_size( self.graphics )[0] )


    def _animate_bars ( self, bars ):
        """ Sets up the animation for histogram *bars*.
        """
        if self.factory.animate:
            scale = 0.6 / len( bars )
            for i, bar in enumerate( bars ):
                bdx, bdy   = bar.size
                bx, by     = bar.origin
                bar.size   = ( bdx, 0 )
                bar.origin = ( bx, by + bdy )
                bar.animate_facet( 'size', 3.5, ( bdx, -bdy ),
                    tweener = RampTweener(
                        EaseIn, start = 0.2 + (scale * (i - 1)), cycle = 0.25
                    )
                )


    def _animate_items ( self, items ):
        """ Sets up the animation for drawable graphics *items*.
        """
        if self.factory.animate:
            for item in items:
                item.opacity = 0.0
                item.animate_facet( 'opacity', 1.5, 1.0 )

    #-- Facet Event handlers ---------------------------------------------------

    @on_facet_set( 'data, labels' )
    def _histogram_modified ( self ):
        """ Handles any of the facets affecting the content of the histogram
            being modified.
        """
        del self.y_range
        del self.content[:]


    def _bounds_set ( self, bounds ):
        """ Handles the 'bounds' facet being changed.
        """
        self._histogram_modified()

        super( HistogramCanvas, self )._bounds_set( bounds )

#-------------------------------------------------------------------------------
#  '_HistogramEditor' class:
#-------------------------------------------------------------------------------

class _HistogramEditor ( _DrawableCanvasEditor ):
    """ Defines an editor for plotting histograms.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Indicate the editor is scrollable:
    scrollable = True

    #-- Public Methods ---------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        if self._control.canvas is None:
            self._control.canvas = HistogramCanvas()

        canvas = self._control.canvas
        labels = self.factory.labels
        data   = self.value
        if (len( data ) == 2) and (labels is None):
            data, labels = data
        elif isinstance( labels, basestring ):
            labels = xgetattr( aelf.object, labels, None )

        if labels is None:
            labels = [ str( i ) for i in xrange( 1, len( data ) + 1 ) ]

        n = len( data )
        if len( labels ) == (n + 1):
            labels = [ (labels[ i + 1 ] + labels[ i ]) / 2.0
                       for i in xrange( n ) ]

        for i in xrange( n ):
            label = labels[ i ]
            if not isinstance( label, basestring ):
                labels[ i ] = self.string_value( label )

        x_units = self.factory.x_units
        if x_units != '':
            labels = [ '%s%s' % ( label, x_units ) for label in labels ]

        canvas.set( data = data, labels = labels, factory = self.factory )
        self._control.refresh()

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

class HistogramEditor ( BasicEditorFactory ):
    """ Editor factory for histogram editors.

        The editor data can either be a sequence of data values, in which case
        the 'labels' facet is used to specify the data labels, or it can be a
        tuple of the form: ( data, labels ). If the length of labels is one
        greater than the length of data, it is assumed to specify the bin
        start/end ranges for the data (e.g. as returned by the numpy.histogram
        function).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the Editor class to be instantiated:
    klass = _HistogramEditor

    # The units used for the x-axis:
    x_units = Str

    # The units used for the y-axis:
    y_units = Str

    # Histogram title (optional):
    title = Str

    # Histogram subtitle (optional):
    subtitle = Str

    # The color to use for the histogram bars. Some nice alternate choices are:
    # - 0xFF5656 = a red
    # - 0xFACA0A = a yellow
    # - 0xCBC689 = a gold
    # - 0x6BC689 = a green
    # - 0xEEA85C = an orange
    bar_color = Color( 0x6DADDD )

    # The background color for the histogram plot:
    bg_color = Color( 0xEAEAEA )

    # The axis and label colors:
    label_color = Color( 0x000000 )

    # The color used to draw tick lines:
    line_color = Color( 0xB8B8B8 )

    # The labels to use for the histogram data bars (it should either be a
    # sequence of strings or numbers, or the name of the facet containing the
    # sequence).
    # Note: If the sequence has one more element than the data, it is assumed
    # to specify the start/end values for each data "bin" (e.g. as returned by
    # the numpy.histogram function):
    labels = Any

    # The strategy to use when there is not enough room for all labels:
    label_mode = Enum( 'skip', 'x...', 'x...x', '...x' )

    # The amount of space between two histogram bars (the value can either be
    # in pixels, or a fraction between 0.0 and 1.0 indicating the width of the
    # gap as a percentage of each bar's available space):
    spacing = Float( 0.1 )

    # The theme to use for displaying the content:
    theme = ATheme( facet_value = True )

    # Should a tooltip be shown when mousing over histogram bars?
    show_tooltip = Bool( True )

    # Should a horizontal mouse cursor track mousing over histogram bars?
    show_cursor = Bool( True )

    # Should the histogram be animated?
    animate = Bool( False )

#-- EOF ------------------------------------------------------------------------