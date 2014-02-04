"""
# Scrollable Control Editor #

A simple demonstration of creating a scrollable custom control that can be used
as a Facets *editor* using the special **CustomControlEditor** *editor factory*.
For an example of creating a simple, *non-scrollable* custom control, refer to
the *Basic_control_editor.py* demo.

The **ScrollableEditor** class creates a custom control that simply draws its
***value*** facet as text using the editor's font. It draws the text repeatedly
(along with the current line number) until a total vertical height of 4000
pixels is reached (to give the control some scrollable content).

The **ScrollableControl** class defines a ***text*** facet which is edited using
both the default text editor and a custom **CustomControlEditor** using the
**ScrollableEditor** class to implement the editing control.

Try modifying the contents of the text entry field at the top of the view and
watch the custom **ScrollableEditor**-based editor below it automatically
reflect the changes made to the value.

The **ScrollableEditor** class subclasses the **ControlEditor** class, which
allows a control to be used with the  **CustomControlEditor** editor factory
class.

In particular, a control which is a subclass of **ControlEditor** has a facet
called ***value*** which the associated **Editor** instance created by the
**CustomControlEditor** editor factory keeps in sync with the object facet being
edited (***text*** in this case).

Also, in the case of a scrollable custom control, the ***virtual_size*** facet
of the **ControlEditor** subclass must be given a default value which is a tuple
of the form: (*initial_width*, *initial_height*), which indicates that the
control supports a *virtual size* which may be different than the physical size
of the control. For this demo, the default value is set to (10, 10). Normally,
the default value for this facet is **(-1, -1)**, which indicates that the
control does not support a virtual size different than its physical size.

The net result is that, along with an automatic *refresh* performed when
***value *** changes, the only additional code needed in this example is to
override the **ThemedWindow** class's default ***paint*** method to customize
the drawing behavior of the editor control. Note how at the end of the
***paint*** method, the ***virtual_size*** facet is set to a new tuple value
indicating the actual size of the content just drawn.

Of course, in a more complex editor control, additional methods would need to be
defined and overridden to handle mouse and keyboard events. You might want to
refer to the *twixter.py* demo for a more sophisticated example of defining a
custom editor control.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, View, VGroup, Item

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

#-- ScrollableEditor class -----------------------------------------------------

class ScrollableEditor ( ControlEditor ):

    virtual_size = ( 10, 10 )

    def paint ( self, g ):
        text   = self.value
        dx, dy = g.text_size( text )
        y      = 5
        i      = 1
        if dx > 0:
            while y < 4000:
                text_i = '%s (%d)' % ( text, i )
                g.draw_text( text_i, 5, y )
                y += dy
                i += 1

            dx, dy = g.text_size( text_i )

        self.virtual_size = ( dx + 13, y + 8 )

#-- ScrollableControl class ----------------------------------------------------

class ScrollableControl ( HasFacets ):

    text = Str( 'Hello, world!' )

    view = View(
        VGroup(
            Item( 'text' ),
            '_',
            Item( 'text',
                  editor = CustomControlEditor( klass = ScrollableEditor,
                                                font  = '40' )
            ),
            show_labels = False
        ),
        width  = 0.5,
        height = 0.5
    )

#-- Create the demo ------------------------------------------------------------

demo = ScrollableControl

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
