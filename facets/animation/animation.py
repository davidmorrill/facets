"""
Defines the Animation class that provides an abstract base class for an object
that can be animated.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Range, Any, Instance

from facets.core.facet_base \
    import SequenceTypes

from base_animation \
    import BaseAnimation

from path \
    import APath, Path

from tweener \
    import ATweener, NoEasing

from clock \
    import Clock

#-------------------------------------------------------------------------------
#  'Animation' class:
#-------------------------------------------------------------------------------

class Animation ( BaseAnimation ):
    """ Defines the Animation class that provides an abstract base class for an
        object that can be animated.
    """

    # The time period over which to perform the animation (in seconds):
    time = Range( 0.0, None, 1.0 )

    # The path to follow during the animation (an iterable)
    path = APath

    # The tweener to use during the animation (an iterable)
    tweener = ATweener

    #-- Facets that must be implemented by each concrete subclass --------------

    # Each of the 'begin' and 'end' facets must have the same number of
    # elements, which can be either a single value or an iterable:

    # The beginning point for the animation:
    begin = Any

    # The end point for the animation:
    end = Any

    #-- Private Facets ---------------------------------------------------------

    # The clock object used to drive the animation:
    clock = Instance( Clock, () )

    #-- Default Value Methods --------------------------------------------------

    def _path_default ( self ):
        return Path()


    def _tweener_default ( self ):
        return NoEasing

    #-- Facet Event Handlers ---------------------------------------------------

    def _start_set ( self, start ):
        """ Handles starting the animation.
        """
        if not self.running:
            self._start     = self.clock.time
            self._end       = self._start + self.time
            self._iteration = 1
            self._reverse   = not start
            if self.time > 0.0:
                self.clock.on_facet_set( self._next_frame, 'time' )
                self.running = True

            self._next_frame( self._start )


    def _stop_set ( self ):
        """ Handles (manually) stopping the animation.
        """
        if self.running:
            self.clock.on_facet_set( self._next_frame, 'time', remove = True )
            self.running = False
            self.stopped = True

    #-- Private Methods --------------------------------------------------------

    def _next_frame ( self, now ):
        """ Handles performing the action at the next frame.
        """
        done = (now >= self._end)
        if done:
            t = 1.0
        else:
            t = (now - self._start) / (self._end - self._start)

        if self._reverse:
            t = 1.0 - t

        self.frame( self.path.at( self.begin, self.end, self.tweener( t ) ) )

        if done:
            if (self.repeat == 0) or (self._iteration < self.repeat):
                self._start      = now
                self._end        = self._start + self.time
                self._iteration += 1
                if self.reverse:
                    self._reverse = not self._reverse
            elif self.running:
                self.stop = True
            else:
                self.stopped = True

    #-- Subclassed Methods -----------------------------------------------------

    ###def frame ( self, *args ):
    def frame ( self, value ):
        """ Handles updating the animatable object with the current frame data
            specified by '*args'.
        """
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------
