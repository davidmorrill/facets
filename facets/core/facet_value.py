"""
Defines the FacetValue class, used for creating special, dynamic facet values.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facet_base \
    import Undefined

from facet_defs \
    import CFacet

from has_facets \
    import HasFacets, HasPrivateFacets

from facet_errors \
    import FacetError

from facet_types \
    import Tuple, Dict, Any, Str, Instance, Event, Callable

from facet_handlers \
    import FacetType, _read_only, _write_only, _arg_count

#-------------------------------------------------------------------------------
#  'BaseFacetValue' class:
#-------------------------------------------------------------------------------

class BaseFacetValue ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # Subclasses can define this facet as a property:
    # value = Property

    #-- Public Methods ---------------------------------------------------------

    def as_cfacet ( self, original_facet ):
        """ Returns the low-level C-based facet for this FacetValue.
        """
        notifiers = original_facet._notifiers( 0 )

        if self._cfacet is not None:
            if (notifiers is None) or (len( notifiers ) == 0):
                return self._cfacet

            facet = CFacet( 0 )
            facet.clone( self._cfacet )
        else:
            facet = self._as_cfacet( original_facet )

        if ((facet     is not None) and
            (notifiers is not None) and
            (len( notifiers ) > 0)):
            facet._notifiers( 1 ).extend( notifiers )

        return facet

    #-- Private Methods --------------------------------------------------------

    def _as_cfacet ( self, original_facet ):
        """ Returns the low-level C-based facet for this FacetValue.
        """
        value_facet = self.facet( 'value' )
        if value_facet is None:
            return None

        if value_facet.type != 'property':
            raise FacetError( 'Invalid FacetValue specified.' )

        metadata = {
            'type':         'property',
            '_facet_value': self
        }

        getter, setter, validate = value_facet.property()
        read_only = (getter is _read_only)
        if not read_only:
            getter = self._getter
            metadata[ 'transient' ] =  True

        if setter is not _write_only:
            if read_only:
                setter = self._read_only_setter
            else:
                setter = self._setter

            metadata[ 'transient' ] =  True

        return self._property_facet( getter, setter, validate, metadata )


    def _property_facet ( self, getter, setter, validate, metadata ):
        """ Returns a properly constructed 'property' facet.
        """
        n = 0
        if validate is not None:
            n = _arg_count( validate )

        facet = CFacet( 4 )
        facet.property(
            getter,   _arg_count( getter ),
            setter,   _arg_count( setter ),
            validate, n
        )

        facet.value_allowed(  True )
        facet.value_property( True )
        facet.__dict__ = metadata

        return facet


    def _getter ( self, object, name ):
        return self.value


    def _setter ( self, object, name, value ):
        old_value  = self.value
        self.value = value
        new_value  = self.value
        if new_value != old_value:
            object.facet_property_set( name, old_value, new_value )


    def _read_only_setter ( self, object, name, value ):
        self.value = value
        object.facet_property_set( name, Undefined, value )

#-------------------------------------------------------------------------------
#  'FacetValue' class:
#-------------------------------------------------------------------------------

class FacetValue ( BaseFacetValue ):

    #-- Facet Definitions ------------------------------------------------------

    # The callable used to define a default value:
    default = Callable

    # The positional arguments to pass to the callable default value:
    args = Tuple

    # The keyword arguments to pass to the callable default value:
    kw = Dict

    # The facet to use as the new facet type:
    type = Any

    # The object to delegate the new value to:
    delegate = Instance( HasFacets )

    # The name of the facet on the delegate object to get the new value from:
    name = Str

    #-- Private Methods --------------------------------------------------------

    def _as_cfacet ( self, original_facet ):
        """ Returns the low-level C-based facet for this FacetValue.
        """
        if self.default is not None:
            facet = CFacet( 0 )
            facet.clone( original_facet )
            if original_facet.__dict__ is not None:
                facet.__dict__ = original_facet.__dict__.copy()

            facet.default_value( 7, ( self.default, self.args, self.kw ) )

        elif self.type is not None:
            type = self.type
            try:
                rc = issubclass( type, FacetType )
            except:
                rc = False

            if rc:
                type = type( *self.args, **self.kw )

            if not isinstance( type, FacetType ):
                raise FacetError(
                    ("The 'type' attribute of a FacetValue instance must be a "
                     "FacetType instance or subclass, but a value of %s was "
                     "specified.") % self.facet
                )

            self._cfacet = facet = type.as_cfacet()
            facet.value_allowed( True )

        elif self.delegate is None:
            return None

        else:
            if self.name == '':
                raise FacetError(
                    "You must specify a non-empty string value for the 'name' "
                    "attribute when using the 'delegate' facet of a FacetValue "
                    "instance."
                )

            metadata = {
                'type':         'property',
                '_facet_value': self,
                'transient':    True
            }

            getter   = self._delegate_getter
            setter   = self._delegate_setter
            validate = None

            self.add_facet( 'value', Event() )
            self.delegate.on_facet_set( self._delegate_modified,
                                        self.name + '[]' )

            facet = self._property_facet( getter, setter, validate, metadata )

        return facet


    def _delegate_getter ( self, object, name ):
        # Return 'Undefined' if facet can't be read, since it may be write-only:
        return getattr( self.delegate, self.name, Undefined )

    def _delegate_setter ( self, object, name, value ):
        setattr( self.delegate, self.name, value )

    #-- Facets Event Handlers --------------------------------------------------

    def _delegate_modified ( self ):
        self.value = True

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def SyncValue ( delegate, name ):
    return FacetValue( delegate = delegate, name = name )

def TypeValue ( type ):
    return FacetValue( type = type )

def DefaultValue ( default, args = (), kw = {} ):
    return FacetValue( default = default, args = args, kw = kw )

#-------------------------------------------------------------------------------
#  Tell the C-based facets module about the 'BaseFacetValue' class:
#-------------------------------------------------------------------------------

import cfacets
cfacets._value_class( BaseFacetValue )

#-- EOF ------------------------------------------------------------------------