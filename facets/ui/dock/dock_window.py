"""
This package implements a 'dockable' window component that allows child windows
to be reorganized within the DockWindow using drag and drop. The component also
allows multiple sub-windows to occupy the same sub-region of the DockWindow, in
which case each sub-window appears as a separate notebook-like tab within the
region.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt

from facets.api \
    import HasFacets, HasPrivateFacets, HasStrictFacets, Int, Instance, Tuple, \
           Any, Str, List, Bool, Range, Property, View, HGroup, VGroup, Item,  \
           UItem, Button, Handler, Control, GridEditor, StringGridEditor,      \
           error, toolkit, property_depends_on, spring

from facets.core.facet_db \
    import facet_db

from facets.core.facets_env \
    import facets_env

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.menu \
    import Menu, Action, ActionGroup, Separator

from facets.ui.pyface.message_dialog \
    import error as warning

from facets.ui.pyface.timer.api \
    import do_after, do_later

from dock_constants \
    import features, DockStyle, no_dock_info

from dock_control \
    import DockControl

from dock_sizer \
    import DockSizer

from dock_region \
    import DockRegion

from dock_splitter \
    import DockSplitter

from dock_window_handler \
    import DockWindowHandler

from dock_window_theme \
    import DockWindowTheme

from dock_window_theme_factory \
    import theme_factory

from idock_ui_provider \
    import IDockUIProvider

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The DockWindow layout templates that can be applied:
Templates = {
    '2_0': ( ( 1, 1 ), ),
    '2_1': ( 1, 1 ),
    '3_0': ( ( 1, 1, 1 ), ),
    '3_1': ( 2, ( 1, 1, 1 ) ),
    '3_2': ( ( 1, 1, 1 ), 2 ),
    '3_3': ( ( 2, ( 1, 1, 1 ) ), ),
    '3_4': ( ( ( 1, 1, 1 ), 2 ), ),
    '3_5': ( 1, 1, 1 ),
    '4_0': ( ( 1, 1, 1 ), ( 1, 1, 1 ) ),
    '4_1': ( 2, ( 1, 1, 1, 1 ) ),
    '4_2': ( ( 1, 1, 1, 1 ), 2 ),
    '4_3': ( ( 2, ( 1, 1, 1, 1 ) ), ),
    '4_4': ( ( ( 1, 1, 1, 1 ), 2 ), ),
}

# The set of standard window sizes and their labels:
standard_sizes = (
    ( '640 x 480',              (  640,  480 ) ),
    ( '800 x 600',              (  800,  600 ) ),
    ( '1024 x 768',             ( 1024,  768 ) ),
    ( '1280 x 720 (HD 720)',    ( 1280,  720 ) ),
    ( '1366 x 768',             ( 1366,  768 ) ),
    ( '1440 x 900',             ( 1440,  900 ) ),
    ( '1600 x 1200',            ( 1600, 1200 ) ),
    ( '1920 x 1080 (HD 1080)',  ( 1920, 1080 ) ),
    ( '1920 x 1200',            ( 1920, 1200 ) ),
    ( '2560 x 1440',            ( 2560, 1440 ) ),
    ( None, None ),
    ( 'Top',                    ( 0.00, 0.00, 1.0, 0.5 ) ),
    ( 'Bottom',                 ( 0.00, 0.50, 1.0, 0.5 ) ),
    ( 'Left',                   ( 0.00, 0.00, 0.5, 1.0 ) ),
    ( 'Right',                  ( 0.50, 0.00, 0.5, 1.0 ) ),
    ( None, None ),
    ( 'Top left',               ( 0.00, 0.00, 0.5, 0.5 ) ),
    ( 'Top right',              ( 0.50, 0.00, 0.5, 0.5 ) ),
    ( 'Bottom left',            ( 0.00, 0.50, 0.5, 0.5 ) ),
    ( 'Bottom right',           ( 0.50, 0.50, 0.5, 0.5 ) ),
    ( 'Center',                 ( 0.25, 0.25, 0.5, 0.5 ) )
)

#-------------------------------------------------------------------------------
#  Custom actions:
#-------------------------------------------------------------------------------

class ResizeAction ( Action ):
    """ Action for resizing a window.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The size the window should be resized to as a tuple of the form:
    # ( Int dx, Int dy ) or ( Float x, Float y, Float dx, Float dy )
    size = Any

    # The action to take (override):
    action = 'on_resize'

#-------------------------------------------------------------------------------
#  DockWindow context menu:
#-------------------------------------------------------------------------------

min_max_action           = Action( name   = 'Maximize',
                                   action = 'on_min_max' )

undock_action            = Action( name   = 'Undock',
                                   action = 'on_undock' )

lock_action              = Action( name   = 'Lock layout',
                                   action = 'on_lock_layout',
                                   style  = 'toggle' )

layout_action            = Action( name   = 'Switch layout',
                                   action = 'on_switch_layout' )

manage_layouts_action    = Action( name   = 'Manage layouts...',
                                   action = 'manage_layouts' )

hide_action              = Action( name   = 'Hide',
                                   action = 'on_hide' )

show_action              = Action( name   = 'Show',
                                   action = 'on_show' )

select_theme_action      = Action( name   = 'Select theme...',
                                   action = 'select_theme' )

display_shell_action     = Action( name   = 'VIP Shell',
                                   action = 'on_display_shell' )

display_workbench_action = Action( name   = 'Workbench',
                                   action = 'on_display_workbench' )

display_monitor_action   = Action( name   = 'Instance Monitor',
                                   action = 'on_display_monitor' )

display_tools_action     = Action( name   = 'Tools',
                                   action = 'on_display_tools' )

display_fbi_action       = Action( name   = 'FBI',
                                   action = 'on_display_fbi' )

edit_action              = Action( name   = 'Edit properties...',
                                   action = 'on_edit' )

enable_features_action   = Action( name   = 'Show all',
                                   action = 'on_enable_all_features' )

disable_features_action  = Action( name   = 'Hide all',
                                   action = 'on_disable_all_features' )

screenshot_tab_action    = Action( name   = 'Capture tab',
                                   action = 'on_screenshot_tab' )

screenshot_group_action  = Action( name   = 'Capture group',
                                   action = 'on_screenshot_group' )

screenshot_window_action = Action( name   = 'Capture window',
                                   action = 'on_screenshot_window' )

screenshot_screen_action = Action( name   = 'Capture screen',
                                   action = 'on_screenshot_screen' )

screenshot_to_clipboard_action = Action( name   = 'Send capture to clipboard',
                                         action = 'on_screenshot_to_clipboard',
                                         style  = 'toggle' )

screenshot_to_tool_action      = Action( name   = 'Send capture to image tool',
                                         action = 'on_screenshot_to_tool',
                                         style  = 'toggle' )

#-------------------------------------------------------------------------------
#  'DockWindow' class:
#-------------------------------------------------------------------------------

class DockWindow ( HasPrivateFacets ):
    """ Defines the DockWindow control used to manage a collection of UI
        elements organized into user specified tab and splitter groups. The
        actual layout of the UI elements is performed by the DockWindow's
        associated DockSizer, which organizes the elements using a hierarchy of
        DockControl (UI element), DockRegion (tab group) and DockSection
        (splitter group) objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The (adapted) control being used as the DockWindow:
    control = Instance( Control )

    # The handler used to determine how certain events should be processed:
    handler = Any( DockWindowHandler() )

    # The 'extra' arguments to be passed to each handler call:
    handler_args = Tuple

    # Close the parent window if the DockWindow becomes empty:
    auto_close = Bool( False )

    # The maximum number of tabs the user is allowed to drag into a single
    # group (a value of 0 means there is no maximum):
    max_tabs = Range( 0, 25 )

    # The DockWindow graphical theme style information:
    theme = Instance( DockWindowTheme )

    # Default style for external objects dragged into the window:
    style = DockStyle

    # Return the sizer associated with the window:
    dock_sizer = Instance( DockSizer )

    # The list of all DockControls contained in the window:
    dock_controls = Property

    # The currently selected DockControl:
    selected = Instance( DockControl )

    # The id used to identify this DockWindow:
    id = Str

    # The list of DockWindowFeatures that apply to this DockWindow:
    features = List # ( DockWindowFeature subclass )

    # Should screen captures be sent to the clipboard (True) or image tool
    # (False)?
    capture_clipboard = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, parent, **facets ):
        """ Initializes the object.
        """
        super( DockWindow, self ).__init__( **facets )

        # Create the actual window:
        self.control = control = toolkit().create_control( parent )
        control.min_size = ( 20, 20 )

        # Set up the event handlers:
        control.set_event_handler(
            paint       = self.paint,
            size        = self.size,
            left_down   = self.left_down,
            left_up     = self.left_up,
            left_dclick = self.left_dclick,
            right_down  = self.right_down,
            right_up    = self.right_up,
            motion      = self.mouse_move,
            leave       = self.mouse_leave
        )

        # Set up the drag and drop handler:
        control.drop_target = self

        control().owner = self

        # Initialize the window background color:
        self._set_background_color()

        # fixme: We have to set up this listener manually here because the
        # @on_facet_set decorator doesn't seem to work if the facet has a
        # '_xxx_default' method defined...
        self.on_facet_set( self._theme_updated, 'theme.updated' )


    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            DockWindow.
        """
        self.capture_clipboard        = prefs.get( 'capture_clipboard', True )
        self.dock_sizer.max_structure = prefs.get( 'max_structure' )
        self.dock_sizer.set_structure( self.control, prefs.get( 'structure' ) )
        self.control.update()


    def save_prefs ( self ):
        """ Returns any user preference information associated with the
            DockWindow.
        """
        return {
            'capture_clipboard': self.capture_clipboard,
            'structure':         self.dock_sizer.get_structure(),
            'max_structure':     self.dock_sizer.max_structure
        }

    #-- Default Facet Values ---------------------------------------------------

    def _theme_default ( self ):
        return theme_factory.theme

    #-- Property Implementations -----------------------------------------------

    def _get_dock_controls ( self ):
        return self.dock_sizer.contents.get_controls()

    #-- Public Methods ---------------------------------------------------------

    def add_feature ( self, feature_class ):
        """ Adds a new DockWindowFeature class to the list of available
            features for this DockWindow. Returns True if the feature was added
            successfully, and False if the feature was already in the features
            list.
        """
        result = (feature_class not in self.features)
        if result:
            self.features.append( feature_class )

            # Mark the feature class as having been installed:
            if feature_class.state == 0:
                feature_class.state = 1

        return result


    def dock_window_empty ( self ):
        """ Notifies the DockWindow that its contents are empty.
        """
        self.handler.dock_window_empty( self )


    def set_cursor ( self, cursor = 'arrow' ):
        """ Sets the cursor to a specified cursor shape.
        """
        control        = self.control
        control.cursor = cursor

        if cursor == 'arrow':
            if self._mouse_capture:
                self._mouse_capture = control.mouse_capture = False
        elif not self._mouse_capture:
            if not control.mouse_capture:
                self._mouse_capture = control.mouse_capture = True
        else:
            # This seems to be a Qt'ism that we have to release then grab the
            # mouse capture to make the new cursor shape 'stick':
            control.mouse_capture = False
            control.mouse_capture = True


    def release_mouse ( self ):
        """ Releases ownership of the mouse capture.
        """
        if self._owner is not None:
            self._owner = None
            self._mouse_capture = self.control.mouse_capture = False


    def auto_layout ( self ):
        """ Automatically lay out the contents of the DockWindow using an
            appropriate layout algorithm chosen based upon the number of items
            contained in the window.
        """
        n = len( self.dock_sizer.contents.get_controls() )
        self.apply_layout( min( n, 5 ), 3 * (n == 3) )


    def apply_layout ( self, items, style ):
        """ Applies the layout specified by *items* and *style* to the current
            contents of the view. *Items* is a number in the range from 1 to 5,
            specifying the number of items in the layout (with 5 meaning "more
            than 4"). *style* is a small integer value describing the layout
            style to use for the specified number of items.
        """
        if items < 5:
            template = Templates.get( '%s_%d' % ( items, style ) )
        else:
            items = len( self.dock_sizer.contents.get_controls() )
            if style == 0:
                columns  = int( sqrt( items ) + 0.99 )
                template = []
                while items > 0:
                    columns = min( columns, items )
                    items  -= columns
                    template.append( ( 1, ) * (columns + 1) )

                template = tuple( template )
            else:
                template = ( ( ( 1, ) * items, 2 ),
                             ( 2, ( 1, ) * items ) )[ style & 1 ]
                if style >= 3:
                    template = ( template, )

        if template is not None:
            self.update_layout( template )


    def update_layout ( self, layout = None ):
        """ Updates the layout of the window. If *layout* is not None, it first
            applies the layout structure specified by *layout* to the window.
        """
        if layout is not None:
            self.dock_sizer.set_structure( self.control, layout )

        self.control.update()


    def manage_layouts ( self ):
        """ Allow the user to save, restore or delete layouts associated with
            this DockWindow.
        """
        if self.id != '':
            LayoutManager( dock_window = self ).edit_facets(
                parent = self.control
            )


    def select_theme ( self ):
        """ Allow the user to select a new DockWindow theme.
        """
        ThemeManager().edit_facets( parent = self.control )


    def min_max ( self, dock_control ):
        """ Minimizes/maximizes a specified DockControl.
        """
        dock_sizer = self.dock_sizer
        if dock_sizer is not None:
            dock_sizer.min_max( self.control, dock_control )
            self.update_layout()


    def feature_bar_popup ( self, dock_control ):
        """ Pops up the feature bar for a specified DockControl.
        """
        fb = self._feature_bar
        if fb is None:
            from feature_bar import FeatureBar

            self._feature_bar = fb = FeatureBar( parent = self.control )
            fb.on_facet_set( self._feature_bar_closed, 'completed' )

        fb.dock_control = dock_control
        fb.show()


    def _feature_bar_closed ( self ):
        fb = self._feature_bar
        fb.dock_control.feature_bar_closed()
        fb.hide()


    def close ( self ):
        """ Closes the dock window.  In this case, all event handlers are
            unregistered.  Other cleanup operations go here, but at the moment
            Linux (and other non-Windows platforms?) are less forgiving when
            things like event handlers aren't unregistered.
        """
        control = self.control
        control.unset_event_handler(
            paint       = self.paint,
            size        = self.size,
            left_down   = self.left_down,
            left_up     = self.left_up,
            left_dclick = self.left_dclick,
            right_down  = self.right_down,
            right_up    = self.right_up,
            motion      = self.mouse_move,
            leave       = self.mouse_leave
        )

        # Remove the drag and drop handler:
        control.drop_target = None

        # Discard the DockSizer:
        self.dock_sizer.close()
        self.dock_sizer = None

        # Delete the owner reference:
        del control().owner


    def paint ( self, event ):
        """ Handles repainting the window.
        """
        control = self.control
        g       = control.graphics.graphics_buffer()
        g.pen   = None
        g.brush = control.background_color
        dx, dy  = control.size
        g.draw_rectangle( 0, 0, dx, dy )

        dock_sizer = self.dock_sizer
        if isinstance( dock_sizer, DockSizer ) and (not dock_sizer.draw( g )):
            do_later( self.control.refresh )

        g.copy()


    def size ( self, event ):
        """ Handles the window being resized.
        """
        dock_sizer = self.dock_sizer
        if dock_sizer is not None:
            dx, dy = self.control.size
            dock_sizer.perform_layout( 0, 0, dx, dy )


    def left_down ( self, event ):
        """ Handles the left mouse button being pressed.
        """
        dock_sizer = self.dock_sizer
        if dock_sizer is not None:
            object = dock_sizer.object_at( event.x, event.y )
            if object is not None:
                self._owner                = object
                self.control.mouse_capture = True
                self._mouse_capture        = False
                object.mouse_down( event )


    def left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        window = self.control
        if self._owner is not None:
            self._mouse_capture = window.mouse_capture = False
            self._owner.mouse_up( event )
            self._owner = None

        # Check for the user requesting that the layout structure be reset:
        if event.shift_down:
            if event.control_down:
                # Check for the developer requesting a structure dump (DEBUG):
                if event.alt_down:
                    contents = self.dock_sizer.contents
                    if contents is not None:
                        import sys

                        contents.dump()
                        sys.stdout.flush()
                else:
                    self.dock_sizer.reset_structure( window )
                    self.update_layout()
            elif event.alt_down:
                self.dock_sizer.toggle_lock()
                self.update_layout()


    def left_dclick ( self, event ):
        """ Handles the left mouse button being double clicked.
        """
        dock_sizer = self.dock_sizer
        if dock_sizer is not None:
            object = dock_sizer.object_at( event.x, event.y, True )
            if isinstance( object, DockControl ):
                dockable = object.dockable
                if (((dockable is None) or
                     (dockable.dockable_dclick( object, event ) is False)) and
                    (object.style != 'fixed')):
                    self.min_max( object )
            elif isinstance( object, DockRegion ):
                self._owner = object
                self.control.mouse_capture = True
                self._mouse_capture        = False
                object.mouse_down( event )


    def right_down ( self, event ):
        """ Handles the right mouse button being pressed.
        """
        pass


    def right_up ( self, event ):
        """ Handles the right mouse button being released.
        """
        # If the context menu has been disabled globally, then don't display it:
        if not facets_env.menu:
            return

        dock_sizer = self.dock_sizer
        if dock_sizer is not None:
            object = dock_sizer.object_at( event.x, event.y, True )
            if object is not None:
                popup_menu      = None
                window          = self.control
                is_dock_control = isinstance( object, DockControl )

                if (is_dock_control and (object.dockable is not None) and
                    (event.shift_down or event.control_down or event.alt_down)):
                    self._menu_self = object.dockable
                    popup_menu = object.dockable.dockable_menu( object, event )

                if popup_menu is None:
                    self._menu_self = self
                    section         = self.dock_sizer.contents
                    is_splitter     = isinstance( object, DockSplitter )
                    self._object    = object
                    if is_splitter:
                        self._object = object = object.parent

                    group = object
                    if is_dock_control:
                        group = group.parent

                    if dock_sizer.is_maximizable():
                        min_max_action.name = 'Maximize'
                    else:
                        min_max_action.name = 'Restore'

                    min_max_action.enabled  = is_dock_control
                    undock_action.enabled   = (is_dock_control and
                                               (object.export != ''))
                    hide_action.enabled     = (is_splitter or object.visible)
                    show_action.enabled     = (self._hidden_group_for( group )
                                               is not None)
                    edit_action.enabled     = (not is_splitter)
                    controls                = section.get_controls( False )
                    lock_action.checked     = ((len( controls ) > 0) and
                                               controls[0].locked)
                    manage_layouts_action.enabled = (self.id != '')

                    feature_menu    = self._get_feature_menu()
                    resize_menu     = self._get_resize_menu()
                    screenshot_menu = self._get_screenshot_menu(
                        is_dock_control
                    )

                    menu_items = [
                        min_max_action,
                        undock_action,
                        Separator(),
                        feature_menu,
                        Separator(),
                        hide_action,
                        show_action,
                        Separator(),
                        lock_action,
                        layout_action,
                        manage_layouts_action,
                        Separator(),
                        select_theme_action,
                        Separator(),
                        edit_action,
                        Separator(),
                        resize_menu
                    ]

                    if facets_env.dev:
                        menu_items.extend( [
                            Separator(),
                            Menu(
                                display_shell_action,
                                display_workbench_action,
                                display_monitor_action,
                                display_tools_action,
                                display_fbi_action,
                                name = 'Display'
                            )
                        ] )

                    menu_items.extend( [
                        Separator(),
                        screenshot_menu
                    ] )

                    popup_menu = Menu( *menu_items, name = 'popup' )

                window.popup_menu( popup_menu.create_menu( window(), self ),
                                   event.x - 10, event.y - 10 )


    def mouse_move ( self, event ):
        """ Handles the mouse moving over the window.
        """
        if self._last_dock_control is not None:
            self._last_dock_control.reset_feature_popup()
            self._last_dock_control = None

        if self._owner is not None:
            self._owner.mouse_move( event )
        else:
            dock_sizer = self.dock_sizer
            if dock_sizer is not None:
                object = (self._object or
                          dock_sizer.object_at( event.x, event.y ))
                self._set_cursor( event, object )

                if object is not self._hover:
                    if self._hover is not None:
                        self._hover.hover_exit()

                    if object is not None:
                        object.hover_enter()
                        do_after( 200, self._hover_check )

                    self._hover = object

                # Handle feature related processing:
                if (isinstance( object, DockControl) and
                    object.feature_activate( event )):
                    self._last_dock_control = object


    def mouse_leave ( self, event ):
        """ Handles the mouse leaving the window.
        """
        if self._hover is not None:
            self._hover.hover_exit()
            self._hover = None

        self._set_cursor( event )


    def _set_cursor ( self, event, object = None ):
        """ Sets the cursor for a specified object.
        """
        if object is None:
            self.set_cursor()
        else:
            self.set_cursor( object.get_cursor( event ) )

    #-- Context menu action handlers -------------------------------------------

    def on_min_max ( self ):
        """ Handles the user asking for a DockControl to be maximized/restored.
        """
        self.min_max( self._object )
        self._object = None


    def on_undock ( self ):
        """ Handles the user requesting an element to be undocked.
        """
        self.handler.open_view_for( self._object, use_mouse = False )
        self._object = None


    def on_hide ( self ):
        """ Handles the user requesting an element to be hidden.
        """
        self._object.show( False )
        self._object = None


    def on_show ( self ):
        """ Handles the user requesting an element to be shown.
        """
        object, self._object = self._object, None
        if isinstance( object, DockControl ):
            object = object.parent

        self._hidden_group_for( object ).show( True )


    def on_switch_layout ( self ):
        """ Handles the user requesting that the current layout be switched.
        """
        self._object = None
        self.dock_sizer.reset_structure( self.control )
        self.update_layout()


    def on_lock_layout ( self ):
        """ Handles the user requesting that the layout be locked/unlocked.
        """
        self._object = None
        self.dock_sizer.toggle_lock()
        self.update_layout()


    def on_edit ( self, object = None ):
        """ Handles the user requesting to edit an item.
        """
        if object is None:
            object = self._object

        self._object = None
        control_info = ControlInfo( **object.get( 'name', 'user_name',
                                                  'style', 'user_style' ) )
        if control_info.edit_facets( parent = self.control ).result:
            name = control_info.name.strip()
            if name != '':
                object.name = name

            object.set( **control_info.get( 'user_name',
                                            'style', 'user_style' ) )
            self.update_layout()


    def on_enable_all_features ( self, action ):
        """ Enables all features.
        """
        global features

        self._object = None
        for feature in set( features + self.features ):
            if (feature.feature_name != '') and (feature.state != 1):
                feature.toggle_feature( action )


    def on_disable_all_features ( self, action ):
        """ Disables all features.
        """
        global features

        self._object = None
        for feature in set( features + self.features ):
            if (feature.feature_name != '') and (feature.state == 1):
                feature.toggle_feature( action )


    def on_toggle_feature ( self, action ):
        """ Toggles the enabled/disabled state of the action's associated
            feature.
        """
        self._object = None
        action._feature.toggle_feature( action )


    def on_screenshot_tab ( self, action ):
        """ Copies of a screenshot of the current tab to the currently selected
            target.
        """
        do_later( self._process_capture, '' )


    def on_screenshot_group ( self, action ):
        """ Copies of a screenshot of the DockWindow to the currently selected
            target.
        """
        do_later( self._process_capture, '.parent' )


    def on_screenshot_window ( self, action ):
        """ Copies of a screenshot of the current application window to the
            currently selected target.
        """
        do_later( self._process_capture, '.root_parent' )


    def on_screenshot_screen ( self, action ):
        """ Copies of a screenshot of the screen to the currently selected
            target.
        """
        do_later( self._process_capture )


    def on_screenshot_to_clipboard ( self, action ):
        """ Sets up to send screen captures to the clipboard.
        """
        self.capture_clipboard = True
        self._object           = None


    def on_screenshot_to_tool ( self, action ):
        """ Sets up to send screen captures to the image tool.
        """
        self.capture_clipboard = False
        self._object           = None


    def on_select_theme ( self, name ):
        """ Sets the theme specified by *name* as the new DockWindow theme to
            use.
        """
        global theme_factory

        theme_factory.name = name
        self._object       = None


    def on_display_shell ( self, action ):
        """ Displays a VIP Shell window.
        """
        from facets.extra.tools.vip_shell import VIPShell

        VIPShell(
            name   = 'Developer VIP Shell',
            values = { 'object': self._object }
        ).edit_facets()
        self._object = None


    def on_display_workbench ( self, action ):
        """ Displays a Workbench window.
        """
        from facets.extra.tools.workbench import Workbench

        Workbench().edit_facets()
        self._object = None


    def on_display_monitor ( self, action ):
        """ Displays an Instance Monitor window.
        """
        from facets.extra.tools.instance_monitor import InstanceMonitor

        InstanceMonitor().edit_facets()
        self._object = None


    def on_display_tools ( self, action ):
        """ Displays a tools window.
        """
        from facets.extra.tools.tools import tools

        tools( object = self._object )
        self._object = None


    def on_display_fbi ( self, action ):
        """ Displays an FBI debugger window.
        """
        from facets.extra.helper.fbi import FBI

        FBI().tools.activate()
        self._object = None


    def on_resize ( self, action ):
        """ Resizes the window to the requested size (and optional position).
        """
        # Get the control that will be resized:
        control      = self._object.control.root_parent
        self._object = None

        # We use the frame bounds, since that includes the title bar and resize
        # widgets. But we have to also calculate the size of the frame controls
        # because when we resize/position the control, we have to do so in terms
        # of the client area, which does not include the frame size:
        cx, cy, cdx, cdy = control.frame_bounds
        bx, by, bdx, bdy = control.bounds
        fx, fy, fdx, fdy = bx - cx, by - cy, cdx - bdx, cdy - bdy

        # Find the hardware display that contains the largest part of the
        # window:
        max_size = -1
        info     = toolkit().screen_info()
        for sx, sy, sdx, sdy in info:
            tx, ty, tdx, tdy = cx, cy, cdx, cdy
            if cx < sx:
                tdx = max( 0, tdx - (sx - tx) )
                tx  = sx

            if cy < sy:
                tdy = max( 0, tdy - (sy - ty) )
                ty  = sy

            size = (max( 0, (min( sx + sdx, tx + tdx ) - tx) ) *
                    max( 0, (min( sy + sdy, ty + tdy ) - ty) ))
            if size > max_size:
                max_size = size
                screen   = ( sx, sy, sdx, sdy )

        sx, sy, sdx, sdy = screen
        if len( action.size ) == 2:
            # An absolute size was selected:
            cdx, cdy = action.size
            if (cdx > sdx) or (cdy > sdy):
                # If the new size won't fit on the current hardware display for
                # the control, find the first display it will fit on:
                for sx, sy, sdx, sdy in info:
                    if (cdx <= sdx) and (cdy <= sdy):
                        cx, cy = sx, sy

                        break

            # Set the new control size and position, making sure the control
            # fits completely on the selected display:
            control.bounds = (
                fx  + max( sx, min( cx, sx + sdx - cdx ) ),
                fy  + max( sy, min( cy, sy + sdy - cdy ) ),
                cdx - fdx,
                cdy - fdy
            )
        else:
            # A size relative to the current display was selected, so resize
            # and position the control using the fractional values selected:
            x, y, dx, dy   = action.size
            control.bounds = (
                sx + fx + int( x * sdx ),
                sy + fy + int( y * sdy ),
                int( dx * sdx ) - fdx,
                int( dy * sdy ) - fdy
            )


    #-- DockWindow User Preference Database Methods ----------------------------

    def _get_feature_menu ( self ):
        """ Returns the 'Features' sub_menu.
        """
        global features

        enable_features_action.enabled = disable_features_action.enabled = False
        all_features = set( features + self.features )
        for feature in all_features:
            if feature.feature_name != '':
                if feature.state == 1:
                    disable_features_action.enabled = True
                    if enable_features_action.enabled:
                        break
                else:
                    enable_features_action.enabled = True
                    if disable_features_action.enabled:
                        break

        actions = []
        for feature in all_features:
            if feature.feature_name != '':
                actions.append( Action( name     = feature.feature_name,
                                        action   = 'on_toggle_feature',
                                        _feature = feature,
                                        style    = 'toggle',
                                        checked  = (feature.state == 1) ) )

        if len( actions ) > 0:
            actions.sort( lambda l, r: cmp( l.name, r.name ) )
            actions[0:0] = [ Separator() ]

        return Menu(
            name = 'Features',
            *([ enable_features_action, disable_features_action ] + actions)
        )


    def _get_resize_menu ( self ):
        """ Returns the 'Resize' sub-menu.
        """
        sdx = sdy = 0
        for x, y, dx, dy in toolkit().screen_info():
            sdx = max( sdx, dx )
            sdy = max( sdy, dy )

        actions = []
        for name, size in standard_sizes:
            if name is None:
                actions.append( Separator() )
            else:
                action = ResizeAction( name = name, size = size )
                if len( size ) == 2:
                    dx, dy         = size
                    action.enabled = ((dx <= sdx) and (dy <= sdy))

                actions.append( action )

        return Menu( name = 'Resize', *actions )


    def _get_screenshot_menu ( self, is_dock_control ):
        """ Returns the menu used to create screen shots of the associated
            DockWindow, tab or containing window.
        """
        screenshot_tab_action.enabled          = is_dock_control
        screenshot_to_clipboard_action.checked = self.capture_clipboard
        screenshot_to_tool_action.checked      = not self.capture_clipboard

        return Menu(
            ActionGroup(
                screenshot_tab_action,
                screenshot_group_action,
                screenshot_window_action,
                screenshot_screen_action
            ),
            Separator(),
            ActionGroup(
                screenshot_to_clipboard_action,
                screenshot_to_tool_action
            ),
            name = 'Screen capture'
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _theme_updated ( self ):
        """ Handles the theme being changed or updated.
        """
        control = self.control
        if control is not None:
            self._set_background_color()
            self.dock_sizer.reset_appearance()
            self.update_layout()


    def _dock_sizer_set ( self, old, new ):
        """ Handles the 'dock_sizer' facet being changed by linking the
            underlying toolkit specific control and layout objects together.
        """
        if old is not None:
            old.dock_window = None

        if new is not None:
            new.dock_window = self
            self.control.layout = toolkit().layout_adapter_for( new )
        else:
            self.control.layout = None


    def _selected_set ( self, old, new ):
        """ Handles the 'selected' item being changed.
        """
        if old is not None:
            old.selected = False

        if new is not None:
            new.selected = True

    #-- Drag and Drop Event Handlers: ------------------------------------------

    def drag_drop ( self, event ):
        """ Handles an object being dropped on the window.
        """
        data = event.object
        if (isinstance( data, DockControl ) or
            (isinstance( data, HasFacets ) and
             data.has_facets_interface( IDockUIProvider ))):
            window    = self.control
            dock_info = self._dock_info

            # See the 'drag_leave' method for an explanation of this code:
            if dock_info is None:
                dock_info = self._leave_info

            dock_info.draw( window )
            self._dock_info = None
            try:
                control = self.handler.dock_control_for(
                                       *(self.handler_args + ( window, data )) )
                dock_info.dock( control, window )
                event.result = event.request

                return
            except:
                warning( window,
                         "An error occurred while attempting to add an item of "
                         "type '%s' to the window." % data.__class__.__name__,
                         title = 'Cannot add item to window' )

        # Indicate that we don't handle the drag object:
        event.result = 'ignore'


    def drag_move ( self, event ):
        """ Handles an object being dragged over the control.
        """
        if event.has_object:
            x, y, data  = event.x, event.y, event.object
            ui_provider = (isinstance( data, HasFacets ) and
                           data.has_facets_interface( IDockUIProvider ))
            if ui_provider or isinstance( data, DockControl ):
                if (ui_provider and (not self.handler.can_drop(
                                           *(self.handler_args + ( data, )) ))):
                    event.result = event.request

                    return

                # Check to see if we are in 'drag mode' yet:
                cur_dock_info = self._dock_info
                if cur_dock_info is None:
                    cur_dock_info = no_dock_info()
                    if isinstance( data, DockControl ):
                        self._dock_size = data.tab_width
                    else:
                        self._dock_size = 80

                # Get the window and DockInfo object associated with the event:
                window          = self.control
                self._dock_info = dock_info = self.dock_sizer.dock_info_at(
                                                  x, y, self._dock_size, False )

                # If the DockInfo has changed, then update the screen:
                if ((cur_dock_info.kind != dock_info.kind)         or
                    (cur_dock_info.region is not dock_info.region) or
                    (cur_dock_info.bounds != dock_info.bounds)):

                    # Erase the old region:
                    cur_dock_info.draw( window )

                    # Draw the new region:
                    dock_info.draw( window )

                event.result = event.request

                return

            # Handle the case of dragging a normal object over a feature enabled
            # tab:
            self._check_drop_on_feature( x, y, data )

        # Indicate that we don't handle the drag object:
        event.result = 'ignore'


    def drag_leave ( self, event ):
        """ Handles a dragged object leaving the window.
        """
        if self._dock_info is not None:
            self._dock_info.draw( self.control )

            # fixme: Is this code needed anymore?
            # Save the current '_dock_info' in '_leave_info' because under
            # Linux the drag and drop code sends a spurious 'drag_leave' event
            # immediately before a 'dropped_on' event, so we need to remember
            # the '_dock_info' value just in case the next event is
            # 'dropped_on':
            self._leave_info, self._dock_info = self._dock_info, None

    #-- Pyface Menu Interface --------------------------------------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        pass


    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a tool bar item to the tool bar being constructed.
        """
        pass


    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        return True


    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return True


    def perform ( self, action_object ):
        """ Performs the action described by a specified Action object.
        """
        action = action_object.action
        if action[:5] == 'self.':
            eval( action, globals(), { 'self': self._menu_self } )
        else:
            method = getattr( self, action )
            try:
                method()
            except:
                method( action_object )

    #-- Private Methods --------------------------------------------------------

    def _set_background_color ( self ):
        """ Sets the correct background color for the control based on the
            color specified by the current theme.
        """
        theme = self.theme
        if theme.use_theme_color:
            color = theme.background_color
            if color is None:
                color = theme.tab.image_slice.bg_color
        else:
            color = self.control.parent.background_color

        self.control.background_color = color


    def _hidden_group_for ( self, group ):
        """ Finds the first group with any hidden items (if any).
        """
        while True:
            if group is None:
                return None

            if len( group.contents ) > len( group.visible_contents ):
                return group

            group = group.parent


    def _check_drop_on_feature ( self, x, y, data ):
        """ Checks whether the control has a feature which can accept the
            specified data and activates the feature popup if the pointer is
            over the feature 'trigger'.
        """
        if self.dock_sizer is not None:
            object = self.dock_sizer.object_at( x, y )
            ldc    = self._last_dock_control
            if (ldc is not None) and (ldc is not object):
                ldc.reset_feature_popup()

            self._last_dock_control = object

            if isinstance( object, DockControl ):
                event = FakeEvent( x = x, y = y, object = self.control )
                object.feature_activate( event, data )


    def _hover_check ( self ):
        """ Checks to see if the mouse pointer is still hovering over an item.
        """
        hover = self._hover
        if hover is not None:
            sx, sy = self.control.screen_position
            mx, my = self.control.mouse_position
            if self.dock_sizer.object_at( mx - sx, my - sy ) is hover:
                do_after( 200, self._hover_check )
            else:
                hover.hover_exit()
                self._hover = None


    def _process_capture ( self, target = None ):
        """ Processes *image* by sending it either to the system clipboard or to
            the Facets image tool.
        """
        if target is None:
            image = toolkit().screen().image
        else:
            image = eval( 'self._object.control%s.image' % target )

        self._object = None
        if self.capture_clipboard:
            toolkit().clipboard().image = image
        else:
            from facets.tools.image_tool import ImageTool

            ImageTool().image = image

#-------------------------------------------------------------------------------
#  'FakeEvent' class:
#-------------------------------------------------------------------------------

class FakeEvent ( HasStrictFacets ):

    #-- Facet Definitions ------------------------------------------------------

    x = Int
    y = Int

    # fixme: This probably isn't right...
    object = Any

#-------------------------------------------------------------------------------
#  'LayoutName' class:
#-------------------------------------------------------------------------------

class LayoutName ( Handler ):
    """ The view/handler used to prompt the user for a unique layout name.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name the user wants to assign to the layout:
    name = Str

    # The list of currently assigned names:
    names = List( Str )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'name', label = 'Layout name' ),
        title   = 'Save Layout',
        kind    = 'modal',
        buttons = [ 'OK', 'Cancel' ]
    )

    #-- Public Methods ---------------------------------------------------------

    def close ( self, info, is_ok ):
        """ Handles a request to close a dialog-based user interface by the
            user.
        """
        if is_ok:
            name = info.object.name.strip()
            if name == '':
                warning( info.ui.control, 'No name specified',
                         title = 'Save Layout Error' )
                return False

            if name in self.names:
                return error( message = '%s is already defined. Replace?' %
                                        name,
                              title   = 'Save Layout Warning',
                              parent  = info.ui.control )

        return True

#-------------------------------------------------------------------------------
#  'LayoutManagerAdapter' class:
#-------------------------------------------------------------------------------

class LayoutManagerAdapter ( GridAdapter ):
    """ Adapts a list of layout names for use with the GridEditor.
    """

    columns = [ ( 'Name', 'name' ) ]

    def name_content ( self ):
        return self.item

    def name_sorter ( self ):
        return lambda l, r: cmp( l, r )

    def double_clicked ( self ):
        self.object.restore = True

#-------------------------------------------------------------------------------
#  'LayoutManager' class:
#-------------------------------------------------------------------------------

class LayoutManager ( HasPrivateFacets ):
    """ Allow the user to manage the layouts associated with a particular
        DockWindow.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The DockWindow this is a layout manager for:
    dock_window = Instance( DockWindow )

    # The 'id' used to identify the DockWindow's associated layouts:
    id = Str

    # The actual name that will be used (minus leading/trailing blanks):
    actual_name = Property

    # The name of the current layout:
    name = Str

    # The names of the layouts associated with the DockWindow:
    names = List # ( Str )

    # Mapping from layout name to layout structure:
    layouts = Any # Dict

    # Event fired when the user wants to save a new layout:
    save = Button( 'Save' )

    # Event fired when the user wants to restore the currently selected layout:
    restore = Button( 'Restore' )

    # Event fired when the user wants to delete the currently selected layout:
    delete = Button( 'Delete' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'name' ),
            group_theme = '#themes:tool_options_group'
        ),
        VGroup(
            UItem( 'names',
                   editor = GridEditor(
                       adapter     = LayoutManagerAdapter,
                       operations  = [ 'sort' ],
                       selected    = 'name',
                       show_titles = False
                   )
            ),
            group_theme = '#themes:tool_options_group'
        ),
        HGroup(
            spring,
            UItem( 'save',
                   enabled_when = "(actual_name != '') and "
                                  "(actual_name not in names)",
                   tooltip = 'Click to save the current layout using the '
                             'specified name'
            ),
            UItem( 'restore',
                   enabled_when = 'actual_name in names',
                   tooltip = 'Click to restore the currently selected layout'
            ),
            UItem( 'delete',
                   enabled_when = 'actual_name in names',
                   tooltip = 'Click to delete the currently selected layout'
            ),
            group_theme = '#themes:toolbar_group'
        ),
        title  = 'Manage Layouts',
        id     = 'facets.ui.dock.dock_window.LayoutManager',
        width  = 0.20,
        height = 0.33
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'name' )
    def _get_actual_name ( self ):
        return self.name.strip()

    #-- Facet Default Values ---------------------------------------------------

    def _id_default ( self ):
        return self.dock_window.id


    def _names_default ( self ):
        return self.layouts.keys()


    def _layouts_default ( self ):
        result = {}
        db     = self._dw_db()
        if db is not None:
            result = db.get( self.id, {} )
            db.close()

        return result

    #-- Facet Event Handlers ---------------------------------------------------

    def _save_set ( self ):
        """ Handles the 'save' event being fired.
        """
        ds = self.dock_window.dock_sizer
        self.layouts[ self.actual_name ] = ds.get_structure()
        self.names.append( self.actual_name )
        self._save_layouts()


    def _restore_set ( self ):
        """ Handles the 'restore' event being fired.
        """
        dw = self.dock_window
        dw.dock_sizer.set_structure(
            dw.control, self.layouts[ self.actual_name ]
        )
        dw.update_layout()


    def _delete_set ( self ):
        """ Handles the 'delete' event being fired.
        """
        del self.layouts[  self.actual_name ]
        self.names.remove( self.actual_name )
        self._save_layouts()

    #-- Private Methods --------------------------------------------------------

    def _save_layouts ( self ):
        """ Saves the current layouts to the DockWindow FacetDB.
        """
        db = self._dw_db( mode = 'c' )
        if db is not None:
            db[ self.id ] = self.layouts
            db.close()


    def _dw_db ( self, mode = 'r' ):
        """ Returns the DockWindow FacetDB opened in the mode specifed by
            'mode'.
        """
        return facet_db( 'dock_window', mode )

#-------------------------------------------------------------------------------
#  'ThemeManager' class:
#-------------------------------------------------------------------------------

class ThemeManager ( HasPrivateFacets ):
    """ Allows the user to select the theme applied to the DockWindow.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of all available themes:
    themes = List # ( Str )

    # The currently selected theme:
    theme = Str

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'themes', editor = StringGridEditor( selected = 'theme' ) ),
        title  = 'Select Theme',
        id     = 'facets.ui.dock.dock_window.ThemeManager',
        width  = 0.15,
        height = 0.50
    )

    #-- Facet Default Values ---------------------------------------------------

    def _themes_default ( self ):
        global theme_factory

        return theme_factory.themes


    def _theme_default ( self ):
        global theme_factory

        return theme_factory.name

    #-- Facet Event Handlers ---------------------------------------------------

    def _theme_set ( self ):
        """ Handles the 'theme' facet being changed.
        """
        global theme_factory

        theme_factory.name = self.theme

#-------------------------------------------------------------------------------
#  'ControlInfo' class:
#-------------------------------------------------------------------------------

class ControlInfo ( HasPrivateFacets ):
    """ A class to allow the user to edit the properties of an item displayed in
        a DockWindow.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name to be edited:
    name = Str

    # Has the user set the name of the control?
    user_name = Bool( False )
    id        = Str

    # The style of drag bar/tab to use:
    style = DockStyle

    # Has the user set the style for this control?
    user_style = Bool( False )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        VGroup(
            Item( 'name',       label = 'Label', width = 100 ),
            Item( 'user_name',  label = 'Remember' ),
            Item( 'style',      width = 101 ),
            Item( 'user_style', label = 'Remember' ),
            columns     = 2,
            group_theme = '#themes:tool_options_group'
        ),
        title   = 'Edit properties',
        kind    = 'modal',
        buttons = [ 'OK', 'Cancel' ]
    )

#-- EOF ------------------------------------------------------------------------
