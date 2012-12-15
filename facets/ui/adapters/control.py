"""
Defines an abstract Control base class that each GUI toolkit backend must
provide a concrete implementation of.

The Control class adapts a GUI toolkit control/window to provide a set of
toolkit neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Property, Instance, Bool, Str, Enum, Tuple, Any

from abstract_adapter \
    import AbstractAdapter

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# The horizontal or vertical size policy supported by a control:
SizePolicy = Enum( 'fixed', 'expanding' )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def as_toolkit_control ( control ):
    """ Returns the GUI toolkit specific control associated with *control*.
    """
    if isinstance( control, Control ):
        return control()

    return control

#-------------------------------------------------------------------------------
#  'Control' class:
#-------------------------------------------------------------------------------

class Control ( AbstractAdapter ):

    #-- Facet Definitions ------------------------------------------------------

    # The GUI toolkit specific control/window being adapted:
    control = Any

    # The position of the control (x,y) relative to its parent:
    position = Property

    # The size of the control (dx,dy) in pixels:
    size = Property

    # The virtual size of the control's contents:
    virtual_size = Property

    # The bounds of the control (x,y,dx,dy):
    bounds = Property

    # The bounds of the control, including its frame (x,y,dx,dy):
    frame_bounds = Property

    # The visible bounds of the client area (useful in paint handlers):
    visible_bounds = Property

    # The size of the control's client area (dx,dy):
    client_size = Property

    # The best (optimal) size (dx,dy) for the control:
    best_size = Property

    # The minimum size (dx,dy) the control will accept:
    min_size = Property

    # The size policy (horizontal,vertical) of the control:
    size_policy = Tuple( SizePolicy, SizePolicy )

    # The position of the control (x,y) relative to the screen:
    screen_position = Property

    # The current mouse position (x,y) relative to the screen:
    mouse_position = Property

    # Is the control visible or not (True/False)?
    visible = Property

    # Is the control maximized (True/False)?
    maximized = Property

    # The kind of (top-level) control this is:
    kind = Str

    # Is the control modal or not (True/False)?
    modal = Bool( False )

    # Was the result of a modal control successful or not (True/False)?
    result = Bool( True )

    # Is the control enabled or not (True/False)?
    enabled = Property

    # Is the control checked or not (True/False)?
    checked = Property

    # The object that handles drag and drop events for the control:
    drop_target = Property

    # The layout manager associated with the control:
    layout = Property

    # The layout manager (if any) this control is contained in:
    parent_layout = Property

    # The (adapted) parent of this control:
    parent = Property

    # The (adapted) content of the control (used for scrollable controls):
    content = Property

    # The (adapted) root parent of this control (i.e. top level control):
    root_parent = Property

    # The list of (adapted) children of this control:
    children = Property

    # The current 'value' of the control:
    value = Property

    # The number of items the control contains (for controls with items):
    count = Property

    # The current selection range:
    selection = Property

    # The font associated with this control:
    font = Property

    # The (adapted) graphics object associated with the control:
    graphics = Property # ( Instance( Graphics ) )

    # A correctly initialized double-buffered graphics object:
    graphics_buffer = Property

    # A temporary (non-paint event) graphics object associated with the control:
    temp_graphics = Property # ( Instance( Graphics ) )

    # A graphics object for drawing on the screen:
    screen_graphics = Property # ( Instance( Graphics ) )

    # An image containing the current contents of the control (i.e. screen
    # capture):
    image = Property # ( Instance( AnImageResource ) )

    # The tooltip associated with the control:
    tooltip = Property # ( Str )

    # Is the mouse currently captured?
    mouse_capture = Property # ( Bool )

    # The foreground color of the control:
    foreground_color = Property # ( Color )

    # The background color of the control:
    background_color = Property # ( Color )

    # The mouse cursor for the control:
    cursor = Property

    # The icon associated with the control:
    icon = Property

    # The menu associated with the control:
    menubar = Property

    # The toolbar associated with the control:
    toolbar = Property

    # Should the control not perform screen updates?
    frozen = Property

    # The owner of the control:
    owner = Property

    # The Facets object associated with the control:
    object = Property

    # The editor associated with the control (if any):
    editor = Any # Instance( Editor )

    # Optional image slice used with the control:
    image_slice = Instance( 'facets.ui.pyface.image_slice.ImageSlice' )

    # Is the control a panel (i.e. container control)?
    is_panel = Property

    # Can the control be scrolled vertically?
    scroll_vertical = Property

    # Can the control be scrolled horizontally?
    scroll_horizontal = Property

    #-- Method Implementations -------------------------------------------------

    def __init__ ( self, control, **facets ):
        """ Initializes the object by saving the control being adapted.
        """
        super( Control, self ).__init__( **facets )

        self.control    = control
        control.adapter = self


    def __call__ ( self ):
        """ Returns the control being adapted.
        """
        return self.control

    #-- Default Facet Values ---------------------------------------------------

    def _editor_default ( self ):
        parent = self.parent
        if parent is None:
            return None

        return parent.editor

    #-- Abstract Method Definitions --------------------------------------------

    def refresh ( self, x = None, y = None, dx = None, dy = None  ):
        """ Refreshes the specified region of the control. If no arguments
            are specified, the entire control should be refreshed.
        """
        raise NotImplementedError


    def update ( self ):
        """ Causes the control to update its layout.
        """
        raise NotImplementedError


    def set_focus ( self ):
        """ Sets the keyboard focus on the associated control.
        """
        raise NotImplementedError


    def set_mouse_focus ( self ):
        """ Sets the mouse focus on the associated control.
        """
        raise NotImplementedError


    def popup_menu ( self, menu, x, y ):
        """ Pops up the specified context menu at the specified screen position.
        """
        raise NotImplementedError


    def bitmap_size ( self, bitmap ):
        """ Returns the size (dx,dy) of the specified toolkit specific bitmap:
        """
        raise NotImplementedError


    def text_size ( self, text ):
        """ Returns the size (dx,dy) of the specified text string (using the
            current control font).
        """
        raise NotImplementedError


    def set_event_handler ( self, **handlers ):
        """ Sets up event handlers for a specified set of events. The keyword
            names correspond to UI toolkit neutral event names, and the values
            are the callback functions for the events. Multiple event handlers
            can be set up in a single call.
        """
        raise NotImplementedError


    def unset_event_handler ( self, **handlers ):
        """ Tears down event handlers for a specified set of events. The keyword
            names correspond to UI toolkit neutral event names, and the values
            are the callback functions for the events that should no longer be
            called. Multiple event handlers can be torn down in a single call.
        """
        raise NotImplementedError


    def tab ( self, forward = True ):
        """ Moves the keyboard focus to the next/previous control that will
            accept it. If *forward* is True (the default) the next valid control
            is used; otherwise the previous valid control is used.
        """
        raise NotImplementedError


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
        raise NotImplementedError


    def destroy_children ( self ):
        """ Destroys all controls contained within the control associated with
            the adapter.
        """
        for child in self.children:
            child.destroy()


    def clear ( self ):
        """ Clears the current contents of the control.
        """
        raise NotImplementedError


    def close ( self ):
        """ Request the control to close itself.
        """
        raise NotImplementedError


    def get_item ( self, index ):
        """ Returns the control's *index*th item, for controls that contain
            items (e.g. list boxes, notebooks).
        """
        raise NotImplementedError


    def remove_item ( self, index ):
        """ Removes the control's *index*th item, for controls that contain
            items (e.g. list boxes, notebooks).
        """
        raise NotImplementedError


    def add_item ( self, value ):
        """ Adds the value specified by *value* to the control, and returns the
            index assigned to it.
        """
        raise NotImplementedError


    def find_item ( self, value ):
        """ Returns the index of the control item matching the specified
            *value*. If no matching item is found, it returns -1.
        """
        raise NotImplementedError


    def find_control ( self, x, y ):
        """ Finds and returns the topmost control at the specified (x, y )
            location, where ( x, y ) are in the control's local coordinate
            space. If no control is at the specified location, None is return.
        """
        raise NotImplementedError


    def add_page ( self, name, control ):
        """ Adds the page defined by *control* with the name *name* to the
            control (which should be some type of notebook control).
        """
        raise NotImplementedError


    def shrink_wrap ( self ):
        """ Resizes the control so that it fits snugly around its child
            controls.
        """
        raise NotImplementedError


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
        raise NotImplementedError


    def activate ( self ):
        """ Makes sure that the control (which should be a top-level window) is
            on top of all other application windows. If it is not, then it will
            brought in front of all other windows.
        """
        raise NotImplementedError


    def set_position ( self, width = None, height = None, parent = None ):
        """ Positions a top-level control (i.e. window) on the screen with a
            specified width and height so that the control completely fits on
            the screen if possible.
        """
        from facets.ui.constants import screen_dx, screen_dy

        dx, dy = self.best_size
        width  = width  or dx
        height = height or dy

        if parent is None:
            parent = self.parent

        if parent is None:
            # Center the popup on the screen:
            self.bounds = ( (screen_dx - width)  / 2, (screen_dy - height) / 2,
                            width, height )
            return

        # Calculate the desired size of the popup control:
        if isinstance( parent, Control ):
            x, y     = parent.screen_position
            cdx, cdy = parent.size
        else:
            # Special case of parent being a screen position and size tuple
            # (used to pop-up a dialog for a table cell):
            x, y, cdx, cdy = parent

        adjacent = (getattr( self, '_kind', 'popup' ) == 'popup')
        width    = min( max( cdx, width ), screen_dx )
        height   = min( height, screen_dy )

        # Calculate the best position and size for the pop-up:

        # Note: This code tries to deal with the fact that the user may have
        # multiple monitors. The underlying toolkit may not report this
        # information, so the screen_dx, screen_dy values usually just provide
        # the size of the primary monitor. To get around this, the code assumes
        # that the original (x,y) values are valid, and that all monitors are
        # the same size. If this assumption is not true, popups may appear in
        # wierd positions on the secondary monitors.
        nx     = x % screen_dx
        xdelta = x - nx
        rx     = nx + cdx
        if (nx + width) > screen_dx:
            if (rx - width) < 0:
                nx = screen_dx - width
            else:
                nx = rx - width

        ny     = y % screen_dy
        ydelta = y - ny
        by     = ny
        if adjacent:
            by += cdy

        if (by + height) > screen_dy:
            if not adjacent:
                ny += cdy

            if ( ny - height ) < 0:
                ny = screen_dy - height
            else:
                by = ny - height

        # Position and size the window as requested:
        self.bounds = ( nx + xdelta, by + ydelta, width, height )


    def is_visible ( self, x, y, dx, dy ):
        """ Returns True if any part of the region specified by *x*, *y*, *dx*
            and *dy* is visible in the control, and False otherwise.
        """
        vx, vy, vdx, vdy = self.visible_bounds

        return (((x + dx) > vx) and ((vx + vdx) > x) and
                ((y + dy) > vy) and ((vy + vdy) > y))

    #-- Abstract Property Implementations --------------------------------------

    def _get_position ( self ):
        raise NotImplementedError

    def _set_position ( self, x_y ):
        raise NotImplementedError


    def _get_size ( self ):
        raise NotImplementedError

    def _set_size ( self, dx_dy ):
        raise NotImplementedError


    def _get_virtual_size ( self ):
        raise NotImplementedError

    def _set_virtual_size ( self, dx_dy ):
        raise NotImplementedError


    def _get_bounds ( self ):
        raise NotImplementedError

    def _set_bounds ( self, x_y_dx_dy ):
        raise NotImplementedError


    def _get_frame_bounds ( self ):
        raise NotImplementedError


    def _get_visible_bounds ( self ):
        raise NotImplementedError


    def _get_client_size ( self ):
        raise NotImplementedError

    def _set_client_size ( self, dx_dy ):
        raise NotImplementedError


    def _get_best_size ( self ):
        raise NotImplementedError


    def _get_min_size ( self ):
        raise NotImplementedError

    def _set_min_size ( self, dx_dy ):
        raise NotImplementedError


    def _get_screen_position ( self ):
        raise NotImplementedError


    def _get_mouse_position ( self ):
        raise NotImplementedError


    def _get_visible ( self ):
        raise NotImplementedError

    def _set_visible ( self, is_visible ):
        raise NotImplementedError


    def _get_maximized ( self ):
        raise NotImplementedError

    def _set_maximized ( self, maximized ):
        raise NotImplementedError


    def _get_enabled ( self ):
        raise NotImplementedError

    def _set_enabled ( self, enabled ):
        raise NotImplementedError


    def _get_checked ( self ):
        raise NotImplementedError

    def _set_checked ( self, checked ):
        raise NotImplementedError


    def _get_drop_target ( self ):
        raise NotImplementedError

    def _set_drop_target ( self, is_drop_target ):
        raise NotImplementedError


    def _get_layout ( self ):
        raise NotImplementedError

    def _set_layout ( self, layout ):
        raise NotImplementedError


    def _get_parent_layout ( self ):
        raise NotImplementedError


    def _get_parent ( self ):
        raise NotImplementedError


    def _get_content ( self ):
        raise NotImplementedError

    def _set_content ( self, content ):
        raise NotImplementedError


    def _get_root_parent ( self ):
        raise NotImplementedError


    def _get_children ( self ):
        raise NotImplementedError


    def _get_value ( self ):
        raise NotImplementedError

    def _set_value ( self, value ):
        raise NotImplementedError


    def _get_count ( self ):
        raise NotImplementedError


    def _get_selection ( self ):
        raise NotImplementedError

    def _set_selection ( self, selection ):
        raise NotImplementedError


    def _get_font ( self ):
        raise NotImplementedError

    def _set_font ( self, font ):
        raise NotImplementedError


    def _get_graphics ( self ):
        raise NotImplementedError


    def _get_graphics_buffer ( self ):
        raise NotImplementedError


    def _get_temp_graphics ( self ):
        raise NotImplementedError


    def _get_screen_graphics ( self ):
        raise NotImplementedError

    def _set_screen_graphics ( self, value ):
        raise NotImplementedError


    def _get_image ( self ):
        raise NotImplementedError


    def _set_tooltip ( self, tooltip ):
        raise NotImplementedError


    def _get_mouse_capture ( self ):
        raise NotImplementedError

    def _set_mouse_capture ( self, is_captured ):
        raise NotImplementedError


    def _get_foreground_color ( self ):
        raise NotImplementedError

    def _set_foreground_color ( self, color ):
        raise NotImplementedError


    def _get_background_color ( self ):
        raise NotImplementedError

    def _set_background_color ( self, color ):
        raise NotImplementedError


    def _set_cursor ( self, cursor ):
        raise NotImplementedError


    def _set_icon ( self, icon ):
        raise NotImplementedError


    def _set_menubar ( self, menubar ):
        raise NotImplementedError


    def _set_toolbar ( self, toolbar ):
        raise NotImplementedError

    def _set_frozen ( self, is_frozen ):
        raise NotImplementedError


    def _get_owner ( self ):
        return getattr( self.control, 'owner', None )

    def _set_owner ( self, owner ):
        setattr( self.control, 'owner', owner )


    def _get_object ( self ):
        return getattr( self.control, '_object', None )


    def _get_is_panel ( self ):
        raise NotImplementedError


    def _set_scroll_vertical ( self, can_scroll ):
        raise NotImplementedError


    def _set_scroll_horizontal ( self, can_scroll ):
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------