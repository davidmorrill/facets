"""
Defines the ViewItem class used by the VIP Shell to create an in-line Facets
view of an associated HasFacets object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Either, Range, View, Item, RangeEditor, toolkit, on_facet_set

from labeled_item \
    import LabeledItem

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The screen and scrollbar sizes:
screen_dx, screen_dy       = toolkit().screen_size()
scrollbar_dx, scrollbar_dy = toolkit().scrollbar_size()

#-------------------------------------------------------------------------------
#  'ViewItem'
#-------------------------------------------------------------------------------

class ViewItem ( LabeledItem ):
    """ Defines the ViewItem class used by the VIP Shell to create an in-line
        Facets view of an associated HasFacets object.
    """

    #-- Facet Definitions ------------------------------------------------------

    type = 'view'
    icon = '@facets:shell_view'

    # The Facets UI for the item's view:
    ui = Any # Instance( UI )

    # The object view to display:
    view = Any

    # The 'zoom' view height:
    height = Either( -1, Range( 60, screen_dy ), default = -1 )

    #-- Facet View Definitions -------------------------------------------------

    zoom_view = View(
        Item( 'height',
              editor = RangeEditor(
                  low = 60, high = screen_dy, increment = 1, body_style = 25
              )
        )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _ui_default ( self ):
        self.add_tool( self.shell.resizer )

        return self.item.edit_facets( parent = self.context.control,
                                      view   = self.view,
                                      kind   = 'editor' )

    #-- IStackItem Interface Methods -------------------------------------------

    def initialized ( self ):
        """ Called when the shell item has been fully initialized.
        """
        super( ViewItem, self ).initialized()

        # Set the correct item label, then force an update:
        item            = self.item
        self.item_label = getattr( item, 'name', item.__class__.__name__  )
        self.update     = True


    def key_z ( self, event ):
        """ Change the vertical height of a view item using a pop-up slider.

            The [[z]] key displays a pop-up slider bar that allows you to adjust
            the height of the view. Use the scroll wheel or drag the slider tip
            to adjust the view's height.

            When using the scroll wheel, you can press the [[Shift]] key to
            increase rate of change, or you can press the [[Ctrl]] key to
            decrease the rate of change.

            The dialog closes automatically when you move the mouse pointer away
            from the dialog.
        """
        if self.lod > 0:
            self.height = int( self.size[1] )
            self.popup_for( 'zoom_view' )


    def paint_item_for_0 ( self, g, bounds ):
        """ Paints the text and optional label in the specified graphics
            context *g* for level of detail 0.
        """
        self.ui.control.visible = False

        x, y, dx, dy = self.bounds
        self.current_theme.draw_graphics_text( g, self.gtext, x, y, dx, dy,
                                               bounds )


    def paint_item_for_1 ( self, g, bounds ):
        """ Paints the text and optional label in the specified graphics
            context *g* for level of detail 1.
        """
        if not self.hidden:
            self.ui.control.visible = True

        if self.ltext is not None:
            x, y, dx, dy = self.bounds
            self.current_theme.draw_graphics_label( g, self.ltext, x, y, dx, dy,
                                                    bounds )


    def paint_item_for_2 ( self, g, bounds ):
        """ Paints the text and optional label in the specified graphics
            context *g* for level of detail 2.
        """
        self.paint_item_for_1( g, bounds )


    def size_item_for_1 ( self, g ):
        """ Returns the current size of the item.
        """
        cdx, cdy         = self.ui.control.best_size
        ax, ay, adx, ady = self.current_theme.bounds( 0, 0, 0, 0 )
        sdx              = self.stack_width
        height           = self.height
        if height < 0:
            height = min( cdy, screen_dy / 4 ) - ady

        return ( min( sdx, cdx - adx ), height )


    def size_item_for_2 ( self, g ):
        """ Returns the current size of the item.
        """
        cdx, cdy         = self.ui.control.best_size
        ax, ay, adx, ady = self.current_theme.bounds( 0, 0, 0, 0 )
        height           = self.height
        if height < 0:
            height = max( cdy, screen_dy / 2 ) - ady

        return ( cdx - adx, height )

    #-- ShellItem Interface Methods --------------------------------------------

    def dispose ( self ):
        """ Disposes of the item when it is no longer needed.
        """
        self.ui.dispose()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'bounds, current_theme' )
    def _bounds_modified ( self ):
        """ Handles a change to a facet that affects the size of the view.
        """
        if (self.lod > 0) and (self.context is not None):
            bx, by, bdx, bdy = self.bounds
            cx, cy, cdx, cdy = self.current_theme.bounds( bx, by, bdx, bdy )
            sdx              = self.stack_width + cdx - bdx - scrollbar_dx
            control          = self.ui.control
            if self.lod == 1:
                cdx = sdx
            else:
                cdx = max( min( cdx, control.best_size[0] ), sdx )

            control.bounds = ( cx, cy, cdx, cdy )


    @on_facet_set( 'hidden, filter_hidden' )
    def _hidden_modified ( self ):
        """ Handles one of the 'hidden' facets being changed.
        """
        if self.lod > 0:
            self.ui.control.visible = not (self.hidden or self.filter_hidden)


    def _height_set ( self, height ):
        """ Handles the 'height' facet being changed.
        """
        self.size    = ( self.size[0], height )
        self.refresh = True

#-- EOF ------------------------------------------------------------------------
