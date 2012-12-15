"""
Defines the concrete wxPython specific implementation of the Control class for
providing GUI toolkit neutral control support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import wx
import drag

from facets.core_api \
    import Bool, cached_property

from facets.ui.adapters.control \
    import Control

from graphics \
    import WxGraphics, color_for, dc_for

from ui_event \
    import WxUIEvent

from drag \
    import RequestAction, ResultAction, WxDropTarget, python_data_object

from layout \
    import WxLayout, adapted_layout, layout_adapter

from facets.ui.wx.constants \
    import is_mac, is_win32, scrollbar_dx

# Define version dependent values:
wx_26 = (wx.__version__[:3] == '2.6')

#-------------------------------------------------------------------------------
#  Global data:
#-------------------------------------------------------------------------------

# Mapping of standard cursor names to wxPython cursor id's:
cursor_name_map = {
    'arrow':    wx.CURSOR_ARROW,
    'hand':     wx.CURSOR_HAND,
    'sizing':   wx.CURSOR_SIZING,
    'sizens':   wx.CURSOR_SIZENS,
    'sizeew':   wx.CURSOR_SIZEWE,
    'sizenwse': wx.CURSOR_SIZENWSE,
    'sizenesw': wx.CURSOR_SIZENESW,
    'question': wx.CURSOR_QUESTION_ARROW
}

# Dictionary of cursors in use:
cursor_map = {}

# Standard wx event handlers for use with the 'event_handler' method:
event_handlers = {
    'text_change':   ( wx.EVT_TEXT,          True  ),
    'text_enter':    ( wx.EVT_TEXT_ENTER,    True  ),
    'clicked':       ( wx.EVT_BUTTON,        True  ),
    'checked':       ( wx.EVT_CHECKBOX,      True  ),
    'choose':        ( wx.EVT_CHOICE,        True  ),
    'picked':        ( wx.EVT_COMBOBOX,      True  ),
    'dialed':        ( wx.EVT_RADIOBUTTON,   True  ),

    'paint':         ( wx.EVT_PAINT,         False ),
    'size':          ( wx.EVT_SIZE,          False ),
    'get_focus':     ( wx.EVT_SET_FOCUS,     False ),
    'lose_focus':    ( wx.EVT_KILL_FOCUS,    False ),
    'key_press':     ( wx.EVT_KEY_DOWN,      False ),
    'key':           ( wx.EVT_CHAR,          False ),
    'left_down':     ( wx.EVT_LEFT_DOWN,     False ),
    'middle_down':   ( wx.EVT_MIDDLE_DOWN,   False ),
    'right_down':    ( wx.EVT_RIGHT_DOWN,    False ),
    'left_up':       ( wx.EVT_LEFT_UP,       False ),
    'middle_up':     ( wx.EVT_MIDDLE_UP,     False ),
    'right_up':      ( wx.EVT_RIGHT_UP,      False ),
    'left_dclick':   ( wx.EVT_LEFT_DCLICK,   False ),
    'middle_dclick': ( wx.EVT_MIDDLE_DCLICK, False ),
    'right_dclick':  ( wx.EVT_RIGHT_DCLICK,  False ),
    'motion':        ( wx.EVT_MOTION,        False ),
    'enter':         ( wx.EVT_ENTER_WINDOW,  False ),
    'leave':         ( wx.EVT_LEAVE_WINDOW,  False ),
    'wheel':         ( wx.EVT_MOUSEWHEEL,    False ),
    'close':         ( wx.EVT_CLOSE,         False ),
    'activate':      ( wx.EVT_ACTIVATE,      False ),
}

# The list of mouse related events:
mouse_events = (
    'left_down', 'middle_down', 'right_down', 'left_up', 'middle_up',
    'right_up', 'left_dclick', 'middle_dclick', 'right_dclick', 'motion',
    'enter', 'leave', 'wheel'
)

# Mapping of wx control class names to methods of those classes which handle
# the getting and setting of the control's 'value':
value_method = {
    #'TextCtrl':   'Value',
    #'CheckBox':   'Value',
    'StaticText': 'Label',
    'Button':     'Label',
    'Frame':      'Title',
    'Dialog':     'Title'
}

# Set of drag and drop related events:
DragDropEvents = set(
    ( 'drag_enter', 'drag_leave', 'drag_move', 'drag_drop' )
)

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

# Standard font used by controls:
standard_font = None

def set_standard_font ( dc ):
    """ Sets the standard font to use for a specified device context.
    """
    global standard_font

    if standard_font is None:
        standard_font = wx.SystemSettings_GetFont( wx.SYS_DEFAULT_GUI_FONT )

    dc.SetFont( standard_font )

    return dc


def adapted_control ( control ):
    """ Returns a correctly adapted version of the specified control.
    """
    if control is None:
        return None

    return control_adapter( control )


def control_adapter ( control ):
    """ Returns the control adapter associated with a specified control.
    """
    adapter = getattr( control, 'adapter', None )
    if adapter is None:
        adapter = WxControl( control )

    return adapter

#-------------------------------------------------------------------------------
#  'WxControl' class:
#-------------------------------------------------------------------------------

class WxControl ( Control ):
    """ Defines the concrete wxPython specific implementation of the Control
        class for providing GUI toolkit neutral control support.
    """

    #-- Private Facets ---------------------------------------------------------

    # Is the mouse currently captured?
    is_mouse_captured = Bool( False )

    #-- Control Property Implementations ---------------------------------------

    def _get_position ( self ):
        return self.control.GetPositionTuple()

    def _set_position ( self, x_y ):
        self.control.SetPosition( x_y )


    def _get_size ( self ):
        return self.control.GetSizeTuple()

    def _set_size ( self, dx_dy ):
        self.control.SetSize( dx_dy )


    def _get_virtual_size ( self ):
        return self.control.GetVirtualSize()

    def _set_virtual_size ( self, dx_dy ):
        dx, dy   = dx_dy
        pdx, pdy = self.parent.size
        size     = ( max( dx, pdx - (scrollbar_dx * (dy > pdy)) ),
                     max( dy, pdy ) )
        self.control.SetSize( size )

        # The following line is a hack that seems to be necessary in order to
        # get wx to calculate whether or not it actually needs scroll bars:
        self.parent().SetVirtualSize( ( 0, 0 ) )

        # Now, set the correct size needed:
        self.parent().SetVirtualSize( size )


    def _get_bounds ( self ):
        control = self.control
        if control.IsTopLevel():
            # If this is a top-level window, return the bounds of the client
            # window, excluding any of the frame decorators:
            return (control.ClientToScreenXY( 0, 0 ) +
                    control.GetClientSizeTuple())

        return (control.GetPositionTuple() + control.GetSizeTuple())

    def _set_bounds ( self, x_y_dx_dy ):
        # Note: All we really want to do is the 'SetDimensions' call, but the
        # other code is needed for Linux/GTK which will not correctly process
        # the SetDimensions call if the min size is larger than the specified
        # size. So we temporarily set its min size to (0,0), do the
        # SetDimensions, then restore the original min size:
        control  = self.control
        min_size = control.GetMinSize()
        control.SetMinSize( wx.Size( 0, 0 ) )

        if control.IsTopLevel():
            # If this is a top-level window, assume we are given the bounds of a
            # client window excluding any frame decorators, and restore that
            # size and position, taking into account that wx does not have any
            # direct way to do this (which is why we may have to adjust the
            # original position after having set an initial 'guess'). All of
            # this is done so that the abstract API can always deal with client
            # window bounds, which allows for cross-toolkit saving and restoring
            # of window sizes and positions (albeit very awkwardly):
            x, y, dx, dy = x_y_dx_dy
            control.SetPosition( wx.Point( x, y ) )
            control.SetClientSizeWH( dx, dy )
            x1, y1 = control.ClientToScreenXY( 0, 0 )
            if (x != x1) or (y != y1):
                control.SetPosition( wx.Point( x - (x1 - x), y - (y1 - y) ) )
        else:
            control.SetDimensions( *x_y_dx_dy )

        control.SetMinSize( min_size )


    def _get_frame_bounds ( self ):
        raise NotImplementedError


    def _get_visible_bounds ( self ):
        parent     = self.control.GetParent()
        x, y       = parent.GetViewStart()
        ppux, ppuy = parent.GetScrollPixelsPerUnit()
        dx, dy     = parent.GetClientSizeTuple()

        return ( x * ppux, y * ppuy, dx, dy )


    def _get_client_size ( self ):
        # Note: We are using GetSizeTuple instead of GetClientSizeTuple for
        # consistency with the Qt version, which does not exclude scroll bars
        # from the client area:
        return self.control.GetSizeTuple()

    def _set_client_size ( self, dx_dy ):
        self.control.SetClientSize( dx_dy )


    def _get_best_size ( self ):
        if wx_26:
            return self.control.GetBestFittingSize()
        else:
            return self.control.GetEffectiveMinSize()


    def _get_min_size ( self ):
        return self.control.GetMinSize()

    def _set_min_size ( self, dx_dy ):
        self.control.SetMinSize( wx.Size( *dx_dy ) )


    def _get_screen_position ( self ):
        control  = self.control
        parent   = control.GetParent()
        position = control.GetPositionTuple()
        if parent is None:
            return position

        return parent.ClientToScreenXY( *position )


    def _get_mouse_position ( self ):
        return wx.GetMousePosition()


    def _get_visible ( self ):
        return self.control.IsShown()

    def _set_visible ( self, visible ):
        was_visible = self.control.IsShown()
        if self.modal:
            if visible:
                self.control.ShowModal()
            else:
                self.control.EndModal( self.result )
        else:
            self.control.Show( visible )

        if visible != was_visible:
            self.facet_property_set( 'visible', was_visible, visible )


    def _get_maximized ( self ):
        raise NotImplementedError

    def _set_maximized ( self, maximized ):
        raise NotImplementedError


    def _get_enabled ( self ):
        return self.control.IsEnabled()

    def _set_enabled ( self, enabled ):
        was_enabled = self.control.IsEnabled()
        if enabled != was_enabled:
            self.control.Enable( enabled )
            self.facet_property_set( 'enabled', was_enabled, enabled )


    def _get_checked ( self ):
        return self.control.IsChecked()

    def _set_checked ( self, checked ):
        was_checked = self.control.IsChecked()
        if checked != was_checked:
            self.control.SetValue( checked )
            self.facet_property_set( 'checked', was_checked, checked )


    def _get_drop_target ( self ):
        return self._drop_target

    def _set_drop_target ( self, drop_target ):
        self._drop_target = drop_target
        # fixme: Implement the rest of this...


    def _get_layout ( self ):
        return adapted_layout( self.control.GetSizer() )

    def _set_layout ( self, adapter ):
        if adapter is None:
            self.control.SetSizer( None )
        else:
            # If we received a toolkit specific layout manager, convert it to
            # an adapted one:
            if not isinstance( adapter, WxLayout ):
                adapter = layout_adapter( adapter )

            self.control.SetSizer( adapter.layout )


    def _get_parent_layout ( self ):
        return adapted_layout( self.control.GetContainingSizer() )


    @cached_property
    def _get_parent ( self ):
        return adapted_control( self.control.GetParent() )


    def _get_content ( self ):
        raise NotImplementedError

    def _set_content ( self, content ):
        layout = wx.BoxSizer( wx.VERTICAL )
        layout.Add( content(), 1, wx.EXPAND )
        self.control.SetSizer( layout )


    @cached_property
    def _get_root_parent ( self ):
        parent = self.control
        while parent is not None:
            control = parent
            parent  = control.GetParent()

        return adapted_control( control )


    def _get_children ( self ):
        return [ control_adapter( child )
                 for child in self.control.GetChildren() ]


    def _get_value ( self ):
        control = self.control
        return getattr( control,
            'Get' + value_method.get( control.__class__.__name__, 'Value' ) )()

    def _set_value ( self, value ):
        control = self.control
        getattr( control, 'Set' + value_method.get( control.__class__.__name__,
                                                    'Value' ) )( value )


    def _get_count ( self ):
        return getattr( self, '_get_count_for_' +
                              self.control.__class__.__name__ )()

    def _get_count_for_Notebook ( self ):
        return self.control.GetPageCount()


    def _get_selection ( self ):
        return getattr( self, '_get_selection_for_' +
                              self.control.__class__.__name__ )()

    def _get_selection_for_TextCtrl ( self ):
        return self.control.GetSelection()

    def _set_selection ( self, selection ):
        getattr( self, '_set_selection_for_' +
                       self.control.__class__.__name__ )( selection )

    def _set_selection_for_TextCtrl ( self, selection ):
        self.control.SetSelection( *selection )

    def _set_selection_for_Choice ( self, selection ):
        if isinstance( selection, int ):
            self.control.SetSelection( selection )
        elif isinstance( selection, basestring ):
            self.control.SetStringSelection( selection )
        else:
            self.control.SetMark( *selection )

    def _set_selection_for_ComboBox ( self, selection ):
        self._set_selection_for_Choice( selection )


    def _get_font ( self ):
        return self.control.GetFont()

    def _set_font ( self, font ):
        self.control.SetFont( font )


    def _get_graphics ( self ):
        return WxGraphics(
            dc_for( set_standard_font( wx.PaintDC( self.control ) ) )
        )


    def _get_graphics_buffer ( self ):
        g      = self.graphics.graphics_buffer()
        parent = self.parent
        slice  = parent.image_slice
        if slice is not None:
            x, y   = self.position
            dx, dy = parent.size
            slice.fill( g, -x, -y, dx, dy )
        else:
            # Otherwise, just paint the normal window background color:
            dx, dy  = self.size
            g.brush = parent.background_color
            color   = g.pen
            g.pen   = None
            g.draw_rectangle( 0, 0, dx, dy )
            g.pen   = color

        return g


    def _get_temp_graphics ( self ):
        return WxGraphics(
            dc_for( set_standard_font( wx.ClientDC( self.control ) ) )
        )


    def _get_screen_graphics ( self ):
        control = self.control

        if is_mac:
            dc     = dc_for( wx.ClientDC( control ) )
            x, y   = control.GetPositionTuple()
            dx, dy = control.GetSizeTuple()
            while True:
                control = control.GetParent()
                if control is None:
                    break

                xw, yw   = control.GetPositionTuple()
                dxw, dyw = control.GetSizeTuple()
                dx, dy   = min( dx, dxw - x ), min( dy, dyw - y )
                x += xw
                y += yw

            dc.SetClippingRegion( 0, 0, dx, dy )

            return ( WxGraphics( dc ), 0, 0 )

        x, y = control.ClientToScreenXY( 0, 0 )

        return ( WxGraphics( dc_for( wx.ScreenDC() ) ), x, y )

    def _set_screen_graphics ( self, value ):
        if is_mac:
            self.top_parent.refresh()
        else:
            self.control.Refresh()


    def _get_image ( self ):
        raise NotImplementedError


    def _get_tooltip ( self, tooltip ):
        tooltip = self.control.GetTooltip()
        if tooltip is None:
            return ''

        return str( tooltip.GetTip() )

    def _set_tooltip ( self, tooltip ):
         wx.ToolTip.Enable( False )
         wx.ToolTip.Enable( True )
         self.control.SetToolTip( wx.ToolTip( tooltip ) )


    def _get_mouse_capture ( self ):
        return self.is_mouse_captured

    def _set_mouse_capture ( self, is_captured ):
        if is_captured:
            if not self.is_mouse_captured:
                self.control.CaptureMouse()
        elif self.is_mouse_captured:
            self.control.ReleaseMouse()

        self.is_mouse_captured = is_captured


    def _get_foreground_color ( self ):
        return self.control.GetForegroundColour()

    def _set_foreground_color ( self, color ):
        self.control.SetForegroundColour( color_for( color ) or wx.NullColour )


    def _get_background_color ( self ):
        return self.control.GetBackgroundColour()

    def _set_background_color ( self, color ):
        self.control.SetBackgroundColour( color_for( color ) or wx.NullColour )


    def _set_cursor ( self, cursor ):
        global cursor_map, cursor_name_map

        if cursor not in cursor_map:
            cursor_map[ cursor ] = wx.StockCursor(
                cursor_name_map.get( cursor, wx.CURSOR_ARROW )
            )

        self.control.SetCursor( cursor_map[ cursor ] )


    def _set_icon ( self, icon ):
        self.control.SetIcon( icon )


    def _set_menubar ( self, menubar ):
        self.control.SetMenuBar( menubar )


    def _set_toolbar ( self, toolbar ):
        self.control.SetToolBar( toolbar )


    def _set_frozen ( self, is_frozen ):
        if is_frozen:
            self.control.Freeze()
        else:
            self.control.Thaw()


    def _get_is_panel ( self ):
        return isinstance( self.control, wx.Panel )


    def _set_scroll_vertical ( self, can_scroll ):
        self.control.SetupScrolling( scroll_y = can_scroll )


    def _set_scroll_horizontal ( self, can_scroll ):
        self.control.SetupScrolling( scroll_x = can_scroll )

    #-- Control Method Implementations -----------------------------------------

    def refresh ( self, x = None, y = None, dx = None, dy = None ):
        """ Refreshes the specified region of the control. If no arguments
            are specified, the entire control should be refreshed.
        """
        if x is None:
            self.control.Refresh()
        else:
            self.control.RefreshRect( wx.Rect( x, y, dx, dy ), False )


    def update ( self ):
        """ Causes the control to update its layout.
        """
        try:
            self.control.Layout()
            self.control.Refresh()
        except wx.PyDeadObjectError:
            pass


    def set_focus ( self ):
        """ Sets the keyboard focus on the associated control.
        """
        self.control.SetFocus()


    def set_mouse_focus ( self ):
        """ Sets the mouse focus on the associated control.
        """
        self.control.SetFocus()


    def popup_menu ( self, menu, x, y ):
        """ Pops up the specified context menu at the specified screen position.
        """
        self.control.PopupMenuXY( menu, x, y )


    def bitmap_size ( self, bitmap ):
        """ Returns the size (dx,dy) of the specified toolkit specific bitmap:
        """
        return ( bitmap.GetWidth(), bitmap.GetHeight() )


    def text_size ( self, text ):
        """ Returns the size (dx,dy) of the specified text string (using the
            current control font).
        """
        return self.control.GetTextExtent( text )


    def set_event_handler ( self, **handlers ):
        """ Sets up event handlers for a specified set of events. The keyword
            names correspond to UI toolkit neutral event names, and the values
            are the callback functions for the events. Multiple event handlers
            can be set up in a single call.
        """
        self._mouse_handler( handlers )

        control = self.control
        parent  = control.GetParent()
        id      = control.GetId()

        for name, handler in handlers.iteritems():
            if name in DragDropEvents:
                drop_target = control.GetDropTarget()
                if drop_target is None:
                    drop_target = WxDropTarget()
                    control.SetDropTarget( drop_target )

                setattr( drop_target, '_' + name, handler )

            else:
                wx_event, use_id = event_handlers[ name ]
                if use_id:
                    wx_event( parent, id, EventWrapper( handler, name ) )
                else:
                    wx_event( control, EventWrapper( handler, name ) )

                # Handle any special cases:
                if name == 'paint':
                    # 'paint' requires an appropriate 'erase_background'
                    # handler:
                    wx.EVT_ERASE_BACKGROUND( control, self._erase_background )
                elif name == 'enter':
                    # Note the fact that an 'enter' handler has been set up
                    # (see the 'wheel' code below):
                    self._enter = True
                elif name == 'wheel':
                    # 'wheel' requires that the control accepts focus:
                    control.accepts_focus = True
                    if not self._enter:
                        wx.EVT_ENTER_WINDOW( control, self._set_mouse_focus )


    def unset_event_handler ( self, **handlers ):
        """ Tears down event handlers for a specified set of events. The keyword
            names correspond to UI toolkit neutral event names, and the values
            are the callback functions for the events that should no longer be
            called. Multiple event handlers can be torn down in a single call.
        """
        self._mouse_handler( handlers )

        control = self.control
        parent  = control.GetParent()
        id      = control.GetId()

        for name, handler in handlers.iteritems():
            if name in DragDropEvents:
                drop_target = control.GetDropTarget()
                if drop_target is not None:
                    name = '_' + name
                    if hasattr( drop_target, name ):
                        delattr( drop_target, name )
            else:
                setup, use_id = event_handlers[ name ]
                if use_id:
                    setup( parent, id, None )
                else:
                    setup( control, None )

                # Handle any special cases:
                if name == 'paint':
                    # Remove the 'paint' 'erase_background' handler:
                    wx.EVT_ERASE_BACKGROUND( control, None )
                elif name == 'enter':
                    # Note that the 'enter' handler has been removed:
                    del self._enter


    def tab ( self, forward = True ):
        """ Moves the keyboard focus to the next/previous control that will
            accept it. If *forward* is True (the default) the next valid control
            is used; otherwise the previous valid control is used.
        """
        if forward:
            self.control.Navigate( 1 )
        else:
            self.control.Navigate( 0 )


    def scroll_to ( self, x = None, y = None ):
        """ Scrolls the control so that the point (x,y) is visible. If x or y
            is None, the maximum value for that coordinate is used.
        """
        raise NotImplementedError


    def scroll_by ( self, x = 0, y = 0 ):
        """ Scrolls the control by the amount specified by *x* and *y*.
        """
        raise NotImplementedError


    def destroy ( self ):
        """ Destroys the control associated with the adapter.
        """
        self.control.Destroy()


    def clear ( self ):
        """ Clears the current contents of the control.
        """
        getattr( self, 'clear_for_' + self.control.__class__.__name__ )()

    def clear_for_Choice ( self ):
        self.control.Clear()

    def clear_for_ComboBox ( self ):
        self.control.Clear()


    def close ( self ):
        """ Request the control to close itself.
        """
        self.control.Close()


    def get_item ( self, index ):
        """ Returns the control's *index*th item, for controls that contain
            items (e.g. list boxes, notebooks).
        """
        return getattr( self, 'get_item_for_' +
                              self.control.__class__.__name__ )( index )

    def get_item_for_Noteboook ( self, index ):
        return control_adapter( self.control.GetPage( index ) )


    def remove_item ( self, index ):
        """ Removes the control's *index*th item, for controls that contain
            items (e.g. list boxes, notebooks).
        """
        getattr( self, 'remove_item_for_' + self.control.__class__.__name__ )(
            index )

    def remove_item_for_Notebook ( self, index ):
        self.control.RemovePage( index )


    def add_item ( self, value ):
        """ Adds the value specified by *value* to the control, and returns the
            index assigned to it.
        """
        return getattr( self, 'add_item_for_' +
                              self.control.__class__.__name__ )( value )

    def add_item_for_Choice ( self, value ):
        return self.control.Append( value )

    def add_item_for_ComboBox ( self, value ):
        return self.control.Append( value )


    def find_item ( self, value ):
        """ Returns the index of the control item matching the specified
            *value*. If no matching item is found, it returns -1.
        """
        return getattr( self, 'find_item_for_' +
                              self.control.__class__.__name__ )( value )

    def find_item_for_Choice ( self, value ):
        return self.control.FindString( value )

    def find_item_for_ComboBox ( self, value ):
        return self.control.FindString( value )


    def find_control ( self, x, y ):
        """ Finds and returns the topmost control at the specified (x, y )
            location, where ( x, y ) are in the control's local coordinate
            space. If no control is at the specified location, None is return.
        """
        x0, y0 = self.screen_position

        return adapted_control(
            wx.FindWindowAtPoint( wx.Point( x0 + x, y0 + y ) )
        )


    def add_page ( self, name, control ):
        """ Adds the page defined by *control* with the name *name* to the
            control (which should be some type of notebook control).
        """
        self.control.AddPage( control(), name )


    def shrink_wrap ( self ):
        """ Resizes the control so that it fits snugly around its child
            controls.
        """
        control  = self.control
        children = control.GetChildren()
        if len( children ) == 1:
            control.SetClientSize( children[0].GetSize() )
        else:
            control.Fit()


    def drag ( self, data, type = None, request = 'copy', image = None ):
        """ Initiates a drag operation with the specified *data*. If *type* is
            **None**, the control will try to determine the kind of data being
            dragged from the data itself. Other than **None**, the legal values
            for *type* are: 'color', 'image', 'text', 'html', 'files', 'urls'
            and 'object'.

            *Request* specifies whether the data is to be copied ('copy'),
            moved ('move') or linked ('link'), with the default request being to
            copy the data.

            *Image* specifies an ImageResource image to be used while dragging
            to provide the user with some indication of what is being dragged.
            This may not be supported with all UI back-ends. If not supported,
            the *image* value is treated as *None*. A value of *None* indicates
            that the default drag image should be used.

            The result is a string indicating the action taken by the receiver
            (if any) of the data at the completion of the drag and drop
            operation. The possible values are: 'copy', 'move', 'link' and
            'ignore'.
        """
        # If no specific type is specified, assign one based on the data type:
        if type is None:
            if isinstance( data, basestring ):
                type = 'text'
            elif isinstance( data, AnImageResource ):
                type = 'image'
                data = data.bitmap
            elif (is_win32 and isinstance( data, SequenceTypes ) and
                  (len( data ) > 0) and isinstance( data[0], basestring )):
                type = 'files'
            else:
                type = 'object'

        # Create the drop source and perform the drag and drop operation:
        ds = wx.DropSource( self.control )
        ds.SetData(
            getattr( self, '_drag_%s' % type, self._drag_object )( data )
        )
        result = RequestAction[ ds.DoDragDrop(
            ResultAction.get( request, wx.Drag_CopyOnly )
        ) ]

        # Clean up any unpickled Python object that might have been used during
        # the drag operation:
        drag_adapter.drag_object = None

        return result

    def _drag_image ( self, image ):
        if not isinstance( image, wx.Bitmap ):
            return self._drag_object( image )

        return wx.BitmapDataObject( image )

    def _drag_text ( self, text ):
        if not isinstance( text, basestring ):
            text = str( text )

        return wx.TextDataObject( text )

    def _drag_files ( self, files ):
        try:
            if isinstance( files, basestring ):
                result = wx.FileDataObject()
                result.AddFile( files )

                return result

            if isinstance( files, SequenceTypes ) and (len( files ) > 0):
                result = wx.FileDataObject()
                for file in files:
                    if not isinstance( file, basestring ):
                        break

                    result.AddFile( file )
                else:
                    return result
        except:
            pass

        return self._drag_object( image )

    def _drag_object ( self, object ):
        return python_data_object( object )


    def activate ( self ):
        """ Makes sure that the control (which should be a top-level window) is
            on top of all other application windows. If it is not, then it will
            brought in front of all other windows.
        """
        self.visible = True
        self.control.Raise()

    #-- Private Methods --------------------------------------------------------

    def _erase_background ( self, event ):
        """ Never erase the background. The paint handler will do all of the
            required work.
        """
        pass


    def _set_mouse_focus ( self, event ):
        """ Handles the mouse pointing entering the control by setting mouse
            focus to the control.
        """
        self.set_mouse_focus()


    def _mouse_handler ( self, handlers ):
        """ Replace any 'mouse' handler in *handlers* by the equivalent set of
            individual mouse event handlers.
        """
        handler = handlers.get( 'mouse' )
        if handler is not None:
            del handlers[ 'mouse' ]

            for event in mouse_events:
                handlers[ event ] = handler

#-------------------------------------------------------------------------------
#  'EventWrapper' class:
#-------------------------------------------------------------------------------

class EventWrapper ( object ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, method, name ):
        self.method = method
        self.name   = name


    def __call__ ( self, event ):
        self.method( WxUIEvent( event, name = self.name ) )

#-- EOF ------------------------------------------------------------------------