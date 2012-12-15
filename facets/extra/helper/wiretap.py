"""
Defines the Wiretap and FBIWiretap classes used to create and manage 'wiretaps'
placed on individual facets or complete objects. A wiretap is a hook added to
an object to notify the FBI when a specified facet has changed value (and
optionally satisifes an arbitrary condition).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, SingletonHasPrivateFacets, Int, Any, Constant

from facets.extra.helper.fbi \
    import FBI

#-------------------------------------------------------------------------------
#  'Wiretap' class:
#-------------------------------------------------------------------------------

class Wiretap ( HasPrivateFacets ):

    #-- Public Facet Definitions -----------------------------------------------

    # Refrence to the FBI debugger context:
    fbi = Constant( FBI() )

    # Number of active 'entire object' wiretaps:
    count = Int

    # Set of 'facet level' wiretaps in effect:
    facets = Any( {} ) # Dict( Str, Dict )

    #-- Public Methods ---------------------------------------------------------

    def add_object ( self, object, condition ):
        """ Adds a new 'entire object' wiretap.
        """
        self.add_condition( '', condition )
        self.count += 1
        if self.count == 1:
            for facet in self.facets.keys():
                object.on_facet_set( self.facet_change, facet, remove = True )

            object.on_facet_set( self.facet_change )


    def remove_object ( self, object, condition ):
        """ Removes an 'entire object' wiretap.
        """
        self.remove_condition( '', condition )
        self.count -= 1
        if self.count == 0:
            object.on_facet_set( self.facet_change, remove = True )
            for facet in self.facets.keys():
                object.on_facet_set( self.facet_change, facet )

        return ((self.count > 0) or (len( self.facets ) > 0))


    def add_facet ( self, object, facet, condition ):
        """ Adds a new facet specific wiretap for an object.
        """
        first = self.add_condition( facet, condition )
        if (self.count == 0) and first:
            object.on_facet_set( self.facet_change, facet )


    def remove_facet ( self, object, facet, condition ):
        """ Removes a facet specific wiretap from an object.
        """
        if ((not self.remove_condition( facet, condition )) and
            (self.count == 0)):
            object.on_facet_set( self.facet_change, facet, remove = True )

        return ((self.count > 0) or (len( self.facets ) > 0))


    def add_condition ( self, facet, condition ):
        """ Adds a condition to a specified facet.
        """
        conditions = self.facets.setdefault( facet, {} )
        n          = len( conditions )
        items      = conditions.get( condition )
        if items is None:
            compiled = None
            if condition is not None:
                compiled = compile( condition, '<string>', 'eval' )
            conditions[ condition ] = items = [ compiled, 1 ]
        else:
            items[1] += 1

        return (n == 0)


    def remove_condition ( self, facet, condition ):
        """ Removes a condition from a specified facet.
        """
        conditions = self.facets.get( facet )
        if conditions is not None:
            items = conditions.get( condition )
            if items is not None:
                items[1] -= 1
                if items[1] == 0:
                    del conditions[ condition ]
                    if len( conditions ) == 0:
                        del self.facets[ facet ]
                        return False

        return True


    def facet_change ( self, object, facet, old, new ):
        """ Handles any facet of a monitored object being changed.
        """
        if (self.if_condition( '', object ) or
            self.if_condition( facet, object )):
            self.fbi.bp(
                msg = "The monitored facet '%s' has changed from %s to %s" %
                      ( facet, repr( old ), repr( new ) ),
                offset = 2
            )


    def if_condition ( myself, facet, self ):
        """ Tests if any conditions for a specified facet are true.
        """
        conditions = myself.facets.get( facet )
        if conditions is not None:
            for compiled, _ in conditions.values():
                if (compiled is None) or eval( compiled ):
                    return True

        return False

#-------------------------------------------------------------------------------
#  'FBIWiretap' class:
#-------------------------------------------------------------------------------

class FBIWiretap ( SingletonHasPrivateFacets ):

    #-- Public Facet Definitions -----------------------------------------------

    # Current objects being monitored:
    objects = Any( {} ) # Dict( Str, Instance( Wiretap ) )

    #-- Public Methods ---------------------------------------------------------

    def wiretap ( self, monitor, remove ):
        """ Adds/Removes objects from the most wanted wiretap list.
        """
        # Normalize the 'monitor' value so that it is in the form of a list:
        if ((not isinstance( monitor, SequenceTypes )) or
            ((len( monitor ) > 1) and
             (isinstance( monitor[1], basestring ) or (monitor[1] is None)))):
            monitor = [ monitor ]

        # Process each item in the monitor list. Each item should have one of
        # the following forms:
        # - object
        # - ( object, )
        # - ( object, None )
        # - ( object, None, condition )
        # - ( object, facet )
        # - ( object, facet, condition )
        # - ( object, ( facet, ..., facet ) )
        # - ( object, ( facet, ..., facet ), condition )
        for item in monitor:
            facets = condition = None
            if not isinstance( item, SequenceTypes ):
                object = item
            else:
                n = len( item )
                if n == 0:
                    continue

                object = item[0]
                if n >= 2:
                    facets = item[1]
                    if ((facets is not None) and
                        (not isinstance( facets, SequenceTypes ))):
                        facets = [ facets ]

                    if n >= 3:
                        condition = item[2]
                        if condition == '':
                            condition = None

            if facets is None:
                self.wiretap_object( object, condition, remove )
            else:
                for facet in facets:
                    self.wiretap_facet( object, facet, condition, remove )


    def wiretap_object ( self, object, condition, remove ):
        """ Sets/Removes a wiretap on an entire object.
        """
        if remove:
            wiretap = self.get_wiretap_for( object, False )
            if ((wiretap is not None) and
                (not wiretap.remove_object( object, condition ))):
                del self.objects[ id( object ) ]
        else:
            self.get_wiretap_for( object ).add_object( object, condition )


    def wiretap_facet ( self, object, facet, condition, remove ):
        """ Sets/Removes a wiretap on a particular object facet, with an
            optional condition to be on the look-out for.
        """
        if remove:
            wiretap = self.get_wiretap_for( object, False )
            if ((wiretap is not None) and
                (not wiretap.remove_facet( object, facet, condition ))):
                del self.objects[ id( object ) ]
        else:
            self.get_wiretap_for( object ).add_facet( object, facet, condition )


    def get_wiretap_for ( self, object, create = True ):
        """ Gets the Wiretap object for a specified object.
        """
        wiretap = self.objects.get( id( object ) )
        if (wiretap is None) and create:
            self.objects[ id( object ) ] = wiretap = Wiretap()

        return wiretap

#-- EOF ------------------------------------------------------------------------