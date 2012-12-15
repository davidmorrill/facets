"""
A simple demonstration combining the creation of a <b>CustomControlEditor</b>
with some animation to create a themed control with variable sized text that
could be used in a presentation or for a video clip title.

You can enter the <b><i>Label</i></b> and <b><i>Content</i></b> for the cover
page in the designated text entry fields. Note that you can enter "\n" in the
content text field to insert a carriage return into the displayed text.

You can use the <b><i>Size</i></b> scrubber to increase or decrease the size of
the displayed text, and you can selected a different background color for the
page using the color editor in the bottom-right corner of the view. Note that
you can <i>right-click</i> the color editor to cycle through the various color
properties (i.e. <i>hue</i>, <i>saturation</i> and <i>lightness</i>). The
control defaults to editing the <i>lightness</i> of the background color.

Finally, you can click the <i>animate</i> icon located next to the color editor
to animate the text going from a very small size to the size currently
specified.

In terms of the code, this example doesn't really cover any new ground not
already covered in other demos in this section. But it does provide another
illustration of what is possible, and is provided with the belief that more
examples are better than fewer examples.

The only new technique worth mentioning is the ability to specify in the
<b>CustomControlEditor</b> editor factory class (i.e. <b>CoverPageEditor</b>)
the value of the <b><i>refresh</i></b> facet, which is a string describing what
external changes should trigger a refresh of the custom control:

  refresh = 'factory:[label, bg_color, size]'

Use of this facet eliminates the need to create a separate notification handler
in the custom control class just to schedule a refresh operation.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import UIView, Str, Range, Button, ATheme, Theme, Color, Font, View, \
           VGroup, HGroup, Item, UItem, HLSColorEditor, ScrubberEditor,  \
           SyncValue

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.animation.api \
    import EaseIn

#-- _CoverPageEditor class -----------------------------------------------------

class _CoverPageEditor ( ControlEditor ):

    font = Font

    def paint ( self, g ):
        factory   = self.factory
        content   = self.value.replace( '\\n', '\n' )
        self.font = str( factory.size )
        g.font    = self.font
        cdx, cdy  = self.control.client_size
        g.pen     = None
        g.brush   = factory.bg_color
        g.draw_rectangle( 0, 0, cdx, cdy )
        margin   = int( 0.05 * min( cdx, cdy ) )
        adx, ady = cdx - (2 * margin), cdy - (2 * margin)
        theme    = factory.background
        theme.fill( g, margin, margin, adx, ady )
        tx, ty, tdx, tdy = theme.bounds( margin, margin, adx, ady )
        g.pen = theme.content_color
        theme.draw_text( g, content, 0, margin, margin, adx, ady )
        if theme.has_label and (factory.label != ''):
            g.font = theme.label_font
            theme.draw_label( g, factory.label, None, margin, margin, adx, ady )

#-- CoverPageEditor class ------------------------------------------------------

class CoverPageEditor ( CustomControlEditor ):

    klass      = _CoverPageEditor
    refresh    = 'factory:[label, bg_color, size]'
    label      = Str(               facet_value = True )
    bg_color   = Color( 0x404040,   facet_value = True )
    size       = Range( 8, 200, 80, facet_value = True )
    background = ATheme( Theme( '@xform:b8td?H56S13', content = 10 ),
                         facet_value = True )

#-- CoverPage class ------------------------------------------------------------

class CoverPage ( UIView ):

    content    = Str( 'Welcome to\\nFacets!' )
    label      = Str( 'We are Proud to Present...' )
    size       = Range( 8, 200, 80 )
    bg_color   = Color( 0x404040 )
    animate    = Button( '@icons2:GearExecute' )

    def default_facets_view ( self ):
        return View(
            VGroup(
                Item( 'content',
                      editor = CoverPageEditor(
                          label    = SyncValue( self, 'label' ),
                          size     = SyncValue( self, 'size' ),
                          bg_color = SyncValue( self, 'bg_color' )
                      )
                ),
                HGroup(
                    Item(  'label',   springy = True ), '_',
                    Item(  'content', springy = True ), '_',
                    Item(  'size',
                           width      = -38,
                           editor     = ScrubberEditor(),
                           item_theme = '#themes:ScrubberEditor'
                    ), '_',
                    UItem( 'animate' ), '_',
                    UItem( 'bg_color',
                           springy = True,
                           editor  = HLSColorEditor( edit = 'lightness' )
                    ),
                    group_theme = '#themes:toolbar_group'
                ),
                show_labels = False
            ),
            width  = 0.67,
            height = 0.67
        )

    def _animate_set ( self ):
        self.halt_animated_facets()
        self.animate_facet(
            'size', 3.0, self.size, 8, tweener = EaseIn
        )

    def _ui_info_set ( self ):
        self.halt_animated_facets()

#-- Create the demo ------------------------------------------------------------

demo = CoverPage

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
