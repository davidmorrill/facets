"""
Defines a HTML browser editor used for viewing Web pages organized as a table of
contents and set of content pages. The table of content page appears on the
left, and the content pages appear on the right. This can be useful for viewing
help or other types of documentation.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Str, List, View, HSplit, Item, UIEditor, \
           BasicEditorFactory, HTMLEditor, NotebookEditor, on_facet_set

#-------------------------------------------------------------------------------
#  'HTMLPage' class:
#-------------------------------------------------------------------------------

class HTMLPage ( HasPrivateFacets ):
    """ Represents a single web content page.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The URL to be displayed:
    url = Str

    # The most recent link the user has middle mouse button clicked on:
    link = Str

    # The title of the page:
    title = Str

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'url',
              show_label = False,
              editor     = HTMLEditor( alt_url = 'link', title = 'title' )
        )
    )

#-------------------------------------------------------------------------------
#  '_HTMLBrowserEditor' class:
#-------------------------------------------------------------------------------

class _HTMLBrowserEditor ( UIEditor ):
    """ Defines a HTML browser editor used for viewing Web pages organized as a
        table of contents and set of content pages.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current set of pages being viewed:
    pages = List

    # The table of contents link most recently clicked on:
    link = Str

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HSplit(
            Item( 'value',
                  show_label = False,
                  editor     = HTMLEditor( url = 'link' )
            ),
            Item( 'pages',
                  show_label = False,
                  editor     = NotebookEditor(
                      deletable  = True,
                      dock_style = 'tab',
                      page_name  = '.title'
                  )
            ),
            id = 'splitter'
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def init_ui ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        return self.edit_facets( parent = parent, kind = 'editor' )

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        super( _HTMLBrowserEditor, self ).restore_prefs( prefs )

        self.pages = [ HTMLPage( url = url )
                       for url in prefs.get( 'urls', [] ) ]


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        result = super( _HTMLBrowserEditor, self ).save_prefs()
        if result is None:
            result = {}

        result[ 'urls' ] = [ page.url for page in self.pages ]

        return result

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'link, pages:link' )
    def _link_modified ( self, url ):
        """ Handles the 'root' facet being modified.
        """
        self.pages.append( HTMLPage( url = url ) )

#-------------------------------------------------------------------------------
#  'HTMLBrowserEditor' class:
#-------------------------------------------------------------------------------

class HTMLBrowserEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _HTMLBrowserEditor

#-- EOF ------------------------------------------------------------------------
