"""
Defines the markdown tool for rendering text using markdown-style markup.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, SyncValue, View, UItem

from tools \
    import Tool

from facets.extra.markdown.markdown \
    import MarkdownEditor

#-------------------------------------------------------------------------------
#  'Markdown' class:
#-------------------------------------------------------------------------------

class Markdown ( Tool ):
    """ Renders a web page with the HTML generated from a markdown encoded text
        string or file.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Markdown' )

    # The markdown encoded text of file name to render:
    markdown = Str( connect = 'to: markdown encoded text or .md file name' )

    # The CSS rules or file name used to render the rendered markdown page:
    css = Str( connect = 'to: CSS rules or .css file name' )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'markdown',
                   editor = MarkdownEditor( css = SyncValue( self, 'css' ) )
            )
        )

#-------------------------------------------------------------------------------
#  'MarkdownHTML' class:
#-------------------------------------------------------------------------------

class MarkdownHTML ( Tool ):
    """ Displays the HTML generated from a markdown encoded text string or file.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Markdown HTML' )

    # The markdown encoded text of file name to render:
    markdown = Str( connect = 'to: markdown encoded text or .md file name' )

    # The CSS rules or file name used to render the rendered markdown page:
    css = Str( connect = 'to: CSS rules or .css file name' )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'markdown',
                   editor = MarkdownEditor(
                       css      = SyncValue( self, 'css' ),
                       show_raw = True
                   )
            )
        )

#-- EOF ------------------------------------------------------------------------
