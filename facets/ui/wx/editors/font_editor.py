"""
Defines the various font editors and the font editor factory, for the
    wxPython user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.ui.editor_factory \
    import EditorFactory, SimpleEditor, TextEditor, ReadonlyEditor

from facets.ui.wx.helper \
    import FacetsUIPanel, FontEnumerator, disconnect

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard font point sizes:
PointSizes = [
    '8',  '9', '10', '11', '12', '14', '16', '18', '20', '22', '24', '26', '28',
    '36', '48', '72'
]

# All available font facenames:
facenames = None

#-------------------------------------------------------------------------------
#  'FontEditor' class:
#-------------------------------------------------------------------------------

class FontEditor ( EditorFactory ):
    """ wxPython editor factory for font editors.
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

    def to_wx_font ( self, editor ):
        """ Returns a wx Font object corresponding to a specified object's font
            facet.
        """
        font = editor.value

        return wx.Font( font.GetPointSize(), font.GetFamily(), font.GetStyle(),
                        font.GetWeight(),    font.GetUnderlined(),
                        font.GetFaceName() )


    def from_wx_font ( self, font ):
        """ Gets the application equivalent of a wxPython Font value.
        """
        return font


    def str_font ( self, font ):
        """ Returns the text representation of the specified object facet value.
        """
        weight = { wx.LIGHT: ' Light',
                   wx.BOLD:  ' Bold'   }.get( font.GetWeight(), '' )
        style  = { wx.SLANT: ' Slant',
                   wx.ITALIC: ' Italic' }.get( font.GetStyle(), '' )

        return '%s point %s%s%s' % (
               font.GetPointSize(), font.GetFaceName(), style, weight )


    def all_facenames ( self ):
        """ Returns a list of all available font facenames.
        """
        global facenames

        if facenames is None:
            facenames = FontEnumerator().facenames()
            facenames.sort()

        return facenames

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
        font_data = wx.FontData()
        font_data.SetInitialFont( self.factory.to_wx_font( self ) )
        dialog = wx.FontDialog( self.control, font_data )
        if dialog.ShowModal() == wx.ID_OK:
            self.value = self.factory.from_wx_font(
                              dialog.GetFontData().GetChosenFont() )
            self.update_editor()

        dialog.Destroy()


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

        * A text field containing the text representation of the font value
          (using that font if possible).
        * A combo box containing all available type face names.
        * A combo box containing the available type sizes.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create a panel to hold all of the buttons:
        self.control = panel = FacetsUIPanel( parent, -1 )
        sizer = wx.BoxSizer( wx.VERTICAL )

        # Add the standard font control:
        font = self._font = wx.TextCtrl( panel, -1, self.str_value )
        wx.EVT_KILL_FOCUS( font, self.update_object )
        wx.EVT_TEXT_ENTER( panel, font.GetId(), self.update_object )
        sizer.Add( font, 0, wx.EXPAND | wx.BOTTOM, 3 )

        # Add all of the font choice controls:
        sizer2    = wx.BoxSizer( wx.HORIZONTAL )
        facenames = self.factory.all_facenames()
        control   = self._facename = wx.Choice( panel, -1, wx.Point( 0, 0 ),
                                                wx.Size( -1, -1 ), facenames )

        sizer2.Add( control, 4, wx.EXPAND )
        wx.EVT_CHOICE( panel, control.GetId(), self.update_object_parts )

        control = self._point_size = wx.Choice( panel, -1, wx.Point( 0, 0 ),
                                                wx.Size( -1, -1 ), PointSizes )
        sizer2.Add( control, 1, wx.EXPAND | wx.LEFT, 3 )
        wx.EVT_CHOICE( panel, control.GetId(), self.update_object_parts )

        sizer.Add( sizer2, 0, wx.EXPAND )

        # Set-up the layout:
        panel.SetSizer( sizer )

        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        wx.EVT_KILL_FOCUS( self._font, None )

        disconnect( self._font,       wx.EVT_TEXT_ENTER )
        disconnect( self._facename,   wx.EVT_CHOICE )
        disconnect( self._point_size, wx.EVT_CHOICE )

        super( CustomFontEditor, self ).dispose()


    def update_object ( self, event ):
        """ Handles the user changing the contents of the font text control.
        """
        self.value = self._font.GetValue()
        self._set_font( self.factory.to_wx_font( self ) )
        self.update_editor()


    def update_object_parts ( self, event ):
        """ Handles the user modifying one of the font components.
        """
        point_size = int( self._point_size.GetStringSelection() )
        facename   = self._facename.GetStringSelection()
        font       = wx.Font( point_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                              faceName = facename )
        self.value = self.factory.from_wx_font( font )
        self._font.SetValue( self.str_value )
        self._set_font( font )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        font = self.factory.to_wx_font( self )

        try:
           self._facename.SetStringSelection( font.GetFaceName() )
        except:
           self._facename.SetSelection( 0 )

        try:
           self._point_size.SetStringSelection( str( font.GetPointSize() ) )
        except:
           self._point_size.SetSelection( 0 )

        self._font.SetValue( self.str_value )


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
        font.SetPointSize( min( 10, font.GetPointSize() ) )
        self._font.SetFont( font )

#-------------------------------------------------------------------------------
#  'TextFontEditor' class:
#-------------------------------------------------------------------------------

class TextFontEditor ( TextEditor ):
    """ Text style of font editor, which displays an editable text field
        containing a text representation of the font value (using that font if
        possible).
    """

    #-- Public Methods ---------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        self.value = self.control.GetValue()


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
#  Set the editor control's font to match a specified font:
#-------------------------------------------------------------------------------

def set_font ( editor ):
    """ Sets the editor control's font to match a specified font.
    """
    font = editor.factory.to_wx_font( editor )
    font.SetPointSize( min( 10, font.GetPointSize() ) )
    editor.control.SetFont( font )

#-- EOF ------------------------------------------------------------------------