"""
Adds a 'custom' feature to DockWindow which allows views to contribute
custom features to their own tab.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, Property, Instance, Str, Bool, Image, \
           on_facet_set

from facets.ui.dock.api \
    import DockWindowFeature

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard sequence types:
SequenceTypes = ( list, tuple )

#-------------------------------------------------------------------------------
#  'CustomFeatureItem' class:
#-------------------------------------------------------------------------------

class CustomFeatureItem ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The current image to display on the feature bar:
    image = Image

    # The tooltip to display when the mouse is hovering over the image:
    tooltip = Str

    # Is the feature currently enabled?
    enabled = Bool( True )

    # Name of the method to invoke on a left click:
    click = Str

    # Name of the method to invoke on a right click:
    right_click = Str

    # Name of the method to invoke when the user starts to drag with the left
    # mouse button:
    drag = Str

    # Name of the method to invoke when the user starts to ctrl-drag with the
    # left mouse button:
    control_drag = Str

    # Name of the method to invoke when the user starts to shift-drag with the
    # left mouse button:
    shift_drag = Str

    # Name of the method to invoke when the user starts to alt-drag with the
    # left mouse button:
    alt_drag = Str

    # Name of the method to invoke when the user starts to drag with the right
    # mouse button:
    right_drag = Str

    # Name of the method to invoke when the user starts to ctrl-drag with the
    # right mouse button:
    control_right_drag = Str

    # Name of the method to invoke when the user starts to shift-drag with the
    # right mouse button:
    shift_right_drag = Str

    # Name of the method to invoke when the user starts to alt-drag with the
    # right mouse button:
    alt_right_drag = Str

    # Name of the method to invoke when the user drops an object:
    drop = Str

    # Name of the method to invoke to see if the user can drop an object:
    can_drop = Str

#-------------------------------------------------------------------------------
#  'ACustomFeature' class:
#-------------------------------------------------------------------------------

class ACustomFeature ( DockWindowFeature ):

    #-- Facet Definitions ------------------------------------------------------

    # The CustomFeatureItem associated with this feature:
    custom_feature = Instance( CustomFeatureItem )

    # The current image to display on the feature bar:
    image = Property

    # The tooltip to display when the mouse is hovering over the image:
    tooltip = Property

    #-- Property Implementations -----------------------------------------------

    def _get_image ( self ):
        if self.custom_feature.enabled:
            return self.custom_feature.image

        return None


    def _get_tooltip ( self ):
        return self.custom_feature.tooltip

    #-- Overrides of DockWindowFeature Methods ---------------------------------

    def click ( self ):
        """ Handles the user left clicking on the feature image.
        """
        self.dynamic_call( 'click' )


    def right_click ( self ):
        """ Handles the user right clicking on the feature image.
        """
        self.dynamic_call( 'right_click' )


    def drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image with the left mouse button.
        """
        return self.dynamic_call( 'drag', None )


    def control_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image with the left mouse button while holding down the 'Ctrl' key:
        """
        return self.dynamic_call( 'control_drag', None )


    def shift_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image with the left mouse button while holding down the 'Shift' key.
        """
        return self.dynamic_call( 'shift_drag', None )


    def alt_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image with the left mouse button while holding down the 'Alt' key:
        """
        return self.dynamic_call( 'alt_drag', None )


    def right_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image with the right mouse button.
        """
        return self.dynamic_call( 'right_drag', None )


    def control_right_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image with the right mouse button while holding down the 'Ctrl' key:
        """
        return self.dynamic_call( 'control_right_drag', None )


    def shift_right_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image with the right mouse button while holding down the 'Shift'
            key.
        """
        return self.dynamic_call( 'shift_right_drag', None )


    def alt_right_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image with the right mouse button while holding down the 'Alt' key:
        """
        return self.dynamic_call( 'alt_right_drag', None )


    def drop ( self, object ):
        """ Handles the user dropping a specified object on the feature image.
        """
        return self.dynamic_call( 'drop', args = ( object, ) )


    def can_drop ( self, object ):
        """ Returns whether a specified object can be dropped on the feature
            image.
        """
        return self.dynamic_call( 'can_drop', False, args = ( object, ) )


    def dispose ( self ):
        """ Performs any clean-up needed when the feature is being removed.
        """
        self.custom_feature.on_facet_set( self._custom_feature_updated,
                                          remove = True )

    #-- ACustomFeature Methods -------------------------------------------------

    def dynamic_call ( self, method, default = None, args = () ):
        """ Performs a method invocation using the associated
            CustomFeatureItem.
        """
        method = getattr( self.custom_feature, method )
        if method == '':
            return default

        return getattr( self.dock_control.object, method )( *args )


    @on_facet_set( 'custom_feature:+' )
    def _custom_feature_updated ( self ):
        """ Handles any facet on the associated dynamic feature being changed.
        """
        self.refresh()

    #-- Overridable Class Methods ----------------------------------------------

    @classmethod
    def feature_for ( cls, dock_control ):
        """ Returns a feature object for use with the specified DockControl (or
            None if the feature does not apply to the DockControl object).
        """
        from facets.extra.features.api import is_not_none

        object = dock_control.object
        if isinstance( object, HasFacets ):
            result = []
            for name in object.facet_names( custom_feature = is_not_none ):
                custom_feature = getattr( object, name, None )
                if isinstance( custom_feature, CustomFeatureItem ):
                    result.append( cls(
                        dock_control   = dock_control,
                        custom_feature = custom_feature
                    ) )
                elif isinstance( custom_feature, SequenceTypes ):
                    for feature in custom_feature:
                        if isinstance( feature, CustomFeatureItem ):
                            result.append( cls(
                                dock_control   = dock_control,
                                custom_feature = feature
                            ) )

            return result

        return None

#-------------------------------------------------------------------------------
#  Helper function for creating custom features:
#-------------------------------------------------------------------------------

def CustomFeature ( **facets ):
    return Instance( CustomFeatureItem, facets, custom_feature = True )

#-- EOF ------------------------------------------------------------------------