"""
Defines the standard exceptions raised by the Facets package.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import exceptions

from facet_base \
    import class_of

#-------------------------------------------------------------------------------
#  'FacetError' class:
#-------------------------------------------------------------------------------

class FacetError ( exceptions.Exception ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, args = None, name = None, info = None, value = None ):
        if name is None:
            # If the given args is not a tuple then assume that the user
            # intended it to be the single item in a one-element tuple.
            if not isinstance( args, tuple ):
                args = args,

            self.args = args
        else:
            # Save the information, in case the 'args' object is not the correct
            # one, and we need to regenerate the message later:
            self.name   = name
            self.info   = info
            self.value  = value
            self.desc   = None
            self.prefix = 'The'
            self.set_desc( None, args )


    def set_desc ( self, desc, object = None ):
        if hasattr( self, 'desc' ):
            if desc is not None:
                self.desc = desc

            if object is not None:
                self.object = object

            self.set_args()


    def set_prefix ( self, prefix ):
        if hasattr( self, 'prefix' ):
            self.prefix = prefix
            self.set_args()


    def set_args ( self ):
        if self.desc is None:
            extra = ''
        else:
            extra = ' specifies %s and' % self.desc

        obj = getattr( self, 'object', None )

        # Note: self.args must be a tuple so be sure to leave the trailing
        # commas.
        if obj is not None:
            self.args = ( "%s '%s' facet of %s instance%s must be %s, "
                          "but a value of %s was specified." % (
                          self.prefix, self.name, class_of( obj ), extra,
                          self.info, self.value ) ),
        else:
            self.args = ( "%s '%s' facet%s must be %s, but a value of %s was "
                          "specified." % ( self.prefix, self.name, extra,
                                           self.info, self.value ) ),

#-------------------------------------------------------------------------------
#  'FacetNotificationError' class:
#-------------------------------------------------------------------------------

class FacetNotificationError ( exceptions.Exception ):

    pass

#-------------------------------------------------------------------------------
#  'DelegationError' class:
#-------------------------------------------------------------------------------

class DelegationError ( FacetError ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, args ):
        """ Initializes the object.
        """
        # 'args' must be a tuple:
        self.args = args,

#-------------------------------------------------------------------------------
#  Export the defined exceptions to the C-base facets module:
#-------------------------------------------------------------------------------

import cfacets
cfacets._exceptions( FacetError, DelegationError )

#-- EOF ------------------------------------------------------------------------