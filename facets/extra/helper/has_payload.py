"""
Defines the HasPayload class for defining objects that carry some type of data
payload.

It is intended to be used as a common tool data interchange format.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Any, Property

#-------------------------------------------------------------------------------
#  'HasPayload' class:
#-------------------------------------------------------------------------------

class HasPayload ( HasPrivateFacets ):
    """ Defines the HasPayload class for defining objects that carry some type
        of data payload.

        It is intended to be used as a common tool data interchange format.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The 'payload' object:
    payload = Any

    # Payload name:
    payload_name = Property

    # Full payload name:
    payload_full_name = Property

    #-- Property Implementations -----------------------------------------------

    def _get_payload_name ( self ):
        if self._payload_name is not None:
            return self._payload_name

        return self.payload.__class__.__name__

    def _set_payload_name ( self, name ):
        self._payload_name = name


    def _get_payload_full_name ( self ):
        if self._payload_full_name is not None:
            return self._payload_full_name

        return self.payload.__class__.__name__

    def _set_payload_full_name ( self, full_name ):
        self._payload_full_name = full_name

#-- EOF ------------------------------------------------------------------------