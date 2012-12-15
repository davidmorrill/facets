"""
Defines the query_from_string function which translates a Python-like expression
into an equivalent MongoDB query document.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from facets.api \
    import HasPrivateFacets, Any, Str, Bool, Property, FacetError

from facets.core.facet_base \
    import Undefined

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Regular expression patterns used to perform substitution in a query string:
and_pat  = re.compile( r'([^_a-zA-Z0-9])and([^_a-zA-Z0-9])' )
or_pat   = re.compile( r'([^_a-zA-Z0-9])or([^_a-zA-Z0-9])' )
not_pat  = re.compile( r'([^_a-zA-Z0-9])not([^_a-zA-Z0-9])' )
not_pat2 = re.compile( r'^not([^_a-zA-Z0-9])' )

# Mapping from Perl-style regular expression modifiers to Python equivalents:
RegexModifiers = {
    'i': re.IGNORECASE
}

#-------------------------------------------------------------------------------
#  'query_from'string' function:
#-------------------------------------------------------------------------------

def query_from_string ( query ):
    """ Translates the specified *query* string into an equivalent MongoDB
        query document.
    """
    query = and_pat.sub(  r'\1&\2',
            or_pat.sub(   r'\1|\2',
            not_pat.sub(  r'\1!\2',
            not_pat2.sub( r'!\1', query ) ) ) )

    return eval( query, globals(), DBQueryDict() ).document

#-------------------------------------------------------------------------------
#  'DBQuery' class:
#-------------------------------------------------------------------------------

class DBQuery ( HasPrivateFacets ):
    """ Defines a DBQuery class used to represent terms in a query expression.
        This class is actually a hack that leverages the ability to override
        many (but not all) of the basic Python operators (like '>', '==', ...).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the query term:
    name = Str

    # The query document fragment for this term:
    document = Any( {} )

    # The modulus value for name % n:
    modulus = Any

    # Does the expression reference the 'size' property?
    has_size = Bool( False )

    # Does the name have the 'len' function applied to it?
    size = Property

    # Handles a 'name.exists' term:
    exists = Property

    #-- object Method Overrides ------------------------------------------------

    def __getitem__ ( self, key ):
        self.name = '%s.%s' % ( self.name, key )

        return self


    def __getslice__ ( self, i, j ):
        pass


    def __lt__ ( self, other ):
        self.document[ self.name ] = { '$lt': other }

        return self


    def __le__ ( self, other ):
        self.document[ self.name ] = { '$lte': other }

        return self


    def __gt__ ( self, other ):
        self.document[ self.name ] = { '$gt': other }

        return self


    def __ge__ ( self, other ):
        self.document[ self.name ] = { '$gte': other }

        return self


    def __eq__ ( self, other ):
        other = self._check_regex( other )
        if isinstance( other, list ):
            self.document[ self.name ] = { '$in': other }
        elif isinstance( other, set ):
            self.document[ self.name ] = { '$all': list( other ) }
        elif self.has_size:
            self.document[ self.name ] = { '$size': other }
        elif self.modulus is not None:
            self.document[ self.name ] = { '$mod': [ self.modulus, other ] }
        else:
            self.document[ self.name ] = other

        return self


    def __ne__ ( self, other ):
        other = self._check_regex( other )
        if isinstance( other, list ):
            value = { '$nin': other }
        elif isinstance( other, set ):
            value = { '$not': { '$all': list( other ) } }
        elif self.has_size:
            self.document[ self.name ] = { '$not': { '$size': other } }
        elif self.modulus is not None:
            value = { '$not': { '$mod': [ self.modulus, other ] } }
        else:
            value = { '$ne': other }

        self.document[ self.name ] = value

        return self


    def __neg__ ( self ):
        self.document = { '$not': self.document }

        return self


    def __or__ ( self, other ):
        self_document  = self.document
        other_document = other.document
        if (len( self_document ) == 1) and ('$or' in self_document):
            if (len( other_document ) == 1) and ('$or' in other_document):
                self_document[ '$or' ] = (self_document[  '$or' ] +
                                          other_document[ '$or' ])
            else:
                self.document[ '$or' ].append( other_document )
        elif (len( other_document ) == 1) and ('$or' in other_document):
            other_document[ '$or' ].insert( 0, self_document )
            self.document = other_document
        else:
            self.document = { '$or': [ self.document, other_document ] }

        old_items = self.document[ '$or' ]
        new_items = []
        i         = 0
        while i < len( old_items ):
            item = old_items[ i ]
            if len( item ) == 1:
                key, value = item.items()[0]
                if not isinstance( value, dict ):
                    value = { '$in': [ value ] }
                elif (len( value ) != 1) or (value.keys()[0] != '$in'):
                    value = None

                if value is not None:
                    matches = value[ '$in' ]
                    for j in xrange( len( old_items ) -1, i, -1 ):
                        item2 = old_items[ j ]
                        if len( item2 ) == 1:
                            key2, value2 = item2.items()[0]
                            if key2 == key:
                                if not isinstance( value2, dict ):
                                    matches.append( value2 )
                                elif ((len( value2 ) == 1) and
                                          (value2.keys()[0] == '$in')):
                                    matches.extend( value2[ '$in' ] )
                                else:
                                    continue

                                del old_items[ j ]

                    matches = sorted( list( set( matches ) ) )
                    if len( matches ) > 1:
                        item = { key: { '$in': matches } }

            new_items.append( item )
            i += 1

        self.document[ '$or' ] = new_items

        return self


    def __and__ ( self, other ):
        document = self.document
        for key, value2 in other.document.iteritems():
            value1 = document.get( key, Undefined )
            if value1 is not Undefined:
                if not isinstance( value1, dict ):
                    document[ key ] = value1 = { '$in': [ value1 ] }

                if not isinstance( value2, dict ):
                    value2 = { '$in': [ value2 ] }

                for sub_key, sub_value in value2.iteritems():
                    if not sub_key in value1:
                        value1[ sub_key ] = sub_value
                    else:
                        raise FacetError(
                            'Duplicate operators found in query expression'
                        )
            else:
                document[ key ] = value2

        return self


    def __mod__ ( self, other ):
        self.modulus = other

        return self


    def __getattr__ ( self, name ):
        self.name = '%s.%s' % ( self.name, name )

        return self


    def __call__ ( self, expr ):
        self.document[ self.name ] = { '$elemMatch': expr.document }

        return self

    #-- Property Implementations -----------------------------------------------

    def _get_size ( self ):
        self.has_size = True

        return self


    def _get_exists ( self ):
        self.document[ self.name ] = { '$exists': True }

        return self

    #-- Private Methods --------------------------------------------------------

    def _check_regex ( self, value ):
        """ Checks to see if *value* appears to be a MongoDB style regular
            expression, and if so, returns its Python equivalent. Otherwise it
            simply returns the original *value*.
        """
        if isinstance( value, basestring ) and value.startswith( '/' ):
            col = value.rfind( '/' )
            if col > 0:
                flags = 0
                for modifier in value[ col + 1: ]:
                    flag = RegexModifiers.get( modifier )
                    if flag is None:
                        return value

                    flags |= flag

                try:
                    return re.compile( value[ 1: col ], flags )
                except:
                    pass

        return value

#-------------------------------------------------------------------------------
#  'DBQueryDict' class:
#-------------------------------------------------------------------------------

class DBQueryDict ( dict ):
    """ Defines a dictionary-like object for use with the 'eval' function that
        returns a DBQuery object for any undefined key. This eliminates the
        need for the 'query_from_string' function to know in advance every
        symbol the query expression might contain.
    """

    #-- Public Methods ---------------------------------------------------------

    def __getitem__ ( self, key ):
        if not self.has_key( key ):
            return DBQuery( name = key )

        return dict.__getitem__( self, key )


    def get ( self, key, default ):
        if not self.has_key( key ):
            return DBQuery( name = key )

        return dict.get( self, key, default )

#-- EOF ------------------------------------------------------------------------
