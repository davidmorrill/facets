"""
Facets UI themed button editor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Instance, Str, Theme, ATheme, on_facet_set, BasicEditorFactory

from facets.ui.ui_facets \
    import AView, Image, Alignment

from facets.ui.controls.themed_control \
    import ThemedControl

from facets.extra.helper.image \
    import hlsa_derived_image, HoverTransform, DownTransform, DisabledTransform

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_ThemedButtonEditor' class:
#-------------------------------------------------------------------------------

class _ThemedButtonEditor ( Editor ):
    """ Facets UI themed button editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ThemedControl used for the button:
    button = Instance( ThemedControl )

    # Is the mouse pointer currently in the button control?
    in_control = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create the button and its control:
        factory         = self.factory
        label           = factory.label
        self._has_label = (label != '')
        if (label == '') and (factory.image is None):
            label = self.item.get_label( self.ui )

        label = self.string_value( label )

        button = ThemedControl(
            **factory.get( 'theme', 'image', 'alignment' )
        ).set(
            text       = label,
            controller = self,
            min_size   = ( 16, 0 ),
            parent     = parent
        )
        self.adapter = button()
        self.button  = button

        # Set the tooltip:
        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.button.dispose()

        super( _ThemedButtonEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        pass

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'button:state' )
    def _button_update ( self ):
        """ Make sure the button values are correct for the current button
            state.
        """
        factory      = self.factory
        image, theme = factory.image, factory.theme
        button       = self.button
        state        = button.state
        if state == 'hover':
            if self.in_control:
                image = factory.hover_image
                theme = factory.hover_theme or theme
        elif state == 'down':
            if self.in_control:
                image = factory.down_image
                theme = factory.down_theme or theme
        elif state == 'disabled':
            image = factory.disabled_image
            theme = factory.disabled_theme or theme

        button.image     = image
        button.theme     = theme
        button.alignment = factory.alignment
        label            = factory.label
        has_label        = (label != '')
        if has_label or self._has_label:
            self._has_label |= has_label
            button.text      = self.string_value( label )


    @on_facet_set( 'button:enabled' )
    def _enabled_modified ( self ):
        """ Handles the button 'enabled' state changing.
        """
        self.button.state = ( 'disabled', 'normal' )[ self.button.enabled ]


    @on_facet_set( 'factory:+' )
    def _factory_modified ( self ):
        """ Handles one of the factory parameters that affects the appearance
            of the control being changed.
        """
        if self.adapter is not None:
            self._button_update()
            self.adapter.refresh()

    #-- ThemedControl Event Handlers -------------------------------------------

    def normal_left_down ( self, x, y, event ):
        if self.adapter.enabled:
            self.button.state = 'down'


    def normal_motion ( self, x, y, event ):
        if self.adapter.enabled:
            self.in_control            = True
            self.button.state          = 'hover'
            self.adapter.mouse_capture = True


    def hover_left_down ( self, x, y, event ):
        self.normal_left_down( x, y, event )


    def hover_motion ( self, x, y, event ):
        self.in_control = self.button.in_control( x, y )
        if not self.in_control:
            self.button.state          = 'normal'
            self.adapter.mouse_capture = False


    def down_left_up ( self, x, y, event ):
        self.in_control = self.button.in_control( x, y )
        if self.in_control:
            self.button.state = 'hover'
            self.value        = True

            # If there is an associated view, display it:
            if self.factory.view is not None:
                self.object.edit_facets( view   = self.factory.view,
                                         parent = self.control )

            self.adapter.mouse_capture = self.button.enabled
        else:
            self.button.state = 'normal'


    def down_motion ( self, x, y, event ):
        factory         = self.factory
        theme           = factory.down_theme or factory.theme
        image           = factory.down_image
        self.in_control = self.button.in_control( x, y )
        if not self.in_control:
            image, theme = factory.image, factory.theme

        self.button.set( image = image, theme = theme )

#-------------------------------------------------------------------------------
#  'ThemedButtonEditor' class:
#-------------------------------------------------------------------------------

class ThemedButtonEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ThemedButtonEditor

    # The button label:
    label = Str( facet_value = True )

    # The basic theme for the button (i.e. the 'up' state):
    theme = ATheme( facet_value = True )

    # The optional 'hover' state theme for the button:
    hover_theme = ATheme( facet_value = True )

    # The optional 'down' state theme for the button:
    down_theme = ATheme( facet_value = True )

    # The optional 'disabled' state theme for the button:
    disabled_theme = ATheme( facet_value = True )

    # The optional image to display in the button:
    image = Image( facet_value = True )

    # The optional 'hover' state image for the button:
    hover_image = Image #( facet_value = True )

    # The optional 'down' state image for the button:
    down_image = Image #( facet_value = True )

    # The optional 'disabled' state image for the button:
    disabled_image = Image #( facet_value = True )

    # The alignment of the text and image within the button:
    alignment = Alignment( 'center', facet_value = True )

    # The optional view to display when the button is clicked:
    view = AView

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

    def _theme_default ( self ):
        return self._default_theme


    def _hover_theme_default ( self ):
        if self.theme is self._default_theme:
            return self._default_hover_theme

        return self.theme


    def _down_theme_default ( self ):
        if self.theme is self._default_theme:
            return self._default_down_theme

        return self.theme


    def _disable_theme_default ( self ):
        if self.theme is self._default_theme:
            return self._default_disabled_theme

        return self.theme


    def _hover_image_default ( self ):
        return hlsa_derived_image( self.image, HoverTransform )


    def _down_image_default ( self ):
        return hlsa_derived_image( self.image, DownTransform )


    def _disabled_image_default ( self ):
        return hlsa_derived_image( self.image, DisabledTransform )

#-- EOF ------------------------------------------------------------------------