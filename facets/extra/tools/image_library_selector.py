"""
Defines the ImageLibrarySelector tool for selecting images in the standard
Facets image library.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Image, Str, View, UItem

from facets.extra.editors.image_library_editor \
    import ImageLibraryEditor

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ImageLibrarySelector' class:
#-------------------------------------------------------------------------------

class ImageLibrarySelector ( Tool ):
    """ Defines the ImageLibrarySelector tool for selecting images in the
        standard Facets image library.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Image Library Selector' )

    # The currently selected image:
    image = Image( connect = 'from' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'image', editor = ImageLibraryEditor() )
    )

#-- EOF ------------------------------------------------------------------------
