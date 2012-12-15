"""
Defines the FacetAnimation class that animates a specified facet value on a
specified HasFacets object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Instance, Str

from animation \
    import Animation

#-------------------------------------------------------------------------------
#  'FacetAnimation' class:
#-------------------------------------------------------------------------------

class FacetAnimation ( Animation ):
    """ Defines the FacetAnimation class that animates a specified facet value
        on a specified HasFacets object.
    """

    #-- Public Facets ----------------------------------------------------------

    # The HasFacets object whose facet is being animated:
    object = Instance( HasFacets )

    # The name of the facet on the object being animated:
    name = Str

    #-- Default Value Methods --------------------------------------------------

    def _begin_default ( self ):
        return getattr( self.object, self.name )

    #-- Concrete Subclass Methods ----------------------------------------------

    def frame ( self, value ):
        """ Handles updating the animatable object with the current frame data,
            specified by '*value'.
        """
        try:
            setattr( self.object, self.name, value )
        except:
            try:
                setattr( self.object, self.name, int( round( value ) ) )
            except:
                pass

#-- EOF ------------------------------------------------------------------------
