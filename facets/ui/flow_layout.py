"""
Defines a GUI toolkit neutral layout manager that arranges control from left to
right, top to bottom, or from top to bottom, left to right.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core.api \
    import HasPrivateFacets, Any, Bool, List, implements

from facets.ui.pyface.timer.api \
    import do_later

from i_abstract_layout \
    import IAbstractLayout

#-------------------------------------------------------------------------------
#  'FlowLayout' class:
#-------------------------------------------------------------------------------

class FlowLayout ( HasPrivateFacets ):

    implements( IAbstractLayout )

    #-- Facet Definitions ------------------------------------------------------

    # The underlying GUI toolkit specific layout manager
    # (part of IAbstractLayout interface):
    layout = Any

    # Is the orientation of the flow layout vertical:
    is_vertical = Bool( False )

    # The items contained within the layout:
    items = List

    #-- Public Methods ---------------------------------------------------------

    def calculate_minimum ( self ):
        """ Calculates the minimum size needed by the sizer.
        """
        if self._needed_size is not None:
            return self._needed_size

        dx = dy = 0

        if self.is_vertical:
            for item in self.items:
                if not isinstance( item, int ):
                    dx = max( dx, item.best_size[0] )

            return ( dx, 0 )

        for item in self.items:
            if not isinstance( item, int ):
                dy = max( dy, item.best_size[1] )

        return ( 0, dy )


    def perform_layout ( self, x, y, dx, dy ):
        """ Layout the contents of the layout based on the layout's current size
            and position.
        """
        x0, y0    = x, y
        ex        = x + dx
        ey        = y + dy
        mdx = mdy = 0
        visible   = True
        cur_max   = 0

        if self.is_vertical:
            for item in self.items:
                idy       = item
                is_spacer = isinstance( idy, int )
                if not is_spacer:
                    idx, idy = item.best_size

                expand = True
                #expand = item.GetFlag() & wx.EXPAND
                if (y > y0) and ((y + idy) > ey):
                    y   = y0
                    x  += mdx
                    mdx = 0
                    if x >= ex:
                        visible = False

                if not is_spacer:
                    cur_max = max( idx, cur_max )
                    if expand:
                        idx = cur_max

                    item.bounds  = ( x, y, idx, idy )
                    item.visible = visible
                    y           += idy
                    mdx          = max( mdx, idx )
                elif y > y0:
                    y += idy
        else:
            for item in self.items:
                idx       = item
                is_spacer = isinstance( idx, int )
                if not is_spacer:
                    idx, idy = item.best_size

                expand = True
                #expand = item.GetFlag() & wx.EXPAND
                if (x > x0) and ((x + idx) > ex):
                    x   = x0
                    y  += mdy
                    mdy = 0
                    if y >= ey:
                        visible = False

                if not is_spacer:
                    cur_max = max( idy, cur_max )
                    if expand:
                        idy = cur_max

                    item.bounds  = ( x, y, idx, idy )
                    item.visible = visible
                    x           += idx
                    mdy          = max( mdy, idy )
                elif x > x0:
                    x += idx

        if (not visible) and (self._needed_size is None):
            max_dx = max_dy = 0
            if self.is_vertical:
                max_dx = max( dx, x + mdx - x0 )
            else:
                max_dy = max( dy, y + mdy - y0 )

            self._needed_size = ( max_dx, max_dy )

            if not self._frozen:
                self._do_parent( '_freeze' )

            do_later( self._do_parent, '_thaw' )
        else:
            self._needed_size = None


    def add ( self, item ):
        """ Adds an adapted item to the layout.
        """
        self.items.append( item )

    #-- Private Methods --------------------------------------------------------

    def _freeze ( self, control ):
        """ Prevents the specified control from doing any further screen
            updates.
        """
        control.frozen = self._frozen = True


    def _thaw ( self, control ):
        """ Lays out a specified control and then allows it to be updated again.
        """
        control.update()
        if self._frozen:
            control.frozen = self._frozen = False


    def _do_parent ( self, method ):
        """ Does a specified operation on the layout's parent control.
        """
        for item in self.items:
            #if item.IsWindow():
            if not isinstance( item, int ):
                getattr( self, method )( item.parent )

            return

#-- EOF ------------------------------------------------------------------------