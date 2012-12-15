"""
Defines the AttrList class which allows you to map a list of values into an
object which appears to have a variable number of facets with names of the
form: attr_n, where 0 <= n < len(list).

The intended purpose of the class is for use in user interfaces that wish to
have an unique editor associated with each list item.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, List, Str, Int, Bool, Instance, Event, Property, \
           View, Item, Handler, EditorFactory

from facets.ui.pyface.timer.api \
    import do_later

#-------------------------------------------------------------------------------
#  'AttrList' class:
#-------------------------------------------------------------------------------

class AttrList ( HasPrivateFacets ):
    """ Defines the AttrList class which allows you to map a list of values
        into an object which appears to have a variable number of facets with
        names of the form: attr_n, where 0 <= n < len(list).

        The intended purpose of the class is for use in user interfaces that
        wish to have an unique editor associated with each list item.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of items being mapped to individual attributes:
    items = List( facet_value = True )

    # The prefix to be used when displaying the dynamic attributes in a UI:
    prefix = Str( 'Attr' )

    # The logical starting index of the dynamic attributes when displayed in a
    # UI:
    origin = Int( 0 )

    # Should labels be displayed when viewing the dynamic attributes n a UI:
    show_labels = Bool( True )

    # Should the user interface view be scrollable if there are many dynamic
    # items to view, or should it adjust its minimum size to encompass all of
    # the dynamic items?
    scrollable = Bool( False )

    # The editor to use when displaying the dynamic attributes in a UI:
    editor = Instance( EditorFactory )

    # Event fired when list changes size:
    resized = Event

    #-- Property Implementations -----------------------------------------------

    def _get_attr_list ( self, name ):
        try:
            return self.items[ int( name[ name.find( '_' ) + 1: ] ) ]
        except IndexError:
            raise AttributeError(
                "'%s' object has no attribute '%s'" %
                ( self.__class__.__name__, name )
            )

    def _set_attr_list ( self, name, value ):
        try:
            index = int( name[ name.find( '_' ) + 1: ] )
            old   = self.items[ index ]
            if old != value:
                self.items[ index ] = value
                self.facet_property_set( name, old, value )
        except IndexError:
            raise AttributeError(
                "'%s' object has no attribute '%s'" %
                ( self.__class__.__name__, name )
            )

    # The dynamically defined set of attributes being mapped to each list item:
    attr__ = Property( _get_attr_list, _set_attr_list )

    #-- Facet Event Handlers ---------------------------------------------------

    def _items_set ( self, old, new ):
        """ Handles the 'items' facet being changed.
        """
        nn = len( new )
        no = 0
        if old is not None:
            no = len( old )

        #for i in xrange( nn ):
        #    oi = Undefined
        #    if i < no:
        #        oi = old[i]
        #
        #    self.facet_property_set( 'attr_%d' % i, oi, new[i] )

        if no != nn:
            self.resized = True


    def _items_items_set ( self, event ):
        """ Handles the contents of the 'items' facet being changed.
        """
        removed = event.removed
        added   = event.added
        index   = event.index
        n       = len( added )
        if n == len( removed ):
            for i in range( n ):
                if removed[i] != added[i]:
                    self.facet_property_set( 'attr_%d' % (index + i),
                                             removed[i], added[i] )
        else:
            old = self.items[:]
            old[ index: index + len( added ) ] = removed
            self._items_set( old, self.items )

    #-- Facet Default Values -------------------------------------------------

    def _editor_default ( self ):
        """ Returns the default value for the 'editor' facet.
        """
        facet  = self.facet( 'items' )
        editor = facet.editor
        if editor is None:
            facet = facet.item_facet
            if facet is not None:
                editor = facet.get_editor()

        return editor

    #-- HasFacets Method Overrides -------------------------------------------

    def default_facets_view ( self ):
        """ Returns the default facets view for the object.
        """
        return View(
            *self.view_items(),
            scrollable = self.scrollable,
            handler    = AttrListHandler()
        )


    def view_items ( self ):
        """ Returns the list of Items that should appear in the view.
        """
        prefix      = self.prefix
        origin      = self.origin
        show_labels = self.show_labels
        editor      = self.editor

        return [ Item( 'attr_%d' % i,
                       label      = '%s%d' % ( prefix, i + origin ),
                       show_label = show_labels,
                       editor     = editor )
                 for i in xrange( len( self.items ) ) ]

#-------------------------------------------------------------------------------
#  'AttrListHandler' class:
#-------------------------------------------------------------------------------

class AttrListHandler ( Handler ):
    """ Handler for the default AttrList class user interface.
    """

    #-- Facet Event Handlers ---------------------------------------------------

    def object_resized_changed ( self, info ):
        """ Force the user interface to be rebuilt when the underlying object
            list is resized.
        """
        if info.initialized:
            info.initialized = False
            do_later( self._rebuild_ui, info )


    def _rebuild_ui ( self, info ):
        info.ui.view.content.content = info.object.view_items()
        info.ui.updated = True

#-------------------------------------------------------------------------------
#  Test Case:
#-------------------------------------------------------------------------------

if __name__ == '__main__':

    from facets.api \
        import Button, VGroup, HGroup, ValueEditor

    class Test ( HasPrivateFacets ):

        add    = Button( 'Add' )
        remove = Button( 'Remove' )
        data   = List( Int )
        al     = Instance( AttrList, () )

        view = View(
            VGroup(
                Item( 'al@' ),
                HGroup(
                    Item( 'add' ),
                    Item( 'remove',
                          enabled_when = 'len(al.items) > 0'
                    ),
                    show_labels = False
                ),
                Item( 'al', editor = ValueEditor() ),
                show_labels = False
            )
        )

        def _al_default ( self ):
            return AttrList(
                items       = [ 1, 2, 3, 4, 5 ],
                show_labels = False,
                prefix      = 'Field',
                origin      = 1
            )

        def _add_set ( self ):
            self.al.items.append( len( self.al.items ) + 1 )

        def _remove_set ( self ):
            del self.al.items[-1]


    Test( data = [ 1, 2, 3, 4, 5 ] ).edit_facets()

#-- EOF ------------------------------------------------------------------------