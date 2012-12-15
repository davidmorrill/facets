"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

# Facets library imports:
from facets.lib.resource.api \
    import ResourceFactory


class PyfaceResourceFactory ( ResourceFactory ):
    """ The implementation of a shared resource manager. """

    #---------------------------------------------------------------------------
    # 'ResourceFactory' toolkit interface.
    #---------------------------------------------------------------------------

    def image_from_file ( self, filename ):
        """ Creates an image from the data in the specified filename. """
        # Just return the data as a string for now.
        f = open( filename, 'rb' )
        data = f.read()
        f.close()

        return data

    def image_from_data ( self, data ):
        """ Creates an image from the specified data. """
        return data

#-- EOF ------------------------------------------------------------------------