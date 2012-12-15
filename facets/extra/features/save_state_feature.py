"""
Manages saving/restoring the state of an object. Any facets with metadata
'save_state = True' are automatically restored when the feature is applied and
saved when they are changed. The facets are saved under the id specified by a
facet with metadata 'save_state_id = True'. If no such facet exists, an id of
the form: 'unknown.plugins.?.state', where ? = the name of the object's
associated DockControl.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets, List, FacetListObject, FacetSetObject, FacetDictObject, \
           Str, on_facet_set

from facets.core.facet_db \
    import facet_db

from facets.ui.dock.api \
    import DockWindowFeature

#-------------------------------------------------------------------------------
#  'SaveStateFeature' class:
#-------------------------------------------------------------------------------

class SaveStateFeature ( DockWindowFeature ):

    #-- Facet Definitions ------------------------------------------------------

    # The persistence id to save the data under:
    id = Str

    # List of facets to save/restore:
    names = List( Str )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'dock_control:object:+save_state' )
    def save_state ( self ):
        """ Saves the current state of the plugin.
        """
        values = self.dock_control.object.get( *self.names )
        for name, value in values.items():
            if isinstance( value, FacetListObject ):
                values[ name ] = list( value )
            elif isinstance( value, FacetSetObject ):
                values[ name ] = set( value )
            elif isinstance( value, FacetDictObject ):
                values[ name ] = dict( value )

        facet_db.set( self.id, values )

    #-- Overidable Class Methods -----------------------------------------------

    @classmethod
    def feature_for ( cls, dock_control ):
        """ Returns a feature object for use with the specified DockControl (or
            None if the feature does not apply to the DockControl object).
        """
        object = dock_control.object
        if isinstance( object, HasFacets ):
            names = object.facet_names( save_state = True )
            if len( names ) > 0:

                # Get the id to save the options under:
                ids = object.facet_names( save_state_id = True )
                id  = ''
                if len( ids ) == 1:
                    id = getattr( object, ids[0] )

                if id == '':
                    id = 'unknown.plugins.%s.state' % dock_control.name

                # Assign the current saved state (if any) to the object:
                state = facet_db.get( id )
                if state is not None:
                    for name, value in state.iteritems():
                        try:
                            setattr( object, name, value )
                        except:
                            pass

                # Create and return the feature:
                return cls(
                    dock_control = dock_control,
                    id           = id ).set(
                    names        = names
                )

        return None

#-- EOF ------------------------------------------------------------------------