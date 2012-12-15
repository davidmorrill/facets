"""
Defines the various color editors and their editor factories.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from colorsys \
    import rgb_to_hls, hls_to_rgb

from facets.api \
    import Bool, Instance, Str, RGBFloat, Tuple, Float, Any, Image,    \
           on_facet_set, View, Item, toolkit, UIEditor, EditorFactory, \
           BasicEditorFactory

from facets.ui.editor_factory \
    import SimpleEditor, ReadonlyEditor

from facets.ui.controls.themed_window \
    import ThemedWindow

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The color drawn around the edges of the HLSSelector:
EdgeColor = ( 64, 64, 64 )

# The text colors used to contrast with the colored background:
Black = ( 0, 0, 0 )
White = ( 255, 255, 255 )

#-------------------------------------------------------------------------------
#  'ColorEditor' class:
#-------------------------------------------------------------------------------

class ColorEditor ( EditorFactory ):
    """ Editor factory for color editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the underlying color facet mapped?
    mapped = Bool( True )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View( [ 'mapped{Is value mapped?}', '|[]>' ] )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleColorEditor( factory     = self,
                                  ui          = ui,
                                  object      = object,
                                  name        = name,
                                  description = description )


    def custom_editor ( self, ui, object, name, description ):
        return CustomColorEditor( factory     = self,
                                  ui          = ui,
                                  object      = object,
                                  name        = name,
                                  description = description )


    def text_editor ( self, ui, object, name, description ):
        return TextColorEditor( factory     = self,
                                ui          = ui,
                                object      = object,
                                name        = name,
                                description = description )


    def readonly_editor ( self, ui, object, name, description ):
        return ReadonlyColorEditor( factory     = self,
                                    ui          = ui,
                                    object      = object,
                                    name        = name,
                                    description = description )

    #-- Public Methods ---------------------------------------------------------

    def to_toolkit_color ( self, editor ):
        """ Gets the GUI toolkit specific color equivalent of the object facet.
        """
        if self.mapped:
            return getattr( editor.object, editor.name + '_' )

        return getattr( editor.object, editor.name )


    def from_toolkit_color ( self, color ):
        """ Gets the application equivalent of a GUI toolkit specific value.
        """
        return color


    def str_color ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        if isinstance( color, basestring ):
            return color

        color = toolkit().from_toolkit_color( color )
        if (len( color ) < 4) or (color[3] == 255):
            return "(%d,%d,%d)" % color[:3]

        return "(%d,%d,%d,%d)" % color

#-------------------------------------------------------------------------------
#  'SimpleColorEditor' class:
#-------------------------------------------------------------------------------

class SimpleColorEditor ( Editor ):

    #-- Facet Definitions ------------------------------------------------------

    # The HLSSelector control used by the editor:
    selector = Instance( 'BaseHLSSelector' )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.selector = self.create_selector( parent )
        self.adapter  = self.selector()

        self.set_tooltip()


    def create_selector ( self, parent ):
        """ Creates the HLS selector for this style of editor.
        """
        return SimpleHLSSelector( parent = parent )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if not self._no_update:
            self.selector.color = self.value

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'selector:color' )
    def _color_modified ( self, color ):
        self._no_update = True
        self.value      = color
        self._no_update = False

#-------------------------------------------------------------------------------
#  'CustomColorEditor' class:
#-------------------------------------------------------------------------------

class CustomColorEditor ( SimpleColorEditor ):

    #-- Public Methods ---------------------------------------------------------

    def create_selector ( self, parent ):
        """ Creates the HLS selector for this style of editor.
        """
        return CustomHLSSelector( parent = parent )

#-------------------------------------------------------------------------------
#  'TextColorEditor' class:
#-------------------------------------------------------------------------------

class TextColorEditor ( SimpleEditor ):
    """ Text style of color editor, which displays a text field whose
        background color is the color value. Selecting the text field displays
        a dialog box for selecting a new color value.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The color sample control used to display the current color:
    color_sample = Any

    # Is the editor busy (which means any popups should not close right now)?
    busy = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def popup_editor ( self ):
        """ Invokes the pop-up editor for an object facet.
        """
        # Fixes a problem with the edit field having the focus:
        if self.adapter.mouse_capture:
            self.adapter.mouse_capture = False

        self.object.edit_facets( view = View(
                Item(
                    self.name,
                    id         = 'color_editor',
                    show_label = False,
                    padding    = -4,
                    editor     = PopupColorEditor( factory = self.factory )
                ),
                kind = 'popup'
            ),
            parent = self.adapter
        )


    def create_control ( self, parent ):
        """ Creates the control to use for the simple editor.
        """
        self.color_sample = ColorSample( parent = parent )

        return self.color_sample()


    def update_object_from_swatch ( self, color ):
        """ Updates the object facet when a color swatch is clicked.
        """
        self.value = color
        self.update_editor()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.color_sample.text = self.str_value
        set_color( self )


    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color )

#-------------------------------------------------------------------------------
#  'ReadonlyColorEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyColorEditor ( ReadonlyEditor ):
    """ Read-only style of color editor, which displays a read-only text field
        whose background color is the color value.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.adapter = ColorSample( parent = parent )()

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        set_color( self )

#-------------------------------------------------------------------------------
#   Helper Functions:
#-------------------------------------------------------------------------------

def set_color ( editor ):
    """  Sets the color of the specified color control.
    """
    color                    = editor.factory.to_toolkit_color( editor )
    control                  = editor.adapter
    control.background_color = color
    color                    = toolkit().from_toolkit_color( color )
    if (color[0] > 192) or (color[1] > 192) or (color[2] > 192):
        control.foreground_color = Black
    else:
        control.foreground_color = White

    control.refresh()

#-------------------------------------------------------------------------------
#  'ColorSample' class:
#-------------------------------------------------------------------------------

class ColorSample ( ThemedWindow ):

    #-- Facet Definitions ------------------------------------------------------

    # The text to display in the control:
    text = Str

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the underlying 'control' being created.
        """
        control.min_size = ( 20, control.text_size( 'My' )[1] + 8 )

    #-- Control Event Handlers -------------------------------------------------

    def _paint ( self, event ):
        control = self.control
        g       = control.graphics
        g.pen   = EdgeColor
        g.brush = control.background_color
        dx, dy  = control.size
        g.draw_rectangle( 0, 0, dx, dy )

        if self.text != '':
            g.font = control.font
            g.draw_text( self.text, 3, 3 )

#-------------------------------------------------------------------------------
#   'BaseHLSSelector' class:
#-------------------------------------------------------------------------------

class BaseHLSSelector ( ThemedWindow ):
    """ Abstract base class for creating HSL color space color selectors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Does this control handle keyboard input (override)?
    handle_keys = True

    # The current selected color:
    color = RGBFloat( 0xFF0000 )

    # The HLS values corresponding to the current color:
    hls = Tuple( Float, Float, Float )

    #-- Facet Default Values ---------------------------------------------------

    def _hls_default ( self ):
        return self._to_hls( toolkit().from_toolkit_color( self.color ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the underlying 'control' being created.
        """
        control.size = control.min_size = self.size


    def _color_set ( self, color ):
        """ Updates the display when the current color changes.
        """
        self.hls = self._to_hls( color )
        self.refresh()

    #-- Control Event Handlers -------------------------------------------------

    def left_down ( self, event ):
        if self.control.enabled:
            self._active = True
            self.control.mouse_capture = True
            self._set_color( event )


    def left_up ( self, event ):
        if self._active:
            self._active = False
            self.control.mouse_capture = False
            self._set_color( event )


    def motion ( self, event ):
        if self._active:
            self._set_color( event )

    #-- Private Methods --------------------------------------------------------

    def _to_hls ( self, color ):
        """ Returns a GUI toolkit neutral color converted to an HLS tuple.
        """
        return rgb_to_hls( *color )


    def _from_hls ( self, h, l, s ):
        """ Converts HLS values to a GUI toolkit neutral color.
        """
        return tuple(
            [ int( round( c * 255.0 ) ) for c in hls_to_rgb( h, l, s ) ]
        )

#-------------------------------------------------------------------------------
#   'SimpleHLSSelector' class:
#-------------------------------------------------------------------------------

class SimpleHLSSelector ( BaseHLSSelector ):
    """ Simple 'one line' multi-bar HSL color space color selector.
    """

    #-- Facet Definitions ------------------------------------------------------

    size = Tuple( 200, 16 )

    #-- Control Event Handlers ------------------------------------------------

    def paint ( self, g ):
        """ Paints the HLS selector on the display.
        """
        # Calculate the size and position of each HLS selector:
        wdx, wdy  = self.control.size
        self._sdx = sdx = ((wdx - 12) / 4) - 2
        self._hx0 = hx0 = 1
        self._sx0 = sx0 = hx0 + sdx + 6
        self._lx0 = lx0 = sx0 + sdx + 6
        self._cx0 = cx0 = lx0 + sdx + 6

        # Draw the selector boundaries:
        g.pen   = EdgeColor
        g.brush = None
        g.draw_rectangle( hx0 - 1, 0, sdx + 2, wdy )
        g.draw_rectangle( lx0 - 1, 0, sdx + 2, wdy )
        g.draw_rectangle( sx0 - 1, 0, sdx + 2, wdy )

        # Draw the current color sample:
        g.brush = self.color
        g.draw_rectangle( cx0 - 1, 0, sdx + 2, wdy )

        # Now fill the contents of each of the HLS selectors:
        h, l, s = self.hls
        range   = sdx - 1
        step    = 1.0 / range
        ey      = wdy - 2

        # Draw the 'H' selector color range based upon the current color:
        hp = 0.0
        for x in xrange( hx0, hx0 + sdx ):
            g.pen = self._from_hls( hp, 0.5, 1.0 )
            g.draw_line( x, 1, x, ey )
            hp += step

        # Draw the 'S' selector color range based upon the current color:
        sp = 1.0
        for x in xrange( sx0, sx0 + sdx ):
            g.pen = self._from_hls( h, 0.5, sp )
            g.draw_line( x, 1, x, ey )
            sp -= step

        # Draw the 'L' selector color range based upon the current color:
        lp = 1.0
        for x in xrange( lx0, lx0 + sdx ):
            g.pen = self._from_hls( h, lp, 1.0 )
            g.draw_line( x, 1, x, ey )
            lp -= step

        # Draw the current HLS selectors:
        g.pen = EdgeColor
        self._draw_selector( g, wdy, hx0 + int( round( range * h ) ) )
        self._draw_selector( g, wdy, sx0 + int( round( range * (1.0 - s) ) ) )
        self._draw_selector( g, wdy, lx0 + int( round( range * (1.0 - l) ) ) )

    #-- Private Methods --------------------------------------------------------

    def _draw_selector ( self, g, dy, x ):
        """ Draws the current position of one of the HLS selectors.
        """
        g.draw_line( x, 3, x, dy - 4 )
        g.draw_line( x - 2, 1, x + 2, 1 )
        g.draw_line( x - 2, dy - 2, x + 2, dy - 2 )
        g.draw_line( x - 1, 2, x + 1, 2 )
        g.draw_line( x - 1, dy - 3, x + 1, dy - 3 )


    def _set_color ( self, event ):
        """ Sets the color based on the current mouse position.
        """
        x, y   = event.x, event.y
        dx, dy = self.control.size
        if 0 <= y < dy:
            h, l, s = h0, l0, s0 = self.hls
            sdx     = float( self._sdx - 1 )

            if self._hx0 <= x <= self._hx0 + sdx:
                h = ( x - self._hx0 ) / sdx
            elif self._lx0 <= x <= self._lx0 + sdx:
                l = 1.0 - ((x - self._lx0) / sdx)
            elif self._sx0 <= x <= self._sx0 + sdx:
                s = 1.0 - ((x - self._sx0) / sdx)
            else:
                return

            if (h != h0) or (l != l0) or (s != s0):
                self.color = self._from_hls( h, l, s )
                self.hls   = ( h, l, s )
                if ((l == 0.0) or (l == 1.0) ):
                    self.refresh()

#-------------------------------------------------------------------------------
#   'CustomHLSSelector' class:
#-------------------------------------------------------------------------------

class CustomHLSSelector ( BaseHLSSelector ):
    """ A larger (i.e. custom) HSL color space color selector.
    """

    #-- Class Constants --------------------------------------------------------

    # Override the default size for the window:
    size = Tuple( 246, 102 )

    #-- Facet Definitions ------------------------------------------------------

    # The HS color map image:
    color_map = Image( '@facets:hs_color_map' )

    #-- Control Event Handlers -------------------------------------------------

    def paint ( self, g ):
        """ Paints the HLS selector on the display.
        """
        # Draw the current color sample (if there is room):
        g.pen    = EdgeColor
        wdx, wdy = self.control.size
        if wdx >= 230:
            g.brush = self.color
            g.draw_rectangle( 228, 0, wdx - 228, 102 )

        # Draw the 'HS' color map and frame:
        g.brush = None
        g.draw_rectangle( 0, 0, 202, 102 )
        g.draw_bitmap( self.color_map.bitmap, 1, 1 )

        # Draw the 'L' selector frame:
        g.draw_rectangle( 206, 0, 18, 102 )

        # Draw the 'L' selector color range based upon the current color:
        h, l, s = self.hls
        lp      = 1.0
        lstep   = 1.0 / 99
        for y in xrange( 1, 101 ):
            g.pen = self._from_hls( h, lp, s )
            g.draw_line( 207, y, 222, y )
            lp -= lstep

        # Draw the current 'HS' selector:
        g.pen   = Black
        g.brush = None
        g.draw_circle( int( round( 199 * h ) ) + 1,
                       int( round(  99 * ( 1.0 - s ) ) ) + 1, 3 )

        # Draw the current 'L' selector:
        y = int( round( 99 * ( 1.0 - l ) ) ) + 1
        g.draw_line( 203, y,     226, y )
        g.draw_line( 204, y - 1, 204, y + 1 )
        g.draw_line( 225, y - 1, 225, y + 1 )
        g.draw_line( 205, y - 2, 205, y + 2 )
        g.draw_line( 224, y - 2, 224, y + 2 )

    #-- Private Methods --------------------------------------------------------

    def _set_color ( self, event ):
        """ Sets the color based on the current mouse position.
        """
        x, y = event.x, event.y

        if 1 <= y <= 100:
            h, l, s = h0, l0, s0 = self.hls

            if 1 <= x <= 200:
                h = (x - 1) / 199.0
                s = 1.0 - ((y - 1) / 99.0)
            elif 206 <= x <= 223:
                l = 1.0 - ((y - 1) / 99.0)
            else:
                return

            if (h != h0) or (l != l0) or (s != s0):
                self.color = self._from_hls( h, l, s )
                self.hls   = ( h, l, s )
                if (l == 0.0) or (l == 1.0):
                    self.refresh()

#-------------------------------------------------------------------------------
#  'PopupColorEditor' editor definition:
#-------------------------------------------------------------------------------

class _PopupColorEditor ( UIEditor ):

    #-- Public Methods ---------------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        return self.object.edit_facets(
            parent = parent,
            view   = View(
                Item( self.name,
                      id         = 'color_editor',
                      style      = 'custom',
                      show_label = False,
                      editor     = self.factory.factory
                ),
                kind = 'editor'
            )
        )

#-------------------------------------------------------------------------------
#  'PopupColorEditor' class:
#-------------------------------------------------------------------------------

class PopupColorEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    klass = _PopupColorEditor

    # The editor factory to be used by the sub-editor:
    factory = Instance( EditorFactory )

#-- EOF ------------------------------------------------------------------------