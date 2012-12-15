"""
Defines the tree-based Python value editor and the value editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, Int, Bool, Str, Any, View, Item, TreeEditor, \
           BasicEditorFactory

from facets.ui.value_tree \
    import RootNode, value_tree_nodes

from facets.ui.ui_editor \
    import UIEditor

#-------------------------------------------------------------------------------
#  '_ValueEditor' class:
#-------------------------------------------------------------------------------

class _ValueEditor ( UIEditor ):
    """ Simple style of editor for values, which displays a tree.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the editor read only?
    readonly = Bool( False )

    # The root node of the value tree
    root = Instance( RootNode )

    # Is the value editor scrollable? This values overrides the default.
    scrollable = True

    # The currently selected value tree node:
    selected_node = Any

    # The currently selected value tree item:
    selected = Any

    #-- Public Methods ---------------------------------------------------------

    def init_ui ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.update_editor()
        editor = TreeEditor(
            auto_open = self.factory.auto_open,
            hide_root = True,
            editable  = False,
            selected  = 'selected_node',
            nodes     = value_tree_nodes
        )

        # Set up selection synchronization:
        self.sync_value( self.factory.selected, 'selected' )

        return self.edit_facets( parent = parent, view = View(
            Item( 'root', show_label = False, editor = editor ),
            kind = 'editor'
        ) )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        self.root = RootNode( name     = '',
                              value    = self.value,
                              readonly = self.readonly )

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_node_set ( self, node ):
        """ Handles the user selecting a value tree node.
        """
        self.selected = node.value

#-------------------------------------------------------------------------------
#  'ValueEditor' class:
#-------------------------------------------------------------------------------

class ValueEditor ( BasicEditorFactory ):
    """ Editor factory for tree-based value editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to create:
    klass = _ValueEditor

    # Number of tree levels to automatically open
    auto_open = Int( 2 )

    # Name of the [object.]facet[.facet...] to synchronize value tree item
    # selection with:
    selected = Str

#-- EOF ------------------------------------------------------------------------