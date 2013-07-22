"""
Facets UI simple, read-only single line text editor with a themed (i.e. image)
background.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Dict, Str, Any, Image, Instance, Property, FacetError, \
           cached_property, toolkit, EditorFactory

from facets.ui.colors \
    import OKColor, ErrorColor

from facets.ui.ui_facets \
    import ATheme

from facets.ui.pyface.image_slice \
    import paint_parent, default_image_slice

from facets.ui.controls.themed_control \
    import ThemedControl

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Define a simple identity mapping:
#-------------------------------------------------------------------------------

class _Identity ( object ):
    """ A simple indentity mapping.
    """
    def __call__ ( self, value ):
        return value

#-------------------------------------------------------------------------------
#  'ThemedTextEditor' class:
#-------------------------------------------------------------------------------

class ThemedTextEditor ( EditorFactory ):
    """ Facets UI simple, single line text editor with a themed (i.e. image)
        background.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The background theme image to display:
    theme = ATheme

    # Dictionary that maps user input to other values:
    mapping = Dict( Str, Any )

    # Is user input set on every keystroke?
    auto_set = Bool( True )

    # Is user input set when the Enter key is pressed?
    enter_set = Bool( False )

    # Is user input unreadable? (e.g., for a password)
    password = Bool( False )

    # Function to evaluate textual user input:
    evaluate = Any

    # The object facet containing the function used to evaluate user input:
    evaluate_name = Str

    #-- 'readonly' Style Facets ------------------------------------------------

    # The optional image to display adjacent to the text:
    image = Image

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return _ThemedTextEditor( factory     = self,
                                  ui          = ui,
                                  object      = object,
                                  name        = name,
                                  description = description )


    def custom_editor ( self, ui, object, name, description ):
        return _ThemedTextEditor( factory     = self,
                                  ui          = ui,
                                  object      = object,
                                  name        = name,
                                  description = description )


    def text_editor ( self, ui, object, name, description ):
        return _ThemedTextEditor( factory     = self,
                                  ui          = ui,
                                  object      = object,
                                  name        = name,
                                  description = description )


    def readonly_editor ( self, ui, object, name, description ):
        return _ReadonlyTextEditor( factory     = self,
                                    ui          = ui,
                                    object      = object,
                                    name        = name,
                                    description = description )

#-------------------------------------------------------------------------------
#  '_ThemedTextEditor' class:
#-------------------------------------------------------------------------------

class _ThemedTextEditor ( Editor ):
    """ Facets UI simple, single line text editor with a themed (i.e. image
        background).
    """

    #-- Facet Definitions ------------------------------------------------------

    # Function used to evaluate textual user input:
    evaluate = Any

    # The text alignment to use:
    alignment = Property

    # The image slice to use:
    image_slice = Property

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory  = self.factory
        evaluate = factory.evaluate
        if evaluate is None:
            handler  = self.object.facet( self.name ).handler
            evaluate = getattr( handler, 'evaluate', None )
            if evaluate is None:
                evaluate = _Identity()

        self.evaluate = evaluate
        self.sync_value( factory.evaluate_name, 'evaluate', 'from' )

        padding_x = padding_y = 0
        if factory.theme is not None:
            slice     = self.image_slice
            padding_x = slice.xleft + slice.xright
            padding_y = slice.xtop  + slice.xbottom

        self.adapter = control = toolkit().create_control( parent,
                                                           handle_keys = True )
        control.min_size = ( padding_x + 20, padding_y + 20 )

        self._text_size = None

        # Set up the control's event handlers:
        control.set_event_handler(
            paint     = self._on_paint,
            key       = self._inactive_key_entered,
            get_focus = self._set_focus,
            left_up   = self._set_focus,
            size      = self._resize
        )

        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        # Remove all of the control's event listeners:
        self.adapter.unset_event_handler(
            paint     = self._on_paint,
            key       = self._inactive_key_entered,
            get_focus = self._set_focus,
            left_up   = self._set_focus,
            size      = self._resize
        )

        super( _ThemedTextEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self._text is None:
            self._refresh()

            return

        if self._get_user_value() != self.value:
            self._no_update  = True
            self._text.value = self.str_value
            self._no_update  = False

        if self._error is not None:
            self._error                 = None
            self.ui.errors             -= 1
            self._text.background_color = OKColor
            self._text.refresh()


    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._no_update:
            try:
                self.value                  = self._get_user_value()
                self._text.background_color = OKColor
                self._text.refresh()

                if self._error is not None:
                    self._error     = None
                    self.ui.errors -= 1

                return True

            except FacetError, excp:
                return False


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        self._text.background_color = ErrorColor
        self._text.refresh()
        toolkit().beep()

        if self._error is None:
            self._error     = True
            self.ui.errors += 1

    #-- Private Methods --------------------------------------------------------

    def _get_user_value ( self ):
        """ Gets the actual value corresponding to what the user typed.
        """
        value = self._text.value
        try:
            value = self.evaluate( value )
        except:
            pass

        return self.factory.mapping.get( value, value )


    def _pop_up_text ( self ):
        """ Pop-up a text control to allow the user to enter a value using
            the keyboard.
        """
        control     = self.adapter
        factory     = self.factory
        self._text  = text = toolkit().create_text_input( control(),
                                 password     = factory.password,
                                 handle_enter = True,
                                 align        = self.alignment )
        text.value  = self.str_value
        slice       = self.image_slice
        wdx, wdy    = control.client_size
        tdx, tdy    = text.size
        text.bounds = ( slice.xleft,
                        ((wdy + slice.xtop - slice.xbottom - tdy) / 2) + 1,
                        wdx - slice.xleft - slice.xright,
                        tdy )
        text.selection = ( -1, -1 )
        text.set_focus()

        text.set_event_handler(
            lose_focus = self._text_completed,
            key        = self._key_entered,
            text_enter = self.update_object
        )

        if factory.auto_set and (not factory.is_grid_cell):
            text.set_event_handler( text_change = self.update_object )


    def _destroy_text ( self ):
        """ Destroys the current text control.
        """
        self.adapter.destroy_children()
        self._text = None


    def _refresh ( self ):
        """ Refreshes the contents of the control.
        """
        if self._text_size is not None:
            self.adapter.refresh( *self._get_text_bounds() )
            self._text_size = None


    def _get_text_size ( self ):
        """ Returns the text size information for the window.
        """
        if self._text_size is None:
            self._text_size = self.adapter.text_size( self._get_text() or 'M' )

        return self._text_size


    def _get_text_bounds ( self ):
        """ Get the window bounds of where the current text should be
            displayed.
        """
        tdx, tdy  = self._get_text_size()
        wdx, wdy  = self.adapter.client_size
        slice     = self.image_slice
        ady       = wdy - slice.xtop  - slice.xbottom
        ty        = slice.xtop + ((ady - tdy) / 2) - 1
        alignment = self.alignment
        if alignment == 'center':
            adx = wdx - slice.xleft - slice.xright
            tx  = slice.xleft + ((adx - tdx) / 2)
        elif alignment == 'right':
            tx = wdx - tdx - slice.xright - 4
        else:
            tx = slice.xleft + 4

        return ( tx, ty, tdx, tdy )


    def _get_text ( self ):
        """ Returns the current text to display.
        """
        if self.factory.password:
            return '*' * len( self.str_value )

        return self.str_value

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_alignment ( self ):
        theme = self.factory.theme
        if theme is not None:
            return theme.alignment

        return 'left'


    @cached_property
    def _get_image_slice ( self ):
        theme = self.factory.theme
        if theme is not None:
            return theme.image_slice or default_image_slice

        return default_image_slice

    #-- Control Event Handlers -------------------------------------------------

    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        control  = self.adapter
        g        = control.graphics.graphics_buffer()
        slice    = paint_parent( g, control )
        slice2   = self.image_slice
        if slice2 is not default_image_slice:
            wdx, wdy = control.client_size
            slice2.fill( g, 0, 0, wdx, wdy )
            slice = slice2
        elif slice is None:
            slice = slice2

        g.text_background_color = None
        g.text_color            = slice.content_color
        g.font                  = control.font
        tx, ty, tdx, tdy        = self._get_text_bounds()
        g.draw_text( self._get_text(), tx, ty )
        g.copy()


    def _resize ( self, event ):
        """ Handles the control being resized.
        """
        if self._text is not None:
            self._text.size = self.adapter.size


    def _set_focus ( self, event ):
        """ Handle the control getting the keyboard focus.
        """
        if self._text is None:
            self._pop_up_text()

        event.handled = False


    def _text_completed ( self, event ):
        """ Handles the user transferring focus out of the text control.
        """
        if self.update_object( event ):
            self._destroy_text()


    def _key_entered ( self, event ):
        """ Handles individual key strokes while the text control is active.
        """
        key_code = event.key_code
        if key_code == 'Esc':
            self._destroy_text()

            return

        if key_code == 'Tab':
            if self.update_object( event ):
                self.adapter.tab( not event.shift_down )

            return

        event.handled = False


    def _inactive_key_entered ( self, event ):
        """ Handles individual key strokes while the text control is inactive.
        """
        if event.key_code == 'Enter':
            if self._text is None:
                self._pop_up_text()

            return

        event.handled = False

#-------------------------------------------------------------------------------
#  '_ReadonlyTextEditor' class:
#-------------------------------------------------------------------------------

class _ReadonlyTextEditor ( Editor ):
    """ Facets UI simple, read-only single line text view with a themed (i.e.
        image background).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The themed control used to implement the editor:
    themed_control = Instance( ThemedControl )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        theme = self.factory.theme
        self.themed_control = ThemedControl(
            theme     = theme,
            image     = self.factory.image,
            alignment = (theme.alignment if theme is not None else 'left'),
            parent    = parent
        )
        self.adapter = self.themed_control()
        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.themed_control.text = self.value

        # Make sure the control is sized correctly:
        self.adapter.min_size = self.themed_control.best_size

#-- EOF ------------------------------------------------------------------------