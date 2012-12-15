"""
A GUI-based program for querying the document index database.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Range, Enum, Instance, List, View, HGroup, VSplit, \
           Item, GridEditor, ScrubberEditor, on_facet_set

from facets.ui.grid_adapter \
    import GridAdapter

from document_classes \
    import IndexDocument, IndexWord

#-------------------------------------------------------------------------------
#  'WordAdapter' class:
#-------------------------------------------------------------------------------

class WordAdapter ( GridAdapter ):
    """ Adapts IndexWord instances for use with the GridEditor.
    """
    columns = [ ( 'Word', 'word' ), ( 'Count', 'count' ) ]

#-------------------------------------------------------------------------------
#  'DocumentAdapter'
#-------------------------------------------------------------------------------

class DocumentAdapter ( GridAdapter ):
    """ Adapts IndexDocument instances for use with the GridEditor.
    """

    columns = [ ('Document', 'document' ), ( 'Words', 'words' ) ]

#-------------------------------------------------------------------------------
#  'DocumentQuery' class:
#-------------------------------------------------------------------------------

class DocumentQuery ( HasFacets ):
    """ Represents a query against the document index.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The substring used to match a partial or complete word in the index:
    match = Str

    # The minimum word count to match:
    min_count = Range( 0, 1000000, 50 )

    # The maximum word count to match:
    max_count = Range( 0, 1000000, 1000000 )

    # The document to restrict the search to:
    document = Enum( 'Any', values = 'all_documents' )

    # The list of all documents in the document index:
    all_documents = List

    # The list of index words matching the current query values:
    words = List

    # The currently selected word:
    word = Instance( IndexWord )

    # The list of documents the currently selected word is contained in:
    documents = List

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HGroup(
            Item( 'match', springy = True ), '_',
            Item( 'min_count',
                  editor     = ScrubberEditor(),
                  width      = -60,
                  item_theme = '#themes:ScrubberEditor'
            ), '_',
            Item( 'max_count',
                  editor     = ScrubberEditor(),
                  width      = -60,
                  item_theme = '#themes:ScrubberEditor'
            ), '_',
            Item( 'document' )
        ),
        VSplit(
            Item( 'words',
                  editor = GridEditor( adapter    = WordAdapter,
                                       operations = [ 'sort' ],
                                       selected   = 'word' )
            ),
            Item( 'documents',
                  editor = GridEditor( adapter    = DocumentAdapter,
                                       operations = [ 'sort' ] )
            ),
            show_labels = False
        ),
        title     = 'Document Index Query',
        id        = 'facets.extra.mongodb.examples.document_query.'
                    'DocumentQuery',
        width     = 0.50,
        height    = 0.67,
        resizable = True
    )

    #-- Facet Default Values ---------------------------------------------------

    def _all_documents_default ( self ):
        return ([ 'Any' ] + [ id.document for id in IndexDocument().all() ])


    def _words_default ( self ):
        return self._query_words()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'match, min_count, max_count, document' )
    def _query_modified ( self ):
        """ Handles any facet affecting the current query being changed.
        """
        self.word  = None
        self.words = self._query_words()


    def _word_set ( self, word ):
        """ Handles the 'word' facet being changed.
        """
        documents = []
        if word is not None:
            documents = [ IndexDocument( document = document ).load()
                          for document in word.documents ]

        self.documents = documents

    #-- Private Methods --------------------------------------------------------

    def _query_words ( self ):
        """ Returns all words matching the current query parameters.
        """
        query = []
        if self.match != '':
            query.append( "(word == '/%s/')" % self.match )

        if self.min_count > 1:
            query.append( '(count >= %s)' % self.min_count )

        if self.max_count < 1000000:
            query.append( '(count <= %s)' % self.max_count )

        if self.document != 'Any':
            query.append( "(documents == ['%s'])" %
                          self.document.replace( '\\', '\\\\' ) )

        return IndexWord().all( ' and '.join( query ) )

#-- Run the program ------------------------------------------------------------

if __name__ == '__main__':
    DocumentQuery().edit_facets()

#-- EOF ------------------------------------------------------------------------
