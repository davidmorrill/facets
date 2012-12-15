"""
Demonstrates use of the <b>FileStackEditor</b>, which displays a <i>stacked</i>
view of the file system and is designed to allow you to navigate to and select
existing files (and optionally directories) with a minimal amount of mouse
movement.

The <b>FileStackEditor</b>:
 - Shows you two lists of file-related data.
 - The top list displays path information.
 - The bottom list displays file information.

The top list displays a list of directories, starting from the root of the file
system at the top, to the currently selected directory (highlighted in blue)
somewhere in the middle, down to the list of directories (in darker grey)
contained in the current directory shown at the bottom of the list.

You can select any item in the list to make it the current directory, which
will update both the path and file lists accordingly.

The list at the bottom displays the files (if any) in the currently selected
directory. You can select any file in the list to make it the currently
selected file, which is assigned to the facet being edited by the editor. In the
case of the demo, this sends the selected file to the <b>UniversalInspector</b>
object for display.

The <b><i>File</i></b> tab also allows you to filter the files displayed by
clicking on the <b><i>Filter</i></b> header at the top of the list and entering
(or clearing) the filter text in the pop-up editor that appears. If you do not
need to filter the files displayed, you can set the <b>FileStackEditor</b>'s
<b><i>filter</i></b> facet to False.

You can drag the <b><i>Path</i></b> and <b><i>File</i></b> tabs of the
<b>FileStackEditor</b> to place them side-by-side, or even drag the
<b><i>File</i></b> tab above the <b><i>Path</i></b> tab if you want. You can
also adjust the amount of space each list occupies using the splitter bar
between them. The <b>FileStackEditor</b> also provides an
<b><i>orientation</i></b> facet if you want to change the default vertical
<i>orientation</i> to <i>horizontal</i>.

The <b>FileStackEditor</b> can be further configured using the
<b><i>type</i></b> facet:
 - <b><i>"file"</i></b>: Only allow files to be selected (the default).
 - <b><i>"path"</i></b>: Only allow directories to be selected (the
   <b><i>File</i></b> tab is not displayed).
 - <b><i>"both"</i></b>: Allows either files or directories to be selected.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

import facets.extra.demo.ui.Advanced

from os.path \
    import join, dirname

from facets.api \
    import HasFacets, Str, Instance, View, HSplit, UItem, FileStackEditor

from facets.extra.tools.universal_inspector \
    import UniversalInspector

#-- FileStackEditorDemo class --------------------------------------------------

class FileStackEditorDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The currently selected file:
    file_name = Str

    # The Universal Inspector used to display the currently selected file:
    inspector = Instance( UniversalInspector, { 'max_inspectors': 1 } )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HSplit(
            UItem( 'file_name', width = 0.2, editor = FileStackEditor() ),
            UItem( 'inspector', width = 0.8, style  = 'custom' ),
            id = 'splitter'
        ),
        title     = 'FileStackEditor Demo',
        id        = 'facets.extra.demo.ui.Advanced.FileStackEditor_demo',
        width     = 0.67,
        height    = 0.80,
        resizable = True
    )

    #-- Facet Object Initialization --------------------------------------------

    def facets_init ( self ):
        self.file_name = join(
            dirname( facets.extra.demo.ui.Advanced.__file__ ),
            'FileStackEditor_demo.py'
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        self.inspector.item = file_name

#-- Create the demo ------------------------------------------------------------

demo = FileStackEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
