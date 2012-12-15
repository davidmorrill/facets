"""
Defines ThemedControl, a themed control based class. A 'themed' control is a
control (optionally) supporting a stretchable background image.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Int, Bool, Property, Event, Tuple, DelegatesTo, \
           property_depends_on, default_theme

from facets.ui.ui_facets \
    import Image, Alignment

from themed_window \
    import ThemedWindow

#-------------------------------------------------------------------------------
#  'ThemedControl' class:
#-------------------------------------------------------------------------------

class ThemedControl ( ThemedWindow ):

    #-- Facet Definitions ------------------------------------------------------

    # Does this control handle keyboard input (override)?
    handle_keys = True

    # An (optional) image to be drawn inside the control:
    image = Image( event = 'updated' )

    # The (optional) text to be displayed inside the control:
    text = Str( event = 'updated' )

    # The alignment of the text and image within the control:
    alignment = Alignment( 'center', event = 'updated' )

    # Is the text value private (like a password):
    password = Bool( False, event = 'updated' )

    # Minimum default size for the control:
    min_size = Tuple( Int, Int )

    # Is the control enabled:
    enabled = DelegatesTo( 'control' )

    #-- Private Facets ---------------------------------------------------------

    # An event fired when any display related value changes:
    updated = Event( on_facet_set = 'theme.+, image' )

    # The current text value to display:
    current_text = Property

    # The best size for the control:
    best_size = Property

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'text, password' )
    def _get_current_text ( self ):
        """ Returns the current text to display.
        """
        if self.password:
            return ('*' * len( self.text ))

        return self.text


    def _get_best_size ( self ):
        """ Returns the 'best' size for the control.
        """
        mdx, mdy = self.min_size
        cdx, cdy = (self.theme or default_theme).size_for(
            self.control.temp_graphics, self.text, self.image
        )

        return ( max( cdx, mdx ), max( cdy, mdy ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the underlying 'control' being created.
        """
        # Make sure the control is sized correctly:
        control.min_size = control.size = self.best_size


    def _updated_set ( self ):
        """ Handles any update related facet being changed.
        """
        if self.control is not None:
            self.control.refresh()

    #-- Control Event Handlers -------------------------------------------------

    def paint ( self, g ):
        """ Paints the foreground into the specified graphics object.
        """
        dx, dy = self.control.client_size
        (self.theme or default_theme).draw_text(
            g, self.current_text, self.alignment, 0, 0, dx, dy,
            image = self.image
        )


    def resize ( self, event ):
        """ Handles the control being resized.
        """
        super( ThemedControl, self ).resize( event )

        self.updated = True

#-- EOF ------------------------------------------------------------------------