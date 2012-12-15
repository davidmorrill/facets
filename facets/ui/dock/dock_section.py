"""
Manages a region of a DockWindow containing non-overlapping items separated by
horizontal or vertical splitter bars. All items in the same section are
separated by the same style of splitter bar (horizontal or vertical).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Bool, List, Instance, Property, property_depends_on

from dock_constants \
    import DOCK_SPLITTER, DOCK_EXPORT, DOCK_LEFT, DOCK_RIGHT, DOCK_TOP, \
           DOCK_BOTTOM, FixedSplitterPadding

from dock_group \
    import DockGroup

from dock_region \
    import DockRegion

from dock_splitter \
    import DockSplitter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Reference to the DockInfo class:
DockInfo = None

#-------------------------------------------------------------------------------
#  'DockSection' class:
#-------------------------------------------------------------------------------

class DockSection ( DockGroup ):
    """ Manages a region of a DockWindow containing non-overlapping items
        separated by horizontal or vertical splitter bars. All items in the
        same section are separated by the same style of splitter bar
        (horizontal or vertical).
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is this a row (or a column)?
    is_row = Bool( True )

    # Bounds of any splitter bars associated with the region:
    splitters = List( DockSplitter )

    # The DockWindow that owns this section (set on top level section only):
    dock_window = Instance( 'facets.ui.dock.dock_window.DockWindow' )

    # Contents of the section have been modified property:
    modified = Property

    #-- HasFacets Interface ----------------------------------------------------

    def facets_init ( self ):
        global DockInfo

        if DockInfo is None:
            import dock_info

            DockInfo = dock_info.DockInfo

    #-- Property Overrides -----------------------------------------------------

    @property_depends_on( 'parent.owner, dock_window' )
    def _get_owner ( self ):
        if self.dock_window is not None:
            return self.dock_window

        if self.parent is None:
            return None

        return self.parent.owner

    #-- Public Methods ---------------------------------------------------------

    def calc_min ( self, use_size = False ):
        """ Calculates the minimum size of the section.
        """
        tdx      = tdy = 0
        contents = self.visible_contents
        n        = len( contents )

        if self.is_row:
            sdx = self.theme.vertical_splitter.image_slice.dx

            for item in contents:
                dx, dy = item.calc_min( use_size )
                tdx   += dx
                tdy    = max( tdy, dy )

            if self.resizable:
                tdx += ((n - 1) * sdx)
            else:
                tdx += ((n + 1) * FixedSplitterPadding)
                tdy += 2 * FixedSplitterPadding

        else:
            sdy = self.theme.horizontal_splitter.image_slice.dy

            for item in contents:
                dx, dy = item.calc_min( use_size )
                tdx    = max( tdx, dx )
                tdy   += dy

            if self.resizable:
                tdy += ((n - 1) * sdy)
            else:
                tdx += 2 * FixedSplitterPadding
                tdy += ((n + 1) * FixedSplitterPadding)

        if self.width < 0:
            self.width  = tdx
            self.height = tdy

        return ( tdx, tdy )


    def recalc_sizes ( self, x, y, dx, dy ):
        """ Layout the contents of the section based on the specified bounds.
        """
        self.width  = dx = max( 0, dx )
        self.height = dy = max( 0, dy )
        self.bounds = ( x, y, dx, dy )

        # If none of the contents are resizable, use the fixed layout method:
        if not self.resizable:
            self.recalc_sizes_fixed( x, y, dx, dy )

            return

        contents      = self.visible_contents
        splitters     = []
        cur_splitters = self.splitters
        nc            = len( cur_splitters )
        n             = len( contents ) - 1

        # Perform a horizontal layout:
        if self.is_row:
            sdx = self.theme.vertical_splitter.image_slice.dx
            dx -= (n * sdx)

            # Calculate the current logical width of all items:
            cdx = max( 1, reduce( lambda sum, item: sum + item.width, contents,
                                  0 ) )

            # Calculate each item's new size based on its current size and the
            # available size:
            remaining = dx
            for i, item in enumerate( contents ):
                if i < n:
                    idx = int( round( float( item.width * dx ) / cdx) )
                else:
                    idx = remaining

                item.recalc_sizes( x, y, idx, dy )
                remaining -= idx
                x         += idx

                # Define the splitter bar between adjacent items:
                if i < n:
                    if i < nc:
                        splitter = cur_splitters[i]
                    else:
                        splitter = DockSplitter( parent = self, index = i )

                    splitters.append(
                        splitter.set( bounds = ( x, y, sdx, dy ),
                                      style  = 'vertical' ) )

                x += sdx

        # Perform a vertical layout:
        else:
            sdy = self.theme.horizontal_splitter.image_slice.dy
            dy -= (n * sdy)

            # Calculate the current logical height of all items:
            cdy = max( 1, reduce( lambda sum, item: sum + item.height, contents,
                                  0 ) )

            # Allocate the change (plus or minus) proportionally based on each
            # item's current size:
            remaining = dy
            for i, item in enumerate( contents ):
                if i < n:
                    idy = int( round( float( item.height * dy ) / cdy) )
                else:
                    idy = remaining

                item.recalc_sizes( x, y, dx, idy )
                remaining -= idy
                y         += idy

                # Define the splitter bar between adjacent items:
                if i < n:
                    if i < nc:
                        splitter = cur_splitters[i]
                    else:
                        splitter = DockSplitter( parent = self, index = i )

                    splitters.append(
                        splitter.set( bounds = ( x, y, dx, sdy ),
                                      style  = 'horizontal' ) )

                y += sdy

        # Make sure the bounds of the 'hot spot' has been calculated for all of
        # the splitters:
        for splitter in splitters:
            splitter.set_hot_spot()

        # Save the new set of splitter bars:
        self.splitters = splitters

        # Set the visibility for all contained items:
        self._set_visibility()


    def recalc_sizes_fixed ( self, x, y, dx, dy ):
        """ Layout the contents of the section based on the specified bounds
            using the minimum requested size for each item.
        """
        self.splitters = []

        x += FixedSplitterPadding
        y += FixedSplitterPadding
        dx = max( 0, dx - 2 * FixedSplitterPadding )
        dy = max( 0, dy - 2 * FixedSplitterPadding )

        # Perform a horizontal layout:
        if self.is_row:
            # Allocate the space for each item based on its minimum size until
            # the space runs out:
            items = self.visible_contents
            last  = len( items ) - 1
            for i, item in enumerate( items ):
                idx = dx
                if i != last:
                    idx, idy = item.calc_min()
                idx = min( dx, idx )
                dx  = max( 0, dx - idx - FixedSplitterPadding )
                item.recalc_sizes( x, y, idx, dy )
                x += idx + FixedSplitterPadding

        # Perform a vertical layout:
        else:
            # Allocate the space for each item based on its minimum size until
            # the space runs out:
            items = self.visible_contents
            last  = len( items ) - 1
            for i, item in enumerate( items ):
                idy = dy
                if i != last:
                    idx, idy = item.calc_min()

                idy = min( dy, idy )
                dy  = max( 0, dy - idy - FixedSplitterPadding )
                item.recalc_sizes( x, y, dx, idy )
                y += idy + FixedSplitterPadding

        # Set the visibility for all contained items:
        self._set_visibility()


    def draw ( self, g ):
        """ Draws the contents of the section.
        """
        if self._visible is not False:
            contents = self.visible_contents

            for item in contents:
                item.draw( g )

            self.begin_draw( g )

            for item in self.splitters:
                item.draw( g )

            self.end_draw( g )


    def object_at ( self, x, y, force = False ):
        """ Returns the object at a specified window position.
        """
        if self._visible is not False:
            for item in self.splitters:
                if item.is_at( x, y ):
                    return item

            for item in self.visible_contents:
                object = item.object_at( x, y )
                if object is not None:
                    return object

        if force and self.is_at( x, y ):
            return self

        return None


    def dock_info_at ( self, x, y, tdx, is_control, force = False ):
        """ Gets the DockInfo object for a specified window position.
        """
        # Check to see if the point is in our drag bar:
        info = super( DockSection, self ).dock_info_at( x, y, tdx, is_control )
        if info is not None:
            return info

        if self._visible is False:
            return None

        for item in self.splitters:
            if item.is_at( x, y ):
                return DockInfo( kind = DOCK_SPLITTER )

        for item in self.visible_contents:
            object = item.dock_info_at( x, y, tdx, is_control )
            if object is not None:
                return object

        # Check to see if we must return a DockInfo object:
        if not force:
            return None

        # Otherwise, figure out which side or center region the point is closest
        # to and return a DockInfo object describing that region:
        lx, ty, dx, dy = self.bounds
        left   = lx - x
        right  = x - lx - dx + 1
        top    = ty - y
        bottom = y - ty - dy + 1

        # If the point is way outside of the section, mark it is a drag and
        # drop candidate:
        if max( left, right, top, bottom ) > 20:
            return DockInfo( kind = DOCK_EXPORT )

        left      = abs( left )
        right     = abs( right )
        top       = abs( top )
        bottom    = abs( bottom )
        mdx       = dx / 2
        mdy       = dy / 2
        in_left   = (left   <= mdx)
        in_right  = (right  <= mdx)
        in_top    = (top    <= mdy)
        in_bottom = (bottom <= mdy)

        if in_left:
            left *= mdy
            if (left <= (top * mdx)) and (left <= (bottom * mdx)):
                return DockInfo( kind   = DOCK_LEFT,
                                 bounds = ( lx, ty, mdx, dy ) )

        if in_right:
            right *= mdy
            if (right <= (top * mdx)) and (right <= (bottom * mdx)):
                return DockInfo( kind   = DOCK_RIGHT,
                                 bounds = ( lx + dx - mdx, ty, mdx, dy ) )

        if in_top:
            return DockInfo( kind   = DOCK_TOP,
                             bounds = ( lx, ty, dx, mdy ) )

        return DockInfo( kind   = DOCK_BOTTOM,
                         bounds = ( lx, ty + dy - mdy, dx, mdy ) )


    def add ( self, control, region, kind ):
        """ Adds a control to the section at the edge of the region specified.
        """
        contents   = self.contents
        new_region = control
        if not isinstance( new_region, DockRegion ):
            new_region = DockRegion( contents = [ control ] )

        i = contents.index( region )
        if self.is_row:
            if (kind == DOCK_TOP) or (kind == DOCK_BOTTOM):
                if kind == DOCK_TOP:
                    new_contents = [ new_region, region ]
                else:
                    new_contents = [ region, new_region ]

                contents[i] = DockSection( is_row   = False ).set(
                                           contents = new_contents )
            else:
                if new_region.parent is self:
                    contents.remove( new_region )
                    i = contents.index( region )

                if kind == DOCK_RIGHT:
                    i += 1

                contents.insert( i, new_region )
        else:
            if (kind == DOCK_LEFT) or (kind == DOCK_RIGHT):
                if kind == DOCK_LEFT:
                    new_contents = [ new_region, region ]
                else:
                    new_contents = [ region, new_region ]

                contents[i] = DockSection( is_row   = True ).set(
                                           contents = new_contents )
            else:
                if new_region.parent is self:
                    contents.remove( new_region )
                    i = contents.index( region )

                if kind == DOCK_BOTTOM:
                    i += 1

                contents.insert( i, new_region )


    def remove ( self, item ):
        """ Removes a specified region or section from the section.
        """
        contents = self.contents
        if isinstance( item, DockGroup ) and (len( item.contents ) == 1):
            contents[ contents.index( item ) ] = item.contents[0]
        else:
            contents.remove( item )

        if self.parent is not None:
            if len( contents ) <= 1:
                self.parent.remove( self )
        elif (len( contents ) == 0) and (self.dock_window is not None):
            self.dock_window.dock_window_empty()


    def set_visibility ( self, visible ):
        """ Sets the visibility of the group.
        """
        self._visible = visible
        for item in self.contents:
            item.set_visibility( visible )


    def get_structure ( self ):
        """ Returns a copy of the section 'structure', minus the actual content.
        """
        return self.clone_facets( [ 'is_row', 'width', 'height' ] ).set(
               contents  = [ item.get_structure() for item in self.contents  ],
               splitters = [ item.get_structure() for item in self.splitters ] )


    def get_splitter_bounds ( self, splitter ):
        """ Gets the maximum bounds that a splitter bar is allowed to be
            dragged.
        """
        x, y, dx, dy     = splitter.bounds
        i                = self.splitters.index( splitter )
        contents         = self.visible_contents
        item1            = contents[ i ]
        item2            = contents[ i + 1 ]
        bx, by, bdx, bdy = item2.bounds

        if self.is_row:
            x  = item1.bounds[0]
            dx = bx + bdx - x
        else:
            y  = item1.bounds[1]
            dy = by + bdy - y

        return ( x, y, dx, dy )


    def update_splitter ( self, splitter, window ):
        """ Updates the affected regions when a splitter bar is released.
        """
        x, y, dx, dy         = splitter.bounds
        i                    = splitter.index
        contents             = self.visible_contents
        item1                = contents[ i ]
        item2                = contents[ i + 1 ]
        ix1, iy1, idx1, idy1 = item1.bounds
        ix2, iy2, idx2, idy2 = item2.bounds

        window.frozen = True

        if self.is_row:
            item1.recalc_sizes( ix1, iy1, x - ix1, idy1 )
            item2.recalc_sizes( x + dx, iy2, ix2 + idx2 - x - dx, idy2 )
        else:
            item1.recalc_sizes( ix1, iy1, idx1, y - iy1 )
            item2.recalc_sizes( ix2, y + dy, idx2, iy2 + idy2 - y - dy )

        window.frozen = False

        if splitter.style == 'horizontal':
            dx = 0
        else:
            dy = 0

        window.refresh( ix1 - dx, iy1 - dy,
                        ix2 + idx2 - ix1 + 2 * dx, iy2 + idy2 - iy1 + 2 * dy )


    def dump ( self, indent = 0 ):
        """ Prints the contents of the section.
        """
        print '%sSection( %08X, is_row = %s, width = %d, height = %d )' % (
              ' ' * indent, id( self ), self.is_row, self.width, self.height )

        for item in self.contents:
            item.dump( indent + 3 )


    def _set_visibility ( self ):
        """ Sets the correct visibility for all contained items.
        """
        for item in self.contents:
            item.set_visibility( item.visible )

    #-- Facet Event Handlers ---------------------------------------------------

    def _contents_set ( self ):
        """ Handles the 'contents' facet being changed.
        """
        for item in self.contents:
            item.parent = self

        self.calc_min( True )
        self.modified = True


    def _contents_items_set ( self, event ):
        """ Handles the 'contents' facet being changed.
        """
        for item in event.added:
            item.parent = self

        self.calc_min( True )
        self.modified = True


    def _splitters_set ( self ):
        """ Handles the 'splitters' facet being changed.
        """
        for item in self.splitters:
            item.parent = self


    def _splitters_items_set ( self, event ):
        """ Handles the 'splitters' facet being changed.
        """
        for item in event.added:
            item.parent = self

    #-- Property Implementations -----------------------------------------------

    def _set_modified ( self, value ):
        self._resizable = None
        if self.parent is not None:
            self.parent.modified = True

#-- EOF ------------------------------------------------------------------------