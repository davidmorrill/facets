"""
Defines the StackItemToolbar class for creating toolbars for use with a
StackEditor BaseStackItem or any of its subclasses.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt

from facets.api \
    import HasPrivateFacets, Bool, List, Int, Float, Instance, Any, Tuple, \
           Range, Color, ATheme, Property, implements, property_depends_on, \
           on_facet_set

from facets.ui.i_stack_item \
    import IStackItemTool

from facets.ui.menu \
    import Action

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The 'sticky' threshold opacity:
ThresholdOpacity = 0.50

# The 'motor skills error' threshold for allowing the user to accidentally move
# the pointer outside of an 'active' toolbar without reseting the opacity level:
EdgeError = 5

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# The delay time (in milliseconds) before displaying a toolbar:
ToolbarDelay = Range( 0, 1000, 250 )

#-------------------------------------------------------------------------------
#  'StackItemToolbar' class:
#-------------------------------------------------------------------------------

class StackItemToolbar ( HasPrivateFacets ):
    """ The StackItemToolbar class defines a toolbar that can be used with
        a StackEditor BaseStackItem or any of its subclasses.
    """

    implements( IStackItemTool )

    #-- Facet Definitions ------------------------------------------------------

    # The list of toolbar actions:
    actions = List( Action )

    # The location of the toolbar relative to the item:
    location = Tuple( -4.0, 4.0 )

    # The color to use for the toolbar 'target':
    target_color = Color( 0x000000 )

    # The themes to use for the toolbar items:
    normal_theme = ATheme( '@xform:b?L30a15' )
    hover_theme  = ATheme( '@xform:b?H62L30S97' )
    click_theme  = ATheme( '@xform:b?H7L11S97' )

    # The opacity used for drawing in the 'triggered' state:
    trigger_opacity = Range( 0.0, 1.0, 0.3 )

    # The trigger radius for initially activating the toolbar:
    trigger_radius = Int( 250 )

    # The activation radius for fully activating the toolbar:
    active_radius = Int( 25 )

    # The delay time (in milliseconds) before displaying the toolbar:
    toolbar_delay = ToolbarDelay

    #-- Private Facets ---------------------------------------------------------

    # The size of the toolbar:
    size = Property

    # The Action item the mouse pointer is currently over (if any):
    action = Instance( Action )

    # Is the left mouse button currently pressed?
    mouse_down = Bool( False )

    # The stack item the toolbar is currently associated with:
    item = Any

    # The 'target' point for marking the toolbar activation location:
    target = Property

    # The current opacity being drawn with:
    opacity = Float

    # The current toolbar draw bounds:
    bounds = Tuple( Int, Int, Int, Int )

    # The most recently unprocessed mouse motion (x,y) coordinates:
    pending_xy = Any # None or Tuple( Int, Int )

    #-- IStackItemTool Interface Methods ---------------------------------------

    def paint ( self, item, g, bounds ):
        """ Paints the tool in the specified item using the specified graphics
            context. *Bounds* is a tuple of the form (x, y, dx, dy) specifying
            the visible bounds of the control, and can be used for optimizing
            graphics updates.
        """
        if ((self.pending_xy is None) and
            (item is self.item)       and
            (len( self.actions ) > 0)):
            opacity = g.opacity

            # Only draw the target when the toolbar is at low opacity settings
            # so that it does not interfere with the drawing of the toolbar:
            if self.opacity <= 0.05:
                g.opacity = self.trigger_opacity
                g.pen     = None
                g.brush   = self.target_color
                cx, cy    = self.target
                g.draw_circle( cx, cy, 3 )
            else:
                # Only draw the toolbar if the opacity is high enough (to
                # prevent drawing errors that seem to occur at very low opacity
                # levels):
                g.opacity = self.opacity
                self._draw_toolbar( item, g )

            g.opacity = opacity


    def mouse_event ( self, item, event ):
        """ Handles the mouse event specified by *event* for the stack item
            specified by *item*. Returns True if the event was handled. Any
            other result means that the event has not been handled.
        """
        method = getattr( self, '_mouse_' + event.name, None )
        if method is not None:
            return method( item, event )

    #-- Property Implementations -----------------------------------------------

    def _get_target ( self ):
        ldx, ldy     = self.location
        x, y, dx, dy = self.item.bounds
        if ldx < 0.0:
            x += (dx - 1)

        if abs( ldx ) < 1.0:
            ldx *= dx

        if ldy < 0.0:
            y += (dy - 1)

        if abs( ldy ) < 1.0:
            ldy *= dy

        return ( int( x + ldx ), int( y + ldy ) )


    @property_depends_on( 'actions[]' )
    def _get_size ( self ):
        dx = dy = 0
        for action in self.actions:
            dx += action.image.width
            dy  = max( dy, action.image.height )

        tdx, tdy = self.normal_theme.bounds()

        return ( dx + (len( self.actions ) * (tdx + 4)), dy + tdy + 4 )

    #-- Facet Event Handlers ---------------------------------------------------

    def _item_set ( self, old, new ):
        """ Handles the current item the mouse is over being changed.
        """
        if old is not None:
            old.refresh = True

        if new is not None:
            new.refresh = True


    @on_facet_set( 'opacity, mouse_down' )
    def _refresh_item ( self ):
        """ Handles the 'opacity' facet being changed.
        """
        self.item.refresh = True


    def _action_set ( self, action ):
        """ Handles the 'action' facet being changed.
        """
        self.item.refresh = True
        tooltip           = ''
        if action is not None:
            tooltip = action.tooltip

        self.item.context.control.tooltip = tooltip

    #-- Private Methods --------------------------------------------------------

    def _draw_toolbar ( self, item, g ):
        """ Draws the toolbar.
        """
        x, y, dx, dy = item.bounds
        tdx, tdy     = self.size
        tx, ty       = self.target

        # Determine the left, middle or right alignment point for the menu:
        cx = min( x + ((dx - tdx) / 2), x + dx - tdx )
        if abs( tx - x ) < abs( tx - x - dx + 1 ):
            if abs( tx - x ) < abs( tx - x - (dx / 2) ):
                cx = x
        elif abs( tx - x - dx + 1 ) < abs( tx - x - (dx / 2) ):
            cx = x + dx - tdx

        # Determine the top, middle or bottom alignment point for the menu:
        cy = min( y + ((dy - tdy) / 2), y + dy - tdy )
        if abs( ty - y ) < abs( ty - y - dy + 1 ):
            if abs( ty - y ) < abs( ty - y - (dy / 2) ):
                cy = y
        elif abs( ty - y - dy + 1 ) < abs( ty - y - (dy / 2) ):
            cy = y + dy - tdy

        # Save the location the menu will be drawn at (for use by the mouse
        # motion event handler):
        self.bounds = ( cx, cy, tdx, tdy )

        # Determine which menu actions are currently enabled:
        self._enabled_when()

        # Draw each of the menu actions in their correct enabled/disabled state:
        for action in self.actions:
            theme = self.normal_theme
            if action.enabled and (action is self.action):
                theme = self.hover_theme
                if self.mouse_down:
                    theme = self.click_theme

            image = action.image
            idx   = image.width + theme.bounds()[0] + 4
            theme.fill( g, cx, cy, idx, tdy )
            ax, ay, adx, ady = theme.bounds( cx, cy, idx, tdy )
            if not action.enabled:
                opacity    = g.opacity
                g.opacity *= 0.40
                g.draw_bitmap( image.bitmap, ax + 2,
                                             ay + (ady - image.height) / 2 )
                g.opacity = opacity
            else:
                g.draw_bitmap( image.bitmap, ax + 2,
                                             ay + (ady - image.height) / 2 )
            cx += idx


    def _action_at ( self, x, y ):
        """ Returns the Action at the location specified by *x* and *y*. Returns
            None if there is no toolbar action at the specified location.
        """
        bx, by, bdx, bdy = self.bounds
        if (bx <= x < (bx + bdx)) and (by <= y < (by + bdy)):
            tdx = self.normal_theme.bounds()[0] + 4
            for action in self.actions:
                adx = action.image.width + tdx
                if (bx <= x < (bx + adx)):
                    return action

                bx += adx

        return None


    def _enabled_when ( self ):
        """ Evaluate the current 'enabled' status of all toolbar actions.
        """
        context = None
        for action in self.actions:
            enabled_when = action.enabled_when
            if enabled_when != '':
                if context is None:
                    context     = { 'item': self.item }
                    environment = globals()

                action.enabled = bool(
                    eval( enabled_when, environment, context )
                )

    def _start_menu ( self ):
        """ Enables menu drawing after the menu delay time has expired.
        """
        xy, self.pending_xy = self.pending_xy, None
        if self.item is not None:
            self._process_xy( self.item, *xy )
            if self.action is None:
                self.item.refresh = True


    def _process_xy ( self, item, x, y ):
        """ Process the mouse moving to the point specified by (x,y).
        """
        action = None
        if len( self.actions ) > 0:
            ix, iy, idx, idy = item.bounds
            cx, cy           = self.target
            dx, dy           = x - cx, y - cy
            distance         = sqrt( (dx * dx) + (dy * dy) )
            opacity          = 0.0
            if distance <= self.trigger_radius:
                opacity = (1.0 - max( 0.0, distance - self.active_radius ) /
                               (self.trigger_radius - self.active_radius))

            bx, by, bdx, bdy = self.bounds
            if (((bx - EdgeError) <= x < (bx + bdx + EdgeError)) and
                ((by - EdgeError) <= y < (by + bdy + EdgeError)) and
                (self.opacity >= ThresholdOpacity)):
                opacity = max( opacity, self.opacity )

            self.opacity = opacity
            if opacity >= 0.05:
                action = self._action_at( x, y )

        self.action = action

    #-- Mouse Event Handlers ---------------------------------------------------

    def _mouse_enter ( self, item, event ):
        """ Handles the mouse entering an item.
        """
        self.item    = item
        self.opacity = 0.0
        delay        = self.toolbar_delay
        if delay == 0:
            self.pending_xy = None
        else:
            self.pending_xy = ( event.x, event.y )
            if delay < 1000:
                do_after( delay, self._start_menu )


    def _mouse_leave ( self, item, event ):
        """ Handles the mouse leaving an item.
        """
        if self.item is item:
            self.item = None


    def _mouse_motion ( self, item, event ):
        """ Handles the mouse moving.
        """
        xy = ( event.x, event.y )
        if self.pending_xy is None:
            self._process_xy( item, *xy )
        else:
            self.pending_xy = xy


    def _mouse_left_down ( self, item, event ):
        """ Handles the left mouse button being pressed.
        """
        if (self.action is not None) and (self.opacity >= 0.15):
            self.mouse_down = True

            return True


    def _mouse_left_up ( self, item, event ):
        """ Handles the left mouse button being released.
        """
        if self.mouse_down:
            self.mouse_down = False
            action = self.action
            if action is not None:
                if action.enabled:
                    method_name = action.action
                    if method_name.find( '.' ) >= 0:
                        if method_name.find( '(' ) < 0:
                            method_name += '()'

                        eval( method_name, globals(), { 'item': item } )
                    elif action.on_perform is not None:
                        action.on_perform( item )

                return True

#-- EOF ------------------------------------------------------------------------
