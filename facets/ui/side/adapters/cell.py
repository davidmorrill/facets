"""
Defines the concrete Qt4 specific implementation of the Cell class for providing
GUI toolkit neutral grid cell support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide.QtGui \
    import QStyle

from facets.ui.adapters.cell \
    import Cell

from graphics \
    import QtGraphics

#-------------------------------------------------------------------------------
#  'QtCell' class:
#-------------------------------------------------------------------------------

class QtCell ( Cell ):

    #-- Public Methods ---------------------------------------------------------

    def init ( self, painter, option, grid_adapter, row, column, screen_row ):
        """ Fast initializer to allow a single cell adapter to be re-used.
        """
        self.graphics     = QtGraphics( painter )
        self.grid_adapter = grid_adapter
        self.row          = row
        self.column       = column
        self.screen_row   = screen_row
        self._option      = option
        self._state       = int( option.state )

    #-- Property Implementations -----------------------------------------------

    def _get_x ( self ):
        return self._option.rect.x()

    def _get_y ( self ):
        return self._option.rect.y()

    def _get_width ( self ):
        return self._option.rect.width()

    def _get_height ( self ):
        return self._option.rect.height()

    def _get_has_focus ( self ):
        return ((self._state & QStyle.State_HasFocus) != 0)

    def _get_enabled ( self ):
        return ((self._state & QStyle.State_Enabled) != 0)

    def _get_selected ( self ):
        return ((self._state & QStyle.State_Selected) != 0)

#-- EOF ------------------------------------------------------------------------