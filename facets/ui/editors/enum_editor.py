"""
Defines the various GUI toolkit neutral editors and the editor factory for
single-selection enumerations.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from string \
    import capitalize

from facets.api \
    import Any, Range, Enum, Property, Bool, Editor, EditorWithListFactory, \
           toolkit

from facets.ui.colors \
    import OKColor, ErrorColor

from facets.ui.helper \
    import enum_values_changed

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Supported display modes for a custom style editor
Mode = Enum( 'radio', 'list' )

#-------------------------------------------------------------------------------
#  'EnumEditor' class:
#-------------------------------------------------------------------------------

class EnumEditor ( EditorWithListFactory ):
    """ GUI toolkit neutral editor factory for enumeration editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # (Optional) Function used to evaluate text input:
    evaluate = Any

    # Is user input set on every keystroke (when text input is allowed)?
    auto_set = Bool( True )

    # Number of columns to use when displayed as a grid:
    cols = Range( 1, 20 )

    # Display modes supported for a custom style editor:
    mode = Mode

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )


    def custom_editor ( self, ui, object, name, description ):
        if self.mode == 'radio':
            return RadioEditor( factory     = self,
                                ui          = ui,
                                object      = object,
                                name        = name,
                                description = description )
        else:
            return ListEditor( factory     = self,
                               ui          = ui,
                               object      = object,
                               name        = name,
                               description = description )

#-------------------------------------------------------------------------------
#  'BaseEditor' class:
#-------------------------------------------------------------------------------

class BaseEditor ( Editor ):
    """ Base class for enumeration editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Current set of enumeration names:
    names = Property

    # Current mapping from names to values:
    mapping = Property

    # Current inverse mapping from values to names:
    inverse_mapping = Property

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if factory.name != '':
            self._object, self._name, self._value = \
                self.parse_extended_name( factory.name )
            self.values_changed()
            self._object.on_facet_set( self._values_modified,
                                       ' ' + self._name, dispatch = 'ui' )
        else:
            factory.on_facet_set( self.rebuild_editor, 'values_modified',
                                  dispatch = 'ui' )


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self._object is not None:
            self._object.on_facet_set( self._values_modified,
                                       ' ' + self._name, remove = True )
        else:
            self.factory.on_facet_set( self.rebuild_editor,
                                       'values_modified', remove = True )

        super( BaseEditor, self ).dispose()


    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** facet changes.
        """
        raise NotImplementedError


    def values_changed ( self ):
        """ Recomputes the cached data based on the underlying enumeration
            model.
        """
        self._names, self._mapping, self._inverse_mapping = \
            enum_values_changed( self._value() )

    #-- Private Methods --------------------------------------------------------

    def _get_names ( self ):
        """ Gets the current set of enumeration names.
        """
        if self._object is None:
            return self.factory._names

        return self._names


    def _get_mapping ( self ):
        """ Gets the current mapping.
        """
        if self._object is None:
            return self.factory._mapping

        return self._mapping


    def _get_inverse_mapping ( self ):
        """ Gets the current inverse mapping.
        """
        if self._object is None:
            return self.factory._inverse_mapping

        return self._inverse_mapping

    #-- Facet Event Handlers ---------------------------------------------------

    def _values_modified ( self ):
        """ Handles the underlying object model's enumeration set being changed.
        """
        self.values_changed()
        self.rebuild_editor()

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( BaseEditor ):
    """ Simple style of enumeration editor, which displays a combo box.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( SimpleEditor, self ).init( parent )

        factory = self.factory
        if factory.evaluate is None:
            self.adapter = control = toolkit().create_combobox( parent )
            control.add_items( self.names )
            control.set_event_handler( choose = self.update_object )
        else:
            self.adapter = control = toolkit().create_combobox( parent, True )
            control.add_items( self.names )
            control.set_event_handler(
                choose     = self.update_object,
                text_enter = self.update_text_object,
                lose_focus = self.on_kill_focus
            )

            if (not factory.is_grid_cell) and factory.auto_set:
                control.set_event_handler(
                    text_change = self.update_text_object
                )

        self._no_enum_update = 0

        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.adapter.unset_event_handler(
            choose      = self.update_object,
            picked      = self.update_object,
            text_enter  = self.update_text_object,
            text_change = self.update_text_object,
            lose_focus  = self.on_kill_focus
        )

        super( SimpleEditor, self ).dispose()


    def update_object ( self, event ):
        """ Handles the user selecting a new value from the combo box.
        """
        self._no_enum_update += 1
        try:
            self.value = self.mapping[ event.value ]
        except:
            pass
        self._no_enum_update -= 1


    def update_text_object ( self, event ):
        """ Handles the user typing text into the combo box text entry field.
        """
        if self._no_enum_update == 0:
            value = self.adapter.value
            try:
                value = self.mapping[ value ]
            except:
                try:
                    value = self.factory.evaluate( value )
                except Exception, excp:
                    self.error( excp )

                    return

            self._no_enum_update += 1
            try:
                self.value = value
                self.adapter.background_color = OKColor
                self.adapter.refresh()
            except:
                pass
            self._no_enum_update -= 1


    def on_kill_focus ( self, event ):
        """ Handles the control losing the keyboard focus.
        """
        self.update_text_object( event )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self._no_enum_update == 0:
            if self.factory.evaluate is None:
                try:
                    self.adapter.selection = self.inverse_mapping[ self.value ]
                except:
                    pass
            else:
                try:
                    self.adapter.value = self.str_value
                except:
                    pass


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        self.adapter.background_color = ErrorColor
        self.adapter.refresh()


    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** facet changes.
        """
        # Note: This code is unnecessarily complex due to a strange bug in
        # wxWidgets implementation of the wx.Combobox control that has strange
        # behavior when the current text field value is one of the selection
        # values when 'Clear' is called. In this case, even saving and
        # restoring the text field value does not work, so we go to great
        # lengths to detect this case and avoid using 'Clear', but still get
        # the equivalent visual results. Modify this code at your own risk...

        control  = self.adapter
        clear    = True
        cur_name = None
        if self.factory.evaluate is not None:
            n         = control.count
            cur_names = [ control.get_item( i ) for i in range( n ) ]
            cur_name  = control.value
            if cur_name in self.names:
                clear   = False
                include = True
                for i in range( n - 1, -1, -1 ):
                    if cur_name == cur_names[i]:
                        include = False
                    else:
                        control.remove_item( i )

                for name in self.names:
                    if include or (name != cur_name):
                        control.add_item( name )

                cur_name = None
            else:
                point = control.insertion_point

        if clear:
            control.clear()
            control.add_items( self.names )

        if cur_name is not None:
            self._no_enum_update   += 1
            control.value           = cur_name
            control.insertion_point = point
            self._no_enum_update   -= 1

        self.update_editor()

#-------------------------------------------------------------------------------
#  'RadioEditor' class:
#-------------------------------------------------------------------------------

class RadioEditor ( BaseEditor ):
    """ Enumeration editor, used for the "custom" style, that displays radio
        buttons.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( RadioEditor, self ).init( parent )

        # Create a panel to hold all of the radio buttons:
        self.adapter = toolkit().create_panel( parent )
        self.rebuild_editor()


    def update_object ( self, event ):
        """ Handles the user clicking one of the custom radio buttons.
        """
        try:
            self.value = event.control.value
        except:
            pass


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        value = self.value
        for button in self.control.children:
            state = (button._value == value)
            button.checked = state
            if state:
                button.set_focus()


    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** facet changes.
        """
        # Clear any existing content:
        panel  = self.adapter
        layout = panel.layout
        if layout is not None:
            layout.clear()

        # Get the current facet value:
        cur_name = self.str_value

        # Create a sizer to manage the radio buttons:
        names   = self.names
        mapping = self.mapping
        n       = len( names )
        cols    = self.factory.cols
        rows    = ( n + cols - 1 ) / cols
        incr    = [ n / cols ] * cols
        rem     = n % cols
        for i in range( cols ):
            incr[i] += (rem > i)

        incr[-1] = -(reduce( lambda x, y: x + y, incr[:-1], 0 ) - 1)
        if cols > 1:
            layout = toolkit().create_grid_layout( 0, cols, 2, 4 )
        else:
            layout = toolkit().create_box_layout()

        # Add the set of all possible choices:
        ### style = wx.RB_GROUP
        index = 0
        for i in range( rows ):
            for j in range( cols ):
                if n > 0:
                    name    = label = names[ index ]
                    label   = self.string_value( label, capitalize )
                    control = toolkit().create_radio_button( panel, label )
                    ### control = wx.RadioButton( panel, -1, label, style = style )
                    control._value = mapping[ name ]
                    ### style         = 0
                    control.checked = (name == cur_name)
                    control.set_event_handler( dialed = self.update_object )
                    self.set_tooltip( control )
                    index += incr[j]
                    n     -= 1
                else:
                    control         = toolkit().create_radio_button( panel )
                    control._value  = ''
                    control.visible = False

                layout.add( control, top = 5, fill = False )

        # Set-up the layout:
        panel.layout = layout
        panel.shrink_wrap()

#-------------------------------------------------------------------------------
#  'ListEditor' class:
#-------------------------------------------------------------------------------

class ListEditor ( BaseEditor ):
    """ Enumeration editor, used for the "custom" style, that displays a list
        box.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( ListEditor, self ).init( parent )

        # Create a panel to hold all of the radio buttons:
        self.adapter = control = toolkit().create_listbox( parent )
        control.add_items( self.names )
        control.set_event_handler( selected = self.update_object )

        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.adapter.unset_event_handler( selected = self.update_object )

        super( ListEditor, self ).dispose()


    def update_object ( self, event ):
        """ Handles the user selecting a list box item.
        """
        if not self._ignore_update:
            value = self.adapter.selection
            try:
                value = self.mapping[ value ]
            except:
                try:
                    value = self.factory.evaluate( value )
                except:
                    pass
            try:
                self.value = value
            except:
                pass


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        control = self.adapter
        try:
            index = control.find_item( self.inverse_mapping[ self.value ] )
            if index >= 0:
                control.selection = index
        except:
            pass


    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** facet changes.
        """
        self._ignore_update = True
        self.adapter.clear()
        self.adapter.add_items( self.names )
        self._ignore_update = False

        # fixme: Is this line necessary?
        self.update_editor()

#-- EOF ------------------------------------------------------------------------