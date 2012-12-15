"""
Defines a DockWindow feature for allowing the user to interatively select the
layout style to use for the current contents of a DockWindow.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, List, Any, Theme, View, Item, \
           FilmStripEditor

from facets.ui.dock.api \
    import DockWindowFeature, DockControl

from facets.ui.filmstrip_adapter \
    import FilmStripAdapter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The HLSA modifier to be applied to each layout item:
HLSAModifier = '?H56l13S'

# The height of the layout selector popup:
PopupHeight = 50

#-------------------------------------------------------------------------------
#  'LayoutFeature' class:
#-------------------------------------------------------------------------------

class LayoutFeature ( DockWindowFeature ):
    """ The DockWindow feature for displaying the layout selector.
    """

    #-- Class Constants --------------------------------------------------------

    # The user interface name of the feature:
    feature_name = 'Layout'

    #-- Facet Definitions ------------------------------------------------------

    # The current image to display on the feature bar:
    image = '@facets:layout'

    # The tooltip to display when the mouse is hovering over the image:
    tooltip = 'Click to select a layout style.'

    #-- Event Handlers ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left clicking on the feature image.
        """
        dc = self.dock_control
        LayoutSelector( dock_control = dc ).show( dc.control )

    #-- DockWindowFeature Method Overrides -------------------------------------

    def is_enabled ( self ):
        """ Returns whether or not the feature is currently enabled.
        """
        return (len( self.dock_control.dock_controls ) > 0)

#-------------------------------------------------------------------------------
#  'LayoutSelector' class:
#-------------------------------------------------------------------------------

class LayoutSelector ( HasPrivateFacets ):
    """ Allow the user to select a layout style consistent with the number of
        items currently being displayed in a DockWindow.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The DockControl the selector was invoked from:
    dock_control = Instance( DockControl )

    # The layout images that apply to the contents of the composite view:
    images = List

    # The currently selected layout:
    selected = Any # None or string

    #-- Public Methods ---------------------------------------------------------

    def show ( self, control ):
        """ Displays the layout selector as a popup relative to the specified
            *control*.
        """
        x, y   = control.screen_position
        dx, dy = control.client_size

        self.edit_facets( view = View(
            Item( 'images',
                  show_label = False,
                  height     = -56,
                  editor     = FilmStripEditor(
                      adapter = FilmStripAdapter(
                          mode           = 'actual',
                          has_label      = False,
                          theme          = Theme( '@xform:b?l20', content = 3 ),
                          selected_theme = Theme( '@xform:b?H57L16S',
                                                  content = 3 ),
                          hover_selected_theme = Theme( '@xform:b?H57L28S',
                                                        content = 3 )
                      ),
                      theme    = Theme( '@std:popup3?H9L19S~l60|L50' ),
                      selected = 'selected',
                      ratio    = 1.3333 )
            ),
            popup_bounds = ( x, max( 0, y - (PopupHeight / 2) ),
                             dx, PopupHeight ),
            kind         = 'popover',
            width        = 460,
            height       = PopupHeight )
        )

    #-- Facet Default Values ---------------------------------------------------

    def _images_default ( self ):
        n = min( 5, len( self.dock_control.dock_controls ) + 1 )

        return [ '@facets:layout_%d%d%s' % ( n, i + 1, HLSAModifier )
                 for i in xrange( ( 0, 1, 2, 6, 5, 5 )[ n ] ) ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if selected is not None:
            col = selected.find( '_' )
            self.dock_control.owner.apply_layout(
                int( selected[ col + 1 ] ), int( selected[ col + 2 ] ) - 1
            )

#-- EOF ------------------------------------------------------------------------
