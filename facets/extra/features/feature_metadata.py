"""
Classes and functions used to define feature metadata values or options.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasStrictFacets, List, Str, Bool

#-------------------------------------------------------------------------------
#  Metadata filters:
#-------------------------------------------------------------------------------

def is_not_none ( value ):
    return (value is not None)

#-------------------------------------------------------------------------------
#  'DropFile' class:
#-------------------------------------------------------------------------------

class DropFile ( HasStrictFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # List of valid droppable file extensions:
    extensions = List( Str )

    # Is the facet also draggable?
    draggable = Bool( False )

    # The tooltip to use for the feature:
    tooltip = Str

#-- EOF ------------------------------------------------------------------------