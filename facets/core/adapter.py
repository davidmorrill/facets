"""
An extension to PyProtocols to simplify the declaration of adapters.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import weakref

from has_facets \
    import HasFacets

from facet_types \
    import Any, Bool, Expression

from facets.core.protocols.api \
    import addClassAdvisor, declareAdapter, declareImplementation, Protocol

#-------------------------------------------------------------------------------
#  'Adapter' class:
#-------------------------------------------------------------------------------

class Adapter ( HasFacets ):
    """ The base class for all facets adapters.

    In Facets, an *adapter* is a special type of class whose role is to
    transform some type of object which does not implement a specific interface,
    or set of interfaces, into one that does.

    This class is provided as a convenience. If you subclass this class, the
    only things you need to add to the subclass definition are:

        * An implements() function call declaring which interfaces the adapter
          class implements on behalf of the object is is adapting.
        * A declaration for the **adaptee** facet, usually as an Instance of
          a particular class.
        * The actual implementations of the interfaces declared in the
          implements() call. Usually the implementation code is written in
          terms of the **adaptee** facet.

    """

    #-- Facet Definitions ------------------------------------------------------

    # The object that is being adapted.
    adaptee = Any

    #-- Constructor ------------------------------------------------------------

    def __init__ ( self, adaptee ):
        """ Constructor.

            We have to declare an explicit constructor because adapters are
            created by PyProtocols itself, which knows nothing about facets.
        """
        super( Adapter, self ).__init__()

        self.adaptee = adaptee

#-------------------------------------------------------------------------------
#  'DefaultAdapterFactory' class:
#-------------------------------------------------------------------------------

class DefaultAdapterFactory ( HasFacets ):
    """ An adapter factory for producing cached or categorized adapters.
    """

    #-- 'DefaultAdapterFactory' Interface --------------------------------------

    # The adapter class that this factory creates instances of:
    klass = Any

    # Does the factory generate cached adapters?
    # If an adapter is cached then the factory will produce at most one
    # adapter per instance.
    cached = Bool( False )

    # An expression that is used to select which instances of a particular
    # type can be adapted by this factory.
    #
    # The expression is evaluated in a namespace that contains a single name
    # 'adaptee', which is bound to the object that this factory is attempting
    # to adapt (e.g. 'adaptee.is_folder').
    when = Expression

    #-- Private Interface ------------------------------------------------------

    # If this is a cached adapter factory, then this mapping will contain
    # the adapters keyed by weak references to the adapted objects:
    _adapters = Any

    #-- 'IAdapterFactory' Interface --------------------------------------------

    def __call__ ( self, object ):
        """ Creates an adapter for the specified object.

            Returns **None** if the factory cannot perform the required
            adaptation.
        """
        namespace = { 'adaptee': object }
        if eval( self.when_, namespace, namespace ):
            if self.cached:
                adapter = self._adapters.get( object )
                if adapter is None:
                    self._adapters[ object ] = adapter = self.klass( object )

                return adapter

            return self.klass( object )

        return None

    #-- Private Methods --------------------------------------------------------

    def __adapters_default ( self ):
        """ Facet initializer.
        """
        return weakref.WeakKeyDictionary()

#-------------------------------------------------------------------------------
#  'adapts' function:
#-------------------------------------------------------------------------------

def adapts ( from_, to, extra = None, factory = None, cached = False,
                        when  = '' ):
    """ A class advisor for declaring adapters.

    Parameters
    ----------
    ``from_`` : type or interface
        What the adapter adapts *from*, or a list of such types or interfaces
        (the '_' suffix is used because 'from' is a Python keyword).
    to : type or interface
        What the adapter adapts *to*, or a list of such types or interfaces.
    factory : callable
        An (optional) factory for actually creating the adapters. This is
        any callable that takes a single argument which is the object to
        be adapted. The factory should return an adapter if it can
        perform the adaptation and **None** if it cannot.

    The following arguments are ignored if *factory* is specified:

    cached : Boolean
        Should the adapters be cached? If an adapter is cached, then the
        factory will produce at most one adapter per instance.
    when : A Python expression
        Selects which instances of a particular type can be adapted by this
        factory. The expression is evaluated in a namespace that contains a
        single name *adaptee*, which is bound to the object to be adapted
        (e.g., 'adaptee.is_folder').
    """
    if extra is not None:
        adapter, from_, to = from_, to, extra
    else:
        adapter = None

    def callback ( klass ):
        """ Called when the class has been created. """

        # What the adapter adapts from:
        if type( from_ ) is not list:
            for_items = [ from_ ]
        else:
            for_items = from_

        # The things we adapt from have to be split into two lists for
        # PyProtocols, one containing Python types (i.e. classes) and one
        # containing protocols (i.e. interfaces):
        for_types     = []
        for_protocols = []
        for item in for_items:
            if isinstance( item, Protocol ):
                for_protocols.append( item )
            else:
                for_types.append( item )

        # What the adapter adapts to:
        if type( to ) is not list:
            provides = [ to ]
        else:
            provides = to

        # Tell PyProtocols that the adapter class implements the protocols that
        # it adapts to:
        declareImplementation( klass, instancesProvide = provides )

        # If a factory was specified then use it:
        if factory is not None:
            f = factory

        # If the adapter is cached or has a 'when' expression then create a
        # default factory:
        elif cached or ( when != '' ):
            f = DefaultAdapterFactory( klass  = klass,
                                       cached = cached,
                                       when   = when or 'True' )

        # Otherwise, just use the adapter class itself:
        else:
            f = klass

        # Tell PyProtocols about the factory:
        declareAdapter( f, provides, forProtocols = for_protocols,
                                     forTypes     = for_types )

        return klass

    if adapter is not None:
        callback( adapter )
    else:
        addClassAdvisor( callback )

#-- EOF ------------------------------------------------------------------------