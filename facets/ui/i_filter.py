"""
Defines the IFilter interface which any filter class must implement.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasStrictFacets, Interface, Event, Bool, implements

#-------------------------------------------------------------------------------
#  'IFilter' interface:
#-------------------------------------------------------------------------------

class IFilter ( Interface ):
    """ The interface that any filter class must implement.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the filter active?
    active = Bool

    # Event fired when the filter criteria defined by the filter has changed
    # (Thus necessitating that the filter be reapplied to all objects):
    changed = Event

    #-- Interface Methods ------------------------------------------------------

    def filter ( self, object ):
        """ Returns True if object is accepted by the filter, and False if it is
            not.
        """

#-------------------------------------------------------------------------------
#  'Filter' class:
#-------------------------------------------------------------------------------

class Filter ( HasStrictFacets ):
    """ Base class for a filter that implements IFilter.
    """

    implements( IFilter )

    #-- Facet Definitions ------------------------------------------------------

    # Is the filter active?
    active = Bool( True )

    # Event fired when the filter criteria defined by the filter has changed
    # (Thus necessitating that the filter be reapplied to all objects):
    changed = Event

    #-- Interface Methods ------------------------------------------------------

    def filter ( self, object ):
        """ Returns True if object is accepted by the filter, and False if it is
            not.

            This method should be overridden by any subclass.
        """
        return True

    #-- Facet Event Handlers ---------------------------------------------------

    def _anyfacet_set ( self, facet ):
        """ Handles any facet on the filer being changed by indicating that the
            filter has been changed.
        """
        if facet != 'changed':
            self.changed = True

#-- EOF ------------------------------------------------------------------------