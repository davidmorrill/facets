"""
Resource references.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Any, HasFacets, Instance

from resource_factory \
    import ResourceFactory

#-------------------------------------------------------------------------------
#  'ResourceReference' class:
#-------------------------------------------------------------------------------

class ResourceReference ( HasFacets ):
    """ Abstract base class for resource references.

        Resource references are returned from calls to 'locate_reference' on the
        resource manager.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The resource factory that will be used to load the resource:
    resource_factory = Instance( ResourceFactory ) # ReadOnly

    #-- 'ResourceReference' Interface ------------------------------------------

    def load ( self ):
        """ Loads the resource.
        """
        raise NotImplementedError

#-------------------------------------------------------------------------------
#  'ImageReference' class:
#-------------------------------------------------------------------------------

class ImageReference ( ResourceReference ):
    """ A reference to an image resource.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Iff the image was found in a file then this is the name of that file:
    filename = Any # ReadOnly

    # Iff the image was found in a zip file then this is the image data that
    # was read from the zip file:
    data = Any # ReadOnly

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, resource_factory, filename = None, data = None ):
        """ Creates a new image reference.
        """
        self.resource_factory = resource_factory
        self.filename         = filename
        self.data             = data

    #-- 'ResourceReference' Interface ------------------------------------------

    def load ( self ):
        """ Loads the resource.
        """
        if self.filename is not None:
            image = self.resource_factory.image_from_file( self.filename )

        elif self.data is not None:
            image = self.resource_factory.image_from_data( self.data )

        else:
            raise ValueError( "Image reference has no filename OR data" )

        return image

#-- EOF ------------------------------------------------------------------------