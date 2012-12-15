"""
Demonstrates the use of the HTMLEditor available when using the Qt4 Facets UI
back-end.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, View, Tabbed, Item, HTMLEditor

#-- Constants ------------------------------------------------------------------

# A web page to be displayed:
web_page = """
<html>
    <head></head>
    <body>
        <p>This is a very simple web page.</p>
    </body>
</html>
"""

#-- Demo Class -----------------------------------------------------------------

class Demo ( HasFacets ):

    # The URL and HTML to display:
    url  = Str( 'http://dmorrill.com' )
    html = Str( web_page )

    # The facets UI view used by the editor:
    view = View(
        Tabbed(
            Item( 'url',
                  editor = HTMLEditor(),
                  dock   = 'tab'
            ),
            Item( 'html',
                  editor = HTMLEditor(),
                  dock   = 'tab'
            ),
            show_labels = False
        ),
        title     = 'HTMLEditor Demo',
        width     = 0.5,
        height    = 0.75,
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = Demo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------