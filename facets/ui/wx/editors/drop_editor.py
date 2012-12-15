"""
Defines a drop target editor and editor factory for the wxPython user
    interface toolkit. A drop target editor handles drag and drop operations as
    a drop target.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.core_api \
    import Any, Bool

from facets.ui.editors.text_editor \
    import TextEditor, SimpleEditor as Editor

from facets.ui.wx.util.drag_and_drop \
    import PythonDropTarget, clipboard

from facets.ui.wx.constants \
    import DropColor

#-------------------------------------------------------------------------------
#  'DropEditor' class:
#-------------------------------------------------------------------------------

class DropEditor ( TextEditor ):
    """ wxPython editor factory for drop editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Allowable drop objects must be of this class (optional)
    klass = Any

    # Must allowable drop objects be bindings?
    binding = Bool( False )

    # Can the user type into the editor, or is it read only?
    readonly = Bool( True )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

    def custom_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
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
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style of drop editor, which displays a read-only text field that
        contains the string representation of the object facet's value.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Background color when it is OK to drop objects.
    ok_color = DropColor

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if self.factory.readonly:
            self.control = wx.TextCtrl( parent(), -1, self.str_value,
                                        style = wx.TE_READONLY )
            self.set_tooltip()
        else:
            super( SimpleEditor, self ).init( parent )

        self.control.SetBackgroundColour( self.ok_color )
        self.control.SetDropTarget( PythonDropTarget( self ) )


    def string_value ( self, value ):
        """ Returns the text representation of a specified object facet value.
        """
        if value is None:
            return ''
        return str( value )


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        pass

    #-- Drag and drop event handlers -------------------------------------------


    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles a Python object being dropped on the tree.
        """
        klass = self.factory.klass
        value = data
        if self.factory.binding:
            value = getattr( clipboard, 'node', None )
        if ( klass is None ) or isinstance( data, klass ):
            self._no_update = True
            try:
                if hasattr( value, 'drop_editor_value' ):
                    self.value = value.drop_editor_value()
                else:
                    self.value = value
                if hasattr( value, 'drop_editor_update' ):
                    value.drop_editor_update( self.control )
                else:
                    self.control.SetValue( self.str_value )
            finally:
                self._no_update = False
            return drag_result

        return wx.DragNone


    def wx_drag_over ( self, x, y, data, drag_result ):
        """ Handles a Python object being dragged over the tree.
        """
        if self.factory.binding:
            data = getattr( clipboard, 'node', None )
        try:
            self.object.base_facet( self.name ).validate( self.object,
                                                          self.name, data )
            return drag_result
        except:
            return wx.DragNone

#-- EOF ------------------------------------------------------------------------