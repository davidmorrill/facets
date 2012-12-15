"""
Defines a drop target editor and editor factory for the PyQt user interface
    toolkit. A drop target editor handles drag and drop operations as a drop
    target.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtGui \
    import QLineEdit, QPalette

from facets.core_api \
    import Any, Bool

from facets.ui.editors.text_editor \
    import TextEditor, SimpleEditor as SimpleTextEditor

from facets.ui.qt4.constants \
    import DropColor

from facets.ui.qt4.adapters.drag \
    import PyMimeData

#-------------------------------------------------------------------------------
#  'DropEditor' class:
#-------------------------------------------------------------------------------

class DropEditor ( TextEditor ):
    """ PyQt editor factory for drop editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Allowable drop objects must be of this class (optional):
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

class SimpleEditor ( SimpleTextEditor ):
    """ Simple style of drop editor, which displays a read-only text field that
        contains the string representation of the object facet's value.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Background color when it is OK to drop objects:
    ok_color = DropColor

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if self.factory.readonly:
            self.control = QLineEdit( self.str_value, parent() )
            self.control.setReadOnly( True )
            self.set_tooltip()
        else:
            super( SimpleEditor, self ).init( parent )

        control = self.control
        pal     = QPalette( control.palette() )
        pal.setColor( QPalette.Base, self.ok_color )
        control.setPalette( pal )

        # Patch the type of the control to insert the DND event handlers.
        control.__class__ = type( _DropWidget.__name__,
                ( type( control ), ), dict( _DropWidget.__dict__ ) )

        control._qt4_editor = self


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

#-------------------------------------------------------------------------------
#  '_DropWidget' class:
#-------------------------------------------------------------------------------

class _DropWidget ( object ):

    #-- Public Methods ---------------------------------------------------------

    def dropEvent ( self, e ):
        """ Handles a Python object being dropped on the tree.
        """
        editor = self._qt4_editor

        klass = editor.factory.klass

        if editor.factory.binding:
            value = getattr( clipboard, 'node', None )
        else:
            value = e.mimeData().instance()

        if ( klass is None ) or isinstance( data, klass ):
            editor._no_update = True
            try:
                if hasattr( value, 'drop_editor_value' ):
                    editor.value = value.drop_editor_value()
                else:
                    editor.value = value
                if hasattr( value, 'drop_editor_update' ):
                    value.drop_editor_update( self )
                else:
                    self.setText( editor.str_value )
            finally:
                editor._no_update = False

            e.acceptProposedAction()


    def dragEnterEvent ( self, e ):
        """ Handles a Python object being dragged over the tree.
        """
        editor = self._qt4_editor

        if editor.factory.binding:
            data = getattr( clipboard, 'node', None )
        else:
            md = e.mimeData()

            if not isinstance( md, PyMimeData ):
                return

            data = md.instance()

        try:
            editor.object.base_facet( editor.name ).validate( editor.object,
                    editor.name, data )
            e.acceptProposedAction()
        except:
            pass

#-- EOF ------------------------------------------------------------------------