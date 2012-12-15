"""
Defines the various button editors and the button editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Int, Str, Range, Enum, Property, View, EditorFactory

from facets.ui.ui_facets \
    import AView, Image

from facets.ui.toolkit \
    import toolkit

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'ButtonEditor' class:
#-------------------------------------------------------------------------------

class ButtonEditor ( EditorFactory ):
    """ Editor factory for buttons.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Value to set when the button is clicked:
    value = Property

    # Optional label for the button:
    label = Str

    # The name of the external object facet that the button label is synced to:
    label_value = Str

    # (Optional) Image to display on the button:
    image = Image

    # The maximum size of the image to display (0 = No maximum):
    image_size = Int

    # Extra padding to add to both the left and the right sides:
    width_padding = Range( 0, 31, 7 )

    # Extra padding to add to both the top and the bottom sides:
    height_padding = Range( 0, 31, 5 )

    # Presentation style:
    style = Enum( 'button', 'radio', 'toolbar', 'checkbox' )

    # Orientation of the text relative to the image:
    orientation = Enum( 'vertical', 'horizontal' )

    # The optional view to display when the button is clicked:
    view = AView

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View( [ 'label', 'value', '|[]' ] )

    #-- Property Implementations -----------------------------------------------

    def _get_value ( self ):
        return self._value

    def _set_value ( self, value ):
        self._value = value
        if isinstance( value, basestring ):
            try:
                self._value = int( value )
            except:
                try:
                    self._value = float( value )
                except:
                    pass

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, **facets ):
        self._value = 0

        super( ButtonEditor, self ).__init__( **facets )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )


    def custom_editor ( self, ui, object, name, description ):
        return CustomEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style editor for a button.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The button label
    label = Str

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label        = self.factory.label or self.item.get_label( self.ui )
        self.adapter = toolkit().create_button( parent,
                                                self.string_value( label ) )
        self.adapter.set_event_handler( clicked = self.update_object )
        self.sync_value( self.factory.label_value, 'label', 'from' )

        self.set_tooltip()


    def update_object ( self, event ):
        """ Handles the user clicking the button by setting the factory value
            on the object.
        """
        factory    = self.factory
        self.value = factory.value

        # If there is an associated view, then display it:
        if factory.view is not None:
            self.object.edit_facets( view   = factory.view,
                                     parent = self.control )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        pass


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.adapter.unset_event_handler( clicked = self.update_object )

        super( SimpleEditor, self ).dispose()

    #-- Facet Event Handlers ---------------------------------------------------

    def _label_set ( self, label ):
        self.adapter.value = label

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style editor for a button, which can contain an image.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        from facets.ui.controls.image_button import ImageButton

        factory       = self.factory
        self._control = ImageButton(
            parent,
            label          = self.string_value( factory.label ),
            image          = factory.image,
            image_size     = factory.image_size,
            style          = factory.style,
            orientation    = factory.orientation,
            width_padding  = factory.width_padding,
            height_padding = factory.height_padding
        )
        self.adapter = self._control.control
        self._control.on_facet_set( self.update_object, 'clicked',
                                    dispatch = 'ui' )

        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self._control.on_facet_set( self.update_object, 'clicked',
                                    remove = True )

        super( CustomEditor, self ).dispose()

#-- EOF ------------------------------------------------------------------------