"""
Defines the AbstractAdapter base class used as the common base class for various
GUI toolkit adapter classes.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets

#-------------------------------------------------------------------------------
#  'AbstractAdapter' class:
#-------------------------------------------------------------------------------

class AbstractAdapter ( HasPrivateFacets ):
    """ Abstract adapter base class for both the Control and Layout classes.
    """

#-- EOF ------------------------------------------------------------------------