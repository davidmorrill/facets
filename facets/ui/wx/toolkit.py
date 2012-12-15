"""
Defines the concrete implementations of the facets Toolkit interface for
the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

# Make sure that wxPython is installed
import wx

# Make sure a wx.App object is created early:
_app = wx.GetApp()
if _app is None:
    _app = wx.PySimpleApp()

from numpy \
    import fromstring, reshape, uint8

from facets.core_api \
    import HasPrivateFacets, Instance, Int, Property, Category, cached_property

from facets.core.facet_notifiers \
    import set_ui_handler

from facets.ui.ui \
    import UI

from facets.ui.theme \
    import Theme

from facets.ui.constants \
    import screen_dx, screen_dy

from facets.ui.toolkit \
    import Toolkit

from facets.ui.editor \
    import Editor

from facets.ui.adapters.control \
    import Control, as_toolkit_control

from facets.ui.wx.adapters.control \
    import adapted_control, control_adapter

from facets.ui.wx.adapters.layout \
    import adapted_layout, layout_adapter

from facets.ui.wx.util.drag_and_drop \
    import PythonDropTarget, clipboard

from constants \
    import WindowColor

from helper \
    import FacetsUIPanel, FacetsUIScrolledPanel, FontEnumerator

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

EventSuffix = {
    wx.wxEVT_LEFT_DOWN:     'left_down',
    wx.wxEVT_LEFT_DCLICK:   'left_dclick',
    wx.wxEVT_LEFT_UP:       'left_up',
    wx.wxEVT_MIDDLE_DOWN:   'middle_down',
    wx.wxEVT_MIDDLE_DCLICK: 'middle_dclick',
    wx.wxEVT_MIDDLE_UP:     'middle_up',
    wx.wxEVT_RIGHT_DOWN:    'right_down',
    wx.wxEVT_RIGHT_DCLICK:  'right_dclick',
    wx.wxEVT_RIGHT_UP:      'right_up',
    wx.wxEVT_MOTION:        'mouse_move',
    wx.wxEVT_ENTER_WINDOW:  'enter',
    wx.wxEVT_LEAVE_WINDOW:  'leave',
    wx.wxEVT_MOUSEWHEEL:    'mouse_wheel',
    wx.wxEVT_PAINT:         'paint',
 }

# Horizontal alignment styles:
horizontal_alignment_styles = {
    'default': wx.ALIGN_LEFT,
    'left':    wx.ALIGN_LEFT,
    'center':  wx.ALIGN_CENTRE,
    'right':   wx.ALIGN_RIGHT
}

# Horizontal alignment styles for text input:
input_horizontal_alignment_styles = {
    'default': wx.TE_LEFT,
    'left':    wx.TE_LEFT,
    'center':  wx.TE_CENTRE,
    'right':   wx.TE_RIGHT
}

# Mapping from boolean 'is_vertical' to wxPython layout orientation:
orientation_map = {
    True:  wx.VERTICAL,
    False: wx.HORIZONTAL
}

# Mapping from boolean 'is_vertical' to wx.StaticLine orientation styles:
separator_map = {
    True:  wx.LI_VERTICAL,
    False: wx.LI_HORIZONTAL
}

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# The singleton clipboard object:
the_clipboard = None

# The singleton font enumerator object:
the_font_enumerator = None

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def ui_handler ( handler, *args ):
    """ Handles UI notification handler requests that occur on a thread other
        than the UI thread.
    """
    wx.CallAfter( handler, *args )

# Tell the facets notification handlers to use this UI handler
set_ui_handler( ui_handler )

#-------------------------------------------------------------------------------
#  'GUIToolkit' class:
#-------------------------------------------------------------------------------

class GUIToolkit ( Toolkit ):
    """ Implementation class for wxPython toolkit.
    """

    def ui_wizard ( self, ui, parent ):
        """ Creates a wxPython wizard dialog user interface using information
            from the specified UI object.
        """
        import facets.ui.wx.editors.ui_wizard

        ui_wizard.ui_wizard( ui, parent )


    def show_help ( self, ui, control ):
        """ Shows a help window for a specified UI and control.
        """
        import facets.ui.wx.editors.ui_panel

        ui_panel.show_help( ui, control )


    def key_event_to_name ( self, event ):
        """ Converts a keystroke event into a corresponding key name.
        """
        from key_event_to_name import key_event_to_name

        return key_event_to_name( event )


    def hook_events ( self, ui, control, events = None, handler = None,
                      drop_target = None ):
        """ Hooks all specified events for all controls in a UI so that they
            can be routed to the correct event handler.
        """
        wx_control = as_toolkit_control( control )
        if isinstance( wx_control, wx.Window ):
            if events is None:
                events = (
                   wx.wxEVT_LEFT_DOWN, wx.wxEVT_LEFT_DCLICK, wx.wxEVT_LEFT_UP,
                   wx.wxEVT_MIDDLE_DOWN, wx.wxEVT_MIDDLE_DCLICK,
                   wx.wxEVT_MIDDLE_UP, wx.wxEVT_RIGHT_DOWN,
                   wx.wxEVT_RIGHT_DCLICK, wx.wxEVT_RIGHT_UP, wx.wxEVT_MOTION,
                   wx.wxEVT_ENTER_WINDOW, wx.wxEVT_LEAVE_WINDOW,
                   wx.wxEVT_MOUSEWHEEL, wx.wxEVT_PAINT
                )
                wx_control.SetDropTarget( PythonDropTarget(
                                    DragHandler( ui = ui, control = wx_control ) ) )
            elif events == 'keys':
                events = ( wx.wxEVT_CHAR, )

            if handler is None:
                handler = ui.route_event

            id            = wx_control.GetId()
            event_handler = wx.EvtHandler()
            connect       = event_handler.Connect

            for event in events:
                connect( id, id, event, handler )

            wx_control.PushEventHandler( event_handler )

        for child in control.children:
            self.hook_events( ui, child, events, handler, drop_target )


    def route_event ( self, ui, event ):
        """ Routes a hooked event to the correct handler method.
        """
        suffix  = EventSuffix[ event.GetEventType() ]
        control = event.GetEventObject()
        handler = ui.handler
        method  = None

        owner   = getattr( control, '_owner', None )
        if owner is not None:
            method = getattr( handler, 'on_%s_%s' % ( owner.get_id(), suffix ),
                              None )

        if method is None:
            method = (getattr( handler, 'on_%s' % suffix, None ) or
                      getattr( handler, 'on_any_event',   None ))

        if (method is None) or (method( ui.info, owner, event ) is False):
            event.Skip()


    def event_loop ( self, exit_code = None ):
        """ Enters or exits a user interface event loop. If *exit_code* is
            omitted, a new event loop is started. If *exit_code*, which should
            be an integer, is specified, the most recent event loop started is
            exited with the specified *exit_code* as the result. Control does
            not return from a call to start an event loop until a corresponding
            request to exit an event loop is made. Event loops may be nested.
        """
        if exit_code is None:
            if self._event_loop is None:
                self._event_loop = []

            event_loop = self._event_loop
            if len( event_loop ) == 0:
                event_loop.append( wx.Eventloop.GetActive() )

            loop = wx.EventLoop()
            event_loop.append( loop )
            wx.EventLoop.SetActive( loop )
            result = loop.Run()
            wx.EventLoop.SetActive( event_loop[-1] )

            return result

        if len( self._event_loop or []) > 1:
            self._event_loop.pop().Exit( int( exit_code ) )


    def image_size ( self, image ):
        """ Returns a (width,height) tuple containing the size of a specified
            toolkit image.
        """
        return ( image.GetWidth(), image.GetHeight() )


    def constants ( self ):
        """ Returns a dictionary of useful constants.

            Currently, the dictionary should have the following key/value pairs:
            - WindowColor': the standard window background color in the toolkit
              specific color format.
        """
        return {
            'WindowColor': WindowColor
        }


    def to_toolkit_color ( self, color ):
        """ Returns a specified GUI toolkit neutral color as a toolkit specific
            color object.
        """
        return wx.Colour( *color )


    def from_toolkit_color ( self, color ):
        """ Returns a toolkit specific color object as a GUI toolkit neutral
            color.
        """
        if isinstance( color, tuple ):
            return color

        alpha = color.Alpha()
        if alpha == 255:
            return ( color.Red(), color.Green(), color.Blue() )

        return ( color.Red(), color.Green(), color.Blue(), alpha )


    def beep ( self ):
        """ Makes a beep to alert the user to a situation requiring their
            attention.
        """
        wx.Bell()


    def screen_size ( self ):
        """ Returns a tuple of the form (width,height) containing the size of
            the user's display.
        """
        return ( wx.SystemSettings_GetMetric( wx.SYS_SCREEN_X ),
                 wx.SystemSettings_GetMetric( wx.SYS_SCREEN_Y ) )


    def screen_info ( self ):
        """ Returns a list of tuples of the form: ( x, y, dx, dy ), which
            describe the available screen area (excluding system managed areas
            like the Mac Dock or Windows launch bar) for all of the system's
            displays. There is one tuple for each display. The first tuple in
            the list is always for the system's primary display.
        """
        raise NotImplementedError


    def screen ( self ):
        """ Returns a Control object representing the entire display.
        """
        raise NotImplementedError


    def scrollbar_size ( self ):
        """ Returns a tuple of the form (width,height) containing the standard
            width of a vertical scrollbar, and the standard height of a
            horizontal scrollbar.
        """
        return ( wx.SystemSettings_GetMetric( wx.SYS_VSCROLL_X ),
                 wx.SystemSettings_GetMetric( wx.SYS_HSCROLL_Y ) )


    def mouse_position ( self ):
        """ Returns the current mouse position (in screen coordinates) as a
            tuple of the form: (x,y).
        """
        return wx.GetMousePosition()


    def mouse_buttons ( self ):
        """ Returns a set containing the mouse buttons currently being pressed.
            The possible set values are: 'left', 'middle', 'right'.
        """
        result = set()
        ms     = wx.GetMouseState()

        if ms.LeftDown():
            result.add( 'left' )

        if ms.MiddleDown():
            result.add( 'middle' )

        if ms.RightDown():
            result.add( 'right' )

        return result


    def control_at ( self, x, y ):
        """ Returns the Control at the specified screen coordinates, or None if
            there is no control at that position.
        """
        return adapted_control( wx.FindWindowAtPoint( wx.Point( x, y ) ) )


    def is_application_running ( self ):
        """ Returns whether or not the wx.App object has been created and is
            running its event loop.
        """
        global _app

        return _app.IsMainLoopRunning()


    def run_application ( self, app_info ):
        """ Runs the application described by the *app_info* object as a Facets
            UI modal application using the wxPython toolkit.
        """
        Application( app_info )


    # fixme: We should be able to delete this after everything is debugged...
    def as_toolkit_adapter ( self, control ):
        """ Returns the GUI toolkit specific control adapter associated with
            *control*.
        """
        if ((control is None) or isinstance( control, ( Control, tuple ) )):
            return control

        return control_adapter( control )


    def clipboard ( self ):
        """ Returns the GUI toolkit specific implementation of the clipboard
            object that implements the Clipboard interface.
        """
        global the_clipboard

        if the_clipboard is None:
            from facets.ui.wx.adapters.clipboard import WxClipboard

            the_clipboard = WxClipboard()

        return the_clipboard


    def font_names ( self ):
        """ Returns a list containing the names of all available fonts.
        """
        global the_font_enumerator

        if the_font_enumerator is None:
            the_font_enumerator = FontEnumerator()

        return the_font_enumerator.facenames()


    def font_fixed ( self, font_name ):
        """ Returns **True** if the font whose name is specified by *font_name*
            is a fixed (i.e. monospace) font. It returns **False** if
            *font_name* is a proportional font.
        """
        font = wx.Font( 10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_NORMAL, False, font_name )

        return ((font is not None) and (font.IsFixedWidth()))

    #-- GUI Toolkit Dependent Facet Definitions --------------------------------

    def color_facet ( self, *args, **facets ):
        import color_facet as cf

        return cf.WxColor( *args, **facets )


    def rgb_color_facet ( self, *args, **facets ):
        import rgb_color_facet as rgbcf

        return rgbcf.RGBColor( *args, **facets )


    def font_facet ( self, *args, **facets ):
        import font_facet as ff

        return ff.WxFont( *args, **facets )

    #-- 'EditorFactory' Factory Methods ----------------------------------------

    # Code:
    def code_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.code_editor as ce

        return ce.CodeEditor( *args, **facets )


    # Directory:
    def directory_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.directory_editor as de

        return de.DirectoryEditor( *args, **facets )


    # Drop (drag and drop target):
    def drop_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.drop_editor as de

        return de.DropEditor( *args, **facets )


    # Enum(eration):
    def enum_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.enum_editor as ee

        return ee.EnumEditor( *args, **facets )


    # File:
    def file_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.file_editor as fe

        return fe.FileEditor( *args, **facets )


    # Font:
    def font_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.font_editor as fe

        return fe.FontEditor( *args, **facets )


    # Grid:
    def grid_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.grid_editor as ge

        return ge.WxGridEditor( *args, **facets )


    # HTML:
    def html_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.html_editor as he

        return he.HTMLEditor( *args, **facets )


    # Image enum(eration):
    def image_enum_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.image_enum_editor as iee

        return iee.ImageEnumEditor( *args, **facets )


    # List:
    def list_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.list_editor as le

        return le.ListEditor( *args, **facets )


    # ListStr:
    def list_str_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.list_str_editor as lse

        return lse.ListStrEditor( *args, **facets )


    # Ordered set:
    def ordered_set_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.ordered_set_editor as ose

        return ose.OrderedSetEditor( *args, **facets )


    # Plot:
    def plot_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.plot_editor as pe

        return pe.PlotEditor( *args, **facets )


    # Tree:
    def tree_editor ( self, *args, **facets ):
        import facets.ui.wx.editors.tree_editor as te

        return te.TreeEditor( *args, **facets )

    #-- Create GUI Toolkit Neutral Common Controls -----------------------------

    def create_control ( self, parent, tab_stop = False, handle_keys = False ):
        """ Returns an adapted control suitable for use as a base for creating
            custom controls.
        """
        style = wx.FULL_REPAINT_ON_RESIZE

        if tab_stop:
            style |= wx.TAB_TRAVERSAL

        if handle_keys:
            style |= wx.WANTS_CHARS

        control = WxControl( as_toolkit_control( parent ), -1, style = style )
        control.accepts_focus = tab_stop or handle_keys

        return control_adapter( control )


    def create_frame ( self, parent, style, title = '' ):
        """ Returns an adapted top-level window frame/dialog control. The
            *style* parameter is a set containing values from the following
            list:
            - 'frame':      The result should be a normal top-level window.
            - 'dialog':     The result should be a dialog window.
            - 'resizable':  The window should have a resize border.
            - 'simple':     The window should have a simple border.
            - 'none':       The window should not have any border.
            - 'min_max':    The window should have minimize/maximize buttons.
            - 'float':      The window should float on top of its parent.
            - 'no_taskbar': The window should not appear on the system taskbar.
        """
        flags = (wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        if 'frame' in style:
            flags |= (wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)
        elif 'min_max' in style:
            flags |= (wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)

        if 'resizable' in style:
            flags |= wx.RESIZE_BORDER
        elif 'simple' in style:
            flags = wx.SIMPLE_BORDER
        elif 'none' in style:
            flags = wx.BORDER_NONE

        if 'float' in style:
            flags |= wx.FRAME_FLOAT_ON_PARENT

        if 'no_taskbar' in style:
            flags |= wx.FRAME_NO_TASKBAR

        klass = wx.Dialog
        if 'dialog' not in style:
            klass  = wx.Frame
            flags |= wx.CLIP_CHILDREN

        return control_adapter(
            klass( as_toolkit_control( parent ), -1, title, style = flags )
        )


    def create_panel ( self, parent ):
        """ Returns an adapted panel control.
        """
        return control_adapter(
            FacetsUIPanel( as_toolkit_control( parent ), -1,
                           style = wx.CLIP_CHILDREN )
        )


    def create_scrolled_panel ( self, parent ):
        """ Returns a panel that can scroll its contents.
        """
        tuisp = FacetsUIScrolledPanel( as_toolkit_control( parent ) )
        tuisp.SetScrollRate( 1, 1 )

        return control_adapter( tuisp )


    def create_label ( self, parent, label = '', align = 'left' ):
        """ Returns an adapted label control.
        """
        return control_adapter(
            wx.StaticText( as_toolkit_control( parent ), -1, label,
                           style = horizontal_alignment_styles[ align ] )
        )


    def create_text_input ( self, parent, read_only = False, password = False,
                                  handle_enter = False, multi_line = False,
                                  align = 'left' ):
        """ Returns an adapted single or mutli line text input control.
        """
        style = input_horizontal_alignment_styles[ align ]

        if read_only:
            style |= wx.TE_READONLY

        if password:
            style |= wx.TE_PASSWORD

        if handle_enter:
            style |= wx.TE_PROCESS_ENTER

        if multi_line:
            style |= wx.TE_MULTILINE

        if read_only and multi_line:
            style |= wx.NO_BORDER

        return control_adapter(
            wx.TextCtrl( as_toolkit_control( parent ), -1, '', style = style )
        )


    def create_button ( self, parent, label = '' ):
        """ Returns an adapted button.
        """
        return control_adapter(
            wx.Button( as_toolkit_control( parent ), -1, label )
        )


    def create_checkbox ( self, parent, label = '' ):
        """ Returns an adapted checkbox control.
        """
        return control_adapter(
            wx.CheckBox( as_toolkit_control( parent ), -1, label )
        )


    def create_combobox ( self, parent, editable = False ):
        """ Returns an adapted wx.Choice or wx.ComboBox control.
        """
        if editable:
            return control_adapter(
                wx.ComboBox( as_toolkit_control( parent ), -1, '',
                             wx.Point( 0, 0 ), wx.Size( -1, -1 ), [],
                             style = wx.CB_DROPDOWN )
            )

        return control_adapter(
            wx.Choice( as_toolkit_control( parent ), -1,
                       wx.Point( 0, 0 ), wx.Size( -1, -1 ), [] )
        )


    def create_separator ( self, parent, is_vertical = True ):
        """ Returns an adapted separator line control.
        """
        return control_adapter(
            wx.StaticLine( as_toolkit_control( parent ), -1,
                           style = separator_map[ is_vertical ] )
        )

    #-- Create GUI Toolkit Neutral Common Layout Managers ----------------------

    def create_layout ( self, layout ):
        """ Creates a new GUI toolkit neutral layout manager for the specified
            GUI toolkit specific layout manager or implementor of the
            IAbstractLayout interface.
        """
        return layout_adapter( layout )


    def create_box_layout ( self, is_vertical = True, align = '' ):
        """ Returns a new GUI toolkit neutral 'box' layout manager.
        """
        return layout_adapter(
            wx.BoxSizer( orientation_map[ is_vertical ] ), is_vertical
        )


    def create_groupbox_layout ( self, is_vertical, parent, label, owner ):
        """ Returns a new GUI toolkit neutral vertical layout manager for a
            groupbox.
        """
        gbox       = wx.StaticBox( as_toolkit_control( parent ), -1, label )
        gbox.owner = owner
        return (
            None,
            layout_adapter(
                wx.StaticBoxSizer( gbox, orientation_map[ is_vertical ] ),
                is_vertical
            )
        )


    def create_flow_layout ( self, is_vertical ):
        """ Returns a new GUI toolkit neutral horizontal or vertical flow
            layout.
        """
        from facets.ui.flow_layout import FlowLayout

        return self.create_layout( FlowLayout( is_vertical = is_vertical ) )


    def create_grid_layout ( self, rows = 0, columns = 1, v_margin = 0,
                                   h_margin = 0 ):
        """ Returns a new GUI toolkit neutral grid layout manager which
            supports a (rows,columns) sized grid, with each grid element
            having (v_margin,h_margin) pixels of space around it.

            If rows is 0, the number of rows is not predefined, but will be
            determined by the actual number of controls added to the layout.
        """
        return layout_adapter(
            wx.FlexGridSizer( rows, columns, v_margin, h_margin )
        )

    #-- Create GUI Toolkit Neutral Miscellaneous Objects -----------------------

    def create_bitmap ( self, buffer, width, height ):
        """ Create a GUI toolkit specific bitmap of the specified width and
            height from the specified buffer 'bgra' data in row order.
        """
        data  = reshape( fromstring( buffer, uint8 ), ( height, width, 4 ) )
        image = wx.EmptyImage( width, height )
        image.SetData( data[ :, :, 2::-1 ].tostring() )
        image.SetAlphaData( data[ :, :, 3 ].tostring() )

        return wx.BitmapFromImage( image, 32 )


    def create_timer ( self, milliseconds, handler ):
        """ Creates and returns a timer which will call *handler* every
            *milliseconds* milliseconds. The timer can be cancelled by calling
            the returned object with no arguments.
        """
        return WxTimer( milliseconds, handler )

    #-- GUI Toolkit Neutral Adapter Methods ------------------------------------

    def adapter_for ( self, item ):
        """ Returns the correct type of adapter (control or layout) for the
            specified item.
        """
        if isinstance( item, wx.Window ):
            return adapted_control( item )

        return adapted_layout( item )


    def control_adapter_for ( self, control ):
        """ Returns the GUI toolkit neutral adapter for the specified GUI
            toolkit specific control.
        """
        return adapted_control( control )


    def layout_adapter_for ( self, layout ):
        """ Returns the GUI toolkit neutral adapter for the specified GUI
            toolkit specific layout manager.
        """
        return adapted_layout( layout )

#-------------------------------------------------------------------------------
#  'WxControl' class:
#-------------------------------------------------------------------------------

class WxControl ( wx.PyWindow ):

    # Debug:
    def __init__ ( self, *args, **kw ):
        from facets.extra.helper.debug import created_from; created_from(self,2)

        super( WxControl, self ).__init__( *args, **kw )

    def AcceptsFocus ( self ):
        """ Indicate that we are a static control that does not accept focus.
        """
        return self.accepts_focus

#-------------------------------------------------------------------------------
#  'WxTimer' class:
#-------------------------------------------------------------------------------

class WxTimer ( wx.Timer ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, milliseconds, handler ):
        """ Initializes the object.
        """
        super( WxTimer, self ).__init__()

        self._handler = handler
        self.Start( milliseconds )


    def __call__ ( self ):
        """ Stop the timer.
        """
        self.Stop()


    def Notify ( self ):
        """ Notify the handler that the timer has 'popped'.
        """
        self._handler()

#-------------------------------------------------------------------------------
#  'DragHandler' class:
#-------------------------------------------------------------------------------

class DragHandler ( HasPrivateFacets ):
    """ Handler for drag events.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The UI associated with the drag handler
    ui = Instance( UI )

    # The wx control associated with the drag handler
    control = Instance( wx.Window )

    #-- Drag and Drop Event Handlers -------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles a Python object being dropped on the window.
        """
        return self._drag_event( 'dropped_on', x, y, data, drag_result )


    def wx_drag_over ( self, x, y, data, drag_result ):
        """ Handles a Python object being dragged over the tree.
        """
        return self._drag_event( 'drag_over', x, y, data, drag_result )


    def wx_drag_leave ( self, data ):
        """ Handles a dragged Python object leaving the window.
        """
        return self._drag_event( 'drag_leave' )


    def _drag_event ( self, suffix, x = None, y = None, data = None,
                                    drag_result = None ):
        """ Handles routing a drag event to the appropriate handler.
        """
        control = self.control
        handler = self.ui.handler
        method  = None

        owner   = getattr( control, '_owner', None )
        if owner is not None:
            method = getattr( handler, 'on_%s_%s' % ( owner.get_id(), suffix ),
                              None )

        if method is None:
            method = getattr( handler, 'on_%s' % suffix, None )

        if method is None:
            return wx.DragNone

        if x is None:
            result = method( self.ui.info, owner )
        else:
            result = method( self.ui.info, owner, x, y, data, drag_result )
        if result is None:
            result = drag_result
        return result

#-------------------------------------------------------------------------------
#  'Application' class:
#-------------------------------------------------------------------------------

class Application ( wx.PySimpleApp ):
    """ Modal window that contains a stand-alone application.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, app_info ):
        """ Initializes the object.
        """
        self.app_info = app_info

        wx.InitAllImageHandlers()

        if app_info.filename != '':
            super( Application, self ).__init__( 1, app_info.filename )
        else:
            super( Application, self ).__init__()

        self.MainLoop()


    def OnInit ( self ):
        """ Handles application initialization.
        """
        app_info    = self.app_info
        app_info.ui = app_info.view.ui(
            app_info.context,
            kind       = app_info.kind,
            handler    = app_info.handler,
            id         = app_info.id,
            scrollable = app_info.scrollable,
            args       = app_info.args
        )

        return True

#-- GUI toolkit specifc extensions to GUI toolkit neutral classes --------------

#-------------------------------------------------------------------------------
#  'WxEditor' class:
#-------------------------------------------------------------------------------

class WxEditor ( Category, Editor ):
    """ Defines the extensions needed to make the generic Editor class specific
        to wxPython.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Style for embedding control in a sizer:
    layout_style = Int( wx.EXPAND )

    # The maximum extra padding that should be allowed around the editor:
    border_size = Int( 4 )

#-- EOF ------------------------------------------------------------------------
