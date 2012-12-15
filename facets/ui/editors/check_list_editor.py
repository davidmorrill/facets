"""
Defines the various GUI toolkit neutral editors and the editor factory for
multi-selection enumerations.
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
    import Range, List, Str, FacetError, EditorWithList, \
           EditorWithListFactory, toolkit

from facets.ui.editor_factory \
    import TextEditor as BaseTextEditor

#-------------------------------------------------------------------------------
#  'CheckListEditor' class:
#-------------------------------------------------------------------------------

class CheckListEditor ( EditorWithListFactory ):
    """ GUI toolkit neutral editor factory for checklists.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Number of columns to use when the editor is displayed as a grid:
    cols = Range( 1, 20 )

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
        return TextEditor( factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = name,
                           description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( EditorWithList ):
    """ Simple style of editor for checklists, which displays a combo box.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Checklist item names:
    names = List( Str )

    # Checklist item values:
    values = List

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.create_control( parent )

        super( SimpleEditor, self ).init( parent )

        self.set_tooltip()


    def create_control ( self, parent ):
        """ Creates the initial editor control.
        """
        self.adapter = toolkit().create_combobox( parent )
        self.adapter.set_event_handler( choose = self.update_object )


    def list_updated ( self, values ):
        """ Handles updates to the list of legal checklist values.
        """
        sv = self.string_value
        if (len( values ) > 0) and isinstance( values[0], basestring ):
            values = [ ( x, sv( x, capitalize ) ) for x in values ]

        self.values = valid_values = [ x[0] for x in values ]
        self.names  =                [ x[1] for x in values ]

        # Make sure the current value is still legal:
        modified  = False
        cur_value = parse_value( self.value )
        for i in range( len( cur_value ) - 1, -1, -1 ):
            if cur_value[i] not in valid_values:
                try:
                    del cur_value[i]
                    modified = True
                except TypeError:
                    print ('Unable to remove non-current value [%s] from '
                           'values %s', cur_value[i], values)

        if modified:
            if isinstance( self.value, basestring ):
                cur_value = ','.join( cur_value )
            self.value = cur_value

        self.rebuild_editor()


    def rebuild_editor ( self ):
        """ Rebuilds the editor after its definition is modified.
        """
        control = self.adapter
        control.clear()

        for name in self.names:
            control.add_item( name )

        self.update_editor()


    def update_object ( self, event ):
        """ Handles the user selecting a new value from the combo box.
        """
        value = self.values[ self.names.index( event.value ) ]
        if type( self.value ) is not str:
            value = [ value ]

        self.value = value


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        try:
            self.adapter.selection = self.values.index(
                                                 parse_value( self.value )[0] )
        except:
            pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style of editor for checklists, which displays a set of check
        boxes.
    """

    #-- Public Methods ---------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the initial editor control.
        """
        # Create a panel to hold all of the check boxes:
        self.adapter = toolkit().create_panel( parent )


    def rebuild_editor ( self ):
        """ Rebuilds the editor after its definition is modified.
        """
        panel  = self.adapter
        layout = panel.layout
        if layout is not None:
            layout.clear()

        cur_value = parse_value( self.value )

        # Create a layout manager to manage the radio buttons:
        labels = self.names
        values = self.values
        n      = len( labels )
        cols   = self.factory.cols
        rows   = (n + cols - 1) / cols
        incr   = [ n / cols ] * cols
        rem    = n % cols

        for i in range( cols ):
            incr[i] += (rem > i)

        incr[-1] = -(reduce( lambda x, y: x + y, incr[:-1], 0 ) - 1)

        if cols > 1:
            layout = toolkit().create_grid_layout( 0, cols, 2, 4 )
        else:
            layout = toolkit().create_box_layout()

        # Add the set of all possible choices:
        index = 0
        for i in range( rows ):
            for j in range( cols ):
                if n > 0:
                    label   = labels[ index ]
                    control = toolkit().create_checkbox( panel, label )
                    control._value  = value = values[ index ]
                    control.checked = (value in cur_value)
                    control.set_event_handler( checked = self.update_object )
                    index += incr[j]
                    n     -= 1
                else:
                    control = toolkit().create_checkbox( panel )
                    control.visible = False

                layout.add( control, top = 5, fill = False )

        # Lay out the controls:
        panel.layout = layout
        panel.shrink_wrap()

        # FIXME: There are cases where one of the parent panel's of the check
        # list editor has a fixed 'min size' which prevents the check list
        # editor from expanding correctly, so we currently are making sure
        # that all of the parent panels do not have a fixed min size before
        # doing the layout/refresh:
        ### parent = panel.GetParent()
        ### while isinstance( parent, wx.Panel ):
        ###     parent.SetMinSize( wx.Size( -1, -1 ) )
        ###     panel  = parent
        ###     parent = parent.GetParent()

        panel.update()


    def update_object ( self, event ):
        """ Handles the user clicking one of the custom check boxes.
        """
        if not self._ignore_update:
            control   = event.control
            cur_value = parse_value( self.value )

            if control.checked:
                cur_value.append( control._value )
            else:
                cur_value.remove( control._value )

            if isinstance( self.value, basestring ):
                cur_value = ','.join( cur_value )

            self.value = cur_value


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self._ignore_update = True

        new_values = parse_value( self.value )

        for control in self.adapter.children:
            if control.visible:
                control.checked = (control._value in new_values)

        self._ignore_update = False

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( BaseTextEditor ):
    """ Text style of editor for checklists, which displays a text field.
    """

    #-- Public Methods ---------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            value = self.adapter.value
            value = eval( value )
        except:
            pass

        try:
            self.value = value
        except FacetError:
            pass

#-------------------------------------------------------------------------------
#  Parse a value into a list:
#-------------------------------------------------------------------------------

def parse_value ( value ):
    """ Parses a value into a list.
    """
    if value is None:
        return []

    if type( value ) is not str:
        return value[:]

    return [ x.strip() for x in value.split( ',' ) ]

#-- EOF ------------------------------------------------------------------------