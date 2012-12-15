"""
Initializes any facet of an object with 'dock_control = True' metadata to point
to the object's DockControl.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets

from facets.ui.dock.api \
    import DockWindowFeature

#-------------------------------------------------------------------------------
#  'DockControlFeature' class:
#-------------------------------------------------------------------------------

class DockControlFeature ( DockWindowFeature ):

    #-- Overridable Class Methods ----------------------------------------------

    @classmethod
    def feature_for ( cls, dock_control ):
        """ Returns a feature object for use with the specified DockControl (or
            None if the feature does not apply to the DockControl object).
        """
        object = dock_control.object
        if isinstance( object, HasFacets ):
            for name in object.facet_names( dock_control = True ):
                try:
                    setattr( object, name, dock_control )
                except:
                    pass

        return None

#-- EOF ------------------------------------------------------------------------