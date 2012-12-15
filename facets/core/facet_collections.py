"""
Defines the classes used to implement the evented collection objects used by the
Facets List, Dict and Set types.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import copy

from weakref \
    import ref

from facet_base \
    import Undefined, class_of

from facet_errors \
    import FacetError

from cfacets \
    import CFacetNotification

#-------------------------------------------------------------------------------
#  'FacetListEvent' class:
#-------------------------------------------------------------------------------

class FacetListEvent ( object ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, object, name,
                         index = 0, removed = None, added = None ):
        """ Initializes the object.
        """
        self.index = index

        if removed is None:
            removed = []

        self.removed = removed

        if added is None:
            added = []

        self.added  = added
        self.notify = CFacetNotification(
            3, object, name, added, removed, index
        )

#-------------------------------------------------------------------------------
#  'FacetListObject' class:
#-------------------------------------------------------------------------------

class FacetListObject ( list ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, facet, object, name, value ):
        self.facet      = facet
        self.object     = ref( object )
        self.name       = name
        self.name_items = None
        if facet.has_items:
            self.name_items = name + '_items'

        # Do the validated 'setslice' assignment without raising an
        # 'items_changed' event:
        if facet.minlen <= len( value ) <= facet.maxlen:
            try:
                validate = facet.item_facet.handler.validate
                if validate is not None:
                    value = [ validate( object, name, val ) for val in value ]

                list.__setslice__( self, 0, 0, value )

                return

            except FacetError, excp:
                excp.set_prefix( 'Each element of the' )
                raise excp

        self.len_error( len( value ) )


    def __deepcopy__ ( self, memo ):
        id_self = id( self )
        if id_self in memo:
            return memo[ id_self ]

        memo[ id_self ] = result = self.__class__(
            self.facet, self.object(), self.name,
            [ copy.deepcopy( x, memo ) for x in self ]
        )

        return result


    def __setitem__ ( self, key, value ):
        try:
            removed = self[ key ]
        except:
            pass
        try:
            validate = self.facet.item_facet.handler.validate
            object   = self.object()
            if validate is not None:
                value = validate( object, self.name, value )

            list.__setitem__( self, key, value )
            if self.name_items is not None:
                if key < 0:
                    key = len( self ) + key

                try:
                    if removed == value:
                        return
                except:
                    # Treat incomparable values as unequal:
                    pass

                object.facet_items_event(
                    self.name_items,
                    FacetListEvent( object, self.name,
                                    key, [ removed ], [ value ] ),
                    self.facet.items_event()
                )

        except FacetError, excp:
            excp.set_prefix( 'Each element of the' )

            raise excp


    def __setslice__ ( self, i, j, values ):
        try:
            delta = len( values ) - (min( j, len( self ) ) - max( 0, i ))
        except:
            raise TypeError(
                'must assign sequence (not "%s") to slice' %
                ( values.__class__.__name__ )
            )

        self_facet = self.facet
        if self_facet.minlen <= ( len( self ) + delta ) <= self_facet.maxlen:
            try:
                object   = self.object()
                name     = self.name
                facet    = self_facet.item_facet
                removed  = self[ i: j ]
                validate = facet.handler.validate
                if validate is not None:
                    values = [ validate( object, name, value )
                               for value in values ]

                list.__setslice__( self, i, j, values )

                if self.name_items is not None:
                    if delta == 0:
                        try:
                            if removed == values:
                                return
                        except:
                            # Treat incomparable values as equal:
                            pass
                    object.facet_items_event(
                        self.name_items,
                        FacetListEvent( object, name,
                                        max( 0, i ), removed, values ),
                        self_facet.items_event()
                    )

                return

            except FacetError, excp:
                excp.set_prefix( 'Each element of the' )

                raise excp

        self.len_error( len( self ) + delta )


    def __delitem__ ( self, key ):
        if self.facet.minlen <= (len( self ) - 1):
            try:
                removed = [ self[ key ] ]
            except:
                pass

            list.__delitem__( self, key )

            if self.name_items is not None:
                if key < 0:
                    key = len( self ) + key + 1

                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetListEvent( object, self.name, key, removed ),
                    self.facet.items_event()
                )

            return

        self.len_error( len( self ) - 1 )


    def __delslice__ ( self, i, j ):
        delta = min( j, len( self ) ) - max( 0, i )
        if self.facet.minlen <= ( len( self ) - delta ):
            removed = self[ i: j ]
            list.__delslice__( self, i, j )
            if (self.name_items is not None) and (len( removed ) != 0):
                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetListEvent( object, self.name, max( 0, i ), removed ),
                    self.facet.items_event()
                )

            return

        self.len_error( len( self ) - delta )


    def append ( self, value ):
        facet = getattr( self, 'facet', None )
        if facet is None:
            list.append( self, value )

            return

        if facet.minlen <= (len( self ) + 1) <= facet.maxlen:
            try:
                validate = facet.item_facet.handler.validate
                object   = self.object()
                if validate is not None:
                    value = validate( object, self.name, value )

                list.append( self, value )

                if self.name_items is not None:
                    object.facet_items_event(
                        self.name_items,
                        FacetListEvent( object, self.name,
                                        len( self ) - 1, None, [ value ] ),
                        facet.items_event()
                    )

                return

            except FacetError, excp:
                excp.set_prefix( 'Each element of the' )

                raise excp

        self.len_error( len( self ) + 1 )


    def insert ( self, index, value ):
        facet = self.facet
        if facet.minlen <= (len( self ) + 1) <= facet.maxlen:
            try:
                validate = facet.item_facet.handler.validate
                object   = self.object()
                if validate is not None:
                    value = validate( object, self.name, value )

                list.insert( self, index, value )

                if self.name_items is not None:
                    if index < 0:
                        index = len( self ) + index - 1

                    object.facet_items_event(
                        self.name_items,
                        FacetListEvent( object, self.name,
                                        index, None, [ value ] ),
                        facet.items_event()
                    )

                return

            except FacetError, excp:
                excp.set_prefix( 'Each element of the' )

                raise excp

        self.len_error( len( self ) + 1 )


    def extend ( self, xlist ):
        facet = getattr( self, 'facet', None )
        if facet is None:
            list.extend( self, xlist )

            return

        try:
            len_xlist = len( xlist )
        except:
            raise TypeError( "list.extend() argument must be iterable" )

        if facet.minlen <= (len( self ) + len_xlist) <= facet.maxlen:
            object   = self.object()
            name     = self.name
            validate = facet.item_facet.handler.validate
            try:
                if validate is not None:
                    xlist = [ validate( object, name, value )
                              for value in xlist ]

                list.extend( self, xlist )

                if (self.name_items is not None) and (len( xlist ) != 0):
                    object.facet_items_event(
                        self.name_items,
                        FacetListEvent( object, name,
                            len( self ) - len( xlist ), None, xlist ),
                        facet.items_event()
                    )

                return

            except FacetError, excp:
                excp.set_prefix( 'The elements of the' )

                raise excp

        self.len_error( len( self ) + len( xlist ) )


    def remove ( self, value ):
        if self.facet.minlen < len( self ):
            try:
                index   = self.index( value )
                removed = [ self[ index ] ]
            except:
                pass

            list.remove( self, value )

            if self.name_items is not None:
                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetListEvent( object, self.name, index, removed ),
                    self.facet.items_event()
                )
        else:
            self.len_error( len( self ) - 1 )


    def sort ( self, cmp = None, key = None, reverse = False ):
        removed = self[:]
        list.sort( self, cmp = cmp, key = key, reverse = reverse )

        if self.name_items is not None:
            object = self.object()
            object.facet_items_event(
                self.name_items,
                FacetListEvent( object, self.name, 0, removed, self[:] ),
                self.facet.items_event()
            )


    def reverse ( self ):
        removed = self[:]
        if len( self ) > 1:
            list.reverse( self )
            if self.name_items is not None:
                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetListEvent( object, self.name, 0, removed, self[:] ),
                    self.facet.items_event()
                )


    def pop ( self, *args ):
        if self.facet.minlen < len( self ):
            if len( args ) > 0:
                index = args[0]
            else:
                index = -1

            try:
                removed = [ self[ index ] ]
            except:
                pass

            result = list.pop( self, *args )

            if self.name_items is not None:
                if index < 0:
                    index = len( self ) + index + 1

                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetListEvent( object, self.name, index, removed ),
                    self.facet.items_event()
                )

            return result

        else:
            self.len_error( len( self ) - 1 )


    def rename ( self, name ):
        facet = self.object()._facet( name, 0 )
        if facet is not None:
            self.name  = name
            self.facet = facet.handler


    def len_error ( self, len ):
        raise FacetError(
            "The '%s' facet of %s instance must be %s, but you attempted to "
            "change its length to %d element%s." %
            ( self.name, class_of( self.object() ),
              self.facet.full_info( self.object(), self.name, Undefined ),
              len, 's'[ len == 1: ] )
        )


    def __getstate__ ( self ):
        result = self.__dict__.copy()
        result[ 'object' ] = self.object()
        if 'facet' in result:
            del result[ 'facet' ]

        return result


    def __setstate__ ( self, state ):
        name   = state.pop( 'name' )
        object = state.pop( 'object' )
        if object is not None:
            self.object = ref( object )
            self.rename( name )

        self.__dict__.update( state )

#-------------------------------------------------------------------------------
#  'FacetDictEvent' class:
#-------------------------------------------------------------------------------

class FacetDictEvent ( object ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, object, name, added = None, changed = None,
                         removed = None ):
        """ Parameters
            ----------
            object : HasFacets instance
                The object that owns the dictionary
            name : string
                The name of the facet containing the dictionary
            added : dictionary
                New keys and values
            changed : dictionary
                Updated keys and their previous values
            removed : dictionary
                Old keys and values that were just removed
        """
        # Construct new empty dicts every time instead of using a default value
        # in the method argument, just in case someone gets the bright idea of
        # modifying the dict they get in-place.
        if added is None:
            added = {}

        self.added = added

        if changed is None:
            changed = {}

        self.changed = changed

        if removed is None:
            removed = {}

        self.removed = removed
        self.notify  = CFacetNotification(
            7, object, name, added, removed, changed
        )

#-------------------------------------------------------------------------------
#  'FacetDictObject' class:
#-------------------------------------------------------------------------------

class FacetDictObject ( dict ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, facet, object, name, value ):
        self.facet      = facet
        self.object     = ref( object )
        self.name       = name
        self.name_items = None
        if facet.has_items:
            self.name_items = name + '_items'

        if len( value ) > 0:
            dict.update( self, self._validate_dic( value ) )


    def __setitem__ ( self, key, value ):
        facet = getattr( self, 'facet', None )
        if facet is None:
            dict.__setitem__( self, key, value )
            return

        object = self.object()
        try:
            validate = facet.key_facet.handler.validate
            if validate is not None:
                key = validate( object, self.name, key )

        except FacetError, excp:
            excp.set_prefix( 'Each key of the' )
            raise excp

        try:
            validate = facet.value_handler.validate
            if validate is not None:
                value = validate( object, self.name, value )

            if self.name_items is not None:
                if dict.has_key( self, key ):
                    added   = None
                    old     = self[ key ]
                    changed = { key: old }
                else:
                    added   = { key: value }
                    changed = None

            dict.__setitem__( self, key, value )

            if self.name_items is not None:
                if added is None:
                    try:
                        if old == value:
                            return
                    except:
                        # Treat incomparable objects as unequal:
                        pass

                object.facet_items_event(
                    self.name_items,
                    FacetDictEvent( object, self.name, added, changed ),
                    facet.items_event()
                )

        except FacetError, excp:
            excp.set_prefix( 'Each value of the' )
            raise excp


    def __delitem__ ( self, key ):
        if self.name_items is not None:
            removed = { key: self[ key ] }

        dict.__delitem__( self, key )

        if self.name_items is not None:
            object = self.object()
            object.facet_items_event(
                self.name_items,
                FacetDictEvent( object, self.name, removed = removed ),
                self.facet.items_event()
            )


    def clear ( self ):
        if len( self ) > 0:
            if self.name_items is not None:
                removed = self.copy()

            dict.clear( self )

            if self.name_items is not None:
                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetDictEvent( object, self.name, removed = removed ),
                    self.facet.items_event()
                )


    def update ( self, dic ):
        if len( dic ) > 0:
            new_dic = self._validate_dic( dic )

            if self.name_items is not None:
                added   = {}
                changed = {}
                for key, value in new_dic.iteritems():
                    if key in self:
                        changed[ key ] = self[ key ]
                    else:
                        added[ key ] = value

                dict.update( self, new_dic )

                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetDictEvent( object, self.name, added   = added,
                                                       changed = changed ),
                    self.facet.items_event()
                )
            else:
                dict.update( self, new_dic )


    def setdefault ( self, key, value = None ):
        if self.has_key( key ):
            return self[ key ]

        self[ key ] = value
        result      = self[ key ]

        if self.name_items is not None:
            object = self.object()
            object.facet_items_event(
                self.name_items,
                FacetDictEvent( object, self.name, added = { key: result } ),
                self.facet.items_event()
            )

        return result


    def pop ( self, key, value = Undefined ):
        if (value is Undefined) or self.has_key( key ):
            result = dict.pop( self, key )

            if self.name_items is not None:
                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetDictEvent( object, self.name,
                                    removed = { key: result } ),
                    self.facet.items_event()
                )

            return result

        return value


    def popitem ( self ):
        result = dict.popitem( self )

        if self.name_items is not None:
            object = self.object()
            object.facet_items_event(
                self.name_items,
                FacetDictEvent( object, self.name,
                                removed = { result[0]: result[1] } ),
                self.facet.items_event()
            )

        return result


    def rename ( self, name ):
        facet = self.object()._facet( name, 0 )
        if facet is not None:
            self.name  = name
            self.facet = facet.handler
        else:
            logger.debug( "rename: No 'facet' in %s for '%s'" %
                          ( self.object(), name ) )


    def __getstate__ ( self ):
        result = self.__dict__.copy()
        result[ 'object' ] = self.object()
        #del result[ 'facet' ]
        if 'facet' not in result:
            logger.debug( "__getstate__: No 'facet' in %s for '%s'" %
                          ( self.object(), self.name ) )
        else:
            del result[ 'facet' ]

        return result


    def __setstate__ ( self, state ):
        name   = state.pop( 'name' )
        object = state.pop( 'object' )
        if object is not None:
            self.object = ref( object )
            self.rename( name )

        self.__dict__.update( state )

    #-- Private Methods ------------------------------------------------------------

    def _validate_dic ( self, dic ):
        name    = self.name
        new_dic = {}

        key_validate = self.facet.key_facet.handler.validate
        if key_validate is None:
            key_validate = lambda object, name, key: key

        value_validate = self.facet.value_facet.handler.validate
        if value_validate is None:
            value_validate = lambda object, name, value: value

        object = self.object()
        for key, value in dic.iteritems():
            try:
                key = key_validate( object, name, key )
            except FacetError, excp:
                excp.set_prefix( 'Each key of the' )
                raise excp

            try:
                value = value_validate( object, name, value )
            except FacetError, excp:
                excp.set_prefix( 'Each value of the' )
                raise excp

            new_dic[ key ] = value

        return new_dic

#-------------------------------------------------------------------------------
#  'FacetSetEvent' class:
#-------------------------------------------------------------------------------

class FacetSetEvent ( object ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, object, name, removed = None, added = None ):
        """ Initializes the object.
        """
        if removed is None:
            removed = set()

        self.removed = removed

        if added is None:
            added = set()

        self.added  = added
        self.notify = CFacetNotification( 5, object, name, added, removed )

#-------------------------------------------------------------------------------
#  'FacetSetObject' class:
#-------------------------------------------------------------------------------

class FacetSetObject ( set ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, facet, object, name, value ):
        self.facet      = facet
        self.object     = ref( object )
        self.name       = name
        self.name_items = None
        if facet.has_items:
            self.name_items = name + '_items'

        # Validate and assign the initial set value:
        try:
            validate = facet.item_facet.handler.validate
            if validate is not None:
                value = [ validate( object, name, val ) for val in value ]

            super( FacetSetObject, self ).__init__( value )

            return

        except FacetError, excp:
            excp.set_prefix( 'Each element of the' )
            raise excp


    def __deepcopy__ ( self, memo ):
        id_self = id( self )
        if id_self in memo:
            return memo[ id_self ]

        memo[ id_self ] = result = FacetSetObject( self.facet, self.object(),
                         self.name, [ copy.deepcopy( x, memo ) for x in self ] )

        return result


    def update ( self, value ):
        try:
            added = value.difference( self )
            if len( added ) > 0:
                object   = self.object()
                validate = self.facet.item_facet.handler.validate
                if validate is not None:
                    name  = self.name
                    added = set( [ validate( object, name, item )
                                   for item in added ] )

                set.update( self, added )

                if self.name_items is not None:
                    object.facet_items_event(
                        self.name_items,
                        FacetSetEvent( object, self.name, None, added ),
                        self.facet.items_event()
                    )

        except FacetError, excp:
            excp.set_prefix( 'Each element of the' )
            raise excp


    def intersection_update ( self, value ):
        removed = self.difference( value )
        if len( removed ) > 0:
            set.difference_update( self, removed )

            if self.name_items is not None:
                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetSetEvent( object, self.name, removed ),
                    self.facet.items_event()
                )


    def difference_update ( self, value ):
        removed = self.intersection( value )
        if len( removed ) > 0:
            set.difference_update( self, removed )

            if self.name_items is not None:
                object = self.object()
                object.facet_items_event(
                    self.name_items,
                    FacetSetEvent( object, self.name, removed ),
                    self.facet.items_event()
                )


    def symmetric_difference_update ( self, value ):
        removed = self.intersection( value )
        added   = value.difference( self )
        if ( len( removed ) > 0 ) or ( len( added ) > 0 ):
            object = self.object()
            set.difference_update( self, removed )

            if len( added ) > 0:
                validate = self.facet.item_facet.handler.validate
                if validate is not None:
                    name  = self.name
                    added = set( [ validate( object, name, item )
                                   for item in added ] )

                set.update( self, added )

            if self.name_items is not None:
                object.facet_items_event(
                    self.name_items,
                    FacetSetEvent( object, self.name, removed, added ),
                    self.facet.items_event()
                )


    def add ( self, value ):
        if value not in self:
            try:
                object   = self.object()
                validate = self.facet.item_facet.handler.validate
                if validate is not None:
                    value = validate( object, self.name, value )

                set.add( self, value )

                if self.name_items is not None:
                    object.facet_items_event(
                        self.name_items,
                        FacetSetEvent( object, self.name, None,
                                       set( [ value ] ) ),
                        self.facet.items_event()
                    )
            except FacetError, excp:
                excp.set_prefix( 'Each element of the' )
                raise excp


    def remove ( self, value ):
        set.remove( self, value )

        if self.name_items is not None:
            object = self.object()
            object.facet_items_event(
                self.name_items,
                FacetSetEvent( object, self.name, set( [ value ] ) ),
                self.facet.items_event()
            )


    def discard ( self, value ):
        if value in self:
            self.remove( value )


    def pop ( self ):
        value = set.pop( self )

        if self.name_items is not None:
            object = self.object()
            object.facet_items_event(
                self.name_items,
                FacetSetEvent( object, self.name, set( [ value ] ) ),
                self.facet.items_event()
            )

        return value


    def clear ( self ):
        removed = set( self )
        set.clear( self )

        if self.name_items is not None:
            object = self.object()
            object.facet_items_event(
                self.name_items,
                FacetSetEvent( object, self.name, removed ),
                self.facet.items_event()
            )


    def __getstate__ ( self ):
        result = self.__dict__.copy()
        result[ 'object' ] = self.object()
        if 'facet' in result:
            del result[ 'facet' ]

        return result


    def __setstate__ ( self, state ):
        name   = state.pop( 'name' )
        object = state.pop( 'object' )
        if object is not None:
            self.object = ref( object )
            self.rename( name )

        self.__dict__.update( state )

#-- EOF ------------------------------------------------------------------------
