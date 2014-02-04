"""
# Themed Control Editor #

A slightly more elaborate demonstration of creating a scrollable custom control
that can be used as a Facets *editor* using the special **CustomControlEditor**
*editor factory*. For a somewhat simpler example, refer to the
*Scrollable_control_editor.py* demo.

The **ThemedEditor** class creates a custom control that draws a grid of themed
text strings using the editor's ***value*** facet as the text. Each themed text
item also displays a label containing the row and column number of the item.

The **ThemedControl** class defines a ***text*** facet which is edited using
both the default text editor and a custom **CustomControlEditor** using the
**ThemedEditor** class to implement the editing control.

Try modifying the contents of the text entry field at the top of the view and
watch the custom **ThemedEditor**-based editor below it automatically reflect
the changes made to the value.

The **ThemedEditor** class subclasses the **ControlEditor** class, which allows
a control to be used with the **CustomControlEditor** editor factory class.

In particular, a subclass of **ControlEditor** has a facet called ***value***
which the associated **Editor** instance created by the **CustomControlEditor**
editor factory keeps in sync with the object facet being edited (***text*** in
this case).

Also, in the case of a scrollable custom control, the ***virtual_size*** facet
of the **ControlEditor** subclass must be given a default value which is a tuple
of the form: (*initial_width*, *initial_height*), which indicates that the
control supports a *virtual size* which may be different than the physical size
of the control. For this demo, the default value is set to (10, 10). Normally,
the default value for this facet is **(-1, -1)**, which indicates that the
control does not support a virtual size different than its physical size.

The net result is that, along with an automatic *refresh* performed when
***value*** changes, the only additional code needed in this example is to
override the **ThemedWindow** class's default ***paint_content*** method to
customize the drawing behavior of the editor control. Note how at the end of the
***paint*** method, the ***virtual_size*** facet is set to a new tuple value
indicating the actual size of the content just drawn.

In this demo, we take advantage of the ability of a **ThemedWindow** to
automatically draw the background of the control using a specified theme, which
we set using the ***theme*** facet of the **CustomControlEditor**. Also, by
overriding the ***paint_content*** method, rather than the ***paint*** method,
we also make use of the **ThemedWindow** class's ability to automatically draw a
label for the control using the control's ***label*** facet, which we override
in the demo and define as a **Property** whose value is a string based on the
editor's current value.

The actual content of the control is drawn in the ***paint_content*** method
using another theme, specified by the ***item_theme*** facet. Here we use
several methods defined on a **Theme** object to simplify the process of drawing
the theme as well as its content and label.

Finally, we use information obtained from both the main control theme and the
item theme to compute the new *virtual size* of the control to ensure that the
control's scroll bars have the correct size information.

The Facets tool box also defines a number of tools to assist in the creation of
new themes from images. In particular, be sure to try out the
**Image Transformer**, **Theme Editor**, **Theme Layout** and **Theme Sampler**
tools, possibly used in conjunction with the **File Browser** or
**Image Library Selector** tools (to provide a source of image files for
creating themes).

Of course, in a more complex editor control, additional methods would need to be
defined and overridden to handle mouse and keyboard events. You might want to
refer to the *twixter.py* demo for a more sophisticated example of defining a
custom editor control.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, ATheme, Theme, Property, View, VGroup, Item

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.theme \
    import LEFT

#-- ThemedEditor class ---------------------------------------------------------

class ThemedEditor ( ControlEditor ):

    virtual_size = ( 10, 10 )
    label        = Property
    item_theme   = ATheme( Theme( '@xform:b6td?H54L2S12',
                                  content      = ( 4, 4, 3, 0 ),
                                  content_font = '14' ) )

    def _get_label ( self ):
        return 'The current text is: %r' % self.value

    def paint_content ( self, g ):
        is_visible = self.control.is_visible
        theme      = self.item_theme
        text       = self.value
        label      = theme.label_font
        g.font     = content = theme.content_font
        tdx, tdy   = theme.size_for( g, text )
        row        = 1
        cx, cy, cdx, cdy = self.content_bounds
        y = cy
        while y < 4000:
            x = cx
            for column in xrange( 1, 11 ):
                if is_visible( x, y, tdx, tdy ):
                    theme.fill( g, x, y, tdx, tdy )
                    g.font = content
                    theme.draw_text( g, text, LEFT, x, y, tdx, tdy )
                    g.font = label
                    theme.draw_label( g, 'Item %d,%d' % ( row, column ), None,
                                      x, y, tdx, tdy )

                x += tdx + 4

            y   += tdy + 4
            row += 1

        bdx, bdy          = self.theme.bounds()
        self.virtual_size = ( bdx + 10 * (tdx + 4) - 4, y + bdy - cy - 4 )

#-- ThemedControl class --------------------------------------------------------

class ThemedControl ( HasFacets ):

    text = Str( 'Hello, world!' )

    view = View(
        VGroup(
            Item( 'text', style = 'custom', height = 0.05 ),
            '_',
            Item( 'text',
                  editor = CustomControlEditor(
                      klass = ThemedEditor,
                      theme = Theme( '@xform:btd?L30',
                                     alignment = 'left',
                                     content   = 6,
                                     label     = 6 )
                  )
            ),
            show_labels = False
        ),
        width  = 0.5,
        height = 0.5
    )

#-- Create the demo ------------------------------------------------------------

demo = ThemedControl

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
