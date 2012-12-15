"""
Defines the popup editor and editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Float, Enum, Any, View, VGroup, Item, EditorFactory, \
           BasicEditorFactory, TextEditor, UIEditor

from facets.ui.ui_facets \
    import EditorStyle

#-------------------------------------------------------------------------------
#  '_PopupEditor' class:
#-------------------------------------------------------------------------------

class _PopupEditor ( UIEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The (optional) label to display instead of the item's value:
    label = Str

    #-- UIEditor Method Overrides ----------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        self.label = self.factory.label

        return self.object.edit_facets(
            view    = self.base_view(),
            parent  = parent,
            kind    = 'editor',
            context = { 'object': self.object, 'editor': self }
        )

    #-- Facet View Definitions -------------------------------------------------

    def base_view ( self ):
        """ Returns the View that allows the popup view to be displayed.
        """
        name = self.name
        if self.label != '':
            name = 'editor.label'

        return View(
            Item( name,
                  show_label = False,
                  style      = 'readonly',
                  editor     = TextEditor( view = self.popup_view() )
            )
        )


    def popup_view ( self ):
        """ Returns the popup View.
        """
        name = self.name
        if self.label != '':
            name = 'object.object.' + name

        factory = self.factory
        item    = Item(
            name,
            show_label = False,
            padding    = -4,
            style      = factory.style,
            height     = factory.height,
            width      = factory.width
        )

        editor = factory.editor
        if editor is not None:
            if not isinstance( editor, EditorFactory ):
                editor = editor()

            item.editor = editor

        return View(
            VGroup(
                item,
                group_theme = '@std:popup'
            ),
            kind = factory.kind
        )

#-------------------------------------------------------------------------------
#  'PopupEditor' class:
#-------------------------------------------------------------------------------

class PopupEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The class used to construct editor objects:
    klass = _PopupEditor

    # An optional label to display instead of the item's value:
    label = Str

    # The kind of popup to use:
    kind = Enum( 'popup', 'popover', 'popout', 'info' )

    # The editor to use for the pop-up view (can be None (use default editor),
    # an EditorFactory instance, or a callable that returns an EditorFactory
    # instance):
    editor = Any

    # The style of editor to use for the popup editor (same as Item.style):
    style = EditorStyle

    # The height of the popup (same as Item.height):
    height = Float( -1.0 )

    # The width of the popup (same as Item.width):
    width = Float( -1.0 )

#-- EOF ------------------------------------------------------------------------