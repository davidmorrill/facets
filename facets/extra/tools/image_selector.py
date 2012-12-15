"""
Defines the ImageSelector tool for selecting images using a FilmStripEditor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Image, Str, List, Any, View, UItem, FilmStripEditor

from facets.ui.filmstrip_adapter \
    import FilmStripAdapter

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'FSAdapter' class:
#-------------------------------------------------------------------------------

class FSAdapter ( FilmStripAdapter ):
    """ Adapts the items in the 'images' list for display in the
        FilmStripEditor.
    """

    def get_image ( self, value ):
        return value[1]


    def get_label ( self, value ):
        return value[0]

#-------------------------------------------------------------------------------
#  'ImageSelector' class:
#-------------------------------------------------------------------------------

class ImageSelector ( Tool ):
    """ Defines the ImageSelector tool for selecting images using a
        FilmStripEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Image Selector' )

    # The most recently passed in image:
    image_in = Image( connect = 'to: input image' )

    # The currently selected image:
    image_out = Image( connect = 'from: output image' )

    # The list of all available images;
    images = List # ( ( name, image ) )

    # The currently selected ( name, image ) tuple:
    selected = Any

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'images',
               height = -100,
               editor = FilmStripEditor( adapter  = FSAdapter(),
                                         selected = 'selected' )
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _image_in_set ( self, image ):
        """ Handles the 'image_in' facet being changed.
        """
        item = ( image.name, image )
        if item not in self.images:
            self.images.append( item )


    def _selected_set ( self, selected ):
        self.image_out = selected[1]

#-- EOF ------------------------------------------------------------------------
