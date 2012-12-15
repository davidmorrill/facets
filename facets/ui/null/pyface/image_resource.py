"""
Null toolkit implementation of an ImageResource.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import abspath

from facets.core_api \
    import Any, cached_property

from facets.ui.pyface.i_image_resource \
    import MImageResource

#-------------------------------------------------------------------------------
#  'ImageResource' class:
#-------------------------------------------------------------------------------

class ImageResource ( MImageResource ):
    """ The 'null' toolkit specific implementation of an ImageResource. See the
        i_image_resource module for the API documentation.
    """

    #-- Private interface ------------------------------------------------------

    # The resource manager reference for the image.
    _ref = Any

    #-- 'ImageResource' Interface ----------------------------------------------

    def create_bitmap ( self, size = None ):
        return self.create_image( size )


    def create_icon ( self, size = None ):
        return self.create_image( size )

    #-- Private Interface ------------------------------------------------------

    @cached_property
    def _get_absolute_path ( self ):
        # FIXME: This doesn't quite work with the new notion of image size. We
        # should find out who is actually using this facet, and for what!
        # (AboutDialog uses it to include the path name in some HTML.)
        ref = self._get_ref()
        if ref is not None:
            return abspath( self._ref.filename )

        return self._get_image_not_found().absolute_path

#-- EOF ------------------------------------------------------------------------