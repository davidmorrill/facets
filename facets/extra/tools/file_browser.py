"""
Defines the FileBrowser tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import listdir

from os.path \
    import exists, join, isdir, isfile, dirname

from facets.api \
    import Any, Instance, File, Directory, Str, Property, Callable, View, \
           VGroup, Item, TreeEditor, TreeNodeObject, ObjectTreeNode

from facets.extra.api \
    import FilePosition

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'BaseNode' class:
#-------------------------------------------------------------------------------

class BaseNode ( TreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # Path to this node:
    path = Str

    # Name of this node:
    name = Str

    # Complete file name of this node:
    file_name = Property

    #-- Property Implementations -----------------------------------------------

    def _get_file_name ( self ):
        return join( self.path, self.name )

    #-- Tree Node Method Overrides ---------------------------------------------

    def tno_get_drag_object ( self, node ):
        """ Returns the 'draggable' version of a specified object.
        """
        return self.file_name

#-------------------------------------------------------------------------------
#  'PathNode' class:
#-------------------------------------------------------------------------------

class PathNode ( BaseNode ):

    #-- Facet Definitions ------------------------------------------------------

    # Filter used to determine if a specified path is accepted:
    path_filter = Callable

    # Filter used to determine if a specified file is accepted:
    file_filter = Callable

    # Factory used to create new file nodes:
    file_factory = Callable

    #-- Tree Node Method Overrides ---------------------------------------------

    def tno_allows_children ( self, node ):
        """ Returns whether chidren of this object are allowed or not.
        """
        return True


    def tno_has_children ( self, node = None ):
        """ Returns whether or not the object has children.
        """
        return ( len( self.tno_get_children( node ) ) > 0 )


    def tno_get_children ( self, node ):
        """ Gets the object's children.
        """
        if self._get_children is None:
            paths = []
            files = []
            path  = self.file_name
            path_filter = self.path_filter
            if path_filter is None:
                path_filter = lambda f: 1

            file_filter = self.file_filter
            if file_filter is None:
                file_filter = lambda f: 1

            file_factory = self.file_factory
            if file_factory is None:
                file_factory = lambda p, n: FileNode( path = p, name = n )

            try:
                for name in listdir( path ):
                    new_path = join( path, name )
                    if isdir( new_path ):
                        if path_filter( new_path ):
                            paths.append(
                                PathNode( path        = path,
                                          name        = name,
                                          path_filter = path_filter,
                                          file_filter = file_filter ) )
                    elif isfile( new_path ):
                        if file_filter( new_path ):
                            files.append( file_factory( path, name ) )
            except:
                pass

            paths.sort( lambda l, r: cmp( l.name, r.name ) )
            files.sort( lambda l, r: cmp( l.name, r.name ) )
            self._get_children = paths + files

        return self._get_children

#-------------------------------------------------------------------------------
#  'RootNode' class:
#-------------------------------------------------------------------------------

class RootNode ( PathNode ):

    pass

#-------------------------------------------------------------------------------
#  'FileNode' class:
#-------------------------------------------------------------------------------

class FileNode ( BaseNode ):

    #-- Tree Node Method Overrides ---------------------------------------------

    def tno_allows_children ( self, node ):
        """ Returns whether chidren of this object are allowed or not.
        """
        return False

#-------------------------------------------------------------------------------
#  Tree editor definition:
#-------------------------------------------------------------------------------

tree_editor = TreeEditor(
    editable  = False,
    selected  = 'selected',
    nodes     = [
        ObjectTreeNode( node_for   = [ RootNode ],
                        auto_open  = True,
                        label      = 'path' ),
        ObjectTreeNode( node_for   = [ PathNode ],
                        auto_close = True,
                        label      = 'name' ),
        ObjectTreeNode( node_for   = [ FileNode ],
                        label      = 'name' )
    ]
)

#-------------------------------------------------------------------------------
#  'FileBrowser' class:
#-------------------------------------------------------------------------------

class FileBrowser ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'File Browser'

    # File browser root path:
    root_path = Directory( '/',
                           connect    = 'to: root directory',
                           save_state = True )

    # Root of the class browser tree:
    root = Instance( RootNode, { 'path': 'C:\\' } )

    # The current file position:
    file_position = Instance( FilePosition,
                              connect = 'from: selected file position' )

    # The current file name:
    file_name = File( connect = 'from: selected file' )

    # The current directory:
    directory = Directory( connect = 'from: selected directory' )

    # Current path (file or directory):
    path = File( connect   = 'from: selected path',
                 draggable = 'Drag the selected path.' )

    # The current selected node:
    selected = Any

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( name       = 'root',
              editor     = tree_editor,
              show_label = False
        )
    )

    options = View(
        VGroup(
            Item( 'root_path',
                  label = 'Root path',
                  width = 300
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _root_path_set ( self, path ):
        """ Handles the 'path' facet being changed.
        """
        if exists( path ):
            if not isdir( path ):
                path = dirname( path )

            self.root = RootNode( path = path )


    def _selected_set ( self, selected ):
        """ Handles a path/file being selected.
        """
        if selected is not None:
            if isinstance( selected, PathNode ):
                self.directory = selected.file_name
            else:
                self.file_name     = selected.file_name
                self.file_position = FilePosition(
                                         file_name = selected.file_name )

            self.path = selected.file_name

#-- EOF ------------------------------------------------------------------------