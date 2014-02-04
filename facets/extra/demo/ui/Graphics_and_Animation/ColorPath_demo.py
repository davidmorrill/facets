"""
# ColorPath Demo #

Provides a simple demonstration of the Facets animation system's **ColorPath**
class, which allows animating color changes in the HLSA (Hue, Lightness,
Saturation, Alpha) color space.

The demo animates four different colors using four different paths through HLSA
color space:

- **HLSPath**: Animates between *begin_color* and *end_color* along the hue,
  lightness and saturation axes.
- **HPath**: Animates between *begin_color* and *end_color* only along the hue
  axis.
- **LPath**: Animates between *begin_color* and *end_color* only along the
  lightness axis.
- **SPath**: Animates between *begin_color* and *end_color* only along the
  saturation axis.

Select a new *Begin color* and/or *End color* value to update the animation
begin and end colors. Note that for all paths other than **HLSPath**, the end
color of the animation may not be the same as the end color selected, since the
path only follows one of the possible HLS axes from the begin color to the end
color.

You can also change the cycle time for the animation by adjusting the *Time*
value up or down.

Note that the demo imports four predefined color paths (i.e. **HLSColorPath**,
**HColorPath**, **LColorPath** and **SColorPath**), but you can also create
custom color paths by importing the **ColorPath** class and setting a custom
value for its *hlsa* facet (e.g. *ColorPath( hlsa = 'hs' )* for animating along
the hue and saturation axes). Using **ColorPath**, you can also animate along
the 'a' (i.e. alpha) axis, which may affect the alpha (i.e. opacity) of the
color value being animated.
"""

from facets.api \
    import HasFacets, Int, Color, Range, Theme, ATheme, View, VGrid, VGroup, \
           Item, UItem, HLSColorEditor, on_facet_set

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.animation.api \
    import HLSAColorPath, HColorPath, LColorPath, SColorPath

#-- ColorChipEditor class ---------------------------------------------------

class ColorChipEditor ( ControlEditor ):
    """ Defines a simple 'color chip' for showing the animation. """

    def paint ( self, g ):
        cdx, cdy = self.control.size
        g.brush  = self.value
        g.draw_rectangle( 0, 0, cdx, cdy )

#-- ColorPathDemo class --------------------------------------------------------

# Define a reusable editor for selecting a color in HLS space:
color_editor = HLSColorEditor(
    edit      = 'all',
    cell_size = 20,
    space     = 0
)

# Define a reusable UI Item for displaying a color using the ColorChipEditor:
class ColorItem ( Item ):
    width      = Int( -200 )
    height     = Int( -200 )
    editor     = CustomControlEditor( klass = ColorChipEditor )
    item_theme = ATheme( Theme( '@xform:b?L25', content = 8 ) )

# Define the main demo class:
class ColorPathDemo ( HasFacets ):

    # Animated color values:
    hls_path    = Color
    h_path      = Color
    l_path      = Color
    s_path      = Color

    # The parameters used to control the animations:
    begin_color = Color( 0xFF0000 )
    end_color   = Color( 0x101080 )
    time        = Range( 0.1, 10.0, 5.0 )

    # The view of the four color chips and the animaton parameters:
    view = View(
        VGrid(
            ColorItem( 'hls_path' ),
            ColorItem( 'h_path' ),
            ColorItem( 'l_path' ),
            ColorItem( 's_path' ),
            group_theme = Theme( '@xform:b?L25' )
        ),
        VGroup(
            Item( 'begin_color', editor = color_editor ),
            Item( 'end_color',   editor = color_editor ),
            Item( 'time' ),
            group_theme = '@xform:b?L25'
        )
    )

    # Initialize the animations on start-up and whenever any animation parameter
    # changes:
    @on_facet_set( 'begin_color, end_color, time' )
    def facets_init ( self ):
        self.animate_color( 'hls_path', path = HLSAColorPath )
        self.animate_color( 'h_path',   path = HColorPath )
        self.animate_color( 'l_path',   path = LColorPath )
        self.animate_color( 's_path',   path = SColorPath )

    # Define a helper function for setting up a color animation:
    def animate_color ( self, name, path ):
        self.animate_facet( name,
            time    = self.time,
            begin   = self.begin_color,
            end     = self.end_color,
            path    = path,
            repeat  = 0,
            replace = True
        )

    # Clean-up when the demo is stopped (unloaded):
    def dispose ( self ):
        self.halt_animated_facets()

#-- Create the demo ------------------------------------------------------------

demo = ColorPathDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------