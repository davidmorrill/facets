"""
Defines the HasState class for defining features with persistable state data.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Str

#-------------------------------------------------------------------------------
#  'HasState' class:
#-------------------------------------------------------------------------------

class HasState ( HasPrivateFacets ):
    """ Defines the HasState class for defining features with persistable state
        data.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The persistence id for the plugin:
    id = Str

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, **facets ):
        super( HasState, self ).__init__( **facets )

        self.restore_state()


    def get_state ( self ):
        return self.get()


    def save_state ( self ):
        """ Saves the current state of the plugin.
        """
        if (not self._no_save_state) and (self.id != ''):
            self.facet_db_set( self.id, self.get_state() )


    def restore_state ( self ):
        """ Restores the previously saved state of the plugin.
        """
        id = self.id
        if id != '':
            state = self.facet_db_get( id )
            if state is not None:
                self._no_save_state = True
                try:
                    self.set( **state )
                except:
                    pass

                self._no_save_state = False

#-- EOF ------------------------------------------------------------------------