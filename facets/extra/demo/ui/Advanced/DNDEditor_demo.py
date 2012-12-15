"""
Demonstrates use of the DNDEditor (drag and drop editor), which allows the value
of an object facet to be used as a drag source or drop target or both.

In this demonstration, the DNDEditor appears as a down pointing blue arrow icon
in the top-left corner of the view. Dragging and dropping one or more objects
onto the arrow icon displays the dropped objects in the UniversalInspector view
located directly below the DNDEditor.

To try it out, simply drag one or more files from your operating system's
standard file browser and drop them on the blue arrow. The contents of the
dropped files are immediately displayed in the UniversalInspector view.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from os.path \
    import exists

from facets.api \
    import HasFacets, Any, Instance, View, VGroup, HGroup, Item, DNDEditor, \
           spring

from facets.extra.tools.universal_inspector \
    import UniversalInspector

#-- DNDEditorDemo class --------------------------------------------------------

class DNDEditorDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The most recently dropped items:
    items = Any

    # The Universal Inspector used to display the contents of the current item:
    inspector = Instance( UniversalInspector, () )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'items',
                      label  = 'Drop an object here',
                      editor = DNDEditor( image = '@icons2:ArrowLargeDown' )
                ),
                spring
            ),
            '_',
            Item( 'inspector', style = 'custom' ),
            show_labels = False
        ),
        title     = 'DNDEditor Demo',
        id        = 'facets.extra.demo.ui.Advanced.DNDEditor_demo',
        width     = 0.50,
        height    = 0.67,
        resizable = True
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _items_set ( self, items ):
        if not isinstance( items, ( list, tuple ) ):
            items = [ items ]

        for item in items:
            if (isinstance( item, basestring ) and
                (item[:3] == '///')            and
                exists( item[3:])):
                item = item[3:]

            self.inspector.item = item

#-- Create the demo ------------------------------------------------------------

demo = DNDEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
