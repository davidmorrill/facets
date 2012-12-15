"""
Defines the HasFacets class, along with several useful subclasses and
associated metaclasses.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import copy as copy_module
import weakref
import re
import facet_types

from cPickle \
    import Pickler, Unpickler

from types \
    import FunctionType, MethodType

from weakref \
    import WeakSet

from facets_version \
    import __version__ as FacetsVersion

from cfacets \
    import CHasFacets, CFacetMethod, _HasFacets_monitors

from facet_defs \
    import Facet, CFacet, FacetFactory, facet_factory, \
           Property, ForwardProperty, generic_facet, __newobj__, SpecialNames

from facet_types \
    import Any, Str, Instance, Event, EventFacet, Bool, Python, Disallow, This

from facet_notifiers \
    import StaticFacetSetWrapper, FacetSetWrapper, ExtendedFacetSetWrapper, \
           FastUIFacetSetWrapper, NewFacetSetWrapper, FacetsListener, ARG_NONE

from facet_handlers \
    import FacetType

from facet_base \
    import Missing, SequenceTypes, Undefined, FacetsCache, add_article, \
           is_none, not_false, not_event

from facet_db \
    import facet_db

from facet_errors \
    import FacetError

from protocols.api \
    import InterfaceClass, Protocol, addClassAdvisor, declareImplementation

#-------------------------------------------------------------------------------
#  Set CHECK_INTERFACES to one of the following values:
#
#  - 0: Does not check to see if classes implement their declared interfaces.
#  - 1: Ensures that classes implement the interfaces they say they do, and
#       logs a warning if they don't.
#  - 2: Ensures that classes implement the interfaces they say they do, and
#       raises an InterfaceError if they don't.
#-------------------------------------------------------------------------------

CHECK_INTERFACES = 0

#-------------------------------------------------------------------------------
#  Deferred definitions:
#
#  The following classes have a 'chicken and the egg' definition problem. They
#  require Facets to work, because they subclass Facets, but the Facets
#  meta-class programming support uses them, so Facets can't be subclassed
#  until they are defined.
#
#  Note: We need to look at whether the Category support could be used to
#        allow us to implement this better.
#-------------------------------------------------------------------------------

class ViewElement ( object ):
    pass

def ViewElements ( ):
    return None

def is_view_element ( object ):
    return isinstance( object, ViewElement )

def new_view_elements ( ):
    return ViewElements()

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

WrapperTypes  = ( StaticFacetSetWrapper, FacetSetWrapper )
MethodTypes   = ( MethodType,   CFacetMethod )
FunctionTypes = ( FunctionType, CFacetMethod )

# Class dictionary entries used to save facet, listener and view information and
# definitions:

BaseFacets      = '__base_facets__'
ClassFacets     = '__class_facets__'
PrefixFacets    = '__prefix_facets__'
DelegateFacets  = '__delegate_facets__'
ListenerFacets  = '__listener_facets__'
ViewFacets      = '__view_facets__'
SubclassFacets  = '__subclass_facets__'
InstanceFacets  = '__instance_facets__'
ImplementsClass = '__implements__'

# Instance dictionary entries used to save Facets related values:
AnimatedFacets = '__animated_facets__'

# The default Facets View name
DefaultFacetsView = 'facets_view'

# Facet types which cannot have default values
CantHaveDefaultValue = ( 'event', 'delegate', 'constant' )

# An empty list
EmptyList = []

# The facet types that should be copied last when doing a 'copy_facets':
DeferredCopy = ( 'delegate', 'property' )

# Quick test for normal vs extended facet name
extended_facet_pat = re.compile( r'.*[ :\+\-,\.\*\?\[\]]' )

# Generic 'Any' facet:
any_facet = Any().as_cfacet()

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# The global cache mapping listener strings to parsed ListenerBase objects:
FacetsListeners = {}

# Mapping from 'dispatch' type to notification wrapper class type:
OnFacetChangeWrappers = {
    'same':     FacetSetWrapper,
    'extended': ExtendedFacetSetWrapper,
    'new':      NewFacetSetWrapper,
    'fast_ui':  FastUIFacetSetWrapper,
    'ui':       FastUIFacetSetWrapper
    # fixme: Disabling the new ui dispatch mechanism until the problems can
    # be worked out (i.e. breaks Undo/Redo and doesn't handle list item
    # event objects correctly because of the 'new' value replacement not
    # always being the correct action to take).
    #'ui':     UIFacetSetWrapper
}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def _clone_facet ( clone, metadata = None ):
    """ Creates a clone of a specified facet.
    """
    facet = CFacet( 0 )
    facet.clone( clone )

    if clone.__dict__ is not None:
        facet.__dict__ = clone.__dict__.copy()

    if metadata is not None:
        facet.__dict__.update( metadata )

    return facet


def _get_method ( cls, method ):
    """ Gets the definition of a specified method (if any).
    """
    result = getattr( cls, method, None )
    if (result is not None) and isinstance( result, MethodTypes ):
        return result

    return None


def _is_serializable ( value ):
    """ Returns whether or not a specified value is serializable.
    """
    if isinstance( value, ( list, tuple ) ):
        for item in value:
            if not _is_serializable( item ):
                return False

        return True

    if isinstance( value, dict ):
        for name, item in value.iteritems():
            if ((not _is_serializable( name )) or
                (not _is_serializable( item ))):
                return False

        return True

    return ((not isinstance( value, HasFacets )) or
            value.has_facets_interface( ISerializable))


def _get_delegate_pattern ( name, facet ):
    """ Returns the correct 'delegate' listener pattern for a specified name and
        delegate facet.
    """
    prefix = facet._prefix
    if prefix == '':
        prefix = name
    elif prefix[-1] == '*':
        prefix = prefix[:-1] + name

    return (' %s:%s' % ( facet._delegate, prefix ))


def _check_method ( class_dict, name, func ):
    """ Checks if a function can be converted to a 'facet method' (and converts
        it if possible).
    """
    method_name  = name
    return_facet = Any

    col = name.find( '__' )
    if col >= 1:
        type_name    = name[ : col ]
        method_name  = name[ col + 2: ]

        return_facet = globals().get( type_name )
        if not isinstance( return_facet, CFacet ):
            return_facet = SpecialNames.get( type_name.lower() )
            if return_facet is None:
                return_facet = Any
                method_name  = name

    has_facets = (method_name != name)
    arg_facets = []

    defaults = func.func_defaults
    if defaults is not None:
        for facet in defaults:
            facet = _check_facet( facet )
            if isinstance( facet, CFacet ):
                has_facets = True
            else:
                facet = Any( facet ).as_cfacet()

            arg_facets.append( facet )

    if has_facets:
        code       = func.func_code
        var_names  = code.co_varnames
        arg_facets = (([ Missing ] * (code.co_argcount - len( arg_facets ))) +
                      arg_facets)
        facets     = []

        for i, facet in enumerate( arg_facets ):
            facets.append( var_names[i] )
            facets.append( facet )

        del class_dict[ name ]
        class_dict[ method_name ] = CFacetMethod( method_name, func,
                                          tuple( [ return_facet ] + facets ) )


def _check_facet ( facet ):
    """ Returns either the original value or a valid CFacet if the value can be
        converted to a CFacet.
    """
    if isinstance( facet, CFacet ):
        return facet

    if isinstance( facet, FacetFactory ):
        return facet_factory( facet )

    if isinstance( facet, type ) and issubclass( facet, FacetType ):
        facet = facet()

    if isinstance( facet, FacetType ):
        return facet.as_cfacet()

    return facet


def _non_none ( *args ):
    """ Returns a list containing all non-None arguments.
    """
    return [ arg for arg in args if arg is not None ]


def _listener_for ( name ):
    """ Returns an instance of ListenerBase derived from *name*. The result is
        actually a clone of a globally cached result for *name* to save having
        to parse the same *name* over and over again (on early testing, the
        cache hit ratio was > 98%).
    """
    global FacetsListeners

    from facets_listener import ListenerParser

    listener = FacetsListeners.get( name )
    if listener is None:
        FacetsListeners[ name ] = listener = ListenerParser( name ).listener

    return listener.clone()


def _facet_for ( facet ):
    """ Returns the facet corresponding to a specified value.
    """
    facet = _check_facet( facet )
    if isinstance( facet, CFacet ):
        return facet

    return Facet( facet )


def _mapped_facet_for ( facet ):
    """ Returns the 'mapped facet' definition for a mapped facet.
    """
    default_value = facet.default_value()[ 1 ]
    try:
        default_value = facet.handler.mapped_value( default_value )
    except:
        pass

    return Any( default_value, is_base  = False, transient = True,
                               editable = False ).as_cfacet()


def _add_notifiers ( notifiers, handlers ):
    """ Adds a list of handlers to a specified notifiers list.
    """
    for handler in handlers:
        if not isinstance( handler, WrapperTypes ):
            handler = StaticFacetSetWrapper( handler )

        notifiers.append( handler )


def _add_event_handlers ( facet, cls, handlers ):
    """ Adds any specified event handlers defined for a facet by a class.
    """
    events = facet.event
    if events is not None:
        if isinstance( events, basestring ):
            events = [ event.strip() for event in events.split( ',' ) ]

        for event in events:
            handlers.extend(
                _non_none( _get_method( cls, '_%s_set' % event ) )
            )


def _property_method ( class_dict, name ):
    """ Returns the method associated with a particular class property
        getter/setter.
    """
    return class_dict.get( name )


def facet_method ( func, return_type, **arg_types ):
    """ Factory function for creating type-checked methods.

    Parameters
    ----------
    func : function
        The method to be type-checked
    return_type : facet or value that can be converted to a facet using Facet()
        The return type of the method
    arg_types : zero or more '*keyword* = *facet*' pairs
        Argument names and types of parameters of the type-checked method. The
        *facet* portion of each pair must be a facet or a value that can be
        converted to a facet using Facet().
    """
    # Make the sure the first argument is a function:
    if type( func ) is not FunctionType:
        if type( return_type ) is not FunctionType:
            raise TypeError( 'First or second argument must be a function.' )
        else:
            func, return_type = return_type, func

    # Make sure the return type is a facet (if not, coerce it to one):
    return_type = _facet_for( return_type )

    # Make up the list of arguments defined by the function we are wrapping:
    code       = func.func_code
    arg_count  = code.co_argcount
    var_names  = code.co_varnames[ : arg_count ]
    defaults   = func.func_defaults or ()
    defaults   = ( Missing, ) * (arg_count - len( defaults )) + defaults
    arg_facets = []
    for i, name in enumerate( var_names ):
        try:
            facet = arg_types[ name ]
            del arg_types[ name ]
        except:
            # fixme: Should this be a hard error (i.e. missing parameter type?)
            facet = Any

        arg_facets.append( name )
        arg_facets.append( Facet( defaults[i], _facet_for( facet ) ) )

    # Make sure there are no unaccounted for type parameters left over:
    if len( arg_types ) > 0:
        names = arg_types.keys()
        if len( names ) == 1:
            raise FacetError(
                "The '%s' keyword defines a type for an argument which '%s' "
                "does not have." % ( names[0], func.func_name )
            )
        else:
            names.sort()
            raise FacetError(
                ("The %s keywords define types for arguments which '%s' does "
                 "not have.") %
                ( ', '.join( [ "'%s'" % name for name in names ] ),
                  func.func_name )
            )

    # Otherwise, return a method wrapper for the function:
    return CFacetMethod( func.func_name, func,
                                         tuple( [ return_type ] + arg_facets ) )


def _add_assignment_advisor ( callback, depth = 2 ):
    """ Defines a method 'decorator' for adding type checking to methods.
    """
    frame      = sys._getframe( depth )
    old_trace  = [ frame.f_trace ]
    old_locals = frame.f_locals.copy()

    def tracer ( frm, event, arg ):

        if event == 'call':
            if old_trace[0]:
                return old_trace[0]( frm, event, arg )

            return None
        try:
            if frm is frame and event != 'exception':
                for k, v in frm.f_locals.items():
                    if k not in old_locals:
                        del frm.f_locals[ k ]

                        break
                    elif old_locals[ k ] is not v:
                        frm.f_locals[ k ] = old_locals[ k ]

                        break
                else:
                    return tracer

                callback( frm, k, v )

        finally:
            if old_trace[0]:
                old_trace[0] = old_trace[0]( frm, event, arg )

        frm.f_trace = old_trace[0]
        sys.settrace( old_trace[0] )

        return old_trace[0]

    frame.f_trace = tracer
    sys.settrace( tracer )


def method ( return_type = Any, *arg_types, **kwarg_types ):
    """ Declares that the method defined immediately following a call to this
        function is type-checked.

        Parameters
        ----------
        return_type : type
            The type returned by the type-checked method. Must be either a facet
            or a value that can be converted to a facet using the Facet()
            function. The default of Any means that the return value is not
            type-checked.
        arg_types : zero or more types
            The types of positional parameters of the type-checked method. Each
            value must either a facet or a value that can be converted to a
            facet using the Facet()  function.
        kwarg_types : zero or more *keyword* = *type* pairs
            Type names and types of keyword parameters of the type-checked
            method. The *type* portion of the parameter must be either a facet
            or a value that can be converted to a facet using the Facet()
            function.

        Description
        -----------
        Whenever the type-checked method is called, the method() function
        ensures that each parameter passed to the method of the type specified
        by *arg_types* and *kwarg_types*, and that the return value is of the
        type specified by *return_type*. It is an error to specify both
        positional and keyword definitions for the same method parameter. If a
        parameter defined by the type-checked method is not referenced in the
        method() call, the parameter is not type-checked (i.e., its type is
        implicitly set to Any). If the call to method() signature contains an
        *arg_types* or *kwarg_types* parameter that does not correspond to a
        parameter in the type-checked method definition, a FacetError exception
        is raised.
    """
    # The following is a 'hack' to get around what seems to be a Python bug
    # that does not pass 'return_type' and 'arg_types' through to the scope of
    # 'callback' below:
    kwarg_types[''] = ( return_type, arg_types )

    def callback ( frame, method_name, func ):

        # This undoes the work of the 'hack' described above:
        return_type, arg_types = kwarg_types['']
        del kwarg_types['']

        # Add a 'fake' positional argument as a place holder for 'self':
        arg_types = ( Any, ) + arg_types

        # Make the sure the first argument is a function:
        if type( func ) is not FunctionType:
            raise TypeError(
                "'method' must immediately precede a method definition."
            )

        # Make sure the return type is a facet (if not, coerce it to one):
        return_type = _facet_for( return_type )

        # Make up the list of arguments defined by the function we are wrapping:
        code       = func.func_code
        func_name  = func.func_name
        arg_count  = code.co_argcount
        var_names  = code.co_varnames[ : arg_count ]
        defaults   = func.func_defaults or ()
        defaults   = ( Missing, ) * (arg_count - len( defaults )) + defaults
        arg_facets = []
        n          = len( arg_types )
        if n > len( var_names ):
            raise FacetError(
                ('Too many positional argument types specified in the method '
                 'signature for %s') % func_name
            )

        for i, name in enumerate( var_names ):
            if (i > 0) and (i < n):
                if name in kwarg_types:
                    raise FacetError(
                        "The '%s' argument is defined by both a positional and "
                        "keyword argument in the method signature for %s" %
                        ( name, func_name )
                    )

                facet = arg_types[ i ]
            else:
                try:
                    facet = kwarg_types[ name ]
                    del kwarg_types[ name ]
                except:
                    # fixme: Should this be an error (missing parameter type?)
                    facet = Any

            arg_facets.append( name )
            arg_facets.append( Facet( defaults[i], _facet_for( facet ) ) )

        # Make sure there are no unaccounted for type parameters left over:
        if len( kwarg_types ) > 0:
            names = kwarg_types.keys()
            if len( names ) == 1:
                raise FacetError(
                    ("The '%s' method signature keyword defines a type for an "
                     "argument which '%s' does not have.") %
                    ( names[0], func_name )
                )
            else:
                names.sort()

                raise FacetError(
                    ("The %s method signature keywords define types for "
                     "arguments which '%s' does not have.") %
                    ( ', '.join( [ "'%s'" % name for name in names ] ),
                      func_name )
                )

        # Otherwise, return a method wrapper for the function:
        frame.f_locals[ method_name ] = CFacetMethod(
            func_name, func, tuple( [ return_type ] + arg_facets )
        )

    _add_assignment_advisor( callback )

#-------------------------------------------------------------------------------
#  '_SimpleTest' class:
#-------------------------------------------------------------------------------

class _SimpleTest:
    def __init__ ( self, value ): self.value = value
    def __call__ ( self, test  ): return test == self.value

#-------------------------------------------------------------------------------
#  '__NoInterface__' class:
#-------------------------------------------------------------------------------

class __NoInterface__ ( object ):
    """ An uninstantiated class used to tag facet subclasses which do not
        implement any interfaces.
    """
    pass

#-------------------------------------------------------------------------------
#  'DelegateNotifier' class:
#-------------------------------------------------------------------------------

class DelegateNotifier ( object ):
    """ Passes through delegation notifications to the specified target object
        using the target's designated facet name.
    """

    def __init__ ( self, target, name ):
        self.target = weakref.ref( target )
        self.name   = name


    def notify ( self, object, name, old, new ):
        self.target().facet_property_set( self.name, old, new )

#-------------------------------------------------------------------------------
#  'MetaHasFacets' class:
#-------------------------------------------------------------------------------

# This really should be 'HasFacets', but it's not defined yet:
_HasFacets = None

class MetaHasFacets ( type ):
    """ The metaclass used to process classes derived from HasFacets.
    """

    #-- Class Variables --------------------------------------------------------

    # All registered class creation listeners. A dictionary of the form:
    # { Str class_name: Callable listener }
    _listeners = {}

    #-- Public Methods ---------------------------------------------------------

    def __new__ ( cls, class_name, bases, class_dict ):
        mhfo = MetaHasFacetsObject( cls, class_name, bases, class_dict, False )

        # Finish building the class using the updated class dictionary:
        klass = type.__new__( cls, class_name, bases, class_dict )

        if _HasFacets is not None:
            for base in bases:
                if issubclass( base, _HasFacets ):
                    getattr( base, SubclassFacets ).add( klass )

        setattr( klass, SubclassFacets, WeakSet() )

        # Fix up all self referential facets to refer to this class:
        for facet in mhfo.self_referential:
            facet.set_validate( ( 11, klass ) )

        # Call all listeners that registered for this specific class:
        name = '%s.%s' % ( klass.__module__, klass.__name__ )
        for listener in MetaHasFacets._listeners.get( name, [] ):
            listener( klass )

        # Call all listeners that registered for ANY class:
        for listener in MetaHasFacets._listeners.get( '', [] ):
            listener( klass )

        return klass


    @classmethod
    def add_listener ( cls, listener, class_name = '' ):
        """ Adds a class creation listener.

            If the class name is the empty string then the listener will be
            called when *any* class is created.
        """
        MetaHasFacets._listeners.setdefault( class_name, [] ).append( listener )


    @classmethod
    def remove_listener ( cls, listener, class_name = '' ):
        """ Removes a class creation listener.
        """
        MetaHasFacets._listeners[ class_name ].remove( listener )

#-------------------------------------------------------------------------------
#  'MetaInterface' class:
#-------------------------------------------------------------------------------

class MetaInterface ( MetaHasFacets, InterfaceClass ):
    """ Meta class for interfaces.

        This combines facet and PyProtocols functionality.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, __name__, __bases__, __dict__ ):
        """ This method is copied over from PyProtocols 'AbstractBaseMets'.

            It is needed here to make sure that we don't add any implied
            protocols for *our* 'Interface' class (since PyProtocols doesn't
            know about it.
        """

        type.__init__( self, __name__, __bases__, __dict__ )
        Protocol.__init__( self )

        for base in __bases__:
            if isinstance( base, InterfaceClass ) and (base is not Interface):
                self.addImpliedProtocol( base )


    def __call__ ( self, *args, **kw ):
        """ This method is copied over from the PyProtocols 'InterfaceClass'
            (and cleaned up a little). It is needed here because:

            a) the 'InterfaceClass' is no longer the first class in the
               hierarchy.
            b) the reference to 'Interface' now needs to reference *our*
               Interface.
        """
        if self.__init__ is Interface.__init__:
            return Protocol.__call__( self, *args, **kw )

        return type.__call__( self, *args, **kw )


    def getBases ( self ):
        """ Overridden to make sure we don't return our 'Interface' class. """

        return [ base for base in self.__bases__
                 if isinstance( base, InterfaceClass ) and
                    (base is not Interface) ]

#-------------------------------------------------------------------------------
#  'MetaHasFacetsObject' class:
#-------------------------------------------------------------------------------

class MetaHasFacetsObject ( object ):
    """ Performs all of the meta-class processing needed to convert any
        subclass of HasFacets into a well-formed facets class.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, cls, class_name, bases, class_dict, is_category ):
        """ Processes all of the facets related data in the class dictionary.
        """
        # Create the various class dictionaries, lists and objects needed to
        # hold facet and view information and definitions:
        self.class_name            = class_name
        self.bases                 = bases
        self.class_dict            = class_dict
        self.is_category           = is_category
        self.base_facets           = {}
        self.class_facets          = {}
        self.prefix_facets         = {}
        self.prefix_list           = []
        self.pre_static_decorators = {}
        self.static_decorators     = {}
        self.view_elements         = new_view_elements()
        self.self_referential      = []
        self.fired_events          = set()
        self.event_handlers        = {}
        self.implements            = []

        # Initialize information about HasFacets base classes for this class:
        self._process_base_info()

        # Move all facet definitions from the class dictionary to the
        # appropriate facet class dictionaries:
        self._process_facet_definitions()

        # Process all HasFacets base classes:
        self._process_base_classes()

        # Process the prefix facet information:
        self._process_prefix_facets()

        # Create the list of all possible 'Instance'/'List(Instance)' handlers:
        self._process_instance_handlers()

        # Process all of the static decorator information:
        self._process_static_decorators()

        # Process all 'anyfacet' related information:
        self._process_anyfacets()

        # Process any implicitly fired event definitions:
        self._process_events()

        # Process all of the static and default value handlers:
        self._process_static_handlers()

        # Issue any possibly useful diagnostic messages:
        self._process_warnings()

        # Add the facets meta-data to the class:
        self.add_facets_meta_data(
            bases, class_dict, self.base_facets, self.class_facets,
            self.instance_facets, self.prefix_facets, self.listeners,
            self.view_elements, self._process_implements_class()
        )


    def add_facets_meta_data ( self, bases, class_dict, base_facets,
                               class_facets,  instance_facets, prefix_facets,
                               listeners, view_elements, implements_class ):
        """ Adds the Facets metadata to the class dictionary.
        """
        class_dict[ BaseFacets      ] = base_facets
        class_dict[ ClassFacets     ] = class_facets
        class_dict[ InstanceFacets  ] = instance_facets
        class_dict[ PrefixFacets    ] = prefix_facets
        class_dict[ ListenerFacets  ] = listeners
        class_dict[ ViewFacets      ] = view_elements
        class_dict[ ImplementsClass ] = implements_class

    #-- Private Methods --------------------------------------------------------

    def _process_base_info ( self ):
        """ Initializes information about the HasFacets base classes for this
            class.
        """
        # Create a list of just those base classes that derive from HasFacets:
        self.hasfacets_bases = hfb = [
            base for base in self.bases
            if base.__dict__.get( ClassFacets ) is not None
        ]

        # Create a dictionary of all inherited facets:
        self.inherited_class_facets = icf = {}
        for i in xrange( len( hfb ) - 1, -1, -1 ):
            icf.update( hfb[ i ].__dict__.get( ClassFacets ) )


    def _process_facet_definitions ( self ):
        """ Move all facet definitions from the class dictionary to the
            appropriate facet class dictionaries.
        """
        class_dict             = self.class_dict
        class_facets           = self.class_facets
        base_facets            = self.base_facets
        self_referential       = self.self_referential
        class_name             = self.class_name
        prefix_list            = self.prefix_list
        prefix_facets          = self.prefix_facets
        inherited_class_facets = self.inherited_class_facets

        for name, value in class_dict.items():
            value = _check_facet( value )
            rc    = isinstance( value, CFacet )

            if (not rc) and isinstance( value, ForwardProperty ):
                value = self._convert_property( name, value )
                rc    = True

            if rc:
                del class_dict[ name ]
                value_type = value.type
                if value_type == 'delegate':
                    self._check_delegate( name, value )

                if name[-1:] != '_':
                    base_facets[ name ] = class_facets[ name ] = value
                    events              = self._events_for( value )
                    if value_type == 'facet':
                        handler = value.handler
                        if handler is not None:
                            self._check_handler( name, value, handler, events )
                            if isinstance( handler, This ):
                                handler.info_text = (add_article( class_name ) +
                                                     ' instance')
                                self_referential.append( value )
                    elif value_type == 'event':
                        self._check_event( name, value )
                    elif value_type == 'property':
                        self._check_property( name, value )
                else:
                    name = name[:-1]
                    prefix_list.append( name )
                    prefix_facets[ name ] = value
            elif isinstance( value, FunctionType ):
                self._check_method( name, value )
            elif isinstance( value, property ):
                class_facets[ name ] = generic_facet
            elif is_view_element( value ):
                self._check_view_element( name, value )
            else:
                facet = inherited_class_facets.get( name )
                if facet is not None:
                    self._check_inherited_facet( name, facet, value )


    def _process_base_classes ( self ):
        """ Processes all HasFacets base classes.
        """
        class_dict          = self.class_dict
        class_facets        = self.class_facets
        base_facets         = self.base_facets
        prefix_list         = self.prefix_list
        prefix_facets       = self.prefix_facets
        view_elements       = self.view_elements
        is_category         = self.is_category
        implements          = self.implements
        migrated_properties = {}

        for base in self.hasfacets_bases:
            base_dict = base.__dict__

            # List the subclasses that implement interfaces:
            if ((not is_category) and
                (base_dict.get( ImplementsClass ) is not __NoInterface__)):
                implements.append( base )

            # Merge base facets:
            for name, value in base_dict.get( BaseFacets ).iteritems():
                if name not in base_facets:
                    property_info = value.property()
                    if property_info is not None:
                        key = id( value )
                        migrated_properties[ key ] = value = \
                            self._migrate_property( name, value, property_info )

                    base_facets[ name ] = value

                elif is_category:
                    raise FacetError(
                        "Cannot override '%s' facet definition in a category" %
                        name
                    )

            # Merge class facets:
            # Note: The check for the name, stripped of blanks, not being in the
            # class dictionary checks for the existence of a method override
            # which in a base class had an @on_facet_set decorator:
            for name, value in base_dict.get( ClassFacets ).iteritems():
                if ((name not in class_facets) and
                    (name.strip() not in class_dict)):
                    property_info = value.property()
                    if property_info is not None:
                        new_value = migrated_properties.get( id( value ) )
                        if new_value is not None:
                            value = new_value
                        else:
                            value = self._migrate_property( name, value,
                                                            property_info )

                    class_facets[ name ] = value

                elif is_category:
                    raise FacetError(
                        "Cannot override '%s' facet definition in a category" %
                        name
                    )

            # Merge prefix facets:
            base_prefix_facets = base_dict.get( PrefixFacets )
            for name in base_prefix_facets['*']:
                if name not in prefix_list:
                    prefix_list.append( name )
                    prefix_facets[ name ] = base_prefix_facets[ name ]
                elif is_category:
                    raise FacetError(
                        "Cannot override '%s_' facet definition in a category" %
                        name
                    )

            # If the base class has a 'ViewElements' object defined, add it to
            # the 'parents' list of this class's 'ViewElements':
            parent_view_elements = base_dict.get( ViewFacets )
            if parent_view_elements is not None:
                view_elements.parents.append( parent_view_elements )


    def _process_prefix_facets ( self ):
        """ Process all of the prefix facet related information.
        """
        prefix_facets = self.prefix_facets
        prefix_list   = self.prefix_list

        # Make sure there is a definition for 'undefined' facets:
        if (prefix_facets.get( '' ) is None) and (not self.is_category):
            prefix_list.append( '' )
            prefix_facets[''] = Python().as_cfacet()

        # Save a link to the prefix_list:
        prefix_facets['*'] = prefix_list

        # Make sure the facet prefixes are sorted longest to shortest
        # so that we can easily bind dynamic facets to the longest matching
        # prefix:
        prefix_list.sort( lambda x, y: len( y ) - len( x ) )


    def _process_instance_handlers ( self ):
        """ Returns a dictionary of potential 'Instance' or 'List(Instance)'
            handlers.
        """
        # fixme: I think this is for a feature that can be removed from Facets.
        # Create the results dictionary:
        self.instance_facets = instance_facets = {}

        # Merge all of the base class information into the result:
        for base in self.hasfacets_bases:
            for name, base_arg_lists in \
                base.__dict__.get( InstanceFacets ).iteritems():
                print '_process_instance_handlers:', name
                arg_lists = instance_facets.get( name )
                if arg_lists is None:
                    instance_facets[ name ] = base_arg_lists[:]
                else:
                    for arg_list in base_arg_lists:
                        if arg_list not in arg_lists:
                            arg_lists.append( arg_list )


    def _process_events ( self ):
        """ Checks to see if any implicitly fired events do not have an explicit
            event defined for them, and if not, adds one now.
        """
        class_facets = self.class_facets

        for name in self.fired_events:
            if name not in class_facets:
                class_facets[ name ] = EventFacet


    def _process_static_decorators ( self ):
        """ Processes all class facets, adding all static and dynamic notifiers
            to their correct targets (via the 'static_decorators',
            'pre_static_decorators' dictionaries and 'listeners' lists).
        """
        pre_static_decorators = self.pre_static_decorators
        static_decorators     = self.static_decorators
        post_listeners        = []
        listeners             = []

        for name, facet in self.class_facets.iteritems():
            if facet._pre_static is not None:
                self._merge_static( pre_static_decorators, facet._pre_static )

            if facet._static is not None:
                self._merge_static( static_decorators, facet._static )

            if facet._dynamic is not None:
                kind, listener = facet._dynamic
                item           = ( kind, name.strip(), listener )
                if (kind == 'method') and listener._post_init:
                    post_listeners.append( item )
                else:
                    listeners.append( item )

        self.listeners = ( listeners, post_listeners )

        # Create additional handlers for any collection facets that have
        # suitable handlers:
        self._process_items_for( pre_static_decorators )
        self._process_items_for( static_decorators )


    def _process_anyfacets ( self ):
        """ If there is an 'anyfacet_...' event handler, wrap it so that it can
            be attached to all facets in the class.
        """
        self.pre_anyfacets = self.pre_static_decorators.pop( '', EmptyList )[:]
        self.anyfacets = (self.static_decorators.pop( '', EmptyList )[:] +
                          _non_none( self._get_def( '_anyfacet_set' ) ))

        if len( self.anyfacets ) > 0:
            # Save it in the prefix facets dictionary so that any dynamically
            # created facets (e.g. 'prefix facets') can re-use it:
            self.prefix_facets['@'] = self.pre_anyfacets + self.anyfacets


    def _process_items_for ( self, decorators ):
        """ For each facet and handler referenced by the *decorators* dictionary
            { facet_name: [ static_handlers ] }, add a corresponding
            static_handler entry for the facet_name + '_items' facet if
            facet_name is a collection and static_handler requires no arguments.
        """
        class_facets = self.class_facets

        for name, handlers in decorators.items():
            facet = class_facets.get( name )
            if facet is not None:
                handler = facet.handler
                if (handler is not None) and handler.has_items:
                    name_items     = name + '_items'
                    items_handlers = decorators.get( name_items )
                    for handler in handlers:
                        if handler.arg_types == ARG_NONE:
                            if items_handlers is None:
                                decorators[ name_items ] = item_handlers = []

                            item_handlers.append( handler )


    def _process_static_handlers ( self ):
        """ Makes one final pass over the class facets dictionary, making sure
            that all static facet notification handlers are attached to a
            'cloned' copy of the original facet.
        """
        class_name            = self.class_name
        class_dict            = self.class_dict
        class_facets          = self.class_facets
        bases                 = self.bases
        get_def               = self._get_def
        event_handlers        = self.event_handlers
        instance_facets       = self.instance_facets
        pre_anyfacets         = self.pre_anyfacets
        anyfacets             = self.anyfacets
        pre_static_decorators = self.pre_static_decorators
        static_decorators     = self.static_decorators
        cloned                = set()

        for name, facet in class_facets.iteritems():
            handlers = (
                pre_anyfacets                                +
                pre_static_decorators.pop( name, EmptyList ) +
                anyfacets                                    +
                _non_none( get_def( '_%s_set' % name ) )     +
                static_decorators.pop( name, EmptyList ))

            # Check for an 'Instance' or 'List(Instance)' facet with defined
            # handlers:
            instance_handler = facet.instance_handler
            if ((instance_handler is not None) and
                (name in instance_facets) or
                ((instance_handler == '_list_items_changed_handler') and
                 (name[-6:] == '_items') and
                 (name[:-6] in instance_facets))):
                handlers.append( getattr( HasFacets, instance_handler ) )

            # If the facet implicitly fires events, add the handlers for that:
            events = facet.event
            if isinstance( events, SequenceTypes ):
                for event in events:
                    handler = event_handlers.get( event )
                    if handler is None:
                        event_handlers[ event ] = handler = \
                            self._event_setter_for( event )

                    handlers.append( handler )

            default = get_def( '_%s_default' % name, skip_bases = True )
            if (len( handlers ) > 0) or (default is not None):
                if name not in cloned:
                    cloned.add( name )
                    class_facets[ name ] = facet = _clone_facet( facet )

                if len( handlers ) > 0:
                    _add_notifiers( facet._notifiers( 1 ), handlers )

                if default is not None:
                    facet.default_value( 8, default )


    def _process_warnings ( self ):
        """ Processes any diagnostic messages about the class being created.
        """
        if len( self.static_decorators ) > 0:
            print ('Warning: The %s class references the undefined facets: %s' %
                  ( self.class_name,
                    ', '.join( self.static_decorators.keys() ) ))


    def _process_implements_class ( self ):
        """ Defines and returns a class that is a subclass of all of the
            interfaces that the HasFacets base classes implement (we won't know
            which interfaces this class explicitly implements until the
            'implements' function callback runs, which is after we exit).
        """
        n = len( self.implements )
        if n == 0:
            return __NoInterface__

        if n == 1:
            return self.implements[0].__implements__

        return _create_implements_class(
            self.class_name, EmptyList, self.implements
        )


    def _convert_property ( self, name, facet ):
        """ Converts a ForwardProperty pseudo-facet *facet* into an actual
            Property facet and returns it.
        """
        class_dict = self.class_dict
        getter     = _property_method( class_dict, '_get_' + name )
        setter     = _property_method( class_dict, '_set_' + name )
        if (setter is None) and (getter is not None):
            if getattr( getter, 'settable', False ):
                setter = HasFacets._set_facets_cache
            elif getattr( getter, 'flushable', False ):
                setter = HasFacets._flush_facets_cache

        validate = _property_method( class_dict, '_validate_' + name )
        if validate is None:
            validate = facet.validate

        return Property( getter, setter, validate, True, facet.handler,
                         **facet.metadata )


    def _migrate_property ( self, name, facet, property_info ):
        """ Migrates an existing property facet to the class being defined
            (allowing  for method overrides).
        """
        class_dict = self.class_dict
        get        = _property_method( class_dict, '_get_'      + name )
        set        = _property_method( class_dict, '_set_'      + name )
        val        = _property_method( class_dict, '_validate_' + name )
        if ((get is not None) or (set is not None) or (val is not None)):
            old_get, old_set, old_val = property_info
            metadata = facet.__dict__.copy()
            if get is not None:
                depends_on = getattr( get, 'depends_on', None )
                if depends_on is not None:
                    metadata[ 'depends_on' ] = depends_on

                if ((metadata.get( 'depends_on' ) is not None) and
                     getattr( get, 'cached_property', False )):
                    metadata[ 'cached' ] = True

            facet = Property( get or old_get, set or old_set, val or old_val,
                              True, **metadata )
            self._check_property( name, facet )

        return facet


    def _get_def ( self, method, skip_bases = False ):
        if method[:2] == '__':
            method = '_%s%s' % ( self.class_name, method )

        result = self.class_dict.get( method )
        if ((result is not None)                and
            isinstance( result, FunctionTypes ) and
            (getattr( result, 'on_facet_set', None ) is None) ):
            return result

        if skip_bases:
            return None

        for base in self.bases:
            result = getattr( base, method, None )
            if ((result is not None)              and
                isinstance( result, MethodTypes ) and
                (getattr( result.im_func, 'on_facet_set', None ) is None)):
                return result

        return None


    def _events_for ( self, facet ):
        """ Maintains a list of all implicitly fired events, indicated by a
            facet having 'event' metadata which specifies which implicit events
            should be fired. Returns the list of implicit events being fired (or
            None).
        """
        events = facet.event
        if isinstance( events, basestring ):
            facet.event = events = [ _.strip() for _ in events.split( ',' ) ]

        if isinstance( events, SequenceTypes ):
            self.fired_events.update( events )

        return events


    def _check_inherited_facet ( self, name, facet, value ):
        """ Processes a default value override of an inherited facet.
        """
        if facet.type in CantHaveDefaultValue:
            raise FacetError(
                ("Cannot specify a default value for the %s facet '%s'. You "
                 "must override the the facet definition instead.") %
                ( facet.type, name )
            )

        self.class_facets[ name ] = new_facet = facet( value )
        del self.class_dict[ name ]
        handler = new_facet.handler
        if (handler is not None) and handler.is_mapped:
            self.class_facets[ name + '_' ] = _mapped_facet_for( new_facet )


    def _check_view_element ( self, name, value ):
        """ Processes a view element.
        """
        # Add the view element to the class's 'ViewElements' if it is not
        # already defined (duplicate definitions are errors):
        view_elements = self.view_elements
        if name in view_elements.content:
            raise FacetError(
                "Duplicate definition for view element '%s'" % name
            )

        view_elements.content[ name ] = value

        # Replace all substitutable view sub elements with 'Include' objects,
        # and add the sustituted items to the 'ViewElements':
        value.replace_include( view_elements )

        # Remove the view element from the class definition:
        del self.class_dict[ name ]


    def _check_handler ( self, name, value, handler, events ):
        """ Checks a normal facet's handler for any special processing that
            needs to be performed.
        """
        if handler.has_items:
            items_facet = _clone_facet( handler.items_event(), value.__dict__ )
            items_facet.event = events

            if items_facet.instance_handler == '_list_changed_handler':
                items_facet.instance_handler = '_list_items_changed_handler'

            self.class_facets[ name + '_items' ] = items_facet

        if handler.is_mapped:
            self.class_facets[ name + '_' ] = _mapped_facet_for( value )


    def _check_delegate ( self, name, facet ):
        """ Checks a 'delegate' facet for any additional processing that needs
            to be performed.
        """
        if facet._listenable is not False:
            facet._dynamic = (
                'delegate',
                _listener_for( _get_delegate_pattern( name, facet ) )
            )


    def _check_event ( self, name, facet ):
        """ Checks an 'event' facet for 'on_facet_set' information and processes
            it if it exists.
        """
        on_facet_set = facet.on_facet_set
        if isinstance( on_facet_set, basestring ):
            simple, rest = _listener_for( on_facet_set ).extract_static()
            if len( simple ) > 0:
                self.event_handlers[ name ] = handler = \
                    self._event_setter_for( name )
                facet._static = static = {}
                for item in simple:
                    static[ item.name ] = handler

            if rest is not None:
                facet._dynamic = ( 'event', rest )


    def _check_method ( self, name, method ):
        """ Checks a method definition for any additional processing that needs
            to be performed.
        """
        # Handle a method with 'on_facet_set' decorator information:
        listener = getattr( method, 'on_facet_set', None )
        if listener is not None:
            # Create a 'hidden' pseudo-facet for the method, so we can attach
            # the decorator information to it:
            self.class_facets[ ' ' + name ] = facet = _clone_facet( any_facet )

            simple, rest = listener.extract_static()
            if len( simple ) > 0:
                facet._static   = static = {}
                wrapped_handler = OnFacetChangeWrappers[ simple[0].dispatch ](
                                                                  method, None )
                for simple_item in simple:
                    static[ simple_item.name ] = wrapped_handler

            if rest is not None:
                rest._post_init = listener._post_init
                facet._dynamic  = ( 'method', rest )

        # fixme: This checks for a facets method, an unused feature...
        _check_method( self.class_dict, name, method )


    def _check_property ( self, name, facet ):
        """ Checks a 'property' facet for dependency information and processes
            it if it exists.
        """
        depends_on = facet.depends_on
        if depends_on is not None:
            cached = facet.cached
            if cached is True:
                cached = FacetsCache + name

            if isinstance( depends_on, SequenceTypes ):
                depends_on = ','.join( depends_on )

            simple, rest = _listener_for( depends_on ).extract_static()
            if len( simple ) > 0:
                pre, post     = self._property_zapper_for( name, cached )
                facet._static = static = {}
                if pre is not None:
                    facet._pre_static = pre_static = {}

                for _ in simple:
                    static[ _.name ] = post
                    if pre is not None:
                        pre_static[ _.name ] = pre

            if rest is not None:
                rest._cached   = cached
                facet._dynamic = ( 'property', rest )


    def _property_zapper_for ( self, name, cached ):
        """ Returns a tuple of the form ( pre, post ), where 'pre' and 'post'
            are notification handlers for a property which depends upon other
            values. The 'pre' handler (which may be None) makes sure the current
            property value is saved for the property changed notification that
            follows. The 'post' handler generates the actual property change
            notification.
        """
        if cached is None:
            def post_notify ( object ):
                object.facet_property_set( name, None )

            return ( None, StaticFacetSetWrapper( post_notify ) )

        cached_old = cached + ':old'

        def pre_notify ( object ):
            dict = object.__dict__
            old  = dict.get( cached_old, Undefined )
            if old is Undefined:
                dict[ cached_old ] = dict.pop( cached, None )

        def post_notify ( object ):
            old = object.__dict__.pop( cached_old, Undefined )
            if old is not Undefined:
                object.facet_property_set( name, old )

        return ( StaticFacetSetWrapper( pre_notify  ),
                 StaticFacetSetWrapper( post_notify ) )


    def _event_setter_for ( self, name ):
        """ Returns a function to fire an event called *name* on an arbitrary
            object.
        """
        def event_setter ( object ):
            setattr( object, name, True )

        return StaticFacetSetWrapper( event_setter )


    def _merge_static ( self, to_dic, from_dic ):
        """ Merges the static notifiers in the *from_dic* with the *to_dic*.
        """
        for name, handler in from_dic.iteritems():
            to_dic.setdefault( name, [] ).append( handler )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def _facet_monitor_index ( cls, handler ):
    """ Manages the list of facet instance monitors.
    """
    global _HasFacets_monitors

    type_handler = type( handler )
    for i, cls_handler in enumerate( _HasFacets_monitors ):
        _cls, _handler = cls_handler
        if type_handler is type( _handler ):
            if ((type_handler is MethodType) and
                (handler.im_self is not None)):
                if ((handler.__name__ == _handler.__name__) and
                    (handler.im_self is _handler.im_self)):
                    return i
            elif handler == _handler:
                return i

    return -1


def _create_implements_class ( class_name, interfaces, base_classes ):
    """ Creates a class the implements a set of interfaces.
    """
    locals  = {}
    classes = []
    for interface in interfaces:
        locals[ interface.__name__ ] = interface
        classes.append( interface.__name__ )

    for base_class in base_classes:
        ic = getattr( base_class, ImplementsClass, __NoInterface__ )
        if ic is not __NoInterface__:
            for ifc in _extract_interfaces( ic ):
                name = ifc.__name__
                if name not in locals:
                    locals[ ifc.__name__ ] = ifc
                    classes.append( ifc.__name__ )

    name = class_name + 'Implements'
    exec 'class %s(%s):__ignore_interface__=None' % (
         name, ','.join( classes ) ) in locals

    return locals[ name ]


def _extract_interfaces ( implements_class ):
    """ Extracts the list of interfaces implemented by a specified class.
    """
    result = []
    for ifc in implements_class.__mro__:
        if ifc is Interface:
            break

        if not hasattr( ifc, '__ignore_interface__' ):
            result.append( ifc )

    return result


def implements ( *interfaces ):
    """ Declares the interfaces that a class implements.

        Parameters
        ----------
        interfaces : A list of interface classes
            Classes that the containing class implements.

        Returns
        -------
        Nothing

        Description
        -----------
        Registers each specified interface with the interface manager as an
        interface that the containing class implements. Each specified interface
        must be a subclass of **Interface**. This function should only be
        called from directly within a class body.
    """
    # Exit immediately if there is nothing to do:
    if len( interfaces ) == 0:
        return

    # Verify that each argument is a valid interface:
    for interface in interfaces:
        if not issubclass( interface, Interface ):
            raise FacetError(
                "All arguments to 'implements' must be subclasses of Interface."
            )

    # Define a function that is called when the containing class is constructed:
    def callback ( klass ):
        from category import Category

        target = klass
        bases  = klass.__bases__
        if (len( bases ) == 2) and (bases[0] is Category):
            target = bases[1]

            # Update the class and each of the existing subclasses:
            for subclass in target.facet_subclasses( True ):
                # Merge in the interfaces implemented by the category:
                subclass.__implements__ = _create_implements_class(
                        subclass.__name__, interfaces, [ subclass ] )

        target.__implements__ = _create_implements_class(
            target.__name__, interfaces, bases )

        # Compute the closure of all the interfaces (i.e. include all interface
        # superclasses which are also interfaces):
        closure = set( interfaces )
        for interface in interfaces:
            for subclass in interface.__mro__:
                if subclass is Interface:
                    break

                if issubclass( subclass, Interface ):
                    closure.add( subclass )

        # Tell PyProtocols that the class implements its interfaces:
        declareImplementation( target, instancesProvide = list( closure ) )

        # Make sure the class actually does implement the interfaces it claims
        # to:
        if CHECK_INTERFACES:
            from interface_checker import check_implements

            check_implements( klass, interfaces, CHECK_INTERFACES )

        return klass

    # Request that we be called back at class construction time:
    addClassAdvisor( callback )

#-- 'HasFacets' Decorators -----------------------------------------------------

def on_facet_set ( name, post_init = False, dispatch = 'same', *names ):
    """ Marks the following method definition as being a handler for the
        extended facet change specified by *name(s)*.

        Refer to the documentation for the on_facet_set() method of the
        **HasFacets** class for information on the correct syntax for the
        *name(s)* argument.

        A handler defined using this decorator is normally effective
        immediately. However, if *post_init* is **True**, then the handler only
        become effective after all object constructor arguments have been
        processed. That is, facet values assigned as part of object construction
        will not cause the handler to be invoked.
    """
    if len( names ) > 0:
        name = '%s,%s' % ( name, ','.join( names ) )

    data = ( name, post_init, dispatch )

    def decorator ( function ):
        name, post_init, dispatch = data
        function.on_facet_set  = _listener_for( name ).set(
            dispatch   = dispatch,
            _post_init = post_init
        )

        return function

    return decorator


def cached_property ( function ):
    """ Marks the following method definition as being a "cached property".
        That is, it is a property getter which, for performance reasons, caches
        its most recently computed result in an attribute whose name is of the
        form: *_facets_cache_name*, where *name* is the name of the property. A
        method marked as being a cached property needs only to compute and
        return its result. The @cached_property decorator automatically wraps
        the decorated method in cache management code, eliminating the need to
        write boilerplate cache management code explicitly. For example::

            file_name = File
            file_contents = Property( depends_on = 'file_name' )

            @cached_property
            def _get_file_contents(self):
                fh = open(self.file_name, 'rb')
                result = fh.read()
                fh.close()
                return result

        In this example, accessing the *file_contents* facet calls the
        _get_file_contents() method only once each time after the **file_name**
        facet is modified. In all other cases, the cached value
        **_file_contents**, which maintained by the @cached_property wrapper
        code, is returned.

        Note the use, in the example, of the **depends_on** metadata attribute
        to specify that the value of **file_contents** depends on **file_name**,
        so that _get_file_contents() is called only when **file_name** changes.
        For details, see the facets.core.facets.Property() function.
    """
    name = FacetsCache + function.__name__[ 5: ]

    def decorator ( self ):
        result = self.__dict__.get( name, Undefined )
        if result is Undefined:
            self.__dict__[ name ] = result = function( self )

        return result

    decorator.cached_property = True

    return decorator


def property_depends_on ( dependency = '', settable = False,
                          flushable  = False ):
    """ Marks the following method definition as being a "cached property"
        that depends on the specified extended facet names. That is, it is a
        property getter which, for performance reasons, caches its most recently
        computed result in an attribute whose name is of the form:
        *_facets_cache_name*, where *name* is the name of the property. A method
        marked as being a cached property needs only to compute and return its
        result. The @property_depends_on decorator automatically wraps the
        decorated method in cache management code that will cache the most
        recently computed value and flush the cache when any of the specified
        dependencies are modified, thus eliminating the need to write
        boilerplate cache management code explicitly. For example::

            file_name = File
            file_contents = Property

            @property_depends_on( 'file_name' )
            def _get_file_contents(self):
                fh = open(self.file_name, 'rb')
                result = fh.read()
                fh.close()
                return result

        In this example, accessing the *file_contents* facet calls the
        _get_file_contents() method only once each time after the **file_name**
        facet is modified. In all other cases, the cached value
        **_file_contents**, which is maintained by the @cached_property wrapper
        code, is returned.
    """
    def decorator ( function ):
        name = FacetsCache + function.__name__[5:]

        def wrapper ( self ):
            result = self.__dict__.get( name, Undefined )
            if result is Undefined:
                self.__dict__[ name ] = result = function( self )

            return result

        wrapper.cached_property = True
        wrapper.depends_on      = dependency
        wrapper.settable        = settable
        wrapper.flushable       = flushable

        return wrapper

    return decorator

#-------------------------------------------------------------------------------
#  'HasFacets' class:
#-------------------------------------------------------------------------------

class HasFacets ( CHasFacets ):
    """ Enables any Python class derived from it to have facet atttributes.

        Most of the methods of HasFacets operated by default only on the facet
        attributes explicitly defined in the class definition. They do not
        operate on facet attributes defined by way of wildcards or by calling
        **add_facet()**.
        For example::

            >>>class Person(HasFacets):
            ...    name = Str
            ...    age  = Int
            ...    temp_ = Any
            >>>bob = Person()
            >>>bob.temp_lunch = 'sandwich'
            >>>bob.add_facet('favorite_sport', Str('football'))
            >>>print bob.facet_names()
            ['facet_added', 'age', 'name']

        In this example, the facet_names() method returns only the *age* and
        *name* attributes defined on the Person class. (The **facet_added**
        attribute is an explicit facet event defined on the HasFacets class.)
        The wildcard attribute *temp_lunch* and the dynamically-added facet
        attribute *favorite_sport* are not listed.
    """
    __metaclass__ = MetaHasFacets

    #-- Facet Prefix Rules -----------------------------------------------------

    # Make facets 'property cache' values private with no type checking:
    _facets_cache__ = Any( private = True, transient = True )

    #-- Facet Definitions ------------------------------------------------------

    # An event fired when a new facet is dynamically added to the object:
    facet_added = Event( basestring )

    # An event that can be fired to indicate that the state of the object has
    # been modified:
    facet_modified = Event

    #-- Public Methods ---------------------------------------------------------

    @classmethod
    def facet_monitor ( cls, handler, remove = False ):
        """ Adds or removes the specified *handler* from the list of active
            monitors.

            Parameters
            ----------
            handler : function
                The function to add or remove as a monitor.
            remove : boolean
                Flag indicating whether to remove (True) or add the specified
                handler as a monitor for this class.

            Description
            -----------
            If *remove* is omitted or False, the specified handler is added to
            the list of active monitors; if *remove* is True, the handler is
            removed from the active monitor list.
        """
        global _HasFacets_monitors

        index = _facet_monitor_index( cls, handler )
        if remove:
            if index >= 0:
                del _HasFacets_monitors[ index ]

            return

        if index < 0:
            _HasFacets_monitors.append( ( cls, handler ) )


    @classmethod
    def add_class_facet ( cls, name, *facet ):
        """ Adds a named facet attribute to this class.

            Parameters
            ----------
            name : string
                Name of the attribute to add
            facet : a facet or value that can be converted to a facet using
                Facet() Facet definition of the attribute. It can be a single
                value or a list equivalent to an argument list for the Facet()
                function
        """
        # Make sure a facet argument was specified:
        if len( facet ) == 0:
            raise ValueError( 'No facet definition was specified.' )

        # Make sure only valid facets get added:
        if len( facet ) > 1:
            facet = Facet( * facet )
        else:
            facet = _facet_for( facet[0] )

        # Add the facet to the class:
        cls._add_class_facet( name, facet, False )

        # Also add the facet to all subclasses of this class:
        for subclass in cls.facet_subclasses( True ):
            subclass._add_class_facet( name, facet, True )


    @classmethod
    def _add_class_facet ( cls, name, facet, is_subclass ):
        # Get a reference to the class's dictionary and 'prefix' facets:
        class_dict    = cls.__dict__
        prefix_facets = class_dict[ PrefixFacets ]

        # See if the facet is a 'prefix' facet:
        if name[-1:] == '_':
            name = name[:-1]
            if name in prefix_facets:
                if is_subclass:
                    return

                raise FacetError( "The '%s_' facet is already defined." % name )

            prefix_facets[ name ] = facet

            # Otherwise, add it to the list of known prefixes:
            prefix_list = prefix_facets['*']
            prefix_list.append( name )

            # Resort the list from longest to shortest:
            prefix_list.sort( lambda x, y: len( y ) - len( x ) )

            return

        # Check to see if the facet is already defined:
        class_facets = class_dict[ ClassFacets ]
        if class_facets.get( name ) is not None:
            if is_subclass:
                return

            raise FacetError( "The '%s' facet is aleady defined." % name )

        # Check to see if the facet has additional sub-facets that need to be
        # defined also:
        handler = facet.handler
        if handler is not None:
            if handler.has_items:
                cls.add_class_facet( name + '_items', handler.items_event() )

            if handler.is_mapped:
                cls.add_class_facet( name + '_', _mapped_facet_for( facet ) )

        # Make the new facet inheritable (if allowed):
        if facet.is_base is not False:
            class_dict[ BaseFacets ][ name ] = facet

        # See if there are any static notifiers defined:
        handlers = _non_none( _get_method( cls, '_%s_set' % name ) )

        # Add any special facet defined event handlers:
        _add_event_handlers( facet, cls, handlers )

        # Add the 'anyfacet' handler (if any):
        handlers.extend( prefix_facets.get( '@', EmptyList ) )

        # If there are any handlers, add them to the facet's notifier's list:
        if len( handlers ) > 0:
            facet = _clone_facet( facet )
            _add_notifiers( facet._notifiers( 1 ), handlers )

        # Finally, add the new facet to the class facet dictionary:
        class_facets[ name ] = facet


    @classmethod
    def add_facet_category ( cls, category ):
        """ Adds a facet category to a class.
        """
        if issubclass( category, HasFacets ):
            cls._add_facet_category(
                getattr( category, BaseFacets ),
                getattr( category, ClassFacets ),
                getattr( category, InstanceFacets ),
                getattr( category, PrefixFacets ),
                getattr( category, ListenerFacets ),
                getattr( category, ViewFacets, None ),
                getattr( category, ImplementsClass )
            )

        # Copy all methods that are not already in the class from the category:
        for subcls in category.__mro__:
            for name, value in subcls.__dict__.iteritems():
                if not hasattr( cls, name ):
                    setattr( cls, name, value )


    @classmethod
    def _add_facet_category ( cls, base_facets, class_facets, instance_facets,
                                   prefix_facets, listeners, view_elements,
                                   implements_class ):
        """ Adds a 'category' to the class.
        """
        # Update the class and each of the existing subclasses:
        for subclass in [ cls ] + cls.facet_subclasses( True ):

            # Merge the 'base_facets':
            subclass_facets = getattr( subclass, BaseFacets )
            for name, value in base_facets.iteritems():
                subclass_facets.setdefault( name, value )

            # Merge the 'class_facets':
            subclass_facets = getattr( subclass, ClassFacets )
            for name, value in class_facets.iteritems():
                subclass_facets.setdefault( name, value )

            # Merge the 'instance_facets':
            subclass_facets = getattr( subclass, InstanceFacets )
            for name, arg_lists in instance_facets.iteritems():
                subclass_arg_lists = subclass_facets.get( name )
                if subclass_arg_lists is None:
                    subclass_facets[ name ] = arg_lists[:]
                else:
                    for arg_list in arg_lists:
                        if arg_list not in subclass_arg_lists:
                            subclass_arg_lists.append( arg_list )

            # Merge the 'prefix_facets':
            subclass_facets = getattr( subclass, PrefixFacets )
            subclass_list   = subclass_facets['*']
            changed         = False
            for name, value in prefix_facets.iteritems():
                if name not in subclass_facets:
                    subclass_facets[ name ] = value
                    subclass_list.append( name )
                    changed = True

            # Resort the list from longest to shortest (if necessary):
            if changed:
                subclass_list.sort( lambda x, y: len( y ) - len( x ) )

            # Merge the 'listeners':
            subclass_listeners = getattr( subclass, ListenerFacets )
            subclass_listeners[0].extend( listeners[0] )
            subclass_listeners[1].extend( listeners[1] )

        # Copy all our new view elements into the base class's ViewElements:
        if view_elements is not None:
            content = view_elements.content
            if len( content ) > 0:
                base_ve = getattr( cls, ViewFacets, None )
                if base_ve is None:
                    base_ve = new_view_elements()
                    setattr( cls, ViewFacets, base_ve )
                base_ve_content = base_ve.content
                for name, value in content.iteritems():
                    base_ve_content.setdefault( name, value )


    @classmethod
    def set_facet_dispatch_handler ( cls, name, klass, override = False ):
        """ Sets a facet notification dispatch handler.
        """
        global OnFacetChangeWrappers

        try:
            if issubclass( klass, FacetSetWrapper ):
                if (not override) and (name in OnFacetChangeWrappers):
                    raise FacetError(
                        ("A dispatch handler named '%s' has already been "
                         "defined.") % name
                    )

                OnFacetChangeWrappers[ name ] = klass

                return
        except TypeError:
            pass

        raise FacetError( '%s is not a subclass of FacetSetWrapper.' % klass )


    @classmethod
    def facet_subclasses ( cls, all = False ):
        """ Returns a list of the immediate (or all) subclasses of this class.

            Parameters
            ----------
            all : Boolean
                Indicates whether to return all subclasses of this class. If
                False, only immediate subclasses are returned.
        """
        if not all:
            return list( getattr( cls, SubclassFacets ) )

        return list( cls._facet_subclasses( set() ) )


    @classmethod
    def _facet_subclasses ( cls, subclasses ):
        for subclass in getattr( cls, SubclassFacets ):
            if subclass not in subclasses:
                subclasses.add( subclass )
                subclass._facet_subclasses( subclasses )

        return subclasses


    def has_facets_interface ( self, *interfaces ):
        """Returns whether the object implements a specified facets interface.

           Parameters
           ----------
           interfaces : one or more facets Interface (sub)classes.

           Description
           -----------
           Tests whether the object implements one or more of the interfaces
           specified by *interfaces*. Return **True** if it does, and **False**
           otherwise.
        """
        return issubclass( self.__implements__, interfaces )


    def __getstate__ ( self ):
        """ Returns a dictionary of facets to pickle.

            In general, avoid overriding __getstate__ in subclasses. Instead,
            mark facets that should not be pickled with 'transient = True'
            metadata.

            In cases where this strategy is not sufficient, override
            __getstate__ in subclasses using the following pattern to remove
            items that should not be persisted::

                def __getstate__(self):
                    state = super(X,self).__getstate__()
                    for key in ['foo', 'bar']:
                        state.pop(key,None)
                return state
        """
        # Save all facets which do not have any 'transient' metadata:
        result = self.facet_get( transient = is_none )

        # Add all delegate facets that explicitly have 'transient = False'
        # metadata:
        dic = self.__dict__
        result.update( dict( [ ( name, dic[ name ] )
                             for name in self.facet_names( type = 'delegate',
                                                           transient = False )
                             if name in dic ] ) )

        # If this object implements ISerializable, make sure that all
        # contained HasFacets objects in its persisted state also implement
        # ISerializable:
        if self.has_facets_interface( ISerializable ):
            for name, value in result.iteritems():
                if not _is_serializable( value ):
                    raise FacetError(
                        ("The '%s' facet of a '%s' instance contains the "
                         "unserializable value: %s") %
                        ( name, self.__class__.__name__, value )
                    )

        # Store the facets version in the state dictionary (if possible):
        result.setdefault( '__facets_version__', FacetsVersion )

        # Return the final state dictionary:
        return result


    def __reduce_ex__ ( self, protocol ):
        return ( __newobj__, ( self.__class__, ), self.__getstate__() )


    def __setstate__ ( self, state, facet_change_notify = True ):
        """ Restores the previously pickled state of an object.
        """
        self._init_facet_listeners()
        self.facet_set( facet_change_notify = facet_change_notify, **state )
        self._post_init_facet_listeners()
        self.facets_init()

        self.facets_inited( True )


    def facet_get ( self, *names, **metadata ):
        """ Shortcut for getting object facet attributes.

            Parameters
            ----------
            names : list of facet attribute names
                Facet attributes whose values are requested

            Returns
            -------
            A dictionary whose keys are the names passed as arguments and whose
            values are the corresponding facet values

            Description
            -----------
            Looks up the value of each facet whose name is passed as an argument
            and returns a dictionary containing the resulting name/value pairs.
            If any name does not correspond to a defined facet, it is not
            included in the result.

            If no names are specified, the result is a dictionary containing
            name/value pairs for *all* facets defined on the object.
        """
        result = {}
        n      = len( names )
        if (n == 1) and (type( names[0] ) in SequenceTypes):
            names = names[0]
        elif n == 0:
            names = self.facet_names( **metadata )

        for name in names:
            value = getattr( self, name, Missing )
            if value is not Missing:
                result[ name ] = value

        return result

    # Defines the deprecated alias for 'facet_get'
    get = facet_get


    def facet_set ( self, facet_change_notify = True, **facets ):
        """ Shortcut for setting object facet attributes.

            Parameters
            ----------
            facet_change_notify : Boolean
                If **True** (the default), then each value assigned may generate
                a facet change notification. If **False**, then no facet change
                notifications will be generated. (see also: facet_setq)
            facets : list of key/value pairs
                Facet attributes and their values to be set

            Returns
            -------
            self
                The method returns this object, after setting attributes.

            Description
            -----------
            Treats each keyword argument to the method as the name of a facet
            attribute and sets the corresponding facet attribute to the value
            specified. This is a useful shorthand when a number of facet
            attributes need to be set on an object, or a facet attribute value
            needs to be set in a lambda function. For example, you can write::

                person.facet_set(name='Bill', age=27)

            instead of::

                person.name = 'Bill'
                person.age = 27

        """
        if not facet_change_notify:
            self._facet_change_notify( False )
            try:
                for name, value in facets.iteritems():
                    setattr( self, name, value )
            finally:
                self._facet_change_notify( True )
        else:
            for name, value in facets.iteritems():
                setattr( self, name, value )

        return self

    # Defines the deprecated alias for 'facet_set'
    set = facet_set


    def facet_setq ( self, **facets ):
        """ Shortcut for setting object facet attributes.

            Parameters
            ----------
            facets : list of key/value pairs
                Facet attributes and their values to be set. No facet change
                notifications will be generated for any values assigned (see
                also: facet_set).

            Returns
            -------
            self
                The method returns this object, after setting attributes.

            Description
            -----------
            Treats each keyword argument to the method as the name of a facet
            attribute and sets the corresponding facet attribute to the value
            specified. This is a useful shorthand when a number of facet
            attributes need to be set on an object, or a facet attribute value
            needs to be set in a lambda function. For example, you can write::

                person.facet_setq(name='Bill', age=27)

            instead of::

                person.name = 'Bill'
                person.age = 27

        """
        return self.facet_set( facet_change_notify = False, **facets )


    def facet_value ( self, name ):
        """ Returns the value of a specified facet.

            Parameters
            ----------
            name : string
                Name of the facet whose value is to be returned.

            Returns
            -------
            The value of the facet specified by *name*.

            Description
            -----------
            This method is the same as **getattr( self, name )** except in
            the case where a **FacetValue** object has been assigned to *name*.
            In this case, the result is the **FacetValue** object, instead of
            the value the **FacetValue** object refers to. In other words, this
            method returns the *quoted* value of *name*.
        """
        return (self.facet( name )._facet_value or getattr( self, name ))


    def facet_db_get ( self, name, default = None ):
        """ Gets the value associated with a specified persistent facets
            database name.

            Parameters
            ----------
            name : string
                Name of the facets database value to get.

            default : any
                The value to be returned if the specified name is not in the
                facets database. The default value is None.

            Returns
            -------
            The value in the facets database associated with the specified
            *name*, or *default* if *name* is not defined.

            Description
            -----------
            The *name* specified should be a string. If *name* does not contain
            any '.' characters, then a composite name of the form:
            fully_qualified_name( self.__class__ ):name is used. For example,
            if the *name* is 'foo', and self is an instance of the Bar class
            from the bar module in the mycode.mypackage package, then the
            resulting name is: "mycode.mypackage.bar.Bar:foo". The purpose of
            using the composite name in this case is to avoid unnecessary
            namespace collisions in the database.
        """
        return facet_db.get( name, default, self )


    def facet_db_set ( self, name, value = Missing ):
        """ Sets or deletes the value associated with a specified persistent
            facets database name.

            Parameters
            ----------
            name : string
                Name of the facets database value to set or delete.

            value : any
                The value to be associated with the specified name in the facets
                database. The default value is Missing, which means any value
                currently associated with the specified name in the facets
                database should be deleted.

            Returns
            -------
            None

            Description
            -----------
            The *name* specified should be a string. If *name* does not contain
            any '.' characters, then a composite name of the form:
            fully_qualified_name( self.__class__ ):name is used. For example,
            if the *name* is 'foo', and self is an instance of the Bar class
            from the bar module in the mycode.mypackage package, then the
            resulting name is: "mycode.mypackage.bar.Bar:foo". The purpose of
            using the composite name in this case is to avoid unnecessary
            namespace collisions in the database.

            No error is raised if *value* is Missing and the facets database
            does not have any value associated with the specified name.
        """
        facet_db.set( name, value, self )


    def reset_facets ( self, facets = None, **metadata ):
        """ Resets some or all of an object's facet attributes to their default
            values.

            Parameters
            ----------
            facets : list of strings
                Names of facet attributes to reset

            Returns
            -------
            A list of attributes that the method was unable to reset, which is
            empty if all the attributes were successfully reset.

            Description
            -----------
            Resets each of the facets whose names are specified in the *facets*
            list to their default values. If *facets* is None or omitted, the
            method resets all explicitly-defined object facet attributes to
            their default values. Note that this does not affect wildcard facet
            attraibutes or facet attributes added via add_facet(), unless they
            are explicitly named in *facets*.
        """
        unresetable = []

        if facets is None:
            facets = self.facet_names( **metadata )

        for name in facets:
            try:
                delattr( self, name )
            except ( AttributeError, FacetError ):
                unresetable.append( name )

        return unresetable


    def copyable_facet_names ( self, **metadata ):
        """ Returns the list of facet names to copy or clone by default.
        """
        metadata.setdefault( 'transient', lambda t: t is not True )

        return self.facet_names( **metadata )


    def all_facet_names ( self ):
        """ Returns the list of all facet names, including implicitly defined
            facets.
        """
        return self.__class_facets__.keys()


    def copy_facets ( self, other, facets = None, memo = None, copy = None,
                            **metadata ):
        """ Copies another object's facet attributes into this one.

            Parameters
            ----------
            other : object
                The object whose facet attribute values should be copied.
            facets : list of strings
                A list of names of facet attributes to copy. If None or
                unspecified, the set of names returned by facet_names() is used.
                If 'all' or an empty list, the set of names returned by
                all_facet_names() is used.
            memo : dictionary
                A dictionary of objects that have already been copied.
            copy : None | 'deep' | 'shallow'
                The type of copy to perform on any facet that does not have
                explicit 'copy' metadata. A value of None means
                'copy reference'.

            Returns
            -------
            A list of attributes that the method was unable to copy,
            which is empty if all the attributes were successfully copied.
        """
        if facets is None:
            facets = self.copyable_facet_names( **metadata )
        elif (facets == 'all') or (len( facets ) == 0):
            facets = self.all_facet_names()
            if memo is not None:
                memo[ 'facets_to_copy' ] = 'all'

        unassignable = []
        deferred     = []
        deep_copy    = (copy == 'deep')
        shallow_copy = (copy == 'shallow')

        for name in facets:
            try:
                facet = self.facet( name )
                if facet.type in DeferredCopy:
                    deferred.append( name )
                    continue

                base_facet = other.base_facet( name )
                if base_facet.type == 'event':
                    continue

                value     = getattr( other, name )
                copy_type = base_facet.copy
                if copy_type == 'shallow':
                    value = copy_module.copy( value )
                elif copy_type == 'ref':
                    pass
                elif (copy_type == 'deep') or deep_copy:
                    if memo is None:
                        value = copy_module.deepcopy( value )
                    else:
                        value = copy_module.deepcopy( value, memo )
                elif shallow_copy:
                    value = copy_module.copy( value )

                setattr( self, name, value )
            except:
                unassignable.append( name )

        for name in deferred:
            try:
                value     = getattr( other, name )
                copy_type = other.base_facet( name ).copy
                if copy_type == 'shallow':
                    value = copy_module.copy( value )
                elif copy_type == 'ref':
                    pass
                elif (copy_type == 'deep') or deep_copy:
                    if memo is None:
                        value = copy_module.deepcopy( value )
                    else:
                        value = copy_module.deepcopy( value, memo )
                elif shallow_copy:
                    value = copy_module.copy( value )

                setattr( self, name, value )
            except:
                unassignable.append( name )

        return unassignable


    def clone_facets ( self, facets = None, memo = None, copy = None,
                             **metadata ):
        """ Clones a new object from this one, optionally copying only a
            specified set of facets.

            Parameters
            ----------
            facets : list of strings
                The names of the facet attributes to copy.
            memo : dictionary
                A dictionary of objects that have already been copied.
            copy : None | 'deep' | 'shallow'
                The type of copy to perform on any facet that does not have
                explicit 'copy' metadata. A value of None means
                'copy reference'.

            Returns
            -------
            The newly cloned object.

            Description
            -----------
            Creates a new object that is a clone of the current object. If
            *facets* is None (the default), then all explicit facet attributes
            defined for this object are cloned. If *facets* is 'all' or an empty
            list, the list of facets returned by all_facet_names() is used;
            otherwise, *facets* must be a list of the names of the facet
            attributes to be cloned.
        """
        if memo is None:
            memo = {}

        if facets is None:
            facets = self.copyable_facet_names( **metadata )
        elif (facets == 'all') or (len( facets ) == 0):
            facets = self.all_facet_names()
            memo[ 'facets_to_copy' ] = 'all'

        memo[ 'facets_copy_mode' ] = copy
        new = self.__new__( self.__class__ )
        memo[ id( self ) ] = new
        new._init_facet_listeners()
        new.copy_facets( self, facets, memo, copy, **metadata )
        new._post_init_facet_listeners()
        new.facets_init()
        new.facets_inited( True )

        return new


    def __deepcopy__ ( self, memo ):
        """ Creates a deep copy of the object.
        """
        id_self = id( self )
        if id_self in memo:
            return memo[ id_self ]

        result = self.clone_facets( memo   = memo,
                                    facets = memo.get( 'facets_to_copy' ),
                                    copy   = memo.get( 'facets_copy_mode' ) )

        return result


    def edit_facets ( self, view       = None, parent  = None,
                            kind       = None, context = None,
                            handler    = None, id      = '',
                            scrollable = None, **args ):
        """ Displays a user interface window for editing facet attribute values.

            Parameters
            ----------
            view : view or string
                A View object (or its name) that defines a user interface for
                editing facet attribute values of the current object. If the
                view is defined as an attribute on this class, use the name of
                the attribute. Otherwise, use a reference to the view object. If
                this attribute is not specified, the View object returned by
                facet_view() is used.
            parent : window handle
                A user interface component to use as the parent window for the
                object's UI window.
            kind : string
                The type of user interface window to create. See the
                **facets.ui.ui_facets.AKind** facet for values and
                their meanings. If *kind* is unspecified or None, the **kind**
                attribute of the View object is used.
            context : object or dictionary
                A single object or a dictionary of string/object pairs, whose
                facet attributes are to be edited. If not specified, the current
                object is used.
            handler : Handler object
                A handler object used for event handling in the dialog box. If
                None, the default handler for Facets UI is used.
            id : string
                A unique ID for persisting preferences about this user
                interface, such as size and position. If not specified, no user
                preferences are saved.
            scrollable : Boolean
                Indicates whether the dialog box should be scrollable. When set
                to True, scroll bars appear on the dialog box if it is not large
                enough to display all of the items in the view at one time.
        """
        if context is None:
            context = self

        view = self.facet_view( view )

        from facets.ui.toolkit          import toolkit
        from facets.ui.view_application import view_application

        if toolkit().is_application_running():
            return view.ui( context, parent, kind, self.facet_view_elements(),
                            handler, id, scrollable, args )

        return view_application( context, view, kind, handler, id, scrollable,
                                 args )


    def facet_context ( self ):
        """ Returns the default context to use for editing or configuring
            facets.
        """
        return { 'object': self }


    def facet_view ( self, name = None, view_element = None ):
        """ Gets or sets a ViewElement associated with an object's class.

            Parameters
            ----------
            name : string
                Name of a view element
            view_element : a ViewElement object
                View element to associate

            Returns
            -------
            A view element.

            Description
            -----------
            If both *name* and *view_element* are specified, the view element is
            associated with *name* for the current object's class. (That is,
            *view_element* is added to the ViewElements object associated with
            the current object's class, indexed by *name*.)

            If only *name* is specified, the function returns the view element
            object associated with *name*, or None if *name* has no associated
            view element. View elements retrieved by this function are those
            that are bound to a class attribute in the class definition, or that
            are associated with a name by a previous call to this method.

            If neither *name* nor *view_element* is specified, the method
            returns a View object, based on the following order of preference:

            1. If there is a View object named ``facets_view`` associated with
               the current object, it is returned.
            2. If there is exactly one View object associated the current
               object, it is returned.
            3. Otherwise, it returns a View object containing items for all the
               non-event facet attributes on the current object.

        """
        return self.__class__._facet_view( name, view_element,
                            self.default_facets_view, self.facet_view_elements,
                            self.editable_facets, self )


    @classmethod
    def class_facet_view ( cls, name = None, view_element = None ):
        return cls._facet_view( name, view_element,
                  cls.class_default_facets_view, cls.class_facet_view_elements,
                  cls.class_editable_facets, None )


    @classmethod
    def _facet_view ( cls, name, view_element, default_name, view_elements,
                           editable_facets, handler ):
        """ Gets or sets a ViewElement associated with an object's class.
        """
        # If a view element was passed instead of a name or None, return it:
        if is_view_element( name ):
            return name

        # Get the ViewElements object associated with the class:
        view_elements = view_elements()

        # The following test should only succeed for objects created before
        # facets has been fully initialized (such as the default Handler):
        if view_elements is None:
            from facets.ui.view_elements import dummy_view_elements

            view_elements = dummy_view_elements

        if name:
            if view_element is None:
                # If only a name was specified, return the ViewElement it
                # matches, if any:
                result = view_elements.find( name )
                if (result is None) and (handler is not None):
                    method = getattr( handler, name, None )
                    if callable( method ):
                        result = method()

                return result

            # Otherwise, save the specified ViewElement under the name
            # specified:
            view_elements.content[ name ] = view_element

            return None

        # Get the default view/view name:
        name = default_name()

        # If the default is a View, return it:
        if is_view_element( name ):
            return name

        # Otherwise, get all View objects associated with the object's class:
        names = view_elements.filter_by()

        # If the specified default name is in the list, return its View:
        if name in names:
            return view_elements.find( name )

        if handler is not None:
            method = getattr( handler, name, None )
            if callable( method ):
                result = method()
                if is_view_element( result ):
                    return result

        # If there is only one View, return it:
        if len( names ) == 1:
            return view_elements.find( names[0] )

        # Otherwise, create and return a View based on the set of editable
        # facets defined for the object:
        from facets.api import View

        return View( editable_facets() )


    def default_facets_view ( self ):
        """ Returns the name of the default facets view for the object's class.
        """
        return self.__class__.class_default_facets_view()


    @classmethod
    def class_default_facets_view ( cls ):
        """ Returns the name of the default facets view for the class.
        """
        return DefaultFacetsView


    def facet_views ( self, klass = None ):
        """ Returns a list of the names of all view elements associated with the
            current object's class.

            Parameters
            ----------
            klass : a class
                A class, such that all returned names must correspond to
                instances of this class. Possible values include:

                * Group
                * Item
                * View
                * ViewElement
                * ViewSubElement

            Description
            -----------
            If *klass* is specified, the list of names is filtered such that
            only objects that are instances of the specified class are returned.
        """
        return self.__class__.__dict__[ ViewFacets ].filter_by( klass )


    def facet_view_elements ( self ):
        """ Returns the ViewElements object associated with the object's
            class.

            The returned object can be used to access all the view elements
            associated with the class.
        """
        return self.__class__.class_facet_view_elements()


    @classmethod
    def class_facet_view_elements ( cls ):
        """ Returns the ViewElements object associated with the class.

        The returned object can be used to access all the view elements
        associated with the class.
        """
        return cls.__dict__[ ViewFacets ]


    def configure_facets ( self, filename = None, view       = None,
                                 kind     = None, edit       = True,
                                 context  = None, handler    = None,
                                 id       = '',   scrollable = None, **args ):
        """Creates and displays a dialog box for editing values of facet
            attributes, as if it were a complete, self-contained GUI
            application.

            Parameters
            ----------
            filename : string
                The name (including path) of a file that contains a pickled
                representation of the current object. When this parameter is
                specified, the method reads the corresponding file (if it
                exists) to restore the saved values of the object's facets
                before displaying them. If the user confirms the dialog box (by
                clicking **OK**), the new values are written to the file. If
                this parameter is not specified, the values are loaded from the
                in-memory object, and are not persisted when the dialog box is
                closed.
            view : view or string
                A View object (or its name) that defines a user interface for
                editing facet attribute values of the current object. If the
                view is defined as an attribute on this class, use the name of
                the attribute. Otherwise, use a reference to the view object. If
                this attribute is not specified, the View object returned by
                facet_view() is used.
            kind : string
                The type of user interface window to create. See the
                **facets.ui.ui_facets.AKind** facet for values and
                their meanings. If *kind* is unspecified or None, the **kind**
                attribute of the View object is used.
            edit : Boolean
                Indicates whether to display a user interface. If *filename*
                specifies an existing file, setting *edit* to False loads the
                saved values from that file into the object without requiring
                user interaction.
            context : object or dictionary
                A single object or a dictionary of string/object pairs, whose
                facet attributes are to be edited. If not specified, the current
                object is used
            handler : Handler object
                A handler object used for event handling in the dialog box. If
                None, the default handler for Facets UI is used.
            id : string
                A unique ID for persisting preferences about this user
                interface, such as size and position. If not specified, no user
                preferences are saved.
            scrollable : Boolean
                Indicates whether the dialog box should be scrollable. When set
                to True, scroll bars appear on the dialog box if it is not large
                enough to display all of the items in the view at one time.

            Description
            -----------
            This method is intended for use in applications that do not normally
            have a GUI. Control does not resume in the calling application until
            the user closes the dialog box.

            The method attempts to open and unpickle the contents of *filename*
            before displaying the dialog box. When editing is complete, the
            method attempts to pickle the updated contents of the object back to
            *filename*. If the file referenced by *filename* does not exist, the
            object is not modified before displaying the dialog box. If
            *filename* is unspecified or None, no pickling or unpickling occurs.

            If *edit* is True (the default), a dialog box for editing the
            current object is displayed. If *edit* is False or None, no
            dialog box is displayed. You can use ``edit=False`` if you want the
            object to be restored from the contents of *filename*, without being
            modified by the user.
        """
        if filename is not None:
            fd = None
            try:
                fd = open( filename, 'rb' )
                self.copy_facets( Unpickler( fd ).load() )
            except:
                if fd is not None:
                    fd.close()

        if edit:
            from facets.ui.view_application import view_application

            if context is None:
                context = self

            rc = view_application( context, self.facet_view( view ), kind,
                                   handler, id, scrollable, args ).result
            if rc and (filename is not None):
                fd = None
                try:
                    fd = open( filename, 'wb' )
                    Pickler( fd, True ).dump( self )
                finally:
                    if fd is not None:
                        fd.close()
            return rc

        return True


    def editable_facets ( self ):
        """Returns an alphabetically sorted list of the names of non-event
           facet attributes associated with the current object.
        """
        names = self.facet_names( type = not_event, editable = not_false )
        names.sort()

        return names


    @classmethod
    def class_editable_facets ( cls ):
        """Returns an alphabetically sorted list of the names of non-event
           facet attributes associated with the current class.
        """
        names = cls.class_facet_names( type = not_event, editable = not_false )
        names.sort()

        return names


    def print_facets ( self, show_help = False, **metadata ):
        """ Prints the values of all explicitly-defined, non-event facet
            attributes on the current object, in an easily readable format.

            Parameters
            ----------
            show_help : Boolean
                Indicates whether to display additional descriptive information.
        """
        if len( metadata ) > 0:
            names = self.facet_names( **metadata )
        else:
            names = self.facet_names( type = not_event )

        if len( names ) == 0:
            print ''
            return

        result = []
        pad    = max( [ len( x ) for x in names ] ) + 1
        maxval = 78 - pad
        names.sort()

        for name in names:
            try:
                value = repr( getattr( self, name ) ).replace( '\n', '\\n' )
                if len( value ) > maxval:
                    value = '%s...%s' % ( value[ : (maxval - 2) / 2 ],
                                          value[ -(( maxval - 3) / 2): ] )
            except:
                value = '<undefined>'

            lname = (name + ':').ljust( pad )
            if show_help:
                result.append( '%s %s\n   The value must be %s.' % (
                       lname, value, self.base_facet( name ).setter.info() ) )
            else:
                result.append( '%s %s' % ( lname, value ) )

        print '\n'.join( result )


    def _on_facet_set ( self, handler, name = None, remove = False,
                              dispatch = 'same', priority = False ):
        """ Causes the object to invoke a handler whenever a facet attribute
            is modified, or removes the association.

            Parameters
            ----------
            handler : function
                A facet notification function for the attribute specified by
                *name*.
            name : string
                Specifies the facet attribute whose value changes trigger the
                notification.
            remove : Boolean
                If True, removes the previously-set association between
                *handler* and *name*; if False (the default), creates the
                association.

            Description
            -----------
            Multiple handlers can be defined for the same object, or even for
            the same facet attribute on the same object. If *name* is not
            specified or is None, *handler* is invoked when any facet attribute
            on the object is changed.
        """
        name = name or 'anyfacet'

        if remove:
            if name == 'anyfacet':
                notifiers = self._notifiers( 0 )
            else:
                facet = self._facet( name, 1 )
                if facet is None:
                    return

                notifiers = facet._notifiers( 0 )

            if notifiers is not None:
                for i, notifier in enumerate( notifiers ):
                    if notifier.equals( handler ):
                        del notifiers[i]
                        notifier.dispose()

                        break

            return

        if name == 'anyfacet':
            notifiers = self._notifiers( 1 )
        else:
            notifiers = self._facet( name, 2 )._notifiers( 1 )

        for notifier in notifiers:
            if notifier.equals( handler ):
                break
        else:
            wrapper = OnFacetChangeWrappers[ dispatch ]( handler, notifiers )
            if priority:
                notifiers.insert( 0, wrapper )
            else:
                notifiers.append( wrapper )


    def on_facet_set ( self, handler, name = None, remove = False,
                             dispatch = 'same', priority = False,
                             deferred = False ):
        """ Causes the object to invoke a handler whenever a facet attribute
            matching a specified pattern is modified, or removes the
            association.

            Parameters
            ----------
            handler : function
                A facet notification function for the *name* facet attribute,
                with one of the signatures described below.
            name : string
                The name of the facet attribute whose value changes trigger the
                notification. The *name* can specify complex patterns of facet
                changes using an extended *name* syntax, which is described
                below.
            remove : Boolean
                If True, removes the previously-set association between
                *handler* and *name*; if False (the default), creates the
                association.
            dispatch : string
                A string indicating the thread on which notifications must be
                run. Possible values are:

                    * 'same': Run notifications on the same thread as this one.
                    * 'ui': Run notifications on the UI thread, and allow them
                      to be queued and deferred.
                    * 'fast_ui': Run notifications on the UI thread, and process
                      them immediately.
                    * 'new': Run notifications in a new thread.

            Description
            -----------
            Multiple handlers can be defined for the same object, or even for
            the same facet attribute on the same object. If *name* is not
            specified or is None, *handler* is invoked when any facet attribute
            on the object is changed.

            The *name* parameter is a single *xname* or a list of *xname* names,
            where an *xname* is an extended name of the form::

                xname2[('.'|':') xname2]*

            An *xname2* is of the form::

                ( xname3 | '['xname3[','xname3]*']' ) ['*']

            An *xname3* is of the form::

                 xname | ['+'|'-'][name] | name['?' | ('+'|'-')[name]]

            A *name* is any valid Python attribute name. The semantic meaning of
            this notation is as follows:

            - ``item1.item2`` means *item1* is a facet containing an object (or
              objects if *item1* is a list or dict) with a facet called *item2*.
              Changes to either *item1* or *item2* cause a notification to be
              generated.
            - ``item1:item2`` means *item1* is a facet containing an object (or
              objects if *item1* is a list or dict) with a facet called *item2*.
              Changes to *item2* cause a notification to be generated, while
              changes to *item1* do not (i.e., the ':' indicates that changes to
              the *link* object should not be reported).
            - ``[ item1, item2, ..., itemN ]``: A list which matches any of the
              specified items. Note that at the topmost level, the surrounding
              square brackets are optional.
            - ``name?``: If the current object does not have an attribute called
              *name*, the reference can be ignored. If the '?' character is
              omitted, the current object must have a facet called *name*,
              otherwise an exception will be raised.
            - ``prefix+``: Matches any facet on the object whose name
              begins with *prefix*.
            - ``+metadata_name``: Matches any facet on the object having
              *metadata_name* metadata.
            - ``-metadata_name``: Matches any facet on the object which
              does not have *metadata_name* metadata.
            - ``prefix+metadata_name``: Matches any facet on the object
              whose name begins with *prefix* and which has *metadata_name*
              metadata.
            - ``prefix-metadata_name``: Matches any facet on the object
              whose name begins with *prefix* and which does not have
              *metadata_name* metadata.
            - ``+``: Matches all facets on the object.
            - ``pattern*``: Matches object graphs where *pattern* occurs one or
              more times (useful for setting up listeners on recursive data
              structures like trees or linked lists).

            Some examples of valid names and their meaning are as follows:

            - 'foo,bar,baz': Listen for facet changes to *object.foo*,
              *object.bar*, and *object.baz*.
            - ['foo','bar','baz']: Equivalent to 'foo,bar,baz', but may be more
              useful in cases where the individual items are computed.
            - 'foo.bar.baz': Listen for facet changes to *object.foo.bar.baz*
              and report changes to *object.foo*, *object.foo.bar* or
              *object.foo.bar.baz*.
            - 'foo:bar:baz': Listen for changes to *object.foo.bar.baz*, and
              only report changes to *object.foo.bar.baz*.
            - 'foo.[bar,baz]': Listen for facet changes to *object.foo.bar* and
              *object.foo.baz*.
            - '[left,right]*.name': Listen for facet changes to the *name*
              facet of each node of a tree having *left* and *right* links to
              other tree nodes, and where *object* the method is applied to
              the root node of the tree.
            - +dirty: Listen for facet changes on any facet in the *object*
              which has the 'dirty' metadata set.
            - 'foo.+dirty': Listen for facet changes on any facet in
              *object.foo* which has the 'dirty' metadata set.
            - 'foo.[bar,-dirty]': Listen for facet changes on *object.foo.bar*
              or any facet on *object.foo* which does not have 'dirty' metadata
              set.

            Note that any of the intermediate (i.e., non-final) links in a
            pattern can be facets of type Instance, List or Dict. In the case
            of List and Dict facets, the subsequent portion of the pattern is
            applied to each item in the list, or value in the dictionary.

            For example, if the self.children is a list, 'children.name'
            listens for facet changes to the *name* facet for each item in the
            self.children list.

            Note that items added to or removed from a list or dictionary in
            the pattern will cause the *handler* routine to be invoked as well,
            since this is treated as an *implied* change to the item's facet
            being monitored.

            The signature of the *handler* supplied also has an effect on
            how changes to intermediate facets are processed. The five valid
            handler signatures are:

            1. handler()
            2. handler(new)
            3. handler(name,new)
            4. handler(object,name,new)
            5. handler(object,name,old,new)

            For signatures 1, 4 and 5, any change to any element of a path
            being listened to invokes the handler with information about the
            particular element that was modified (e.g., if the item being
            monitored is 'foo.bar.baz', a change to 'bar' will call *handler*
            with the following information:

            - object: object.foo
            - name:   bar
            - old:    old value for object.foo.bar
            - new:    new value for object.foo.bar

            If one of the intermediate links is a List or Dict, the call to
            *handler* may report an *_items* changed event. If in the previous
            example, *bar* is a List, and a new item is added to *bar*, then
            the information passed to *handler* would be:

            - object: object.foo
            - name:   bar_items
            - old:    Undefined
            - new:    FacetListEvent whose *added* facet contains the new item
              added to *bar*.

            For signatures 2 and 3, the *handler* does not receive enough
            information to discern between a change to the final facet being
            listened to and a change to an intermediate link. In this case,
            the event dispatcher will attempt to map a change to an
            intermediate link to its effective change on the final facet. This
            only works if all of the intermediate links are single values (such
            as an Instance or Any facet) and not Lists or Dicts. If the modified
            intermediate facet or any subsequent intermediate facet preceding
            the final facet is a List or Dict, then a FacetError is raised,
            since the effective value for the final facet cannot in general be
            resolved unambiguously. To prevent FacetErrors in this case, use the
            ':' separator to suppress notifications for changes to any of the
            intermediate links.

            Handler signature 1 also has the special characteristic that if a
            final facet is a List or Dict, it will automatically handle '_items'
            changed events for the final facet as well. This can be useful in
            cases where the *handler* only needs to know that some aspect of the
            final facet has been changed. For all other *handler* signatures,
            you must explicitly specify the 'xxx_items' facet if you want to
            be notified of changes to any of the items of the 'xxx' facet.
        """
        # Check to see if we can do a quick exit to the basic facet change
        # handler:
        if ((isinstance( name, basestring ) and
            (extended_facet_pat.match( name ) is None)) or
            (name is None)):
            self._on_facet_set( handler, name, remove, dispatch, priority )

            return

        if isinstance( name, list ):
            for name_i in name:
                self.on_facet_set(
                    handler, name_i, remove, dispatch, priority
                )

            return

        # Make sure we have a name string:
        name = (name or 'anyfacet').strip()

        if remove:
            dict = self.__dict__.get( FacetsListener )
            if dict is not None:
                listeners = dict.get( name )
                if listeners is not None:
                    for i, wrapper in enumerate( listeners ):
                        if wrapper.equals( handler ):
                            del listeners[ i ]
                            if len( listeners ) == 0:
                                del dict[ name ]
                                if len( dict ) == 0:
                                    del self.__dict__[ FacetsListener ]

                            wrapper.listener.unregister( self )
                            wrapper.dispose()

                            break
        else:
            dict      = self.__dict__.setdefault( FacetsListener, {} )
            listeners = dict.setdefault( name, [] )
            for wrapper in listeners:
                if wrapper.equals( handler ):
                    break
            else:
                listener = _listener_for( name )
                lnw = listener.wrapper_class( handler, self, name, listener )
                listeners.append( lnw )
                listener.set(
                    wrapped_handler = lnw,
                    dispatch        = dispatch,
                    priority        = priority,
                    deferred        = deferred
                )
                listener.register( self )

    # Define a synonym for 'on_facet_set':
    on_facet_event = on_facet_set


    def notify_on_facet_set ( self, *names ):
        """ Suspends the caller until one of the facets specified by *names* has
            been changed. It returns the notification object for the facet that
            was changed.

            *names* can be a list of one or more strings using the facet
            extended change notification syntax used by the 'on_facet_set'
            method, or can contains lists of such strings. If no values are
            specified, then the method will return once any facet on the object
            has changed.
        """
        for i, name in enumerate( names ):
            if isinstance( name, SequenceTypes ):
                names[ i ] = ','.join( name )

        return EventLoopListener(
            object = self,
            facets = ','.join( names )
        ).wait()


    def sync_facet ( self, facet_name, object, alias = None, mutual = True,
                           remove = False ):
        """ Synchronizes the value of a facet attribute on this object with a
            facet attribute on another object.

            Parameters
            ----------
            name : string
                Name of the facet attribute on this object
            object : object
                The object with which to synchronize
            alias : string
                Name of the facet attribute on *other*; if None or omitted, same
                as *name*.
            mutual : Boolean or integer
                Indicates whether synchronization is mutual (True or non-zero)
                or one-way (False or zero)
            remove : Boolean or integer
                Indicates whether sychronization is being added (False or zero)
                or removed (True or non-zero)

            Description
            -----------
            In mutual synchronization, any change to the value of the specified
            facet attribute of either object results in the same value being
            assigned to the corresponding facet attribute of the other object.
            In one-way synchronization, any change to the value of the attribute
            on this object causes the corresponding facet attribute of *object*
            to be updated, but not vice versa.
        """
        if alias is None:
            alias = facet_name

        is_list = (self._is_list_facet( facet_name ) and
                   object._is_list_facet( alias ))

        if remove:
            info = self._get_sync_facet_info()
            dic  = info.get( facet_name )
            if dic is not None:
                key = ( id( object ), alias )
                if key in dic:
                    del dic[ key ]

                    if len( dic ) == 0:
                        del info[ facet_name ]
                        self._on_facet_set( self._sync_facet_modified,
                                            facet_name, remove = True )

                        if is_list:
                            self._on_facet_set( self._sync_facet_items_modified,
                                          facet_name + '_items', remove = True )

            if mutual:
                object.sync_facet( alias, self, facet_name, False, True )

            return

        value = ( weakref.ref( object, self._sync_facet_listener_deleted ),
                  alias )
        dic   = self._get_sync_facet_info().setdefault( facet_name, {} )
        key   = ( id( object ), alias )
        if key not in dic:
            if len( dic ) == 0:
                self._on_facet_set( self._sync_facet_modified, facet_name )
                if is_list:
                    self._on_facet_set( self._sync_facet_items_modified,
                                        facet_name + '_items' )

            dic[ key ] = value
            setattr( object, alias, getattr( self, facet_name ) )

        if mutual:
            object.sync_facet( alias, self, facet_name, False )


    def _get_sync_facet_info ( self ):
        info = getattr( self, '__sync_facet__', None )
        if info is None:
            self.__dict__[ '__sync_facet__' ] = info = { '': set() }

        return info


    def _sync_facet_modified ( self, object, facet, old, new ):
        info   = self.__sync_facet__
        locked = info[ '' ]
        locked.add( facet )
        for object, object_name in info[ facet ].values():
            object = object()
            if object_name not in object._get_sync_facet_info()[ '' ]:
                try:
                    setattr( object, object_name, new )
                except:
                    pass

        locked.remove( facet )


    def _sync_facet_items_modified ( self, object, facet, old, event ):
        n0     = event.index
        n1     = n0 + len( event.removed )
        facet  = facet[:-6]
        info   = self.__sync_facet__
        locked = info['']
        locked.add( facet )
        for object, object_name in info[ facet ].values():
            object = object()
            if object_name not in object._get_sync_facet_info()['']:
                try:
                    getattr( object, object_name )[ n0: n1 ] = event.added
                except:
                    pass

        locked.remove( facet )


    def _sync_facet_listener_deleted ( self, ref ):
        info = self.__sync_facet__
        for key, dic in info.items():
            if key != '':
                for name, value in dic.items():
                    if ref is value[0]:
                        del dic[ name ]
                        if len( dic ) == 0:
                            del info[ key ]


    def _is_list_facet ( self, facet_name ):
        handler = self.base_facet( facet_name ).handler

        return ((handler is not None) and (handler.collection_type == 'list'))


    def add_facet ( self, name, *facet ):
        """ Adds a facet attribute to this object.

            Parameters
            ----------
            name : string
                Name of the attribute to add
            facet : facet or a value that can be converted to a facet by Facet()
                Facet definition for *name*. If more than one value is
                specified, it is equivalent to passing the entire list of values
                to Facet().
        """
        # Make sure a facet argument was specified:
        if len( facet ) == 0:
            raise ValueError( 'No facet definition was specified.' )

        # Make sure only valid facets get added:
        if len( facet ) > 1:
            facet = Facet( *facet )
        else:
            facet = _facet_for( facet[0] )

        # Check to see if the facet has additional sub-facets that need to be
        # defined also:
        handler = facet.handler
        if handler is not None:
            if handler.has_items:
                self.add_facet( name + '_items', handler.items_event() )

            if handler.is_mapped:
                self.add_facet( name + '_', _mapped_facet_for( facet ) )

        # See if there already is a class or instance facet with the same name:
        old_facet = self._facet( name, 0 )

        # Get the object's instance facet dictionary and add a clone of the new
        # facet to it:
        ifacet_dict = self._instance_facets()
        ifacet_dict[ name ] = facet = _clone_facet( facet )

        # If there already was a facet with the same name:
        if old_facet is not None:
            # Copy the old facets notifiers into the new facet:
            old_notifiers = old_facet._notifiers( 0 )
            if old_notifiers is not None:
                facet._notifiers( 1 ).extend( old_notifiers )
        else:
            # Otherwise, see if there are any static notifiers that should be
            # applied to the facet:
            cls      = self.__class__
            handlers = _non_none( _get_method( cls, '_%s_set' % name ) )

            # Add any special facet defined event handlers:
            _add_event_handlers( facet, cls, handlers )

            # Add the 'anyfacet' handler (if any):
            handlers.extend( self.__prefix_facets__.get( '@', EmptyList ) )

            # If there are any static notifiers, attach them to the facet:
            if len( handlers ) > 0:
                _add_notifiers( facet._notifiers( 1 ), handlers )

            if (facet.type == 'delegate') and (name[-6:] != '_items'):
                listener = _listener_for( _get_delegate_pattern( name, facet ) )
                facet._dynamic = ( 'delegate', listener )
                self._init_facet_delegate_listener( name, listener )

            # Since this is a new facet, fire the 'facet_added' event:
            self.facet_added = name


    def remove_facet ( self, name ):
        """ Removes a facet attribute from this object.

            Parameters
            ----------
            name : string
                Name of the attribute to remove
        """
        # Get the facet definition:
        facet = self._facet( name, 0 )
        if facet is not None:

            # Check to see if the facet has additional sub-facets that need to
            # be removed also:
            handler = facet.handler
            if handler is not None:
                if handler.has_items:
                    self.remove_facet( name + '_items' )

                if handler.is_mapped:
                    self.remove_facet( name + '_' )

            # If the facet is a 'delegate', remove its delegate listener:
            if (facet.type == 'delegate') and (name[-6:] != '_items'):
                self._remove_facet_delegate_listener( name, facet, True )

            # Remove the facet value from the object dictionary as well:
            if name in self.__dict__:
                del self.__dict__[ name ]

            # Get the object's instance facet dictionary and remove the facet
            # from it:
            ifacet_dict = self._instance_facets()
            if name in ifacet_dict:
                del ifacet_dict[ name ]

                return True

        return False


    def facet ( self, name, force = False, copy = False ):
        """ Returns the facet definition for the *name* facet attribute.

            Parameters
            ----------
            name : string
                Name of the attribute whose facet definition is to be returned
            force : Boolean
                Indicates whether to return a facet definition if *name* is
                not explicitly defined
            copy : Boolean
                Indicates whether to return the original facet definition or a
                copy

            Description
            -----------
            If *force* is False (the default) and *name* is the name of an
            implicitly defined facet attribute that has never been referenced
            explicitly (i.e., has not yet been defined), the result is None. In
            all other cases, the result is the facet definition object
            associated with *name*.

            If *copy* is True, and a valid facet definition is found for *name*,
            a copy of the facet found is returned. In all other cases, the facet
            definition found is returned unmodified (the default).
        """
        mode = 0
        if force:
            mode = -1

        result = self._facet( name, mode )
        if (not copy) or (result is None):
            return result

        return  _clone_facet( result )


    def base_facet ( self, name ):
        """ Returns the base facet definition for a facet attribute.

            Parameters
            ----------
            name : string
                Name of the attribute whose facet definition is returned.

            Description
            -----------
            This method is similar to the facet() method, and returns a
            different result only in the case where the facet attribute defined
            by *name* is a delegate. In this case, the base_facet() method
            follows the delegation chain until a non-delegated facet attribute
            is reached, and returns the definition of that attribute's facet as
            the result.
        """
        return self._facet( name, -2 )


    def validate_facet ( self, name, value ):
        """ Validates whether a value is legal for a facet.

            Returns the validated value if it is valid.
        """
        return self.base_facet( name ).validate( self, name, value )


    def animated_facets ( self, *names, **kw ):
        """ Returns a list of all currently animated facets for the list of
            facets specified by *names* or for the entire object if no *names*
            are specified.

            If the *running* keyword argument is **True**, then only the
            animations currently running for the affected facets are returned.

            If *running* is **False** (the default), then all animations, either
            running or pending, for the affected facets are returned.
        """
        result   = []
        animated = self.__dict__.get( AnimatedFacets )
        if animated is not None:
            if len( names ) == 0:
                names = animated.iterkeys()

            if kw.get( 'running', False ):
                for name in names:
                    animations = animated.get( name )
                    if animations is not None:
                        result.append( animations[0] )
            else:
                for name in names:
                    animations = animated.get( name )
                    if animations is not None:
                        result.extend( animations )

        return result


    def halt_animated_facets ( self, *names, **kw ):
        """ Halts all current animations for the list of facets specified by
            *names* or for all facets if no *names* are specified.

            If the *flush* keyword argument is **True** (the default), then any
            pending animations for the affected facets are also discarded.

            If *flush* is **False**, then the currently running animations are
            simply halted, which allows any pending animations waiting for them
            to complete to be started.
        """
        if kw.get( 'flush', True ):
            animated = self.__dict__.get( AnimatedFacets )
            if animated is None:
                return

            if len( names ) == 0:
                names = animated.iterkeys()

            dummy_list = []
            for name in names:
                del animated.get( name, dummy_list )[1:]

        for item in self.animated_facets( running = True, *names ):
            item.halt()


    def animate_facet ( self, name    = Missing, time   = 1.0, end    = Missing,
                              begin   = Missing, repeat = 1,  reverse = True,
                              tweener = Missing, path   = Missing,
                              replace = False,   start  = True ):
        """ Animates a facet changing values over time.
        """
        from facets.animation.facet_animation import FacetAnimation

        if name is Missing:
            raise FacetError(
                'animate_facet: Must specify the name of the facet to be '
                'animated'
            )

        if start:
            if (end is Missing) and (begin is Missing):
                raise FacetError(
                    'animate_facet: Must specify at least a begin or end value'
                )

            if replace:
                self.halt_animated_facets( name )

        if end is Missing:
            end = getattr( self, name )

        animation = FacetAnimation(
            object  = self,
            name    = name,
            end     = end,
            time    = time,
            repeat  = repeat,
            reverse = reverse
        )

        if begin is not Missing:
            animation.begin = begin

        if path is Missing:
            value = getattr( self, name, None )
            if isinstance( value, int ):
                from facets.animation.linear_int_path import LinearInt

                path = LinearInt
            elif isinstance( value, float ):
                from facets.animation.path import Linear

                path = Linear
            elif isinstance( value, SequenceTypes ) and (len( value ) > 0):
                item = value[0]
                if isinstance( item, int ):
                    from facets.animation.linear_int_path import LinearInt
                    path = LinearInt
                elif isinstance( item, float ):
                    from facets.animation.path import Linear
                    path = Linear
            elif isinstance( value, basestring ):
                from facets.animation.text_path import Text

                path = Text

        if path is not Missing:
            animation.path = path

        if tweener is not Missing:
            animation.tweener = tweener

        if start:
            # We cache all of the currently running animations in a hidden item
            # dictionary whose keys are facet names and whose values are the
            # list of currently running or pending animations for the facet.
            # When an animation completes it is removed from the dictionary and
            # the next animation, if any, for the facet is started.
            animated = self.__dict__.get( AnimatedFacets )
            if animated is None:
                self.__dict__[ AnimatedFacets ] = animated = {}

            animated_facets = animated.get( name )
            if animated_facets is None:
                animation.on_facet_set( self._animate_facet_stopped, 'stopped' )
                animated[ name ] = [ animation ]
                animation.start = True
            else:
                animated_facets.append( animation )

        return animation


    def _animate_facet_stopped ( self, object ):
        """ Handles a facet animation completing.
        """
        animated = self.__dict__.get( AnimatedFacets )
        if animated is not None:
            animations = animated.get( object.name )
            if (animations is not None) and (animations[0] is object):
                del animations[0]
                if len( animations ) == 0:
                    del animated[ object.name ]
                    if len( animated ) == 0:
                        del self.__dict__[ AnimatedFacets ]
                else:
                    animation = animations[0]
                    animation.on_facet_set( self._animate_facet_stopped,
                                            'stopped' )
                    animation.start = True


    def facets ( self, **metadata ):
        """ Returns a dictionary containing the definitions of all of the facet
            attributes of this object that match the set of *metadata* criteria.

            Parameters
            ----------
            metadata : dictionary
                Criteria for selecting facet attributes

            Description
            -----------
            The keys of the returned dictionary are the facet attribute names,
            and the values are their corresponding facet definition objects.

            If no *metadata* information is specified, then all explicitly
            defined facet attributes defined for the object are returned.

            Otherwise, the *metadata* keyword dictionary is assumed to define a
            set of search criteria for selecting facet attributes of interest.
            The *metadata* dictionary keys correspond to the names of facet
            metadata attributes to examine, and the values correspond to the
            values the metadata attribute must have in order to be included in
            the search results.

            The *metadata* values either may be simple Python values like
            strings or integers, or may be lambda expressions or functions that
            return True if the facet attribute is to be included in the result.
            A lambda expression or function must receive a single argument,
            which is the value of the facet metadata attribute being tested. If
            more than one metadata keyword is specified, a facet attribute must
            match the metadata values of all keywords to be included in the
            result.
        """
        facets = self.__base_facets__.copy()
        for name in self.__dict__.keys():
            if name not in facets:
                facet = self.facet( name )
                if facet is not None:
                    facets[ name ] = facet

        if len( metadata ) == 0:
            return facets

        for meta_name, meta_eval in metadata.items():
            if type( meta_eval ) is not FunctionType:
                metadata[ meta_name ] = _SimpleTest( meta_eval )

        result = {}
        for name, facet in facets.iteritems():
            for meta_name, meta_eval in metadata.iteritems():
                if not meta_eval( getattr( facet, meta_name ) ):
                    break
            else:
                result[ name ] = facet

        return result


    @classmethod
    def class_facets ( cls, **metadata ):
        """ Returns a dictionary containing the definitions of all of the facet
            attributes of the class that match the set of *metadata* criteria.

            Parameters
            ----------
            metadata : dictionary
                Criteria for selecting facet attributes

            Description
            -----------
            The keys of the returned dictionary are the facet attribute names,
            and the values are their corresponding facet definition objects.

            If no *metadata* information is specified, then all explicitly
            defined facet attributes defined for the class are returned.

            Otherwise, the *metadata* keyword dictionary is assumed to define a
            set of search criteria for selecting facet attributes of interest.
            The *metadata* dictionary keys correspond to the names of facet
            metadata attributes to examine, and the values correspond to the
            values the metadata attribute must have in order to be included in
            the search results.

            The *metadata* values either may be simple Python values like
            strings or integers, or may be lambda expressions or functions that
            return **True** if the facet attribute is to be included in the
            result. A lambda expression or function must receive a single
            argument, which is the value of the facet metadata attribute being
            tested. If more than one metadata keyword is specified, a facet
            attribute must match the metadata values of all keywords to be
            included in the result.
        """
        if len( metadata ) == 0:
            return cls.__base_facets__.copy()

        result = {}

        for meta_name, meta_eval in metadata.items():
            if type( meta_eval ) is not FunctionType:
                metadata[ meta_name ] = _SimpleTest( meta_eval )

        for name, facet in cls.__base_facets__.iteritems():
            for meta_name, meta_eval in metadata.iteritems():
                if not meta_eval( getattr( facet, meta_name ) ):
                    break
            else:
                result[ name ] = facet

        return result


    def facet_names ( self, **metadata ):
        """ Returns a list of the names of all facet attributes whose
            definitions match the set of *metadata* criteria specified.

            Parameters
            ----------
            metadata : dictionary
                Criteria for selecting facet attributes

            Description
            -----------
            This method is similar to the facets() method, but returns only the
            names of the matching facet attributes, not the facet definitions.
        """
        return self.facets( **metadata ).keys()


    @classmethod
    def class_facet_names ( cls, **metadata ):
        """ Returns a list of the names of all facet attributes whose
            definitions match the set of *metadata* criteria specified.

            Parameters
            ----------
            metadata : dictionary
                Criteria for selecting facet attributes

            Description
            -----------
            This method is similar to the facets() method, but returns only the
            names of the matching facet attributes, not the facet definitions.
        """
        return cls.class_facets( **metadata ).keys()


    def _set_facets_cache ( self, name, value ):
        """ Explicitly sets the value of a cached property.
        """
        cached    = FacetsCache + name
        old_value = self.__dict__.get( cached, Undefined )
        self.__dict__[ cached ] = value
        if old_value != value:
            self.facet_property_set( name, old_value, value )


    def _flush_facets_cache ( self, name, value ):
        """ Explicitly flushes the value of a cached property.
        """
        self.facet_property_set(
            name, self.__dict__.pop( FacetsCache + name, Undefined ) )


    def __prefix_facet__ ( self, name, is_set ):
        """ Returns the facet definition for a specified name when there is no
            explicit definition in the class.
        """
        # Check to see if the name is of the form '__xxx__':
        if (name[:2] == '__') and (name[-2:] == '__'):
            if name == '__class__':
                return generic_facet

            # If this is for purposes of performing a 'setattr', always map the
            # name to an 'Any' facet:
            if is_set:
                return any_facet

            # Otherwise, it is a 'getattr' request, so indicate that no such
            # attribute exists:
            raise AttributeError(
                "'%s' object has no attribute '%s'" %
                ( self.__class__.__name__, name )
            )

        # Handle the special case of 'delegated' facets:
        if name[-1:] == '_':
            facet = self._facet( name[:-1], 0 )
            if (facet is not None) and (facet.type == 'delegate'):
                return _clone_facet( facet )

        prefix_facets = self.__prefix_facets__
        for prefix in prefix_facets['*']:
            if prefix == name[ : len( prefix ) ]:
                # If we found a match, use its facet as a template for a new
                # facet:
                facet = prefix_facets[ prefix ]

                # Get any change notifiers that apply to the facet:
                cls      = self.__class__
                handlers = _non_none( _get_method( cls, '_%s_set' % name ) )

                # Add any special facet defined event handlers:
                _add_event_handlers( facet, cls, handlers )

                # Add the 'anyfacet' handler (if any):
                handlers.extend( prefix_facets.get( '@', EmptyList ) )

                # If there are any handlers, add them to the facet's notifier's
                # list:
                if len( handlers ) > 0:
                    facet = _clone_facet( facet )
                    _add_notifiers( facet._notifiers( 1 ), handlers )

                return facet

        # There should ALWAYS be a prefix match in the facet classes, since ''
        # is at the end of the list, so we should never get here:
        raise SystemError(
            ("Facet class look-up failed for attribute '%s' for an object of "
             "type '%s'") %
            ( name, self.__class__.__name__ )
        )


    def add_facet_listener ( self, object, prefix = '' ):
        self._facet_listener( object, prefix, False )


    def remove_facet_listener ( self, object, prefix = '' ):
        self._facet_listener( object, prefix, True )


    def _facet_listener ( self, object, prefix, remove ):
        if prefix[-1:] != '_':
            prefix += '_'

        n      = len( prefix )
        facets = self.__base_facets__
        for name in self._each_facet_method( object ):
            if name[ :n ] == prefix:
                if name[-8:] == '_set':
                    short_name = name[ n: -8 ]
                    if short_name in facets:
                        self._on_facet_set( getattr( object, name ),
                                            short_name, remove = remove )
                    elif short_name == 'anyfacet':
                        self._on_facet_set( getattr( object, name ),
                                            remove = remove )


    def _each_facet_method ( self, object ):
        """ Generates each (name, method) pair for a specified object.
        """
        dic = {}
        for klass in object.__class__.__mro__:
            for name, method in klass.__dict__.iteritems():
                if (type( method ) is FunctionType) and (name not in dic):
                    dic[ name ] = True

                    yield name


    def _instance_changed_handler ( self, facet, old, new ):
        """ Handles adding/removing listeners for a generic 'Instance' facet.
        """
        arg_lists = self._get_instance_handlers( facet )

        if old is not None:
            for args in arg_lists:
                old.on_facet_set( remove = True, *args )

        if new is not None:
            for args in arg_lists:
                new.on_facet_set( *args )


    def _list_changed_handler ( self, facet, old, new ):
        """ Handles adding/removing listeners for a generic 'List( Instance )'
            facet.
        """
        arg_lists = self._get_instance_handlers( facet )

        for item in old:
            for args in arg_lists:
                item.on_facet_set( remove = True, *args )

        for item in new:
            for args in arg_lists:
                item.on_facet_set( *args )


    def _list_items_changed_handler ( self, facet, event ):
        """ Handles adding/removing listeners for a generic 'List( Instance )'
            facet.
        """
        arg_lists = self._get_instance_handlers( facet[:-6] )

        for item in event.removed:
            for args in arg_lists:
                item.on_facet_set( remove = True, *args )

        for item in event.added:
            for args in arg_lists:
                item.on_facet_set( *args )


    def _get_instance_handlers ( self, name ):
        """ Returns a list of ( name, method ) pairs for a specified 'Instance'
            or 'List( Instance )' facet name:
        """
        return [ ( getattr( self, method_name ), item_name )
                 for method_name, item_name in
                     self.__class__.__instance_facets__[ name ] ]


    def _post_init_facet_listeners ( self ):
        """ Performs any post-initialization listener set-up.
        """
        for kind, name, listener in self.__class__.__listener_facets__[1]:
            getattr( self, '_post_init_facet_%s_listener' % kind )( name,
                                                                    listener )


    def _post_init_facet_method_listener ( self, name, listener ):
        """ Sets up the listener for a method with the @on_facet_set decorator.
        """
        listener.clone().set(
            wrapped_handler = listener.wrapper_class( getattr( self, name ) )
        ).register_static( self )


    def _init_facet_listeners ( self ):
        """ Performs any pre-initialization listener set-up.
        """
        for kind, name, listener in self.__class__.__listener_facets__[0]:
            getattr( self, '_init_facet_%s_listener' % kind )( name, listener )


    def _init_facet_method_listener ( self, name, listener ):
        """ Sets up the listener for a method with the @on_facet_set decorator.
        """
        listener.clone().set(
            wrapped_handler = listener.wrapper_class( getattr( self, name ) ),
            deferred        = True
        ).register_static( self )


    def _init_facet_event_listener ( self, name, listener ):
        """ Sets up the listener for an event with 'on_facet_set' metadata.
        """
        def notify ( ):
            setattr( self, name, True )

        listener.clone().set(
            wrapped_handler = listener.wrapper_class( notify )
        ).register_static( self )


    def _init_facet_property_listener ( self, name, listener ):
        """ Sets up the listener for a property with 'depends_on' metadata.
        """
        cached = listener._cached
        if cached is None:
            def post_notify ( ):
                self.facet_property_set( name, None )

            listener.clone().set(
                wrapped_handler = listener.wrapper_class( post_notify )
            ).register_static( self )

            return

        cached_old = cached + ':old'

        def pre_notify ( ):
            dict = self.__dict__
            old  = dict.get( cached_old, Undefined )
            if old is Undefined:
                dict[ cached_old ] = dict.pop( cached, None )

        listener.clone().set(
            wrapped_handler = listener.wrapper_class( pre_notify ),
            priority        = True
        ).register_static( self )

        def post_notify ( ):
            old = self.__dict__.pop( cached_old, Undefined )
            if old is not Undefined:
                self.facet_property_set( name, old )

        listener.clone().set(
            wrapped_handler = listener.wrapper_class( post_notify )
        ).register_static( self )


    def _init_facet_delegate_listener ( self, name, listener ):
        """ Sets up the listener for a delegate facet.
        """
        df       = self.__dict__.setdefault( DelegateFacets, {} )
        notifier = df.setdefault( name, DelegateNotifier( self, name ) )
        self.__dict__.setdefault( ListenerFacets, {} )[ name ] = listener = \
            listener.clone()
        listener.set(
            wrapped_handler = listener.wrapper_class( notifier.notify )
        ).register( self )


    def _remove_facet_delegate_listener ( self, name, facet, remove ):
        """ Removes a delegate listener when the local delegate value is set.

            Note: This code is called directly from cfacets.c when a delegate
            facet has its local value set or deleted and the facet does not
            modify its delegate...
        """
        if remove:
            # Although the name should be in the dict, it may not be if a value
            # was assigned to a delegate in a constructor or setstate:
            dict = self.__dict__.get( ListenerFacets )
            if dict is not None:
                listener = dict.get( name )
                if listener is not None:
                    listener.unregister( self )
                    del dict[ name ]
                    if len( dict ) == 0:
                        del self.__dict__[ ListenerFacets ]

                    dict = self.__dict__[ DelegateFacets ]
                    del dict[ name ]
                    if len( dict ) == 0:
                        del self.__dict__[ DelegateFacets ]

            return

        # Otherwise the local copy of the delegate value was deleted, restore
        # the delegate listener (unless it's already there):
        dict = self.__dict__.setdefault( ListenerFacets, {} )
        if name not in dict:
            self._init_facet_delegate_listener( name, facet._dynamic[1] )

# Patch the definition of _HasFacets to be the real 'HasFacets':
_HasFacets = HasFacets

#-------------------------------------------------------------------------------
#  'HasStrictFacets' class:
#-------------------------------------------------------------------------------

class HasStrictFacets ( HasFacets ):
    """ This class guarantees that any object attribute that does not have an
        explicit or wildcard facet definition results in an exception.

        This feature can be useful in cases where a more rigorous software
        engineering approach is being used than is typical for Python programs.
        It also helps prevent typos and spelling mistakes in attribute names
        from going unnoticed; a misspelled attribute name typically causes an
        exception.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Disallow access to any facets not explicitly defined:
    _ = Disallow

#-------------------------------------------------------------------------------
#  'HasPrivateFacets' class:
#-------------------------------------------------------------------------------

class HasPrivateFacets ( HasFacets ):
    """ This class ensures that any public object attribute that does not have
        an explicit or wildcard facet definition results in an exception, but
        "private" attributes (whose names start with '_') have an initial value
        of **None**, and are not type-checked.

        This feature is useful in cases where a class needs private attributes
        to keep track of its internal object state, which are not part of the
        class's public API. Such attributes do not need to be type-checked,
        because they are manipulated only by the (presumably correct) methods
        of the class itself.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Make 'private' facets (leading '_') have no type checking:
    __ = Any( private = True, transient = True )

    # Disallow access to all other facets not explicitly defined:
    _  = Disallow

#-------------------------------------------------------------------------------
#  Singleton classes with facets:
#
#  This code is based on a recipe taken from:
#      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531
#  Specifically, the implementation of Oren Tirosh is used.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  'SingletonHasFacets' class:
#-------------------------------------------------------------------------------

class SingletonHasFacets ( HasFacets ):
    """ Singleton class that support facet attributes.
    """

    #-- Public Methods ---------------------------------------------------------

    def __new__ ( cls, *args, **facets ):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = HasFacets.__new__( cls, *args, **facets )

        return cls._the_instance

#-------------------------------------------------------------------------------
#  'SingletonHasStrictFacets' class:
#-------------------------------------------------------------------------------

class SingletonHasStrictFacets ( HasStrictFacets ):
    """ Singleton class that supports strict facet attributes.

        Non-facet attributes generate an exception.
    """

    #-- Public Methods ---------------------------------------------------------

    def __new__ ( cls, *args, **facets ):
        return SingletonHasFacets.__new__( cls, *args, **facets )

#-------------------------------------------------------------------------------
#  'SingletonHasPrivateFacets' class:
#-------------------------------------------------------------------------------

class SingletonHasPrivateFacets ( HasPrivateFacets ):
    """ Singleton class that supports facet attributes, with private attributes
        being unchecked.
    """

    #-- Public Methods ---------------------------------------------------------

    def __new__ ( cls, *args, **facets ):
        return SingletonHasFacets.__new__( cls, *args, **facets )

#-------------------------------------------------------------------------------
#  'Vetoable' class:
#-------------------------------------------------------------------------------

class Vetoable ( HasStrictFacets ):
    """ Defines a 'vetoable' request object and an associated event.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Should the request be vetoed? (Can only be set to 'True')
    veto = Bool( False )

    #-- Facet Event Handlers ---------------------------------------------------

    def _veto_set ( self, state ):
        self._facet_veto_notify( state )

VetoableEvent = Event( Vetoable )

#-------------------------------------------------------------------------------
#  'Interface' class:
#-------------------------------------------------------------------------------

class Interface ( HasFacets ):
    """ The base class for all interfaces.
    """

    __metaclass__ = MetaInterface

# Patch the Interface definition in has_types.py (circular reference problem):
facet_types.Interface = Interface

#-------------------------------------------------------------------------------
#  'ISerializable' interface:
#-------------------------------------------------------------------------------

class ISerializable ( Interface ):
    """ A class that implemented ISerializable requires that all HasFacets
        objects saved as part of its state also implement ISerializable.
    """

#-------------------------------------------------------------------------------
#  'EventLoopListener' class:
#-------------------------------------------------------------------------------

class EventLoopListener ( HasFacets ):
    """ Suspends the caller until one of a list of specified facets is modified
        on a specified object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The object whose facets are being monitored:
    object = Instance( HasFacets )

    # The facets being monitored for change:
    facets = Str

    # The CFacetNotification object for the facet that changed:
    notify = Any

    #-- Public Methods ---------------------------------------------------------

    def wait ( self ):
        """ Creates a new event loop (suspending the caller) until one of the
            specified 'facets' on 'object' is changed. It returns the
            notification object for the facet that changed value.
        """
        from facets.ui.toolkit import toolkit

        self.object.on_facet_set( self._facet_modified, self.facets )
        toolkit().event_loop()
        notify, self.object, self.notify = self.notify, None, None

        return notify

    #-- Private Methods --------------------------------------------------------

    def _facet_modified ( self, object, facet, old, new ):
        """ Handles any of the specified facets being changed.
        """
        from facets.ui.toolkit import toolkit
        from cfacets           import CFacetNotification

        self.notify = CFacetNotification( 0, object, facet, new, old )
        self.object.on_facet_set( self._facet_modified, self.facets,
                                  remove = True )
        toolkit().event_loop( 0 )

#-------------------------------------------------------------------------------
#  'facets_super' class:
#-------------------------------------------------------------------------------

class facets_super ( super ):

    #-- Public Methods ---------------------------------------------------------

    def __getattribute__ ( self, name ):
        try:
            return super( facets_super, self ).__getattribute__( name )
        except:
            return self._noop


    def _noop ( self, *args, **kw ):
        pass

#-- EOF ------------------------------------------------------------------------