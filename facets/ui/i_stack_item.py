"""
Defines the IStackItem interface that any items displayed by a StackEditor must
implement.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, Interface, Bool, Str, Int, Range,   \
           Tuple, Enum, List, Event, Instance, Any, ATheme, Font, Property, \
           Control, Graphics, UIEvent, Undefined, implements, on_facet_set, \
           property_depends_on

from facets.ui.constants \
    import TOP, LEFT, CENTER, RIGHT

from facets.ui.ui_facets \
    import Image, Alignment

from facets.ui.graphics_text \
    import GraphicsText

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The mapping from 'alignment' names to theme alignment values:
AlignmentMap = {
    'left':   (TOP | LEFT),
    'center': (TOP | CENTER),
    'right':  (TOP | RIGHT)
}

# The mapping from a boolean selection state to a selection name:
SelectedName = ( 'unselected', 'selected' )

# The different types of popup views:
PopupTypes = ( 'popup', 'popout', 'popover', 'info' )

# Mapping from keyboard characters to names:
KeyMap = {
    ',':  'comma',
    '.':  'period',
    '/':  'slash',
    '\\': 'backslash',
    '-':  'minus',
    '+':  'plus',
    '[':  'left_bracket',
    ']':  'right_bracket',
    '{':  'left_brace',
    '}':  'right_brace',
    '(':  'left_parenthesis',
    ')':  'right_parenthesis',
    '<':  'less_than',
    '>':  'greater_than',
    '\'': 'quote',
    '"':  'doublequote',
    ':':  'colon',
    ';':  'semicolon',
    '|':  'bar',
    '`':  'backquote',
    '~':  'tilde',
    '!':  'exclamation',
    '@':  'at',
    '#':  'pound',
    '$':  'dollar',
    '%':  'percent',
    '^':  'caret',
    '&':  'ampersand',
    '*':  'asterisk',
    '_':  'underscore',
    '=':  'equal'
}

#-------------------------------------------------------------------------------
#  'IStackContext' interface:
#-------------------------------------------------------------------------------

class IStackContext ( Interface ):
    """ The IStackContext interface describes information and services provided
        by its containing environment to an object implementing the IStackItem
        interface.
    """

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

            Note that a simple single item selection model can be implemented
            by setting a stack item's 'selected' facet True. Similarly, stack
            items can be unselected by setting the 'selected' facet to False.
        """

#-------------------------------------------------------------------------------
#  'IStackItemTool' Interface:
#-------------------------------------------------------------------------------

class IStackItemTool ( Interface ):
    """ Defines the interface that any tool associated with a stack item must
        implement.
    """

    #-- Interface Methods ------------------------------------------------------

    def paint ( self, item, g, bounds ):
        """ Paints the tool in the specified item using the specified graphics
            context. *Bounds* is a tuple of the form (x, y, dx, dy) specifying
            the visible bounds of the control, and can be used for optimizing
            graphics updates.
        """


    def mouse_event ( self, item, event ):
        """ Handles the mouse event specified by *event* for the stack item
            specified by *item*. Returns True if the event was handled. Any
            other result means that the event has not been handled.
        """

#-------------------------------------------------------------------------------
#  'IStackItem' Interface:
#-------------------------------------------------------------------------------

class IStackItem ( Interface ):

    #-- Facet Definitions ------------------------------------------------------

    #-- Editor/Item Initiated/Defined ------------------------------------------

    # Is the item selected?
    selected = Bool

    # The current 'level of detail' displayed by the item:
    lod = Range( 0 )

    #-- Item Initiated/Defined -------------------------------------------------

    # The maximum 'level of detail' supported by the item:
    maximum_lod = Range( 0 )

    # The current size of the item in the form (width,height):
    size = Tuple( Int, Int )

    # The minimum size the item will accept, in the form (width,height):
    min_size = Tuple( Int, Int )

    # The cursor shape the mouse should have while over the item:
    cursor = Str

    # The tooltip that should be displayed while the mouse is over the item:
    tooltip = Str

    # Does the item currently have the mouse capture?
    capture = Bool

    # Does the item currently have keyboard focus?
    focus = Bool

    # Event fired when the item should be deleted from the list:
    delete = Event

    # Event fired when an item should be refreshed (i.e. re-painted):
    refresh = Event

    #-- Editor Initiated/Defined ---------------------------------------------------

    # The item being adapted:
    item = Any

    # The context the item is associated with:
    context = Instance( IStackContext )

    # The current bounds of the item within the containing stack:
    bounds = Tuple( Int, Int, Int, Int )

    # The current bounds of the item on the screen:
    screen_bounds = Property

    # Information about a mouse event that occurs over the item:
    mouse = Event( UIEvent )

    # Information about a keyboard event for the item:
    keyboard = Event( UIEvent )

    #-- Interface Methods ------------------------------------------------------

    def paint ( self, g, bounds ):
        """ Paints the item in the specified graphics context. *Bounds* is a
            tuple of the form (x, y, dx, dy) specifying the visible bounds of
            the control, and can be used for optimizing graphics updates.
        """

#-------------------------------------------------------------------------------
#  'AbstractStackItem' class:
#-------------------------------------------------------------------------------

class AbstractStackItem ( HasPrivateFacets ):
    """ Abstract implementation of the IStackItem interface which can be used as
        a base class for other IStackItem implementations.
    """

    implements( IStackItem )

    #-- Facet Definitions ------------------------------------------------------

    #-- Editor/Item Initiated/Defined ------------------------------------------

    # Is the item selected?
    selected = Bool( False )

    # The current 'level of detail' displayed by the item:
    lod = Range( 0 )

    #-- Item Initiated/Defined -------------------------------------------------

    # The maximum 'level of detail' supported by the item:
    maximum_lod = Range( 0 )

    # The current size of the item in the form (width,height):
    size = Tuple( Int, Int )

    # The minimum size the item will accept, in the form (width,height):
    min_size = Property # Tuple( Int, Int )

    # The cursor shape the mouse should have while over the item:
    cursor = Str( 'arrow' )

    # The tooltip that should be displayed while the mouse is over the item:
    tooltip = Str

    # Does the item currently have the mouse capture?
    capture = Bool( False )

    # Does the item currently have keyboard focus?
    focus = Bool( False )

    # Event fired when the item should be deleted from the list:
    delete = Event

    # Event fired when an item should be refreshed (i.e. re-painted):
    refresh = Event

    #-- Editor Initiated/Defined ---------------------------------------------------

    # The item being adapted:
    item = Any

    # The context the item is associated with:
    context = Instance( IStackContext )

    # The current bounds of the item within the containing stack:
    bounds = Tuple( Int, Int, Int, Int )

    # The current bounds of the item on the screen:
    screen_bounds = Property

    # Information about a mouse event that occurs over the item:
    mouse = Event( UIEvent )

    # Information about a keyboard event for the item:
    keyboard = Event( UIEvent )

    #-- Interface Methods ------------------------------------------------------

    def paint ( self, g, bounds ):
        """ Paints the item in the specified graphics context. *Bounds* is a
            tuple of the form (x, y, dx, dy) specifying the visible bounds of
            the control, and can be used for optimizing graphics updates.
        """

    #-- Property Implementations -----------------------------------------------

    def _get_min_size ( self ):
        return self.size


    def _get_screen_bounds ( self ):
        ix, iy, idx, idy = self.bounds
        cx, cy           = self.context.control.screen_position

        return ( cx + ix, cy + iy, idx, idy )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, item = None, **facets ):
        """ Initializes the object.
        """
        super( AbstractStackItem, self ).__init__( **facets )

        if item is not None:
            self.item = item


    def popup_for ( self, view = None, kind = None ):
        """ Displays a popup editor using the specified view.
            The view can either be None, a View object or a ViewElement
            (such as a Group or Item). If None is specified, a View for the
            current adapter facet will be created.
        """
        view = self.facet_view( view )

        control           = self.context.control
        sx, _             = control.screen_position
        _, my             = control.mouse_position
        x, _, dx, _       = self.bounds
        view.popup_bounds = ( x + sx, my - 1, dx, 2 )

        if (kind is None) and (view.kind not in PopupTypes):
            kind = 'popup'

        self.edit_facets( view = view, kind = kind, parent = control )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'lod, maximum_lod, size, refresh' )
    def _facet_modified ( self, facet ):
        """ Handles a facet of interest to the item owner being modified.
        """
        if self.context is not None:
            self.context.owner.item_changed = facet


    def _tooltip_set ( self, tooltip ):
        """ Handles the 'tooltip' facet being modified.
        """
        self.context.control.tooltip = tooltip

#-------------------------------------------------------------------------------
#  'BaseStackItem' class:
#-------------------------------------------------------------------------------

class BaseStackItem ( AbstractStackItem ):
    """ An implementation of the IStackItem interface which adds a layer of
        automatic event routing to the AbstractStackItem.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of active tools for the item:
    tools = List( IStackItemTool )

    # The font to use for rendering the item:
    font = Font

    # The theme to use when rendering the item:
    theme = ATheme( '@facets:stack_item' )

    # The current global state of the item:
    state = Str

    # The current mouse state of the item:
    mouse_state = Str

    # The current keyboard state of the item:
    keyboard_state = Str

    # The current paint state of the item:
    paint_state = Str

    # The current theme state of the item:
    theme_state = Str

    # The current font state of the item:
    font_state = Str

    # The current theme being used:
    current_theme = Property

    # The current font being used:
    current_font = Property

    #-- Private Facets ---------------------------------------------------------

    # Used for theme conversions:
    _theme = ATheme

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'theme_state, theme, state, selected, lod' )
    def _get_current_theme ( self ):
        self._theme = self.value_of( 'theme', self.theme_state )

        return self._theme


    @property_depends_on( 'font_state, font, state, selected, lod' )
    def _get_current_font ( self ):
        return self.value_of( 'font', self.font_state )

    #-- Facet Event Handlers ---------------------------------------------------

    def _mouse_set ( self, event ):
        """ Handles the 'mouse' event being fired.
        """
        # Give all of the currently defined tools a chance to handle the mouse
        # event first:
        for tool in self.tools:
            if tool.mouse_event( self, event ) is True:
                event.handled = True

                return

        method = self.lookup( event.name, self.mouse_state )
        if method is not None:
            method( event )


    def _keyboard_set ( self, event ):
        """ Handles the 'keyboard' event being fired.
        """
        key_code = event.key_code
        if len( key_code ) == 1:
            key_code = KeyMap.get( key_code, key_code )
        else:
            key_code = key_code.lower().replace( '-', '_' )

        method = None
        if key_code != '':
            method = self.lookup( '%s_%s' % ( event.name, key_code ),
                                  self.keyboard_state )

        if method is None:
            method = self.lookup( event.name, self.keyboard_state )

        if method is not None:
            method( event )


    @on_facet_set( 'current_theme, current_font, paint_state, context' )
    def _visuals_modified ( self ):
        """ Handles any facet affecting the visual appearance of the item being
            modified.
        """
        if self.context is not None:
            self.refresh = True

    #-- Mouse Event Handlers ---------------------------------------------------

    def wheel ( self, event ):
        """ Handles a mouse wheel change by increasing or decreasing the level
            of detail for the item.
        """
        if event.control_down and (not event.shift_down):
            event.handled = True
            if event.wheel_change < 0:
                if self.lod > 0:
                    self.lod -= 1
            elif self.lod < self.maximum_lod:
                self.lod += 1

    #-- IStackItem Interface Methods -------------------------------------------

    def paint ( self, g, bounds ):
        """ Paints the item in the specified graphics context. *Bounds* is a
            tuple of the form (x, y, dx, dy) specifying the visible bounds of
            the control, and can be used for optimizing graphics updates.
        """
        theme = self.current_theme
        x, y, dx, dy = self.bounds
        theme.fill( g, x, y, dx, dy )

        font = self.current_font
        if font is not None:
            g.font = font

        self.lookup( 'paint_item', self.paint_state )( g, bounds )

        # Allow the currently defined tools to paint their contents over the
        # item:
        for tool in self.tools:
            tool.paint( self, g, bounds )


    def paint_item ( self, g, bounds ):
        """ Default handler for painting the content of the item using the
            specified graphics context *g*. *Bounds* is a tuple of the form
            (x, y, dx, dy) specifying the visible bounds of the control, and can
            be used for optimizing graphics updates.

            This method should either be subclasses or another custom paint
            handler based on object state using the various routing rules
            should be defined (e.g. 'paint_item_for_1').
        """

    #-- Public Methods ---------------------------------------------------------

    def add_tool ( self, *tools ):
        """ Adds the specified list of *tools* to the list of tools for the
            item.
        """
        self.tools.extend( tools )


    def remove_tool ( self, *tools ):
        """ Removes the specified tool from the list of tools for the item.
        """
        for tool in tools:
            if tool in self.tools:
                self.tools.remove( tool )


    def value_of ( self, name, modifier = '' ):
        """ Looks up the value of a custom object attribute whose name is based
            on various combinations of a custom modifier, the current state, the
            name of the attribute and the current level of detail being
            displayed. If an attribute is found, and it is callable, the result
            of calling it with no arguments is returned; otherwise the attribute
            itself is returned. If no attribute is found, None is returned.
        """
        value = self.lookup( name, modifier )
        if callable( value ):
            value = value()

        return value


    def lookup ( self, name, modifier = '' ):
        """ Looks up the value of a custom object attribute whose name is based
            on various combinations of a custom modifier, the current state, the
            name of the attribute and the current level of detail being
            displayed.
        """
        lod      = 'for_%d' % self.lod
        selected = SelectedName[ self.selected ]

        if modifier != '':
            value = self._lookup( selected, '%s_%s' % ( modifier, name ), lod )
            if value is not None:
                return value

        if self.state != '':
            value = self._lookup( selected, '%s_%s' % ( self.state, name ),
                                  lod )
            if value is not None:
                return value

        return self._lookup( selected, name, lod )

    #-- Private Methods --------------------------------------------------------

    def _lookup ( self, selected, name, lod ):
        """ Looks up a custom object attribute whose name is of the form
            'selected_name_lod', 'selected_name', 'name_lod' or 'name'.
        """
        value = getattr( self, '%s_%s_%s' % ( selected, name, lod ), None )
        if value is not None:
            return value

        value = getattr( self, '%s_%s' % ( selected, name ), None )
        if value is not None:
            return value

        value = getattr( self, '%s_%s' % ( name, lod ), None )
        if value is not None:
            return value

        return getattr( self, name, None )

#-------------------------------------------------------------------------------
#  'StrStackItem' class:
#-------------------------------------------------------------------------------

class StrStackItem ( BaseStackItem ):
    """ An implementation of the IStackItem interface which renders its item as
        a themed multi-line string.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The text value rendered for the item:
    text = Str

    # An optional image to display with the text:
    image = Image

    # The alignment of the text and optional image:
    alignment = Alignment

    # The (optional) label value rendered for the item:
    label = Str

    # An optional image to display with the label:
    label_image = Image

    # The horizontal alignment of the label:
    label_alignment = Enum( 'left', 'center', 'right' )

    # Event fired when the contents of the item need to be recomputed:
    update = Event

    # Event fired when the label or item text needs to be re-evaluated:
    reset = Event

    #-- Private Facet Definitions ----------------------------------------------

    # The GraphicsText object used to represent the text and image:
    gtext = Instance( GraphicsText )

    # The GraphicsText object used to represent the label text and image:
    ltext = Instance( GraphicsText )

    #-- Public Methods ---------------------------------------------------------

    def text_value ( self ):
        """ Returns the string text value used to render the item. The default
            implementation simply calls str(item), but can be overridden to
            return some other value.
        """
        value = str( self.item )
        if (self.maximum_lod != 0) and (self.lod == 0):
            lines = value.split( '\n' )
            if len( lines ) > 1:
                value = self.text_value_0( lines )

        return value


    def text_value_0 ( self, lines ):
        """ Returns the string text value to display in cases where the minimum
            level of detail is being displayed for the multi-line value
            specified by *lines*.
        """
        return '%s [%d]' % ( lines[0], len( lines ) )


    def image_value ( self ):
        """ Returns the text image value used to render the item. The default
            implementation simply returns Undefined (indicating that there is no
            text image to display).
        """
        return Undefined


    def label_value ( self ):
        """ Returns the string value used to render the item's label. The
            default implementation simply returns Undefined.
        """
        return Undefined


    def label_image_value ( self ):
        """ Returns the label image value used to render the item. The default
            implementation simply returns Undefined (indicating that there is no
            label image to display).
        """
        return Undefined


    def set_text ( self ):
        """ Sets the correct value for the 'text' facet.
        """
        self.text = self.value_of( 'text_value' )


    def set_image ( self ):
        """ Sets the correct value for the 'image' facet.
        """
        value = self.value_of( 'image_value' )
        if value is not Undefined:
            self.image = value


    def set_label ( self ):
        """ Sets the correct value for the 'label' facet.
        """
        value = self.value_of( 'label_value' )
        if value is not Undefined:
            self.label = value


    def set_label_image ( self ):
        """ Sets the correct value for the 'label_image' facet.
        """
        value = self.value_of( 'label_image_value' )
        if value is not Undefined:
            self.label_image = value


    def tag_content ( self, index ):
        """ Returns the content associated with the *index*th tag for the item.

            This method should be overridden by any subclasses that use tag
            references.
        """
        return ''

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'item, lod, update' )
    def _item_modified ( self ):
        """ Handles the 'item' facet being changed.
        """
        self.set_text()
        self.set_image()
        self.set_label()
        self.set_label_image()


    @on_facet_set( 'reset, text, label, image, label_image, current_font, current_theme, alignment, context' )
    def _visuals_modified ( self ):
        """ Handles any facet affecting the visual appearance of the item being
            modified.
        """
        if self.context is not None:
            g    = self.context.graphics
            font = self.current_font
            if font is not None:
                g.font = font

            self.gtext = GraphicsText(
                text        = self.text,
                image       = self.image,
                alignment   = self.alignment,
                tag_content = self.tag_content
            )
            self.size = self.lookup( 'size_item', self.theme_state )( g )

            if (self.label != '') or (self.label_image is not None):
                self.ltext = GraphicsText(
                    text        = self.label,
                    image       = self.label_image,
                    alignment   = self.label_alignment,
                    tag_content = self.tag_content
                )
            else:
                self.ltext = None

            self.refresh = True

    #-- IStackItem Interface Methods -------------------------------------------

    def paint_item ( self, g, bounds ):
        """ Paints the text and optional label in the specified graphics
            context *g*.
        """
        x, y, dx, dy = self.bounds
        self.current_theme.draw_graphics_text( g, self.gtext, x, y, dx, dy,
                                               bounds )
        if self.ltext is not None:
            self.current_theme.draw_graphics_label( g, self.ltext, x, y, dx, dy,
                                                    bounds )


    def size_item ( self, g ):
        """ Returns the current size of the item.
        """
        return self.current_theme.size_for( g, self.gtext )

#-- EOF ------------------------------------------------------------------------
