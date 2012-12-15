"""
Defines the concrete wxPython specific implementation of the Cell class for
providing GUI toolkit neutral grid cell support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.ui.adapters.cell \
    import Cell

from graphics \
    import WxGraphics

#-------------------------------------------------------------------------------
#  'WxCell' class:
#-------------------------------------------------------------------------------

class WxCell ( Cell ):

    #-- Public Methods ---------------------------------------------------------

    def init ( self, dc, rect, grid_adapter, row, column, screen_row,
                     selected, extra ):
        """ Fast initializer to allow a single cell adapter to be re-used.
        """
        self.graphics     = WxGraphics( dc )
        self.grid_adapter = grid_adapter
        self.row          = row
        self.column       = column
        self.screen_row   = screen_row
        self._rect        = rect
        self._selected    = selected
        self._extra       = extra

    #-- Property Implementations -----------------------------------------------

    def _get_x ( self ):
        return self._rect.x

    def _get_y ( self ):
        return self._rect.y

    def _get_width ( self ):
        return self._rect.width

    def _get_height ( self ):
        return self._rect.height

    def _get_has_focus ( self ):
        # fixme: Can we return a better answer than this?...
        return False

    def _get_enabled ( self ):
        # fixme: Can we return a better answer than this?...
        return False

    def _get_selected ( self ):
        return self._selected

    #-- Cell Method Overrides --------------------------------------------------

    def _get_text ( self ):
        if self.row < 0:
            result = self.grid_adapter.get_title( self.column )
            if not isinstance( self._extra, unicode ):
                return (result + self._extra)

            return (unicode( result, 'ascii' ) +
                    self._extra).encode( 'latin-1' )

        return self.grid_adapter.get_text( self.row, self.column )


    def _get_state_bg_color ( self ):
        return (super( WxCell, self )._get_state_bg_color() or wx.WHITE)

#-- EOF ------------------------------------------------------------------------
