"""
A very simple demonstration of creating a custom control that can be used as a
Facets <i>editor</i> using the special <b>CustomControlEditor</b> <i>editor
factory</i>.

The <b>BasicControlEditor</b> class creates a custom control that simply draws
its <b><i>value</i></b> facet as text using the default font, and then adds a
red overstrike.

The <b>BasicControl</b> class defines a <b><i>name</i></b> facet which is edited
using both the default text editor and a custom <b>CustomControlEditor</b> using
the <b>BasicControlEditor</b> class to implement the editing control.

Try modifying the contents of the <i>Name</i> field and watch the custom
<b>BasicControlEditor</b>-based editor below it automatically reflect the
changes made to the value.

The <b>BasicControlEditor</b> class subclasses the <b>ControlEditor</b> class,
which allows a control to be used with the <b>CustomControlEditor</b> editor
factory class. <b>ControlEditor</b> is a subclass of the <b>ThemedWindow</b>
class.

In particular, the <b>ControlEditor</b> class defines a facet called
<b><i>value</i></b> which the associated <b>Editor</b> instance created by the
<b>CustomControlEditor</b> editor factory keeps in sync with the object facet
being edited (<b><i>name</i></b> in this case).

As a result, along with an automatic <i>refresh</i> performed when
<b><i>value </i></b> changes, the only additional code needed in this example is
to override the <b>ThemedWindow</b> class's default <b><i>paint</i></b> method
to customize the drawing behavior of the editor control.

Of course, in a more complex editor control, additional methods would need to
be defined and overridden to handle mouse and keyboard events. Please refer to
the <i>Twixter.py</i> demo for a more sophisticated example of defining an
editor control.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, View, Item

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

#-- BasicControlEditor class ---------------------------------------------------

class BasicControlEditor ( ControlEditor ):

    def paint ( self, g ):
        dx, dy = g.text_size( self.value )
        if dx > 0:
            g.draw_text( self.value, 3, 1 )
            g.pen = ( 255, 0, 0 )
            g.draw_line( 3, 3 + (dy / 2), dx + 3, 3 + (dy / 2) )

#-- BasicControl class ---------------------------------------------------------

class BasicControl ( HasFacets ):

    name = Str( 'Sample text' )

    view = View(
        Item( 'name' ),
        Item( 'name',
              show_label = False,
              editor     = CustomControlEditor( klass = BasicControlEditor )
        )
    )

#-- Create the demo ------------------------------------------------------------

demo = BasicControl

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
