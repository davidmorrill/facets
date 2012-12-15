"""
Defines the theme style information for a DockWindow and its components.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Bool, Range, Instance, Property, Event, Color, \
           cached_property

from facets.ui.ui_facets \
    import Image, ATheme

#-------------------------------------------------------------------------------
#  'DockWindowTheme' class:
#-------------------------------------------------------------------------------

class DockWindowTheme ( HasPrivateFacets ):
    """ Defines the theme style information for a DockWindow and its components.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Do splitter bars have open and close buttons?
    splitter_open_close = Bool( True )

    # Should the text displayed on a tab have an engraved look?
    engraved_text = Bool( False )

    # Draw notebook tabs at the top (True) or the bottom (False)?
    tabs_at_top = Bool( True )

    # Should tabs be drawn full width when not appearing with other tabs in the
    # same region (i.e. when not in a multi-tab notebook)?
    tabs_are_full_width = Bool( False )

    # Display text and icons in a tab?
    tabs_show_text = Bool( True )

    # Use the theme background color as the DockWindow background color?
    use_theme_color = Bool( True )

    # The theme background color:
    background_color = Color( None )

    # The amount of space inserted between adjacent notebook tabs:
    tab_spacing = Range( 0, 10 )

    # Selected tab theme:
    tab_selected = ATheme

    # Active tab theme:
    tab_active = ATheme

    # Inactive tab theme:
    tab_inactive = ATheme

    # Optional image to use for right edge of rightmost inactive tab:
    tab_inactive_edge = Image

    # Tab hover theme (used for inactive tabs):
    tab_hover = ATheme

    # Optional image to use for right edge of rightmost hover tab:
    tab_hover_edge = Image

    # Tab background theme:
    tab_background = ATheme

    # Tab theme:
    tab = ATheme

    # Vertical splitter bar theme:
    vertical_splitter = ATheme

    # Horizontal splitter bar theme:
    horizontal_splitter = ATheme

    # Vertical drag bar theme:
    vertical_drag = ATheme

    # Horizontal drag bar theme:
    horizontal_drag = ATheme

    # The set of icon images used to add additional details:
    images = Instance( 'facets.ui.dock.dock_window_images.DockWindowImages' )

    # Event fired when the theme has been dynamically updated:
    updated = Event

    #-- Private Facets ---------------------------------------------------------

    # The bitmap for the 'tab_inactive_edge' image:
    tab_inactive_edge_bitmap = Property( depends_on = 'tab_inactive_edge' )

    # The bitmap for the 'tab_hover_edge' image:
    tab_hover_edge_bitmap = Property( depends_on = 'tab_hover_edge' )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_tab_inactive_edge_bitmap ( self ):
        image = self.tab_inactive_edge
        if image is None:
            return None

        return image.bitmap


    @cached_property
    def _get_tab_hover_edge_bitmap ( self ):
        image = self.tab_hover_edge
        if image is None:
            return self.tab_inactive_edge_bitmap

        return image.bitmap

    #-- Facet Default Values ---------------------------------------------------

    def _images_default ( self ):
        from facets.ui.dock.dock_window_images import dock_window_images

        return dock_window_images

    #-- Public Methods ---------------------------------------------------------

    def clone ( self ):
        """ Returns a clone of this theme.
        """
        return self.__class__().copy_theme( self )


    def copy_theme ( self, theme ):
        """ Copies the contents of the specified DockWindowTheme *theme* into
            this one.
        """
        self.copy_facets( theme )
        self.updated = True

        return self

#-- EOF ------------------------------------------------------------------------