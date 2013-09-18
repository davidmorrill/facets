"""
This shows a simple example of using the PropertyListEditor to display and edit
a list of specified object facets using a property sheet style editor.

The PropertyListEditor is a subclass of the PropertySheetEditor, but differs
in how it specifies the object facets to display and edit. Whereas the
PropertySheetEditor edits a specified HasFacets instance and is provided with
a custom PropertySheetAdapter subclass that defines what object facets are
included in the property sheet, the PropertyListEditor edits a list of item,
each of which describes a particular object facet to be included in the property
sheet.

At its simplest, each list item provided to the PropertyListEditor is a tuple of
the form:

    ( HasFacets_object, name [, label] [, editor] [, mode] )

where:
    HasFacets_object: A HasFacets instance.
    name:             The name of the 'HasFacet_object' facet to edit.
    label:            The UI label to display (defaults to using 'name').
    editor:           The Editor used to edit the facet (defaults to the
                      default editor for 'HasFacets_object.name').
    mode:             The editing mode to use (defaults to 'inline'). Refer to
                      the PropertySheetAdapter for more information.

As an alternative to using the simple tuple form, instances of PropertyListItem
can also be used:

    PropertyListItem(
        object                = Instance( HasFacets ),
        name                  = Str,
        label                 = Str,
        editor                = Instance( EditorFactory ),
        mode                  = EditMode,
        formatter             = Callable,
        image                 = Str,
        image_alignment       = CellImageAlignment,
        paint                 = Either( Str, Callable ),
        theme                 = ATheme,
        label_image           = Str,
        label_image_alignment = CellImageAlignment,
        label_paint           = Either( Str, Callable ),
        label_theme           = ATheme,
        label_menu            = Any,
        tooltip               = Str,
        is_open               = Bool,
        show_children         = Bool,
        show_group            = Bool
    )

Using an explicit PropertyListItem provides greater flexibility than using a
simple tuple, but can be somewhat more verbose. Note that internal to the
PropertyListEditor, all items are represented using PropertyListItem instances.

In this demo, we use a PropertyListEditor to edit a list of object facets
selected from a Person and Address instance. Two identical property sheets are
displayed, with the only difference being that the bottom list's fields are all
read-only.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Int, Instance, List, View, UItem, RangeEditor, \
           PropertyListEditor

from facets.ui.editors.property_list_editor \
    import PropertyListItem

#-- Person class ---------------------------------------------------------------

class Person ( HasFacets ):
    name = Str
    age  = Int

#-- Address class --------------------------------------------------------------

class Address ( HasFacets ):
    Street = Str
    City   = Str
    State  = Str

#-- PropertyListEditorDemo class -----------------------------------------------

class PropertyListEditorDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # A sample person:
    person  = Instance( Person, {
        'name': 'Bill Thompson',
        'age':  66
    } )

    # A sample address:
    address = Instance( Address, {
        'street': '456 Sycamore Lane',
        'city':   'Home Town',
        'state':  'CO'
    } )

    # The list of properties to edit:
    items = List

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'items', editor = PropertyListEditor() ),
        UItem( 'items', editor = PropertyListEditor( readonly = True ) )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _items_default ( self ):
        return [
            ( self.person,  'name', 'Full name' ),
            ( self.address, 'street' ),
            ( self.address, 'city'   ),
            PropertyListItem(
                object  = self.address,
                name    = 'state',
                image   = '@icons:red_ball',
                tooltip = 'The red ball is totally gratuitous'
            ),
            ( self.person,  'age', RangeEditor( low = 0, high = 120 ) )
        ]

#-- Create the demo ------------------------------------------------------------

demo = PropertyListEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------