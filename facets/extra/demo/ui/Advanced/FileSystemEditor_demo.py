"""
Demonstrates use of the FileSystemEditor, which displays a hierarchical grid
view of a specified portion of the file system.

The FileSystemEditor allows you to specify or determine:
 - The root of the file system to display.
 - One or more 'glob' patterns to use when matching files. More than one glob
   pattern can be specified by separating the individual patterns with commas
   (e.g. '*.png,*.jpg,*.gif').
 - The file system path the user most recently double-clicked.
 - The interval (in milliseconds) the editor's contents are refreshed at.
 - Whether files and directories, or only directories, are displayed.
 - Whether files and directories, or only files, can be selected.
 - Which columns of file system information to display. The default is to show
   all columns:
   - 'size': File size
   - 'type': File type
   - 'modified': File last modified time
   - 'created': File creation time

The demo allows you to modify the root of the file system to display and the
list of glob patterns used to determine which files to display. If you want
to use more than one glob pattern, separate each pattern with a comma. Also,
make sure to press the Enter key after entering the final glob pattern to update
the file system display.

Clicking a file in the file system view displays the contents of the selected
file in the UniversalInspector view located below the file system view.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

import facets.extra.demo.ui

from os.path \
    import dirname

from facets.api \
    import HasFacets, Str, Directory, Instance, SyncValue, View, VGroup, \
           VSplit, Item, FileSystemEditor, TextEditor

from facets.extra.tools.universal_inspector \
    import UniversalInspector

#-- FileSystemEditorDemo Class Definition --------------------------------------

class FileSystemEditorDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The currently selected file:
    file_name = Str

    # The root of the section of the file system to display:
    root = Directory

    # The glob pattern to use to filter which files should be included in the
    # file system view:
    glob = Str( '*' )

    # The Universal Inspector used to display the contents of the currently
    # selected file:
    inspector = Instance( UniversalInspector, { 'max_inspectors': 1 } )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                Item( 'file_name', style = 'readonly' ),
                Item( 'root' ),
                Item( 'glob',
                      editor = TextEditor( auto_set = False, enter_set = True )
                ),
                group_theme = '@xform:b?L35'
            ),
            VSplit(
                Item( 'file_name',
                      id     = 'file_system_editor',
                      editor = FileSystemEditor(
                          root = SyncValue( self, 'root' ),
                          glob = SyncValue( self, 'glob' )
                      )
                ),
                Item( 'inspector', style = 'custom' ),
                id          = 'splitter',
                show_labels = False
            ),
            title     = 'FileSystemEditor Demo',
            id        = 'facets.extra.demo.ui.Advanced.FileSystemEditor_demo',
            width     = 0.67,
            height    = 0.90,
            resizable = True
        )

    #-- Facet View Definitions -------------------------------------------------

    def _root_default ( self ):
        return dirname( facets.extra.demo.ui.__file__ )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        self.inspector.item = file_name

#-- Create the demo ------------------------------------------------------------

demo = FileSystemEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
