"""
Defines the standard Facets ImageTool class for performing simple image
manipulations.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import join, exists, dirname

from facets.api \
    import SingletonHasPrivateFacets, List, Int, Bool, Any, Instance, Image, \
           File, Button, Theme, View, HGroup, VGroup, Item, UItem,           \
           NotebookEditor, UIInfo, implements, on_facet_set, spring, toolkit

from facets.ui.i_ui_info \
    import IUIInfo

from facets.ui.custom_file_dialog \
    import CustomFileDialog

from facets.ui.editors.custom_file_dialog_editor \
    import ImageExt, ImageFilter

from facets.extra.tools.image_knife \
    import ImageKnife

from facets.extra.features.save_state_feature \
    import SaveStateFeature

#-------------------------------------------------------------------------------
#  'ImageTool' class:
#-------------------------------------------------------------------------------

class ImageTool ( SingletonHasPrivateFacets ):
    """ Defines the standard Facets ImageTool class used to perform simple
        image manipulations.
    """

    implements( IUIInfo )

    #-- Facet Definitions ------------------------------------------------------

    # The image knives used to edit input images:
    knives = List # ( Instance( ImageKnife ) )

    # The currently selected knife:
    knife = Any # Instance( ImageKnife )

    # Next 'index' to assign to an image:
    index = Int

    # The file path of the last image loaded:
    load_path = File

    # The file path of the last image saved:
    save_path = File

    # An externally supplied image (used by DockWindow):
    image = Image

    # The most recent image copied to the system clipboard:
    clipboard_image = Image

    # The system clipboard object:
    clipboard = Any( toolkit().clipboard() )

    # Event fired when the user wants to load an external image file:
    load_image = Button( '@icons2:Folder' )

    # Event fired when the user wants to use the current output image as a new
    # input image:
    copy_image = Button( '@icons2:ClipboardCopy' )

    # Event fired when the clipboard contents should be used to create a new
    # input image:
    from_clipboard = Button( '@icons2:ClipboardPaste' )

    # Event fired when the currently selected image should be copied to the
    # clipboard:
    to_clipboard = Button( '@icons2:Clipboard' )

    # Should updating the clipboard contents automatically create a new input
    # image?
    auto_clipboard = Bool( False )

    #-- IUIInfo Interface Facet Definitions ------------------------------------

    # The UIInfo object for an open View of the object:
    ui_info = Instance( UIInfo )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            UItem( 'knives',
                   id     = 'knives',
                   editor = NotebookEditor(
                       selected   = 'knife',
                       features   = [ SaveStateFeature ],
                       deletable  = True,
                       dock_style = 'tab',
                       page_name  = '.name'
                  )
            ),
            HGroup(
                UItem( 'load_image', tooltip = 'Load an image file' ),
                UItem( 'copy_image',
                       tooltip = 'Create a new image from the current image',
                       enabled_when = 'knife is not None'
                ),
                UItem( 'to_clipboard',
                       tooltip      = 'Copy the current image to the clipboard',
                       enabled_when = 'knife is not None'
                ),
                UItem( 'from_clipboard',
                       tooltip      = 'Paste the clipboard as a new image',
                       enabled_when = 'clipboard_image is not None'
                ),
                '_',
                Item( 'auto_clipboard',
                      label   = 'Auto paste?',
                      tooltip = 'Automatically paste the clipboard as a new '
                                'image'
                ),
                spring,
                id          = 'tb',
                group_theme = Theme( '@xform:b', content = ( 6, 2 ) )
            )
        ),
        title     = 'Image Tool',
        id        = 'facets.tools.image_tool.ImageTool',
        width     = 0.9,
        height    = 0.9,
        resizable = True
    )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        # fixme: Why doesn't the @on_facet_set decorator below work?...
        self.clipboard.on_facet_set( self._clipboard_modified, 'image' )

    #-- Facet Default Values ---------------------------------------------------

    def _save_path_default ( self ):
        return self.facet_db_get( 'save_path', '' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _save_path_set ( self, path ):
        """ Handles the 'save_path' facet being changed.
        """
        path = path.strip()
        if path != '':
            self.facet_db_set( 'save_path', path )


    @on_facet_set( 'knife:output_file_name' )
    def _save_file_name_modified ( self, file_name ):
        """ Handles the currently selected knife's 'output_file_name' facet
            being changed.
        """
        path = dirname( file_name )
        print "path:", path
        if path != '':
            self.save_path = path


    def _image_set ( self, image ):
        """ Handles the 'image' facet being changed.
        """
        if image is not None:
            self.index += 1
            knife = ImageKnife(
                input_image = image,
                name        = 'Image %d' % self.index
            )
            if (image.name == '') and (self.save_path != ''):
                knife.output_file_name = self._next_file_name()

            self.knives.append( knife )
            self.knife = knife

            if self.ui_info is None:
                self.edit_facets()
            else:
                self.ui_info.ui.control.activate()


    @on_facet_set( 'knives[]' )
    def _knives_modified ( self ):
        """ Handles the 'knives' facet being changed.
        """
        if len( self.knives ) == 1:
            self.knife = self.knives[0]


    def _load_image_set ( self ):
        path = CustomFileDialog(
            path    = self.load_path,
            mode    = 'open',
            filters = [ ImageFilter ],
            exts    = [ ImageExt ]
        ).get_path()

        if path is not None:
            self.image = self.load_path = path


    def _copy_image_set ( self ):
        """ Handles the 'copy_image' event being fired.
        """
        self.image = self.knife.output_image


    def _from_clipboard_set ( self, image ):
        """ Handles the 'from_clipboard' event being fired.
        """
        self.image           = self.clipboard_image
        self.clipboard_image = None


    def _to_clipboard_set ( self, image ):
        """ Handles the 'to_clipboard' event being fired.
        """
        self._ignore_event   = True
        self.clipboard.image = self.knife.output_image
        self._ignore_event   = False


    #@on_facet_set( 'clipboard:image' )
    def _clipboard_modified ( self ):
        """ Handles an image being copied to the system clipboard.
        """
        image = self.clipboard.image
        if ((not self._ignore_event) and
            (image is not None)      and
            self.auto_clipboard):
            self.image = image
        else:
            self.clipboard_image = image

    #-- Private Methods --------------------------------------------------------

    def _next_file_name ( self ):
        """ Returns the next available output file name, based on the current
            save path.
        """
        path = self.save_path
        for i in xrange( 1, 1000 ):
            file_name = join( path, 'ss_%d.png' % i )
            if not exists( file_name ):
                break

        return file_name

#-- Run the tool (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    ImageTool().edit_facets()

#-- EOF ------------------------------------------------------------------------