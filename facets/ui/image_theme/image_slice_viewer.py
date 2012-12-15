"""
Defines the ImageSliceViewer class for visualizing ImageSlice objects.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Str, Instance, Image, List, SyncValue, View, \
           VGroup, Item, ImageZoomEditor

from image_slice \
    import ImageSlice

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Colors used to shade the overlay regions of the ImageZoomEditor:
Fixed       = ( 0, 200, 0 )
Stretch     = ( 255, 0, 0 )
Content     = ( 0, 0, 0 )
Transparent = ( 30, )

#-------------------------------------------------------------------------------
#  'ImageSliceViewer' class:
#-------------------------------------------------------------------------------

class ImageSliceViewer ( HasPrivateFacets ):
    """ Defines the ImageSliceViewer class for visualizing ImageSlice objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The logical name of the image slice:
    name = Str

    # The ImageSlice object to visualize:
    image_slice = Instance( ImageSlice )

    # The portion of the ImageSlice image the slice data applies to:
    image = Image

    # The overlays to add to the image to indicate the slice regions:
    overlays = List

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                Item( 'image',
                      editor = ImageZoomEditor(
                                   channel  = 'red',
                                   delta    = True,
                                   overlays = SyncValue( self, 'overlays' ) )
                ),
                show_labels = False
            )
        )

    #-- Facet Default Values ---------------------------------------------------

    def _image_default ( self ):
        iso  = self.image_slice
        x, y = iso.lfx, iso.tfy

        return iso.image.crop(
            x, y, iso.rfx + iso.rfdx - x, iso.bfy + iso.bfdy - y
        )


    def _overlays_default ( self ):
        iso = self.image_slice
        if iso is None:
            return []

        x, y     = iso.lfx, iso.tfy
        overlays = [
            ( 0, 0, iso.lfdx, iso.tfdy,
              Fixed, Fixed + Transparent ),
            ( 0, iso.bfy - y, iso.lfdx, iso.bfdy,
              Fixed, Fixed + Transparent ),
            ( iso.rfx - x, 0, iso.rfdx, iso.tfdy,
              Fixed, Fixed + Transparent ),
            ( iso.rfx - x, iso.bfy - y, iso.rfdx, iso.bfdy,
              Fixed, Fixed + Transparent ),
            ( iso.hsx - x, 0, iso.sdx, iso.tfdy,
              Stretch, Stretch + Transparent ),
            ( 0, iso.vsy - y, iso.lfdx, iso.sdy,
              Stretch, Stretch + Transparent ),
            ( iso.hsx - x, iso.bfy - y, iso.sdx, iso.bfdy,
              Stretch, Stretch + Transparent ),
            ( iso.rfx - x, iso.vsy - y, iso.rfdx, iso.sdy,
              Stretch, Stretch + Transparent )
        ]

        if iso.mfdx > 0:
            overlays.extend( [
                ( iso.mfx - x, 0, iso.mfdx, iso.tfdy,
                  Fixed, Fixed + Transparent ),
                ( iso.mfx - x, iso.bfy - y, iso.mfdx, iso.bfdy,
                  Fixed, Fixed + Transparent ),
                ( iso.mfx - x, iso.vsy - y, iso.mfdx, iso.sdy,
                  Stretch, Stretch + Transparent ),
            ] )

        if iso.mfdy > 0:
            overlays.extend( [
                ( 0, iso.mfy - y, iso.lfdx, iso.mfdy,
                  Fixed, Fixed + Transparent ),
                ( iso.rfx - x, iso.mfy - y, iso.rfdx, iso.mfdy,
                  Fixed, Fixed + Transparent ),
                ( iso.hsx - x, iso.mfy - y, iso.sdx, iso.mfdy,
                  Stretch, Stretch + Transparent )
            ] )

        if (iso.mfdx > 0) and (iso.mfdy > 0):
            overlays.append(
                ( iso.mfx - x, iso.mfy - y, iso.mfdx, iso.mfdy,
                  Fixed, Fixed + Transparent )
            )

        overlays.append( (
            iso.hsx - iso.lcdx - x,
            iso.vsy - iso.tcdy - y,
            iso.sdx + iso.lcdx + iso.rcdx,
            iso.sdy + iso.tcdy + iso.bcdy,
            Content, Content + Transparent
        ) )

        return overlays

#-- EOF ------------------------------------------------------------------------
