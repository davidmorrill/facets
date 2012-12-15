"""
Defines the ThemedButton class, a GUI toolkit independent button control that
can display both images and text on a themed background.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Event, Image, Theme, ATheme

from facets.extra.helper.image \
    import hlsa_derived_image, HoverTransform, DownTransform, DisabledTransform

from themed_control \
    import ThemedControl

#-------------------------------------------------------------------------------
#  'ThemedButton' class:
#-------------------------------------------------------------------------------

class ThemedButton ( ThemedControl ):
    """ Facets UI themed button editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The optional 'normal' state theme for the button:
    normal_theme = ATheme

    # The optional 'hover' state theme for the button:
    hover_theme = ATheme

    # The optional 'down' state theme for the button:
    down_theme = ATheme

    # The optional 'disabled' state theme for the button:
    disabled_theme = ATheme

    # The optional 'normal' state image for the button:
    normal_image = Image

    # The optional 'hover' state image for the button:
    hover_image = Image

    # The optional 'down' state image for the button:
    down_image = Image

    # The optional 'disabled' state image for the button:
    disabled_image = Image

    # Event fired when the button is clicked:
    clicked = Event

    # Is the mouse pointer currently in the button control?
    is_in_control = Bool( False )

    #-- Private Facets ---------------------------------------------------------

    # The default basic theme for the button (i.e. the 'up' state):
    _default_theme = ATheme( Theme( '@xform:ul?a~L45|l2',
                                    content = ( 5, 5, 0, -5 ) ) )

    # The default 'hover' state theme for the button:
    _default_hover_theme = ATheme( Theme( '@xform:ul?L30~L45|l2',
                                          content = ( 5, 5, 0, -5 ) ) )

    # The default 'down' state theme for the button:
    _default_down_theme = ATheme( Theme( '@xform:ul?H58L17S83~L45|l2',
                                         content = ( 5, 5, 0, -5 ) ) )

    # The default 'disabled' state theme for the button:
    _default_disabled_theme = ATheme( Theme( '@xform:ul?a',
                                             content = ( 5, 5, 0, -5 ) ) )

    #-- Facet Default Values ---------------------------------------------------

    def _normal_theme_default ( self ):
        if self.normal_image is None:
            return self._default_theme

        return None


    def _hover_theme_default ( self ):
        if self.normal_theme is self._default_theme:
            return self._default_hover_theme

        return self.normal_theme


    def _down_theme_default ( self ):
        if self.normal_theme is self._default_theme:
            return self._default_down_theme

        return self.normal_theme


    def _disable_theme_default ( self ):
        if self.normal_theme is self._default_theme:
            return self._default_disabled_theme

        return self.normal_theme


    def _normal_image_default ( self ):
        return self.image


    def _hover_image_default ( self ):
        return hlsa_derived_image( self.normal_image, HoverTransform )


    def _down_image_default ( self ):
        return hlsa_derived_image( self.normal_image, DownTransform )


    def _disabled_image_default ( self ):
        return hlsa_derived_image( self.normal_image, DisabledTransform )

    #-- Facet Event Handlers ---------------------------------------------------

    def _state_set ( self, state ):
        """ Handles the 'state' facet being changed by making sure that the
            button values are correct for the current button state.
        """
        image, theme = self.normal_image, self.normal_theme
        if state == 'hover':
            if self.is_in_control:
                image = self.hover_image
                theme = self.hover_theme
        elif state == 'down':
            if self.is_in_control:
                image = self.down_image
                theme = self.down_theme
        elif state == 'disabled':
            image = self.disabled_image
            theme = self.disabled_theme

        self.image, self.theme = image, theme


    def _enabled_set ( self, enabled ):
        """ Handles the 'enabled' state changing.
        """
        self.state = ( 'disabled', 'normal' )[ enabled ]

    #-- ThemedControl Event Handlers -------------------------------------------

    def normal_left_down ( self, x, y, event ):
        if self.control.enabled:
            self.state = 'down'


    def normal_motion ( self, x, y, event ):
        if self.control.enabled:
            self.is_in_control         = True
            self.state                 = 'hover'
            self.control.mouse_capture = True


    def hover_left_down ( self, x, y, event ):
        self.normal_left_down( x, y, event )


    def hover_motion ( self, x, y, event ):
        self.is_in_control = self.in_control( x, y )
        if not self.is_in_control:
            self.state                 = 'normal'
            self.control.mouse_capture = False


    def down_left_up ( self, x, y, event ):
        self.is_in_control = self.in_control( x, y )
        if self.is_in_control:
            self.state                 = 'hover'
            self.clicked               = True
            self.control.mouse_capture = True
        else:
            self.state = 'normal'


    def down_motion ( self, x, y, event ):
        theme              = self.down_theme or self.normal_theme
        image              = self.down_image
        self.is_in_control = self.in_control( x, y )
        if not self.is_in_control:
            image, theme = self.normal_image, self.normal_theme

        self.image, self.theme = image, theme

#-- EOF ------------------------------------------------------------------------
