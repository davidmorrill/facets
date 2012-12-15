"""
Adds an 'options' feature to DockWindow which allows users to configure a
view's options if the object associated with a DockControl has an 'options'
view.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets

from facets.api \
    import View

from facets.ui.dock.api \
    import DockWindowFeature

#-------------------------------------------------------------------------------
#  'OptionsFeature' class:
#-------------------------------------------------------------------------------

class OptionsFeature ( DockWindowFeature ):

    #-- Class Constants --------------------------------------------------------

    # The user interface name of the feature:
    feature_name = 'Options'

    #-- Facet Definitions ------------------------------------------------------

    # The current image to display on the feature bar:
    image = '@facets:options_feature'

    # The tooltip to display when the mouse is hovering over the image:
    tooltip = 'Click to set view options.'

    #-- Event Handlers ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left clicking on the feature image.
        """
        dc                = self.dock_control
        object            = dc.object
        view              = object.facet_view( 'options' )
        sx, sy            = dc.owner.control.screen_position
        _, dby, _, dbdy   = dc.drag_bounds
        bx, _, bdx, _     = dc.bounds
        view.popup_bounds = ( bx + sx, dby + sy, bdx, dbdy )
        self.dock_control.object.edit_facets( view = view, kind = 'popup' )

    #-- Overridable Class Methods ----------------------------------------------

    @classmethod
    def is_feature_for ( self, dock_control ):
        """ Returns whether or not the DockWindowFeature is a valid feature for
            a specified DockControl.
        """
        object = dock_control.object

        return (isinstance( object, HasFacets ) and
                isinstance( object.facet_view( 'options' ), View ))

#-- EOF ------------------------------------------------------------------------