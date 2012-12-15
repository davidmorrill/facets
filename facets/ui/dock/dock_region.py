"""
Manages a region of the DockWindow containing overlapping items displayed as a
set of notebook tabs.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Property, Int

from facets.ui.pyface.timer \
    import do_later

from dock_constants \
    import DOCK_TAB, DOCK_LEFT, DOCK_RIGHT, DOCK_TOP, DOCK_BOTTOM, DOCK_XCHG,  \
           SCROLL_LEFT, SCROLL_RIGHT, SCROLL_TO, TabActive, TabInactive, \
           NotActiveStates, NormalStates

from dock_control \
    import DockControl

from dock_group \
    import DockGroup

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Reference to the DockInfo class:
DockInfo = None

#-------------------------------------------------------------------------------
#  'DockRegion' class:
#-------------------------------------------------------------------------------

class DockRegion ( DockGroup ):
    """ Manages a region of the DockWindow containing overlapping items
        displayed as a set of notebook tabs.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Index of the currently active 'contents' DockControl:
    active = Int

    # Is the region drawn as a notebook or not:
    is_notebook = Property

    # Is the region drawn using a full width tab or not:
    is_full_width_tab = Property

    # Index of the tab scroll image to use (-1 = No tab scroll):
    tab_scroll_index = Int( -1 )

    # The index of the current leftmost visible tab:
    left_tab = Int

    # The current maximum value for 'left_tab':
    max_tab = Int

    # Contents have been modified property:
    modified = Property

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes global class constants.
        """
        global DockInfo

        if DockInfo is None:
            import dock_info

            DockInfo = dock_info.DockInfo


    def calc_min ( self, use_size = False ):
        """ Calculates the minimum size of the region.
        """
        if self.parent is None:
            return ( 0, 0 )

        tab_dx   = tdx = tdy = 0
        contents = self.visible_contents
        theme    = self.theme
        if self.is_notebook or self.is_full_width_tab:
            for item in contents:
                dx, dy  = item.calc_min( use_size )
                tdx     = max( tdx, dx )
                tdy     = max( tdy, dy )
                tab_dx += item.tab_width

            tis  = theme.tab.image_slice
            tc   = theme.tab.content
            tdx  = max( tdx, tab_dx ) + (tis.xleft + tis.xright +
                                         tc.left   + tc.right)
            tdy += (theme.tab_active.image_slice.dy +
                    tis.xtop + tis.xbottom + tc.top + tc.bottom)
        elif len( contents ) > 0:
            item     = contents[0]
            tdx, tdy = item.calc_min( use_size )
            if not item.locked:
                if item.style == 'horizontal':
                    tdy += theme.horizontal_drag.image_slice.dy
                elif item.style == 'vertical':
                    tdx += theme.vertical_drag.image_slice.dx

        if self.width < 0:
            self.width  = tdx
            self.height = tdy

        return ( tdx, tdy )


    def recalc_sizes ( self, x, y, dx, dy ):
        """ Layout the contents of the region based on the specified bounds.
        """
        self.width  = dx = max( 0, dx )
        self.height = dy = max( 0, dy )
        self.bounds = ( x, y, dx, dy )

        theme    = self.theme
        contents = self.visible_contents
        if self.is_notebook or self.is_full_width_tab:
            tab = theme.tab
            tis = tab.image_slice
            tc  = tab.content
            tl  = tab.label
            th  = theme.tab_active.image_slice.dy

            # Lay the region out as a notebook:
            x  += tis.xleft + tc.left
            tx0 = tx = x + tl.left
            dx -= (tis.xleft + tis.xright + tc.left + tc.right)
            tdx = dx - tl.left - tl.right
            ady = dy - th
            dy  = ady - tis.xtop - tis.xbottom - tc.top - tc.bottom
            iy  = y + tis.xtop + tc.top

            if theme.tabs_at_top:
                iy += th
            else:
                y += ady

            # Calculate the default tab clipping bounds:
            cdx = tdx + tc.left + tc.right
            self._tab_clip_bounds = ( tx0, y, cdx, th )

            self.tab_scroll_index = -1
            self.left_tab         = 0

            # Recalculate the size and drag bounds for each item:
            if self.is_full_width_tab:
                item = contents[0]
                item.recalc_sizes( x, iy, dx, dy )
                item.set_drag_bounds( tx, y, tdx, th )
            else:
                spacing = theme.tab_spacing
                rdx     = -spacing
                for item in contents:
                    item.recalc_sizes( x, iy, dx, dy )
                    rdx += (item.tab_width + spacing)

                extra = max( 0, cdx - rdx ) * theme.tabs_are_full_width
                n     = len( contents )
                for item in contents:
                    tdx       = item.tab_width
                    tab_extra = extra / n
                    item.set_drag_bounds( tx, y, tdx + tab_extra, th )
                    tx    += (tdx + spacing + tab_extra)
                    extra -= tab_extra
                    n     -= 1

                # Do we need to enable tab scrolling?
                xr = tx0 + cdx
                if (tx - spacing) > xr:
                    # Calculate the maximum tab index for scrolling:
                    self.max_tab = 1
                    n            = len( contents ) - 1
                    images       = self.theme.images
                    xr          -= images.scroll_left.width
                    for i in range( n, -1, -1 ):
                        xr -= contents[ i ].tab_width
                        if xr < tx0:
                            self.max_tab = min( i + 1, n )
                            break

                    # Set the new leftmost tab index:
                    self.left_tab = min( self.left_tab, self.max_tab )

                    # Determine which tab scroll image to use:
                    self.tab_scroll_index = ((self.left_tab < self.max_tab) +
                                             (2 * (self.left_tab > 0 ))) - 1

                    # Now adjust each tab's bounds accordingly:
                    if self.left_tab > 0:
                        adx = contents[ self.left_tab ].drag_bounds[0] - tx0
                        for item in contents:
                            dbx, dby, _, dbdy = item.drag_bounds
                            item.set_drag_bounds( dbx - adx, dby,
                                                  item.tab_width, dbdy )

                    # Exclude the scroll buttons from the tab clipping region:
                    self._tab_clip_bounds = (
                        tx0, y, cdx - images.scroll_left.width, th
                    )
        else:
            # Lay the region out as a drag bar:
            item        = contents[0]
            drag_bounds = ( 0, 0, 0, 0 )
            if not item.locked:
                if item.style == 'horizontal':
                    db_dy = theme.horizontal_drag.image_slice.dy
                    drag_bounds = ( x, y, dx, db_dy )
                    y  += db_dy
                    dy -= db_dy
                elif item.style == 'vertical':
                    db_dx = theme.vertical_drag.image_slice.dx
                    drag_bounds = ( x, y, db_dx, dy )
                    x  += db_dx
                    dx -= db_dx

            item.recalc_sizes( x, y, dx, dy )
            item.set_drag_bounds( *drag_bounds )

        # Make sure all of the contained controls have the right visiblity:
        self._set_visibility()


    def add ( self, control, before = None, after = None, activate = True ):
        """ Adds a new control before a specified control.
        """
        contents = self.contents
        if control.parent is self:
            contents.remove( control )

        if before is None:
            if after is None:
                i = len( contents )
            else:
                i = contents.index( after ) + 1
        else:
            i = contents.index( before )

        if isinstance( control, DockRegion ):
            contents[ i: i ] = control.contents
            control          = control.contents[0]
        else:
            contents.insert( i, control )

        if activate:
            self.active = i
            control.select()


    def remove ( self, item ):
        """ Removes a specified item.
        """
        contents = self.contents
        i        = contents.index( item )

        if isinstance( item, DockGroup ) and (len( item.contents ) == 1):
            item = item.contents[0]
            if isinstance( item, DockRegion ):
                contents[ i: i + 1 ] = item.contents[:]
            else:
                contents[i] = item
        else:
            del contents[ i ]
            if (self.active > i) or (self.active >= len( contents )):
                self.active -= 1

        if self.parent is not None:
            if len( contents ) == 0:
                self.parent.remove( self )
            elif ((len( contents ) == 1) and
                  isinstance( self.parent, DockRegion )):
                self.parent.remove( self )


    def get_structure ( self ):
        """ Returns a copy of the region 'structure', minus the actual content.
        """
        return self.clone_facets( [ 'active', 'width', 'height' ] ).set(
                 contents = [ item.get_structure() for item in self.contents ] )


    def toggle_lock ( self ):
        """ Toggles the 'lock' status of every control in the group.
        """
        super( DockRegion, self ).toggle_lock()

        self._is_notebook = self._is_full_width_tab = None


    def draw ( self, g ):
        """ Draws the contents of the region.
        """
        if self._visible is not False:
            self.begin_draw( g )

            if self.is_notebook:
                # fixme: There seems to be a case where 'draw' is called before
                # 'recalc_sizes' (which defines '_tab_clip_bounds'), so we need
                # to check to make sure it is defined. If not, it seems safe to
                # exit immediately, since in all known cases, the bounds are
                # ( 0, 0, 0, 0 ), so there is nothing to draw anyways. The
                # question is why 'recalc_sizes' is not being called first.
                if self._tab_clip_bounds is None:
                    return

                self._draw_notebook( g )
                active = self.active

                # Draw the scroll buttons (if necessary):
                x, y, dx, dy = self._tab_clip_bounds
                index = self.tab_scroll_index
                if index >= 0:
                    g.draw_bitmap( self.theme.images.scroll_images[ index ],
                                   x + dx, y + 2 )

                # Draw all the inactive tabs first:
                g.clipping_bounds = ( x, y, dx, dy )
                last_inactive     = -1
                for i, item in enumerate( self.contents ):
                    if (i != active) and item.visible:
                        last_inactive = i
                        if item.tab_state not in NotActiveStates:
                            item.tab_state = TabInactive

                        item.draw_tab( g )

                # Draw the active tab last:
                active_item           = self.contents[ active ]
                active_item.tab_state = TabActive
                active_item.draw_tab( g )

                # If the last inactive tab drawn is also the rightmost tab and
                # the theme has a 'tab right edge' image, draw the image just
                # to the right of the last tab:
                if last_inactive > active:
                    if item.tab_state == TabInactive:
                        bitmap = self.theme.tab_inactive_edge_bitmap
                    else:
                        bitmap = self.theme.tab_hover_edge_bitmap

                    if bitmap is not None:
                        x, y, dx, dy = item.drag_bounds
                        g.draw_bitmap( bitmap, x + dx, y )

            else:
                item = self.visible_contents[0]
                if self.is_full_width_tab:
                    self._draw_notebook( g )
                    if item.tab_state not in NotActiveStates:
                        item.tab_state = TabInactive

                    item.draw_tab( g )
                else:
                    if not item.locked:
                        getattr( item, 'draw_' + item.style )( g )

            self.end_draw( g )

            # Draw each of the items contained in the region:
            for item in self.contents:
                if item.visible:
                    item.draw( g )


    def object_at ( self, x, y ):
        """ Returns the object at a specified window position.
        """
        if (self._visible is not False) and self.is_at( x, y ):
            if self.is_notebook and (self.tab_scroll_index >= 0):
                cx, cy, cdx, _ = self._tab_clip_bounds
                images         = self.theme.images
                if self.is_at( x, y, ( cx + cdx, cy + 2,
                                       images.scroll_left.width,
                                       images.scroll_left.height ) ):
                    return self

            for item in self.visible_contents:
                if item.is_at( x, y, item.drag_bounds ):
                    return item

                object = item.object_at( x, y )
                if object is not None:
                    return object

        return None


    def dock_info_at ( self, x, y, tdx, is_control ):
        """ Gets the DockInfo object for a specified window position.
        """
        # Check to see if the point is in our drag bar:
        info = super( DockRegion, self ).dock_info_at( x, y, tdx, is_control )
        if info is not None:
            return info

        # If we are not visible, or the point is not contained in us, give up:
        if (self._visible is False) or (not self.is_at( x, y )):
            return None

        # Check to see if the point is in the drag bars of any controls:
        contents         = self.visible_contents
        ix, iy, idx, idy = contents[0].drag_bounds
        if iy <= y < (iy + idy):
            xl = 0
            for item in contents:
                ix, iy, idx, idy = item.drag_bounds
                if item._is_tab and (not is_control) and (xl <= x < ix):
                    return DockInfo(
                        kind    = DOCK_TAB,
                        bounds  = ( ix - (tdx / 2), iy, tdx, idy ),
                        region  = self,
                        control = item
                    )

                object = item.dock_info_at( x, y, tdx, is_control )
                if object is not None:
                    return object

                xl = ix + (idx / 2)

        # Check to see if the point is in the empty region outside of any tabs:
        lx, ty, dx, dy = self.bounds
        max_tabs       = self.owner.max_tabs
        if (max_tabs == 0) or (max_tabs > len( contents )):
            item             = contents[-1]
            ix, iy, idx, idy = item.drag_bounds
            if (x >= (ix + (idx / 2))) and (iy <= y < (iy + idy)):
                if self.theme.tabs_are_full_width:
                    idx = max( idx / 2, idx - tdx )

                return DockInfo( kind   = DOCK_TAB,
                                 bounds = ( ix + idx, iy, tdx, idy ),
                                 region = self )

        # Otherwise, figure out which side or center region the point is closest
        # to and return a DockInfo object describing that region:
        left      = x  - lx
        right     = lx + dx - 1 - x
        top       = y  - ty
        bottom    = ty + dy - 1 - y
        mdx       = dx / 3
        mdy       = dy / 3
        in_left   = (left  <= mdx)
        in_right  = (right <= mdx)
        in_top    = (top <= mdy)
        in_bottom = (bottom <= mdy)

        if in_left:
            left *= mdy
            if (left <= (top * mdx)) and (left <= (bottom * mdx)):
                return DockInfo( kind   = DOCK_LEFT,
                                 bounds = ( lx, ty, mdx, dy ),
                                 region = self )

        if in_right:
            right *= mdy
            if (right <= (top * mdx)) and (right <= (bottom * mdx)):
                return DockInfo( kind   = DOCK_RIGHT,
                                 bounds = ( lx + dx - mdx, ty, mdx, dy ),
                                 region = self )

        if in_top:
            return DockInfo( kind   = DOCK_TOP,
                             bounds = ( lx, ty, dx, mdy ),
                             region = self )

        if in_bottom:
            return DockInfo( kind   = DOCK_BOTTOM,
                             bounds = ( lx, ty + dy - mdy, dx, mdy ),
                             region = self )

        return DockInfo( kind   = DOCK_XCHG,
                         bounds = ( lx, ty, dx, dy ),
                         region = self )


    def tab_clicked ( self, control ):
        """ Handles a contained notebook tab being clicked.
        """
        # Find the page that was clicked and mark it as active:
        i = self.contents.index( control )
        if i != self.active:
            self.active = i

            self.refresh( control )

        # Fire the 'activated' event on the control:
        if isinstance( control, DockControl ):
            control.activated = True


    def refresh ( self, control ):
        """ Handles a contained *control* needing to be visually refreshed.
        """
        # Recalculate the tab layout:
        self.recalc_sizes( *self.bounds )

        # Force the notebook to be redrawn:
        control.control.parent.refresh( *self.bounds )


    def scroll ( self, type, left_tab = 0 ):
        """ Handles the user clicking an active scroll button.
        """
        if type == SCROLL_LEFT:
            left_tab = min( self.left_tab + 1, self.max_tab )
        elif type == SCROLL_RIGHT:
            left_tab = max( self.left_tab - 1, 0 )

        if left_tab != self.left_tab:

            # Calculate the amount we need to adjust each tab by:
            contents = self.visible_contents
            adx      = (contents[ left_tab ].drag_bounds[0] -
                        contents[ self.left_tab ].drag_bounds[0])

            # Set the new leftmost tab index:
            self.left_tab = left_tab

            # Determine which tab scroll image to use:
            self.tab_scroll_index = ((left_tab < self.max_tab) +
                                     (2 * (left_tab > 0))) - 1

            # Now adjust each tab's bounds accordingly:
            for item in contents:
                dbx, dby, dbdx, dbdy = item.drag_bounds
                item.set_drag_bounds( dbx - adx, dby, item.tab_width, dbdy )

            # Finally, force a redraw of the affected part of the window:
            x, y, dx, dy = self._tab_clip_bounds
            item.control.parent.refresh(
                x, y, dx + self.theme.images.scroll_left.width, dy
            )


    def mouse_down ( self, event ):
        """ Handles the left mouse button being pressed.
        """
        self._scroll = self._get_scroll_button( event )


    def mouse_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if ((self._scroll is not None) and
            (self._scroll == self._get_scroll_button( event ))):
            self.scroll( self._scroll )
        else:
            super( DockRegion, self ).mouse_up( event )


    def mouse_move ( self, event ):
        """ Handles the mouse moving while the left mouse button is pressed.
        """
        pass


    def set_visibility ( self, visible ):
        """ Sets the visibility of the region.
        """
        self._visible = visible
        active        = self.active
        for i, item in enumerate( self.contents ):
            item.set_visibility( visible and (i == active) )


    def activate ( self, control, layout = True ):
        """ Activates a specified control (i.e. makes it the current notebook
            tab).
        """
        if control.visible and self.is_notebook:
            active = self.contents.index( control )
            if active != self.active:
                self.active = active
                self.make_active_tab_visible()
                window = control.control.parent
                if layout:
                    do_later( window.update )
                else:
                    window.refresh( *self.bounds )


    def make_active_tab_visible ( self ):
        """ Makes sure the active control's tab is completely visible (if
            possible).
        """
        active = self.active
        if active < self.left_tab:
            self.scroll( SCROLL_TO, active )
        else:
            x, y, dx, dy = self.contents[ active ].drag_bounds
            if not self.is_at( x + dx - 1, y + dy - 1, self._tab_clip_bounds ):
                self.scroll( SCROLL_TO, min( active, self.max_tab ) )


    def show_hide ( self, control ):
        """ Handles a contained DockControl item being hidden or shown.
        """
        i = self.contents.index( control )
        if i == self.active:
            self._update_active()
        elif (self.active < 0) and control.visible:
            self.active = i

        self._is_notebook = self._is_full_width_tab = None


    def dump ( self, indent ):
        """ Prints the contents of the region.
        """
        print '%sRegion( %08X, active = %s, width = %d, height = %d )' % (
              ' ' * indent, id( self ), self.active, self.width, self.height )

        for item in self.contents:
            item.dump( indent + 3 )


    def _get_scroll_button ( self, event ):
        """ Returns which scroll button (if any) the pointer is currently over.
        """
        x, y, dx, dy = self._tab_clip_bounds
        images       = self.theme.images
        if self.is_in( event, x + dx, y + 2, images.scroll_left.width,
                                             images.scroll_left.height ):
            if (event.x - (x + dx)) < (images.scroll_left.width / 2):
                return SCROLL_LEFT

            return SCROLL_RIGHT

        return None


    def _update_active ( self, active = None ):
        """ Updates the currently active page after a change.
        """
        if active is None:
            active = self.active

        contents = self.contents
        for i in (range( active, len( contents )) +
                  range( active - 1, -1, -1 )):
            if contents[i].visible:
                self.active = i
                return

        self.active = -1

    #-- Facet Event Handlers ---------------------------------------------------

    def _active_set ( self, old, new ):
        self._set_visibility()

        # Set the correct tab state for each tab:
        for i, item in enumerate( self.contents ):
            item.tab_state = NormalStates[ i == new ]

        n = len( self.contents )
        if 0 <= old < n:
            # Notify the previously active dockable that the control's tab is
            # being deactivated:
            control = self.contents[ old ]
            if (isinstance( control, DockControl ) and
                (control.dockable is not None)):
                control.dockable.dockable_tab_activated( control, False )

        if 0 <= new < n:
            # Notify the new dockable that the control's tab is being
            # activated:
            control = self.contents[ new ]
            if (isinstance( control, DockControl ) and
                (control.dockable is not None)):
                control.dockable.dockable_tab_activated( control, True )


    def _contents_set ( self ):
        """ Handles the 'contents' facet being changed.
        """
        self._is_notebook = self._is_full_width_tab = None
        for item in self.contents:
            item.parent = self

        self.calc_min( True )
        self.modified = True


    def _contents_items_set ( self, event ):
        """ Handles the 'contents' facet being changed.
        """
        self._is_notebook = self._is_full_width_tab = None
        for item in event.added:
            item.parent = self

        self.calc_min( True )
        self.modified = True


    def _set_visibility ( self ):
        """ Set the proper visibility for all contained controls.
        """
        active = self.active
        for i, item in enumerate( self.contents ):
            item.set_visibility( i == active )


    def _set_modified ( self, value ):
        if self.parent is not None:
            self.parent.modified = True


    def _get_is_notebook ( self ):
        if self._is_notebook is None:
            contents = self.visible_contents
            n        = len( contents )
            self._is_notebook = (n > 1)
            if n == 1:
                self._is_notebook = ((contents[0].style == 'tab') and
                                     (not self.theme.tabs_are_full_width))

        return self._is_notebook


    def _get_is_full_width_tab ( self ):
        if self._is_full_width_tab is None:
            contents = self.visible_contents
            self._is_full_width_tab = (self.theme.tabs_are_full_width and
                                       (len( contents ) == 1)         and
                                       (contents[0].style == 'tab'))

        return self._is_full_width_tab


    def _draw_notebook ( self, g ):
        """ Draws the notebook body.
        """
        theme        = self.theme
        tab_height   = theme.tab_active.image_slice.dy
        x, y, dx, dy = self.bounds
        self.fill_bg_color( g, x, y, dx, dy )
        tb = theme.tab_background
        if theme.tabs_at_top:
            if tb is not None:
                tb.image_slice.fill( g, x, y, dx, min( tab_height, dy ) )

            theme.tab.image_slice.fill( g, x, y + tab_height, dx,
                                        max( 0, dy - tab_height ) )
        else:
            if tb is not None:
                tb.image_slice.fill( g, x, y + dy - tab_height,
                                        dx, min( tab_height, dy ) )

            theme.tab.image_slice.fill( g, x, y, dx, max( 0, dy - tab_height ) )

#-- EOF ------------------------------------------------------------------------