"""
A custom editor for tiling an image over the background of a control.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Range, Color, Image, on_facet_set

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.pyface.i_image_resource \
    import AnImageResource

#-------------------------------------------------------------------------------
#  '_ImageTilerEditor' class:
#-------------------------------------------------------------------------------

class _ImageTilerEditor ( ControlEditor ):
    """ A custom editor for tiling images.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor image:
    value = Image

    #-- ControlEditor Method Overrides ----------------------------------------------

    def paint_all ( self, g ):
        """ Paints the contents of the control into the graphics context
            specified by *g*.
        """
        factory = self.factory
        dx, dy  = self.control.size
        g.brush = factory.bg_color
        g.pen   = None
        g.draw_rectangle( 0, 0, dx, dy )
        g.brush = None
        g.pen   = factory.bg_color
        image   = self.value
        if isinstance( image, AnImageResource ):
            bitmap       = image.bitmap
            border       = factory.border
            x, y         = factory.x_origin, factory.y_origin
            sx, sy       = factory.x_shift,  factory.y_shift
            idx, idy     = image.width, image.height
            idx         += (2 * border)
            idy         += (2 * border)
            sdx          = max( idx - border + factory.x_spacing, 1 )
            sdy          = max( idy - border + factory.y_spacing, 1 )
            min_j, max_j = 99999, -99999
            div          = (sdx * sdy) - (sx * sy)
            for xp in ( 1 - idx, dx - 1 ):
                for yp in ( 1 - idy, dy - 1 ):
                    j     = ((sdx * (yp - y)) - (sy * (xp - x))) / div
                    min_j = min( min_j, j )
                    max_j = max( max_j, j )

            count = max( 1000, 200 * ((dx * dy) / (idx * idy)) )
            for j in xrange( min_j, max_j + 1 ):
                i  = (x + (j * sx) + idx - 1) / sdx
                cx = x - (i * sdx) + (j * sx)
                cy = y - (i * sy)  + (j * sdy)

                if sy > 0:
                    if (cy + idy) <= 0:
                        k   = -((cy + idy) / sy)
                        cy += (k * sy)
                        cx += (k * sdx)
                elif sy < 0:
                    if cy >= dy:
                        k   = ((cy - dy) / (-sy)) + 1
                        cy += (k * sy)
                        cx += (k * sdx)

                while cx < dx:
                    if ((count <= 0)                     or
                        ((sy < 0) and ((cy + idy) <= 0)) or
                        ((sy > 0) and (cy >= dy))):
                        break

                    for i in xrange( border ):
                        g.draw_rectangle( cx + i, cy + i,
                                          idx - (2 * i), idy - (2 * i) )

                    g.draw_bitmap( bitmap, cx + border, cy + border )
                    count -= 1
                    cx    += sdx
                    cy    += sy

                if count <= 0:
                    break

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:[bg_color, border, x_spacing, y_spacing, x_shift, y_shift, x_origin, y_origin]' )
    def _refresh_needed ( self ):
        """ Handles any facet requiring the editor to be refreshed being
            changed.
        """
        self.refresh()

#-------------------------------------------------------------------------------
#  'ImageTilerEditor' class:
#-------------------------------------------------------------------------------

class ImageTilerEditor ( CustomControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ImageTilerEditor

    # The background color for the editor:
    bg_color = Color( 0xF0F0F0, facet_value = True )

    # The width of the border to draw around each image:
    border = Range( 0, 32, facet_value = True )

    # The amount of horizontal spacing between tiled images:
    x_spacing = Range( -1024, 1024, 0, facet_value = True )

    # The amount of vertical spacing between tiled images:
    y_spacing = Range( -1024, 1024, 0, facet_value = True )

    # The amount of horizontal shift applied to each new row:
    x_shift = Range( -1024, 1024, 0, facet_value = True )

    # The amount of vertical shift applied to each new column:
    y_shift = Range( -1024, 1024, 0, facet_value = True )

    # The x coordinate of the top-left tiled image:
    x_origin = Range( -1024, 1024, 0, facet_value = True )

    # The y coordinate of the top-left tiled image:
    y_origin = Range( -1024, 1024, 0, facet_value = True )

#-- EOF ------------------------------------------------------------------------
