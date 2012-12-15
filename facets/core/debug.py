"""
Defines the singleton Debug class which provides a number of useful abstract
debugging API's with pluggable back-end implementations.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core.facet_types \
    import Str, Bool, Enum, Event

from facets.core.has_facets \
    import SingletonHasPrivateFacets

from facets.core.facet_base \
    import Missing

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# The current level of log event being processed:
DebugLevel = Enum( 'debug', 'info', 'warning', 'error', 'critical' )

#-------------------------------------------------------------------------------
#  Debug Class:
#-------------------------------------------------------------------------------

class Debug ( SingletonHasPrivateFacets ):
    """ Defines the singleton Debug class which provides a number of useful
        abstract debugging API's with pluggable back-end implementations.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the 'debug' method enabled?
    debug_enabled = Bool( True )

    # Is the 'info' method enabled?
    info_enabled = Bool( True )

    # Is the 'warning' method enabled?
    warning_enabled = Bool( True )

    # Is the 'error' method enabled?
    error_enabled = Bool( True )

    # Is the 'critical' method enabled?
    critical_enabled = Bool( True )

    # Is the 'called_from' method enabled?
    called_from_enabled = Bool( True )

    # Is the 'show_locals' method enabled?
    show_locals_enabled = Bool( True )

    # The current level of log event being processed:
    level = DebugLevel

    # The label associated with an object being logged:
    label = Str

    # Event fired when an object is logged:
    object = Event

    # A 'called_from' stack event:
    stack = Event

    # A 'locals' caller stack event:
    caller = Event

    #-- Public Methods ---------------------------------------------------------

    def called_from ( self, levels = 1, context = 1 ):
        """ Displays where the call is being made from.
        """
        if self.called_from_enabled:
            from inspect import stack

            self.stack = stack( context )[ 1: levels + 2 ]


    def show_locals ( self ):
        """ Displays the caller's local variables.
        """
        if self.show_locals_enabled:
            from inspect import stack

            self.caller = stack()[1]


    def log ( self, level, msg, object = Missing ):
        """ Prints a string message to standard out or logs an object to the
            'object' facet.
        """
        if getattr( self, level + '_enabled', False ):
            if isinstance( msg, basestring ):
                if object is Missing:
                    print '%s: msg' % ( level.upper(), msg )

                    return
            else:
                msg, object = '', msg

            self.level  = level
            self.label  = msg
            self.object = object


    def debug ( self, msg, object = Missing ):
        """ Prints a debug message to standard out or logs an object to the
            'object' facet.
        """
        self.log( 'debug', msg, object )


    def info ( self, msg, object = Missing ):
        """ Prints an info message to standard out or logs an object to the
            'object' facet.
        """
        self.log( 'info', msg, object )


    def warning ( self, msg, object = Missing ):
        """ Prints a warning message to standard out or logs an object to the
            'object' facet.
        """
        self.log( 'warning', msg, object )


    def error ( self, msg, object = Missing ):
        """ Prints an error message to standard out or logs an object to the
            'object' facet.
        """
        self.log( 'error', msg, object )


    def critical ( self, msg, object = Missing ):
        """ Prints a critical message to standard out or logs an object to the
            'object' facet.
        """
        self.log( 'critical', msg, object )

#-------------------------------------------------------------------------------
#  Convenience Definitions:
#-------------------------------------------------------------------------------

# Expose the debug methods as if they were simple functions:
debug       = Debug()
info        = debug.info
warning     = debug.warning
error       = debug.error
critical    = debug.critical
log         = debug.log
called_from = debug.called_from
show_locals = debug.show_locals
debug       = debug.debug    # This replaces the temporary definition of 'debug'

#-- EOF ------------------------------------------------------------------------
