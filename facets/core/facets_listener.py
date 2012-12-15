"""
Defines classes used to implement and manage various facet listener patterns.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re
import string

from string \
    import whitespace

from weakref \
    import WeakKeyDictionary

from has_facets \
    import HasPrivateFacets

from facet_base \
    import Undefined, Uninitialized

from facet_defs \
    import Property

from facet_types \
    import Str, Int, Bool, Instance, Any

from facet_errors \
    import FacetError

from facet_notifiers \
   import FacetsListener, ListenerSetWrapper, ARG_NONE, ARG_VALUE

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# End of String marker:
EOS = '\0'

# Types of facets that can be listened to:
ANYTRAIT_LISTENER = '_register_anyfacet'
SIMPLE_LISTENER   = '_register_simple'
LIST_LISTENER     = '_register_list'
DICT_LISTENER     = '_register_dict'
SET_LISTENER      = '_register_set'

# Mapping from facet collection types to listener types:
type_map = {
    'none': SIMPLE_LISTENER,
    'list': LIST_LISTENER,
    'dict': DICT_LISTENER,
    'set':  SET_LISTENER
}

# Invalid destination ( object, name ) reference marker (i.e. ambiguous):
INVALID_DESTINATION = ( None, None )

# Invalid objects for unregistering:
InvalidObjects = ( None, Uninitialized )

# Regular expressions used by the parser:
simple_pat = re.compile( r'^([a-zA-Z_]\w*)(\.|:)([a-zA-Z_]\w*)$' )
name_pat   = re.compile( r'([a-zA-Z_]\w*)\s*(.*)' )

# Characters valid in a facets name:
name_chars = string.ascii_letters + string.digits + '_'

#-------------------------------------------------------------------------------
# Helper Functions:
#-------------------------------------------------------------------------------

def indent ( text, first_line = True, n = 1, width = 4 ):
    """ Indent lines of text.

        Parameters
        ----------
        text : str
            The text to indent.
        first_line : bool, optional
            If False, then the first line will not be indented.
        n : int, optional
            The level of indentation.
        width : int, optional
            The number of spaces in each level of indentation.

        Returns
        -------
        indented : str
    """
    lines = text.split( '\n' )
    if not first_line:
        first = lines[0]
        lines = lines[1:]

    spaces = ' ' * ( width * n )
    lines2 = [ spaces + x for x in lines ]

    if not first_line:
        lines2.insert( 0, first )

    indented = '\n'.join( lines2 )

    return indented

#-------------------------------------------------------------------------------
#  Metadata filters:
#-------------------------------------------------------------------------------

def is_not_none ( value ): return (value is not None)
def is_none ( value ):     return (value is None)
def not_event ( value ):   return (value != 'event')

#-------------------------------------------------------------------------------
#  'ListenerBase' class:
#-------------------------------------------------------------------------------

class ListenerBase ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The handler to be called when any listened to facet is changed:
    #handler = Any

    # The dispatch mechanism to use when invoking the handler:
    #dispatch = Str

    # Does the handler go at the beginning (True) or end (False) of the
    # notification handlers list?
    #priority = Bool( False )

    # The next level (if any) of ListenerBase object to be called when any of
    # our listened to facets is changed:
    #next = Instance( ListenerBase )

    # Should changes to this item generate a notification to the handler?
    # notify = Bool

    # Should registering listeners for items reachable from this listener item
    # be deferred until the associated facet is first read or set?
    # deferred = Bool

    #-- Public Methods ---------------------------------------------------------

    def extract_static ( self ):
        """ Extracts all 'static' ListenerItem objects. A static item is one
            that can be added to a class-level facet's notifier list. The
            result is a tuple of the form: ([simple ListenerItem,...],
            the_rest). The first tuple element is the (possibly empty) list of
            simple ListenerItem objects, and the second element is the
            non-simple remainder, which may be None, a ListenerItem or a
            ListenerGroup.
        """
        raise NotImplementedError


    def register ( self, new ):
        """ Registers new listeners.
        """
        raise NotImplementedError


    def unregister ( self, old ):
        """ Unregisters any existing listeners.
        """
        raise NotImplementedError


    def handle ( self, object, facet, old, new ):
        """ Handles a facet change for a simple facet.
        """
        raise NotImplementedError


    def handle_list ( self, object, facet, old, new ):
        """ Handles a facet change for a list facet.
        """
        raise NotImplementedError


    def handle_list_items ( self, object, facet, old, new ):
        """ Handles a facet change for a list facets items.
        """
        raise NotImplementedError


    def handle_dict ( self, object, facet, old, new ):
        """ Handles a facet change for a dictionary facet.
        """
        raise NotImplementedError


    def handle_dict_items ( self, object, facet, old, new ):
        """ Handles a facet change for a dictionary facets items.
        """
        raise NotImplementedError

#-------------------------------------------------------------------------------
#  'ListenerItem' class:
#-------------------------------------------------------------------------------

class ListenerItem ( ListenerBase ):

    #-- Facet Definitions (set by parser) --------------------------------------

    # The name of the facet to listen to:
    name = Str

    # Is the name simple (no metadata or name prefix)?
    simple = Bool( True )

    # Is the name being defined optional?
    optional = Bool( False )

    # The name of any metadata that must be present (or not present):
    metadata_name = Str

    # Does the specified metadata need to be defined (True) or not defined
    # (False)?
    metadata_defined = Bool( True )

    # Is this an 'any_facet' change listener, or does it create explicit
    # listeners for each individual facet?
    is_any_facet = Bool( False )

    # Is the associated handler a special list handler that handles both
    # 'foo' and 'foo_items' events by receiving a list of 'deleted' and 'added'
    # items as the 'old' and 'new' arguments?
    list_handler = Bool( False )

    # Should changes to this item generate a notification to the handler?
    notify = Bool( True )

    # The next level (if any) of ListenerBase object to be called when any of
    # this object's listened-to facets is changed:
    next = Instance( ListenerBase )

    #-- Facet Definitions (not set by parser) ----------------------------------

    # The handler to be called when any listened-to facet is changed:
    handler = Any

    # A 'wrapped' version of 'handler':
    wrapped_handler = Any

    # The wrapper class to use for this listener:
    wrapper_class = Property

    # The dispatch mechanism to use when invoking the handler:
    dispatch = Str( 'same' )

    # Does the handler go at the beginning (True) or end (False) of the
    # notification handlers list?
    priority = Bool( False )

    # Should registering listeners for items reachable from this listener item
    # be deferred until the associated facet is first read or set?
    deferred = Bool( False )

    # A dictionary mapping objects to a list of all current active
    # (*name*, *type*) listener pairs, where *type* defines the type of
    # listener, one of: (SIMPLE_LISTENER, LIST_LISTENER, DICT_LISTENER).
    active = Instance( WeakKeyDictionary, () )

    #-- Property Implementations -----------------------------------------------

    def _get_wrapper_class ( self ):
        return ListenerSetWrapper

    #-- 'ListenerBase' Class Method Implementations ----------------------------

    def clone ( self ):
        """ Returns a post-parser clone of this object.
        """
        next = self.next
        if next is not None:
            next = next.clone()

        return self.__class__(
            name             = self.name,
            simple           = self.simple,
            optional         = self.optional,
            metadata_name    = self.metadata_name,
            metadata_defined = self.metadata_defined,
            is_any_facet     = self.is_any_facet,
            list_handler     = self.list_handler,
            notify           = self.notify,
            dispatch         = self.dispatch,
            priority         = self.priority,
            next             = next
        )


    def extract_static ( self ):
        """ Extracts all 'static' ListenerItem objects. A static item is one
            that can be added to a class-level facet's notifier list. The
            result is a tuple of the form: ([simple ListenerItem,...],
            the_rest). The first tuple element is the (possibly empty) list of
            simple ListenerItem objects, and the second element is the
            non-simple remainder, which may be None, a ListenerItem or a
            ListenerGroup.
        """
        if ((self.next is not None)                  or
            (not (self.simple or self.is_any_facet)) or
            self.list_handler):         ### TEMPORARY RESTRICTION ###
            return ( [], self )

        return ( [ self ], None )


    def register_static ( self, new ):
        """ Registers new listeners for a static context (e.g. a method
            decorator).
        """
        # Statically registered listeners need to be kept alive for the entire
        # lifetime of the object (i.e. *new*) that they are associated with,
        # otherwise the listeners they set up will be garbage collected:
        new.__dict__.setdefault( FacetsListener, {} ).setdefault( '', []
                                                                ).append( self )

        name = self.name
        if self.simple:
            # No wildcard matching, just get the specified facet:
            facet = new.base_facet( name )

            # Try to get the object facet:
            if facet is None:
                # Raise an error if facet is not defined and not optional:

                # fixme: Properties which are lists don't implement the
                # '..._items' sub-facet, which can cause a failure here when
                # used with an editor that sets up listeners on the items...
                if not self.optional:
                    raise FacetError(
                        "'%s' object has no '%s' facet" %
                        ( new.__class__.__name__, name )
                    )

                return INVALID_DESTINATION

            # Determine whether the facet type is simple, list, set or
            # dictionary:
            type    = SIMPLE_LISTENER
            handler = facet.handler
            if handler is not None:
                type = type_map[ handler.collection_type ]

            return getattr( self, type)( new, name, False )

        if self.is_any_facet:
            return self._register_anyfacet( new, name, False )

        return self.register( new, False )


    def register ( self, new, dynamic = True ):
        """ Registers new listeners.
        """
        # In the dynamic case, make sure we actually have an object to set
        # listeners on and that it has not already been registered (cycle
        # breaking):
        if (dynamic and
           ((new is None) or (new is Undefined) or (new in self.active))):
            return INVALID_DESTINATION

        # Create a list of (name: facet_values) tuples that match the object's
        # definition for the 'new' object:
        if self.is_any_facet:
            # Handle the special case of an 'anyfacet' change listener:
            try:
                self.active[ new ] = [ ( '', ANYTRAIT_LISTENER ) ]

                return self._register_anyfacet( new, '', False )

            except TypeError:
                # This error can occur if 'new' is a list or other object for
                # which a weakref cannot be created as the dictionary key for
                # 'self.active':
                return INVALID_DESTINATION

        name = self.name
        if not self.simple:
            # Handle facet matching based on a common name prefix and/or
            # matching facet metadata:
            metadata = self._metadata
            if metadata is None:
                self._metadata = metadata = { 'type': not_event }
                if self.metadata_name != '':
                    if self.metadata_defined:
                        metadata[ self.metadata_name ] = is_not_none
                    else:
                        metadata[ self.metadata_name ] = is_none

            # Get all object facets with matching metadata:
            names = new.facet_names( **metadata )

            # If a name prefix was specified, filter out only the names that
            # start with the specified prefix:
            if name != '':
                n     = len( name )
                names = [ aname for aname in names if name == aname[ : n ] ]

            # Create the dictionary of selected facets:
            bt     = new.base_facet
            facets = [ ( name, bt( name ) ) for name in names ]

            # Handle any new facets added dynamically to the object:
            new.on_facet_set( self._new_facet_added, 'facet_added' )
        else:
            # No wildcard matching, just get the specified facet:
            facet = new.base_facet( name )

            # Try to get the object facet:
            if facet is None:
                # Raise an error if facet is not defined and not optional:

                # fixme: Properties which are lists don't implement the
                # '..._items' sub-facet, which can cause a failure here when
                # used with an editor that sets up listeners on the items...
                if not self.optional:
                    raise FacetError(
                        "'%s' object has no '%s' facet" %
                        ( new.__class__.__name__, name )
                    )

                # Otherwise, just skip it:
                facets = []
            else:
                # Create a result dictionary containing just the single facet:
                facets = [ ( name, facet ) ]

        if dynamic:
            self.active[ new ] = active = []

        # For each item, determine its type (simple, list, dict):
        for name, facet in facets:

            # Determine whether the facet type is simple, list, set or
            # dictionary:
            type    = SIMPLE_LISTENER
            handler = facet.handler
            if handler is not None:
                type = type_map[ handler.collection_type ]

            # Add the name and type to the list of facets being registered:
            if dynamic:
                active.append( ( name, type ) )

            # Set up the appropriate facet listeners on the object for the
            # current facet:
            value = getattr( self, type )( new, name, False )

        if len( facets ) == 1:
            return value

        return INVALID_DESTINATION


    def unregister ( self, old ):
        """ Unregisters any existing listeners.
        """
        if old not in InvalidObjects:
            try:
                active = self.active.pop( old, None )
                if active is not None:
                    for name, type in active:
                        getattr( self, type )( old, name, True )
            except TypeError:
                # An error can occur if 'old' is a list or other object for
                # which a weakref cannot be created and used an a key for
                # 'self.active':
                pass


    def handle_simple ( self, object, facet, old, new ):
        """ Handles a facet change for an intermediate link facet.
        """
        self.next.unregister( old )
        self.next.register( new )


    def handle_dst ( self, object, facet, old, new ):
        """ Handles a facet change for an intermediate link facet when the
            notification is for the final destination facet.
        """
        self.next.unregister( old )

        object, name = self.next.register( new )
        if old is not Uninitialized:
            if object is None:
                raise FacetError(
                    'on_facet_set handler signature is incompatible with a '
                    'change to an intermediate facet'
                )

            self.wrapped_handler( object, name, old,
                                  getattr( object, name, Undefined ), None )


    def handle_list ( self, object, facet, old, new ):
        """ Handles a facet change for a list (or set) facet.
        """
        if old not in InvalidObjects:
            unregister = self.next.unregister
            for obj in old:
                unregister( obj )

        register = self.next.register
        for obj in new:
            register( obj )


    def handle_list_items ( self, object, facet, old, new ):
        """ Handles a facet change for items of a list (or set) facet.
        """
        self.handle_list( object, facet, new.removed, new.added )


    def handle_list_items_special ( self, object, facet, old, new ):
        """ Handles a facet change for items of a list (or set) facet with
            notification.
        """
        self.wrapped_handler( object, facet, new.removed, new.added, None )


    def handle_dict ( self, object, facet, old, new ):
        """ Handles a facet change for a dictionary facet.
        """
        if old is not Uninitialized:
            unregister = self.next.unregister
            for obj in old.values():
                unregister( obj )

        register = self.next.register
        for obj in new.values():
            register( obj )


    def handle_dict_items ( self, object, facet, old, new ):
        """ Handles a facet change for items of a dictionary facet.
        """
        self.handle_dict( object, facet, new.removed, new.added )

        if len( new.changed ) > 0:
            unregister = self.next.unregister
            register   = self.next.register
            dict       = getattr( object, facet )
            for key, obj in new.changed.items():
                unregister( obj )
                register( dict[ key ] )


    def handle_error ( self ):
        """ Handles an invalid intermediate facet change to a handler that must
            be applied to the final destination object.facet.
        """
        raise FacetError(
            'on_facet_set handler signature is incompatible with a change to '
            'an intermediate facet'
        )


    def __repr__ ( self, seen = None ):
        """ Returns a string representation of the object.

            Since the object graph may have cycles, we extend the basic __repr__
            API to include a set of objects we've already seen while
            constructing a string representation. When this method tries to get
            the repr of a ListenerItem or ListenerGroup, we will use the
            extended API and build up the set of seen objects. The repr of a
            seen object will just be '<cycle>'.
        """
        if seen is None:
            seen = set()

        seen.add( self )
        next_repr = 'None'
        next      = self.next
        if next is not None:
            if next in seen:
                next_repr = '<cycle>'
            else:
                next_repr = next.__repr__( seen )

        return ("""%s(
    name             = %r,
    metadata_name    = %r,
    metadata_defined = %r,
    simple           = %r,
    is_any_facet     = %r,
    optional         = %r,
    notify           = %r,
    dispatch         = %r,
    list_handler     = %r,
    next             = %s
)""" % ( self.__class__.__name__, self.name, self.metadata_name,
          self.metadata_defined, self.simple, self.is_any_facet, self.optional,
          self.notify, self.dispatch, self.list_handler,
          indent( next_repr, False ) ))

    #-- Facet Event Handlers ---------------------------------------------------

    def _handler_set ( self, handler ):
        """ Handles the 'handler' facet being changed.
        """
        if self.next is not None:
            self.next.handler = handler


    def _wrapped_handler_set ( self, wrapped_handler ):
        """ Handles the 'wrapped_handler' facet being changed.
        """
        if self.next is not None:
            self.next.wrapped_handler = wrapped_handler


    def _dispatch_set ( self, dispatch ):
        """ Handles the 'dispatch' facet being changed.
        """
        if self.next is not None:
            self.next.dispatch = dispatch


    def _priority_set ( self, priority ):
        """ Handles the 'priority' facet being changed.
        """
        if self.next is not None:
            self.next.priority = priority

    #-- Private Methods --------------------------------------------------------

    def _register_optional ( self, object, name, remove ):
        """ Register a non-existent optional facet.
        """
        return INVALID_DESTINATION


    def _register_anyfacet ( self, object, name, remove ):
        """ Registers any 'anyfacet' listener.
        """
        handler = self.wrapped_handler.notifier()
        if handler is not Undefined:
            object._on_facet_set( handler, remove   = remove,
                                           dispatch = self.dispatch,
                                           priority = self.priority )

        return ( object, name )


    def _register_simple ( self, object, name, remove ):
        """ Registers a handler for a simple facet.
        """
        next = self.next
        if next is None:
            handler = self.wrapped_handler.notifier()
            if handler is not Undefined:
                object._on_facet_set( handler, name,
                                      remove   = remove,
                                      dispatch = self.dispatch,
                                      priority = self.priority )

            return ( object, name )

        tl_handler = self.handle_simple
        if self.notify:
            if self.wrapped_handler.arg_types == ARG_VALUE:
                if self.dispatch != 'same':
                    raise FacetError(
                        ("Facet notification dispatch type '%s' is not "
                         "compatible with handler signature and extended facet "
                         "name notification style") % self.dispatch
                    )

                tl_handler = self.handle_dst
            else:
                handler = self.wrapped_handler.notifier()
                if handler is not Undefined:
                    object._on_facet_set( handler, name,
                                          remove   = remove,
                                          dispatch = self.dispatch,
                                          priority = self.priority )

        object._on_facet_set( tl_handler, name,
                              remove   = remove,
                              dispatch = 'extended',
                              priority = self.priority )

        if remove:
            return next.unregister( getattr( object, name ) )

        if not self.deferred:
            return next.register( getattr( object, name ) )

        return ( object, name )


    def _register_list ( self, object, name, remove ):
        """ Registers a handler for a list facet.
        """
        next = self.next
        if next is None:
            handler = self.wrapped_handler.notifier()
            if handler is not Undefined:
                object._on_facet_set( handler, name,
                                      remove   = remove,
                                      dispatch = self.dispatch,
                                      priority = self.priority )

                if self.list_handler:
                    object._on_facet_set( self.handle_list_items_special,
                                          name + '_items',
                                          remove   = remove,
                                          dispatch = self.dispatch,
                                          priority = self.priority )

                elif self.wrapped_handler.arg_types == ARG_NONE:
                    object._on_facet_set( handler, name + '_items',
                                          remove   = remove,
                                          dispatch = self.dispatch,
                                          priority = self.priority )

            return ( object, name )

        tl_handler       = self.handle_list
        tl_handler_items = self.handle_list_items

        if self.notify:
            if self.wrapped_handler.arg_types == ARG_VALUE:
                tl_handler = tl_handler_items = self.handle_error
            else:
                handler = self.wrapped_handler.notifier()
                if handler is not Undefined:
                    object._on_facet_set( handler, name,
                                          remove   = remove,
                                          dispatch = self.dispatch,
                                          priority = self.priority )

                    if self.list_handler:
                        object._on_facet_set( self.handle_list_items_special,
                                              name + '_items',
                                              remove   = remove,
                                              dispatch = self.dispatch,
                                              priority = self.priority )
                    elif self.wrapped_handler.arg_types == ARG_NONE:
                        object._on_facet_set( handler, name + '_items',
                                              remove   = remove,
                                              dispatch = self.dispatch,
                                              priority = self.priority )

        object._on_facet_set( tl_handler, name,
                              remove   = remove,
                              dispatch = 'extended',
                              priority = self.priority )

        object._on_facet_set( tl_handler_items, name + '_items',
                              remove   = remove,
                              dispatch = 'extended',
                              priority = self.priority )

        if remove:
            handler = next.unregister
        elif self.deferred:
            return INVALID_DESTINATION
        else:
            handler = next.register

        for obj in getattr( object, name ):
            handler( obj )

        return INVALID_DESTINATION

    # Handle 'sets' the same as 'lists':
    # Note: Currently the behavior of sets is almost identical to that of lists,
    # so we are able to share the same code for both. This includes some 'duck
    # typing' that occurs with the FacetListEvent and FacetSetEvent, that define
    # 'removed' and 'added' attributes that behave similarly enough (from the
    # point of view of this module) that they can be treated as equivalent. If
    # the behavior of sets ever diverges from that of lists, then this code may
    # need to be changed.
    _register_set = _register_list


    def _register_dict ( self, object, name, remove ):
        """ Registers a handler for a dictionary facet.
        """
        next = self.next
        if next is None:
            handler = self.wrapped_handler.notifier()
            if handler is not Undefined:
                object._on_facet_set( handler, name,
                                      remove   = remove,
                                      dispatch = self.dispatch,
                                      priority = self.priority )

                if self.wrapped_handler.arg_types == ARG_NONE:
                    object._on_facet_set( handler, name + '_items',
                                          remove   = remove,
                                          dispatch = self.dispatch,
                                          priority = self.priority )

            return ( object, name )

        tl_handler       = self.handle_dict
        tl_handler_items = self.handle_dict_items
        if self.notify:
            if self.wrapped_handler.arg_types == ARG_VALUE:
                tl_handler = tl_handler_items = self.handle_error
            else:
                handler = self.wrapped_handler.notifier()
                if handler is not Undefined:
                    object._on_facet_set( handler, name,
                                          remove   = remove,
                                          dispatch = self.dispatch,
                                          priority = self.priority )

                    if self.wrapped_handler.arg_types == ARG_NONE:
                        object._on_facet_set( handler, name + '_items',
                                              remove   = remove,
                                              dispatch = self.dispatch,
                                              priority = self.priority )

        object._on_facet_set( tl_handler, name,
                              remove   = remove,
                              dispatch = self.dispatch,
                              priority = self.priority )

        object._on_facet_set( tl_handler_items, name + '_items',
                              remove   = remove,
                              dispatch = self.dispatch,
                              priority = self.priority )

        if remove:
            handler = next.unregister
        elif self.deferred:
            return INVALID_DESTINATION
        else:
            handler = next.register

        for obj in getattr( object, name ).values():
            handler( obj )

        return INVALID_DESTINATION


    def _new_facet_added ( self, object, new_facet ):
        """ Handles new facets being added to an object being monitored.
        """
        # Set if the new facet matches our prefix and metadata:
        if new_facet.startswith( self.name ):
            facet = object.base_facet( new_facet )
            for meta_name, meta_eval in self._metadata.items():
                if not meta_eval( getattr( facet, meta_name ) ):
                    return

            # Determine whether the facet type is simple, list, set or
            # dictionary:
            type    = SIMPLE_LISTENER
            handler = facet.handler
            if handler is not None:
                type = type_map[ handler.collection_type ]

            # Add the name and type to the list of facets being registered:
            active = self.active.get( object )
            if active is not None:
                active.append( ( new_facet, type ) )

            # Set up the appropriate facet listeners on the object for the
            # new facet:
            getattr( self, type )( object, new_facet, False )

#-- ListProperty Definition ----------------------------------------------------

def _set_value ( self, name, value ):
    for item in self.items:
        setattr( item, name, value )

def _get_value ( self, name ):
    # Use the attribute on the first item. If there are no items, return None.
    if self.items:
        return getattr( self.items[0], name )

    return None

ListProperty = Property( fget = _get_value, fset = _set_value )

#-- ReadOnlyListProperty Definition --------------------------------------------

def _set_value ( self, name, value ):
    xname = '_' + name
    if getattr( self, xname, None ) is None:
        setattr( self, xname, value )
        for item in self.items:
            setattr( item, name, value )

ReadOnlyListProperty = Property( fset = _set_value )

#-------------------------------------------------------------------------------
#  'ListenerGroup' class:
#-------------------------------------------------------------------------------

class ListenerGroup ( ListenerBase ):

    #-- Facet Definitions (set by parser) --------------------------------------

    # The list of ListenerBase objects in the group:
    items = Any( [] )

    #-- Facet Definitions (not set by parser) ----------------------------------

    # A 'wrapped' version of 'handler':
    wrapped_handler = ReadOnlyListProperty

    # The wrapper class to use for this listener:
    wrapper_class = Property

    # The dispatch mechanism to use when invoking the handler:
    dispatch = ReadOnlyListProperty

    # Does the handler go at the beginning (True) or end (False) of the
    # notification handlers list?
    priority = ListProperty

    # The next level (if any) of ListenerBase object to be called when any of
    # this object's listened-to facets is changed
    next = ListProperty

    # Should changes to this item generate a notification to the handler?
    notify = ListProperty

    # Should registering listeners for items reachable from this listener item
    # be deferred until the associated facet is first read or set?
    deferred = ListProperty

    #-- Property Implementations -----------------------------------------------

    def _get_wrapper_class ( self ):
        return self.items[0].wrapper_class

    #-- 'ListenerBase' Class Method Implementations ----------------------------

    def clone ( self ):
        """ Returns a post-parser clone of the object.
        """
        return self.__class__(
            items = [ item.clone() for item in self.items ]
        )


    def extract_static ( self ):
        """ Extracts all 'static' ListenerItem objects. A static item is one
            that can be added to a class-level facet's notifier list. The
            result is a tuple of the form: ([simple ListenerItem,...],
            the_rest). The first tuple element is the (possibly empty) list of
            simple ListenerItem objects, and the second element is the
            non-simple remainder, which may be None, a ListenerItem or a
            ListenerGroup.
        """
        simple = []
        i      = 0
        items  = self.items
        while i < len( items ):
            item = items[ i ]
            if isinstance( item, ListenerItem ):
                new_simple, rest = item.extract_static()
                simple.extend( new_simple )
                if rest is None:
                    del items[ i ]

                    continue

            i += 1

        rest = self
        if len( items ) <= 1:
            rest = None
            if len( items ) == 1:
                rest = items[0]

        return ( simple, rest )


    def register_static ( self, new ):
        """ Registers new listeners for a static context.
        """
        for item in self.items:
            item.register_static( new )

        return INVALID_DESTINATION


    def register ( self, new ):
        """ Registers new listeners.
        """
        for item in self.items:
            item.register( new )

        return INVALID_DESTINATION


    def unregister ( self, old ):
        """ Unregisters any existing listeners.
        """
        for item in self.items:
            item.unregister( old )


    def __repr__ ( self, seen = None ):
        """ Returns a string representation of the object.

            Since the object graph may have cycles, we extend the basic __repr__
            API to include a set of objects we've already seen while
            constructing a string representation. When this method tries to get
            the repr of a ListenerItem or ListenerGroup, we will use the
            extended API and build up the set of seen objects. The repr of a
            seen object will just be '<cycle>'.
        """
        if seen is None:
            seen = set()

        seen.add( self )

        lines = [ '%s(items = [' % self.__class__.__name__ ]

        for item in self.items:
            lines.extend( indent( item.__repr__( seen ), True ).split( '\n' ) )
            lines[-1] += ','

        lines.append( '])' )

        return '\n'.join( lines )

#-------------------------------------------------------------------------------
#  'ListenerParser' class:
#-------------------------------------------------------------------------------

class ListenerParser ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The string being parsed
    text = Str

    # The length of the string being parsed.
    len_text = Int

    # The current parse index within the string
    index = Int

    # The next character from the string being parsed
    next = Property

    # The next Python attribute name within the string:
    name = Property

    # The next non-whitespace character
    skip_ws = Property

    # Backspaces to the last character processed
    backspace = Property

    # The ListenerBase object resulting from parsing **text**
    listener = Instance( ListenerBase )

    #-- object Method Overrides ------------------------------------------------

    def __init__ ( self, text = '', **facets ):
        """ Initializes the object.
        """
        self.text = text

        super( ListenerParser, self ).__init__( **facets )

    #-- Property Implementations -----------------------------------------------

    def _get_next ( self ):
        index       = self.index
        self.index += 1
        if index >= self.len_text:
            return EOS

        return self.text[ index ]


    def _get_backspace ( self ):
        self.index = max( 0, self.index - 1 )


    def _get_skip_ws ( self ):
        while True:
            c = self.next
            if c not in whitespace:
                return c


    def _get_name ( self ):
        match = name_pat.match( self.text, self.index - 1 )
        if match is None:
            return ''

        self.index = match.start( 2 )

        return match.group( 1 )

    #-- Private Methods --------------------------------------------------------

    def parse ( self ):
        """ Parses the text and returns the appropriate collection of
            ListenerBase objects described by the text.
        """
        # Try a simple case of 'name1.name2'. The simplest case of a single
        # Python name never triggers this parser, so we don't try to make that
        # a shortcut too. Whitespace should already have been stripped from the
        # start and end.

        # TODO: The use of regexes should be used throughout all of the parsing
        # functions to speed up all aspects of parsing.
        match = simple_pat.match( self.text )
        if match is not None:
            return ListenerItem(
                       name   = match.group( 1 ),
                       notify = match.group( 2 ) == '.',
                       next   = ListenerItem( name = match.group( 3 ) ) )

        return self.parse_group( EOS )


    def parse_group ( self, terminator = ']' ):
        """ Parses the contents of a group.
        """
        items = []

        while True:
            items.append( self.parse_item( terminator ) )

            c = self.skip_ws
            if c is terminator:
                break

            if c != ',':
                if terminator == EOS:
                    self.error( "Expected ',' or end of string" )
                else:
                    self.error( "Expected ',' or '%s'" % terminator )

        if len( items ) == 1:
            return items[ 0 ]

        return ListenerGroup( items = items )


    def parse_item ( self, terminator ):
        """ Parses a single, complete listener item or group string.
        """
        c = self.skip_ws
        if c == '[':
            result = self.parse_group()
            c      = self.skip_ws
        else:
            name = self.name
            if name != '':
                c = self.next

            result = ListenerItem( name = name )

            if c in '+-':
                result.metadata_defined = (c == '+')
                cn = self.skip_ws
                result.metadata_name = metadata = self.name
                if metadata != '':
                    cn = self.skip_ws

                result.simple       = False
                result.is_any_facet = is_any_facet = (( c == '-')   and
                                                      (name == '')  and
                                                      (metadata == ''))
                c = cn

                if is_any_facet and (not ((c == terminator) or
                    ((c == ',') and (terminator == ']')))):
                    self.error( "Expected end of name" )
            elif c == '?':
                if len( name ) == 0:
                    self.error( "Expected non-empty name preceding '?'" )

                result.optional = True
                c = self.skip_ws

        cycle = (c == '*')
        if cycle:
            c = self.skip_ws

        if c in '.:':
            result.notify = (c == '.')
            next = self.parse_item( terminator )
            if cycle:
                last = result
                while last.next is not None:
                    last = last.next

                last.next = lg = ListenerGroup( items = [ next, result ] )
                result    = lg
            else:
                result.next = next

            return result

        if c == '[':
            if (self.skip_ws == ']') and (self.skip_ws in ( terminator, ',' )):
                self.backspace
                result.list_handler = True
            else:
                self.error( "Expected '[]' at the end of an item" )
        else:
            self.backspace

        if cycle:
            result.next = result

        return result


    def error ( self, msg ):
        """ Raises a syntax error.
        """
        raise FacetError(
            "%s at column %d of '%s'" % ( msg, self.index, self.text )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _text_set ( self ):
        """ Handles the 'text' facet being changed.
        """
        self.index    = 0
        self.len_text = len( self.text )
        self.listener = self.parse()

#-- EOF ------------------------------------------------------------------------