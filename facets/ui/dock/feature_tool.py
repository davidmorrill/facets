"""
Implements the FeatureTool feature that allows a dragged object
implementing the IFeatureTool interface to be dropped onto any compatible
object.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from dock_window_feature \
    import DockWindowFeature

from facets.ui.ui_facets \
    import Image

#-------------------------------------------------------------------------------
#  'FeatureTool' class:
#-------------------------------------------------------------------------------

class FeatureTool ( DockWindowFeature ):

    #-- Facet Definitions ------------------------------------------------------

    image = Image( '@facets:feature_tool' )

    #-- Public Methods ---------------------------------------------------------

    def can_drop ( self, object ):
        """ Returns whether a specified object can be dropped on the feature
            image.
        """
        return True

#-- EOF ------------------------------------------------------------------------