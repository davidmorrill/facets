"""
Manages images used in the display of a DockWindow.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core.api \
    import HasPrivateFacets, Any

from facets.ui.ui_facets \
    import Image

#-------------------------------------------------------------------------------
#  'DockWindowImages' class:
#-------------------------------------------------------------------------------

class DockWindowImages ( HasPrivateFacets ):
    """ Manages images used in the display of a DockWindow.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Image for closing a tab:
    close_tab            = Image( '@facets:close_tab' )

    # Vertical splitter bar full left, middle and full right images:
    vertical_left        = Image( '@facets:sv_left'   )
    vertical_middle      = Image( '@facets:sv_middle' )
    vertical_right       = Image( '@facets:sv_right'  )

    # Horizontal splitter bar full top, middle and full bottom images:
    horizontal_top       = Image( '@facets:sh_top'    )
    horizontal_middle    = Image( '@facets:sh_middle' )
    horizontal_bottom    = Image( '@facets:sh_bottom' )

    # Tab group 'scroll bar' images:
    scroll_left          = Image( '@facets:tab_scroll_l'  )
    scroll_right         = Image( '@facets:tab_scroll_r'  )
    scroll_left_right    = Image( '@facets:tab_scroll_lr' )

    # Feature icons:
    tab_feature_normal   = Image( '@facets:tab_feature_normal'   )
    tab_feature_changed  = Image( '@facets:tab_feature_changed'  )
    tab_feature_drop     = Image( '@facets:tab_feature_drop'     )
    tab_feature_disabled = Image( '@facets:tab_feature_disabled' )
    bar_feature_normal   = Image( '@facets:bar_feature_normal'   )
    bar_feature_changed  = Image( '@facets:bar_feature_changed'  )
    bar_feature_drop     = Image( '@facets:bar_feature_drop'     )
    bar_feature_disabled = Image( '@facets:bar_feature_disabled' )

    #-- Private Facets ---------------------------------------------------------

    # The list of splitter related images:
    splitter_images = Any

    # The tab group 'scroll bar' related images:
    scroll_images = Any

    # Feature related images:
    feature_images = Any

    #-- Facet Default Values ---------------------------------------------------

    def _splitter_images_default ( self ):
        return [ ( image.bitmap, image.width, image.height )
                 for image in [ getattr( self, name ) for name in
                     ( 'vertical_left', 'vertical_middle', 'vertical_right',
                       'horizontal_top', 'horizontal_middle',
                       'horizontal_bottom' ) ] ]


    def _scroll_images_default ( self ):
        return (
            self.scroll_left.bitmap,
            self.scroll_right.bitmap,
            self.scroll_left_right.bitmap
        )


    def _feature_images_default ( self ):
        return [ image.bitmap for image in [ getattr( self, name ) for name in
                 ( 'tab_feature_normal',  'tab_feature_changed',
                   'tab_feature_drop',    'tab_feature_disabled',
                   'bar_feature_normal',  'bar_feature_changed',
                   'bar_feature_drop',    'bar_feature_disabled' ) ] ]

    #-- Method Implementations -------------------------------------------------

    def get_splitter_image ( self, state ):
        """ Returns the splitter image to use for a specified splitter state.
        """
        return self.splitter_images[ state ]


    def get_feature_image ( self, state, is_tab = True ):
        """ Returns the feature image to use for a specified feature state.
        """
        if is_tab:
            return self.feature_images[ state ]

        return self.feature_images[ state + 3 ]

#-- Create a reusable instance -------------------------------------------------

dock_window_images = DockWindowImages()

#-- EOF ------------------------------------------------------------------------