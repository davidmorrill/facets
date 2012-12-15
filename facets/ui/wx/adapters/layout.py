"""
Defines a wxPython specific concrete implementation of the Layout base class
that adapts a wxPython layout manager to provide a set of toolkit neutral
properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.ui.adapters.layout \
    import Layout

from facets.ui.adapters.control \
    import as_toolkit_control

from layout_item \
    import layout_item_adapter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from alignment values to corresponding wx flags:
align_map = {
    'top':     wx.ALIGN_TOP,
    'bottom':  wx.ALIGN_BOTTOM,
    'left':    wx.ALIGN_LEFT,
    'right':   wx.ALIGN_RIGHT,
    'hcenter': wx.ALIGN_CENTER,
    'vcenter': wx.ALIGN_CENTER_VERTICAL
}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def adapted_layout ( layout ):
    """ Returns a correctly adapted version of the specified layout mananger.
    """
    if layout is None:
        return None

    return layout_adapter( layout )


def layout_adapter ( layout, is_vertical = False ):
    """ Returns the layout adapter associated with the specified layout manager.
    """
    adapter = getattr( layout, 'adapter', None )
    if adapter is not None:
        return adapter

    return WxLayout( layout, is_vertical = is_vertical )

#-------------------------------------------------------------------------------
#  'WxLayout' class:
#-------------------------------------------------------------------------------

class WxLayout ( Layout ):
    """ Defines an wxPython specific concrete implementation of the Layout base
        class that adapts a wxPython layout manager to provide a set of toolkit
        neutral properties and methods.
    """

    #-- Concrete Methods -------------------------------------------------------

    def do_layout ( self ):
        """ Lays out the controls belonging to the layout manager.
        """
        self.layout.Layout()


    def clear ( self ):
        """ Clears the contents of the layout.
        """
        self.layout.Clear( True )


    def add ( self, item, left = 0, right = 0, top = 0, bottom = 0,
                          stretch = 0, fill = True, align = '' ):
        """ Adds a specified item to the layout manager with margins determined
            by the specified values for **left**, **right**, **top** and
            **bottom**.

            If **stretch** is 0, the item only receives as much space in the
            layout direction as it requires. If > 0, it receives an amount of
            space proportional to **stretch** when compared to the other items
            having a non-zero **stretch** value.

            If **fill** is False, the item only is the width or height it
            requests. If True, the item is expanded to fill the full width or
            height assigned to the layout manager.

            If **align** is one of the values: 'top', 'bottom', 'left',
            'right', 'hcenter' or 'vcenter', the item will be aligned
            accordingly; otherwise no special alignment is made. Note that a
            list of such values can also be specified.
        """
        pre = post = 0
        if self.is_vertical:
            flags, extra = self._add( left,   wx.LEFT,   0, 0 )
            flags, extra = self._add( right,  wx.RIGHT,  flags, extra )
            if top > 0:
                if top == extra:
                    flags |= wx.TOP
                else:
                    pre = top
            if bottom > 0:
                if bottom == extra:
                    flags |= wx.BOTTOM
                else:
                    post = bottom
        else:
            flags, extra = self._add( top,    wx.TOP,    0, 0 )
            flags, extra = self._add( bottom, wx.BOTTOM, flags, extra )
            if left > 0:
                if left == extra:
                    flags |= wx.LEFT
                else:
                    pre = left
            if right > 0:
                if right == extra:
                    flags |= wx.RIGHT
                else:
                    post = bottom

        if not isinstance( align, list ):
            flags |= align_map.get( align, 0 )
        else:
            for align_item in align:
                flags |= align_map.get( align_item, 0 )

        if fill:
            flags |= wx.EXPAND

        if not isinstance( item, tuple ):
            item = item()

        if pre > 0:
            self.layout.Add( ( pre, pre ) )

        self.layout.Add( item, stretch, flags, extra )

        if post > 0:
            self.layout.Add( ( post, post ) )


    def add_separator ( self, parent ):
        """ Adds a separator to the layout.
        """
        cols   = 1
        layout = self.layout
        if isinstance( layout, wx.GridSizer ):
            cols = layout.GetCols()

        if self.is_vertical:
            style = wx.LI_HORIZONTAL
            flags = wx.EXPAND | wx.TOP | wx.BOTTOM
        else:
            style = wx.LI_VERTICAL
            flags = wx.EXPAND | wx.LEFT | wx.RIGHT

        parent = as_toolkit_control( parent )

        for i in xrange( cols ):
            layout.Add( wx.StaticLine( parent, -1, style = style ),
                        0, flags, 2 )


    def remove ( self, item ):
        """ Removes the specified adapted item from the layout manager.
        """
        self.layout.Remove( item() )


    def set_stretchable_column ( self, column ):
        """ Marks the 'column'th column of a grid layout as 'stretchable'.
        """
        self.layout.AddGrowableCol( column )


    def set_stretchable_row ( self, row ):
        """ Marks the 'row'th row of a grid layout as 'stretchable'.
        """
        self.layout.AddGrowableRow( row )


    def create_generic_layout ( self, layout ):
        """ Returns a generic GUI toolkit specific layout manager that will
            delegate all of its toolkit specific layout methods to the
            corresponding methods in the IAbstractLayout interface implemented
            by the specified **layout** object.
        """
        return GenericLayout( layout )

    #-- Layout Property Implementations ----------------------------------------

    def _get_children ( self ):
        return [ layout_item_adapter( child )
                 for child in self.layout.GetChildren() ]


    def _get_size ( self ):
        dx, dy = self.layout.GetSize()

        return ( dx, dy )

    def _set_size ( self, dx_dy ):
        self.layout.SetMinSize( *dx_dy )


    def _get_bounds ( self ):
        x,  y  = self.layout.GetPosition()
        dx, dy = self.layout.GetPosition()

        return ( x, y, dx, dy )

    #-- Private Methods --------------------------------------------------------

    def _add ( self, value, bit, flags, extra ):
        """ Modifies the layout flags and extra values based on the specified
            size and bit flag.
        """
        if (value > 0) and (value >= extra):
            if value > extra:
                flags = 0
            flags |= bit
            extra  = value

        return ( flags, extra )

#-------------------------------------------------------------------------------
#  'GenericLayout' class:
#-------------------------------------------------------------------------------

class GenericLayout ( wx.PySizer ):
    """ An instance of GenericLayout is automatically created whenever a
        layout manager that implements IAbstractLayout is used. The
        GenericLayout instance routes all wx specific layout manager calls to
        the appropriate methods of the instance implementing IAbstractLayout.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, sizer ):
        self.sizer = sizer

        super( GenericLayout, self ).__init__()


    def CalcMin ( self ):
        """ Calculates the minimum size needed by the sizer.
        """
        return wx.Size( *self.sizer.calculate_minimum() )


    def RecalcSizes ( self ):
        """ Layout the contents of the sizer based on the sizer's current size
            and position.
        """
        x,   y = self.GetPositionTuple()
        dx, dy = self.GetSizeTuple()
        self.sizer.perform_layout( x, y, dx, dy )

#-- EOF ------------------------------------------------------------------------