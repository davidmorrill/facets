"""
# Basic Control Editor #

A very simple demonstration of creating a custom control that can be used as a
Facets *editor* using the special **CustomControlEditor** *editor factory*.

The **BasicControlEditor** class creates a custom control that simply draws its
***value*** facet as text using the default font, and then adds a red
overstrike.

The **BasicControl** class defines a ***name*** facet which is edited using both
the default text editor and a custom **CustomControlEditor** using the
**BasicControlEditor** class to implement the editing control.

Try modifying the contents of the *Name* field and watch the custom
**BasicControlEditor**-based editor below it automatically reflect the changes
made to the value.

The **BasicControlEditor** class subclasses the **ControlEditor** class, which
allows a control to be used with the **CustomControlEditor** editor factory
class. **ControlEditor** is a subclass of the **ThemedWindow** class.

In particular, the **ControlEditor** class defines a facet called ***value***
which the associated **Editor** instance created by the **CustomControlEditor**
editor factory keeps in sync with the object facet being edited (***name*** in
this case).

As a result, along with an automatic *refresh* performed when ***value ***
changes, the only additional code needed in this example is to override the
**ThemedWindow** class's default ***paint*** method to customize the drawing
behavior of the editor control.

Of course, in a more complex editor control, additional methods would need to
be defined and overridden to handle mouse and keyboard events. Please refer to
the *Twixter.py* demo for a more sophisticated example of defining an editor
control.
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
