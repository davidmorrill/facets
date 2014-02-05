"""
# CustomFileDialogEditor Demo #

Demonstrates using the **CustomFileDialogEditor** to display a developer
customizable file dialog.

For this demo the view is split into two tabs:

- *Custom File Dialog Editor*: Shows the *file_name* facet of the main demo
  instance being edited using **CustomFileDialogEditor** instance.
- *Universal Inspector*: Shows a **UniversalInspector** tool instance whose
  *item* facet is set to the current file name each time a new file is selected.
  The **UniversalInspector** attempts to display the contents of each selected
  file in a new tab. The demo is configured to allow the contents of up to three
  files to be displayed at once. Change the value of the *max_inspectors* key to
  a different value if you want to see more or less items.

The **CustomFileDialogEditor** has three points of customization:

- **FSitem**: You can create custom subclasses to allow the user to select file
  and folders from a *virtual file system* of your own design.
- **FSExt**: You can create custom subclasses to allow displaying or prompting
  the user for additional information about a selected file. In the demo, we use
  this to display previews of any image or Python source file the user selects.
- **FSFilter**: You can create custom subclasses or instances to allow the user
  to filter the set of files displayed in the currently selected directory. In
  the demo, we use several **FSTypeFilter** instances to allow the user to view:
  all files, Python source files or various image files. Using custom subclasses
  you can also filter on criteria other than file extension.

There is also a **CustomFileDialog** class which uses the
**CustomFileDialogEditor** to display a modal file selection dialog similar to
the file selection dialog supported in most operating systems, but with the
added ability to use any of the customizations supported by the
**CustomFileDialogEditor**. You can see an example of this by clicking on the
*Add file...* button located in the lower right corner of the *Universal
Inspector* tab.

This *Custom File Dialog Editor* tab uses an *inline*
**CustomFileDialogEditor** view rather than a pop-up dialog. The *mode* facet of
the **CustomFileDialogEditor** instance is set to *accept*, which replaces the
normal *Open* or *Save* button with an *Accept* button used to assign the
currently selected file to the underlying editor facet (*file_name* in this
case). To use this in the demo, select a file in the **CustomFileDialogEditor**
view then click the *Accept* button to notify the application. Repeat these
steps to select other files for display in the **UniversalInspector**.

Also note that when Python source files or image files are selected, the
**CustomFileDialogEditor** and **CustomFileDialog** both show a preview of the
selected file in the bottom half of the view, courtesy of the **ImageExt** and
**TextExt** subclasses of **FSExt** defined by the demo and passed to the
**CustomFileDialogEditor** and **CustomFileDialog** instances.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Code, Instance, Image,Button,  View, Tabbed,      \
           VGroup, HGroup, Item, UItem, ImageEditor, CustomFileDialogEditor, \
           spring

from facets.core.facet_base \
    import read_file

from facets.ui.editors.custom_file_dialog_editor \
    import FSExt, FSTypeFilter

from facets.ui.custom_file_dialog \
    import CustomFileDialog

from facets.extra.tools.universal_inspector \
    import UniversalInspector

#-- The ImageExt class (Used to preview selected image files) ------------------

class ImageExt ( FSExt ):

    types = ( 'png', 'jpg', 'jpeg' )
    image = Image

    view = View(
        VGroup(
            '_',
            Item( 'image', height = -200, editor = ImageEditor() ),
            show_labels = False
        )
    )

    def _item_set ( self ):
        self.image = self.item.path

#-- The TextExt class (Used to preview selected Python source files) -----------

class TextExt ( FSExt ):

    types = ( 'py', 'txt' )
    text  = Code

    view = View(
        VGroup(
            '_',
            Item( 'text', height = -200, style  = 'readonly' ),
            show_labels = False
        )
    )

    def _text_default ( self ):
        return read_file( self.item.path )

#-- The CustomFileDialogEditorDemo class (defines the main demo view) ----------

class CustomFileDialogEditorDemo ( HasFacets ):

    file_name  = Str
    inspector  = Instance( UniversalInspector, { 'max_inspectors': 3 } )
    add_file   = Button( 'Add file...' )

    view = View(
        Tabbed(
             UItem( 'file_name',
                    label  = 'Custom File Dialog Editor',
                    id     = 'file_dialog',
                    editor = CustomFileDialogEditor(
                        mode    = 'accept',
                        exts    = [ ImageExt, TextExt ],
                        filters = [
                            FSTypeFilter(),
                            FSTypeFilter( kind  = 'Python',
                                          types = [ 'py' ] ),
                            FSTypeFilter( kind  = 'Image',
                                          types = [ 'png', 'jpg', 'jpeg' ] )
                        ]
                    )
             ),
             VGroup(
                 VGroup(
                     UItem( 'inspector', style = 'custom' )
                 ),
                 HGroup(
                     spring,
                     UItem( 'add_file' ),
                     group_theme = '@xform:b?L15'
                 ),
                 label = 'Universal Inspector'
             ),
             id   = 'tabbed',
             dock = 'tab'
        ),
        title  = 'CustomFileDialogEditor Demo',
        id     = 'facets.extra.demo.ui.Advanced.CustomFileDialogEditor_demo',
        width  = 0.60,
        height = 0.75
    )

    def _file_name_set ( self ):
        self.inspector.item = self.file_name

    def _add_file_set ( self ):
        file_name = CustomFileDialog(
            path    = self.file_name,
            mode    = 'open',
            exts    = [ ImageExt, TextExt ],
            filters = [
                FSTypeFilter(),
                FSTypeFilter( kind  = 'Python',
                              types = [ 'py' ] ),
                FSTypeFilter( kind  = 'Image',
                              types = [ 'png', 'jpg', 'jpeg' ] )
            ]
        ).get_path()
        if file_name is not None:
            self.file_name = file_name

#-- Create the demo ------------------------------------------------------------

demo = CustomFileDialogEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
