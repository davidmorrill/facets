"""
Defines the adapter classes associated with the Facets UI GridEditor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import SingletonHasPrivateFacets, HasFacets, HasPrivateFacets, Color, Str, \
           Int, Float, Enum, List, Dict, Bool, Instance, Callable, Any, Font,  \
           ATheme, Theme, Event, Image, Property, Interface, DelegatesTo,      \
           implements, Theme, Disallow, View, HGroup, VGroup, Item,            \
           TextEditor, InstanceEditor, ThemedButtonEditor,                     \
           ThemedCheckboxEditor, Undefined, implements, on_facet_set,          \
           property_depends_on

from facets.core.facet_base \
    import user_name_for, SequenceTypes

from facets.ui.menu \
    import Menu, Action

from facets.ui.colors \
    import SelectionColor

from facets.ui.i_filter \
    import IFilter

from facets.ui.ui_facets \
    import HorizontalAlignment, CellImageAlignment

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The different types of popup views:
PopupTypes = ( 'popup', 'popout', 'popover', 'info' )

# The default editor to use for editing a cell value:
default_editor = TextEditor()

# Auto-filter column images (created on demand):
FilterImages = None

# Auto-search column images (created on demand):
SearchImages = None

# Dual auto-filter/auto-search column images (created on demand):
FilterSearchImages = None

# The standard numeric types understood by the ColumnFilter:
NumericTypes = ( int, float )

# The names of the ColumnFilter match operators:
Operators = {
    '':    'contains',
    '!':   'not_contains',
    '..':  'in_range',
    '!..': 'not_in_range',
    '<<':  'starts_with',
    '!<<': 'not_starts_with',
    '>>':  'ends_with',
    '!>>': 'not_ends_with',
    '=':   'equals',
    '!=':  'not_equals',
    '<':   'lt',
    '<=':  'le',
    '>':   'gt',
    '>=':  'ge'
}

# The ColumnFilter operators that can be used with a range ('..'):
RangeOperators = ( '', '!' )

# The theme used when creating popup gri cell editors:
PopupTheme = Theme( '@xform:b?L40', content = 5 )

#-------------------------------------------------------------------------------
#  'GridEventHandler' class:
#-------------------------------------------------------------------------------

class GridEventHandler ( HasPrivateFacets ):
    """ A class that handles events for items within a GridEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The GridAdapter this handler delegates to:
    adapter = Instance( 'GridAdapter' )

    # The object whose facet is being edited:
    object = DelegatesTo( 'adapter' )

    # The name of the facet being edited:
    name = DelegatesTo( 'adapter' )

    # The row index of the event occurred on:
    row = DelegatesTo( 'adapter' )

    # The column index the event occurred on:
    column = DelegatesTo( 'adapter' )

    # The id associated with the column the event occurred on:
    column_id = DelegatesTo( 'adapter' )

    # The item at the row the event occurred on:
    item = DelegatesTo( 'adapter' )

    # The content of the item for the column the event occurred on:
    content = DelegatesTo( 'adapter' )

    #-- Public Methods ---------------------------------------------------------

    def left_down ( self, index, item ):
        """ Handles a left button press event.
        """
        pass


    def left_up ( self, index, item ):
        """ Handles a left button release event.
        """
        pass


    def left_dclick ( self ):
        """ Handles a left button double-click event.
        """
        pass


    def right_down ( self ):
        """ Handles a right button down event.
        """
        pass


    def right_up ( self, index, item ):
        """ Handles a right button release event.
        """
        pass


    def right_dclick ( self ):
        """ Handles a right button double-click event.
        """
        pass


    def mouse_move ( self ):
        """ Handles a mouse move event.
        """
        pass


    def mouse_enter ( self ):
        """ Handles a mouse enter cell event.
        """
        pass


    def mouse_leave ( self ):
        """ Handles a mouse leave cell event.
        """
        pass

#-------------------------------------------------------------------------------
#  'ColumnFilter' class:
#-------------------------------------------------------------------------------

class ColumnFilter ( HasPrivateFacets ):
    """ Defines a ColumnFilter for filtering or searching the contents of a
        GridEditor column when either the 'auto_filter' or 'auto_search' value
        of a GridAdapter column is True.
    """

    implements( IFilter )

    #-- Facet Definitions ------------------------------------------------------

    # The GridFilter object that owns this filter:
    owner = Any # ( Instance( GridFilter ) )

    # The string being filtered on:
    match = Str

    # Are text matches case sensitive?
    case_sensitive = Bool( False )

    # Is this a search (True) or filter (False)?
    is_search = Bool( False )

    # Event fired to clear the current match:
    clear = Event

    # The match string as text:
    text = Str

    # The match string as text (high end of range test):
    text_high = Str

    # The match string as a number:
    value = Float

    # The match string as a number (high end of range test):
    value_high = Float

    # The method called to return the current cell value in the correct case:
    value_case = Callable

    # The name of the current match operator to use when filtering:
    operator = Str( 'contains' )

    #-- IFilter Interface Facet Definitions ------------------------------------

    # Is the filter active?
    active = Bool( False )

    # Event fired when the filter criteria defined by the filter has changed
    # (Thus necessitating that the filter be re-applied to all objects):
    changed = Event

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            HGroup(
                *self._item_content(),
                show_labels = False,
                group_theme = Theme( '@std:popup', content = 0 )
            ),
            kind = 'popup'
        )


    def nested_view ( self ):
        return View( HGroup( *self._item_content(), show_labels = False ) )

    #-- IFilter Interface Methods ----------------------------------------------

    def filter ( self, value ):
        """ Returns True if value is accepted by the filter, and False if it is
            not.
        """
        type = 'number'
        if not isinstance( value, NumericTypes ):
            type  = 'string'
            value = str( value )

        return getattr( self, '_%s_%s' % ( type, self.operator ) )( value )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'match, case_sensitive' )
    def _match_modified ( self ):
        """ Handles the 'match' or 'case sensitive' facets being changed.
        """
        end   = 0
        match = self.match.strip()
        c     = match[:1]
        if c == '=':
            end = 1
        elif c in '!<>':
            end = 1 + (match[1:2] == '=')

        operator = match[ : end ]
        text     = match[ end: ]
        if (operator in RangeOperators) and (match.find( '..' ) >= 0):
            text, text_high = match.split( '..', 1 )
            if not self.case_sensitive:
                text_high = text_high.lower()

            if text_high == '':
                operator += '<<'
            elif text == '':
                operator += '>>'
                text, text_high = text_high, text
            else:
                operator += '..'

            self.text_high = text_high
            try:
                self.value_high = float( text_high )
            except:
                self.value_high = 0.0

        self.operator = Operators[ operator ]
        if self.case_sensitive:
            self.text       = text
            self.value_case = self._value_identity
        else:
            self.text       = text.lower()
            self.value_case = self._value_lower

        try:
            self.value = float( text )
        except:
            self.value = 0.0

        self.active  = (match != '')
        self.changed = True


    def _changed_set ( self ):
        """ Handles the contents of the filter being changed.
        """
        if self.owner is not None:
            self.owner.changed = True


    def _clear_set ( self ):
        """ Handles the 'clear' event being fired.
        """
        self.match = ''

    #-- Private Methods --------------------------------------------------------

    def _value_identity ( self, value ):
        """ Returns the specified *value* umodified.
        """
        return value


    def _value_lower ( self, value ):
        """ Returns the lowercase version of *value* for case insensitive tests.
        """
        return value.lower()


    def _item_content ( self ):
        """ Returns the Items to display in the various Views.
        """
        # fixme: The 'enabled_when' clause below causes an infinite loop in the
        # case when the button is clicked. Loop happens when popup is closed.
        return [
            Item( 'clear',
                  tooltip      = 'Clear the filter',
                  padding      = -2,
                  #enabled_when = "match != ''",
                  editor       = ThemedButtonEditor(
                      theme = None,
                      image = ( '@icons:filter_on', '@icons2:Magnifier' )
                              [ self.is_search ]
                  )
            ),
            Item( 'case_sensitive',
                  padding = -2,
                  editor  = ThemedCheckboxEditor(
                      image       = '@icons:case_sensitive',
                      off_image   = '@icons:case_insensitive',
                      on_tooltip  = 'Use case sensitive matching',
                      off_tooltip = 'Use case insensitive matching' )
            ),
            Item( 'match' )
        ]

    #-- The Filter Methods -----------------------------------------------------

    def _string_contains ( self, value ):
        return (self.value_case( value ).find( self.text ) >= 0)

    def _string_not_contains ( self, value ):
        return (self.value_case( value ).find( self.text ) < 0)

    def _string_in_range ( self, value ):
        return (self.text <= self.value_case( value ) <= self.text_high)

    def _string_not_in_range ( self, value ):
        return (not (self.text <= self.value_case( value ) <= self.text_high))

    def _string_starts_with ( self, value ):
        return self.value_case( value ).startswith( self.text )

    def _string_not_starts_with ( self, value ):
        return (not self.value_case( value ).startswith( self.text ))

    def _string_ends_with ( self, value ):
        return self.value_case( value ).endswith( self.text )

    def _string_not_ends_with ( self, value ):
        return (not self.value_case( value ).endswith( self.text ))

    def _string_equals ( self, value ):
        return (self.value_case( value ) == self.text)

    def _string_not_equals ( self, value ):
        return (self.value_case( value ) != self.text)

    def _string_lt ( self, value ):
        return (self.value_case( value ) < self.text)

    def _string_le ( self, value ):
        return (self.value_case( value ) <= self.text)

    def _string_gt ( self, value ):
        return (self.value_case( value ) > self.text)

    def _string_ge ( self, value ):
        return (self.value_case( value ) >= self.text)

    def _number_contains ( self, value ):
        return (value == self.value)

    def _number_not_contains ( self, value ):
        return (value != self.value)

    def _number_in_range ( self, value ):
        return (self.value <= value <= self.value_high)

    def _number_not_in_range ( self, value ):
        return (not (self.value <= value <= self.value_high))

    def _number_starts_with ( self, value ):
        return (value >= self.value)

    def _number_not_starts_with ( self, value ):
        return (value < self.value)

    def _number_ends_with ( self, value ):
        return (value <= self.value)

    def _number_not_ends_with ( self, value ):
        return (value > self.value)

    def _number_equals ( self, value ):
        return (value == self.value)

    def _number_not_equals ( self, value ):
        return (value != self.value)

    def _number_lt ( self, value ):
        return (value < self.value)

    def _number_le ( self, value ):
        return (value <= self.value)

    def _number_gt ( self, value ):
        return (value > self.value)

    def _number_ge ( self, value ):
        return (value >= self.value)

#-------------------------------------------------------------------------------
#  'FilterSearch' class:
#-------------------------------------------------------------------------------

class FilterSearch ( HasPrivateFacets ):
    """ A composite filter used when both 'auto_filter' and 'auto_search' are
        active for a column at the same time.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ColumnFilter for the filter:
    filter = Instance( ColumnFilter )

    # The ColumnFilter for the search:
    search = Instance( ColumnFilter )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'filter',
                  style  = 'custom',
                  editor = InstanceEditor( view = 'nested_view' ),
            ),
            '_',
            Item( 'search',
                  style  = 'custom',
                  editor = InstanceEditor( view = 'nested_view' ),
            ),
            show_labels = False,
            group_theme = Theme( '@std:popup', content = 0 )
        ),
        kind = 'popup'
    )

#-------------------------------------------------------------------------------
#  'GridFilter' class:
#-------------------------------------------------------------------------------

class GridFilter ( HasPrivateFacets ):
    """ Defines a GridFilter for filtering or searching the contents of all
        GridEditor columns whose GridAdapter 'auto_filter' or 'auto_search'
        value is True.
    """

    implements( IFilter )

    #-- Facet Definitions ------------------------------------------------------

    # The dictionary of all active ColumnFilters:
    filters = Dict

    # The GridAdapter this filter is associated with:
    adapter = Any # ( Instance( GridAdapter ) )

    #-- IFilter Interface Facet Definitions ------------------------------------

    # Is the filter active?
    active = Bool( False )

    # Event fired when the filter criteria defined by the filter has changed
    # (thus necessitating that the filter be re-applied to all objects):
    changed = Event

    #-- IFilter Interface Methods ----------------------------------------------

    def filter ( self, value ):
        """ Returns True if value is accepted by the filter, and False if it is
            not.
        """
        gc = self.adapter.get_content
        for column, filter in self.filters.iteritems():
            if filter.active and (not filter.filter( gc( value, column ) )):
                return False

        return True

    #-- Facet Event Handlers ---------------------------------------------------

    def _filters_items_set ( self, event ):
        """ Handles the contents of the 'filters' dictionary being changed.
        """
        for filter in event.removed.itervalues():
            filter.owner = None

        for filter in event.added.itervalues():
            filter.owner = self

        self.changed = True


    def _changed_set ( self ):
        """ Handles the filter being changed.
        """
        for filter in self.filters.itervalues():
            if filter.active:
                self.active = True

                break
        else:
            self.active = False

#-------------------------------------------------------------------------------
#  'IGridAdapter' interface:
#-------------------------------------------------------------------------------

class IGridAdapter ( Interface ):

    #-- Facet Definitions ------------------------------------------------------

    # Event fired when some aspect of the adapter changes that affects the
    # associated editor:
    changed = Event

    # Event fired when any visual aspect of the adapter changes:
    refresh = Event

    # The row index of the current item being adapted:
    row = Int

    # The current column id being adapted (if any):
    column = Any

    # Current item being adapted:
    item = Any

    # The current value (if any):
    value = Any

    # The list of columns the adapter supports. The items in the list have the
    # same format as the *columns* facet in the *TabularAdapter* class, with the
    # additional requirement that the *string* values must correspond to a
    # *string* value in the associated *TabularAdapter* class.
    columns = List( Str )

    # Does the adapter know how to handle the current *item* or not:
    accepts = Bool

    # Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool

#-------------------------------------------------------------------------------
#  'AnIGridAdapter' class:
#-------------------------------------------------------------------------------

class AnIGridAdapter ( HasPrivateFacets ):

    implements( IGridAdapter )

    #-- Implementation of the ITabularAdapter Interface ------------------------

    # Event fired when some aspect of the adapter changes that affects the
    # associated editor:
    changed = Event

    # Event fired when any visual aspect of the adapter changes:
    refresh = Event

    # The row index of the current item being adapted:
    row = Int

    # The current column id being adapted (if any):
    column = Any

    # Current item being adapted:
    item = Any

    # The current value (if any):
    value = Any

    # The list of columns the adapter supports. The items in the list have the
    # same format as the *columns* facet in the *GridAdapter* class, with the
    # additional requirement that the *string* values must correspond to a
    # *string* value in the associated *GridAdapter* class.
    columns = List( Str )

    # Does the adapter know how to handle the current *item* or not:
    accepts = Bool( True )

    # Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool( True )

#-------------------------------------------------------------------------------
#  'GridAdapter' class:
#-------------------------------------------------------------------------------

class GridAdapter ( HasPrivateFacets ):
    """ The base class for adapting list items to values that can be edited
        by a GridEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Event fired when any aspect of the grid adapter or its associated object
    # facet changes in such a way that it requires a resynchronization with the
    # associated editor:
    changed = Event

    # Event fired when any visual aspect of the grid adapter changes:
    refresh = Event

    # A list of columns that should appear in the table. Each entry can have one
    # of two forms: string or ( string, any ), where *string* is the UI name of
    # the column, and *any* is a value that identifies that column to the
    # adapter. Normally this value is either a facet name or an index, but it
    # can be any value that the adapter wants. If only *string* is specified,
    # then *any* is the index of the *string* within *columns*.
    columns = List()

    # List of optional delegated adapters:
    adapters = List( IGridAdapter )

    # Specifies the default value for a new row:
    default_value = Any( '' )

    # Is the grid visible or not?
    grid_visible = Bool( True )

    # The color to use for grid lines:
    grid_color = Color( 0xD0D0D0 )

    #-- Grid Cell Related Facets -----------------------------------------------

    # The default text color for cells (even, odd, any rows):
    odd_text_color     = Color( None, event = 'refresh' )
    even_text_color    = Color( None, event = 'refresh' )
    default_text_color = Color( None, event = 'refresh' )

    # The default background color for cells (even, odd, any rows):
    odd_bg_color     = Color( None, event = 'refresh' )
    even_bg_color    = Color( None, event = 'refresh' )
    default_bg_color = Color( None, event = 'refresh' )

    # Horizontal text alignment to use for a cell:
    alignment = HorizontalAlignment( event = 'refresh' )

    # Horizontal image alignment to use for a cell:
    image_alignment = CellImageAlignment( event = 'refresh' )

    # The formatting function used to format the contents of a cell:
    formatter = Callable

    # The Python format string to use for a cell:
    format = Str( None, event = 'refresh' )

    # The handler for mouse events for a cell:
    handler = Instance( GridEventHandler )

    # Can a cell be edited?
    can_edit = Bool( True )

    # The editing mode used for changing cell values. The possible values are:
    # - 'live':  Changes are made 'live' while the editor is active.
    # - 'defer': Changes are made only when the editor is closed.
    # - 'save':  Changes are made only when the user clicks the 'OK' button.
    change_mode = Enum( 'live', 'defer', 'save' )

    # The value to be dragged for a cell:
    drag = Property

    # Can any arbitrary value be dropped onto a cell?
    can_drop = Bool( False )

    # Specifies where a dropped item should be placed in the table relative to
    # the cell it is dropped on:
    dropped = Enum( 'after', 'before' )

    # The font to use for a cell:
    font = Font( None, event = 'refresh' )

    # The font to use for a selected cell:
    selected_font = Font( None, event = 'refresh' )

    # The text color to use for a cell:
    text_color = Property

    # The text color to use for a selected cell:
    selected_text_color = Color( 0x202020, event = 'refresh' )

    # The background color to use for a cell:
    bg_color = Property

    # The background color to use for a selected cell:
    selected_bg_color = Color( SelectionColor, event = 'refresh' )

    # The name of the default image to use for a cell:
    image = Str( None, event = 'refresh' )

    # The name of the default image to use for a selected cell:
    selected_image = Str( None, event = 'refresh' )

    # The theme to use when rendering a cell:
    theme = ATheme

    # The theme to use when rendering a selected cell:
    selected_theme = ATheme

    # The amount of indenting to use with a left aligned cell:
    indent = Int( 0 )

    # The custom function to use for rendering a cell:
    paint = Any # Either( Str, Callable )

    # The text to display in a cell:
    text = Property

    # The content of a cell (may be any Python value):
    content = Property

    # If no explicit tooltip is specified, should it default to displaying the
    # text contents of the cell?
    auto_tooltip = Bool( False )

    # The tooltip information to use for a cell:
    tooltip = Str( event = 'refresh' )

    # The EditorFactory to use for editing a cell:
    editor = Property

    # The alias for the current item to use when performing a cell edit (an
    # alias is an alternate ( object, name ) pair to substitute for the current
    # one):
    alias = Property

    # The action to take when a cell is clicked:
    clicked = Str( 'edit' )

    # The action to take when a cell is double clicked:
    double_clicked = Str( None )

    # The context menu to display when a cell is right-clicked:
    menu = Any # Instance( Menu ), Instance( Action ) or List( Action )

    #-- Grid Column Related Facets ---------------------------------------------

    # Can the column be automatically filtered?
    auto_filter = Bool( False )

    # Can the column be automatically searched?
    auto_search = Bool( False )

    # Can a column be sorted?
    sortable = Bool( True )

    # The custom sorting function to use for a column:
    sorter = Callable

    # Width of a specified column:
    width = Float( -1, event = 'refresh' )

    # The title text of a column header:
    title = Str( event = 'refresh' )

    # The alignment to use for a column header:
    column_alignment = Enum( None, 'left', 'center', 'right',
                             event = 'refresh' )

    # The font to use for a column header:
    column_font = Font( None, event = 'refresh' )

    # The text color to use for a column header:
    column_text_color = Color( None, event = 'refresh' )

    # The background color to use for a column header:
    column_bg_color = Color( 0xDCD5C5, event = 'refresh' )

    # The name of the default image to use for a column header:
    column_image = Str( None, event = 'refresh' )

    # The theme to use for a column header:
    column_theme = ATheme

    # The amount of indenting to use for a column header:
    column_indent = Int( 0 )

    # The custom function to use for rendering a column header:
    column_paint = Any # Either( Str, Callable )

    # The tooltip information to use for column header:
    column_tooltip = Str( event = 'refresh' )

    # The context menu to display when a column header is right-clicked:
    column_menu = Any # Instance( Menu ), Instance( Action ) or List( Action )

    #-- Facets Set by the Editor -----------------------------------------------

    # The GridEditor object associated with this adapter:
    grid_editor = Instance( HasFacets )

    # The GridFilter object associated with this adapter for column filtering:
    grid_filter = Instance( GridFilter )

    # The GridFilter object associated with this adapter for column searching:
    grid_search = Instance( GridFilter )

    # The object whose facet is being edited:
    object = Instance( HasFacets )

    # The name of the facet being edited:
    name = Str

    # The physical screen row index of the current item being adapted:
    screen_row = Int

    # The row index of the current item being adapted:
    row = Int

    # The column index of the current item being adapted:
    column = Int

    # The visual bounds of the cell:
    bounds = Any # Tuple( Int, Int, Int, Int )

    # The current column id being adapted (if any):
    column_id = Any

    # Current item being adapted:
    item = Any

    # The current value (if any):
    value = Any

    # Temporary value used to convert font names to Font objects:
    _font = Font

    # Temporary value used to convert image names to ImageResource objects:
    _image = Image

    # Temporary value used to convert numbers to GUI toolkit color values:
    _color = Color

    # Temporary value used to convert theme names to Them objects:
    _theme = ATheme

    #-- Private Facet Definitions ----------------------------------------------

    # Cache of attribute handlers:
    _hit_cache = Any( {} )

    # The mapping from column indices to column identifiers (defined by the
    # *columns* facet):
    column_map = Property

    # The mapping from column indices to column labels (defined by the *columns*
    # facet):
    label_map = Property

    # For each adapter, specifies the column indices the adapter handles:
    adapter_column_indices = Property

    # For each adapter, specifies the mapping from column index to column id:
    adapter_column_map = Property

    #-- Adapter Methods --------------------------------------------------------

    def column_clicked ( self ):
        """ Handles the user clicking a column header.
        """
        if (self.get_auto_filter( self.column ) or
            self.get_auto_search( self.column )):
            self.column_clicked_for()


    def column_double_clicked ( self ):
        """ Handles the user double clicking a column header.
        """
        pass

    #-- Adapter methods that are not sensitive to item type, row or column -----

    def get_grid_color ( self, row = 0, column = 0 ):
        """ Returns the color to use for drawing the grid lines. A value of
            None means use the default grid line color.
        """
        return self._color_result_for( 'get_grid_color', row, column )


    def get_grid_visible ( self, row = 0, column = 0 ):
        """ Returns whether or not grid lines should be shown.
        """
        return self._result_for( 'get_grid_visible', row, column )

    #-- Adapter methods that are sensitive to item type and column -------------

    def get_auto_filter ( self, column ):
        """ Returns True if the specified column can be automatically filtered,
            and False if it can not.
        """
        return self.auto_search_filter_for( 'filter', self.grid_filter, column )


    def get_auto_search ( self, column ):
        """ Returns True if the specified column can be automatically searched,
            and False if it can not.
        """
        return self.auto_search_filter_for( 'search', self.grid_search, column )


    def get_sortable ( self, column ):
        """ Returns True if the specified column is sortable, and False if it
            is not.
        """
        return self._result_for( 'get_sortable', 0, column )


    def get_sorter ( self, column ):
        """ Returns the sorting comparison function (like 'cmp') to use for
            sorting the items in the specified column.
        """
        sorter = self._result_for( 'get_sorter', 0, column )
        if sorter is not None:
            return sorter

        facet = self.column_id

        def default_sorter ( l, r ):
            return cmp( getattr( l, facet ), getattr( r, facet ) )

        return default_sorter


    def get_width ( self, column ):
        """ Returns the width to use for a specified column.
        """
        return self._result_for( 'get_width', 0, column )


    def get_title ( self, column ):
        """ Returns the text to display in the specified column header.
        """
        result = self._result_for( 'get_title', 0, column )
        if result == '':
            result = self.label_map[ column ]

        if self.get_auto_filter( column ):
            filter = self.grid_filter.filters[ column ]
            if filter.active:
                result += ' [%s]' % filter.match

        if self.get_auto_search( column ):
            search = self.grid_search.filters[ column ]
            if search.active:
                result += ' (%s)' % search.match

        return result


    def get_column_alignment ( self, column ):
        """ Returns the alignment style to use for a specified column header.
        """
        result = self._result_for( 'get_column_alignment', 0, column )
        if result is not None:
            return result

        return self._result_for( 'get_alignment', 0, column )


    def get_column_font ( self, column ):
        """ Returns the font to use for a specified column header. A result of
            None means use the default font.
        """
        return self.font_for( self._result_for( 'get_column_font', 0, column ) )


    def get_column_text_color ( self, column ):
        """ Returns the text color to use for a specified column header. A
            result of None means use the default text color.
        """
        return self._color_result_for( 'get_column_text_color', 0, column )


    def get_column_bg_color ( self, column ):
        """ Returns the background color to use for a specified column header.
            A result of None means use the default background color.
        """
        return self._color_result_for( 'get_column_bg_color', 0, column )


    def get_column_image ( self, column ):
        """ Returns the image to use for a specified column header. A result
            of None means no image should be used. Otherwise, the result should
            be an ImageResource item specifying the image to use.
        """
        global FilterImages, SearchImages, FilterSearchImages

        image = self.image_for(
            self._result_for( 'get_column_image', 0, column )
        )

        if image is None:
            filter = search = None
            if self.get_auto_filter( column ):
                filter = self.grid_filter.filters[ column ]

            if self.get_auto_search( column ):
                search = self.grid_search.filters[ column ]

            if search is None:
                if filter is not None:
                    if FilterImages is None:
                        FilterImages = ( self.image_for( '@icons:filter_off' ),
                                         self.image_for( '@icons:filter_on'  ) )

                    image = FilterImages[ filter.active ]
            elif filter is None:
                if SearchImages is None:
                    SearchImages = ( self.image_for( '@icons2:Magnifier?L20' ),
                                     self.image_for( '@icons2:Magnifier'  ) )

                image = SearchImages[ search.active ]
            else:
                if FilterSearchImages is None:
                    FilterSearchImages = (
                        self.image_for( '@icons2:QuestionBox?L42~L22|L47' ),
                        self.image_for( '@icons2:QuestionBox'  ) )

                image = FilterSearchImages[ filter.active or search.active ]

        return image


    def get_column_theme ( self, column ):
        """ Returns the Theme to use when rendering a specified column header.
            A result of None means no theme is to be used. Otherwise the result
            should be a Theme object to use for the column header background.
        """
        return self.theme_for(
            self._result_for( 'get_column_theme', 0, column )
        )


    def get_column_indent ( self, column ):
        """ Returns the amount of indenting to use with the specified column
            header when it is left-aligned.
        """
        return self._result_for( 'get_column_indent', 0, column )


    def get_column_paint ( self, column ):
        """ Returns the custom paint handler to use for rendering the specified
            column header. A result of None means use the default renderer.
            Otherwise the result should be a callable with a signature of the
            form: paint( cell, row, column ), where cell is an instance of Cell,
            which contains all of the information describing the cell to be
            painted.
        """
        result = self._result_for( 'get_column_paint', 0, column )
        if not isinstance( result, basestring ):
            return result

        return StandardCellPainters[ result ]


    def get_column_tooltip ( self, column ):
        """ Returns the tooltip to display for a specified column header.
        """
        return self._result_for( 'get_column_tooltip', 0, column )


    def get_column_menu ( self, column ):
        """ Returns the context menu to display for a specified column header.
        """
        return self.menu_for( self._result_for( 'get_column_menu', 0, column ) )


    def get_column_clicked ( self, column ):
        """ Returns the adapter method handling a column header 'clicked' event
            for a specified column header.
        """
        return self._result_for( 'get_column_clicked', 0, column )


    def get_column_double_clicked ( self, column ):
        """ Returns the adapter method handling a column header 'double clicked'
            event for a specified column header.
        """
        return self._result_for( 'get_column_double_clicked', 0, column )

    #-- Adapter methods that are sensitive to item type, row and column --------

    def get_handler ( self, row, column ):
        """ Returns the GridEventHandler for a specified row:column item.
        """
        handler = self._result_for( self, row, column )
        if handler is not None:
            handler.adapter = self

        return handler


    def get_alignment ( self, row, column ):
        """ Returns the horizontal text alignment style to use for a specified
            row:column item.
        """
        return self._result_for( 'get_alignment', row, column )


    def get_image_alignment ( self, row, column ):
        """ Returns the horizontal image alignment style to use for a specified
            row:column item.
        """
        return self._result_for( 'get_image_alignment', row, column )


    def get_can_edit ( self, row, column ):
        """ Returns whether the user can edit a specified row:column item. A
            True result indicates the value can be edited, while a False result
            indicates that it cannot be edited.
        """
        return self._result_for( 'get_can_edit', row, column )


    def get_change_mode ( self, row, column ):
        """ Returns the change mode used editing the specified row:column item:
            - 'live':  Changes are made live while the editor is active.
            - 'defer': Changes are made only when the editor is closed.
            - 'save':  Changes are made only when user clicks the 'OK' button.
        """
        return self._result_for( 'get_change_mode', row, column )


    def get_drag ( self, row, column ):
        """ Returns the 'drag' value for a specified row:column item. A result
            of *None* means that the item cannot be dragged.
        """
        return self._result_for( 'get_drag', row, column )


    def get_can_drop ( self, row, column, value ):
        """ Returns whether the specified *value* can be dropped on the
            specified row:column item. A value of **True** means the
            *value* can be dropped; and a value of **False** indicates that it
            cannot be dropped.
        """
        return self._result_for( 'get_can_drop', row, column, value )


    def get_dropped ( self, row, column, value ):
        """ Returns how to handle a specified *value* being dropped on a
            specified row:column item. The possible return values are:

            'before'
                Insert the specified *value* before the dropped on item.
            'after'
                Insert the specified *value* after the dropped on item.
        """
        return self._result_for( 'get_dropped', row, column, value )


    def get_font ( self, row, column ):
        """ Returns the font for a specified row:column item. A result of None
            means use the default font.
        """
        return self.font_for(
            self._result_for( 'get_font', row, column )
        )


    def get_selected_font ( self, row, column ):
        """ Returns the font to use for a specified row:column item that is
            selected. A result of None means the default font should be used.
            Otherwise, the result should be an font object specifying the font
            to use.
        """
        font = self._result_for( 'get_selected_font', row, column )
        if font is None:
            return self.get_font( row, column )

        return self.font_for( font )


    def get_text_color ( self, row, column, screen_row ):
        """ Returns the text color for a specified row:column item. A result of
            None means use the default text color. The screen_row value
            specifies the physical screen row this value is for, and is used to
            return the correct oddd/even row color if necessary.
        """
        self.screen_row = screen_row

        return self._color_result_for( 'get_text_color', row, column )


    def get_selected_text_color ( self, row = 0, column = 0 ):
        """ Returns the text color to use for selected row:column item. A value
            of None means use the default text selection color.
        """
        color = self._color_result_for( 'get_selected_text_color', row, column )
        if color is not None:
            return color

        return self.get_text_color( row, column, 0 )


    def get_bg_color ( self, row, column, screen_row ):
        """ Returns the background color to use for a specified row:column item.
            A result of None means use the default background color. The
            screen_row value specifies the physical screen row this value is
            for, and is used to return the correct odd/even row color if
            necessary.
        """
        self.screen_row = screen_row

        return self._color_result_for( 'get_bg_color', row, column )


    def get_selected_bg_color ( self, row = 0, column = 0 ):
        """ Returns the text color to use for the background of a selected
            row:column item. A value of None means use the default background
            selection color.
        """
        return self._color_result_for( 'get_selected_bg_color', row, column )


    def get_image ( self, row, column ):
        """ Returns the image to use for a specified row:column item. A result
            of None means no image should be used. Otherwise, the result should
            be an ImageResource item specifying the image to use, or a string
            which can be converted to an ImageResource.
        """
        return self.image_for(
            self._result_for( 'get_image', row, column )
        )


    def get_selected_image ( self, row, column ):
        """ Returns the image to use for a specified row:column item that is
            selected. A result of None means no image should be used. Otherwise,
            the result should be an ImageResource item specifying the image to
            use.
        """
        image = self._result_for( 'get_selected_image', row, column )
        if image is None:
            return self.get_image( row, column )

        return self.image_for( image )


    def get_theme ( self, row, column ):
        """ Returns the Theme to use when rendering a specified row:column item.
            A result of None means no theme is to be used. Otherwise the result
            should be a Theme object to use for the cell background.
        """
        return self.theme_for(
            self._result_for( 'get_theme', row, column )
        )


    def get_selected_theme ( self, row, column ):
        """ Returns the Theme to use when rendering a specified row:column item
            that is selected. A result of None means no theme is to be used.
            Otherwise the result should be a Theme object to use for the cell
            background.
        """
        theme = self._result_for( 'get_selected_theme', row, column )
        if theme is None:
            return self.get_theme( row, column )

        return self.theme_for( theme )


    def get_indent ( self, row, column ):
        """ Returns the amount of indenting to use with the specified row:column
            item when it is left-aligned.
        """
        return self._result_for( 'get_indent', row, column )


    def get_paint ( self, row, column ):
        """ Returns the custom paint handler to use for rendering the specified
            row:column item. A result of None means use the default renderer.
            Otherwise the result should be a callable with a signature of the
            form: paint( cell, row, column ), where cell is an instance of
            Cell, which contains all of the information describing the cell to
            be painted.
        """
        result = self._result_for( 'get_paint', row, column )
        if not isinstance( result, basestring ):
            return result

        return StandardCellPainters[ result ]


    def get_formatter ( self, row, column ):
        """ Returns the formatting function to use for a specified row:column
            item. The formatting function receives a single argument, the
            cell content to be formatted, and should return the formatted
            string value for the specified content.
        """
        return self._result_for( 'get_formatter', row, column )


    def get_format ( self, row, column ):
        """ Returns the Python format string to use for a specified row:column
            item.
        """
        return self._result_for( 'get_format', row, column )


    def get_text ( self, row, column ):
        """ Returns the text to display for a specified row:column item.
        """
        return self._result_for( 'get_text', row, column )


    def set_text ( self, row, column, text ):
        """ Sets the text for a specified row:column item to *text*.
        """
        self._result_for( 'set_text', row, column, text )


    def get_content ( self, row, column ):
        """ Returns the content to display for a specified row:column item.
        """
        return self._result_for( 'get_content', row, column )


    def get_auto_tooltip ( self, row, column ):
        """ Returns whether or not a tooltip should be automatically generated
            from the specified row:column cell content if no explicit tooltip
            is provided.
        """
        return self._result_for( 'get_auto_tooltip', row, column )


    def get_tooltip ( self, row, column ):
        """ Returns the tooltip for a specified row:column.
        """
        return self._result_for( 'get_tooltip', row, column )


    def get_editor ( self, row, column ):
        """ Returns the Editorfactory to use for editing a specified row:column
            item.
        """
        return self._result_for( 'get_editor', row, column )


    def get_alias ( self, row, column ):
        """ Returns the ( object, name ) alias to use for performing a cell
            'edit' operation for the specified row:column.
        """
        return self._result_for( 'get_alias', row, column )


    def get_clicked ( self, row, column ):
        """ Returns the adapter method handling a cell 'clicked' event for a
            specified row:column item.
        """
        return self._result_for( 'get_clicked', row, column )


    def get_double_clicked ( self, row, column ):
        """ Returns the adapter method handling a cell 'double clicked' event
            for a specified row:column item.
        """
        return self._result_for( 'get_double_clicked', row, column )


    def get_menu ( self, row, column ):
        """ Returns the right-click context menu for a specified row:column
            item.
        """
        return self.menu_for( self._result_for( 'get_menu', row, column ) )

    #-- Adapter methods that are not sensitive to item type --------------------

    def get_item ( self, row ):
        """ Returns the value of the specified row item.
        """
        try:
            return getattr( self.object, self.name )[ row ]
        except:
            return None


    def len ( self ):
        """ Returns the number of items in the associated facet value.
        """
        if self.object is None:
            return 0

        return len( getattr( self.object, self.name ) )


    def get_default_value ( self ):
        """ Returns a new default value for the associated facet value.
        """
        result = self.default_value
        if not callable( result ):
            return result

        return result()


    def delete ( self, row ):
        """ Deletes the specified row item.
        """
        del getattr( self.object, self.name )[ row ]


    def insert ( self, row, value ):
        """ Inserts a new value at the specified row index.
        """
        getattr( self.object, self.name ) [ row: row ] = [ value ]


    def sort ( self, items, sorter, sort_ascending ):
        """ Returns the list of *items* sorted using the *sorter* function and
            in the order specified by *sort_ascending*. Each element in *items*
            is a tuple of the form: (index, value), where *index* specifies
            the original index of *value* after any filtering has been applied.
        """
        items.sort( lambda l, r: sorter( l[1], r[1] ) )

        if not sort_ascending:
            items.reverse()

        return items


    def get_column ( self, column ):
        """ Returns the column id corresponding to a specified column index.
        """
        return self.column_map[ column ]

    #-- Helper Methods ---------------------------------------------------------

    def image_for ( self, image ):
        """ Returns the ImageResource corresponding to the specified image,
            which may be a string specifying the name of the image.
        """
        if not isinstance( image, basestring ):
            return image

        self._image = image

        return self._image


    def theme_for ( self, theme ):
        """ Returns the Theme object for a specified theme, which may be a
            string describing the theme.
        """
        if not isinstance( theme, basestring ):
            return theme

        self._theme = theme

        return self._theme


    def font_for ( self, font ):
        """ Returns the GUI toolkit font object for a specified font, which
            may be a string describing the font.
        """
        if not isinstance( font, basestring ):
            return font

        self._font = font

        return self._font


    def color_for ( self, color ):
        """ Returns the GUI toolkit specific color corresponding to the
            specified toolkit neutral color.
        """
        if color is None:
            return None

        self._color = color

        return self._color


    def popup_for ( self, view = None, object = None, name = None,
                          kind = None, change_mode = None ):
        """ Displays a popup editor using the specified view for the specified
            object. If object is not specified, it defaults to the current
            'item'. The view can either be None, a View object or a ViewElement
            (such as a Group or Item). If None is specified, a View for the
            current adapter facet will be created.
        """
        if object is None:
            object, name = self.get_alias( self.row, self.column )
        elif name is None:
            name = self.column_id
            if isinstance( view, Item ):
                name = view.name

        if view is None:
            view = Item( name,
                show_label = False,
                style      = 'custom',
                editor     = self.get_editor( self.row, self.column )
            )

        if isinstance( view, Item ):
            view.show_label = False
            if view.name == '':
                view.name = name

            view = VGroup( view, group_theme = PopupTheme )

        if isinstance( view, basestring ):
            view = object.facet_view( view )

        if not isinstance( view, View ):
            view = View( view, kind = 'popup' )

        if kind is None:
            kind = view.kind

        if kind in PopupTypes:
            view.popup_bounds = self.bounds

        handler = None
        buttons = []
        if change_mode is None:
            change_mode = self.get_change_mode( self.row, self.column )

        if change_mode != 'live':
            from facets.ui.editors.grid_editor import DeferredEditHandler

            if change_mode == 'save':
                view.buttons = [ 'OK', 'Cancel' ]
                kind         = 'popout'

            handler = DeferredEditHandler(
                target_object = object
            ).set(
                target_name   = name
            )
            object = handler.defer_object

        context = {
            'object':  object,
            'adapter': self
        }
        if isinstance( self.item, HasFacets ):
            context[ 'item' ] = self.item

        object.edit_facets(
            view    = view,
            kind    = kind,
            parent  = self.grid_editor.adapter,
            context = context,
            handler = handler
        )


    def menu_for ( self, menu ):
        """ Returns the Menu object corresponding to the specified 'menu' value.
        """
        if isinstance( menu, Action ):
            menu = Menu( menu )
        elif isinstance( menu, SequenceTypes ):
            menu = Menu( *menu )

        return menu


    def auto_search_filter_for ( self, name, grid_filter, column ):
        """ Returns whether or not automatic searching/filtering is enabled for
            a specified *column*. *Grid_filter* specifies the GridFilter object
            the request is for, and *name* is the name of either the search or
            filter attribute. The corresponding ColumnFilter object is also
            added to or removed from *grid_filter* as needed.
        """
        filters = grid_filter.filters
        filter  = filters.get( column )
        result  = self._result_for( 'get_auto_' + name, 0, column )
        if result:
            if filter is None:
                filters[ column ] = ColumnFilter(
                                        is_search = (name == 'search') )
        elif filter is not None:
            del filters[ column ]

        return result


    def column_clicked_for ( self ):
        """ Handles the user clicking on a column header which has either
            'auto_filter' or 'auto_search' enabled. *Grid_filter* specifies
            either the searching or filtering GridFilter object.
        """
        filter = self.grid_filter.filters.get( self.column )
        search = self.grid_search.filters.get( self.column )
        if search is None:
            self.popup_for( '', filter, change_mode = 'live' )
        elif filter is None:
            self.popup_for( '', search, change_mode = 'live' )
        else:
            self.popup_for(
                '',  FilterSearch( filter = filter, search = search ),
                change_mode = 'live'
            )

    #-- Facets Default Values --------------------------------------------------

    def _columns_default ( self ):
        item = self.get_item( 0 )
        if item is None:
            return []

        if isinstance( item, HasFacets ):
            return [ ( user_name_for( name ), name )
                     for name in item.editable_facets() ]

        return []


    def _formatter_default ( self ):
        return self._format_cell


    def _grid_filter_default ( self ):
        return GridFilter( adapter = self )


    def _grid_search_default ( self ):
        return GridFilter( adapter = self )

    #-- Property Implementations -----------------------------------------------

    def _get_drag ( self ):
        return self.item


    def _get_text_color ( self ):
        if (self.screen_row % 2) == 1:
            return (self.even_text_color or self.default_text_color)

        return (self.odd_text_color or self.default_text_color)


    def _get_bg_color ( self ):
        if (self.screen_row % 2) == 1:
            return (self.even_bg_color or self.default_bg_color)

        return (self.odd_bg_color or self.default_bg_color)


    def _get_text ( self ):
        return self.get_formatter( self.row, self.column )(
                                   self.get_content( self.row, self.column ) )

    def _set_text ( self, value ):
        if isinstance( self.column_id, int ):
            self.item[ self.column_id ] = value
        else:
            setattr( self.item, self.column_id, value )


    def _get_content ( self ):
        if isinstance( self.column_id, int ):
            return self.item[ self.column_id ]

        return getattr( self.item, self.column_id )


    def _get_editor ( self ):
        try:
            return self.item.facet( self.column_id ).get_editor()
        except:
            return default_editor


    def _get_alias ( self ):
        return ( self.grid_editor, 'cell_value' )


    @property_depends_on( 'columns' )
    def _get_column_map ( self ):
        map = []
        for value in self.columns:
            if isinstance( value, tuple ):
                map.append( value[1] )
            else:
                map.append( value )

        return map


    @property_depends_on( 'columns' )
    def _get_label_map ( self ):
        map = []
        for i, value in enumerate( self.columns ):
            if isinstance( value, basestring ):
                map.append( value )
            else:
                map.append( value[0] )

        return map


    @property_depends_on( 'adapters, columns' )
    def _get_adapter_column_indices ( self ):
        labels = self.label_map
        map    = []
        for adapter in self.adapters:
            indices = []
            for label in adapter.columns:
                if not isinstance( label, basestring ):
                    label = label[0]

                indices.append( labels.index( label ) )

        return map


    @property_depends_on( 'adapters, columns' )
    def _get_adapter_column_map ( self ):
        labels = self.label_map
        map    = []
        for adapter in self.adapters:
            mapping = {}
            for label in adapter.columns:
                id = None
                if not isinstance( label, basestring ):
                    label, id = label

                key = labels.index( label )
                if id is None:
                    id = key

                mapping[ key ] = id

            map.append( mapping )

        return map

    #-- Private Methods --------------------------------------------------------

    def _color_result_for ( self, name, row, column ):
        """ Helper method for returning a color result.
        """
        return self.color_for( self._result_for( name, row, column ) )


    def _result_for ( self, name, row, column, value = Undefined ):
        """ Returns/Sets the value of the specified *name* attribute for the
            specified *object.facet[row].column* item.
        """
        object         = self.object
        facet          = self.name
        self.row       = row
        self.column    = column
        self.column_id = column_id = self.column_map[ column ]
        self.value     = value
        self.item      = item = self.get_item( row )
        item_class     = item.__class__
        key            = '%s:%s:%d' % ( item_class.__name__, name, column )
        handler        = self._hit_cache.get( key )
        if handler is not None:
            return handler()

        prefix     = name[:4]
        facet_name = name[4:]

        for i, adapter in enumerate( self.adapters ):
            if column in self.adapter_column_indices[i]:
                adapter.row    = row
                adapter.item   = item
                adapter.value  = value
                adapter.column = column_id = self.adapter_column_map[i][column]
                if adapter.accepts:
                    get_name = '%s_%s' % ( column_id, facet_name )
                    if adapter.facet( get_name ) is not None:
                        if prefix == 'get_':
                            handler = lambda: getattr( adapter.set(
                                row  = self.row, column = column_id,
                                item = self.item ), get_name )
                        else:
                            handler = lambda: setattr( adapter.set(
                                row  = self.row, column = column_id,
                                item = self.item ), get_name, self.value )

                        if adapter.is_cacheable:
                            break

                        return handler()
        else:
            if item is not None:
                for klass in item_class.__mro__:
                    handler = self._get_handler_for( '%s_%s_%s' %
                             ( klass.__name__, column_id, facet_name ), prefix )
                    if (handler is not None) or (klass is HasFacets):
                        break

            if handler is None:
                handler = self._get_handler_for( '%s_%s' % ( column_id,
                              facet_name ), prefix )

            if (handler is None) and (item is not None):
                for klass in item_class.__mro__:
                    handler = self._get_handler_for( '%s_%s' %
                                   ( klass.__name__, facet_name ), prefix )
                    if (handler is not None) or (klass is HasFacets):
                        break

            if handler is None:
                handler = self._get_handler_for( facet_name, prefix )

        self._hit_cache[ key ] = handler

        return handler()


    def _get_handler_for ( self, name, prefix ):
        """ Returns the handler for a specified facet name (or None if not
            found).
        """
        facet = self.facet( name )
        if (facet is not None) and (facet.handler is not Disallow):
            if prefix == 'get_':
                return lambda: getattr( self, name )

            return lambda: setattr( self, name, self.value )

        return getattr( self, name, None )


    def _format_cell ( self, content ):
        format = self.get_format( self.row, self.column )
        if format is None:
            column_id = self.column_id
            if ((not isinstance( column_id, int )) and
                isinstance( self.item, HasFacets )):
                return self.item.facet( column_id ).string_value(
                                                 self.item, column_id, content )

            format = '%s'

        return (format % content)

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'adapters.changed' )
    def _flush_cache ( self ):
        """ Flushes the cache when the columns or any facet on any adapter
            changes.
        """
        self._hit_cache = {}
        self.changed    = True


    @on_facet_set( 'columns' )
    def _needs_refresh ( self ):
        """ Handles something changing that requires a visual refresh.
        """
        self.refresh = True

#-------------------------------------------------------------------------------
#  'HistoCell' class:
#-------------------------------------------------------------------------------

class HistoCell ( HasPrivateFacets ):
    """ Support class for rendering grid cells whose value is drawn like a
        horizontal histogram item.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The color of the histogram bar:
    color = Color( 0xAFCDF0 )

    # The maximum value for the histogram range:
    maximum = Float( facet_value = True )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, cell ):
        """ Paints the grid cell for the specified cell.
        """
        g            = cell.graphics
        x, y, dx, dy = g.clipping_bounds
        hx           = round( (cell.content / self.maximum) * dx )
        pen          = g.pen
        g.pen        = None
        g.brush      = self.color
        g.draw_rectangle( x, y, hx, dy )

        if cell.paint_background:
            g.brush = cell.state_bg_color
            g.draw_rectangle( x + hx, y, dx - hx, dy )

        font = cell.state_font
        if font is not None:
            g.font = font

        color = cell.state_text_color
        if color is not None:
            g.text_color = color

        text = cell.text
        if text != '':
            tdx, tdy  = g.text_size( text )
            alignment = cell.alignment[:1]
            if alignment in ( 'l', 'd' ):
                tx = x + 4 + cell.indent
            elif alignment == 'r':
                tx = x + dx - tdx - 4
            else:
                tx = x + ((dx - tdx) / 2)

            g.pen = pen
            g.draw_text( text, tx, y + ((dy - tdy) / 2) )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def color_cell_paint ( cell ):
    """ Paints a grid cell whose value is a color as a 'color chip' of that
        color.
    """
    g            = cell.graphics
    x, y, dx, dy = g.clipping_bounds

    # Fill the cell background:
    if cell.paint_background:
        g.pen   = None
        g.brush = cell.state_bg_color
        g.draw_rectangle( x, y, dx, dy )

    # Draw the color sample (if enough room is available):
    indent = cell.indent
    if ((dx - indent) > 10) and (dy > 6):
        g.pen   = 0x000000
        g.brush = cell.grid_adapter.color_for( cell.content )
        g.draw_rectangle( x + 4 + indent, y + 2, dx - 8 - indent, dy - 4 )

#-------------------------------------------------------------------------------
#  'BooleanImages' class:
#-------------------------------------------------------------------------------

class BooleanImages ( SingletonHasPrivateFacets ):
    """ Helper class use to define the true/false images used by the
        boolean_cell_paint function.
    """

    #-- Facet Definitions ------------------------------------------------------

    true  = Image( '@facets:on2'  )
    false = Image( '@facets:off5' )
    check = Image( '@facets:on1'  )

boolean_images = None


def bool_cell_paint ( cell, normal = True ):
    """ Paints a grid cell whose value is a boolean using a check mark or 'x'
        image.
    """
    global boolean_images

    g            = cell.graphics
    x, y, dx, dy = g.clipping_bounds

    # Fill the cell background:
    if cell.paint_background:
        g.pen   = None
        g.brush = cell.state_bg_color
        g.draw_rectangle( x, y, dx, dy )

    # Make sure the images have been defined:
    if boolean_images is None:
        boolean_images = BooleanImages()

    # Draw the correct boolean image based upon the cell's value:
    image = boolean_images.false
    if cell.content:
        image = (boolean_images.true if normal else boolean_images.check)
    elif not normal:
        return

    # Calculate the correct horizontal alignment:
    alignment = cell.alignment[:1]
    if alignment in ( 'l', 'd' ):
        ix = x + 4 + cell.indent
    elif alignment == 'r':
        ix = dx - image.width - 4
    else:
        ix = x + ((dx - image.width) / 2)

    g.draw_bitmap( image.bitmap, ix, y + ((dy - image.height) / 2) )


def boolean_cell_paint ( cell ):
    """ Paints a grid cell whose value is a boolean using a check mark or 'x'
        image.
    """
    bool_cell_paint( cell, True )


def check_cell_paint ( cell ):
    """ Paints a grid cell whose value is a boolean using a check mark for True
        and no image if False.
    """
    bool_cell_paint( cell, False )


# Mapping from names to standard cell painters:
StandardCellPainters = {
    'Color':  color_cell_paint,
    'Bool':   boolean_cell_paint,
    'Check':  check_cell_paint
}

#-- EOF ------------------------------------------------------------------------