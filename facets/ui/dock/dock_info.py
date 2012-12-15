"""
Defines information about a region of a DockWindow used while the user is
reorganizing the contents of a DockWindow via dragging.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Range, Instance, Image, Any

from dock_constants \
    import DOCK_TOP, DOCK_BOTTOM, DOCK_LEFT, DOCK_RIGHT, DOCK_XCHG,         \
           DOCK_EXPORT, DOCK_TAB, DOCK_TABADD, DOCK_NONE, DOCK_BAR, Bounds, \
           DragTabPen, DragTabBrush, DragSectionPen1, DragSectionPen2,      \
           DragSectionPen3, DragSectionBrush1, DragSectionBrush2

from dock_region \
    import DockRegion

from dock_section \
    import DockSection

from facets.ui.dock.dock_control \
    import DockControl

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The pens/brushes used for drawing tab and section overlays:
tab_pens = (
    DragTabPen, DragTabBrush, DragTabPen, DragTabBrush
)

section_pens = (
    DragSectionPen1, DragSectionBrush1, DragSectionPen2, DragSectionBrush2,
    DragSectionPen3
)

#-------------------------------------------------------------------------------
#  'DockInfoImages' class:
#-------------------------------------------------------------------------------

class DockInfoImages ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # Images drawn within a DockInfo docking overlay:
    up    = Image( '@facets:dw_up?H60L14S72'    )
    down  = Image( '@facets:dw_down?H60L14S72'  )
    left  = Image( '@facets:dw_left?H60L14S72'  )
    right = Image( '@facets:dw_right?H60L14S72' )
    xchg  = Image( '@facets:dw_xchg?H60L14S72'  )
    tab   = Image( '@facets:dw_up?H33l2S62'  )

    # List of all images in 'DOCK_xxx' order:
    images = Any

    #-- Facet Default Values ---------------------------------------------------

    def _images_default ( self ):
        return [ self.up, self.down, self.left, self.right, self.xchg ]

# Create a reusable instance:
dock_info_images = DockInfoImages()

#-------------------------------------------------------------------------------
#  'DockInfo' class:
#-------------------------------------------------------------------------------

class DockInfo ( HasPrivateFacets ):
    """ Defines information about a region of a DockWindow used while the
        user is reorganizing the contents of a DockWindow via dragging.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Dock kind:
    kind = Range( DOCK_TOP, DOCK_EXPORT )

    # Dock bounds:
    bounds = Bounds

    # Dock Region:
    region = Instance( DockRegion )

    # Dock Control:
    control = Instance( 'facets.ui.dock.dock_item.DockItem' )

    #-- Public Methods ---------------------------------------------------------

    def draw ( self, window, bitmap = None ):
        """ Draws the DockInfo on the display.
        """
        if bitmap is None:
            bitmap = self._bitmap
            if bitmap is None:
                return
        else:
            self._bitmap = bitmap

        sg, bx, by = window.screen_graphics
        bg         = sg.graphics_bitmap( bitmap )
        bdx, bdy   = bg.size
        bg2        = sg.graphics_buffer( bdx, bdy, alpha = True )
        bg2.blit( 0, 0, bdx, bdy, bg )
        bg2.pen   = None
        bg2.brush = ( 0, 0, 0, 48 )
        bg2.draw_rectangle( 0, 0, bdx, bdy )

        kind = self.kind
        if DOCK_TOP <= kind <= DOCK_TABADD:
            x, y, dx, dy = self.bounds
            cx           = x + (dx / 2)
            if DOCK_TAB <= kind <= DOCK_TABADD:
                pens   = tab_pens
                radius = 32
                cy     = y + dy + radius + 3
                image  = dock_info_images.tab
            else:
                pens   = section_pens
                radius = min( 50, (dx - 16) / 2, (dy - 16) / 2 )
                cy     = y + (dy / 2)
                image  = dock_info_images.images[ kind ]

            # Draw the bordered rectangle:
            bg2.pen   = pens[0]
            bg2.brush = pens[1]
            bg2.draw_rectangle( x + 3, y + 3, dx - 4, dy - 4 )

            # If the radius is large enough, draw the bordered circle and arrow
            # image:
            if radius >= 12:
                bg2.brush = pens[3]
                bg2.pen   = pens[2]
                if radius < 24:
                    bg2.pen = pens[4]

                bg2.draw_circle( cx, cy, radius )
                idx, idy = image.width, image.height
                scale    = (1.56 * radius) / max( idx, idy )
                ddx      = int( round( idx * scale ) )
                ddy      = int( round( idy * scale ) )
                bg2.blit( cx - (ddx / 2), cy - (ddy / 2), ddx, ddy,
                          image.bitmap, 0, 0, idx, idy )

        bg2.copy( bx, by )


    def dock ( self, control, window ):
        """ Docks the specified control.
        """
        kind = self.kind
        if kind < DOCK_NONE:
            the_control = control
            the_parent  = control.parent
            region      = self.region
            if (kind == DOCK_TAB) or (kind == DOCK_BAR):
                region.add( control, self.control )
                if isinstance( control, DockRegion ):
                    the_parent.remove( control )
                    the_parent = None
            elif kind == DOCK_TABADD:
                item = self.control
                if isinstance( item, DockControl ):
                    if isinstance( control, DockControl ):
                        control = DockRegion( contents = [ control ] )

                    i = region.contents.index( item )
                    region.contents[ i ] = item = DockSection(
                        contents = [ DockRegion( contents = [ item ] ),
                                     control ],
                        is_row   = True
                    )
                elif isinstance( item, DockSection ):
                    if (isinstance( control, DockSection ) and
                       (item.is_row == control.is_row)):
                        item.contents.extend( control.contents )
                    else:
                        if isinstance( control, DockControl ):
                            control = DockRegion( contents = [ control ] )
                        item.contents.append( control )
                else:
                    item.contents.append( control )

                region.active = region.contents.index( item )
            elif kind == DOCK_XCHG:
                index  = the_parent.contents.index( the_control )
                active = region.active
                the_parent.contents[ index ] = region.contents[ active ]
                region.contents[ active ]    = the_control
                the_parent                   = None
            elif region is not None:
                region.parent.add( control, region, kind )
            else:
                sizer   = window.owner.dock_sizer
                section = sizer.contents
                if ((section.is_row and
                        ((kind == DOCK_TOP) or (kind == DOCK_BOTTOM))) or
                    ((not section.is_row) and
                        ((kind == DOCK_LEFT) or (kind == DOCK_RIGHT)))):
                    if len( section.contents ) > 0:
                        section.dock_window = None
                        sizer.contents = section = DockSection(
                            is_row      = not section.is_row ).set(
                            contents    = [ section ],
                            dock_window = window.owner
                        )

                if len( section.contents ) > 0:
                    i = 0
                    if (kind == DOCK_RIGHT) or (kind == DOCK_BOTTOM):
                        i = -1

                    section.add( control, section.contents[ i ], kind )
                else:
                    section.is_row   = (not section.is_row)
                    section.contents = [ DockRegion( contents = [ control ] ) ]
                    section          = None

            if ((the_parent is not None) and
                (the_parent is not the_control.parent)):
                the_parent.remove( the_control )

            # Force the main window to be laid out and redrawn:
            window.owner.dock_sizer.needs_layout = True
            window.update()

            # Make sure the docked control is selected:
            the_control.select()

#-- EOF ------------------------------------------------------------------------