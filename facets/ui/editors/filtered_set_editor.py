"""
Defines a FilteredSetEditor which allows the user to display the list of items
for a selectable set using dynamic filtering criteria which orders the items
best matching the filter first.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Bool, Callable, Enum, Str, List, View, HGroup, VGroup, Item, \
           UItem, UIEditor, BasicEditorFactory, SyncValue, Property,         \
           property_depends_on, on_facet_set

from facets.ui.editors.set_editor \
    import SetEditor, SetItem

#-------------------------------------------------------------------------------
#  '_FilteredSetEditor' class:
#-------------------------------------------------------------------------------

class _FilteredSetEditor ( UIEditor ):
    """ Defines the _FilteredSetEditor class.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current filter value:
    filter = Str

    # Are the matching filtered set items displayed first or last?
    order = Enum( 'First', 'Last' )

    # The current sort ordering multiplier (+1/-1):
    ordering = Property

    # A local copy of the set of all possible values:
    values = Any( facet_value = True )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        factory     = self.factory
        self.values = factory.facet_value( 'values' )

        return View(
            HGroup(
                Item( 'filter',
                      springy = True,
                      label   = 'Match',
                      tooltip = 'Match items containing this string'
                ),
                UItem( 'order',
                       tooltip = 'Order to display matching items'
                ),
                group_theme = '#themes:tool_options_group'
            ),
            VGroup(
                UItem( 'value',
                       editor = SetEditor(
                           values   = SyncValue( self, 'values' ),
                           ordering = 'sort',
                           separate = factory.separate,
                           adapter  = factory.adapter,
                           key      = self._item_key()
                       )
                )
            )
        )

    #-- Public Methods ---------------------------------------------------------

    def init_ui ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        return self.edit_facets( parent = parent, kind = 'editor' )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'filter, ordering' )
    def _filter_modified ( self ):
        """ Handles the 'filter' or 'ordering' facet being changed.
        """
        # Note: This is a hack to force the SetEditor factory values to appear
        # to have changed, causing the sort to be re-done using the new filter
        # or ordering value:
        values      = self.values[:]
        self.values = []
        self.values = values

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'order' )
    def _get_ordering ( self ):
        return ((2 * (self.order == 'First')) - 1)

    #-- Private Methods --------------------------------------------------------

    def _item_key ( self ):
        """ Returns the 'key' function to pass to the SetEditor used internally.
        """
        key = self.factory.key
        if key is None:
            return self._default_key

        def ordered_key ( item ):
            return (self.ordering * key( self.filter, item ))

        return ordered_key


    def _default_key ( self, item ):
        """ Returns the default key to use for a specified *item* for sorting
            set editor values.
        """
        col = item.lower().find( self.filter.lower() )

        return (self.ordering * (col if col >= 0 else 99999999))

#-------------------------------------------------------------------------------
#  'FilteredSetEditor' class:
#-------------------------------------------------------------------------------

class FilteredSetEditor ( BasicEditorFactory ):
    """ Defines the FilteredSetEditor class.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _FilteredSetEditor

    # The set of all possible values:
    values = Any( facet_value = True )

    # Separate selected items from unselected items:
    separate = Bool( True )

    # Function to convert user items into editor items:
    adapter = Callable( SetItem )

    # Function that returns the value to sort on. It should be a function of the
    # form: number = key( filter, item ), where 'filter' is the current value
    # of the UI 'Filter' field, and 'item' is the set item whose sort value is
    # to be computed. The result should be a number (integer or float)
    # specifying the relative rank of the specified 'item' in the sorted result.
    # The set items are displayed in ascending order based on the result
    # returned by the callable for each set item:
    key = Callable

#-- EOF ------------------------------------------------------------------------