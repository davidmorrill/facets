"""
Facets UI themed checkbox editor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Instance, Str, BasicEditorFactory, on_facet_set

from facets.ui.ui_facets \
    import ATheme, Image, Alignment

from facets.ui.controls.themed_control \
    import ThemedControl

from facets.extra.helper.image \
    import hlsa_derived_image, HoverTransform, OffTransform

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_ThemedCheckboxEditor' class:
#-------------------------------------------------------------------------------

class _ThemedCheckboxEditor ( Editor ):
    """ Facets UI themed checkbox editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ThemedControl used for the checkbox:
    checkbox = Instance( ThemedControl, () )

    # Is the mouse pointer currently in the button control?
    in_control = Bool( False )

    #-- Method Definitions -----------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create the checkbox and its control:
        item            = self.item
        factory         = self.factory
        label           = self.string_value( factory.label or item.label )
        self._has_label = (factory.label != '')
        min_size  = ( 0, 0 )
        if factory.theme is not None:
            min_size  = ( 80, 0 )

        self.adapter = self.checkbox.set(
            **factory.get( 'image', 'alignment', 'theme' )
        ).set(
            text       = label,
            controller = self,
            min_size   = min_size,
            parent     = parent
        )()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.checkbox.dispose()

        super( _ThemedCheckboxEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self.checkbox.state == 'hover':
            self._set_hover_theme()
        else:
            self._set_theme()

        # Set the tooltip:
        self.set_tooltip()


    def set_tooltip ( self ):
        """ Set the editor control's tooltip.
        """
        factory = self.factory
        tooltip = [ factory.off_tooltip, factory.on_tooltip ] [ self.value ]
        self.adapter.tooltip = tooltip or self.item.tooltip

    #-- ThemedControl Event Handlers -------------------------------------------

    def normal_motion ( self ):
        self.in_control = True
        self._set_hover_theme( 'hover' )
        self.adapter.mouse_capture = True


    def hover_left_down ( self ):
        self.adapter.mouse_capture = False
        self._set_hover_theme( 'down', not self.value )


    def hover_motion ( self, x, y ):
        self.in_control = self.checkbox.in_control( x, y )
        if not self.in_control:
            self.adapter.mouse_capture = False
            self._set_theme( 'normal' )


    def hover_leave ( self ):
        self.hover_motion( -1, -1 )


    def down_left_up ( self, x, y ):
        self.in_control = self.checkbox.in_control( x, y )
        if self.in_control:
            self.value = not self.value
            self.normal_motion()
            self.set_tooltip()
        else:
            self._set_theme( 'normal' )


    def hover_left_dclick ( self ):
        self.hover_left_down()


    def down_motion ( self, x, y ):
        self.in_control = self.checkbox.in_control( x, y )
        if not self.in_control:
            self._set_theme()
        else:
            self._set_hover_theme( value = not self.value )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:+' )
    def _factory_modified ( self ):
        """ Handles one of the factory parameters that affects the appearance
            of the control being changed.
        """
        if self.adapter is not None:
            self._checkbox_update()
            self.adapter.refresh()

    #-- Private Methods --------------------------------------------------------

    def _checkbox_update ( self ):
        """ Make sure the checkbox values are correct for the current checkbox
            state.
        """
        factory            = self.factory
        checkbox           = self.checkbox
        checkbox.alignment = factory.alignment
        label              = factory.label
        has_label          = (label != '')
        if has_label or self._has_label:
            self._has_label |= has_label
            checkbox.text    = label

        if checkbox.state == 'hover':
            self._set_hover_theme()
        elif (checkbox.state == 'down') and self.in_control:
            self._set_hover_theme( value = not self.value )
        else:
            self._set_theme()

        self.set_tooltip()


    def _set_theme ( self, state = None, value = None ):
        """ Sets the theme, image, offset and optional checkbox state to use for
            a specified checkbox state value.
        """
        if value is None:
            value = self.value

        factory      = self.factory
        theme, image = factory.theme, factory.image
        if not value:
            theme = factory.off_theme or theme
            image = factory.off_image or image

        self.checkbox.set( theme = theme,
                           image = image,
                           state = state or self.checkbox.state )


    def _set_hover_theme ( self, state = None, value = None ):
        """ Sets the theme, image, offset and optional checkbox state to use for
            a specified checkbox state value while in hover mode.
        """
        if value is None:
            value = self.value

        factory = self.factory
        theme   = factory.hover_on_theme
        image   = factory.hover_on_image or factory.image
        if not value:
            theme = factory.hover_off_theme or factory.off_theme
            image = factory.hover_off_image or factory.off_image

        self.checkbox.set( theme = theme or factory.theme,
                           image = image or factory.image,
                           state = state or self.checkbox.state )

#-------------------------------------------------------------------------------
#  'ThemedCheckboxEditor' class:
#-------------------------------------------------------------------------------

class ThemedCheckboxEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ThemedCheckboxEditor

    # The checkbox label:
    label = Str( facet_value = True )

    # The basic theme for the checkbox (i.e. the 'on' state):
    theme = ATheme( facet_value = True )

    # The optional 'off' state theme for the checkbox:
    off_theme = ATheme( facet_value = True )

    # The optional 'hover on' state theme for the checbox:
    hover_on_theme = ATheme( facet_value = True )

    # The optional 'hover off' state theme for the checkbox:
    hover_off_theme = ATheme( facet_value = True )

    # The optional image to display in the checkbox (i.e. the 'on' state):
    image = Image( facet_value = True )

    # The optional 'off' state image to display in the checkbox:
    off_image = Image( facet_value = True )

    # The optional 'hover on' state image to display in the checkbox:
    hover_on_image = Image( facet_value = True )

    # The optional 'hover off' state image to display in the checkbox:
    hover_off_image = Image( facet_value = True )

    # The tooltip to display in the 'on' state:
    on_tooltip = Str( facet_value = True )

    # The tooltip to display in the 'off' state:
    off_tooltip = Str( facet_value = True )

    # The alignment of the text and image within the control:
    alignment = Alignment( 'center', facet_value = True )

    #-- Private Facets ---------------------------------------------------------

    # The default image to display in the checkbox (i.e. the 'on' state):
    _default_image = Image( '@facets:cb_on' )

    # The default 'off' state image to display in the checkbox:
    _default_off_image = Image( '@facets:cb_off' )

    # The default 'hover on' state image to display in the checkbox:
    _default_hover_on_image = Image( '@facets:cb_hover_on' )

    # The default 'hover off' state image to display in the checkbox:
    _default_hover_off_image = Image( '@facets:cb_hover_off' )

    #-- Facet Default Values ---------------------------------------------------

    def _image_default ( self ):
        return self._default_image


    def _off_image_default ( self ):
        if self.image is self._default_image:
            return self._default_off_image

        return hlsa_derived_image( self.image, OffTransform )


    def _hover_on_image_default ( self ):
        if self.image is self._default_image:
            return self._default_hover_on_image

        return hlsa_derived_image( self.image, HoverTransform )


    def _hover_off_image_default ( self ):
        if self.off_image is self._default_off_image:
            return self._default_hover_off_image

        return hlsa_derived_image( self.off_image, HoverTransform )

#-------------------------------------------------------------------------------
#  Helper function for creating themed checkboxes:
#-------------------------------------------------------------------------------

def themed_checkbox_editor ( style = None, show_checkbox = True, **facets ):
    """ Simplifies creation of a ThemedCheckboxEditor by setting up the
        themes and images automatically based on the value of the *style* and
        *show_checkbox* arguments.
    """
    tce = ThemedCheckboxEditor( **facets )

    if not show_checkbox:
        tce.set( image           = None,
                 on_image        = None,
                 hover_off_image = None,
                 hover_on_image  = None )

    if isinstance( style, basestring ):
        group = style[0:1].upper()
        if (len( group ) == 0) or (group not in 'BCGJTY'):
            group = 'B'

        row      = style[1:2].upper()
        all_rows = '0123456789ABCDEFGHIJKL'
        if (len( row ) == 0) or (row not in all_rows):
            row = 'H'

        column      = style[2:3].upper()
        all_columns = '12345789AB'
        if (len( column ) == 0) or (column not in all_columns):
            column = '5'

        tce.theme = '@%s%s%s' % ( group, row, column )

        if style[-1:] == '.':
            return tce

        alt_row    = '44456349A78FFFGHEFKLIJ'[ all_rows.index( row ) ]
        alt_column = '66666CCCCC'[ all_columns.index( column ) ]

        tce.set( on_theme        = '@%s%s%s' % ( group, alt_row, column ),
                 hover_on_theme  = '@%s%s%s' % ( group, alt_row, alt_column ),
                 hover_off_theme = '@%s%s%s' % ( group, row, alt_column ) )

    return tce

#-- EOF ------------------------------------------------------------------------