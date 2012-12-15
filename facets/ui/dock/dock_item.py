"""
Defines the base class for all items contained in a DockWindow.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Any, Bool, Property, Int, Str, Bool, Instance, \
           Enum, List, Range, Undefined, cached_property, property_depends_on

from facets.ui.adapters.control \
    import Control

from facets.ui.pyface.timer.api \
    import do_later, do_after

from dock_window_theme_factory \
    import theme_factory

from dock_constants \
    import FEATURE_NONE, FEATURE_NORMAL, FEATURE_CHANGED, FEATURE_DROP,       \
           FEATURE_VISIBLE, FEATURE_DROP_VISIBLE, FEATURE_DISABLED,           \
           FEATURE_PRE_NORMAL, FEATURES_VISIBLE, NO_FEATURE_ICON,             \
           FEATURE_EXTERNAL_DRAG, NORMAL_FEATURES, DOCK_XCHG, DOCK_TAB,       \
           DOCK_TABADD, DOCK_BAR, DOCK_EXPORT, ENGRAVED_DARK, ENGRAVED_LIGHT, \
           MaxTabLength, TabActive, TabInactive, TabHover, Bounds, no_clip,   \
           no_dock_info


from ifeature_tool \
    import IFeatureTool

#-------------------------------------------------------------------------------
#  Module data:
#-------------------------------------------------------------------------------

# The standard height for DockWindow tab text:
text_dy = 0

#-------------------------------------------------------------------------------
#  'DockItem' class:
#-------------------------------------------------------------------------------

class DockItem ( HasPrivateFacets ):
    """ Base class for all items contained in a DockWindow.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The parent of this item:
    parent = Any

    # The DockWindow that owns this item:
    owner = Property

    # Bounds of the item:
    bounds = Bounds

    # Current width of the item:
    width = Int( -1 )

    # Current height of the item:
    height = Int( -1 )

    # Bounds of the item's drag bar or tab:
    drag_bounds = Bounds

    # Is this item selected?
    selected = Bool( False )

    # The current tab state:
    tab_state = Any

    # The tab displayable version of the control's UI name:
    tab_name = Property

    # Width of the item's tab:
    tab_width = Property

    # The DockWindowTheme for this item's DockWindow:
    theme = Property

    # The theme for the current tab state:
    tab_theme = Property

    # The current feature mode:
    feature_mode = Enum( FEATURE_NONE, FEATURE_NORMAL, FEATURE_CHANGED,
                         FEATURE_DROP, FEATURE_VISIBLE, FEATURE_DROP_VISIBLE,
                         FEATURE_DISABLED, FEATURE_PRE_NORMAL )

    # The position where the feature popup should appear:
    feature_popup_position = Property

    # The list of features for this item:
    features = List

    # The list of drag data compatible drop features for this item:
    drop_features = List

    # Current active set of features:
    active_features = Property

    # The maximum length of a name that can be displayed on a tab:
    max_tab_length = Range( 30, 256, MaxTabLength )

    # The name of this item (may be overridden in subclasses):
    name = Str

    # The control associated with this item (may be overridden in subclasses):
    control = Instance( Control )

    # Can the control be closed (may be overridden in subclasses)?
    closeable = Bool( False )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'parent.owner' )
    def _get_owner ( self ):
        if self.parent is None:
            return None

        return self.parent.owner


    def _get_tab_name ( self ):
        name = self.name
        mtl  = self.max_tab_length
        if len( name ) > mtl:
            trailing = (2 * mtl) / 3
            name     = '%s...%s' % ( name[ : mtl - trailing - 3 ],
                                     name[ -trailing: ] )

        return name


    @property_depends_on( 'control, tab_state, tab_name' )
    def _get_tab_width ( self ):
        if self.control is None:
            return 0

        self._is_tab = True

        # Calculate the size needed by the theme and margins:
        dw_theme = self.theme
        theme    = self.tab_theme
        tw       = (theme.image_slice.xleft + theme.image_slice.xright +
                    theme.content.left      + theme.content.right)

        if dw_theme.tabs_show_text:
            # Add feature marker width:
            if self.feature_mode != FEATURE_NONE:
                tw += (dw_theme.images.tab_feature_normal.width + 3)

            # Add text width:
            tw += (self.control.text_size( self.tab_name )[0] +
                   dw_theme.engraved_text)

            # Add custom image width:
            image = self.get_image()
            if image is not None:
                tw += (self.control.bitmap_size( image )[0] + 3)

            # Add the close button width:
            if self.closeable:
                tw += (dw_theme.images.close_tab.width + 6)

        # Return the computed width:
        return tw


    def _get_theme ( self ):
        if self.control is None:
            return theme_factory.theme

        return self.control.parent.owner.theme


    def _get_tab_theme ( self ):
        theme = self.theme
        if (self.style == 'horizontal') and (not self.parent.is_notebook):
            return theme.horizontal_drag

        if self.selected:
            return theme.tab_selected or theme.tab_active

        if self.tab_state == TabInactive:
            return theme.tab_inactive

        if self.tab_state == TabActive:
            return theme.tab_active

        return theme.tab_hover


    def _get_active_features ( self ):
        if len( self.drop_features ) > 0:
            return self.drop_features

        return self.features


    def _get_feature_popup_position ( self ):
        x, y, dx, dy = self.drag_bounds

        return ( x + 5, y + 3 )

    #-- Public Methods ---------------------------------------------------------

    def select ( self ):
        """ Select the item.
        """
        pass


    def is_at ( self, x, y, bounds = None ):
        """ Returns whether or not the item is at a specified window position.
        """
        if bounds is None:
            bounds = self.bounds

        bx, by, bdx, bdy = bounds

        return ((bx <= x < (bx + bdx)) and (by <= y < (by + bdy)))


    def is_in ( self, event, x, y, dx, dy ):
        """ Returns whether or not an event is within a specified bounds.
        """
        return ((x <= event.x < (x + dx)) and (y <= event.y < (y + dy)))


    def set_drag_bounds ( self, x, y, dx, dy ):
        """ Sets the control's drag bounds.
        """
        self.drag_bounds = ( x, y, dx, dy )


    def get_cursor ( self, event ):
        """ Gets the cursor to use when the mouse is over the item.
        """
        if self._is_tab and (not self._is_in_close( event )):
            return 'arrow'

        return 'hand'


    def dock_info_at ( self, x, y, tdx, is_control ):
        """ Gets the DockInfo object for a specified window position.
        """
        if self.is_at( x, y, self.drag_bounds ):
            max_tabs = self.owner.max_tabs
            if ((max_tabs == 0) or
                (max_tabs > len( self.parent.visible_contents ))):
                bx, by, bdx, bdy = self.drag_bounds
                control          = self
                if self._is_tab:
                    if is_control:
                        kind   = DOCK_TABADD
                        bounds = ( bx, by, bdx, bdy )
                    else:
                        if x >= (bx + (bdx / 2)):
                            return None

                        kind   = DOCK_TAB
                        bounds = ( bx - (tdx / 2), by, tdx, bdy )
                else:
                    if is_control:
                        kind   = DOCK_TABADD
                        bounds = ( bx, by, self.tab_width, bdy )
                    else:
                        kind    = DOCK_TAB
                        control = None
                        bounds  = ( bx + self.tab_width, by, tdx, bdy )

                from facets.ui.dock.dock_info import DockInfo

                return DockInfo(
                    kind    = kind,
                    bounds  = bounds,
                    region  = self.parent,
                    control = control
                )

        return None


    def features_of_type ( self, klass ):
        """ Returns all features for the item that are of the type specified
            by *klass*.
        """
        return [ feature for feature in self.features
                         if isinstance( feature, klass ) ]


    def begin_draw ( self, g, ox = 0, oy = 0 ):
        """ Prepares for drawing into a graphics object.
        """
        self._save_clip   = g.clipping_bounds
        x, y, dx, dy      = self.bounds
        g.clipping_bounds = ( x + ox, y + oy, dx, dy )


    def end_draw ( self, g ):
        """ Terminates drawing into a graphics object.
        """
        if self._save_clip != no_clip:
            g.clipping_bounds = self._save_clip
        else:
            g.clipping_bounds = None

        self._save_clip = None


    def mouse_down ( self, event ):
        """ Handles the left mouse button being pressed.
        """
        self._xy       = ( event.x, event.y )
        self._closing  = self._is_in_close( event )
        self._dragging = False


    def mouse_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        # Handle the user closing a control:
        if self._closing:
            if self._is_in_close( event ):
                self.close()

        # Handle the completion of a dragging operation:
        elif self._dragging:
            window = event.control
            dock_info, self._dock_info = self._dock_info, None
            self.mark_bounds( False )
            control = self

            # Check to see if the user is attempting to drag an entire notebook
            # region:
            if event.alt_down and control.parent.is_notebook:
                control = self.parent

                # Make sure the target is not contained within the notebook
                # group we are trying to move:
                region = dock_info.region
                while region is not None:
                    if region is control:
                        # If it is, the operation is invalid, abort:
                        return

                    region = region.parent

            # Check to see if the user is attempting to copy the control:
            elif event.control_down:
                owner   = window.owner
                control = owner.handler.dock_control_for(
                                *(owner.handler_args + ( window, control )) )

            # Complete the docking maneuver:
            dock_info.dock( control, window )

            # Restore the normal window cursor:
            window.owner.set_cursor( 'arrow' )

        # Handle the user clicking on a notebook tab to select it:
        elif self.is_at( event.x, event.y, self.drag_bounds ):
            # Mark the item as the currently selected item:
            self.select()

            # If it is also a notebook tab, notify it's containing region that
            # it has been clicked:
            if self._is_tab:
                self.parent.tab_clicked( self )


    def mouse_move ( self, event ):
        """ Handles the mouse moving while the left mouse button is pressed.
        """
        # Exit if control is 'fixed' or a 'close' is pending:
        if self._closing or self.locked or (self.style == 'fixed'):
            return

        window = event.control

        # Check to see if we are in 'drag mode' yet:
        if not self._dragging:
            x, y = self._xy
            if (abs( x - event.x ) + abs( y - event.y )) < 3:
                return

            self._dragging  = True
            self._dock_info = no_dock_info()
            self._dock_size = self.tab_width
            self.mark_bounds( True )
            self._dock_info.draw( window, self._drag_bitmap )

        # Get the window and DockInfo object associated with the event:
        cur_dock_info = self._dock_info
        if cur_dock_info is None:
            return

        self._dock_info = dock_info = window.owner.dock_sizer.dock_info_at(
            event.x, event.y, self._dock_size, event.shift_down
        )

        # Make sure the new DockInfo is legal:
        region = self.parent
        if ((not event.control_down)     and
            (dock_info.region is region) and
            ((len( region.contents ) <= 1) or
             (DOCK_XCHG == dock_info.kind) or
             ((DOCK_TAB <= dock_info.kind <= DOCK_BAR) and
              (dock_info.control is self)))):
            self._dock_info = dock_info = no_dock_info()

        # If the DockInfo has not changed, then no update is needed:
        if ((cur_dock_info.kind == dock_info.kind)     and
            (cur_dock_info.region is dock_info.region) and
            (cur_dock_info.bounds == dock_info.bounds)):
            return

        # Draw the new region:
        dock_info.draw( window, self._drag_bitmap )

        # If this is the start of an export (i.e. drag and drop) request:
        if ((dock_info.kind == DOCK_EXPORT) and
            (self.export != '')             and
            (self.dockable is not None)):

            # Begin the drag and drop operation:
            self.mark_bounds( False )
            window.owner.set_cursor( 'arrow' )
            window.owner.release_mouse()
            try:
                window._dragging = True
                if window.drag( self, 'object' ) == 'ignore':
                    window.owner.handler.open_view_for( self )
            finally:
                window._dragging = False
        else:
            # Update the mouse pointer as required:
            cursor = 'sizing'
            if dock_info.kind == DOCK_BAR:
                cursor = 'hand'

            window.owner.set_cursor( cursor )


    def hover_enter ( self ):
        """ Handles the mouse hovering over the item.
        """
        if self._is_tab:
            self._is_in_tab = True
            self._redraw_tab(
                ( None, TabHover )[ self.tab_state != TabActive ]
            )


    def hover_exit ( self ):
        """ Handles the mouse exiting from hovering over the item.
        """
        if self._is_tab:
            self._is_in_tab = False
            self._redraw_tab(
                ( None, TabInactive )[ self.tab_state != TabActive ]
            )


    def mark_bounds ( self, begin ):
        """ Marks/Unmarks the bounds of the bounding DockWindow.
        """
        window = self.control.parent
        if begin:
            # Create a snapshot of the DockWindow's current contents:
            g, x, y = window.screen_graphics
            dx, dy  = window.size
            g2      = g.graphics_buffer( dx, dy, alpha = True )
            self._drag_bitmap = g2.bitmap
            g2.blit( 0, 0, dx, dy, g, x, y )

            # Draw an overlay over the item being dragged to highlight it:
            g2.pen, g2.brush = None, ( 0, 0, 0, 20 )
            bx, by, bdx, bdy = self.bounds
            dx, dy, ddx, ddy = self.drag_bounds
            if (dy < by) or (dy > (by + bdy)):
                g2.draw_rectangle( bx, min( by, dy ), bdx, bdy + ddy )
            else:
                g2.draw_rectangle( dx, by, bdx + ddx, bdy )
        else:
            # Finished the DockWindow drag, release all resources:
            window.screen_graphics = self._drag_bitmap = None


    def fill_bg_color ( self, g, x, y, dx, dy ):
        """ Fills a specified region with the control's background color.
        """
        g.pen   = None
        g.brush = self.control.parent.background_color
        g.draw_rectangle( x, y, dx, dy )


    def draw_tab ( self, g ):
        """ Draws a notebook tab.
        """
        global text_dy

        x0, y0, dx, dy = self.drag_bounds
        if (dx <= 0) or (dy <= 0):
            # If size is bogus, we are being clipped out of existence, so exit:
            return

        self.tab_state = state = (self.tab_state or TabActive)
        self._is_tab   = True
        theme          = self.tab_theme
        slice          = theme.image_slice
        bg             = g.graphics_buffer( dx, dy )
        self.fill_bg_color( bg, 0, 0, dx, dy )
        slice.fill( bg, 0, 0, dx, dy )

        # Only draw the text and icons if requested:
        if self.theme.tabs_show_text:
            # Compute the initial drawing position:
            name         = self.tab_name
            tdx, text_dy = g.text_size( name )
            tc           = theme.content
            tl           = theme.label
            ox, oy       = tl.left, tl.top
            ady          = dy + slice.xtop + tc.top - slice.xbottom - tc.bottom
            y            = oy + ((ady - text_dy) / 2)
            x            = ox + slice.xleft + tc.left

            mode = self.feature_mode
            if mode == FEATURE_PRE_NORMAL:
                mode = self.set_feature_mode( False )

            # Draw the feature 'trigger' icon (if necessary):
            dw_theme = self.theme
            images   = dw_theme.images
            if mode != FEATURE_NONE:
                if mode not in FEATURES_VISIBLE:
                    if (mode in NORMAL_FEATURES) and (not self._is_in_tab):
                        bg.opacity = 0.25

                    bg.draw_bitmap( images.get_feature_image( mode ), x, y )
                    bg.opacity = 1.0

                x += (images.tab_feature_normal.width + 3)

            # Draw the image (if necessary):
            image = self.get_image()
            if image is not None:
                bg.draw_bitmap( image, x, y )
                # fixme: Is self.control defined here?
                x += (self.control.bitmap_size( image )[0] + 3)

            # Draw the text label:
            if dw_theme.engraved_text:
                bg.text_color = ENGRAVED_LIGHT
                bg.draw_text( name, x + 1, y + 2 )
                bg.text_color = ENGRAVED_DARK
            else:
                bg.text_color = theme.content_color

            bg.draw_text( name, x, y + 1 )

            # Draw the close button (if necessary):
            if self.closeable:
                close_tab = images.close_tab
                bg.draw_bitmap(
                    close_tab.bitmap,
                    dx + ox - slice.xright - tc.right - close_tab.width,
                    oy + ((ady - close_tab.height) / 2) + tl.bottom
                )

        # Copy the buffer to the display:
        bg.copy( x0, y0 )


    def draw_fixed ( self, dc ):
        """ Draws a fixed drag bar.
        """
        pass


    def draw_horizontal ( self, g ):
        """ Draws a horizontal drag bar.
        """
        self._is_tab = False
        x, y, dx, dy = self.drag_bounds
        self.theme.horizontal_drag.image_slice.fill( g, x, y, dx, dy )


    def draw_vertical ( self, g ):
        """ Draws a vertical drag bar.
        """
        self._is_tab = False
        x, y, dx, dy = self.drag_bounds
        self.theme.vertical_drag.image_slice.fill( g, x, y, dx, dy )


    def _redraw_tab ( self, state = None ):
        """ Redraws the control's tab.
        """
        if state is not None:
            self.tab_state = state

        region = self.parent
        if region is not None:
            if region.is_notebook:
                bounds = region._tab_clip_bounds
            else:
                bounds = self.drag_bounds

            self.control.parent.refresh( *bounds )


    def _redraw_bar ( self ):
        """ Redraws the control's drag bar.
        """
        g = self.control.temp_graphics
        getattr( self, 'draw_' + self.style )( g )


    def _redraw_control ( self ):
        """ Redraws the control's tab or bar.
        """
        if self._is_tab:
            self._redraw_tab()
        else:
            self._redraw_bar()


    def _close_bounds ( self ):
        """ Returns the bounds of the close button (if any).
        """
        global text_dy

        if self.closeable and self._is_tab:
            x, y, dx, dy = self.drag_bounds
            theme        = self.tab_theme
            slice        = theme.image_slice
            tc           = theme.content
            ox, oy       = theme.label.left, theme.label.top

            # fixme: x calculation seems to be off by -1...
            close_tab = self.theme.images.close_tab

            return ( x + dx + ox - slice.xright - tc.right - close_tab.width,
                     y + oy + ((dy + slice.xtop + tc.top - slice.xbottom -
                                tc.bottom - text_dy) / 2) + 3,
                     close_tab.width, close_tab.height )

        return ( 0, 0, 0, 0 )


    def _is_in_close ( self, event ):
        """ Returns whether a specified window position is over the close
            button.
        """
        return self.is_in( event, *self._close_bounds() )


    def set_feature_mode ( self, changed = True ):
        """ Sets/Returns the 'normal' feature mode for the control based on the
            number of currently active features.
        """
        if (not changed) or (self.feature_mode != FEATURE_PRE_NORMAL):
            mode = FEATURE_DROP

            features = self.drop_features
            if len( features ) == 0:
                mode     = FEATURE_NORMAL
                features = self.features

            for feature in features:
                if feature.bitmap is not None:
                    if changed:
                        self.feature_mode = FEATURE_CHANGED
                    else:
                        self.feature_mode = mode
                    break
            else:
                self.feature_mode = FEATURE_DISABLED

        return self.feature_mode


    def feature_activate ( self, event, drag_object = Undefined ):
        """ Returns whether or not a specified window position is over the
            feature 'trigger' icon, and if so, triggers display of the feature
            icons.
        """
        global text_dy

        if (self.feature_mode in NO_FEATURE_ICON) or (not self._is_tab):
            return False

        # In 'drag' mode, we may get the same coordinate over and over again.
        # We don't want to restart the timer, so exit now:
        exy = ( event.x, event.y )
        if self._feature_popup_xy == exy:
            return True

        x, y, dx, dy = self.drag_bounds
        images = self.theme.images
        idx    = images.tab_feature_normal.width
        idy    = images.tab_feature_normal.height
        theme  = self.tab_theme
        slice  = theme.image_slice
        tc     = theme.content
        ox, oy = theme.label.left, theme.label.top
        y     += (oy + ((dy + slice.xtop + tc.top - slice.xbottom - tc.bottom -
                         text_dy) / 2))
        x     += ox + slice.xleft + tc.left

        # If this is part of a drag operation, prepare for drag mode:
        if drag_object is not Undefined:
            self.pre_drag( drag_object, FEATURE_EXTERNAL_DRAG )

        # If the pointer is over the feature 'trigger' icon and the control
        # is feature enabled, then display the feature pop-up:
        if (self.is_in( event, x, y, idx, idy ) and
            (self.feature_mode not in NO_FEATURE_ICON)):
            self._feature_popup_xy = exy
            do_after( 100, self._feature_popup )

        return True


    def reset_feature_popup ( self ):
        """ Resets any pending feature popup.
        """
        self._feature_popup_xy = None
        self.post_drag( FEATURE_EXTERNAL_DRAG )


    def _feature_popup ( self ):
        """ Pops up the current features if a feature popup is still pending.
        """
        if self._feature_popup_xy is not None:
            # Set the new feature mode:
            if self.feature_mode == FEATURE_DROP:
                self.feature_mode = FEATURE_DROP_VISIBLE
            else:
                self.feature_mode = FEATURE_VISIBLE

            self.owner.feature_bar_popup( self )
            self._feature_popup_xy = None
        else:
            self.post_drag( FEATURE_EXTERNAL_DRAG )


    def feature_bar_closed ( self ):
        """ Finishes the processing of a feature popup.
        """
        if self.feature_mode == FEATURE_DROP_VISIBLE:
            self.feature_mode = FEATURE_DROP
        else:
            self.feature_mode = FEATURE_NORMAL

        do_later( self._redraw_control )


    def pre_drag_all ( self, object ):
        """ Prepare all DockControls in the associated DockWindow for being
            dragged over.
        """
        for control in self.dock_controls:
            control.pre_drag( object )

        self.pre_drag( object )


    def pre_drag ( self, object, tag = 0 ):
        """ Prepare this DockControl for being dragged over.
        """
        if (self.visible and
            (self.feature_mode != FEATURE_NONE) and
            (self._feature_mode is None)):

            if isinstance( object, IFeatureTool ):
                if (object.feature_can_drop_on( self.object ) or
                    object.feature_can_drop_on_dock_control( self )):
                    from feature_tool import FeatureTool

                    self.drop_features = [
                        FeatureTool( dock_control = self )
                    ]
            else:
                self.drop_features = [ f for f in self.features
                                         if f.can_drop( object ) and
                                            (f.bitmap is not None) ]

            self._feature_mode = self.feature_mode + tag

            if len( self.drop_features ) > 0:
                self.feature_mode = FEATURE_DROP
            else:
                self.feature_mode = FEATURE_DISABLED

            self._redraw_control()


    def post_drag_all ( self ):
        """ Restore all DockControls in the associated DockWindow after a drag
            operation is completed.
        """
        for control in self.dock_controls:
            control.post_drag()

        self.post_drag()


    def post_drag ( self, tag = 0 ):
        """ Restore this DockControl after a drag operation is completed.
        """
        if ((self._feature_mode is None) or (tag == 0) or
            ((self._feature_mode & tag) != 0)):
            self.drop_features = []
            if self.feature_mode != FEATURE_NONE:
                if self._feature_mode is not None:
                    self.feature_mode  = (self._feature_mode &
                                          (~FEATURE_EXTERNAL_DRAG))
                    self._feature_mode = None
                else:
                    self.set_feature_mode( False )

                self._redraw_control()

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self ):
        """ Handles the 'selected' facet being changed.
        """
        if self.parent is not None:
            self.parent.refresh( self )

#-- EOF ------------------------------------------------------------------------