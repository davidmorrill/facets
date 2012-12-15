"""
Defines the AnIFeatureTool class, which is a concrete base class implementation
of the IFeatureTool interface, which allows objects dragged using the
DockWindowFeature API to control the drag target and drop events. Useful for
implementing tools which can be dropped onto compatible view objects.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets, implements

from ifeature_tool \
    import IFeatureTool

#-------------------------------------------------------------------------------
#  'AnIFeatureTool' class:
#-------------------------------------------------------------------------------

class AnIFeatureTool ( HasFacets ):

    implements( IFeatureTool )

    #-- IFeatureTool Interface -------------------------------------------------

    def feature_can_drop_on ( self, object ):
        """ Returns whether or not the object being dragged (i.e. self) can be
            dropped on the specified target object.
        """
        return False


    def feature_can_drop_on_dock_control ( self, dock_control ):
        """ Returns whether or not the object being dragged (i.e. self) can be
            dropped on the specified target object's DockControl.
        """
        return False


    def feature_dropped_on ( self, object ):
        """ Allows the dragged object (i.e. self) to handle being dropped on the
            specified target object.
        """
        return


    def feature_dropped_on_dock_control ( self, dock_control ):
        """ Allows the dragged object (i.e. self) to handle being dropped on the
            specified target object's DockControl.
        """
        return

#-- EOF ------------------------------------------------------------------------