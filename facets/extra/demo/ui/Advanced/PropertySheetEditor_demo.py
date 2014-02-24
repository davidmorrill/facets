"""
# PropertySheetEditor Demo #

This shows a simple example of using a **PropertySheetEditor**. A
PropertySheetEditor allows you to view and/or edit any or all facets (i.e.
properties) of a **HasFacets** object. It can view or edit simple facets, like
strings, numbers or boolean values, or more complex facets like lists, dicts
and tuples. It can even handle facets which contain references to other
HasFacets objects by displaying them as nested (or indented) properties of the
parent object.

In this example, we display and allow editing of some of the properties of a
Facets **Control** object using a PropertySheetEditor. A Control object
represents the widgets you see when using a Facets UI. The full definition of
the Control class can be found in the *facets.ui.adapters.control module*.

We are using Control objects for this example because they are a ready made
source of interesting properties to display and edit, and they simplify the
example by eliminating the need to create dummy demonstration classes.

Visually, the example is organized as follows:

- The top-left portion of the view contains a *dummy* text field and label.
  The text field's Control object is the initial object whose properties are
  displayed by the PropertySheetEditor.
- The top-right portion of the view contains a *control grabber* (represented
  by the question mark icon). You can select a different Control object to
  display by left clicking on the question mark icon and dragging the mouse
  pointer over any other Facets control and releasing the mouse button. The
  Control object the mouse pointer is positioned over at the time of its
  release is then displayed as the new contents of the PropertySheetEditor.
- The bottom portion of the view contains the actual PropertySheetEditor,
  which displays the properties of the currently selected Control object.

Like many of the Facets editors that handle complex data, the
PropertySheetEditor makes use of an adapter, in this case a
**PropertySheetAdapter**. The purpose of the adapter object is to help the
PropertySheetEditor *adapt* the contents of the HasFacets object being edited
to the display and editing requirements of the editor.

Most of the Facets editor adapter classes follow a similar pattern designed to
make solving the problem of adapting the target data to the editor as simple as
possible. They do this by exposing the various pieces of information that the
editor needs as a series of facets (i.e. properties) of the adapter. The editor
then queries the values of these properties in order to display and edit the
affected object's data.

To make these properties more flexible and adaptable to handing different
data requirements, each adapter property is implemented using a very flexible
set of naming conventions. In the case of a PropertySheetAdapter, the naming
rules that can be used are:

- *classname_name_attribute*
- *name_attribute*
- *classname_attribute*
- *attribute*

where:

- *classname*: The name of the HasFacets subclass for the object containing the
  facet to display.
- *name*: The name of the facet to display.
- *attribute*: The name of the property sheet value the editor is trying to
  obtain.

For example, the adapter's *mode* value determines what editing mode a
particular property should use. If we wanted all properties to be read-only, we
could add the following line to the definition of our adapter class:

    mode = Str( 'readonly' ) # Using the 'attribute' pattern

If we wanted all of the properties of a Control object to be read-only we could
use the following line instead:

    Control_mode = Str( 'readonly' ) # Using the 'classname_attribute' pattern

If we wanted a particular property to be read-only (say the *screen_position*
facet, as actually used in the example), we could write:

    screen_position_mode = Str( 'readonly' ) # Using the 'name_attribute' pattern

If there were multiple object types with a *screen_position* facet, but we only
wanted the Control instance's *screen_position* facet to be read-only, we could
also write:

    # Using the 'classname_name_attribute' pattern:
    Control_screen_position_mode = Str( 'readonly' )

This set of adapter naming rules help make customizing a PropertySheetAdapter
to a given task fairly straightforward. In fact, there are more variations
possible, but these are beyond the scope of this example.

Given this explanation of how the adapter works, it should now be possible for
you to read the code for the example's ControlAdapter class and see that it has
facet definitions that tell the PropertySheetEditor to:

- Display a Control object's *screen_position*, *size*, *visible*, *enabled*,
  and parent facets.
- Use *X* and *Y* as the labels for the *screen_position* tuple's fields.
- Make the *screen_position* read-only.
- Use *Width* and *Height* as the labels for the *size* tuple's fields.
- Use the internal *Bool* paint routine for displaying the visible and enabled
  facet's *Bool* values.
- Invoke the *toggle_item* method whenever the user attempts to edit the visible
  or enabled facet by clicking on them.
- Do not initially display the properties of the parent facet (another Control
  object).

An additional useful feature of a PropertySheetEditor is its ability to filter
the set of names and values displayed. In this example, the *name* filter is
enabled (as indicated by the *filter* icon appearing next to the *Name* column
header). Clicking on the *Name* header displays a popup text field. Only
properties partially or completely matching the string you type into the filter
field are displayed. The filter is *live*, affecting the displayed list of
properties as you type. Move the mouse pointer away from the popup field to
dismiss is. You can remove the filter simply by clicking on the *Name* header
again.

Finally, please note that while trying out the example code you are working with
*live* Control objects. For example, clicking the *visible* property of a
Control will hide or show the Control, possibly leaving the application in an
unusable state if you are not careful about which Control you are working with.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import List, Str, Bool, Instance, Control, View, HGroup, VGroup, Item, \
           Handler, PropertySheetEditor, ControlGrabberEditor, spring

from facets.ui.property_sheet_adapter \
    import PropertySheetAdapter

#-- Control PropertySheetAdapter class -----------------------------------------

class ControlAdapter ( PropertySheetAdapter ):

    Control_facets = List( [ 'screen_position', 'size', 'visible', 'enabled',
                             'parent' ] )
    screen_position_labels = List( [ 'X', 'Y' ] )
    screen_position_mode   = Str( 'readonly' )
    size_labels            = List( [ 'Width', 'Height' ] )
    visible_paint          = Str( 'Bool' )
    enabled_paint          = Str( 'Bool' )
    visible_mode           = Str( 'toggle_item' )
    enabled_mode           = Str( 'toggle_item' )
    parent_is_open         = Bool( False )

    def toggle_item ( self, item ):
        setattr( item.object, item.name, not getattr( item.object, item.name ) )

#-- PropertySheetEditorDemo Class Definition -----------------------------------

class PropertySheetEditorDemo ( Handler ):

    #-- Facet Definitions ------------------------------------------------------

    # The most recent control selecting using the ControlGrabberEditor:
    control = Instance( Control )

    # A dummy text field to use as a default control to display initially:
    dummy = Str( 'This is a dummy text field' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HGroup(
            Item( 'dummy', width = 200 ),
            spring,
            Item( 'control',
                  show_label = False,
                  editor     = ControlGrabberEditor()
            )
        ),
        '_',
        VGroup(
            Item( 'control',
                  editor = PropertySheetEditor( adapter = ControlAdapter )
            ),
            show_labels = False
        ),
        title     = 'PropertySheetEditor Demo',
        id        = 'facets.extra.demo.ui.Advanced.PropertySheetEditor_demo',
        width     = 0.25,
        height    = 0.67,
        resizable = True
    )

    #-- Handler Method Overrides -----------------------------------------------

    def init_info ( self, info ):
        self._info = info

    #-- Facet Default Values ---------------------------------------------------

    def _control_default ( self ):
        return self._info.dummy.adapter

#-- Create the demo ------------------------------------------------------------

demo = PropertySheetEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
