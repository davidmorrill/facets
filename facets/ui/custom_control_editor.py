"""
Defines the CustomControlEditor class, which allows creating editor factories
that use a custom control class for creating all editor styles. It also defines
the ControlEditor base class for creating custom controls for use with the
CustomControlEditor class.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Range, Tuple, Str, Bool, Any, Instance

from facets.ui.controls.themed_window \
    import ThemedWindow

from facets.ui.adapters.control \
    import Control

from facets.ui.editor \
    import Editor as BaseEditor

from facets.ui.editors.editor \
    import Editor

from ui_facets \
    import ATheme

from editor_factory \
    import EditorFactory

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The tuple used to indicate no size information is specified:
UndefinedSize = ( -1, -1 )

#-------------------------------------------------------------------------------
#  'ControlEditor' class:
#-------------------------------------------------------------------------------

class ControlEditor ( ThemedWindow ):
    """ The base class for creating custom controls for use with a
        CustomControlEditor factory. It subclasses ThemedWindow and adds a
        number of useful features for defining custom control editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Reference to the associated editor factory (set by the editor prior to
    # calling 'init'):
    factory = Instance( EditorFactory )

    # Reference to the associated editor (set by the editor prior to calling
    # 'init'):
    editor = Instance( Editor )

    # The value the control is editing (the facet type should be set correctly):
    # value = Any

    # The virtual size of the control (UndefinedSize for a non-scrollable
    # control, and a ( width, height ) tuple for a scrollable control):
    virtual_size = Tuple( UndefinedSize )

    # The fixed size of the control (UndefinedSize for a variable size control,
    # and a ( width, height ) tuple for a fixed size control of the given size):
    fixed_size = Tuple( UndefinedSize )

    # For controls with a non-UndefinedSize 'virtual_size', this is the control
    # that manages the scroll area:
    scroll_control = Instance( Control )

    # The base rate at which the mouse wheel scrolls:
    wheel_rate = Range( 0, 256, 32 )

    # Is the default mouse wheel scroll direction vertical (True) or horizontal
    # (False)?
    scroll_vertical = Bool( True )

    #-- Public Methods ---------------------------------------------------------

    def init ( self ):
        """ Allows the control to perform any needed initialization. Called
            immediately after the constructor has run and all externally set
            attributes have been initialized.
        """


    def post_init ( self ):
        """ Allows the control to perform any needed initialization. Called
            after the parent editor has finished all initialization of the
            control.
        """


    def dispose ( self ):
        """ Disposes of the editor when it is no longer needed.
        """
        super( ControlEditor, self ).dispose()

        self.factory = self.editor = self.scroll_control = None


    def scroll_by ( self, x = 0, y = 0 ):
        """ For controls with a non-UndefinedSize 'virtual_size', scrolls the
            contents of the control by the amount specified by *x* and *y*.
        """
        scroller = self.scroll_control
        if (scroller is not None) and ((x != 0) or (y != 0)):
            vx, vy, vdx, vdy = self.control.visible_bounds
            if x < 0:
                px = max( 0, vx + x )
            else:
                px = vx + vdx + x

            if y < 0:
                py = max( 0, vy + y )
            else:
                py = vy + vdy + y

            scroller.scroll_to( px, py )

    #-- Window Event Handlers --------------------------------------------------

    def paint_all ( self, g ):
        """ Paint the background using the associated ImageSlice object.
        """
        g.font = self.factory.font
        self.paint_bg( g )
        self.paint( g )


    def paint_label ( self, g ):
        """ Paints the item label of the window into the supplied device
            context.
        """
        editor = self.editor
        dx, dy = self.control.client_size
        self.theme.draw_label(
            g, editor.item.get_label( editor.ui ), None, 0, 0, dx, dy
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self ):
        """ Handles the 'value' facet being changed.
        """
        self.refresh()


    def _virtual_size_set ( self, vs ):
        """ Handles the 'virtual_size' facet being changed.
        """
        if (vs != UndefinedSize) and (self.control is not None):
            self.control.virtual_size = vs

    #-- Mouse Event Handlers ---------------------------------------------------

    def wheel ( self, event ):
        """ Handles the user scrolling the mouse wheel.
        """
        if event.alt_down:
            self._mouse_event( 'alt_wheel', event )
        else:
            rate = self.wheel_rate
            if (self.scroll_control is not None) and (rate > 0):
                delta = (-event.wheel_change * rate *
                         (1 + (3 * event.shift_down)))
                cd    = event.control_down ^ (not self.scroll_vertical)
                self.scroll_by( delta * cd, delta * (not cd) )

#-------------------------------------------------------------------------------
#  'DefaultCustomControlEditor' class:
#-------------------------------------------------------------------------------

class DefaultCustomControlEditor ( Editor ):
    """ Defines a private Editor class for connecting a custom control specified
        with a CustomControlEditor to help it support the standard Facets Editor
        protocol.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The custom editor control used to implement the editor:
    editor_control = Instance( ControlEditor )

    #-- Editor Method Overrides ------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory             = self.factory
        self.editor_control = control = factory.klass()
        control.factory     = factory
        control.editor      = self
        control.init()

        scroller = None
        if control.virtual_size != UndefinedSize:
            scroller = parent = toolkit().create_scrolled_panel( parent )

        control.parent  = parent
        control.theme   = factory.theme
        ui_control      = control()
        fixed_size      = control.fixed_size
        self.scrollable = (fixed_size == UndefinedSize)

        if factory.refresh != '':
            control.on_facet_set( control.refresh, factory.refresh )

        if scroller is not None:
            control.scroll_control  = scroller
            scroller.content        = ui_control
            ui_control.virtual_size = control.virtual_size
            ui_control              = scroller

        if fixed_size != UndefinedSize:
            ui_control.min_size = fixed_size

        self.adapter = ui_control

        if self.extended_name != 'None':
            object = self.context_object
            name   = self.extended_name
            if control.facet( 'value' ) is None:
                if isinstance( object, BaseEditor ) and (name == 'value'):
                    # FIXME: Handle the special case of an Editor's 'value'
                    # facet, which is a property, which doesn't work well as is,
                    # so we reach down into the editor to extract the actual
                    # object facet being referenced:
                    name   = object.name
                    object = object.object

                control.add_facet( 'value', object.facet( name ) )

            object.sync_facet( name, control, 'value', True )

        self.set_tooltip()
        control.post_init()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        control = self.editor_control
        if self.extended_name != 'None':
            self.context_object.sync_facet(
                self.extended_name, control, 'value', True, True
            )

        if self.factory.refresh != '':
            control.on_facet_set(
                control.refresh, self.factory.refresh, remove = True
            )

        control.dispose()
        self.editor_control = None

        super( DefaultCustomControlEditor, self ).dispose()

#-------------------------------------------------------------------------------
#  'CustomControlEditor' base class:
#-------------------------------------------------------------------------------

class CustomControlEditor ( EditorFactory ):
    """ Base class for editor factories that use a custom control class for
        creating all editor styles.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The optional custom editor class to be instantiated:
    editor_klass = Any( DefaultCustomControlEditor )

    # The custom control class to be instantiated:
    klass = Any

    # The theme associated with this editor's custom control:
    theme = ATheme

    # The facets whose changes should cause the control to be refreshed:
    refresh = Str

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return self.editor_klass(
            factory     = self,
            ui          = ui,
            object      = object,
            name        = name,
            description = description
        )


    def custom_editor ( self, ui, object, name, description ):
        return self.editor_klass(
            factory     = self,
            ui          = ui,
            object      = object,
            name        = name,
            description = description
        )


    def text_editor ( self, ui, object, name, description ):
        return self.editor_klass(
            factory     = self,
            ui          = ui,
            object      = object,
            name        = name,
            description = description
        )


    def readonly_editor ( self, ui, object, name, description ):
        return self.editor_klass(
            factory     = self,
            ui          = ui,
            object      = object,
            name        = name,
            description = description
        )

    #-- Public Method Overrides ------------------------------------------------

    def __call__ ( self, *args, **facets ):
        return self.set( **facets )

#-- EOF ------------------------------------------------------------------------
