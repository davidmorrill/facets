"""
Defines a GUI toolkit independent ToolbarControl class for managing groups of
control organized like a toolbar.
"""

#-------------------------------------------------------------------------------
#  To Do:
#  - Handle 'control' key being released with no motion event to end edit mode.
#  - Provide a means for setting the margin along the side of the toolbar.
#  - Make sure HSplit/VSplit DockWindows handle fixed sized toolbars correctly.
#  - Need to improve the code that allows 'springy' toolbars used for expandable
#    controls. This includes code in this module and in ui_panel.py.
#  - Need way to change margin around a grid layout so that VToolbar items with
#    labels don't have so much white space around them.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Any, Bool, Int, Tuple, Range, Instance, List, \
           Enum, Event, Image, Theme, Control, DelegatesTo, Property,      \
           property_depends_on, on_facet_set, image_for

from facets.core.facet_base \
    import plural_of

from facets.ui.ui_facets \
    import Orientation

from facets.ui.pyface.timer.api \
    import do_after

from themed_window \
    import ThemedWindow

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The width/height of the 'control' area of the main ToolbarControl:
ControlSize = 7

# The default amount of padding to use:
Padding = 2

# The amount of time (in milliseconds) to wait before starting starting to
# auto-scroll the toolbar:
AutoScrollDelay = 250

# The amount of time (in milliseconds) to wait between scroll events:
AutoScrollInterval = 40

# The amount of time (in milliseconds) to wait between scroll events while edit
# mode dragging:
DragScrollInterval = 100

# The number of pixels to scroll per scroll wheel increment:
WheelScrollAmount = 16

# The number of pixels to scroll on each click scroll:
ClickScrollAmount = 16

# The control alignment values:
LEFT  = TOP    = 0
RIGHT = BOTTOM = 1
CENTER         = 2
FILL           = 3

# The mapping from text to numeric alignment values:
AlignmentMapping = {
    'left':   LEFT,
    'top':    TOP,
    'right':  RIGHT,
    'bottom': BOTTOM,
    'center': CENTER,
    'fill':   FILL
}

# Scroll zone images:
tup    = image_for( '@facets:tup?L40'    )
tdown  = image_for( '@facets:tdown?L40'  )
tleft  = image_for( '@facets:tleft?L40'  )
tright = image_for( '@facets:tright?L40' )

# Hide/show zones:
HideZone      = 0
LeftShowZone  = 1
RightShowZone = 2
NoZone        = 3

# Mapping from 'zone' values to tooltips:
ZoneTooltips = {
    HideZone:      'Click to remove item.\n',
    LeftShowZone:  'Click to add hidden item.\n',
    RightShowZone: 'Click to add hidden item.\n',
    NoZone:        '',
    -1:            ''
}

# Hide/Show control images:
hide  = image_for( '@facets:minus?l10S|L94' ).scale( 0.75 )
show  = image_for( '@facets:plus?l10S|L94'  ).scale( 0.75 )
show2 = image_for( '@facets:plus?l48|L94'   ).scale( 0.75 )

# The theme used when in 'edit' mode:
edit_theme = Theme( '@xform:b?H61L36S70', content = 0 )

# The themes used for drawing the 'scroll' zone part of the control:
scroll_themes = (
    Theme( '@xform:b?L25' ),       # Normal
    Theme( '@xform:b?H58L27S64' )  # With hidden controls
)

#-------------------------------------------------------------------------------
#  'ControlImage' class:
#-------------------------------------------------------------------------------

class ControlImage ( HasPrivateFacets ):
    """ Represents an image of a control while in edit mode.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The control this item is the image for:
    control = Instance( Control )

    # The image of the control:
    image = Image

    # The current position of the image within the container:
    position = Tuple( Int, Int )

    # The owner of the item:
    owner = Any # Instance( ToolbarContainer )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        self.image = None if control is None else control.image


    def _position_set ( self ):
        """ Handles the position of the image being changed.
        """
        if self.owner is not None:
            self.owner.refresh()

#-------------------------------------------------------------------------------
#  'ToolbarContainer' class:
#-------------------------------------------------------------------------------

class ToolbarContainer ( ThemedWindow ):
    """ Defines the GUI toolkit neutral ToolbarContainer class that acts as a
        container for the controls being managed by a ToolbarControl.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ToolbarControl object that owns this container:
    owner = Any # Instance( ToolbarControl )

    # Is the orientation vertical (True) or horizontal (False)?
    is_vertical = DelegatesTo( 'owner' )

    # The spacing between adjacent toolbar controls:
    spacing = DelegatesTo( 'owner' )

    # The amount of margin to allow at the ends of the toolbar:
    margin = DelegatesTo( 'owner' )

    # The alignment of the toolbar controls along the non-layout axis:
    alignment = Int

    # The current list of active toolbar controls (in display order):
    active = List # ( Control )

    # The current list of hidden (inactive) toolbar controls:
    hidden = List # ( Control )

    # The maximum size (width or height depending upon orientation) of all
    # active controls:
    size = Property

    # The original size (width or height depending upon orientation) of all
    # active controls:
    original_size = Property

    # The minimum size of the container:
    min_size = Property

    # Event fired when a change to some aspect of the container requires
    # updating the UI:
    modified = Event

    # Can the scrollbar be scrolled left (or up)?
    can_scroll_left_up = Property

    # Can the scrollbar be scrolled right (or down)?
    can_scroll_right_down = Property

    # The list of control images used during edit operations:
    images = List # ( ControlImage )

    # The currently highlighted control in edit mode (if any):
    highlighted = Any # Instance( ControlImage )

    # The current hide/show zone the mouse pointer is in (if any):
    zone = Int

    # Is edit mode only active while 'control' key is pressed?
    control_down = Bool

    # Has edit mode been activated by the mouse entering the container?
    activated = Bool

    #-- Public Methods ---------------------------------------------------------

    def update ( self, added, removed = None ):
        """ Handles adding the list of controls specified by *added* and
            removing the controls specified by *removed* from the toolbar. If
            *removed* is omitted or **None**, then all current controls not in
            *added* are removed from the toolbar.
        """
        # Note: This code assumes 'edit' mode is not currently active.
        modified = False
        active   = self.active
        hidden   = self.hidden
        if removed is None:
            removed = active + hidden

        for control in removed:
            if control not in added:
                if control in active:
                    active.remove( control )
                    control.destroy()
                    modified = True
                elif control in hidden:
                    hidden.remove( control )
                    control.destroy()

        i = len( active )
        for control in added:
            if (control not in active) and (control not in hidden):
                self._init_control( control, i )
                self._init_control_size( control )
                active.append( control )
                modified = True
                i       += 1

        if modified:
            self._layout_active()


    def scroll_active ( self, amount ):
        """ Scrolls the contents of the toolbar by the specified *amount*.
        """
        if len( self.active ) > 0:
            x, y   = self.active[0].position
            dx, dy = self.control.size
            margin = self.margin
            if self.is_vertical:
                self._move_active(
                    0, min( max( y + amount, dy - self.size ), margin ) - y )
            else:
                self._move_active(
                    min( max( x + amount, dx - self.size ), margin ) - x, 0 )


    def begin_edit ( self, event ):
        """ Begins editing mode.
        """
        images = self.images
        for control in self.active:
            control.visible = False
            images.append( ControlImage(
                control  = control,
                position = control.position
            ).set(
                owner = self
            ) )

        self.highlighted           = None
        self.zone                  = NoZone
        self.control.mouse_capture = True
        self.state                 = 'waiting'
        self.control_down          = self.activated = event.control_down


    def end_edit ( self ):
        """ Ends editing mode.
        """
        del self.images[:]
        for control in self.active:
            control.visible = True

        self.control.set(
            mouse_capture = False,
            cursor        = 'arrow',
            tooltip       = ''
        )
        self.state                 = 'normal'
        self._amount               = 0
        self.refresh()


    def paint_all ( self, g ):
        """ Paints the content of the window into the device context specified
            by *g*.
        """
        # If container is empty, use the original paint handler:
        images = self.images
        if len( images ) == 0:
            super( ToolbarContainer, self ).paint_all( g )

            return

        dx, dy = self.control.size

       # Draw the container background:
        edit_theme.fill( g, 0, 0, dx, dy )

        # Draw all of the inactive control images:
        opacity, g.opacity  = g.opacity, 0.67
        active, highlighted = self.active, self.highlighted
        for i, image in enumerate( images ):
            if image is not highlighted:
                x, y = image.position
                g.draw_bitmap( image.image.bitmap, x, y )

        # Draw the currently highlighted control image (if any):
        if highlighted is not None:
            g.opacity = 1.0
            x, y      = highlighted.position
            g.draw_bitmap( highlighted.image.bitmap, x, y )

        # If there are any hidden controls, draw the insertion bar:
        hidden = len( self.hidden )
        if hidden > 0:
            g.brush   = 0x00FF00
            g.pen     = None
            g.opacity = 0.25
            tx  = ty  = 0
            tx2 = tdx = dx
            ty2 = tdy = dy
            if self.is_vertical:
                tdx = dx / 2
                tx  = tx2 = dx - tdx
            else:
                tdy = dy / 2
                ty  = ty2 = dy - tdy

            g.draw_rectangle( tx, ty, tdx, tdy )
            g.pen = 0x000000
            g.draw_line( tx, ty, tx2, ty2 )

        g.opacity = opacity

        # Draw the overlay image (minus sign, plus sign, ...) if needed:
        zone = self.zone
        if ((self.state == 'waiting') and
            (highlighted is not None) and
            (zone != NoZone)):
           image    = (hide if zone == HideZone else
                      (show if hidden == 1 else show2))
           idx, idy = image.width, image.height
           dx, dy   = highlighted.control.size
           if self.is_vertical:
               x, y, dx, dy, idx, idy = y, x, dy, dx, idy, idx

           y += ((dy - idy) / 2)
           if zone == LeftShowZone:
               x -= (idx / 2)
           elif zone == RightShowZone:
               x += (dx - (idx / 2))
           else:
               x += ((dx - idx) / 2)

           if self.is_vertical:
               g.draw_bitmap( image.bitmap, y, x )
           else:
               g.draw_bitmap( image.bitmap, x, y )

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        active   = self.active
        controls = dict( [ ( control._id, control ) for control in active ] )
        if 'hidden' in prefs:
            hidden = self.hidden
            for id in prefs[ 'hidden' ]:
                control = controls.get( id )
                if control is not None:
                    control.visible = False
                    hidden.append( control )
                    active.remove( control )

        if 'active' in prefs:
            new_active = []
            for id in prefs[ 'active' ]:
                control = controls.get( id )
                if control is not None:
                    new_active.append( control )
                    active.remove( control )

            self.active[0:0] = new_active


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return {
            'active': [ control._id for control in self.active ],
            'hidden': [ control._id for control in self.hidden ]
        }

    #-- Facet Default Values ---------------------------------------------------

    def _alignment_default ( self ):
        return AlignmentMapping[ self.owner.alignment ]


    def _active_default ( self ):
        for i, control in enumerate( self.control.children ):
            self._init_control( control, i )

        return self.control.children

    #-- Window Event Handlers --------------------------------------------------

    def resize ( self, event ):
        """ Handles the window being resized.
        """
        self._layout_active()


    def normal_enter ( self ):
        self.control.parent.tooltip = ''


    def waiting_motion ( self, event ):
        """ Handles a mouse motion event in waiting mode.
        """
        if self._edit_active( event ):
            x, y = event.x, event.y
            self._check_cursor( x, y )
            self._check_highlighted( x, y )


    def waiting_left_down ( self, event ):
        """ Handles a left mouse button down event in waiting mode.
        """
        if self.highlighted is not None:
            self._xy       = event.x, event.y
            self._position = self.highlighted.position
            self.state     = 'clicking'


    def waiting_right_down ( self, event ):
        """ Handles a right mouse button down event in waiting mode.
        """
        self.waiting_left_down( event )


    def waiting_left_up ( self, event ):
        """ Handles a left mouse button up event in waiting mode.
        """
        if self._edit_active( event ):
            self.control.mouse_capture = True


    def waiting_right_up ( self, event ):
        """ Handles a right mouse button up event in waiting mode.
        """
        self.waiting_left_up( event )


    def waiting_wheel ( self, event ):
        """ Handles a mouse wheel event while in waiting mode.
        """
        if self._edit_active( event ):
            x, y      = event.x, event.y
            dx, dy    = self.control.size
            scrolling = True
            hidden    = len( self.hidden )
            if hidden > 0:
                scrolling = ((x <= (dx / 2)) if self.is_vertical else
                             (y <= (dy / 2)))

            if scrolling:
                self.scroll_active( (1 + event.shift_down) * event.wheel_change
                                    * WheelScrollAmount )
                self._sync_images()
                self._check_highlighted( x, y )
            else:
                self._check_highlighted( event.x, event.y )
                if (hidden > 0) and (self.highlighted is not None):
                    self._rehide = None
                    self._roll_control(
                        self.highlighted.control, event.wheel_change
                    )
                    self._check_cursor( x, y )
                    if len( self.hidden ) > 0:
                        self._xy   = x, y
                        self.state = 'wheeling'
                    else:
                        self._defer_check_highlighted( event )


    def wheeling_motion ( self, event ):
        """ Handles a mouse motion event in wheeling mode.
        """
        if self._edit_active( event ):
            x, y   = event.x, event.y
            x0, y0 = self._xy
            if (abs( x - x0 ) + abs( y - y0 )) > 3:
                self.state = 'waiting'
                self.waiting_motion( event )


    def wheeling_wheel ( self, event ):
        """ Handles a mouse wheel event in wheeling mode.
        """
        if self._edit_active( event ):
            self._roll_control( self.highlighted.control, event.wheel_change )


    def wheeling_left_down ( self, event ):
        """ Handles a left mouse button down event in wheeling mode.
        """
        self.state = 'waiting'
        self.waiting_left_down( event )


    def wheeling_right_down ( self, event ):
        """ Handles a right mouse button down event in wheeling mode.
        """
        self.state = 'waiting'
        self.waiting_right_down( event )


    def clicking_motion ( self, event ):
        """ Handles a mouse motion event while in clicking mode.
        """
        x, y   = event.x, event.y
        x0, y0 = self._xy
        if (abs( x - x0 ) + abs( y - y0 )) > 3:
            self.state = 'dragging'
            self.dragging_motion( event )


    def clicking_left_up ( self, event ):
        """ Handles a left mouse button up event while in clicking mode.
        """
        if self._edit_active( event ):
            if self.highlighted is not None:
                control = self.highlighted.control
                if self.zone == HideZone:
                    self._hide_control( control )
                elif self.zone != NoZone:
                    self._unhide_control( control )

                self._check_cursor( event.x, event.y )

            self.control.mouse_capture = True
            self.state                 = 'waiting'
            self.highlighted           = None
            self._defer_check_highlighted( event )


    def clicking_right_up ( self, event ):
        """ Handles a right mouse button up event while in clicking mode.
        """
        if self._edit_active( event ):
            if self.highlighted is not None:
                control = self.highlighted.control
                if self.zone == HideZone:
                    self._hide_control( control )
                elif self.zone != NoZone:
                    self._unhide_control( control, len( self.hidden ) )

            self.control.mouse_capture = True
            self.state                 = 'waiting'
            self.highlighted           = None
            self._defer_check_highlighted( event )


    def dragging_motion ( self, event ):
        """ Handles a mouse motion event in dragging mode.
        """
        x0, y0         = self._xy
        dxy            = [ event.x - x0, event.y - y0 ]
        isv            = self.is_vertical
        dxy[ 1 - isv ] = 0
        ci             = self.highlighted
        control        = ci.control
        idxy           = control.size
        idxy2          = idxy[ isv ] / 2
        cdxy           = self.control.size
        position       = self._position
        ixy            = [ position[0] + dxy[0], position[1] + dxy[1] ]
        ixy[ isv ]     = max( min( ixy[ isv ], cdxy[ isv ] - idxy2 ),
                              -idxy2 )
        ci.position    = tuple( ixy )
        self._check_swap()

        amount = 0
        if ixy[ isv ] < -(idxy2 / 2):
            amount = ClickScrollAmount
        elif ixy[ isv ] > (cdxy[ isv ] - (1.5 * idxy2)):
            amount = -ClickScrollAmount

        if (amount != 0) and (self._amount == 0):
            do_after( AutoScrollDelay, self._scroll_toolbar )

        self._amount = amount


    def dragging_left_up ( self, event ):
        """ Handles a left mouse button up event in dragging mode.
        """
        if self._edit_active( event ):
            self.state                 = 'waiting'
            self.control.mouse_capture = True
            highlighted = self.highlighted
            self._animate( highlighted, highlighted.control.position )
            self._defer_check_highlighted( event )

    #-- Property Implementations -----------------------------------------------

    def _get_size ( self ):
        index = self.is_vertical
        size  = self.spacing * (len( self.active ) - 1)
        for control in self.active:
            size += control.size[ index ]

        return size


    def _get_original_size ( self ):
        index = self.is_vertical
        size  = self.spacing * (len( self.active ) - 1)
        for control in self.active:
            size += control._size[ index ]

        return size


    def _get_min_size ( self ):
        nisv = (not self.is_vertical)
        tdxy = dxy = 0
        if self.theme is not None:
            tdxy = self.theme.bounds()[ nisv ]

        for control in self.active:
            self._init_control_size( control )
            dxy = max( dxy, control.size[ nisv ] )

        result = ( 30, dxy + tdxy )

        return ( result[ 1 - nisv ], result[ nisv ] + 6 )


    @property_depends_on( 'modified' )
    def _get_can_scroll_left_up ( self ):
        if len( self.active ) == 0:
            return False

        isv = self.is_vertical

        return ((self.control.size[ isv ] - self.size) <
                self.active[0].position[ isv ])


    @property_depends_on( 'modified' )
    def _get_can_scroll_right_down ( self ):
        if len( self.active ) == 0:
            return False

        return (self.active[0].position[ self.is_vertical ] < self.margin)

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'highlighted, zone' )
    def _redraw_needed ( self ):
        """ Handles any facet requiring the control to be redrawn being changed.
        """
        self.refresh()

    #-- Private Methods --------------------------------------------------------

    def _init_control ( self, control, index ):
        """ Initializes the Control object specified by *control* for use within
            a toolbar control.
        """
        control._size    = control.size
        control.position = ( 9999, 9999 )  # Layout will fix this later
        if control._id is None:
            editor      = control.editor
            control._id = index if editor is None else editor.item.get_id()


    def _init_control_size ( self, control ):
        """ Initializes the size of the Control object specified by *control*.
        """
        if control.layout is not None:
            cdx, cdy     = control.size
            bdx, bdy     = control.best_size
            control.size = control._size = ( max( cdx, bdx ), max( cdy, bdy ) )


    def _edit_active ( self, event ):
        """ Returns whether or not edit mode is still active.
        """
        result = event.control_down
        if not self.control_down:
            result = (not self.activated)
            if self.in_control( event ):
                if not self.activated:
                    self.control.parent.tooltip = ''

                self.activated = result = True

        if not result:
            self.end_edit()

        return result


    def _check_cursor ( self, x, y ):
        """ Checks if the current mouse position is in the insert control zone
            (if active) and sets the cursor and tooltip accordingly.
        """
        # Set the cursor:
        cursor = 'arrow'
        n      = len( self.hidden )
        if (n > 0) and self.in_control( x, y ):
            dx, dy = self.control.size
            if self.is_vertical:
                if x > (dx / 2):
                    cursor = 'sizeew'
            elif y > (dy /2 ):
                cursor = 'sizens'

        self.control.cursor = cursor

        # Set the tooltip:
        tooltip   = ZoneTooltips[ self.zone ]
        show_zone = self.zone in ( LeftShowZone, RightShowZone )
        if (n > 1) and show_zone:
            tooltip += plural_of(
                n, 'Right-click to add all %s hidden item%s.\n'
            )

        if cursor == 'arrow':
            if self.size > self.control.size[ self.is_vertical ]:
                tooltip +=  'Use mouse wheel to scroll items.\n'
        elif show_zone:
            tooltip += 'Use mouse wheel to add hidden item.\n'

        if n > 1:
            tooltip = tooltip.replace(
                'hidden item.', plural_of( n, 'one of %s hidden item%s.' )
            )

        if self.highlighted is not None:
            tooltip += 'Drag to move item.'

        self.control.tooltip = tooltip.strip()


    def _check_highlighted ( self, x, y ):
        """ Sets the highlighted control and hide/show zone for the mouse
            position specified by (*x*,*y*).
        """
        self.highlighted, self.zone = self._find_image_at( x, y )
        self._check_cursor( x, y )


    def _defer_check_highlighted ( self, event ):
        """ Sets the highlighted control and hide/show zone after a brief pause
            to allow any animations to complete.
        """
        do_after( 300, self._check_highlighted, event.x, event.y )


    def _check_swap ( self ):
        """ Checks to see if the current highlighted control needs to be swapped
            with either of its neighbors.
        """
        control = self.highlighted.control
        hxy     = self.highlighted.position
        hdxy    = control.size
        isv     = self.is_vertical
        active  = self.active
        i       = active.index( control )
        i2      = None
        if (i + 1) < len( active ):
            cb = active[ i + 1 ].bounds
            if (hxy[ isv ] + hdxy[ isv ]) > (cb[ isv ] + (cb[ isv + 2 ] / 2)):
                i2 = i + 1

        if (i2 is None) and (i > 0):
            cb = active[ i - 1 ].bounds
            if hxy[ isv ] < (cb[ isv ] + (cb[ isv + 2 ] / 2)):
                i2 = i - 1

        if i2 is not None:
            images = self.images
            image  = images[ i2 ]
            images[ i ], images[ i2 ] = images[ i2 ], images[ i ]
            active[ i ], active[ i2 ] = active[ i2 ], active[ i ]
            self._layout_active()
            self._animate( image, image.control.position )


    def _scroll_toolbar ( self ):
        """ Scroll the toolbar while in edit mode.
        """
        if self._amount != 0:
            highlighted = self.highlighted
            if highlighted is not None:
                position = highlighted.position
                self.scroll_active( self._amount )
                self._sync_images()
                highlighted.position = position
                self._check_swap()
                do_after( DragScrollInterval, self._scroll_toolbar )


    def _sync_images ( self ):
        """ Synchronizes the position of all ghost images with their
            corresponding actual controls.
        """
        active, images = self.active, self.images
        for i in xrange( len( active ) ):
            images[ i ].position = active[ i ].position


    def _hide_control ( self, control ):
        """ Hides the Control specified by *control*.
        """
        active, images = self.active, self.images
        i              = active.index( control )
        self.hidden.append( control )
        del active[ i ]
        del images[ i ]
        self._layout_active()
        self._animate_active()


    def _unhide_control ( self, control, count = 1 ):
        """ Unhides the specified number of hidden controls before or after the
            Control specified by *control*.
        """
        active, images = self.active, self.images
        i              = active.index( control ) + (self.zone == RightShowZone)
        active[ i: i ] = self.hidden[ -count: ]
        del self.hidden[ -count: ]
        images[ i: i ] = [ ControlImage(
            control  = control2,
            position = control.position
        ).set(
            owner = self
        ) for control2 in active[ i: i + count ] ]
        self._layout_active()
        self._animate_active()


    def _roll_control ( self, control, direction ):
        """ Unhides either the first or last hidden control based upon the mouse
            wheel direction specified by *direction* and inserts it before or
            after the Control specified by *control*. If the '_rehide' facet is
            not None, the Control it specifies is rehidden before the new
            Control is unhidden. The newly unhidden Control is saved as the new
            value of '_rehide'.
        """
        active, hidden, images = self.active, self.hidden, self.images
        rehide = self._rehide
        if rehide is not None:
            i = active.index( rehide )
            del active[ i ]
            del images[ i ]
            if direction >= 0:
                hidden.insert( 0, rehide )
            else:
                hidden.append( rehide )

        i      = active.index( control ) + (self.zone == RightShowZone)
        i2     = -(direction >= 0)
        rehide = self._rehide = hidden[ i2 ]
        del hidden[ i2 ]
        active.insert( i, rehide )
        ci = ControlImage( control = rehide ).set( owner = self )
        images.insert( i, ci )
        self._layout_active()
        xy   = list( rehide.position )
        nisv = (not self.is_vertical)
        if direction < 0:
            xy[ nisv ] = self.control.size[ nisv ]
        else:
            xy[ nisv ] = -rehide.size[ nisv ]

        ci.position = tuple( xy )
        self._animate_active()


    def _move_active ( self, dx, dy ):
        """ Adjust the position of all active controls by the amount specified
            by (*dx*, *dy*).
        """
        if (dx != 0) or (dy != 0):
            for control in self.active:
                x, y             = control.position
                control.position = ( x + dx, y + dy )

            self.modified = True


    def _layout_active ( self ):
        """ Lay out all of the current active controls.
        """
        active = self.active
        if len( active ) == 0:
            return

        dx, dy    = self.control.size
        size      = self.original_size
        alignment = self.alignment
        spacing   = self.spacing
        margin    = self.margin

        if self.theme is not None:
            tx, ty, tdx, tdy = self.theme.bounds( 0, 0, dx, dy )
        else:
            tx, ty, tdx, tdy = 0, 0, dx, dy

        images           = self.images
        tweight, weights = self._weights()
        if self.is_vertical:
            extra = dy - margin - size
            y     = min( max( active[0].position[1], extra + margin ), margin )
            bx    = tx

            # Reduce any extra so that springy items don't push the last item
            # right up to the edge of the toolbar:
            extra -= margin

            if alignment == RIGHT:
                bx = tx + tdx
            elif alignment == CENTER:
                bx = tx + (tdx / 2)

            for i, control in enumerate( self.active ):
                cdx, cdy = control.size
                x        = bx
                if alignment == RIGHT:
                    x = bx - cdx
                elif alignment == CENTER:
                    x = bx - (cdx / 2)

                if alignment == FILL:
                    cdx = tdx

                pdy    = cdy
                weight = weights[ i ]
                if weight > 0:
                    cdy = control._size[1]
                    if extra > 0:
                        edy      = int( round( (float( extra ) * weight) /
                                               tweight ) )
                        cdy     += edy
                        extra   -= edy
                        tweight -= weight

                control.bounds = ( x, y, cdx, cdy )
                y             += cdy + spacing
                if ((len( images ) > 0) and
                    ((pdy != cdy) or (cdx != images[ i ].image.width))):
                    images[ i ].image = control.image
        else:
            extra = dx - margin - size
            x     = min( max( active[0].position[0], extra + margin ), margin )
            by    = ty

            # Reduce any extra so that springy items don't push the last item
            # right up to the edge of the toolbar:
            extra -= margin

            if alignment == BOTTOM:
                by = ty + tdy
            elif alignment == CENTER:
                by = ty + (tdy / 2)

            for i, control in enumerate( self.active ):
                cdx, cdy = control.size
                y        = by
                if alignment == BOTTOM:
                    y = by - cdy
                elif alignment == CENTER:
                    y = by - (cdy / 2)

                if alignment == FILL:
                    cdy = tdy

                pdx    = cdx
                weight = weights[ i ]
                if weight > 0:
                    cdx = control._size[0]
                    if extra > 0:
                        edx      = int( round( (float( extra ) * weight) /
                                               tweight ) )
                        cdx     += edx
                        extra   -= edx
                        tweight -= weight

                control.bounds = ( x, y, cdx, cdy )
                x             += cdx + spacing
                if ((len( images ) > 0) and
                    ((pdx != cdx) or (cdy != images[ i ].image.height))):
                    images[ i ].image = control.image

        self.modified = True


    def _weights ( self ):
        """ Returns the total weight and list of individual weights for all
            active controls as a tuple of the form: ( total_weight, [ weight0,
            weight1, ..., weightn ] ).
        """
        total   = 0
        weights = []
        isv     = self.is_vertical
        for control in self.active:
            weight = 0
            editor = control.editor
            if ((editor is not None) and editor.scrollable) or control._stretch:
                weight = control._size[ isv ]

            weights.append( weight )
            total += weight

        return ( total, weights )


    def _find_image_at ( self, x, y ):
        """ Returns a tuple containing the ControlImage object and hide/show
            zone located at the point specified by (*x*,*y*) or ( None, NoZone )
            if no ControlImage is at the specified location.
        """
        is_in = self._is_in
        image = self.highlighted
        if image is not None:
            zone = is_in( x, y, image )
            if zone >= 0:
                return ( image, zone )

        for image in self.images:
            zone = is_in( x, y, image )
            if zone >= 0:
                return ( image, zone )

        return ( None, -1 )


    def _is_in ( self, x, y, image ):
        """ Returns -1 if the location specified by (*x*,*y*) is not in the
            ControlImage specified by *image*. If it is in the image, then the
            hide/show zone for the image is returned.
        """
        ix, iy      = image.position
        image       = image.image
        idx, idy    = image.width, image.height
        edxy        = [ 0, 0 ]
        isv         = self.is_vertical
        edxy[ isv ] = self.spacing

        if ((ix <= x < (ix + idx + edxy[0])) and
            (iy <= y < (iy + idy + edxy[1]))):
            isv *= 3
            xy, bxy, bdxy = ( x, ix, idx, y, iy, idy )[ isv: isv + 3 ]
            if xy < (bxy + (bdxy / 3)):
                if len( self.hidden ) > 0:
                    return LeftShowZone
            elif xy >= (bxy + bdxy - (bdxy / 3)):
                if len( self.hidden ) > 0:
                    return RightShowZone
            elif len( self.images ) > 1:
                return HideZone

            return NoZone

        return -1


    def _animate_active ( self ):
        """ Concurrently animates all current images moving to their
            corresponding active control's position.
        """
        active, images = self.active, self.images
        for i in xrange( len( active ) ):
            self._animate( images[ i ], active[ i ].position )


    def _animate ( self, image, position ):
        """ Animates the traversal of the ControlImage specified by *image* to
            the position (x,y) specified by *position*.
        """
        x, y, dx, dy = self.control.bounds
        idx, idy     = image.image.width, image.image.height
        ix, iy       = image.position
        px, py       = position

        # If there is no motion, or the motion is completely off camera, then
        # skip it:
        if (((ix == px)        and (iy == py))        or
            (((ix + idx) <= x) and ((px + idx) <= x)) or
            ((ix >= (x + dx))  and (px >= (x + dx)))  or
            (((iy + idy) <= y) and ((py + idy) <= y)) or
            ((iy >= (y + dy))  and (py >= (y + dy)))):
            return

        # Animate the movement of the image:
        image.animate_facet( 'position', 0.25, position )

#-------------------------------------------------------------------------------
#  'ToolbarControl' class:
#-------------------------------------------------------------------------------

class ToolbarControl ( ThemedWindow ):
    """ Defines the GUI toolkit independent ToolbarControl class for managing
        groups of control organized like a toolbar.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Background theme for the container control:
    theme = Theme( '@xform:b?L44', content = 0 )

    # The orientation of the toolbar control:
    orientation = Orientation( 'horizontal' )

    # The spacing between adjacent toolbar controls:
    spacing = Range( 0, 32 )

    # The amount of margin to allow at the ends of the toolbar:
    margin = Range( 0, 32 )

    # The alignment of the toolbar controls along the non-layout axis:
    alignment = Enum( 'center', 'left', 'top', 'right', 'bottom', 'fill' )

    # Should the toolbar expand to use extra space along its non-layout axis?
    full_size = Bool( False )

    # The container control all child toolbar controls are placed in:
    container = Instance( Control )

    # The list of controls currently in the toolbar (Note that this facet is
    # provided for dynamically added/deleted controls. For controls that are all
    # added at initialization time, you can just parent all the controls
    # directly to the toolbar's 'container' control and they will be added to
    # the toolbar automatically):
    items = List # ( HasFacets )

    #-- Private Facet Definitions ----------------------------------------------

    # Is the orientation of the toolbar vertical (True) or horizontal (False)?
    is_vertical = Bool

    # The helper object used to manage all of the child toolbar controls:
    helper = Instance( ToolbarContainer, () )

    #-- Public Methods ---------------------------------------------------------

    def create_control ( self ):
        """ Creates and returns the underlying toolkit neutral control used to
            implement the window.
        """
        control             = super( ToolbarControl, self ).create_control()
        size_policy         = ( 'fixed', 'expanding' )
        control.size_policy = (
            size_policy[ self.full_size or (not self.is_vertical) ],
            size_policy[ self.full_size or self.is_vertical ]
        )
        self.helper.set(
            owner  = self,
            parent = control
        )
        if self.theme is not None:
            self.helper.theme = self.theme

        return control


    def init ( self ):
        """ Initializes the toolbar after all controls have been added.
        """
        self.container.visible = True
        self.helper._layout_active()
        self.control.size = self.control.min_size = self.helper.min_size


    def paint_all ( self, g ):
        """ Paints the content of the window into the device context specified
            by *g*.
        """
        global scroll_themes

        dx, dy       = self.control.size
        helper       = self.helper
        scroll_theme = scroll_themes[ len( helper.hidden ) > 0 ]
        if self.is_vertical:
            y   = dy - ControlSize
            dx2 = dx / 2
            scroll_theme.fill( g, 0,   y, dx2, ControlSize )
            if helper.can_scroll_left_up:
                self._draw_image( g, tdown, 0, y, dx2, ControlSize )

            scroll_theme.fill( g, dx2, y, dx2, ControlSize )
            if helper.can_scroll_right_down:
                self._draw_image( g, tup, dx2, y, dx2, ControlSize )
        else:
            x   = dx - ControlSize
            dy2 = dy / 2
            scroll_theme.fill( g, x,   0, ControlSize, dy2 )
            if helper.can_scroll_left_up:
                self._draw_image( g, tright, x, 0, ControlSize, dy2 )

            scroll_theme.fill( g, x, dy2, ControlSize, dy2 )
            if helper.can_scroll_right_down:
                self._draw_image( g, tleft, x, dy2, ControlSize, dy2 )

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        self.helper.restore_prefs( prefs )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return self.helper.save_prefs()

    #-- Default Facet Values ---------------------------------------------------

    def _container_default ( self ):
        # Make sure our underlying control has already been created:
        self()

        return self.helper()


    def _is_vertical_default ( self ):
        return (self.orientation == 'vertical')

    #-- Window Event Handlers --------------------------------------------------

    def resize ( self, event ):
        """ Handles the window being resized.
        """
        dx, dy = self.control.client_size
        if self.is_vertical:
            self.container.bounds = ( 0, 0, dx, dy - ControlSize )
        else:
            self.container.bounds = ( 0, 0, dx - ControlSize, dy )


    def normal_left_down ( self, event ):
        """ Handles a left mouse button down event in normal mode.
        """
        x, y       = self._xy   = ( event.x, event.y )
        self.state = 'pending'
        self._scroll_amount_for( event )
        if not event.control_down:
            do_after( AutoScrollDelay, self._scroll_toolbar )


    def normal_left_dclick ( self ):
        """ Handles a left mouse button double click in normal mode.
        """
        self.helper.scroll_active( self._amount )


    def normal_wheel ( self, event ):
        """ Handles a mouse wheel event in normal mode.
        """
        self.helper.scroll_active(
            (1 + event.shift_down) * event.wheel_change * WheelScrollAmount
        )


    def normal_right_up ( self, event ):
        """ Handles a right mouse button up event in normal mode.
        """
        if self.in_control( event ):
            self.helper.begin_edit( event )


    def normal_motion ( self, event ):
        """ Handles a mouse motion event in normal mode.
        """
        self._check_tooltip( event )


    def pending_left_up ( self, event ):
        """ Handles a left mouse button up event in pending mode.
        """
        self.state = 'normal'
        if event.control_down:
            self.helper.begin_edit( event )
        else:
            self.helper.scroll_active( self._amount )


    def pending_motion ( self, event ):
        """ Handles a mouse motion event in pending mode.
        """
        self._scroll_amount_for( event )


    def scrolling_left_up ( self ):
        self.state = 'normal'


    def scrolling_motion ( self, event ):
        """ Handles a mouse motion event in scrolling mode.
        """
        self._scroll_amount_for( event )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'helper:modified' )
    def _helper_modified ( self ):
        """ Handles the helper control's 'update' event being fired.
        """
        self.refresh()


    def _items_set ( self ):
        """ Handles the 'items' facet being changed.
        """
        self.helper.update( self.items )


    def _items_items_set ( self, event ):
        """ Handles some of the contents of the 'items' list being changed.
        """
        self.helper.update( event.added, event.removed )

    #-- Private Methods --------------------------------------------------------

    def _scroll_toolbar ( self ):
        """ Performs an auto-scroll of the toolbar contents.
        """
        # Make sure we are still in 'scroll' mode:
        if self.state in ( 'pending', 'scrolling' ):
            self.helper.scroll_active( self._amount )
            self.state = 'scrolling'
            do_after( AutoScrollInterval, self._scroll_toolbar )


    def _scroll_amount_for ( self, event ):
        """ Sets the scroll amount to use based on the mouse position.
        """
        dx, dy = self.control.size
        if self.is_vertical:
            self._amount = ClickScrollAmount * (1 - (2 * (event.x < (dx / 2))))
        else:
            self._amount = ClickScrollAmount * (1 - (2 * (event.y < (dy / 2))))


    def _draw_image ( self, g, image, x, y, dx, dy ):
        """ Draws the image specified by *image* in the area specified by
            ( *x*, *y*, *dx*, *dy* ).
        """
        idx, idy = image.width, image.height
        g.draw_bitmap( image.bitmap, x + (dx - idx) / 2, y + (dy - idy) / 2 )


    def _check_tooltip ( self, event ):
        """ Sets the appropriate tooltip based on the mouse position specified
            by *event*.
        """
        left    = self.helper.can_scroll_left_up
        right   = self.helper.can_scroll_right_down
        left_up = ((event.x < (self.control.size[0] / 2)) if self.is_vertical
                   else (event.y < (self.control.size[1] / 2)))
        tooltip = ''
        if (left_up and left) or ((not left_up) and right):
            tooltip = ('Left click to scroll.\n'
                       'Left click and hold to auto-scroll.')

        if left or right:
            tooltip += '\nUse mouse wheel to scroll.'

        tooltip += '\nRight click to edit.'
        n        = len( self.helper.hidden )
        if n > 0:
            tooltip += '\nThere %s %s' % ( 'is' if n == 1 else 'are',
                                           plural_of( n, '%s hidden item%s.' ) )

        self.control.tooltip = tooltip.strip()

#-- EOF ------------------------------------------------------------------------
