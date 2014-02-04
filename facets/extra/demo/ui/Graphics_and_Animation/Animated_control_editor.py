"""
# Animation Control Editor #

This is the fifth (and hopefully last) in a series of increasingly more
elaborate demonstrations of creating custom control editors using the special
**CustomControlEditor** *editor factory*.

This demonstration specifically builds upon the previous
*Interactive_control_editor.py* demo by adding a rudimentary (though
entertaining) animation capability with the help of some of the Facets
*animation* classes and methods.

All of the canvas editing features present in the previous demo remain
unchanged. The one addition occurs at the end of a drag operation. If the
*Control* key is held down when the left mouse button is released, the item
being dragged begins cycling between its ending and starting locations. The
animation continues until the item is clicked on again.

Although this may be a totally useless feature, it is fun to play with and helps
illustrate how simple it can be to add animation capabilities to your code.

We also create an **AnimatedCanvasItem** subclass of the original **CanvasItem**
item class which overrides the base class's ***dispose*** method to stop any
currently active animation when the item is deleted from the canvas.

The main logic changes occur in the **AnimatedCanvasEditor** subclass of the
original **CanvasEditor** class, which overrides some of the original mouse
event handling methods to:

- Cancel any active animation on a canvas item when the left mouse button is
  pressed over it.
- Start a new animation on a canvas item being dragged when the left mouse
  button is released with the *Control* key pressed.

Other than these few, simple changes, the rest of the original demo code
remains unchanged. The animation blends seamlessly with the original code
because the Facets notification system automatically schedules refreshes of
the canvas editor whenever an item's bounds are changed by the animation
subsystem. This behavior is inherited from the original **CanvasEditor** class
code.

You can continue to create, edit and delete items while other items are being
animated. You can even edit the label and contents of an item while it is being
animated.

As with the original demo, be sure to drag one of the canvas tabs to create a
side-by-side view, so that you can see that both canvas editors remain
completely synchronized with any number of animations running.
"""

#-- Imports --------------------------------------------------------------------

from facets.extra.demo.ui.Graphics_and_Animation.Interactive_control_editor \
    import CanvasItem, CanvasEditor, InteractiveControl

from facets.animation.api \
    import EaseOutEaseIn

#-- AnimatedCanvasItem class ---------------------------------------------------

class AnimatedCanvasItem ( CanvasItem ):

    def dispose ( self ):
        self.halt_animated_facets()

#-- AnimatedCanvasEditor class -------------------------------------------------

class AnimatedCanvasEditor ( CanvasEditor ):

    item_class = AnimatedCanvasItem

    def normal_left_down ( self, x, y ):
        super( AnimatedCanvasEditor, self ).normal_left_down( x, y )

        self._bounds = self.value.selected.bounds
        self.value.selected.halt_animated_facets()

    def dragging_left_up ( self, event ):
        super( AnimatedCanvasEditor, self ).dragging_left_up()

        if event.control_down:
            item = self.value.selected
            item.animate_facet( 'bounds', 1.0, self._bounds, item.bounds,
                tweener = EaseOutEaseIn,
                repeat  = 0
            )

#-- AnimatedControl class ------------------------------------------------------

class AnimatedControl ( InteractiveControl ):

    editor = AnimatedCanvasEditor

#-- Create the demo ------------------------------------------------------------

demo = AnimatedControl

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
