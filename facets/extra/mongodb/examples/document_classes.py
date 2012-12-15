"""
Defines the classes used to implement the document indexing example.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.extra.mongodb.api \
    import MongoDBObject, DBStr, DBInt, DBSet

#-------------------------------------------------------------------------------
#  'IndexDocument' class:
#-------------------------------------------------------------------------------

class IndexDocument ( MongoDBObject ):
    """ Represents a document in the document index.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the document:
    document = DBStr

    # The total number of words contained in the document:
    words = DBInt

#-------------------------------------------------------------------------------
#  'IndexWord' class:
#-------------------------------------------------------------------------------

class IndexWord ( MongoDBObject ):
    """ Represents the index information for a specific word.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The word:
    word = DBStr( index = True )

    # The number of times the word is used in all documents:
    count = DBInt

    # The set of documents the word occurs in:
    documents = DBSet

#-- EOF ------------------------------------------------------------------------
