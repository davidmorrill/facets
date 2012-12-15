"""
Defines the StackItemResizer class for adding a vertical resizer to a stack
item.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Bool, Int, Float, Any, Range, Color, implements

from facets.ui.i_stack_item \
    import IStackItemTool

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# The delay time (in milliseconds) before displaying a resizer handle:
ResizerDelay = Range( 0, 1000, 333 )

#-------------------------------------------------------------------------------
#  'StackItemResizer' class:
#-------------------------------------------------------------------------------

class StackItemResizer ( HasPrivateFacets ):
    """ The StackItemResizer class defines a horizontal/vertical resizer tool
        that can be used with  a StackEditor BaseStackItem or any of its
        subclasses.
    """

    implements( IStackItemTool )

    #-- Facet Definitions ------------------------------------------------------

    # Is this a vertical resizer?
    is_vertical = Bool( True )

    # The thickness of the resizer handle:
    thickness = Range( 3, 10, 5 )

    # The minimum size that resizer will allow:
    min_size = Int( 60 )

    # The colors of the resizer handle:
    color_top    = Color( 0xFFFFFF )
    color_middle = Color( 0xC0C0C0 )
    color_bottom = Color( 0x000000 )

    # The vertical trigger distance for initially activating the resizer handle:
    trigger_radius = Range( 1, 90, 50 )

    # The delay time (in milliseconds) before displaying the resizer handle:
    delay = ResizerDelay

    #-- Private Facets ---------------------------------------------------------

    # The base position at the time a drag resize starts:
    resize_xy = Any

    # The stack item the toolbar is currently associated with:
    item = Any

    # The current opacity being drawn with:
    opacity = Float

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
            (self.opacity > 0.05)):
            opacity, g.opacity = g.opacity, self.opacity
            x, y, dx, dy       = item.bounds
            if self.is_vertical:
                y2 = y + dy - 1
                y  = y2 - self.thickness + 1
                x2 = x + dx
                g.pen = self.color_top
                g.draw_line( x, y, x2, y )
                g.pen = self.color_bottom
                g.draw_line( x, y2, x2, y2 )
                g.pen = self.color_middle
                for y in xrange( y + 1, y2 ):
                    g.draw_line( x, y, x2, y )
            else:
                x2 = x + dx - 1
                x  = x2 - self.thickness + 1
                y2 = y + dy
                g.pen = self.color_top
                g.draw_line( x, y, x, y2 )
                g.pen = self.color_bottom
                g.draw_line( x2, y, x2, y2 )
                g.pen = self.color_middle
                for x in xrange( x + 1, x2 ):
                    g.draw_line( x, y, x, y2 )

            g.opacity = opacity


    def mouse_event ( self, item, event ):
        """ Handles the mouse event specified by *event* for the stack item
            specified by *item*. Returns True if the event was handled. Any
            other result means that the event has not been handled.
        """
        method = getattr( self, '_mouse_' + event.name, None )
        if method is not None:
            return method( item, event )

    #-- Facet Event Handlers ---------------------------------------------------

    def _item_set ( self, old, new ):
        """ Handles the current item the mouse is over being changed.
        """
        if old is not None:
            old.refresh = True

        if new is not None:
            new.refresh = True


    def _opacity_set ( self ):
        """ Handles the 'opacity' facet being changed.
        """
        self.item.refresh = True

    #-- Private Methods --------------------------------------------------------

    def _start_resizer ( self ):
        """ Enables resizer handle drawing after the initial delay time has
            expired.
        """
        xy, self.pending_xy = self.pending_xy, None
        if self.item is not None:
            self._process_xy( self.item, *xy )


    def _process_xy ( self, item, x, y ):
        """ Process the mouse moving to the point specified by (x,y).
        """
        ix, iy, idx, idy = item.bounds
        if self.is_vertical:
            bottom = iy + idy
            top    = bottom - self.thickness
            dy     = top - y
            if dy <= 0:
                dy = max( 0, y - bottom + 1 )

            opacity = 0.0
            if dy <= self.trigger_radius:
                opacity = max( 0.0, 1.0 - (float( dy ) / self.trigger_radius) )

            self.opacity = opacity

            if (ix <= x < (ix + idx)) and (top <= y < bottom):
                item.cursor = 'sizens'

                return True

        else:
            right = ix + idx
            left  = right - self.thickness
            dx    = right - x
            if dx <= 0:
                dx = max( 0, x - right + 1 )

            opacity = 0.0
            if dx <= self.trigger_radius:
                opacity = max( 0.0, 1.0 - (float( dx ) / self.trigger_radius) )

            self.opacity = opacity

            if (iy <= y < (iy + idy)) and (left <= x < right):
                item.cursor = 'sizeew'

                return True

        item.cursor = 'arrow'

    #-- Mouse Event Handlers ---------------------------------------------------

    def _mouse_enter ( self, item, event ):
        """ Handles the mouse entering an item.
        """
        self.item    = item
        self.opacity = 0.0
        delay        = self.delay
        if delay == 0:
            self.pending_xy = None
        else:
            self.pending_xy = ( event.x, event.y )
            if delay < 1000:
                do_after( delay, self._start_resizer )


    def _mouse_leave ( self, item, event ):
        """ Handles the mouse leaving an item.
        """
        if self.item is item:
            self.item = None


    def _mouse_motion ( self, item, event ):
        """ Handles the mouse moving.
        """
        self.item = item
        if self.resize_xy is not None:
            x, y, dx, dy = item.bounds
            if self.is_vertical:
                size = ( dx, max( self.min_size, self.resize_xy + event.y ) )
            else:
                size = ( max( self.min_size, self.resize_xy + event.x ), dy )

            if getattr( item, 'resize', None ) is None:
                item.size = size
            else:
                item.resize = size

            item.refresh = True

            return True

        xy = ( event.x, event.y )
        if self.pending_xy is None:
            return self._process_xy( item, *xy )

        self.pending_xy = xy


    def _mouse_left_down ( self, item, event ):
        """ Handles the left mouse button being pressed.
        """
        x, y, dx, dy = item.bounds
        if self.opacity >= 0.25:
            if self.is_vertical:
                if ((x <= event.x < (x + dx)) and
                    ((y + dy - self.thickness) <= event.y < (y + dy))):
                    self.resize_xy = item.size[1] - event.y
                    item.capture   = True

                    return True

            elif ((y <= event.y < (y + dy)) and
                 ((x + dx - self.thickness) <= event.x < (x + dx))):
                self.resize_xy = item.size[0] - event.x
                item.capture  = True

                return True


    def _mouse_left_up ( self, item, event ):
        """ Handles the left mouse button being released.
        """
        if self.resize_xy is not None:
            self.resize_xy = None
            item.capture   = False

            return True

#-- EOF ------------------------------------------------------------------------
