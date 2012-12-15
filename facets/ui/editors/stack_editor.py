"""
A GUI-toolkit independent editor for displaying list items as a vertically or
horizontally scrollable collection of variable-sized items with custom renderers
and event handlers.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, BasicEditorFactory, Any, Range,        \
           ATheme, Bool, Callable, Str, Enum, Event, Instance, List, Property, \
           Editor, Control, Graphics, on_facet_set, implements, toolkit

from facets.ui.constants \
    import scrollbar_dx, scrollbar_dy

from facets.ui.i_filter \
    import IFilter

from facets.ui.i_stack_item \
    import IStackItem, StrStackItem, IStackContext

from facets.ui.pyface.timer.api \
    import do_later, do_after

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def default_adapter ( item ):
    """ Returns the default adaptation of a StackEditor item to the IStackItem
        interface.
    """
    return item

#-------------------------------------------------------------------------------
#  'StackContext' class:
#-------------------------------------------------------------------------------

class StackContext ( HasPrivateFacets ):
    """ Implementation of the IStackContext interface used by the stack editor.
    """

    implements( IStackContext )

    #-- Interface Facet Definitions --------------------------------------------

    # The graphics context the item can use for performing requests like text
    # size measurement:
    graphics = Instance( Graphics )

    # The control the item is contained in:
    control = Instance( Control )

    # The object that 'owns' the item:
    owner = Instance( HasFacets )

    #-- Interface Methods ------------------------------------------------------

    def select ( self, item ):
        """ Adds the specified stack *item* to the current selection (if
            possible).
        """
        self.owner.select( item )

#-------------------------------------------------------------------------------
#  '_StackEditor' class:
#-------------------------------------------------------------------------------

class _StackEditor ( Editor ):
    """ A GUI-toolkit independent editor for displaying list items as a
        vertically or horizontally scrollable collection of variable-sized items
        with custom renderers and event handlers.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Indicate that the editor is resizable. This value overrides the default.
    scrollable = True

    # The list of all items being edited:
    all_items = List # ( IStackItem )

    # The filtered list of items being edited:
    items = List # ( IStackItem )

    # The currently selected stack item (if any):
    selected_stack_item = Any

    # The currently selected item (if any):
    selected = Any

    # Event fired when the editor needs to re-synchronize with its data:
    changed = Event

    # Event fired when specific item facets are modified:
    item_changed = Event

    # A set that captures any pending item_changed events:
    item_changed_pending = Any # (None or set(string))

    # The (optional) IFilter object used to filter the items to display:
    filter = Instance( IFilter )

    # The global 'level of detail' setting for all items displayed:
    lod = Range( 0, facet_value = True )

    # The maximum 'level of detail' setting for all editor items:
    maximum_lod = Range( 0, facet_value = True )

    # Is the stacker oriented vertically?
    is_vertical = Bool

    # The theme to use for the background:
    theme = ATheme

    # The context object provided to each StackItem:
    context = Instance( StackContext, () )

    # The stack item currently having the mouse capture (if any):
    capture = Any

    # The stack item currently having keyboard focus (if any):
    focus = Any

    # The item the most recent mouse event was sent to (if any):
    mouse_item = Any

    # The control used to draw the stack items:
    stacker = Instance( Control )

    # The bounds of the stacker control drawing area:
    content_bounds = Property

    # The virtual size to be set after the mouse capture is released:
    pending_virtual_size = Any # None or (dx,dy) tuple

    #-- Editor Method Overrides ------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Initialize factory provided level of detail settings:
        self.lod         = factory.facet_value( 'lod' )
        self.maximum_lod = factory.facet_value( 'maximum_lod' )
        self.is_vertical = (factory.orientation == 'vertical')
        self.theme       = factory.theme

        # Initialize and create the underlying stacker control:
        self.adapter = control = toolkit().create_scrolled_panel( parent )
        stacker      = toolkit().create_control( control, handle_keys = True )
        control.content = self.stacker = stacker

        # Initialize the StackContext object provided to each stack item:
        self.context.facet_set(
            graphics = stacker.temp_graphics,
            control  = stacker,
            owner    = self
        )

        # Initialize the various control event handlers:
        control.set_event_handler(
            size = self._size
        )

        stacker.set_event_handler(
            paint     = self._paint,
            mouse     = self._mouse,
            key_press = self._key,
            key       = self._key
        )

        # Allow the editor to expand both horizontally and vertically:
        control.size_policy = ( 'expanding', 'expanding' )
        control.min_size    = ( 40, 40 )

        # Set up the additional 'list items changed' event handler needed for
        # a list based facet:
        self.context_object.on_facet_set(
            self.update_editor_item, self.extended_name + '_items?',
            dispatch = 'ui'
        )

        # Set up the item filter:
        self.sync_value( factory.filter, 'filter', 'from' )

        # Set up selection synchronization:
        self.sync_value( factory.selected, 'selected', 'both' )
        if factory.selected != '':
            self.on_facet_set( self._selected_modified, 'items:selected' )

        # Set up external change synchronization:
        self.sync_value( factory.changed, 'changed', 'from' )

        # Add the developer specified tooltip information:
        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.item_changed_pending = set()
        af = self._adapter_for
        self.all_items = [ af( item ) for item in self.value ]
        self._dispatch_pending()


    def update_editor_item ( self, event ):
        """ Handles items in the editor's list content being added or removed.
        """
        self.item_changed_pending = set()
        add_to_bottom = ((event.index == len( self.all_items )) and
                         (len( event.removed ) == 0)            and
                         (len( event.added ) > 0))
        af = self._adapter_for
        self.all_items[ event.index: event.index + len( event.removed ) ] = \
            [ af( item ) for item in event.added ]
        self._dispatch_pending()

        # If new content was added to the bottom of the stack, automatically
        # scroll the control so that the new content is visible:
        # Note: Doing this automatically may not always be desirable. If not,
        # then we can add an option to the editor factory to enable/disable it.
        if add_to_bottom:
            if self.is_vertical:
                do_after( 100, self.adapter.scroll_to, 0, None )
            else:
                do_after( 100, self.adapter.scroll_to, None, 0 )


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        del self.all_items[:]
        del self.items[:]

        self.adapter.unset_event_handler(
            size = self._size
        )

        if self.factory.selected != '':
            self.on_facet_set( self._selected_modified, 'items:selected',
                               remove = True )

        self.stacker.unset_event_handler(
            paint     = self._paint,
            mouse     = self._mouse,
            key_press = self._key,
            key       = self._key
        )

        super( _StackEditor, self ).dispose()


    def select ( self, item ):
        """ Adds the specified stack *item* to the current selection (if
            possible).
        """
        # fixme: This is just a temporary single item selection hack...
        item.selected = True

    #-- Property Implementations -----------------------------------------------

    def _get_content_bounds ( self ):
        wdx, wdy = self.adapter.size
        if self.theme is None:
            return ( 0, 0, wdx, wdy )

        return self.theme.bounds( 0, 0, wdx, wdy )

    #-- Facet Event Handlers ---------------------------------------------------

    def _item_changed_set ( self, item ):
        """ Handles an item facet of interest to the editor being modified.
        """
        pending = self.item_changed_pending
        if pending is not None:
            pending.add( item )
        else:
            getattr( self, '_item_%s_modified' % item )()


    def _item_maximum_lod_modified ( self ):
        """ Handles one of the stacker items changing its maximum level of
            detail setting.
        """
        self.maximum_lod = reduce( lambda x, y: max( x, y.maximum_lod ),
                                   self.items, 0 )


    def _item_size_modified ( self ):
        """ Handles the size of the displayed items being modified.
        """
        if self._updating_size:
            self._resized = True
        else:
            do_later( self._update_size )


    def _item_lod_modified ( self ):
        """ Handles the visual appearance of the displayed items being modified.
        """
        self.stacker.refresh()

    _item_refresh_modified = _item_lod_modified


    @on_facet_set( 'items' )
    def _items_updated ( self ):
        """ Handles the contents of the 'items' list being changed.
        """
        self._item_maximum_lod_modified()
        self._item_size_modified()


    @on_facet_set( 'changed, filter.changed, all_items' )
    def _items_modified ( self ):
        items  = self.all_items
        filter = self.filter
        if filter is not None:
            filter = filter.filter
            items  = [ item for item in items if filter( item ) ]

        # Reset any special items that are no longer in the list:
        self.capture    = self._validate_item( self.capture,    items )
        self.focus      = self._validate_item( self.focus,      items )
        self.mouse_item = self._validate_item( self.mouse_item, items )

        # Save the new filtered set of items:
        self.items = items


    def _selected_modified ( self, object, new ):
        """ Handles a stack item's 'selected' facet being changed.
        """
        if not self._no_update:
            self._no_update = True

            if new:
                if self.selected_stack_item is not None:
                    self.selected_stack_item.selected = False

                self.selected_stack_item = object
                self.selected            = object.item
            elif object is self.selected_stack_item:
                self.selected_stack_item = self.selected = None

            self._no_update = False

            self.stacker.refresh()


    def _selected_set ( self, item ):
        """ Handles the 'selected' facet being changed.
        """
        if not self._no_update:
            stack_item = None
            if (isinstance( item, HasFacets ) and
                item.has_facets_interface( IStackItem )):
                if item in self.all_items:
                    stack_item = item
            elif item is not None:
                for a_stack_item in self.all_items:
                    if item is a_stack_item.item:
                        stack_item = a_stack_item

                        break

            self.selected_stack_item = stack_item

    #-- Control Event Handlers -------------------------------------------------

    def _size ( self, event ):
        """ Handles the size of the scroll control being modified.
        """
        self._update_size()
        event.handled = False


    def _mouse ( self, event ):
        """ Handles routing a mouse event to the appropriate stack item (if
            any).
        """
        name = event.name
        if name == 'leave':
            self._mouse_leave( event )
        elif name == 'enter':
            if self.factory.auto_focus:
                self.stacker.set_focus()
        else:
            item = self.capture
            x, y = event.x, event.y
            if item is None:
                item = self._find_at( x, y )

            # Check to see if we entered a new item:
            self._mouse_enter( event, item )

            if item is not None:
                # Save the current size of the item (in case the event
                # handler modifies it):
                size = item.bounds[2:]

                # fixme: We may need to adjust the event (x,y) value here...
                # Send the event to the item:
                event.handled = False
                item.mouse    = event

                if (name == 'wheel') and (not event.handled):
                    # Use shift-wheel events to scroll the window or to change
                    # the global level of detail:
                    self._mouse_wheel( event )
                else:
                    # Now, check to see if the size of the item changed:
                    self._check_size( item, size )

                    # Process any keyboard focus change:
                    focus_item = self.focus
                    if item.focus and (item is not focus_item):
                        if focus_item is not None:
                            focus_item.focus = False

                        self.focus = item

                    # Synchronize the item's cursor with the control's cursor:
                    self.stacker.cursor = item.cursor

                    # Set the current mouse capture:
                    if not item.capture:
                        item = None

                    self.capture = item

                event.handled = True

                # This code fixes a Qt problem that causes the control to lose
                # keyboard focus when the mouse wheel changes:
                if (name == 'wheel') and self.factory.auto_focus:
                    self.stacker.set_focus()

                self._mouse_enter( event, self._find_at( x, y ) )


    def _mouse_enter ( self, event, item ):
        if item is not self.mouse_item:
            self._mouse_leave( event )

            if item is not None:
                name       = event.name
                event.name = 'enter'
                item.mouse = event
                event.name = name

            self.mouse_item = item


    def _mouse_leave ( self, event ):
        """ If there is a current mouse item, send it a mouse 'leave' event.
        """
        item = self.mouse_item
        if item is not None:
            name            = event.name
            event.name      = 'leave'
            item.mouse      = event
            event.name      = name
            self.mouse_item = None


    def _mouse_wheel ( self, event ):
        """ Handles a mouse wheel change by increasing or decreasing the global
            level of detail for the editor.
        """
        if event.shift_down:
            if event.wheel_change < 0:
                if self.lod > 0:
                    self.lod -= 1
            elif self.lod < self.maximum_lod:
                self.lod += 1

            self._set_lod( self.lod )
        else:
            delta = 75 * ((2 * (event.wheel_change < 0)) - 1)
            if self.is_vertical:
                self.adapter.scroll_by( y = delta )
            else:
                self.adapter.scroll_by( x = delta )


    def _key ( self, event ):
        """ Handles keyboard events by routing them to the correct stack item.
        """
        item = self.focus
        if item is None:
            item = self.mouse_item

        if item is not None:
            # Save the current size of the item (in case the event handler
            # modifies it):
            size = item.bounds[2:]

            # Send the event to the item:
            item.keyboard = event

            # Now, check to see if the size of the item changed:
            self._check_size( item, size )

            if self.focus is None:
                do_after( 100, self._mouse_at )


    def _paint ( self, event ):
        """ Handles redrawing the contents of the control.
        """
        from facets.ui.pyface.image_slice import paint_parent

        stacker = self.stacker
        g       = stacker.graphics.graphics_buffer()

        # Repaint the parent's theme (if necessary):
        paint_parent( g, stacker )

        # Calculate the size of the area to be repainted:
        cdx, cdy = stacker.client_size
        vdx, vdy = stacker.virtual_size
        wdx, wdy = max( cdx, vdx ), max( cdy, vdy )

        # Draw the background theme (if any):
        if self.theme is not None:
            self.theme.fill( g, 0, 0, wdx, wdy )

        # Draw each of the stacker items (using the appropriate orientation):
        items = self.items
        if len( items ) > 0:
            bx, by, bdx, bdy = bounds = stacker.visible_bounds
            low   = self._item_at( bx, by )
            high  = self._item_at( bx + bdx - 1, by + bdy - 1 ) + 1
            for i in xrange( low, high ):
                items[i].paint( g, bounds )

        g.copy()

    #-- Private Methods --------------------------------------------------------

    def _adapter_for ( self, item ):
        """ Returns the initialized IStackItem adapter for the specified item
            (or None if it cannot be adapted).
        """
        stack_item = self.factory.adapter( item )
        if ((not isinstance( stack_item, HasFacets )) or
            (not stack_item.has_facets_interface( IStackItem ))):
            stack_item = StrStackItem()

        # Note: Make sure that the context is set prior to the item in case the
        # stack item uses the context to compute size when the item is changed:
        stack_item.context = self.context

        # Set the editor's current level of detail if the item has the default
        # level:
        if stack_item.lod == 0:
            stack_item.lod = self.lod

        # If a new stack item was created, make sure its item refers to the
        # original item:
        if stack_item is not item:
            stack_item.item = item

        return stack_item


    def _dispatch_pending ( self ):
        """ Dispatches any pending 'item_changed' events, then clears the
            pending set.
        """
        for name in self.item_changed_pending:
            getattr( self, '_item_%s_modified' % name )()

        self.item_changed_pending = None


    def _mouse_at ( self ):
        """ Set the current mouse item based on the current screen position of
            the mouse pointer.
        """
        mx, my          = self.stacker.mouse_position
        cx, cy          = self.stacker.screen_position
        self.mouse_item = self._find_at( mx - cx, my - cy )


    def _find_at ( self, x, y ):
        """ Returns the item at the specified (x,y) location, or None if no item
            is at that location.
        """
        cx  = cy = 0
        cdx, cdy = self.stacker.size
        if self.theme is not None:
            cx, cy, cdx, cdy = self.theme.bounds( cx, cy, cdx, cdy )

        items = self.items
        if (len( items ) == 0) or (x < cx) or (y < cy):
            return None

        ix, iy, idx, idy = items[-1].bounds
        if self.is_vertical:
            is_in = ((x < (cx + cdx)) and (y < (iy + idy)))
        else:
            is_in = ((x < (ix + idx)) and (y < (cy + cdy)))

        if not is_in:
            return None

        return items[ self._item_at( x, y ) ]


    def _item_at ( self, x, y ):
        """ Returns the index of the item containing a specified (x,y) location
            using a binary search. If the point is outside the bounds of any
            item, the index of the nearest item is returned.
        """
        items = self.items
        low   = 0
        high  = len( items ) - 1
        if self.is_vertical:
            if y < items[ low ].bounds[1]:
                return low

            ix, iy, idx, idy = items[ high ].bounds
            if y >= (iy + idy):
                return high

            while True:
                mid  = (low + high) / 2
                item = items[ mid ]
                ix, iy, idx, idy = item.bounds

                # Quit if there is something wrong with the bounds list:
                if high <= low:
                    return mid

                if y < iy:
                    high = mid - 1
                elif y >= (iy + idy):
                    low = mid + 1
                else:
                    return mid

        if x < items[ low ].bounds[0]:
            return low

        ix, iy, idx, idy = items[ high ].bounds
        if x >= (ix + idx):
            return high

        while True:
            mid  = (low + high) / 2
            item = items[ mid ]
            ix, iy, idx, idy = item.bounds

            # Quit if there is something wrong with the bounds list:
            if high <= low:
                return mid

            if x < ix:
                high = mid - 1
            elif x >= (ix + idx):
                low = mid + 1
            else:
                return mid


    def _validate_item ( self, item, items ):
        """ Returns the *item* if it is in the specified list of *items*;
            otherwise it returns None.
        """
        if (item is not None) and (item in items):
            return item

        return None


    def _check_size ( self, item, size ):
        """ Checks to see of the current size of a specified *item* is
            different that the specified *size* (i.e. (dx,dy)). If so, scroll
            the view so that the item is still in the view as much as possible.
        """
        if item.bounds[2:] != size:
            self._ensure_visible( item )


    def _ensure_visible ( self, item ):
        """ Make sure that as much of the specified *item* is visible as
            possible.
        """
        ix, iy, idx, idy = item.bounds
        if self.is_vertical:
            self.adapter.scroll_to( 0, iy + idy - 1 )
            self.adapter.scroll_to( 0, iy )
        else:
            self.adapter.scroll_to( ix + idx - 1, 0 )
            self.adapter.scroll_to( ix, 0 )


    def _update_size ( self ):
        """ Recalculates the size of the stacker based upon its current
            contents.
        """
        # Handle the editor already in the process of being closed:
        if self.adapter is None:
            return

        content_bounds      = self.content_bounds
        is_vertical         = self.is_vertical
        self._updating_size = True
        has_scrollbar       = False
        while True:
            self._resized    = False
            sx, sy, sdx, sdy = content_bounds
            cdx, cdy         = self.adapter.client_size
            csdx, csdy       = cdx - sdx, cdy - sdy
            dx = dy          = 0
            if is_vertical:
                for item in self.items:
                    idx, idy = item.min_size
                    dx       = max( dx, idx )
                    dy      += idy

                dx += csdx
                dy += csdy
                if (dy > cdy) or has_scrollbar:
                    has_scrollbar = True
                    cdx          -= scrollbar_dx

                dx  = max( dx, cdx )
                idx = dx - csdx

                for item in self.items:
                    idy         = item.size[1]
                    item.bounds = ( sx, sy, idx, idy )
                    sy         += idy
            else:
                for item in self.items:
                    idx, idy = item.min_size
                    dx      += idx
                    dy       = max( dy, idy )

                dy += csdy
                dx += csdx
                if (dx > cdx) or has_scrollbar:
                    has_scrollbar = True
                    cdy          -= scrollbar_dy

                dy  = max( dy, cdy )
                idy = dy - csdy

                for item in self.items:
                    idx         = item.size[0]
                    item.bounds = ( sx, sy, idx, idy )
                    sx         += idx

            if not self._resized:
                break

        self._updating_size = False

        # Always allow the virtual size to get larger along the scroll axis, but
        # only allow it to get smaller if no mouse capture is in effect since it
        # can cause very jerky results when the user is dragging something that
        # changes the size of the view. In this case, save the new virtual size
        # and schedule the size update for later:
        vdx, vdy = self.stacker.virtual_size
        if ((self.capture is not None) and
            ((is_vertical and (vdy > dy)) or
             ((not is_vertical) and (vdx > dx)))):
            self.pending_virtual_size = ( dx, dy )
            do_after( 250, self._update_virtual_size )
        else:
            self.stacker.virtual_size = ( dx, dy )
            self.stacker.refresh()


    def _update_virtual_size ( self ):
        """ Attempt to perform a virtual size update that has been deferred. If
            the pending size is None, then the update has already been performed
            and can be ignored.

            If mouse capture is still in effect, then reschedule the update for
            later. Otherwise, perform the requested update.
        """
        if self.pending_virtual_size is not None:
            if self.capture is None:
                self.stacker.virtual_size = self.pending_virtual_size
                self.pending_virtual_size = None
            else:
                do_after( 250, self._update_virtual_size )


    def _set_lod ( self, lod ):
        """ Set the level of detail for all items to *lod* (if the value of
            *lod* is valid for the item.
        """
        for item in self.items:
            if lod <= item.maximum_lod:
                item.lod = lod

#-------------------------------------------------------------------------------
#  'StackEditor' class:
#-------------------------------------------------------------------------------

class StackEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The class used to construct editor objects:
    klass = _StackEditor

    # The adapter used to adapt items to the IStackItem interface. If an editor
    # item does not implement IStackItem, the editor will call the adapter
    # function with the item as argument. The adapter function must return
    # either an object that implements IStackItem or None (in which case the
    # editor will exclude the item):
    adapter = Callable( default_adapter )

    # The optional extended name of the facet that the current selection is
    # synced with:
    selected = Str

    # The optional extended name of the facet that indicates when the editor
    # needs to re-synchronize with its data:
    changed = Str

    # The global 'level of detail' setting for all items displayed:
    lod = Range( 0, facet_value = True )

    # The maximum 'level of detail' setting for all editor items:
    maximum_lod = Range( 0, facet_value = True )

    # The optional extended facet name of the IFilter object used to filter the
    # items displayed. If not specified, no filtering is applied:
    filter = Str

    # The orientation of the editor:
    orientation = Enum( 'vertical', 'horizontal' )

    # The theme to use for the editor 'background':
    theme = ATheme

    # Should the editor set keyboard focus on the mouse entering the editor?
    auto_focus = Bool( False, facet_value = True )

#-- EOF ------------------------------------------------------------------------
