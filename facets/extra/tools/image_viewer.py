"""
Defines the image viewer tool that allows viewing images.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Bool, Image, View, HGroup, Item, UItem, ImageEditor, \
           SyncValue, spring

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.extra.helper.multi_page_tool \
    import MultiPageTool, PageTool, OwnerValue

#-------------------------------------------------------------------------------
#  'ImageViewerPage' class:
#-------------------------------------------------------------------------------

class ImageViewerPage ( PageTool ):

    #-- Facet Definitions ------------------------------------------------------

    # The current image being viewed:
    image = Image( cache = False )

    # The item external tools connect to provide the image to view:
    value = Any( connect = 'to' )

    # Should images automatically be scaled to fit the control size?
    auto_scale = OwnerValue

    # The name of the page:
    page_name = Any

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'image',
                   editor = ImageEditor(
                       auto_scale = SyncValue( self, 'auto_scale' )
                   )
            )
        )

    #-- Facet Default Values ---------------------------------------------------

    def _page_name_default ( self ):
        return (self.image.name if self.image is not None else None)

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self, value ):
        """ Handles the 'value' facet being changed.
        """
        if isinstance( value, ( list, tuple ) ) and (len( value ) > 0):
            value = value[0]

        if isinstance( value, ( basestring, AnImageResource ) ):
            self.image = value
        else:
            self.image = '@std:alert16'

#-------------------------------------------------------------------------------
#  'ImageViewer' class:
#-------------------------------------------------------------------------------

class ImageViewer ( MultiPageTool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Image Viewer'

    # The page tool class this tool creates and manages:
    page_tool_class = ImageViewerPage

    # The item external tools connect to provide the image to view:
    value = Any( connect = 'to' )

    # Should images automatically be scaled to fit the control size?
    auto_scale = Bool( True, save_state = True )

    #-- Facets View Definitions ------------------------------------------------

    page_options = HGroup( Item( 'auto_scale' ) )

#-- EOF ------------------------------------------------------------------------