"""
Defines the TextCollector tool for collecting input text strings and organizing,
filtering, displaying and selecting them.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from time \
    import time

from facets.api \
    import HasPrivateFacets, Str, Float, Bool, Range, List, Instance, Image, \
           View, VGroup, UItem, GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.pyface.timer.api \
    import do_after

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'TextItem' class:
#-------------------------------------------------------------------------------

class TextItem ( HasPrivateFacets ):
    """ Represents a single text string.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The text string:
    text = Str

    # The time stamp of when it was last selected:
    time_stamp = Float( '@icons2:Delete' )

#-------------------------------------------------------------------------------
#  'TextItemAdapter' class:
#-------------------------------------------------------------------------------

class TextItemAdapter ( GridAdapter ):

    columns = [ ( 'X', 'delete' ), ( 'Text', 'text' ), ( 'Lines', 'lines' ) ]

    even_bg_color    = 0xF8F8F8
    text_auto_filter = Bool( True )

    delete_text      = Str
    delete_image     = Image( '@icons2:Delete' )
    delete_alignment = Str( 'center' )
    delete_width     = Float( 25 )

    lines_alignment  = Str( 'center' )
    lines_width      = Float( 50 )

    def text_text ( self ):
        return self.item.text.strip().replace( '  ', ' ' )


    def lines_text ( self ):
        lines = self.item.text.split( '\n' )

        return str( len( lines ) - (lines[-1] == '') )


    def delete_clicked ( self ):
        self.object.delete( self.item )

#-------------------------------------------------------------------------------
#  'TextCollector' class:
#-------------------------------------------------------------------------------

class TextCollector ( Tool ):
    """ Defines the TextCollector tool for collecting input text strings and
        organizing, filtering, displaying and selecting them.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Text Collector'

    # The input text string:
    input_text = Str( connect = 'to: input text' )

    # The current output text string:
    output_text = Str( connect = 'from: output text' )

    # The currently selected text item:
    selected = Instance( TextItem )

    # The list of currently collected text strings:
    texts = List( save_state = True ) # ( Instance( TextItem ) )

    # The maximum number of text string to collect:
    max_texts = Range( 1, 500, 25, save_state = True )

    #-- Facet View Definitions -------------------------------------------------

    facets_view = View(
        UItem( 'texts',
               editor = GridEditor(
                   adapter = TextItemAdapter,
                   operations = [], # [ 'sort' ],
                   selected   = 'selected'
               )
        ),
        title = 'Text Collector',
        id    = 'facets.extra.tools.text_collector.TextCollector',
        width     = 0.5,
        height    = 0.5,
        resizable = True
    )


    options = View(
        VGroup(
            Scrubber( 'max_texts', 'The maximum number of text items',
                label = 'Maximum text items'
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def delete ( self, item ):
        """ Deletes the TextItem specified by *item*.
        """
        self.texts.remove( item )

    #-- Facet Event Handlers ---------------------------------------------------

    def _input_text_set ( self, text ):
        """ Handles the 'input_text' facet being modified.
        """
        for item in self.texts:
            if text == item.text:
                return

        self.texts.append( TextItem( text = text, time_stamp = time () ) )
        self._check_count()


    def _selected_set ( self, item ):
        """ Handles the 'selected' facet being changed.
        """
        if item is not None:
            self.output_text = item.text
            item.time_stamp  = time()


    def _max_texts_set ( self ):
        do_after( 1000, self._check_count )

    #-- Private Methods --------------------------------------------------------

    def _check_count ( self ):
        """ Checks the number of text items against the maximum text count and
            eliminates any excess items using an LRU algorithm.
        """
        texts = self.texts
        if len( texts ) > self.max_texts:

            # Extract out item indices and time stamps:
            items = [ ( i, item.time_stamp ) for i, item in enumerate( texts ) ]

            # Sort with most recent time stamps first:
            items.sort( lambda l, r: cmp( r[1], l[1] ) )

            # Delete the newest time stamp items:
            del items[ : self.max_texts ]

            # Sort remaining items in reverse index order:
            items.sort( lambda l, r: cmp( r[0], l[0] ) )

            # Delete the eliminated TextItems:
            for i, _ in items:
                del texts[ i ]

#-- EOF ------------------------------------------------------------------------
