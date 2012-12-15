"""
Defines a ControlFlasher tool for causing a connected Control object to flash
momentarilly.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Str, Button, List, Event, Range, Float, \
           Any, Control, on_facet_set, View, VGroup, HGroup, UItem,            \
           spring, toolkit

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'Flash' class
#-------------------------------------------------------------------------------

class Flash ( HasPrivateFacets ):
    """ Flashes a specified control momentarily.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The 'owner' of this object:
    owner = Instance( 'ControlFlasher' )

    # The control being flashed:
    control = Instance( Control )

    # The time (in seconds) to flash the control:
    time = Float

    # The timer object used to control the flashing:
    timer = Any

    #-- Private Methods --------------------------------------------------------

    def facets_init ( self ):
        super( Flash, self ).facets_init()

        control  = self.control
        gc, x, y = control.screen_graphics
        dx, dy   = control.client_size
        gc.pen   = None
        gc.brush = ( 255, 0, 0, 128 )
        gc.draw_rectangle( x, y, dx, dy )

        # Start the timer so we can restore the window later:
        self.timer = toolkit().create_timer( int( 1000 * self.time ),
                                             self._timer_pop )


    def _timer_pop ( self ):
        """ Handles the timer event popping.
        """
        # Restore the normal appearance of the control:
        self.control.screen_graphics = None

        # Notify the owner that we are done:
        self.owner.flashed = self

        # Cancel our timer later:
        do_later( self._terminate )


    def _terminate ( self ):
        """ Terminates the timer.
        """
        self.timer()

#-------------------------------------------------------------------------------
#  'ControlFlasher' class:
#-------------------------------------------------------------------------------

class ControlFlasher ( Tool ):
    """ Allows you to cause the currently selected control to 'flash'
        momentarily.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Control Flasher' )

    # The current selected control:
    control = Instance( Control, connect = 'to: a control' )

    # Length of time to flash a window:
    time = Range( 0.1, 5.0, 0.5 )

    # Button to make the current selected window flash:
    flash = Button( 'Flash' )

    # The list of currently active Flash objects:
    active = List( Flash )

    # Event fired when a Flash object has completed flashing:
    flashed = Event

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                UItem( 'flash' ),
                '_',
                Scrubber( 'time', 'Length of time to flash', width = 50 ),
                spring
            ),
            VGroup()
        )
    )

    #-- Facets Event Handlers --------------------------------------------------

    @on_facet_set( 'control, flash' )
    def _flash_control ( self ):
        """ Flashes the currently selected control.
        """
        if self.control is not None:
            self.active.append(
                Flash( owner = self, control = self.control, time = self.time )
            )


    def _flashed_set ( self, flash ):
        """ Handles the 'flashed' event being fired.
        """
        self.active.remove( flash )

#-- EOF ------------------------------------------------------------------------