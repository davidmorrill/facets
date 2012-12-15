"""
Another example of using the <b>CustomControlEditor</b> and <b>ControlEditor</b>
classes to create a custom editor and control.

In this example, we create a graphical editor for displaying numeric values
using an LED-style display (think old clock radios). The editor supports
specifying the number of LED digits to display and automatically scales the
display based on the control size.

We also make use of the Facets animation system to animate the demo by having
them continuously count different facet values up and down so that you can see
the <b>LEDEditor</b> automatically update the display as the associated facets
change value.

The <b>_LEDEditor</b> class also makes use of the facets <i>led</i> image
library, which contains images of each the various LED digits, an empty LED and
a minus sign. The control automatically scales the images up or down as needed
when the control changes size using the <b>AnImageResource</b> class's
<b><i>scale</i></b> method.

If you look at the images in the <i>led</i> image library, you'll notice that
each LED image is actually monochromatic. The green LED color is applied when
the images are loaded using an encoded <b><i>HLSA</i></b> image transform (see
the string following the '?' character in the <b><i>image_for</i></b> call).
This is a very powerful technique that can be used to transform images as
needed.

To make sure the animation is stopped correctly, the <b>LEDControl</b> class
uses the custom <b>LEDHandler</b> <i>handler</i> class to stop the animation
when the view is closed.

Finally, note the use of the <b>PrototypedFrom</b> facet in the
<b>_LEDEditor</b> class to create an alias to its <i>factory</i> object's
<b><i>digits</i></b> value.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Any, Range, Int, PrototypedFrom, View, VSplit, Item, \
           Handler

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.ui_facets \
    import image_for

#-- Global data ----------------------------------------------------------------

# The base images the LED digits are derived from:
LEDDigits = [ image_for( '@led:D%s?H32S~H14l11S|l16' % c )
              for c in '0123456789MB' ]
LEDRatio  = float( LEDDigits[0].width ) / LEDDigits[0].height

#-- _LEDEditor class -----------------------------------------------------------

class _LEDEditor ( ControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The number of digits to display:
    digits = PrototypedFrom( 'factory' )

    # The images used to display each of the digits:
    images = Any

    #-- ThemedWindow Method Overrides ------------------------------------------

    def paint ( self, g ):
        x      = 0
        images = self.images
        y      = (self.control.client_size[1] - images[0].height) / 2
        for d in str( self.value ).rjust( self.digits )[ -self.digits: ]:
            i = '0123456789- '.find( d )
            if i < 0:
                i = 11

            image = images[ i ]
            g.draw_bitmap( image.bitmap, x, y )
            x += image.width

    def resize ( self, event ):
        """ Handles the control being resized.
        """
        dx, dy      = self.control.client_size
        ddx         = min( int( LEDRatio * dy ), dx / self.digits )
        self.images = [ image.scale( ( ddx, 0 ) ) for image in LEDDigits ]

        super( _LEDEditor, self ).resize( event )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        if control is not None:
            control.size_policy = ( 'expanding', 'expanding' )
            control.min_size    = ( 50, 13 )

#-- LEDEditor class ------------------------------------------------------------

class LEDEditor ( CustomControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The custom control class to be instantiated:
    klass = _LEDEditor

    # The number of digits to display:
    digits = Range( 1, 20, 5 )

#-- LEDHandler class ----------------------------------------------------------

class LEDHandler ( Handler ):

    def closed ( self, info, is_ok ):
        info.object.halt_animated_facets()

#-- LEDControl class -----------------------------------------------------------

class LEDControl ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    count_1 = Int
    count_2 = Int

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VSplit(
            Item( 'count_1', editor = LEDEditor() ),
            Item( 'count_2', editor = LEDEditor() )
        ),
        width   = 280,
        height  = 150,
        handler = LEDHandler
    )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        self.animate_facet( 'count_1',  10.0, 1500,  0, repeat = 0 )
        self.animate_facet( 'count_2', 120.0,  -60, 60, repeat = 0 )

#-- Create the demo ------------------------------------------------------------

demo = LEDControl

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
