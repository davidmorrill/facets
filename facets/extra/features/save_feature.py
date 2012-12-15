"""
Adds an 'save' feature to DockWindow which displays a 'save' image whenever
the associated object sets its 'needs_save' facet True. Then when the user
clicks the 'save' image, the feature calls the object's 'save' method.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import on_facet_set

from facets.ui.dock.api \
    import DockWindowFeature

from facets.ui.ui_facets \
    import image_for

from facets.extra.api \
    import Saveable

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

save_feature = image_for( '@facets:save_feature' )

#-------------------------------------------------------------------------------
#  'SaveFeature' class:
#-------------------------------------------------------------------------------

class SaveFeature ( DockWindowFeature ):

    #-- Facet Definitions ------------------------------------------------------

    # The tooltip to display when the mouse is hovering over the image:
    tooltip = 'Click to save.'

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'dock_control:object:needs_save' )
    def _needs_save_modified ( self, needs_save ):
        """ Handles the object's 'needs_save' facet being changed.
        """
        self.image = (save_feature if needs_save else None)
        self.refresh()

    #-- Event Handlers ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left clicking on the feature image.
        """
        self.dock_control.object.save()

    #-- Overidable Class Methods -----------------------------------------------

    @classmethod
    def is_feature_for ( self, dock_control ):
        """ Returns whether or not the DockWindowFeature is a valid feature for
            a specified DockControl.
        """
        return isinstance( dock_control.object, Saveable )

#-- EOF ------------------------------------------------------------------------