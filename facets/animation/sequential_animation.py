"""
Defines the SequentialAnimation class that manages multiple animations running
sequentially.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, on_facet_set

from i_animatable \
    import IAnimatable

from animation_items \
    import AnimationItems

#-------------------------------------------------------------------------------
#  'SequentialAnimation' class:
#-------------------------------------------------------------------------------

class SequentialAnimation ( AnimationItems ):
    """ Defines the SequentialAnimation class that manages multiple animations
        running sequentially.
    """

    #-- Private Facets ---------------------------------------------------------

    # Currently active (animating) item:
    _active = Instance( IAnimatable )

    #-- Facet Event Handlers ---------------------------------------------------

    def _start_set ( self, start ):
        """ Handles starting the animation.
        """
        if (self._active is None) and (len( self.items ) > 0):
            self._iteration    = 1
            self._reverse      = not start
            self._active       = self.items[0]
            self._active.start = start


    def _stop_set ( self ):
        """ Handles (manually) stopping the animation.
        """
        item = self._active
        if item is not None:
            self._active = None
            item.stop    = True


    @on_facet_set( 'items[]' )
    def _items_modified ( self, removed ):
        """ Handles items being added to or removed from the collection.
        """
        if self._active in removed:
            self.stop = True


    @on_facet_set( 'items:stopped' )
    def _item_stopped ( self, object, old, new ):
        """ Handles an item completing its animation.
        """
        if object is self._active:
            index = self.items.index( object )
            if index < (len( self.items ) - 1):
                self._active = self.items[ index + 1 ]
                self._active.start = not self._reverse
            elif (self.repeat == 0) or (self._iteration < self.repeat):
                self._iteration += 1
                if self.reverse:
                    self._reverse = not self._reverse
                self._active       = self.items[0]
                self._active.start = not self._reverse
            else:
                self._active = None
                self.stopped = True
        elif self._active is None:
            self.stopped = True

#-- EOF ------------------------------------------------------------------------
