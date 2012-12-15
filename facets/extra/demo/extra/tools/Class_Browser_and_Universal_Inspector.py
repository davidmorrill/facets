"""
A demonstration of how tools in the <b>facets.extra</b> package can be
easily connected together to form other tools. In this case we are connecting
the <i>ClassBrowser</i> tool to a <i>UniversalInspector</i> to form a new
<i>CBTool</i>.

Note also that in this example, we are <i>programmatically</i> connecting
the two tools together (see the <i>_class_browser_default</i> method). However,
because both of these tools support the <i>feature</i> architecture, they
can just as easily be connected together by the end user using the <i>feature
user interface</i>.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Instance

from facets.api \
    import View, HSplit, Item

from facets.extra.tools.class_browser \
     import ClassBrowser

from facets.extra.tools.universal_inspector \
     import UniversalInspector

class CBTool ( HasFacets ):

    # The class browser tool we are using:
    class_browser = Instance( ClassBrowser )

    # The Universal Inspector we are using:
    inspector = Instance( UniversalInspector, () )

    #-- Facets UI View Definitions ---------------------------------------------

    view = View(
        HSplit(
            Item( 'class_browser', style = 'custom', dock = 'horizontal' ),
            Item( 'inspector',     style = 'custom', dock = 'horizontal' ),
            id          = 'splitter',
            show_labels = False
        ),
        title     = 'Class Browser Tool',
        id        = 'facets.ui.demo.tools.Class_Browser_and'
                    'Universal_Inspector_demo',
        width     = 0.75,
        height    = 0.50,
        resizable = True
    )

    #-- Default Value Handlers -------------------------------------------------

    def _class_browser_default ( self ):
        cb = ClassBrowser()
        cb.sync_facet( 'file_position', self.inspector, 'item' )

        return cb

#-- Create the demo ------------------------------------------------------------

demo = CBTool

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------