"""
The interface for an image cache.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Interface

#-------------------------------------------------------------------------------
#  'IImageCache' class:
#-------------------------------------------------------------------------------

class IImageCache ( Interface ):
    """ The interface for an image cache.
    """

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, width, height ):
        """ Creates a new image cache for images of the given size.
        """

    #-- 'ImageCache' Interface -------------------------------------------------

    def get_image ( self, filename ):
        """ Returns the specified image.
        """


    # FIXME v3: The need to distinguish between bitmaps and images is toolkit
    # specific so, strictly speaking, the conversion to a bitmap should be done
    # wherever the toolkit actually needs it.
    def get_bitmap ( self, filename ):
        """ Returns the specified image as a bitmap.
        """

#-------------------------------------------------------------------------------
#  'MImageCache' class:
#-------------------------------------------------------------------------------

class MImageCache ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IImageCache interface.
    """

#-- EOF ------------------------------------------------------------------------