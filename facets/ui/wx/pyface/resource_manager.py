"""
Facets pyface package component
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os
import tempfile

from cStringIO \
    import StringIO

import wx

from facets.lib.resource.api \
    import ResourceFactory

from facets.core_api \
    import Undefined

#-------------------------------------------------------------------------------
#  'PyfaceResourceFactory' class:
#-------------------------------------------------------------------------------

class PyfaceResourceFactory ( ResourceFactory ):
    """ The implementation of a shared resource manager.
    """

    #-- 'ResourceFactory' Toolkit Interface ------------------------------------

    def image_from_file ( self, filename ):
        """ Creates an image from the data in the specified filename.
        """
        # N.B 'wx.BITMAP_TYPE_ANY' tells wxPython to attempt to autodetect the
        # --- image format.
        return wx.Image( filename, wx.BITMAP_TYPE_ANY )


    def image_from_data ( self, data, filename = None ):
        """ Creates an image from the specified data.
        """
        try:
            return wx.ImageFromStream( StringIO( data ) )
        except:
            # wx.ImageFromStream is only in wx 2.8 or later(?)
            if filename is Undefined:
                return None

        handle = None
        if filename is None:
            # If there is currently no way in wx to create an image from data,
            # we have write it out to a temporary file and then read it back in:
            handle, filename = tempfile.mkstemp()

        # Write it out:
        tf = open( filename, 'wb' )
        tf.write( data )
        tf.close()

        # ... and read it back in!  Lovely 8^()
        image = wx.Image( filename, wx.BITMAP_TYPE_ANY )

        # Remove the temporary file:
        if handle is not None:
            os.close( handle )
            os.unlink( filename )

        return image

#-- EOF ------------------------------------------------------------------------