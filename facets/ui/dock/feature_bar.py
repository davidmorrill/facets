"""
Defines the FeatureBar class which displays and allows the user to
interact with a set of DockWindowFeatures for a specified DockControl.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, HasStrictFacets, Instance, Bool, Event, Color, \
           Int, Any, Control

from facets.ui.toolkit \
    import toolkit

from dock_control \
    import DockControl

from dock_constants \
    import FEATURE_EXTERNAL_DRAG

from ifeature_tool \
    import IFeatureTool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The feature bar window style:
feature_bar_style = set( [ 'simple' ] )

#-------------------------------------------------------------------------------
#  'FeatureBar' class:
#-------------------------------------------------------------------------------

class FeatureBar ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The (adapted) control/window which is the parent for the FeatureBar:
    parent = Instance( Control )

    # The DockControl whose features are being displayed:
    dock_control = Instance( DockControl )

    # The adapted control/window being used for the FeatureBar:
    control = Instance( Control )

    # Event posted when the user has completed using the FeatureBar:
    completed = Event

    # The background color for the FeatureBar:
    bg_color = Color( 0xDBEEF7, allow_none = True )

    # The border color for the FeatureBar:
    border_color = Color( 0X2583AF, allow_none = True )

    # Should the feature bar display horizontally (or vertically)?
    horizontal = Bool( True )

    # The current list of active features:
    features = Any

    #-- Public Methods ---------------------------------------------------------

    def hide ( self ):
        """ Hides the feature bar.
        """
        if self.control is not None:
            self.control.visible = False


    def show ( self ):
        """ Shows the feature bar.
        """
        # Make sure all prerequisites are met:
        dock_control, parent = self.dock_control, self.parent
        if (dock_control is None) or (parent is None):
            return

        # Create the actual control (if needed):
        control = self.control
        if control is None:
            self.control = control = toolkit().create_frame( parent,
                                                             feature_bar_style )

            # Set up all of the event handlers:
            control.set_event_handler(
                paint      = self.paint,
                left_down  = self.left_down,
                left_up    = self.left_up,
                right_down = self.right_down,
                right_up   = self.right_up,
                motion     = self.mouse_move,
                enter      = self.mouse_enter
            )

            # Set up to handle drag and drop events:
            control.drop_target = self

        # Calculate the best size and position for the feature bar:
        size          = ( 32, 32 )
        width         = height = 0
        horizontal    = self.horizontal
        self.features = [ feature
            for feature in dock_control.active_features
            if feature.is_enabled() and (feature.bitmap is not None)
        ]
        for feature in self.features:
            bitmap = feature.bitmap
            dx, dy = control.bitmap_size( bitmap )
            if horizontal:
                width += (dx + 3)
                height = max( height, dy )
            else:
                width   = max( width, dx )
                height += (dy + 3)

        if width > 0:
            if horizontal:
                width  += 5
                height += 8
            else:
                width  += 8
                height += 5

        px, py          = parent.screen_position
        fx, fy          = dock_control.feature_popup_position
        control.bounds  = ( px + fx, py + fy, width, height )
        control.visible = True

    #-- Control Event Handlers --------------------------------------------------

    def paint ( self, event ):
        """ Handles repainting the window.
        """
        window = self.control
        dx, dy = window.size
        g      = window.graphics

        # Draw the feature container:
        bg_color     = self.bg_color
        border_color = self.border_color
        if (bg_color is not None) or (border_color is not None):
            if border_color is None:
                g.pen = None
            else:
                g.pen = border_color

            if bg_color is None:
                g.brush = None
            else:
                g.brush = bg_color

            g.draw_rectangle( 0, 0, dx, dy )

        # Draw the feature icons:
        if self.horizontal:
            x = 4
            for feature in self.features:
                bitmap = feature.bitmap
                g.draw_bitmap( bitmap, x, 4 )
                x += (window.bitmap_size( bitmap )[0] + 3)
        else:
            y = 4
            for feature in self.features:
                bitmap = feature.bitmap
                g.draw_bitmap( bitmap, 4, y )
                y += (window.bitmap_size( bitmap )[1] + 3)


    def left_down ( self, event ):
        """ Handles the left mouse button being pressed.
        """
        self._feature  = self._feature_at( event )
        self._dragging = False
        self._xy       = ( event.x, event.y )


    def left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        self._dragging         = None
        feature, self._feature = self._feature, None
        if feature is not None:
            if feature is self._feature_at( event ):
                self.control.mouse_capture = False
                self.completed = True
                feature._set_event( event )
                feature.click()


    def right_down ( self, event ):
        """ Handles the right mouse button being pressed.
        """
        self._feature  = self._feature_at( event )
        self._dragging = False
        self._xy       = ( event.x, event.y )


    def right_up ( self, event ):
        """ Handles the right mouse button being released.
        """
        self._dragging         = None
        feature, self._feature = self._feature, None
        if feature is not None:
            if feature is self._feature_at( event ):
                self.control.mouse_capture = False
                self.completed = True
                feature._set_event( event )
                feature.right_click()


    def mouse_move ( self, event ):
        """ Handles the mouse moving over the window.
        """
        # Update tooltips if no mouse button is currently pressed:
        if self._dragging is None:
            feature = self._feature_at( event )
            if feature is not self._tooltip_feature:
                self._tooltip_feature = feature
                tooltip = ''
                if feature is not None:
                    tooltip = feature.tooltip

                self.control.tooltip = tooltip

            # Check to see if the mouse has left the window, and mark it
            # completed if it has:
            x, y   = event.x, event.y
            dx, dy = self.control.size
            if (x < 0) or (y < 0) or (x >= dx) or (y >= dy):
                self.control.mouse_capture = False
                self._tooltip_feature      = None
                self.completed             = True

            return

        # Check to see if we are in 'drag mode' yet:
        if not self._dragging:
            x, y = self._xy
            if (abs( x - event.x ) + abs( y - event.y )) < 3:
                return

            self._dragging = True

            # Check to see if user is trying to drag a 'feature':
            feature = self._feature
            if feature is not None:
                feature._set_event( event )

                prefix = button = ''
                if event.right_down:
                    button = 'right_'

                if event.control_down:
                    prefix = 'control_'
                elif event.alt_down:
                    prefix = 'alt_'
                elif event.shift_down:
                    prefix = 'shift_'

                object = getattr( feature, '%s%sdrag' % ( prefix, button ) )()
                if object is not None:
                    self.control.mouse_capture = False
                    self._feature              = None
                    self.completed             = True
                    self.dock_control.pre_drag_all( object )
                    self.control.drag( object, 'object' )
                    self.dock_control.post_drag_all()
                    self._dragging = None


    def mouse_enter ( self, event ):
        """ Handles the mouse entering the window.
        """
        self.control.mouse_capture = True

    #-- Drag and Drop Event Handlers: ------------------------------------------

    def drag_drop ( self, event ):
        """ Handles a Python object being dropped on the window.
        """
        # Determine what, if any, feature the object was dropped on:
        x, y, data = event.x, event.y, event.object
        feature    = self._can_drop_on_feature( x, y, data )

        # Indicate use of the feature bar is complete:
        self.completed = True

        # Reset any drag state information:
        self.dock_control.post_drag( FEATURE_EXTERNAL_DRAG )

        # Check to see if the data was dropped on a feature or not:
        if feature is not None:
            if isinstance( data, IFeatureTool ):
                # Handle an object implementing IFeatureTool being dropped:
                dock_control = feature.dock_control
                data.feature_dropped_on_dock_control( dock_control )
                data.feature_dropped_on( dock_control.object )
            else:
                # Handle a normal object being dropped:
                wx, wy = self.control.screen_position
                feature.set( x = wx + x, y = wy + y )
                feature.drop( data )

            event.result = event.request
        else:
            event.result = 'ignore'


    def drag_move ( self, event ):
        """ Handles a Python object being dragged over the control.
        """
        # Handle the case of dragging a normal object over a 'feature':
        if (event.has_object and
            (self._can_drop_on_feature( event.x, event.y, event.object )
             is not None)):
            event.result = event.request
        else:
            event.result = 'ignore'


    def drag_leave ( self, event ):
        """ Handles a dragged Python object leaving the window.
        """
        # Indicate use of the feature bar is complete:
        self.completed = True

        # Reset any drag state information:
        self.dock_control.post_drag( FEATURE_EXTERNAL_DRAG )

    #-- Private Methods --------------------------------------------------------

    def _can_drop_on_feature ( self, x, y, data ):
        """ Returns a feature that the pointer is over and which can accept the
            specified data.
        """
        feature = self._feature_at( FakeEvent( x = x, y = y ) )
        if (feature is not None) and feature.can_drop( data ):
            return feature

        return None


    def _feature_at ( self, event ):
        """ Returns the DockWindowFeature (if any) at a specified window
            position.
        """
        if self.horizontal:
            x = 4
            for feature in self.features:
                bdx, bdy = self.control.bitmap_size( feature.bitmap )
                if self._is_in( event, x, 4, bdx, bdy ):
                    return feature

                x += (bdx + 3)
        else:
            y = 4
            for feature in self.features:
                bdx, bdy = self.control.bitmap_size( feature.bitmap )
                if self._is_in( event, 4, y, bdx, bdy ):
                    return feature

                y += (bdy + 3)

        return None


    def _is_in ( self, event, x, y, dx, dy ):
        """ Returns whether or not an event is within a specified bounds.
        """
        return ((x <= event.x < (x + dx)) and (y <= event.y < (y + dy)))

#-------------------------------------------------------------------------------
#  'FakeEvent' class:
#-------------------------------------------------------------------------------

class FakeEvent ( HasStrictFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The 'fake' mouse event coordinates:
    x = Int
    y = Int

#-- EOF ------------------------------------------------------------------------