"""
A demonstration of how tools in the <b>facets.extra</b> package can be
easily connected together to form other tools. In this case we are connecting
the <i>FacetsUIDB</i> tool to a <i>UniversalInspector</i> to form a new
<i>UIDBTool</i>.

Note also that in this example, we are <i>programmatically</i> connecting
the two tools together (see the <i>_ui_db_default</i> method). However,
because both of these tools support the <i>feature</i> architecture, they
can just as easily be connected together by the end user using the <i>feature
user interface</i>.

All of the tools in the <b>facets.extra</b> package follow the <i>small,
sharp, visual tools</i> design model, which is intended to allow developers
and end users to create new tools by the interconnection of the other tools,
similar to the shell command line tool model, but oriented toward visual tools.

The <i>FacetsUIDB</i> tool displays a list showing all of the Facets UI data
base entries. Each Facets UI View with an non-empty <i>id</i> facet stores
user preference information about the view in the Facets UI data base under
the value of the View's <i>id</i> facet.

The <i>UniversalInspector</i> tool attempts to display useful information about
any object provided to it. For example, if it is given a Python object, it will
display a tree view of the object showing all of its various attributes. If it
is given a text file name, it will display the contents of the text file, and
so on.

In this example, we are connecting the currently selected item in the Facets
UI DB tool, specified by the tool's <i>value</i> facet, to the Universal
Inspector's <i>item</i> facet, which specifies what item it should display.
This code appears in the <i>_ui_db_default</i> method, and is performed by the
call to the <b>HasFacets</b> class's <i>sync_facet</i> method.

Since they are connected, if you click an item in the Facets UI DB view, you
will see the corresponding selected item's data appear in the Univeral
Inspector view. Note that the value is actually a Python object, which as
mentioned previously, is shown as a tree view of the object in the inspector.

If you select an item in the Facets UI DB view, and then click the <i>Delete</i>
button, the user preference data for the selected item will be deleted from the
Facets UI data base. This can be useful if you are developing a Facets UI View
with persistent user preference data and you wish to reset the view back to the
<i>factory settings</i> for testing purposes or to recover from an error in
your UI code.

Checking the information in the Universal Inspector view can also be useful
for seeing what information Facets saves in the data base, and to see if the
information you expect to be there is actually there.

In order for this demo to run, you must have the facets.extra package
installed.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Instance

from facets.api \
    import View, HSplit, Item

from facets.extra.tools.facets_ui_db \
     import FacetsUIDB

from facets.extra.tools.universal_inspector \
     import UniversalInspector

class UIDBTool ( HasFacets ):

    # The Facets UI DB tool we are using:
    ui_db = Instance( FacetsUIDB )

    # The Universal Inspector we are using:
    inspector = Instance( UniversalInspector, () )

    #-- Facets UI View Definitions -----------------------------------------

    view = View(
        HSplit(
            Item( 'ui_db',     style = 'custom', dock = 'horizontal' ),
            Item( 'inspector', style = 'custom', dock = 'horizontal' ),
            id          = 'splitter',
            show_labels = False
        ),
        id        = 'facets.ui.demo.tools.Facets_UI_DB_and_'
                    'Universal_Inspector_demo',
        width     = 0.75,
        height    = 0.50,
        resizable = True
    )

    #-- Default Value Handlers ---------------------------------------------

    def _ui_db_default ( self ):
        ui_db = FacetsUIDB()
        ui_db.sync_facet( 'value', self.inspector, 'item' )

        return ui_db

#-- Create the demo ------------------------------------------------------------

demo = UIDBTool

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------