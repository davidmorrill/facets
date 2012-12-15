"""
Defines the Saveable class, a mix-in class which allows an object to specify
that it has saveable state that needs to be persisted, as well as a mechanism
for persisting the state.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Bool

#-------------------------------------------------------------------------------
#  'Saveable' class:
#-------------------------------------------------------------------------------

class Saveable ( HasPrivateFacets ):
    """ Defines the Saveable class, a mix-in class which allows an object to
        specify that it has saveable state that needs to be persisted, as well
        as a mechanism for persisting the state.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Set true when the object needs to have its state saved:
    needs_save = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def save ( self ):
        """ The method called to save the state of the objec.
        """
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------