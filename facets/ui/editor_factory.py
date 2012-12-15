"""
Defines the abstract EditorFactory class, which represents a factory for
creating the Editor objects used in a Facets-based user interface.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Callable, Str, Bool, FacetError, Any, Event, Font

from editor \
    import Editor

from toolkit \
    import toolkit

from colors \
    import WindowColor

from helper \
    import enum_values_changed

#-------------------------------------------------------------------------------
#  'EditorFactory' abstract base class:
#-------------------------------------------------------------------------------

class EditorFactory ( HasPrivateFacets ):
    """ Represents a factory for creating the Editor objects in a Facets-based
        user interface.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Function to use for string formatting:
    format_func = Callable

    # Format string to use for formatting (used if **format_func** is not set):
    format_str = Str

    # The font that the editor control should use:
    font = Font

    # The extended facet name of the facet containing editor invalid state
    # status:
    invalid = Str

    # Are created editors initially enabled?
    enabled = Bool( True )

    # Is the editor being used to create table grid cells?
    is_grid_cell = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, *args, **facets ):
        """ Initializes the factory object.
        """
        HasPrivateFacets.__init__( self, **facets )

        self.init( *args )


    def init ( self ):
        """ Performs any initialization needed after all constructor facets
            have been set.
        """
        pass


    def named_value ( self, name, ui ):
        """ Returns the value of a specified extended name of the form: name or
            context_object_name.name[.name...]:
        """
        names = name.split( '.' )

        if len( names ) == 1:
            # fixme: This will produce incorrect values if the actual Item the
            # factory is being used with does not use the default object='name'
            # value, and the specified 'name' does not contain a '.'. The
            # solution will probably involve providing the Item as an argument,
            # but it is currently not available at the time this method needs to
            # be called...
            names.insert( 0, 'object' )

        value = ui.context[ names[0] ]
        for name in names[1:]:
            value = getattr( value, name )

        return value

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, facet_name, description ):
        """ Generates an editor using the "simple" style.
        """
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = facet_name,
                             description = description )


    def custom_editor ( self, ui, object, facet_name, description ):
        """ Generates an editor using the "custom" style.
        """
        return self.simple_editor( ui, object, facet_name, description )


    def text_editor ( self, ui, object, facet_name, description ):
        """ Generates an editor using the "text" style.
        """
        return TextEditor( factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = facet_name,
                           description = description )


    def readonly_editor ( self, ui, object, facet_name, description ):
        """ Generates an "editor" that is read-only.
        """
        return ReadonlyEditor( factory     = self,
                               ui          = ui,
                               object      = object,
                               name        = facet_name,
                               description = description )

#-------------------------------------------------------------------------------
#  'EditorWithListFactory' base class:
#-------------------------------------------------------------------------------

class EditorWithListFactory ( EditorFactory ):
    """ Base class for factories of editors for objects that contain lists.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Values to enumerate (can be a list, tuple, dict, or a CFacet or
    # FacetHandler that is "mapped"):
    values = Any

    # Extended name of the facet on **object** containing the enumeration data:
    object = Str( 'object' )

    # Name of the facet on 'object' containing the enumeration data:
    name = Str

    # Fired when the **values** facet has been updated:
    values_modified = Event

    #-- Facet Event Handlers ---------------------------------------------------

    def _values_set ( self ):
        """ Recomputes the mappings whenever the **values** facet is changed.
        """
        self._names, self._mapping, self._inverse_mapping = \
            enum_values_changed( self.values )

        self.values_modified = True

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Base class for simple style editors, which displays a text field
        containing the text representation of the object facet value. Clicking
        in the text field displays an editor-specific dialog box for changing
        the value.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Has the left mouse button been pressed:
    left_down = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.adapter = control = self.create_control( parent )
        control.set_event_handler(
            left_down = self._enable_popup_editor,
            left_up   = self._show_popup_editor
        )

        self.set_tooltip()


    def create_control ( self, parent ):
        """ Creates the control to use for the simple editor.
        """
        return toolkit().create_text_input( parent, read_only = True ).set(
                   value = self.str_value )


    def popup_editor ( self ):
        """ Invokes the pop-up editor for an object facet.

            Normally overridden in a subclass.
        """
        pass

    #-- Control Event Handlers -------------------------------------------------

    def _enable_popup_editor ( self, event ):
        """ Mark the left mouse button as being pressed currently.
        """
        self.left_down = True


    def _show_popup_editor ( self, event ):
        """ Display the popup editor if the left mouse button was pressed
            previously.
        """
        if self.left_down:
            self.left_down = False
            self.popup_editor()

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( Editor ):
    """ Base class for text style editors, which displays an editable text
        field, containing a text representation of the object facet value.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.adapter  = control = toolkit().create_text_input( parent )
        control.value = self.str_value

        control.set_event_handler(
            lose_focus = self.update_object,
            text_enter = self.update_object
        )

        self.set_tooltip()


    def dispose ( self ):
        """ Handles the editor being closed.
        """
        self.adapter.unset_event_handler(
            lose_focus = self.update_object,
            text_enter = self.update_object
        )

        super( TextEditor, self ).dispose()


    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            self.value = self.adapter.value
        except FacetError:
            pass

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( Editor ):
    """ Base class for read-only style editors, which displays a read-only text
        field, containing a text representation of the object facet value.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if (self.item.resizable is True) or (self.item.height != -1.0):
            self.adapter = toolkit().create_text_input(
                parent, read_only = True, multi_line = True ).set(
                value            = self.str_value,
                background_color = WindowColor )
        else:
            self.adapter = toolkit().create_label( parent ).set(
                value = self.str_value
            )
            # fixme: How to do this in GUI toolkit neutral manner?...
            ###self.layout_style = 0

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        new_value = self.str_value
        if self.adapter.value != new_value:
            self.adapter.value = new_value

#-- EOF ------------------------------------------------------------------------