"""
Defines a Cell base class that each GUI toolkit backend must provide a concrete
implementation of.

The Cell class adapts a GUI toolkit description of a grid cell to provide a set
of toolkit neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Int, Instance, Bool, Property

from graphics \
    import Graphics

#-------------------------------------------------------------------------------
#  'Cell' class:
#-------------------------------------------------------------------------------

class Cell ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The graphics object that should be used to draw within the cell:
    graphics = Instance( Graphics )

    # The GridAdapter for the grid this cell is part of:
    grid_adapter = Instance( 'facets.ui.grid_adapter.GridAdapter' )

    # Should the cell background be drawn by a custom cell paint handler?
    paint_background = Bool

    # The row of the cell within the grid:
    row = Int

    # The column of the cell within the grid:
    column = Int

    # The screen row of the cell within the grid:
    screen_row = Int

    # The leftmost edge of the cell:
    x = Property

    # The topmost edge of the cell:
    y = Property

    # The width of the cell:
    width = Property

    # The height of the cell:
    height = Property

    # Does the cell's control have focus?
    has_focus = Property

    # Is the cell's control enabled?
    enabled = Property

    # Is the cell selected?
    selected = Property

    # The text alignment of the cell:
    alignment = Property

    # The text value of the cell:
    text = Property

    # The raw content of the cell:
    content = Property

    # The amount of indenting of the cell:
    indent = Property

    # Cell theme:
    theme = Property

    # Cell Selected theme:
    selected_theme = Property

    # Cell state theme (takes into account the selected state of the cell:
    state_theme = Property

    # Cell text font:
    font = Property

    # Cell selected text font:
    selected_font = Property

    # Cell state font (takes into account the selected state of the cell):
    state_font = Property

    # Cell background color:
    bg_color = Property

    # Cell selected background color:
    selected_bg_color = Property

    # Cell state background color (takes into account the selection state of the
    # cell):
    state_bg_color = Property

    # Cell text color:
    text_color = Property

    # Cell selected text color:
    selected_text_color = Property

    # Cell state text color (takes into account the selection state of the
    # cell):
    state_text_color = Property

    # Cell image:
    image = Property

    # Cell selected image:
    selected_image = Property

    # Cell state image (takes into account the selection state of the cell):
    state_image = Property

    # The image alignment of the cell:
    image_alignment = Property

    # The custome paint handler for the cell:
    paint = Property

    #-- Property Implementations -----------------------------------------------

    def _get_x ( self ):
        raise NotImplementedError


    def _get_y ( self ):
        raise NotImplementedError


    def _get_width ( self ):
        raise NotImplementedError


    def _get_height ( self ):
        raise NotImplementedError


    def _get_has_focus ( self ):
        raise NotImplementedError


    def _get_enabled ( self ):
        raise NotImplementedError


    def _get_selected ( self ):
        raise NotImplementedError


    def _get_alignment ( self ):
        if self.row < 0:
            return self.grid_adapter.get_column_alignment( self.column )

        return self.grid_adapter.get_alignment( self.row, self.column )


    def _get_text ( self ):
        if self.row < 0:
            return self.grid_adapter.get_title( self.column )

        return self.grid_adapter.get_text( self.row, self.column )


    def _get_content ( self ):
        return self.grid_adapter.get_content( self.row, self.column )


    def _get_indent ( self ):
        if self.row < 0:
            return self.grid_adapter.get_column_indent( self.column )

        return self.grid_adapter.get_indent( self.row, self.column )


    def _get_theme ( self ):
        return self.grid_adapter.get_theme( self.row, self.column )


    def _get_selected_theme ( self ):
        return self.grid_adapter.get_selected_theme( self.row, self.column )


    def _get_state_theme ( self ):
        if self.row < 0:
            return self.grid_adapter.get_column_theme( self.column )

        if self.selected:
            return self.selected_theme

        return self.theme


    def _get_font ( self ):
        return self.grid_adapter.get_font( self.row, self.column )


    def _get_selected_font ( self ):
        return self.grid_adapter.get_selected_font( self.row, self.column )


    def _get_state_font ( self ):
        if self.row < 0:
            return self.grid_adapter.get_column_font( self.column )

        if self.selected:
            return self.selected_font

        return self.font


    def _get_bg_color ( self ):
        return self.grid_adapter.get_bg_color( self.row, self.column,
                                               self.screen_row )


    def _get_selected_bg_color ( self ):
        return self.grid_adapter.get_selected_bg_color( self.row, self.column )


    def _get_state_bg_color ( self ):
        if self.row < 0:
            return self.grid_adapter.get_column_bg_color( self.column )

        if self.selected:
            color = self.selected_bg_color
            if color is not None:
                return color

        return self.bg_color


    def _get_text_color ( self ):
        return self.grid_adapter.get_text_color( self.row, self.column,
                                                 self.screen_row )


    def _get_selected_text_color ( self ):
        return self.grid_adapter.get_selected_text_color( self.row,
                                                          self.column )


    def _get_state_text_color ( self ):
        if self.row < 0:
            return self.grid_adapter.get_column_text_color( self.column )

        if self.selected:
            color = self.selected_text_color
            if color is not None:
                return color

        return self.text_color


    def _get_image ( self ):
        return self.grid_adapter.get_image( self.row, self.column )


    def _get_selected_image ( self ):
        return self.grid_adapter.get_selected_image( self.row, self.column )


    def _get_state_image ( self ):
        if self.row < 0:
            return self.grid_adapter.get_column_image( self.column )

        if self.selected:
            return self.selected_image

        return self.image


    def _get_image_alignment ( self ):
        return self.grid_adapter.get_image_alignment( self.row, self.column )


    def _get_paint ( self ):
        if self.row < 0:
            return self.grid_adapter.get_column_paint( self.column )

        return self.grid_adapter.get_paint( self.row, self.column )

#-- EOF ------------------------------------------------------------------------