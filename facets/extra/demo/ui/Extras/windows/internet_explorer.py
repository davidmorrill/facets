"""
# Internet Explorer #

This demo shows how to use the Windows specific **IEHTMLEditor** class for
displaying web pages using Internet Explorer.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

# Imports:
from facets.extra.wx.editors.windows.ie_html_editor \
    import IEHTMLEditor

from facets.core_api \
    import Str, List, Button, HasFacets

from facets.api \
    import View, VGroup, HGroup, Item, TextEditor, NotebookEditor

# The web page class:
class WebPage ( HasFacets ):

    # The URL to display:
    url = Str( 'http://google.com' )

    # The page title:
    title = Str

    # The page status:
    status = Str

    # The browser navigation buttons:
    back    = Button( '<--' )
    forward = Button( '-->' )
    home    = Button( 'Home' )
    stop    = Button( 'Stop' )
    refresh = Button( 'Refresh' )
    search  = Button( 'Search' )

    # The view to display:
    view = View(
        HGroup( 'back', 'forward', 'home', 'stop', 'refresh', 'search', '_',
                Item( 'status', style = 'readonly' ),
                show_labels = False
        ),
        Item( 'url',
              show_label = False,
              editor     = IEHTMLEditor(
                               home    = 'home',    back   = 'back',
                               forward = 'forward', stop   = 'stop',
                               refresh = 'refresh', search = 'search',
                               title   = 'title',   status = 'status' )
        )
    )

# The demo class:
class InternetExplorerDemo ( HasFacets ):

    # A URL to display:
    url = Str( 'http://' )

    # The list of web pages being browsed:
    pages = List( WebPage )

    # The view to display:
    view = View(
        VGroup(
            Item( 'url',
                  label  = 'Location',
                  editor = TextEditor( auto_set = False, enter_set = True )
            )
        ),
        Item( 'pages',
              show_label = False,
              style      = 'custom',
              editor     = NotebookEditor( deletable  = True,
                                           dock_style = 'tab',
                                           export     = 'DockWindowShell',
                                           page_name  = '.title' )
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _url_set ( self, url ):
        self.pages.append( WebPage( url = url.strip() ) )

#-- Create the demo ------------------------------------------------------------

demo = InternetExplorerDemo( pages = [
    WebPage( url = 'http://dmorrill.com' ),
    WebPage( url = 'http://amazon.com' )
] )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------