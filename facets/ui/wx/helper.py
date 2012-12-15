"""
Defines helper functions and classes used to define wxPython-based facet
    editors and facet editor factories.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
import wx.lib.scrolledpanel

import sys

from os.path \
    import join, dirname, abspath

from facets.core_api \
    import HasPrivateFacets, Enum, CFacet, Instance, Any, Int, Event, Bool, \
           BaseFacetHandler, FacetError

from facets.ui.ui_facets \
    import image_for, SequenceTypes

from facets.ui.toolkit \
    import toolkit

from facets.ui.pyface.timer.api \
    import do_later

from constants \
    import standard_bitmap_width, screen_dx, screen_dy

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum( 'horizontal', 'vertical' )

#-------------------------------------------------------------------------------
#  Data:
#-------------------------------------------------------------------------------

# Bitmap cache dictionary (indexed by filename)
_bitmap_cache = {}

### NOTE: This needs major improvements:

app_path    = None
facets_path = None

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def bitmap_cache ( name, standard_size, path = None ):
    """ Converts an image file name to a cached bitmap.
    """
    global app_path, facets_path

    if name[:1] == '@':
        image = image_for( name.replace( ' ', '_' ).lower() )
        if image is not None:
            return image.create_image().ConvertToBitmap()

    if path is None:
        if facets_path is None:
           import  facets.ui.wx.editors
           facets_path = join( dirname( facets.ui.wx.editors.__file__ ),
                               'images' )
        path = facets_path
    elif path == '':
        if app_path is None:
            app_path = join( dirname( sys.argv[ 0 ] ), '..', 'images' )
        path = app_path

    filename = abspath(
                   join( path, name.replace( ' ', '_' ).lower() + '.gif' ) )
    bitmap   = _bitmap_cache.get( filename + ( '*'[ not standard_size: ] ) )
    if bitmap is not None:
        return bitmap

    std_bitmap = bitmap = wx.BitmapFromImage( wx.Image( filename ) )
    _bitmap_cache[ filename ] = bitmap

    dx = bitmap.GetWidth()
    if dx < standard_bitmap_width:
        dy = bitmap.GetHeight()
        std_bitmap = wx.EmptyBitmap( standard_bitmap_width, dy )
        dc1 = wx.MemoryDC()
        dc2 = wx.MemoryDC()
        dc1.SelectObject( std_bitmap )
        dc2.SelectObject( bitmap )
        dc1.SetPen( wx.TRANSPARENT_PEN )
        dc1.SetBrush( wx.WHITE_BRUSH )
        dc1.DrawRectangle( 0, 0, standard_bitmap_width, dy )
        dc1.Blit( ( standard_bitmap_width - dx ) / 2, 0, dx, dy, dc2, 0, 0 )

    _bitmap_cache[ filename + '*' ] = std_bitmap

    if standard_size:
        return std_bitmap

    return bitmap


def choice_width ( values ):
    """ Returns an appropriate width for a wxChoice widget based upon the list
        of values it contains:
    """
    return max( [ len( x ) for x in values ] ) * 6


def save_window ( ui ):
    """ Saves the user preference items for a specified UI.
    """
    control = ui.control
    ui.save_prefs( control.GetPositionTuple() + control.GetSizeTuple() )


def restore_window ( ui, is_popup = False ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        x, y, dx, dy = prefs
        if is_popup:
            position_window( ui.control, dx, dy )
        else:
            ui.control.SetDimensions( x, y, dx, dy )


def position_window ( window, width = None, height = None, parent = None ):
    """ Positions a window on the screen with a specified width and height so
        that the window completely fits on the screen if possible.
    """
    dx, dy = window.GetSizeTuple()
    width  = width  or dx
    height = height or dy

    if parent is None:
        parent = window._parent

    if parent is None:
        # Center the popup on the screen:
        window.SetDimensions( ( screen_dx - width )  / 2,
                              ( screen_dy - height ) / 2, width, height )
        return

    # Calculate the desired size of the popup control:
    if isinstance( parent, wx.Window ):
        x, y     = parent.ClientToScreenXY( 0, 0 )
        cdx, cdy = parent.GetSizeTuple()
    else:
        # Special case of parent being a screen position and size tuple (used
        # to pop-up a dialog for a table cell):
        x, y, cdx, cdy = parent

    adjacent = ( getattr( window, '_kind', 'popup' ) == 'popup' )
    width    = min( max( cdx, width ), screen_dx )
    height   = min( height, screen_dy )

    # Calculate the best position and size for the pop-up:

    # Note: This code tries to deal with the fact that the user may have
    # multiple monitors. wx does not report this information, so the screen_dx,
    # screen_dy values usually just provide the size of the primary monitor. To
    # get around this, the code assumes that the original (x,y) values are
    # valid, and that all monitors are the same size. If this assumption is not
    # true, popups may appear in wierd positions on the secondary monitors.
    nx     = x % screen_dx
    xdelta = x - nx
    rx     = nx + cdx
    if ( nx + width ) > screen_dx:
        if ( rx - width ) < 0:
            nx = screen_dx - width
        else:
            nx = rx - width

    ny     = y % screen_dy
    ydelta = y - ny
    by     = ny
    if adjacent:
        by += cdy
    if ( by + height ) > screen_dy:
        if not adjacent:
            ny += cdy
        if ( ny - height ) < 0:
            ny = screen_dy - height
        else:
            by = ny - height

    # Position and size the window as requested:
    window.SetDimensions( nx + xdelta, by + ydelta, width, height )


def top_level_window_for ( control ):
    """ Returns the top-level window for a specified control.
    """
    parent = control.GetParent()
    while parent is not None:
        control = parent
        parent  = control.GetParent()

    return control


def enum_values_changed ( values ):
    """ Recomputes the mappings for a new set of enumeration values.
    """

    if isinstance( values, dict ):
        data = [ ( str( v ), n ) for n, v in values.items() ]
        if len( data ) > 0:
            data.sort( lambda x, y: cmp( x[ 0 ], y[ 0 ] ) )
            col = data[ 0 ][ 0 ].find( ':' ) + 1
            if col > 0:
                data = [ ( n[ col: ], v ) for n, v in data ]
    elif not isinstance( values, SequenceTypes ):
        handler = values
        if isinstance( handler, CFacet ):
            handler = handler.handler

        if not isinstance( handler, BaseFacetHandler ):
            raise FacetError( "Invalid value for 'values' specified" )

        if handler.is_mapped:
            data = [ ( str( n ), n ) for n in handler.map.keys() ]
            data.sort( lambda x, y: cmp( x[ 0 ], y[ 0 ] ) )
        else:
            data = [ ( str( v ), v ) for v in handler.values ]
    else:
        data = [ ( str( v ), v ) for v in values ]

    names           = [ x[ 0 ] for x in data ]
    mapping         = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[ name ] = value
        inverse_mapping[ value ] = name

    return ( names, mapping, inverse_mapping )


def disconnect ( control, * events ):
    """ Disconnects a wx event handle from its associated control.
    """
    id = control.GetId()
    for event in events:
        event( control, id, None )


def disconnect_no_id ( control, * events ):
    """ Disconnects a wx event handle from its associated control.
    """
    for event in events:
        event( control, None )

#-------------------------------------------------------------------------------
#  'FacetsUIPanel' class:
#-------------------------------------------------------------------------------

class FacetsUIPanel ( wx.Panel ):
    """ Creates a wx.Panel that correctly sets its background color to be the
        same as its parents.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, parent, *args, **kw ):
        """ Creates a wx.Panel that correctly sets its background color to be
            the same as its parents.
        """
        from facets.extra.helper.debug import created_from; created_from( self )

        wx.Panel.__init__( self, parent, *args, **kw )

        wx.EVT_CHILD_FOCUS(      self, self.OnChildFocus )
        wx.EVT_ERASE_BACKGROUND( self, self.OnEraseBackground )
        wx.EVT_PAINT(            self, self.OnPaint )

        self.SetBackgroundColour( parent.GetBackgroundColour() )

        # Make sure that we have an associated GUI toolkit neutral adapter
        # defined so we don't have to check in the paint handler each time:
        toolkit().control_adapter_for( self )


    def OnEraseBackground ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass


    def OnPaint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        from facets.ui.pyface.image_slice import paint_parent

        paint_parent( self.adapter.graphics, self.adapter )


    def OnChildFocus ( self, event ):
        """ If the ChildFocusEvent contains one of the Panel's direct children,
            then we will Skip it to let it pass up the widget hierarchy.

            Otherwise, we consume the event to make sure it doesn't go any
            farther. This works around a problem in wx 2.8.8.1 where each Panel
            in a nested hierarchy generates many events that might consume too
            many resources. We do, however, let one event bubble up to the top
            so that it may inform a top-level ScrolledPanel that a descendant
            has acquired focus.
        """
        if event.GetWindow() in self.GetChildren():
            event.Skip()

#-------------------------------------------------------------------------------
#  'ChildFocusOverride' class:
#-------------------------------------------------------------------------------

# PyEvtHandler was only introduced in wxPython 2.8.8. Fortunately, it is only
# necessary in wxPython 2.8.8.
if wx.__version__ < '2.8.8':

    class ChildFocusOverride ( object ):
        def __init__ ( self, window ):
            # Set up the event listener.
            window.Bind( wx.EVT_CHILD_FOCUS, window.OnChildFocus )

else:

    class ChildFocusOverride ( wx.PyEvtHandler ):
        """ Override the scroll-to-focus behaviour in wx 2.8.8's ScrolledWindow
            C++ implementation for ScrolledPanel.

            Instantiating this class with the ScrolledPanel will register the
            new instance as the event handler for the panel.
        """

        def __init__ ( self, window ):
            self.window = window
            wx.PyEvtHandler.__init__( self )

            # Make self the event handler for the window.
            window.PushEventHandler( self )


        def ProcessEvent ( self, event ):
            if isinstance( event, wx.ChildFocusEvent ):
                # Handle this one with our code and don't let the C++ event
                # handler get it:
                return self.window.OnChildFocus( event )
            else:
                # Otherwise, just pass this along in the event handler chain.
                result = self.GetNextHandler().ProcessEvent( event )
                return result

#-------------------------------------------------------------------------------
#  'FacetsUIScrolledPanel' class:
#-------------------------------------------------------------------------------

class FacetsUIScrolledPanel ( wx.lib.scrolledpanel.ScrolledPanel ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, parent, id = -1, pos = wx.DefaultPosition,
                   size = wx.DefaultSize, style = wx.TAB_TRAVERSAL,
                   name = "scrolledpanel" ):
        from facets.extra.helper.debug import created_from; created_from( self )

        wx.PyScrolledWindow.__init__( self, parent, id, pos = pos, size = size,
                                      style = style, name = name )
        self.SetInitialSize( size )
        self.SetBackgroundColour( parent.GetBackgroundColour() )

        # Override the C++ ChildFocus event handler:
        ChildFocusOverride( self )


    def OnChildFocus ( self, event ):
        """ Handle a ChildFocusEvent.

        Returns a boolean so it can be used as a library call, too.
        """
        self.ScrollChildIntoView( self.FindFocus() )

        return True


    def ScrollChildIntoView ( self, child ):
        """ Scrolls the panel such that the specified child window is in view.
            This method overrides the original in the base class so that
            nested subpanels are handled correctly.
        """
        sppux, sppuy = self.GetScrollPixelsPerUnit()
        vsx, vsy     = self.GetViewStart()

        crx, cry, crdx, crdy = child.GetRect()
        subwindow = child.GetParent()
        while (subwindow is not None) and (subwindow is not self):
            # Make sure that the descendant's position information is relative
            # to us, not its local parent.
            pwx, pwy   = subwindow.GetRect()[:2]
            crx, cry  = crx + pwx, cry + pwy
            subwindow = subwindow.GetParent()

        cr = wx.Rect( crx, cry, crdx, crdy )

        client_size      = self.GetClientSize()
        new_vsx, new_vsy = -1, -1

        # Is it before the left edge?
        if (cr.x < 0) and (sppux > 0):
            new_vsx = vsx + (cr.x / sppux)

        # Is it above the top?
        if (cr.y < 0) and (sppuy > 0):
            new_vsy = vsy + (cr.y / sppuy)

        # For the right and bottom edges, scroll enough to show the whole
        # control if possible, but if not just scroll such that the top/left
        # edges are still visible:

        # Is it past the right edge?
        if (cr.right > client_size.width) and (sppux > 0):
            diff = (cr.right - client_size.width) / sppux
            if (cr.x - (diff * sppux)) > 0:
                new_vsx = vsx + diff + 1
            else:
                new_vsx = vsx + (cr.x / sppux)

        # Is it below the bottom?
        if (cr.bottom > client_size.height) and (sppuy > 0):
            diff = (cr.bottom - client_size.height) / sppuy
            if (cr.y - (diff * sppuy)) > 0:
                new_vsy = vsy + diff + 1
            else:
                new_vsy = vsy + (cr.y / sppuy)

        # Perform the scroll if any adjustments are needed:
        if (new_vsx != -1) or (new_vsy != -1):
            self.Scroll( new_vsx, new_vsy )

#-------------------------------------------------------------------------------
#  Initializes standard wx event handlers for a specified control and object:
#-------------------------------------------------------------------------------

def open_fbi ( ):
    """ Safely tries to pop up an FBI window if 'facets.extra.helper' is
        installed.
    """
    try:
        from facets.extra.helper.fbi import if_fbi
        if not if_fbi():
            import traceback
            traceback.print_exc()
    except ImportError:
        pass

#-------------------------------------------------------------------------------
#  'PopupControl' class:
#-------------------------------------------------------------------------------

class PopupControl ( HasPrivateFacets ):

    #-- Constructor Facets -----------------------------------------------------

    # The control the popup should be positioned relative to:
    control = Instance( wx.Window )

    # The minimum width of the popup:
    width = Int

    # The minimum height of the popup:
    height = Int

    # Should the popup be resizable?
    resizable = Bool( False )

    #-- Public Facets ----------------------------------------------------------

    # The value (if any) set by the popup control:
    value = Any

    # Event fired when the popup control is closed:
    closed = Event

    #-- Private Facets ---------------------------------------------------------

    # The popup control:
    popup = Instance( wx.Window )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, **facets ):
        """ Initializes the object.
        """
        super( PopupControl, self ).__init__( **facets )

        style = wx.SIMPLE_BORDER
        if self.resizable:
            style = wx.RESIZE_BORDER

        self.popup = popup = wx.Frame( None, -1, '', style = style )
        wx.EVT_ACTIVATE( popup, self._on_close_popup )
        self.create_control( popup )
        self._position_control()
        popup.Show()


    def create_control ( self ):
        """ Creates the control.

            Must be overridden by a subclass.
        """
        raise NotImplementedError


    def dispose ( self ):
        """ Called when the popup is being closed to allow any custom clean-up.

            Can be overridden by a subclass.
        """
        pass

    #-- Event Handlers ---------------------------------------------------------

    def _value_set ( self, value ):
        """ Handles the 'value' being changed.
        """
        do_later( self._close_popup )

    #-- Private Methods --------------------------------------------------------

    def _position_control ( self ):
        """ Initializes the popup control's initial position and size.
        """
        # Calculate the desired size of the popup control:
        px,  cy  = self.control.ClientToScreenXY( 0, 0 )
        cdx, cdy = self.control.GetSizeTuple()
        pdx, pdy = self.popup.GetSizeTuple()
        pdx, pdy = max( pdx, cdx, self.width ), max( pdy, self.height )

        # Calculate the best position and size for the pop-up:
        py = cy + cdy
        if ( py + pdy ) > screen_dy:
            if ( cy - pdy ) < 0:
                bottom = screen_dy - py
                if cy > bottom:
                    py, pdy = 0, cy
                else:
                    pdy = bottom
            else:
                py = cy - pdy

        # Finally, position the popup control:
        self.popup.SetDimensions( px, py, pdx, pdy )


    def _on_close_popup ( self, event ):
        """ Closes the popup control when it is deactivated.
        """
        if not event.GetActive():
            self._close_popup()


    def _close_popup ( self ):
        """ Closes the dialog.
        """
        wx.EVT_ACTIVATE( self.popup, None )
        self.dispose()
        self.closed = True
        self.popup.Destroy()
        self.popup = self.control = None

#-------------------------------------------------------------------------------
#  'Slider' class:
#-------------------------------------------------------------------------------

class Slider ( wx.Slider ):
    """ This is a 'fixed' version of the wx.Slider control which does not
        erase its background, which can cause a lot of update flicker and is
        completely unnecessary.
    """

    def __init__ ( self, *args, **kw ):
        super( Slider, self ).__init__( *args, **kw )

        wx.EVT_ERASE_BACKGROUND( self, self._erase_background )


    def _erase_background ( self, event ):
        pass

#-------------------------------------------------------------------------------
#  'FontEnumerator' class:
#-------------------------------------------------------------------------------

class FontEnumerator ( wx.FontEnumerator ):
    """ An enumeration of fonts.
    """

    #-- Public Methods ---------------------------------------------------------

    def facenames ( self ):
        """ Returns a list of all available font facenames.
        """
        if getattr( self, '_facenames', None ) is None:
            self._facenames = []
            self.EnumerateFacenames()

        return self._facenames


    def OnFacename ( self, facename ):
        """ Adds a facename to the list of facenames.
        """
        self._facenames.append( facename )

        return True

#-- EOF ------------------------------------------------------------------------
