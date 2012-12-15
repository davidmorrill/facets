"""
Defines the various editors and editor factory for a GUI toolkit neutral
drag-and-drop editor. A drag-and-drop editor represents its value as a simple
image which, depending upon the editor style, can be a drag source only, a drop
target only, or both a drag source and a drop target.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Enum, Str, Callable, Editor, EditorFactory, FacetError, \
           image_for, toolkit

from facets.core.facet_base \
    import SequenceTypes

from facets.ui.ui_facets \
    import Image

from facets.extra.helper.image \
    import hlsa_derived_image, DisabledTransform

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The image to use when the editor accepts files:
file_image = image_for( '@facets:file' )

# The image to use when the editor accepts objects:
object_image = image_for( '@facets:object' )

# The image to use when the editor is disabled:
inactive_image = image_for( '@facets:inactive' )

# String types:
string_type = ( str, unicode )

#-------------------------------------------------------------------------------
#  'DNDEditor' class:
#-------------------------------------------------------------------------------

class DNDEditor ( EditorFactory ):
    """ GUI toolkit neutral editor factory for drag-and-drop editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The image to use for the target:
    image = Image

    # The image to use when the target is disabled:
    disabled_image = Image

    # The type of data the value being dragged represents:
    type = Enum( 'object', 'color', 'image', 'text', 'html', 'files', 'urls',
                 'auto' )

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


    def text_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )


    def readonly_editor ( self, ui, object, name, description ):
        return ReadOnlyEditor( factory     = self,
                               ui          = ui,
                               object      = object,
                               name        = name,
                               description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style of editor for a drag-and-drop editor, which is both a drag
        source and a drop target.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the editor a drop target?
    drop_target = Bool( True )

    # Is the editor a drag source?
    drag_source = Bool( True )

    # The type of data the value being dragged represents:
    type = Str

    #-- Private Facet Definitions ----------------------------------------------

    # The validator function used to validate data being dragged:
    validator = Callable

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Determine the drag/drop type:
        self.type = self.factory.type
        if self.type == 'auto':
            value = self.value
            if (isinstance( value, string_type ) or
                (isinstance( value, list ) and (len( value ) > 0) and
                 isinstance( value[0], string_type ))):
                self.type = 'files'

        # Get the right image to use:
        image = self.factory.image
        if image is not None:
            disabled_image = (self.factory.disabled_image or
                              hlsa_derived_image( image, DisabledTransform ))
        else:
            disabled_image = inactive_image
            image          = object_image
            if self.type == 'files':
                image = file_image

        self._image          = image
        self._disabled_image = disabled_image

        # Create the control and set up the event handlers:
        self.adapter     = control = toolkit().create_control( parent )
        control.min_size = ( image.width, image.height )

        control.set_event_handler(
            left_down = self._left_down,
            left_up   = self._left_up,
            motion    = self._mouse_move,
            paint     = self._on_paint
        )

        if self.drop_target:
            control.drop_target = self

        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.adapter.unset_event_handler(
            left_down = self._left_down,
            left_up   = self._left_up,
            motion    = self._mouse_move,
            paint     = self._on_paint
        )

        super( SimpleEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        return

    #-- Default Facet Values ---------------------------------------------------

    def _validator_default ( self ):
        return self.object.base_facet( self.name ).validate

    #-- Control Event Handlers -------------------------------------------------

    def _on_paint ( self, event ):
        """ Called when the control needs repainting.
        """
        image   = self._image
        control = self.adapter
        if not control.enabled:
            image = self._disabled_image

        cdx, cdy = control.client_size
        control.graphics.draw_bitmap(
            image.bitmap, (cdx - image.width) / 2, (cdy - image.height) / 2
        )


    def _left_down ( self, event ):
        """ Handles the left mouse button being pressed.
        """
        if self.adapter.enabled and self.drag_source:
            self._x, self._y           = event.x, event.y
            self.adapter.mouse_capture = True

        event.handled = False


    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if self._x is not None:
            self._x = None
            self.adapter.mouse_capture = False

        event.handled = False


    def _mouse_move ( self, event ):
        """ Handles the mouse being moved.
        """
        if self._x is not None:
            if ((abs( self._x - event.x ) +
                 abs( self._y - event.y )) >= 3):
                self.adapter.mouse_capture = False
                self._x = None
                value   = self.value
                type    = self.type
                if (type == 'files') and (value not in SequenceTypes):
                    value = ( value, )

                self.adapter.drag( self.value, type )

        event.handled = False

    #-- Drag and drop Event Handlers: ------------------------------------------

    def drag_drop ( self, event ):
        """ Handles something being dropped on the editor.
        """
        self._drag_assign( setattr, event )


    def drag_move ( self, event ):
        """ Handles something being dragged over the editor.
        """
        self._drag_assign( self.validator, event )

    #-- Private Methods --------------------------------------------------------

    def _drag_assign ( self, assign, event ):
        """ Attempts to perform the type of drag assignment specified by assign
            for the data associated with the specified drag event.
        """
        kind, data = self._get_drag_data( event )
        try:
            assign( self.object, self.name, data )
            event.result = event.request
        except:
            retry = getattr( self, '_drag_assign_' + kind, None )
            if retry is not None:
                try:
                    retry( assign, event, data )
                    event.result = event.request

                    return
                except:
                    pass

            event.result = 'ignore'

    def _drag_assign_files ( self, assign, event, files ):
        """ Attempt to assign a list of file names to a facet which may only
            want a single value.
        """
        if len( files ) != 1:
            raise FacetError

        assign( self.object, self.name, files[0] )


    def _get_drag_data ( self, event ):
        """ Returns the data associated with a specified drag event.
        """
        if event.has_text:
            return ( 'text', event.text )

        if event.has_color:
            return ( 'color', event.color )

        if event.has_image:
            return ( 'image', event.image )

        if event.has_files:
            return ( 'files', event.files )

        if event.has_urls:
            return ( 'urls', event.urls )

        if event.has_html:
            return ( 'html', event.html )

        if event.has_object:
            return ( 'object', event.object )

        return ( 'none', None )

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style of drag-and-drop editor, which is not a drag source.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the editor a drag source? This value overrides the default.
    drag_source = False

#-------------------------------------------------------------------------------
#  'ReadOnlyEditor' class:
#-------------------------------------------------------------------------------

class ReadOnlyEditor ( SimpleEditor ):
    """ Read-only style of drag-and-drop editor, which is not a drop target.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the editor a drop target? This value overrides the default.
    drop_target = False

#-- EOF ------------------------------------------------------------------------