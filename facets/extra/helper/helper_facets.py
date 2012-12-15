"""
A set of useful facet definitions.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Facet, FacetType, FacetHandler, FacetError

from facets.ui.value_tree \
    import SingleValueTreeNodeObject, FacetsNode

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from standard Python-like relation to legal method name version:
RelationMap = {
    '>=': 'ge',
    '>':  'gt',
    '<=': 'le',
    '<':  'lt',
    '=':  'eq',
    '==': 'eq',
    '!=': 'ne'
 }

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

class FacetValueHandler ( FacetHandler ):

    def validate ( self, object, name, value ):
        """ Validates that the value is a valid facet 'node'.
        """
        if (isinstance( value, SingleValueTreeNodeObject ) and
            isinstance( value.parent, FacetsNode )):
            return ( value.parent.value, value.name[1:] )

        raise FacetError

# Define the facet:
FacetValue = Facet( None, FacetValueHandler() )

#-------------------------------------------------------------------------------
#  'Size' facet:
#-------------------------------------------------------------------------------

class Size ( FacetType ):

    #-- Class Constants --------------------------------------------------------

    is_mapped     = True
    default_value = ''
    info_text     = "a size of the form: ['<='|'<'|'>='|'>'|'='|'=='|'!=']ddd"

    #-- Public Methods ---------------------------------------------------------

    def value_for ( self, value ):
        if isinstance( value, basestring ):
            value = value.strip()
            if len( value ) == 0:
                return ( 'ignore', 0 )

            relation = '<='
            c        = value[0]
            if c in '<>!=':
                relation = c
                value    = value[1:]
                c        = value[0:1]
                if c == '=':
                    relation += c
                    value     = value[1:]
                value = value.lstrip()

            relation = RelationMap[ relation ]

            try:
                size = int( value )
                if size >= 0:
                    return ( relation, size )
            except:
                pass

        raise FacetError

    mapped_value = value_for


    def post_setattr ( self, object, name, value ):
        object.__dict__[ name + '_' ] = value


    def as_cfacet ( self ):
        """ Returns a CFacet corresponding to the facet defined by this class.
        """
        # Tell the C code that the 'post_setattr' method wants the modified
        # value returned by the 'value_for' method:
        return super( Size, self ).as_cfacet().setattr_original_value( True )

#-- EOF ------------------------------------------------------------------------