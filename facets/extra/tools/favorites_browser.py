"""
Defines the FavoritesList tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from os.path \
    import exists, abspath, join, normcase

from facets.api \
    import HasPrivateFacets, Event, List, Range, Instance, Bool, Str, Any, \
           View, VGroup, Item, TreeNode, TreeEditor

from facets.extra.tools.class_browser \
    import CBModuleFile, cb_tree_nodes

from facets.extra.api \
    import FilePosition

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'FavoritesList' class:
#-------------------------------------------------------------------------------

class FavoritesList ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The list of favorite Python source files:
    favorites = List( CBModuleFile )

#-------------------------------------------------------------------------------
#  Favorites tree editor definition:
#-------------------------------------------------------------------------------

favorites_tree_editor = TreeEditor(
    editable = False,
    selected = 'object',
    nodes    = [ TreeNode( node_for  = [ FavoritesList ],
                           auto_open = True,
                           children  = 'favorites',
                           label     = '=Favorites' ) ] + cb_tree_nodes
)

#-------------------------------------------------------------------------------
#  'FavoritesBrowser' class:
#-------------------------------------------------------------------------------

class FavoritesBrowser ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Favorites Browser'

    # Maximum number of favorites to remember:
    max_favorites = Range( 1, 50, 10, save_state = True )

    # Fake option to force a save:
    update = Bool( save_state = True )

    # The list of favorite Python source files:
    root = Instance( FavoritesList, (), save_state = True )

    # The name of a file to add to the favorites list:
    file_name = Event( Str,
                       droppable = 'Drop a favorite Python source file here.' )

    # Currently selected object node:
    object = Any

    # The currently selected file position:
    file_position = Instance( FilePosition,
                        draggable = 'Drag currently selected file position.',
                        connect   = 'from:file position' )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'root',
              editor     = favorites_tree_editor,
              show_label = False
        )
    )

    options = View(
        VGroup(
            Scrubber( 'max_favorites',
                label = 'Maximum number of favorites',
                width = 50
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        """ Handles the 'file_name' facet being changed.
        """
        if exists( file_name ):
            file_name = abspath( str( file_name ) )
            for path in sys.path:
                path = join( abspath( path ), '' )
                if normcase( path ) == normcase( file_name[ : len( path ) ] ):
                    root = self.root
                    for mf in root.favorites:
                        if file_name == mf.path:
                            break
                    else:
                        root.favorites = (
                            [ CBModuleFile( path        = file_name,
                                            python_path = path ) ] +
                            root.favorites )[ : self.max_favorites ]
                        self.update = not self.update

                    return


    def _max_favorites_set ( self, max_favorites ):
        """ Handles the 'max_favorites' facet being changed.
        """
        self.root.favorites = self.root.favorites[ : max_favorites ]
        self.update = not self.update


    def _object_set ( self, value ):
        """ Handles a tree node being selected.
        """
        # If the selected object has a starting line number, then set up
        # the file position for the text fragment the object corresponds to:
        if hasattr( value, 'line_number' ):

            # Read the object's text to force it to calculate the starting
            # line number of number of lines in the text fragment:
            ignore = value.text

            # Set the file position for the object:
            self.file_position = FilePosition(
                name      = value.name,
                file_name = value.path,
                line      = value.line_number + 1,
                lines     = value.lines
            )

#-- EOF ------------------------------------------------------------------------