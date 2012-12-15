"""
Defines the ConcurrentAnimation class that manages multiple animations running
concurrently.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Int, on_facet_set

from animation_items \
    import AnimationItems

#-------------------------------------------------------------------------------
#  'ConcurrentAnimation' class:
#-------------------------------------------------------------------------------

class ConcurrentAnimation ( AnimationItems ):
    """ Defines the ConcurrentAnimation class that manages multiple animations
        running concurrently.
    """

    #-- Private Facets ---------------------------------------------------------

    # Number of currently active (animating) items:
    _active = Int( 0 )

    #-- Facet Event Handlers ---------------------------------------------------

    def _start_set ( self, start ):
        """ Handles starting the animation.
        """
        if self._active == 0:
            self._active    = len( self.items )
            self._iteration = 1
            self._reverse   = not start
            for item in self.items:
                item.start = start


    def _stop_set ( self ):
        """ Handles (manually) stopping the animation.
        """
        if self._active > 0:
            self._iteration = 0
            for item in self.items:
                item.stop = True


    @on_facet_set( 'items[]' )
    def _items_modified ( self, removed, added ):
        """ Handles items being added to or removed from the collection.
        """
        if self._active > 0:
            for item in removed:
                item.stop = True

            self._active += len( added )
            for item in added:
                item.start = not self._reverse


    @on_facet_set( 'items:stopped' )
    def _item_stopped ( self ):
        """ Handles an item completing its animation.
        """
        self._active -= 1
        if self._active == 0:
            if ((self._iteration > 0) and
                ((self.repeat == 0) or (self._iteration < self.repeat))):
                self._active     = len( self.items )
                self._iteration += 1
                if self.reverse:
                    self._reverse = not self._reverse

                for item in self.items:
                    item.start = not self._reverse
            else:
                self.stopped = True

#-- EOF ------------------------------------------------------------------------
