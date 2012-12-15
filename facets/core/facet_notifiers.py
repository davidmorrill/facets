"""
Defines the classes needed to implement and support the Facets change
notification mechanism.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import weakref
import traceback
import sys

try:
    # Requires Python version >= 2.4:
    from threading import local as thread_local
except:
    thread_local = lambda: {}

from threading \
    import Thread

from thread \
    import get_ident

from types \
    import MethodType

from facet_base \
    import Uninitialized

from facet_errors \
    import FacetNotificationError

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The name of the dictionary used to store active listeners:
FacetsListener = '__facets_listener__'

# Mapping from standard facet event handler argument names to *args index:
ARG_NONE   = 0    # Function has no arguments
ARG_VALUE  = 1    # Function has 'old', 'new' type arguments
ARG_SOURCE = 2    # Function has 'object', 'facet', 'notify' type arguments
ARG_BOTH   = ARG_VALUE | ARG_SOURCE

ArgNameToTypeIndex = {
    'self':    ( ARG_NONE,   0 ),
    'object':  ( ARG_SOURCE, 0 ),
    'facet':   ( ARG_SOURCE, 1 ),
    'old':     ( ARG_VALUE,  2 ),
    'removed': ( ARG_VALUE,  2 ),
    'new':     ( ARG_VALUE,  3 ),
    'added':   ( ARG_VALUE,  3 ),
    'notify':  ( ARG_SOURCE, 4 )
}

DefaultTypeIndex = ( ARG_VALUE, 3 )

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# The thread ID for the user interface thread
ui_thread = -1

# The handler for notifications that must be run on the UI thread
ui_handler = None

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def set_ui_handler ( handler ):
    """ Sets up the user interface thread handler.
    """
    global ui_handler, ui_thread

    ui_handler = handler
    ui_thread  = get_ident()


def indices_for ( func, start_index ):
    """ Returns a tuple of the form: ( types, [ index, ... ] ) where 'types' is
        the logical or'ed value of the type of each function argument, and each
        'index' is the argument index for a standard event dispatch call that
        each argument to *func* maps to.
    """

    types     = ARG_NONE
    indices   = []
    var_names = func.func_code.co_varnames
    for i in xrange( start_index, func.func_code.co_argcount ):
         type, index = ArgNameToTypeIndex.get( var_names[ i ],
                                               DefaultTypeIndex )
         types |= type
         indices.append( index )

    return ( types, indices )


undefined_handler = lambda: Undefined

#-------------------------------------------------------------------------------
#  'NotificationExceptionHandlerState' class:
#-------------------------------------------------------------------------------

class NotificationExceptionHandlerState ( object ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, handler, reraise_exceptions, locked ):
        """ Initializes the object.
        """
        self.handler            = handler
        self.reraise_exceptions = reraise_exceptions
        self.locked             = locked

#-------------------------------------------------------------------------------
#  'NotificationExceptionHandler' class:
#-------------------------------------------------------------------------------

class NotificationExceptionHandler ( object ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self ):
        """ Initializes the object.
        """
        self.facets_logger = None
        self.main_thread   = None
        self.thread_local  = thread_local()

    #-- Private Methods --------------------------------------------------------

    def _push_handler ( self, handler = None, reraise_exceptions = False,
                              main = False, locked = False ):
        """ Pushes a new facets notification exception handler onto the stack,
            making it the new exception handler. Returns a
            NotificationExceptionHandlerState object describing the previous
            exception handler.

            Parameters
            ----------
            handler : handler
                The new exception handler, which should be a callable or
                None. If None (the default), then the default facets
                notification exception handler is used. If *handler* is not
                None, then it must be a callable which can accept four
                arguments: object, facet_name, old_value, new_value.
            reraise_exceptions : Boolean
                Indicates whether exceptions should be reraised after the
                exception handler has executed. If True, exceptions will be
                re-raised after the specified handler has been executed.
                The default value is False.
            main : Boolean
                Indicates whether the caller represents the main application
                thread. If True, then the caller's exception handler is
                made the default handler for any other threads that are
                created. Note that a thread can explictly set its own exception
                handler if desired. The *main* flag is provided to make it
                easier to set a global application policy without having to
                explicitly set it for each thread. The default value is
                False.
            locked : Boolean
                Indicates whether further changes to the Facets notification
                exception handler state should be allowed. If True, then
                any subsequent calls to _push_handler() or _pop_handler() for
                that thread will raise a FacetNotificationError. The default
                value is False.
        """
        handlers = self._get_handlers()
        self._check_lock( handlers )
        if handler is None:
            handler = self._log_exception

        handlers.append( NotificationExceptionHandlerState(
            handler, reraise_exceptions, locked
        ) )
        if main:
            self.main_thread = handlers

        return handlers[-2]


    def _pop_handler ( self, key = None ):
        """ Pops the facets notification exception handler stack, restoring
            the exception handler in effect prior to the most recent
            _push_handler() call. If the stack is empty, a
            FacetNotificationError exception is raised. If the stack is locked,
            a FacetNotificationError is also raised unless *key* matches the
            value return by the _push_handler() called that locked the handler
            stack.

            Note that each thread has its own independent stack. See the
            description of the _push_handler() method for more information on
            this.
        """
        handlers = self._get_handlers()
        self._check_lock( handlers, key )
        if len( handlers ) > 1:
            handlers.pop()
        else:
            raise FacetNotificationError(
                'Attempted to pop an empty facets notification exception '
                'handler stack.'
            )


    def _handle_exception ( self, object, facet_name, old, new, notify ):
        """ Handles a facets notification exception using the handler defined
            by the topmost stack entry for the corresponding thread.
        """
        excp_class, excp = sys.exc_info()[:2]
        handler_info     = self._get_handlers()[-1]
        handler_info.handler( object, facet_name, old, new, notify )
        if (handler_info.reraise_exceptions or
            isinstance( excp, FacetNotificationError )):
            raise


    def _get_handlers ( self ):
        """ Returns the handler stack associated with the currently executing
            thread.
        """
        thread_local = self.thread_local
        if isinstance( thread_local, dict ):
            id       = get_ident()
            handlers = thread_local.get( id )
        else:
            handlers = getattr( thread_local, 'handlers', None )

        if handlers is None:
            if self.main_thread is not None:
                handler = self.main_thread[-1]
            else:
                handler = NotificationExceptionHandlerState(
                    self._log_exception, False, False
                )

            handlers = [ handler ]
            if isinstance( thread_local, dict ):
                thread_local[ id ] = handlers
            else:
                thread_local.handlers = handlers

        return handlers


    def _check_lock ( self, handlers, key = None ):
        """ Raises an exception if the specified handler stack is locked.
        """
        if (handlers[-1].locked and
            ((len( handlers ) < 2) or (key is not handlers[-2]))):
            raise FacetNotificationError(
                'The facets notification exception handler is locked. No '
                'changes are allowed.'
            )


    def _log_exception ( self, object, facet_name, old, new, notify ):
        """ This method defines the default notification exception handling
            behavior of facets. However, it can be completely overridden by
            pushing a new handler using the '_push_handler' method.

            It logs any exceptions generated in a facet notification handler.
        """
        # When the stack depth is too great, the logger can't always log the
        # message. Make sure that it goes to the console at a minimum:
        excp_class, excp = sys.exc_info()[:2]
        if ((excp_class is RuntimeError) and
            (excp.args[0] == 'maximum recursion depth exceeded')):
            sys.__stderr__.write(
                'Exception occurred in facets notification handler for object: '
                '%s, facet: %s, old value: %s, new value: %s.\n%s\n' % (
                object, facet_name, old, new,
                ''.join( traceback.format_exception( *sys.exc_info() ) ) )
            )

        logger = self.facets_logger
        if logger is None:
            import logging

            self.facets_logger = logger = logging.getLogger( 'facets.core' )
            handler = logging.StreamHandler()
            handler.setFormatter( logging.Formatter( '%(message)s' ) )
            logger.addHandler( handler )
            print ('Exception occurred in facets notification handler.\n'
                   'Please check the log file for details.')

        try:
            logger.exception(
                'Exception occurred in facets notification handler for '
                'object: %s, facet: %s, old value: %s, new value: %s' %
                ( object, facet_name, old, new )
            )
        except Exception:
            # Ignore anything we can't log the above way:
            pass

#-------------------------------------------------------------------------------
#  Facets global notification exception handler:
#-------------------------------------------------------------------------------

notification_exception_handler = NotificationExceptionHandler()

push_exception_handler = notification_exception_handler._push_handler
pop_exception_handler  = notification_exception_handler._pop_handler
handle_exception       = notification_exception_handler._handle_exception

#-------------------------------------------------------------------------------
#  'StaticFacetSetWrapper' class:
#-------------------------------------------------------------------------------

class StaticFacetSetWrapper:

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, handler ):
        """ Initializes the object.
        """
        self.handler                 = handler
        self.arg_types, self.indices = indices_for( handler, 0 )


    def equals ( self, handler ):
        return False


    def __call__ ( self, *args ):
        if args[2] is not Uninitialized:
            try:
                self.handler( *[ args[ i ] for i in self.indices ] )
            except:
                handle_exception( *args )

#-------------------------------------------------------------------------------
#  'FacetSetWrapper' class:
#-------------------------------------------------------------------------------

class FacetSetWrapper:

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, handler, owner ):
        """ Initializes the object.
        """
        self.init( handler, owner )


    def init ( self, handler, owner ):
        if type( handler ) is MethodType:
            func   = handler.im_func
            object = handler.im_self
            if object is not None:
                if owner is None:
                    self.object = weakref.ref( object )
                else:
                    self.object = weakref.ref( object, self.listener_deleted )
                    self.owner  = owner

                self.name                    = handler.__name__
                self.notifier                = self.bound_handler
                self.arg_types, self.indices = indices_for( func, 1 )

                return

        self.object   = 1     # Dummy object so __call__ method won't abort
        self.name     = None  # Dummy name for equal method
        self.notifier = lambda: handler
        self.arg_types, self.indices = indices_for( handler, 0 )


    def bound_handler ( self ):
        """ Returns a bound handler method.
        """
        object = self.object()

        return (None if object is None else getattr( object, self.name ))


    # NOTE: This method is normally the only one that needs to be overridden in
    # a subclass to implement the subclass's dispatch mechanism:
    def dispatch ( self, *args ):
        self.notifier()( *args )


    def equals ( self, handler ):
        if handler is self:
            return True

        if (type( handler ) is MethodType) and (handler.im_self is not None):
            return ((handler.__name__ == self.name) and
                    (handler.im_self is self.object()))

        return ((self.name is None) and (handler == self.notifier()))


    def listener_deleted ( self, ref ):
        self.owner.remove( self )
        self.object   = self.owner = None
        self.notifier = undefined_handler


    def dispose ( self ):
        self.object = None


    def __call__ ( self, *args ):
        if (self.object is not None) and (args[2] is not Uninitialized):
            try:
                self.dispatch( *[ args[ i ] for i in self.indices ] )
            except:
                handle_exception( *args )

#-------------------------------------------------------------------------------
#  'ExtendedFacetSetWrapper' class:
#-------------------------------------------------------------------------------

class ExtendedFacetSetWrapper ( FacetSetWrapper ):

    def __call__ ( self, *args ):
        if self.object is not None:
            try:
                self.dispatch( *[ args[ i ] for i in self.indices ] )
            except:
                handle_exception( *args )

#-------------------------------------------------------------------------------
#  'FastUIFacetSetWrapper' class:
#-------------------------------------------------------------------------------

class FastUIFacetSetWrapper ( FacetSetWrapper ):

    #-- Public Methods ---------------------------------------------------------

    def dispatch ( self, *args ):
        if get_ident() == ui_thread:
            self.notifier()( *args )
        else:
            ui_handler( self.notifier(), *args )

#-------------------------------------------------------------------------------
#  'UIFacetSetWrapper' class:
#-------------------------------------------------------------------------------

class UIFacetSetWrapper ( FacetSetWrapper ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, handler, owner ):
        self.init( handler, owner )
        self.deferred = None


    def __call__ ( self, *args ):
        if ((self.object is not None)      and
            (args[2] is not Uninitialized) and
            (self.deferred is None)):
            self.deferred = args
            ui_handler( self.dispatch, self.deferred )


    def dispatch ( self, deferred ):
        self.deferred = None
        if self.object is not None:
            try:
                self.handler( *[ deferred[ i ] for i in self.indices ] )
            except:
                handle_exception( *deferred )

#-------------------------------------------------------------------------------
#  'NewFacetSetWrapper' class:
#-------------------------------------------------------------------------------

class NewFacetSetWrapper ( FacetSetWrapper ):

    #-- Public Methods ---------------------------------------------------------

    def dispatch ( self, *args ):
        Thread( target = self.notifier(), args = args ).start()

#-------------------------------------------------------------------------------
#  'ListenerSetWrapper' class:
#-------------------------------------------------------------------------------

class ListenerSetWrapper ( FacetSetWrapper ):

    #-- FacetSetWrapper Method Overrides ---------------------------------------

    def __init__ ( self, handler, owner = None, id = None, listener = None ):
        """ Initializes the object.
        """
        if owner is not None:
            owner = weakref.ref( owner, self.owner_deleted )

        self.init( handler, owner )
        self.id       = id
        self.listener = listener


    def listener_deleted ( self, ref ):
        owner = self.owner()
        if owner is not None:
            dict      = owner.__dict__.get( FacetsListener )
            listeners = dict.get( self.id )
            listeners.remove( self )
            if len( listeners ) == 0:
                del dict[ self.id ]
                if len( dict ) == 0:
                    del owner.__dict__[ FacetsListener ]

                # fixme: Is the following line necessary, since all registered
                # notifiers should be getting the same 'listener_deleted' call:
                self.listener.unregister( owner )

        self.object = self.owner = self.listener = None


    def owner_deleted ( self, ref ):
        self.object = self.owner = None

#-- EOF ------------------------------------------------------------------------