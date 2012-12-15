"""
A group of action manager items.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Any, Bool, HasFacets, List, Property, Str

from facets.core.facet_base \
    import user_name_for

from action \
    import Action

from action_item \
    import ActionItem

#-------------------------------------------------------------------------------
#  'Group' class:
#-------------------------------------------------------------------------------

class Group ( HasFacets ):
    """ A group of action manager items.

        By default, a group declares itself as requiring a separator when it is
        visualized, but this can be changed by setting its 'separator' facet to
        False.
    """

    #-- 'Group' Interface ------------------------------------------------------

    # Is the group enabled?
    enabled = Bool( True )

    # Is the group visible?
    visible = Bool( True )

    # The group's unique identifier (only needs to be unique within the action
    # manager that the group belongs to):
    id = Str

    # All of the items in the group:
    items = Property

    # The action manager that the group belongs to:
    parent = Any # Instance( 'facets.ui.pyface.action.ActionManager' )

    # Does this group require a separator when it is visualized?
    separator = Bool( True )

    #-- Private Facets ---------------------------------------------------------

    # All of the items in the group:
    _items = List #(ActionManagerItem)

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, *items,  **facets ):
        """ Creates a new menu manager.
        """
        # Base class constructor:
        super( Group, self ).__init__( **facets )

        # Add any specified items:
        for item in items:
            self.append( item )

    #-- 'Group' Interface ------------------------------------------------------

    #-- Property Implementations -----------------------------------------------

    def _get_items ( self ):
        """ Returns the items in the group.
        """
        return self._items[:]

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self, enabled ):
        """ Static facet change handler.
        """
        for item in self.items:
            item.enabled = enabled

    #-- Public Methods ---------------------------------------------------------

    def append ( self, item ):
        """ Appends an item to the group.

            See the documentation for 'insert'.
        """
        return self.insert( len( self._items ), item )


    def clear ( self ):
        """ Remove all items from the group.
        """
        self._items = []


    def destroy ( self ):
        """ Called when the manager is no longer required.

            By default this method simply calls 'destroy' on all items in the
            group.
        """
        for item in self.items:
            item.destroy()


    def insert ( self, index, item ):
        """ Inserts an item into the group at the specified index.

            1) An 'ActionManagerItem' instance.

                In which case the item is simply inserted into the group.

            2) An 'Action' instance.

                In which case an 'ActionItem' instance is created with the
                action and then inserted into the group.

            3) A Python callable (ie.'callable(item)' returns True).

                In which case an 'Action' is created that calls the callable
                when it is performed, and the action is then wrapped as in 2).
        """
        if callable( item ):
            item = Action( text       = user_name_for( item.func_name ),
                           on_perform = item )

        if isinstance( item, Action ):
            item = ActionItem( action = item, parent = self )

        self._items.insert( index, item )

        return item


    def remove ( self, item ):
        """ Removes an item from the group.
        """
        self._items.remove( item )
        item.parent = None


    def insert_before ( self, before, item ):
        """ Inserts an item into the group before the specified item.

            See the documentation for 'insert'.
        """
        index = self._items.index( before )
        self.insert( index, item )

        return ( index, item )


    def insert_after ( self, after, item ):
        """ Inserts an item into the group after the specified item.

            See the documentation for 'insert'.
        """
        index = self._items.index( after )
        self.insert( index + 1, item )

        return ( index, item )


    def find ( self, id ):
        """ Returns the item with the specified Id.

            Returns None if no such item exists.
        """
        for item in self._items:
            if item.id == id:
                break

        else:
            item = None

        return item

#-------------------------------------------------------------------------------
#  'Separator' class:
#-------------------------------------------------------------------------------

class Separator ( Group ):
    """ A convenience class.

        This is only used in 'cheap and cheerful' applications that create menus
        like::

            file_menu = MenuManager(
                CopyAction(),
                Separator(),
                ExitAction()
            )

        Hopefully, 'Separator' is more readable than 'Group'...
    """
    pass

#-- EOF ------------------------------------------------------------------------