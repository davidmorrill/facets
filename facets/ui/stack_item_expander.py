"""
Defines the StackItemExpander class for adding an increase/decrease level of
detail tool to a stack item.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Float, Tuple, Any, Range, implements

from facets.ui.i_stack_item \
    import IStackItemTool

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The minimum width for which the expander tool is active:
MinWidth = 10

# The maximum opacity used to display the expander zone:
MaxOpacity = 0.125

#-------------------------------------------------------------------------------
#  'StackItemExpander' class:
#-------------------------------------------------------------------------------

class StackItemExpander ( HasPrivateFacets ):
    """ The StackItemExpander class defines an increase/decrease level of detail
        tool that can be used with  a StackEditor BaseStackItem or any of its
        subclasses.
    """

    implements( IStackItemTool )

    #-- Facet Definitions ------------------------------------------------------

    # The horizontal trigger distance for initially activating the expander
    # zone:
    trigger_radius = Range( 1, 200, 100 )

    # The delay time (in milliseconds) before displaying the expander zone:
    delay = Range( 0, 1000, 333 )

    # The left and right edges of the expander zone:
    zone = Tuple( ( 0, 60 ) )

    #-- Private Facets ---------------------------------------------------------

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
            (self.opacity > 0.01)):
            xl, xr = self.zone
            if (xr - xl) >= MinWidth:
                opacity, g.opacity = g.opacity, self.opacity
                x, y, dx, dy       = item.bounds
                g.pen = g.brush    = 0x000000
                g.draw_rectangle( x + xl, y, xr - xl, dy )
                g.opacity += 0.2
                g.draw_line( x + xl, y, x + xl, y + dy - 1 )
                g.draw_line( x + xr - 1, y, x + xr - 1, y + dy - 1 )
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

    def _start_expander ( self ):
        """ Enables expander zone drawing after the initial delay time has
            expired.
        """
        xy, self.pending_xy = self.pending_xy, None
        if self.item is not None:
            self._process_xy( self.item, *xy )


    def _process_xy ( self, item, x, y ):
        """ Process the mouse moving to the point specified by (x,y).
        """
        ix, iy, idx, idy = item.bounds
        left, right  = self.zone
        x           -= ix
        dx           = max( 0, left - x, x - right )
        self.opacity = max( 0.0, MaxOpacity *
                                 (1.0 - (float( dx ) / self.trigger_radius)) )
        in_zone      = (iy <= y < (iy + idy)) and (dx == 0)
        if in_zone:
            item.cursor  = 'sizens'
            item.tooltip = ('Use the mouse wheel to increase or decrease the '
                            'level of detail')
        else:
            item.cursor  = 'arrow'
            item.tooltip = ''

        return in_zone

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
                do_after( delay, self._start_expander )


    def _mouse_leave ( self, item, event ):
        """ Handles the mouse leaving an item.
        """
        if self.item is item:
            self.item = None


    def _mouse_motion ( self, item, event ):
        """ Handles the mouse moving.
        """
        self.item = item
        xy        = ( event.x, event.y )
        if self.pending_xy is None:
            return self._process_xy( item, *xy )

        self.pending_xy = xy


    def _mouse_wheel ( self, item, event ):
        """ Handles the mouse wheel being rotated.
        """
        if not event.shift_down:
            x, y, dx, dy = item.bounds
            if (self.opacity >= MaxOpacity) and (y <= event.y < (y + dy)):
                xl, xr = self.zone
                if (x + xl) <= event.x < (x + xr):
                    if event.wheel_change < 0:
                        if item.lod > 0:
                            item.lod -= 1
                    elif item.lod < item.maximum_lod:
                        item.lod += 1

                    return True

#-- EOF ------------------------------------------------------------------------
