"""
# Interactive Control Editor #

This is the fourth in a series of increasingly more elaborate demonstrations
of creating custom control editors using the special **CustomControlEditor**
*editor factory*.

This demonstration builds upon the *Themed_control_editor.py* demo by showing
how to add mouse event handling to a custom control editor using the
**ThemedWindow** class's *state*-based event handling methods.

The demo is a simple drawing program which allows you to create, delete, drag
and edit simple themed boxes containing some content text and an optional label.

You create a themed box by clicking (and optionally dragging) anywhere in the
drawing area. The themed box will be created using the current contents of the
*label* and *content* fields at the bottom of the view. Creating a new item
leaves it in the *selected* state. You can continue to make changes to the
*label* and *content* fields and see those changes reflected in the item you
just created.

You can delete an existing item simply by *right clicking* on it. If you
right-click on an empty area, any currently selected item will be deselected.

You select an existing item by *clicking* on it. You move an item by
*click-dragging* it. Selecting an item also copies it current label and content
values back into the text entry fields at the bottom of the view, allowing you
to make editing changes if desired.

The demo code is divided into three model classes:

- **CanvasItem**: A single themed box.
- **Canvas**: The drawing canvas.
- **InteractiveControl**: The main demo class.

The custom control editor is defined by the **CanvasEditor** class. It occupies
the major portion of the view, and its purpose is to allow creating, deleting,
dragging and editing the **CanvasItems** contained within the **Canvas** object
it is editing.

The **InteractiveControl** class defines a ***canvas*** facet, containing a
**Canvas** instance, which is edited using the custom **CustomControlEditor**
using the **CanvasEditor** class to implement the editing control.

As with some of the other custom control editor demos, the **CanvasEditor**
is scrollable. In this case it uses a fixed document size of 5000 x 5000 pixels,
as specified by its ***virtual_size*** facet value.

To help keep this description relatively short, we will not go into any detail
about the drawing or *theme*-related code, referring you instead to the
*Themed_control_editor.py* demo for more information about those topics.

Instead we will focus on the event handling code contained in the
**CanvasEditor** class.

The **ThemedWindow** class, which is a superclass of **CanvasEditor**, defines a
flexible mechanism for handling mouse events based upon a *finite state machine*
mechanism implemented using its ***state*** facet, which contains a string
defining the object's current *state*.

The initial, default value for ***state*** is *"normal"*. When a mouse event
(such as a left mouse button down event) occurs, the class looks for a handler
with a name of the form: *state_event* (e.g. ***normal_left_down***, where
***normal*** is the current state, and ***left_down*** is the name of the event.

If the method is found, it is called with the type of event information it
requests. The requested information is determined by the number of arguments
defined for the method, as shown below:

- *method( self )*
- *method( self, event )*
- *method( self, x, y )*
- *method( self, x, y, event )*

where ***x*** and ***y*** are the mouse coordinates associated with the event,
and ***event*** is an **Event** object containing detailed information about the
event.

The use of the ***state*** facet provides a simple mechanism for writing the
logic of a control without having to maintain or use a lot of other internal
state information. Simply setting ***state*** to a new value causes future mouse
events to be routed to the appropriate method automatically.

If no method matching the combined state/event name is found, the default action
for that event is taken. Thus, all you have to do to handle a specific event in
a specific state is to write a method for handling that event using the above
naming and argument conventions.

Another point worth mentioning is how all of the **CanvasEditor** refresh logic
is automatically handled by the Facets notification system. In particular, the:

    @on_facet_set( 'value:items.refresh' )

decorator ensures that the editor is refreshed whenever any items are added to
or deleted from the canvas, or when the ***refresh*** event is fired on any item
contained in the canvas. In conjunction with this, note how the ***refresh***
event on a **CanvasItem** is automatically fired whenever any of the facets
affecting the visual appearance of an item are changed, courtesy of the
***event*** metadata attached to their facet definitions.

There are lots of other interesting Facets programming style nuggets buried in
this demo, which we will leave interested readers to discover on their own.

Finally, to illustrate the power of the Facets *model-based* approach, the demo
view defines two tabs, each displaying the same **Canvas** model but using
different copies of the **CanvasEditor**. Try dragging one of the tabs so that
you have two side-by-side canvas views.

Notice how both views of the canvas remain completely in sync, due to the fact
that they are both editing the same **Canvas** model. Each view can be scrolled
independently, but the contents for both are always identical.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, UIView, Str, List, Bool, Tuple, Int, Instance, Theme, \
           Property, View, Tabbed, HGroup, VGroup, Item, on_facet_set,      \
           property_depends_on

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

#-- Constants ------------------------------------------------------------------

content1 = ( 4, 4, 0, 0 )
content2 = ( 4, 4, 2, 0 )
Themes   = [
    Theme( '@xform:b6?H54L2S12',   content = content1, content_font = '14' ),
    Theme( '@xform:b6td?H54L2S12', content = content2, content_font = '14' ),
    Theme( '@xform:b6?H10S',       content = content1, content_font = '14' ),
    Theme( '@xform:b6td?H10S',     content = content2, content_font = '14' ),
]

#-- CanvasItem class -----------------------------------------------------------

class CanvasItem ( HasFacets ):

    label    = Str( event = 'refresh' )
    content  = Str( event = 'refresh' )
    selected = Bool( False, event = 'refresh' )
    bounds   = Tuple( Int, Int, Int, Int, event = 'refresh' )

    def paint ( self, g ):
        theme        = Themes[ (2 * self.selected) + (self.label != '') ]
        g.font       = theme.content_font
        content      = self.content.replace( '\\n', '\n' )
        tdx, tdy     = theme.size_for( g, content )
        x, y, dx, dy = self.bounds
        self.facet_setq( bounds = ( x, y, tdx, tdy ) )
        theme.fill( g, x, y, tdx, tdy )
        theme.draw_text( g, content, None, x, y, tdx, tdy )
        if self.label != '':
           g.font = theme.label_font
           theme.draw_label( g, self.label, None, x, y, tdx, tdy )

    def is_in ( self, x, y ):
        bx, by, bdx, bdy = self.bounds

        return ((bx <= x < (bx + bdx)) and (by <= y < (by + bdy)))

    def dispose ( self ):
        pass  # Overridden in Animated_control_editor_demo.py

#-- Canvas class ---------------------------------------------------------------

class Canvas ( HasFacets ):

    label    = Str
    content  = Str( 'Hello, world!' )
    items    = List( CanvasItem )
    selected = Instance( CanvasItem )

    def find_item ( self, x, y ):
        for item in self.items:
            if item.is_in( x, y ):
                return item

        return None

    def dispose ( self ):
        for item in self.items:
            item.dispose()

    def _label_set ( self, label ):
        item = self.selected
        if item is not None:
            item.label = label

    def _content_set ( self, content ):
        item = self.selected
        if item is not None:
            item.content = content

    def _selected_set ( self, old, new ):
        if old is not None:
            old.selected = False

        if new is not None:
            new.selected = True
            self.label   = new.label
            self.content = new.content

#-- CanvasEditor class ---------------------------------------------------------

class CanvasEditor ( ControlEditor ):

    virtual_size = ( 5000, 5000 )
    label        = ('[Click] Empty space: Create item | Item: Select '
                    '[Drag] Item: Move [Right click] Item: Delete')
    item_class   = CanvasItem

    def paint_content ( self, g ):
        for item in self.value.items:
            if self.control.is_visible( *item.bounds ):
                item.paint( g )

    @on_facet_set( 'value:items.refresh' )
    def _needs_update ( self ):
        self.refresh()

    def normal_left_down ( self, x, y ):
        self._x, self._y, self.state = x, y, 'dragging'
        canvas          = self.value
        canvas.selected = canvas.find_item( x, y )
        if canvas.selected is None:
            canvas.selected = self.item_class(
                label    = canvas.label,
                content  = canvas.content,
                selected = True,
                bounds   = ( x - 10, y - 10, 0, 0 )
            )
            canvas.items.append( canvas.selected )

    def normal_right_down ( self, x, y ):
        canvas = self.value
        item   = canvas.find_item( x, y )
        if item is not None:
            item.dispose()
            canvas.items.remove( item )
            if item is canvas.selected:
                canvas.selected = None
        else:
            canvas.selected = None

    def dragging_motion ( self, x, y ):
        item             = self.value.selected
        bx, by, bdx, bdy = item.bounds
        dx, dy           = x - self._x, y - self._y
        if (dx != 0) or (dy != 0):
            self._x, self._y = x, y
            item.bounds      = ( bx + dx, by + dy, bdx, bdy )

    def dragging_left_up ( self ):
        self.state = 'normal'

#-- InteractiveControl class ---------------------------------------------------

class InteractiveControl ( UIView ):

    canvas = Instance( Canvas, () )
    count  = Property
    editor = CanvasEditor

    def default_facets_view ( self ):
        return View(
            VGroup(
                Tabbed(
                    self._canvas_item(),
                    self._canvas_item(),
                    show_labels = False
                ),
                HGroup(
                    Item( 'object.canvas.label',   width = 0.5 ),
                    Item( 'object.canvas.content', width = 0.5 ),
                    '_',
                    Item( 'count',
                          show_label = False,
                          style      = 'readonly',
                          width      = -50
                    ),
                    group_theme = '#themes:toolbar_group'
                ),
                show_labels = False
            ),
            width  = 0.5,
            height = 0.5
        )

    def _canvas_item ( self ):
        return Item( 'canvas',
            dock   = 'tab',
            editor = CustomControlEditor(
                klass = self.editor,
                theme = Theme(
                    '@xform:btd?L30', alignment = 'left', content = 6, label = 6
                )
            )
        )

    @property_depends_on( 'canvas:items' )
    def _get_count ( self ):
        n = len( self.canvas.items )

        return ( 'No items', '1 item', '%d items' % n )[ cmp( n, 1 ) + 1 ]

    def _ui_info_set ( self, ui_info ):
        if ui_info is None:
            self.canvas.dispose()

#-- Create the demo ------------------------------------------------------------

demo = InteractiveControl

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
