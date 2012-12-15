"""
Defines the various font editors and the font editor factory, for the Qt user
interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide.QtCore \
    import QObject, SIGNAL

from PySide.QtGui \
    import QFont, QFontDialog, QFontComboBox, QComboBox, QHBoxLayout, \
           QVBoxLayout, QLineEdit

from facets.ui.api \
    import Editor, EditorFactory

from facets.ui.editor_factory \
    import SimpleEditor, TextEditor, ReadonlyEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard font point sizes
PointSizes = [
    '8',  '9', '10', '11', '12', '14', '16', '18', '20', '22', '24', '26', '28',
    '36', '48', '72'
]

#-------------------------------------------------------------------------------
#  'FontEditor' class:
#-------------------------------------------------------------------------------

class FontEditor ( EditorFactory ):
    """ Qt editor factory for font editors.
    """

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleFontEditor( factory     = self,
                                 ui          = ui,
                                 object      = object,
                                 name        = name,
                                 description = description )

    def custom_editor ( self, ui, object, name, description ):
        return CustomFontEditor( factory     = self,
                                 ui          = ui,
                                 object      = object,
                                 name        = name,
                                 description = description )

    def text_editor ( self, ui, object, name, description ):
        return TextFontEditor( factory     = self,
                               ui          = ui,
                               object      = object,
                               name        = name,
                               description = description )

    def readonly_editor ( self, ui, object, name, description ):
        return ReadonlyFontEditor( factory     = self,
                                   ui          = ui,
                                   object      = object,
                                   name        = name,
                                   description = description )

    #-- Public Methods ---------------------------------------------------------

    def to_qt_font ( self, editor ):
        """ Returns a QFont object corresponding to a specified object's font
            facet.
        """
        return QFont( editor.value )


    def from_qt_font ( self, font ):
        """ Gets the application equivalent of a QFont value.
        """
        return font


    def str_font ( self, font ):
        """ Returns the text representation of the specified object facet value.
        """
        weight = { QFont.Light: ' Light',
                   QFont.Bold:  ' Bold'   }.get( font.weight(), '' )
        style  = { QFont.StyleOblique: ' Slant',
                   QFont.StyleItalic:  ' Italic' }.get( font.style(), '' )

        return '%s point %s%s%s' % (
               font.pointSize(), font.family(), style, weight )

#-------------------------------------------------------------------------------
#  'SimpleFontEditor' class:
#-------------------------------------------------------------------------------

class SimpleFontEditor ( SimpleEditor ):
    """ Simple style of font editor, which displays a text field that contains
        a text representation of the font value (using that font if possible).
        Clicking the field displays a font selection dialog box.
    """

    #-- Public Methods ---------------------------------------------------------

    def popup_editor ( self ):
        """ Invokes the pop-up editor for an object facet.
        """
        fnt, ok = QFontDialog.getFont( self.factory.to_qt_font( self ),
                                       self.control )

        if ok:
            self.value = self.factory.from_qt_font( fnt )
            self.update_editor()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        super( SimpleFontEditor, self ).update_editor()
        set_font( self )


    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )

#-------------------------------------------------------------------------------
#  'CustomFontEditor' class:
#-------------------------------------------------------------------------------

class CustomFontEditor ( Editor ):
    """ Custom style of font editor, which displays the following:

        - A text field containing the text representation of the font value
          (using that font if possible).
        - A combo box containing all available type face names.
        - A combo box containing the available type sizes.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # The control is a vertical layout.
        self.control = layout = QVBoxLayout()
        layout.setSpacing( 5 )
        layout.setMargin( 0 )

        # Add the standard font control:
        self._font = font = QLineEdit( self.str_value )
        QObject.connect( font, SIGNAL( 'editingFinished()' ),
                         self.update_object )
        self.control.addWidget( font )

        # Add all of the font choice controls:
        layout2 = QHBoxLayout()

        self._facename = control = QFontComboBox()
        control.setEditable( False )
        QObject.connect( control, SIGNAL( 'currentFontChanged(QFont)' ),
                         self.update_object_parts )
        layout2.addWidget( control )

        self._point_size = control = QComboBox()
        control.addItems( PointSizes )
        QObject.connect( control, SIGNAL( 'currentIndexChanged(int)' ),
                         self.update_object_parts )
        layout2.addWidget( control )

        # These don't have explicit controls.
        self._bold = self._italic = False

        self.control.addLayout( layout2 )


    def update_object ( self ):
        """ Handles the user changing the contents of the font text control.
        """
        self.value = unicode( self._font.text() )
        self._set_font( self.factory.to_qt_font( self ) )
        self.update_editor()


    def update_object_parts ( self ):
        """ Handles the user modifying one of the font components.
        """
        fnt = self._facename.currentFont()

        fnt.setBold( self._bold )
        fnt.setItalic( self._italic )

        psz, _ = self._point_size.currentText().toInt()
        fnt.setPointSize( psz )

        self.value = self.factory.from_qt_font( fnt )

        self._font.setText( self.str_value )
        self._set_font( fnt )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        font = self.factory.to_qt_font( self )

        self._bold = font.bold()
        self._italic = font.italic()

        self._facename.setCurrentFont( font )

        try:
           idx = PointSizes.index( str( font.pointSize() ) )
        except ValueError:
           idx = PointSizes.index( '9' )

        self._point_size.setCurrentIndex( idx )


    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return [ self._font, self._facename, self._point_size ]

    #-- Private Methods --------------------------------------------------------

    def _set_font ( self, font ):
        """ Sets the font used by the text control to the specified font.
        """
        font.setPointSize( min( 10, font.pointSize() ) )
        self._font.setFont( font )

#-------------------------------------------------------------------------------
#  'TextFontEditor' class:
#-------------------------------------------------------------------------------

class TextFontEditor ( TextEditor ):
    """ Text style of font editor, which displays an editable text field
        containing a text representation of the font value (using that font if
        possible).
    """

    #-- Public Methods ---------------------------------------------------------

    def update_object ( self ):
        """ Handles the user changing the contents of the edit control.
        """
        self.value = unicode( self.control.text() )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        super( TextFontEditor, self ).update_editor()
        set_font( self )


    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )

#-------------------------------------------------------------------------------
#  'ReadonlyFontEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyFontEditor ( ReadonlyEditor ):
    """ Read-only style of font editor, which displays a read-only text field
        containing a text representation of the font value (using that font if
        possible).
    """

    #-- Public Methods ---------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        super( ReadonlyFontEditor, self ).update_editor()
        set_font( self )


    def string_value ( self, font ):
        """ Returns the text representation of a specified font value.
        """
        return self.factory.str_font( font )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def set_font ( editor ):
    """ Sets the editor control's font to match a specified font.
    """
    editor.control.setFont( editor.factory.to_qt_font( editor ) )

#-- EOF ------------------------------------------------------------------------