"""
A command-line tool for indexing a new document.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from time \
    import time

from os.path \
    import abspath, splitext

from glob \
     import iglob

from cStringIO \
    import StringIO

from tokenize \
    import generate_tokens, ENDMARKER, NAME

from facets.api \
    import HasFacets, Any

from facets.core.facet_base \
    import  read_file

from document_classes \
    import IndexDocument, IndexWord

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The correct command usage message:
Usage = """
The correct usage is:
    python document_index.py document [ document, ..., document ]
where:
    document = The name of a text or Python (.py) source file to be indexed.
"""[1:-1]

# The set of valid characters that can appear in a word:
Letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# The set of Python keywords:
PythonKeywords = set( [
    'class', 'def', 'if', 'else', 'elif', 'for', 'in', 'try', 'except',
    'finally', 'from', 'import', 'return', 'break', 'continue', 'while', 'not',
    'and', 'or', 'assert', 'raise', 'del', 'print', 'yield', 'global', 'exec',
    'with', 'as', 'is'
] )

#-------------------------------------------------------------------------------
#  'DocumentIndex' class:
#-------------------------------------------------------------------------------

class DocumentIndexer ( HasFacets ):
    """ Allows new documents to be added to the document index database.
    """

    #-- Facet Definitions ------------------------------------------------------

    # A mapping from words we've already seen to IndexWord objects:
    all_words = Any( {} )

    #-- Public Methods ---------------------------------------------------------

    def add ( self, document ):
        """ Adds the document whose file name is specified by *document* to the
            document index database.
        """
        # Normalize the document path:
        document = abspath( document )

        # Only index documents that we have not already indexed previously:
        if IndexDocument( document = document ).load() is not None:
            print ("'%s' has already been indexed and is being ignored." %
                   document)

            return False

        # Read the contents of the document (if possible):
        text = read_file( document )
        if text is None:
            print "'%s' could not be read and is being ignored." % document

            return False

        # Select the parsing method to use (Python or normal text):
        if splitext( document )[1] == '.py':
            next_word = self.parse_python( text )
        else:
            next_word = self.parse_text( text )

        # Parse the document into words and add each valid word to the document
        # index, creating new entries in the index for newly encountered words:
        words     = 0
        all_words = self.all_words
        for word in next_word():
            index_word = all_words.get( word )
            if index_word is None:
                all_words[ word ] = index_word = \
                    IndexWord( word = word ).load( add = True )

            index_word.documents.add( document )
            index_word.count += 1
            words            += 1

        # Add a new entry for the document to the index:
        IndexDocument( document = document, words = words ).save()

        # Indicate that the document was processed successfully:
        print "'%s' has been added to the document index." % document

        return True

    #-- Private Methods --------------------------------------------------------

    def parse_python ( self, source ):
        """ Sets up to parse the Python source whose contents are specified by
            *source* into a stream of words. Returns an iterator which returns
            the next word from the source on each call.
        """
        tokenizer = generate_tokens( StringIO( source ).readline )

        def parse ( ):
            try:
                for type, token, first, last, line in tokenizer:
                    if type == ENDMARKER:
                        break

                    if (type == NAME) and (token not in PythonKeywords):
                        yield token
            except:
                pass

        return parse


    def parse_text ( self, text ):
        """ Sets up to parse the text document whose contents are specified by
            *source* into a stream of words. Returns an iterator which returns
            the next word from the document on each call.
        """
        def parse ( ):
            for word in text.split():
                word = (''.join( [ c for c in word if c in Letters ] ).lower())
                if word != '':
                    yield word

        return parse

#-- Run the command ------------------------------------------------------------

if __name__ == '__main__':
    # Make sure the command usage is correct, otherwise print an error and exit:
    if len( sys.argv ) < 2:
        print Usage
        sys.exit( 1 )

    # Create a document indexer and use it to index each command line document:
    now       = time()
    documents = 0
    indexer   = DocumentIndexer()
    for pattern in sys.argv[1:]:
        for document in iglob( pattern ):
            documents += indexer.add( document )

    # Display a summary of the indexing results and execution time:
    print '-' * 79
    print '%d document%s processed in %.3f seconds.' % (
          documents, 's'[ documents == 1: ], time() - now )

#-- EOF ------------------------------------------------------------------------
