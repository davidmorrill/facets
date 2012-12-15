"""
The Qt4 toolkit specific implementation of a shared resource manager.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide \
    import QtGui

from facets.lib.resource.api \
    import ResourceFactory

#-------------------------------------------------------------------------------
#  'PyfaceResourceFactory' class:
#-------------------------------------------------------------------------------

class PyfaceResourceFactory ( ResourceFactory ):
    """ The Qt4 toolkit specific implementation of a shared resource manager.
    """

    #-- 'ResourceFactory' Interface --------------------------------------------

    def image_from_file ( self, filename ):
        """ Creates an image from the data in the specified filename.
        """
        return QtGui.QPixmap( filename )


    def image_from_data ( self, data, filename = None ):
        """ Creates an image from the specified data.
        """
        image = QtGui.QPixmap()
        image.loadFromData( data )

        return image

#-- EOF ------------------------------------------------------------------------