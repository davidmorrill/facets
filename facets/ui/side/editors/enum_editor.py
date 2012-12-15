"""
Defines the various editors and the editor factory for single-selection
enumerations for the Qt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from string \
    import capitalize

from PySide.QtCore \
    import QObject, QSignalMapper, SIGNAL, SLOT

from PySide.QtGui \
    import QComboBox, QPalette, QGridLayout, QRadioButton, QListWidget

from facets.api \
    import Any, Range, Enum, Property, Bool, EditorWithListFactory

from facets.ui.side.constants \
    import OKColor, ErrorColor

from facets.ui.side.helper \
    import enum_values_changed

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Supported display modes for a custom style editor
Mode = Enum( 'radio', 'list' )

#-------------------------------------------------------------------------------
#  'EnumEditor' class:
#-------------------------------------------------------------------------------

class EnumEditor ( EditorWithListFactory ):
    """ Qt editor factory for enumeration editors.
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
            self._object.on_facet_set( self._values_updated, ' ' + self._name,
                                       dispatch = 'ui' )
        else:
            factory.on_facet_set( self.rebuild_editor, 'values_modified',
                                  dispatch = 'ui' )


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self._object is not None:
            self._object.on_facet_set(
                self._values_updated, ' ' + self._name, remove = True
            )
        else:
            self.factory.on_facet_set( self.rebuild_editor, 'values_modified',
                                       remove = True )

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

    #-- Property Implementations -----------------------------------------------

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

    def _values_updated ( self ):
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

        self.control = control = QComboBox( parent )
        control.addItems( self.names )
        QObject.connect( control, SIGNAL( 'currentIndexChanged(QString)' ),
                         self.update_object )

        if self.factory.evaluate is not None:
            control.setEditable( True )
            QObject.connect( control, SIGNAL( 'editTextChanged(QString)' ),
                             self.update_text_object )

        self._no_enum_update = 0
        self.set_tooltip()

        control.setVisible( True )


    def update_object ( self, text ):
        """ Handles the user selecting a new value from the combo box.
        """
        self._no_enum_update += 1
        try:
            self.value = self.mapping[ unicode( text ) ]
        except:
            pass
        self._no_enum_update -= 1


    def update_text_object ( self, text ):
        """ Handles the user typing text into the combo box text entry field.
        """
        if self._no_enum_update == 0:
            value = unicode( text )
            try:
                value = self.mapping[ value ]
            except:
                try:
                    value = self.factory.evaluate( value )
                except Exception, excp:
                    self.error( excp )
                    return

            self._no_enum_update += 1
            self.value = value
            self._set_background( OKColor )
            self._no_enum_update -= 1


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self._no_enum_update == 0:
            if self.factory.evaluate is None:
                try:
                    idx = self.control.findText(
                              self.inverse_mapping[ self.value ] )
                    self.control.setCurrentIndex( idx )
                except:
                    pass
            else:
                try:
                    self.control.setEditText( self.str_value )
                except:
                    pass


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        self._set_background( ErrorColor )


    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** facet changes.
        """
        # Restore the old selection after rebuilding the editor(if it is still
        # valid):
        old_mapping = self.inverse_mapping.get( self.value, None )
        self.control.clear()
        self.control.addItems( self.names )
        if old_mapping in self.names:
            try:
                self.value = self.mapping[ old_mapping ]
            except:
                pass

        self.update_editor()

    #-- Private Methods --------------------------------------------------------

    def _set_background ( self, col ):
        le  = self.control.lineEdit()
        pal = QPalette( le.palette() )
        pal.setColor( QPalette.Base, col )
        le.setPalette( pal )

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

        # The control is a grid layout:
        self.control = layout = QGridLayout()
        layout.setSpacing( 0 )
        layout.setMargin( 0 )

        self._mapper = QSignalMapper()
        QObject.connect( self._mapper, SIGNAL( 'mapped(QWidget *)' ),
                         self.update_object )

        self.rebuild_editor()


    def update_object ( self, rb ):
        """ Handles the user clicking one of the custom radio buttons.
        """
        try:
            self.value = rb.value
        except:
            pass


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        value = self.value
        for i in range( self.control.count() ):
            rb = self.control.itemAt( i ).widget()
            rb.setChecked( rb.value == value )


    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** facet changes.
        """
        # Clear any existing content:
        ### self.clear_layout()

        # Get the current facet value:
        cur_name = self.str_value

        # Create a sizer to manage the radio buttons:
        names   = self.names
        mapping = self.mapping
        n       = len( names )
        cols    = self.factory.cols
        rows    = (n + cols - 1) / cols
        incr    = [ n / cols ] * cols
        rem     = n % cols
        for i in range( cols ):
            incr[i] += (rem > i)

        incr[-1] = -( reduce( lambda x, y: x + y, incr[:-1], 0 ) - 1 )

        # Add the set of all possible choices:
        index = 0

        for i in range( rows ):
            for j in range( cols ):
                if n > 0:
                    name = label = names[ index ]
                    label = self.string_value( label, capitalize )
                    rb = QRadioButton( label )
                    rb.value = mapping[ name ]

                    rb.setChecked( name == cur_name )

                    QObject.connect( rb, SIGNAL( 'clicked()' ), self._mapper,
                                     SLOT( 'map()' ) )
                    self._mapper.setMapping( rb, rb )

                    self.set_tooltip( rb )
                    self.control.addWidget( rb, i, j )

                    index += incr[j]
                    n     -= 1

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

        self.control = QListWidget( parent )
        QObject.connect( self.control, SIGNAL( 'currentTextChanged(QString)' ),
                         self.update_object )

        self.rebuild_editor()
        self.set_tooltip()


    def update_object ( self, text ):
        """ Handles the user selecting a list box item.
        """
        value = unicode( text )
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
        control = self.control
        try:
            value = self.inverse_mapping[ self.value ]

            for row in range( control.count() ):
                itm = control.item( row )

                if itm.text() == value:
                    control.setCurrentItem( itm )
                    control.scrollToItem( itm )
                    break
        except:
            pass


    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** facet changes.
        """
        self.control.clear()

        for name in self.names:
            self.control.addItem( name )

#-- EOF ------------------------------------------------------------------------