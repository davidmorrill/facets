"""
Defines the HierarchicalGridAdapter class, a subclass of the GridAdapter class
that supports hierarchical data (i.e. items that may or may not have child
items).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Any, Int, Bool, Image, Property, \
           property_depends_on

from grid_adapter \
    import GridAdapter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The number of pixels/hierarchy level:
INDENT = 15

#-------------------------------------------------------------------------------
#  'HierarchyItem' class:
#-------------------------------------------------------------------------------

class HierarchyItem ( HasPrivateFacets ):
    """ Describes an item in a hierarchical grid.
    """

    # The item to be displayed in the grid:
    item = Any

    # Does the item have any children?
    has_children = Bool

    # Is the item currently open?
    is_open = Bool

    # The level of this item within the hierarchy (0 based):
    level = Int( 0 )

    # The item's children:
    children = Any # List( HierarchyItem )

    # The list of all visible children of this item:
    visible_children = Property

    # The grid adapter this item is associated with:
    grid_adapter = Any # Instance( HierarchicalGridAdapter )

    #-- Facet Default Values ---------------------------------------------------

    def _is_open_default ( self ):
        result = self.grid_adapter.is_open( self.item )
        if result:
            self._init_children()

        return result


    def _has_children_default ( self ):
        return self.grid_adapter.has_children( self.item )

    #-- Property Implementations -----------------------------------------------

    def _get_visible_children ( self ):
        visible = []
        if self.is_open:
            for item in self.children:
                visible.append( item )
                visible.extend( item.visible_children )

        return visible

    #-- Facet Event Handlers ---------------------------------------------------

    def _is_open_set ( self, is_open ):
        """ Handles the 'is_open' facet being changed.
        """
        if is_open and (self.children is None):
            self._init_children()

        self.grid_adapter.is_open( self.item, is_open )
        self.grid_adapter.changed = True


    def _children_modified ( self ):
        """ Handles the children of this item being modified.
        """
        current      = dict( [ ( item.item, item ) for item in self.children ] )
        items        = []
        level        = self.level + 1
        grid_adapter = self.grid_adapter
        for item in self.grid_adapter.children( self.item ):
            hitem = current.get( item )
            if hitem is None:
                hitem = HierarchyItem( item         = item,
                                       grid_adapter = grid_adapter,
                                       level        = level )
            else:
                del current[ item ]

            items.append( hitem )

        # Dispose of any items no longer in the list of children:
        for hitem in current.itervalues():
            hitem.dispose()

        self.children = items
        self.grid_adapter.changed = True

    #-- Public Methods ---------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the object when it is no longer needed.
        """
        if self.children is not None:
            self.children = None
            self.grid_adapter.on_children_changed(
                self.item, self._children_modified, True
            )

        self.grid_adapter = None

    #-- Private Methods --------------------------------------------------------

    def _init_children ( self ):
        """ Initializes the list of children for this item.
        """
        grid_adapter  = self.grid_adapter
        level         = self.level + 1
        self.children = [
            HierarchyItem( item         = child,
                           grid_adapter = grid_adapter,
                           level        = level )
            for child in grid_adapter.children( self.item )
        ]
        grid_adapter.on_children_changed(
            self.item, self._children_modified, False
        )

#-------------------------------------------------------------------------------
#  'HierarchicalGridAdapter' class:
#-------------------------------------------------------------------------------

class HierarchicalGridAdapter ( GridAdapter ):
    """ Defines the HierarchicalGridAdapter class, a subclass of the GridAdapter
        class that supports hierarchical data (i.e. items that may or may not
        have child items).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The image to use when a hierarchy level is closed:
    closed_image = Image( '@icons:closed_dark' )

    # The image to use when a hierarchy level is open:
    open_image = Image( '@icons:open_dark' )

    #-- Private Facet Definitions ----------------------------------------------

    # The current object hierarchy:
    all_items = Any( [] )

    # The current flattened, visible portion of the object hierarchy:
    visible_items = Property

    #-- Public Methods (must be overridden by subclasses) ----------------------

    def is_open ( self, object, is_open = None ):
        """ If *is_open* is None, the method should return True if the specified
            *object* is initially in the "open" state, and False if it is
            initially in the "closed" stated.

            If *is_open* is True or False, the user has changed the "open" state
            of the specified *object* to  the value specified by *is_open*. In
            this case, the return value is ignored.
        """
        return False


    def has_children ( self, object ):
        """ Returns True if the specified *object* can have children, and False
            otherwise.
        """
        return False


    def children ( self, object ):
        """ Returns a (possibly empty) list of the children of the specified
            *object*.
        """
        return []


    def on_children_changed ( self, object, listener, remove ):
        """ Adds/Removes the event listener specified by *listener* on *object*.
            The listener should be called whenever items are added to or removed
            from the children of *object*. If *remove* is True, then the
            *listener* should be removed from *object*. If it is True, then the
            *listener* should be added.
        """

    #-- Facet Default Values ---------------------------------------------------

    def _all_items_default ( self ):
        self.object.on_facet_set( self._root_modified, self.name + '[]' )

        return [ HierarchyItem( item = item, grid_adapter = self )
                 for item in getattr( self.object, self.name ) ]

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'changed' )
    def _get_visible_items ( self ):
        items = []
        for item in self.all_items:
            items.append( item )
            items.extend( item.visible_children )

        return items

    #-- Facet Event Handlers ---------------------------------------------------

    def _root_modified ( self, event ):
        """ Handles the contents of the hierarchy's root level being changed.
        """
        current = dict( [ ( item.item, item ) for item in self.all_items ] )
        items   = []
        for item in getattr( self.object, self.name ):
            hitem = current.get( item )
            if hitem is None:
                hitem = HierarchyItem( item = item, grid_adapter = self )
            else:
                del current[ item ]

            items.append( hitem )

        # Dispose of any items no longer in the list of children:
        for hitem in current.itervalues():
            hitem.dispose()

        self.all_items = items
        self.changed   = True

    #-- Private Methods --------------------------------------------------------

    def get_item ( self, row ):
        """ Returns the value of the specified row item.
        """
        try:
            return self.visible_items[ row ].item
        except:
            return None


    def len ( self ):
        """ Returns the number of items in the associated facet value.
        """
        return len( self.visible_items )


    def get_indent ( self, row, column ):
        """ Returns the amount of indenting to use with the specified row:column
            item when it is left-aligned.
        """
        if column != 0:
            return super( HierarchicalGridAdapter, self ).get_indent( row,
                                                                      column )

        return (self.visible_items[ row ].level * INDENT)


    def get_image ( self, row, column ):
        """ Returns the image to use for a specified row:column item. A result
            of None means no image should be used. Otherwise, the result should
            be an ImageResource item specifying the image to use, or a string
            which can be converted to an ImageResource.
        """
        if column != 0:
            return super( HierarchicalGridAdapter, self ).get_image( row,
                                                                     column )

        item = self.visible_items[ row ]
        if not item.has_children:
            return None

        if item.is_open:
            return self.open_image

        return self.closed_image


    def get_clicked ( self, row, column ):
        """ Returns the adapter method handling a cell 'clicked' event for a
            specified row:column item.
        """
        if column != 0:
            return super( HierarchicalGridAdapter, self ).get_clicked( row,
                                                                       column )

        item = self.visible_items[ row ]
        if item.has_children:
            item.is_open = not item.is_open

        return None


    def sort ( self, items, sorter, sort_ascending ):
        """ Returns the list of *items* sorted using the *sorter* function and
            in the order specified by *sort_ascending*. Each element in *items*
            is a tuple of the form: (index, value), where *index* specifies
            the original index of *value* after any filtering has been applied.
        """
        item_ids = dict( [ ( id( item[1] ), item[0] ) for item in items ] )

        return self._sort( self.all_items, sorter, sort_ascending, item_ids )


    def _sort ( self, items, sorter, sort_ascending, item_ids ):
        matches = []
        for item in items:
            item_item = item.item
            index     = item_ids.get( id( item_item ) )
            if index is not None:
                matches.append( ( index, item_item ) )

        matches.sort( lambda l, r: sorter( l[1], r[1] ) )

        if not sort_ascending:
            matches.reverse()

        visible_items = self.visible_items
        result        = []
        for index, item_item in matches:
            item = visible_items[ index ]
            result.append( ( index, item_item ) )
            if item.is_open:
                result.extend(
                   self._sort( item.children, sorter, sort_ascending, item_ids )
                )

        return result

#-- EOF ------------------------------------------------------------------------
