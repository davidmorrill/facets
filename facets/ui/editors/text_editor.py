"""
Defines the various text editors and the text editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import logging

from facets.api \
    import Dict, Str, Any, Bool, FacetError, View, Group, toolkit, EditorFactory

from facets.ui.ui_facets \
    import AView

from facets.ui.editor_factory \
    import ReadonlyEditor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Start logging:
#-------------------------------------------------------------------------------

logger = logging.getLogger( __name__ )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Readonly text editor with view state colors:
HoverColor = ( 208, 208, 208 )
DownColor  = ( 255, 255, 255 )

# Color used to indicate unassigned modifications to a text editor value:
ModifiedColor = ( 164, 219, 235 )

#-------------------------------------------------------------------------------
#  Define a simple identity mapping:
#-------------------------------------------------------------------------------

class _Identity ( object ):
    """ A simple indentity mapping.
    """
    def __call__ ( self, value ):
        return value

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Mapping from user input text to other value
mapping_facet = Dict( Str, Any )

# Function used to evaluate textual user input
evaluate_facet = Any( _Identity() )

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( EditorFactory ):
    """ Editor factory for text editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Dictionary that maps user input to other values
    mapping = mapping_facet

    # Is user input set on every keystroke?
    auto_set = Bool( True )

    # Is user input set when the Enter key is pressed?
    enter_set = Bool( False )

    # Is multi-line text allowed?
    multi_line = Bool( True )

    # Is user input unreadable? (e.g., for a password)
    password = Bool( False )

    # Function to evaluate textual user input
    evaluate = evaluate_facet

    # The object facet containing the function used to evaluate user input
    evaluate_name = Str

    # Should a FacetError be raised in the value cannot be evaluated correctly?
    strict = Bool( False )

    # The optional view to display when a read-only text editor is clicked:
    view = AView

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View( [ 'auto_set{Set value when text is typed}',
                          'enter_set{Set value when enter is pressed}',
                          'multi_line{Allow multiple lines of text}',
                          '<extras>',
                          '|options:[Options]>' ] )

    extras = Group( 'password{Is this a password field?}' )

    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------

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
        return ReadonlyTextEditor( factory     = self,
                                   ui          = ui,
                                   object      = object,
                                   name        = name,
                                   description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style text editor, which displays a text field.
    """

    #-- Class Constants --------------------------------------------------------

    # Are multiple lines of text allowed?
    multi_line = False

    #-- Facet Definitions ------------------------------------------------------

    # Function used to evaluate textual user input:
    evaluate = evaluate_facet

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory       = self.factory
        self.evaluate = factory.evaluate
        self.sync_value( factory.evaluate_name, 'evaluate', 'from' )

        multi_line = self.multi_line
        if (not factory.multi_line) or factory.password:
            multi_line = False

        self.scrollable    = multi_line
        self._handle_enter = (factory.enter_set and (not multi_line))
        self.adapter       = adapter = toolkit().create_text_input( parent,
                                           password     = factory.password,
                                           handle_enter = self._handle_enter,
                                           multi_line   = multi_line )
        adapter.value = self.str_value
        adapter.set_event_handler( lose_focus = self.update_object )

        if self._handle_enter:
            adapter.set_event_handler( text_enter = self.update_object )
            if not factory.auto_set:
                adapter.set_event_handler( text_change = self.check_update )

        if factory.auto_set:
            adapter.set_event_handler( text_change = self.update_object )

        self.set_tooltip()


    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        adapter = self.adapter
        color   = getattr( adapter, '_bg_color', None )
        if color is not None:
            adapter.background_color = color
            del adapter._bg_color
            adapter.refresh()

        if (not self._no_update) and (self.control is not None):
            try:
                self.value = self._get_user_value()

                if self._error is not None:
                    self._error     = None
                    self.ui.errors -= 1

                self.set_error_state( False )

            except FacetError, excp:
                pass


    def check_update ( self, event ):
        """ Handles an update that occurs when 'enter_set' is active but
            'auto_set' is not.
        """
        adapter = self.adapter
        if getattr( adapter, '_bg_color', None ) is None:
            adapter._bg_color        = adapter.background_color
            adapter.background_color = ModifiedColor
            adapter.refresh()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        user_value = self._get_user_value()
        try:
            unequal = bool( user_value != self.value )
        except ValueError:
            # This might be a numpy array:
            unequal = True

        if unequal:
            self._no_update    = True
            self.adapter.value = self.str_value
            self._no_update    = False

        if self._error is not None:
            self._error     = None
            self.ui.errors -= 1
            self.set_error_state( False )


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        if self._error is None:
            self._error     = True
            self.ui.errors += 1

        self.set_error_state( True )


    def in_error_state ( self ):
        """ Returns whether or not the editor is in an error state.
        """
        return (self.invalid or self._error)


    def dispose ( self ):
        """ Disposes of the editor.
        """
        control = self.adapter
        control.unset_event_handler( lose_focus = self.update_object )

        if self._handle_enter:
            control.unset_event_handler( text_enter = self.update_object )
            if not self.factory.auto_set:
                control.unset_event_handler( text_change = self.check_update )

        if self.factory.auto_set:
            control.unset_event_handler( text_change = self.update_object )

        super( SimpleEditor, self ).dispose()

    #-- Private Methods --------------------------------------------------------

    def _get_user_value ( self ):
        """ Gets the actual value corresponding to what the user typed.
        """
        value = self.adapter.value
        try:
            value = self.evaluate( value )
        except:
            msg = 'Could not evaluate %r in TextEditor' % ( value, )
            if self.factory.strict:
                raise FacetError( msg )
            else:
                logger.exception( msg )

        try:
            return self.factory.mapping.get( value, value )
        except TypeError:
            # The value is probably not hashable:
            return value

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style of text editor, which displays a multi-line text field.
    """

    #-- Class Constants --------------------------------------------------------

    # Are multiple lines of text allowed?
    multi_line = True

#-------------------------------------------------------------------------------
#  'ReadonlyTextEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyTextEditor ( ReadonlyEditor ):
    """ Read-only style of text editor, which displays a read-only text field.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( ReadonlyTextEditor, self ).init( parent )

        if self.factory.view is not None:
            self.adapter.set_event_handler(
                enter     = self._enter_window,
                leave     = self._leave_window,
                left_down = self._left_down,
                left_up   = self._left_up
            )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        control   = self.adapter
        new_value = self.str_value

        if self.factory.password:
            new_value = '*' * len( new_value )

        if control.value != new_value:
            control.value = new_value
            if (self.item.resizable is True) or (self.item.height != -1.0):
                n = len( new_value )
                control.selection = ( n, n )


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self.factory.view is not None:
            self.adapter.unset_event_handler(
                enter     = self._enter_window,
                leave     = self._leave_window,
                left_down = self._left_down,
                left_up   = self._left_up
            )

        super( ReadonlyTextEditor, self ).dispose()

    #-- Private Methods --------------------------------------------------------

    def _set_color ( self ):
        control = self.adapter
        if not self._in_window:
            color = control.parent.background_color
        elif self._down:
            color = DownColor
        else:
            color = HoverColor

        control.background_color = color
        control.refresh()

    #-- Control Event Handlers ------------------------------------------------

    def _enter_window ( self, event ):
        self._in_window = True
        self._set_color()


    def _leave_window ( self, event ):
        self._in_window = False
        self._set_color()


    def _left_down ( self, event ):
        self.adapter.mouse_capture = True
        self._down = True
        self._set_color()


    def _left_up ( self, event ):
        if not self._down:
            self._set_color()

            return

        self.adapter.mouse_capture = False
        self._down = False
        self._set_color()

        if self._in_window:
            self.object.edit_facets( view   = self.factory.view,
                                     parent = self.control )

#-- EOF ------------------------------------------------------------------------