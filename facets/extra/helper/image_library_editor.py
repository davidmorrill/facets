"""
Defines base classes for creating Facets UI Image Library editors.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Instance, Str, List, Property, Constant, \
           on_facet_set

from facets.api \
    import View, VGroup, HSplit, Item, NotebookEditor, InstanceEditor

from facets.ui.image \
    import ImageLibrary, ImageInfo

from facets.extra.helper.library_manager \
    import LibraryManager

#-------------------------------------------------------------------------------
#  'ImageLibraryItem' class:
#-------------------------------------------------------------------------------

class ImageLibraryItem ( HasPrivateFacets ):
    """ Represents an ImageInfo object whose information is being edited by
        some kind of Image Library editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ImageInfo object being edited:
    image = Instance( ImageInfo )

    # The name of the image whose theme is being edited:
    name = Property( depends_on = 'image' )

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        return self.image.image_name

    #-- HasFacets Class Overrides ----------------------------------------------

    def facet_context ( self ):
        """ Returns the default context to use for editing or configuring
            facets.
        """
        return { 'object': self.image }

#-------------------------------------------------------------------------------
#  'ImageLibraryEditor' class:
#-------------------------------------------------------------------------------

class ImageLibraryEditor ( HasPrivateFacets ):
    """ Base class for creating an Image Library Editor.
    """

    #-- Overridable Class Constants --------------------------------------------

    # The persistence id for the image library editor:
    editor_id = ('facets.extra.tools.image_library_editor.'
                 'ImageLibraryEditor')

    # Editor item factory class:
    item_class = ImageLibraryItem

    #-- Facet Definitions ------------------------------------------------------

    # The names of the images currently being edited:
    image_names = List( Str, connect = 'to: list of image names to edit' )

    # The list of ImageLibraryItem objects currently being edited:
    items = List( ImageLibraryItem )

    # The LibraryManager being used to keep track of modified images:
    library = Constant( LibraryManager() )

    # Reference to the image library:
    image_library = Constant( ImageLibrary() )

    # The label/title of the editor for use in the view:
    editor_title = Str( 'Image Library Editor' )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            HSplit(
                VGroup(
                    Item( 'library',
                          show_label = False,
                          style      = 'custom',
                          editor     = InstanceEditor()
                    ),
                    label       = 'Library Manager',
                    group_theme = '@std:GL5TB',
                    dock        = 'horizontal'
                ),
                VGroup(
                    Item( 'items',
                          id         = 'items',
                          show_label = False,
                          style      = 'custom',
                          editor     = NotebookEditor(
                                           deletable  = True,
                                           page_name  = '.name',
                                           export     = 'DockWindowShell',
                                           dock_style = 'tab' )
                    ),
                    label       = self.editor_title,
                    group_theme = '@std:GL5TB',
                    dock        = 'horizontal'
                ),
                group_theme = '@std:XG0',
                id          = 'splitter'
            ),
            id        = self.editor_id,
            width     = 0.7,
            height    = 0.5,
            resizable = True
        )

    #-- Facets Event Handlers --------------------------------------------------

    @on_facet_set( 'image_names[]' )
    def _image_names_modified ( self, removed, added ):
        """ Handles image names being added to or removed from the editor.
        """
        items = self.items

        # fixme: Remove this code if the problem in the TableEditor that allows
        # the same item to be in both the 'removed' and 'added' list is fixed:
        for name in [ name for name in removed if name in added ]:
            removed.remove( name )
            added.remove(   name )

        for image_name in added:
            item = self._find( image_name )
            if item is None:
                image = self.image_library.image_info( image_name )
                if image is not None:
                    items.append( self.item_class( image = image ) )

        for image_name in removed:
            item = self._find( image_name )
            if item is not None:
                items.remove( item )


    @on_facet_set( 'items[]' )
    def _items_modified ( self, removed, added ):
        """ Handles the 'items' list being modified.
        """
        library = self.library

        for item in removed:
            library.remove( item.image )

        for item in added:
            library.add( item.image )

    #-- Private Methods --------------------------------------------------------

    def _find ( self, image_name ):
        """ Tries the find a current ImageLibraryItem matching the specified
            **image_name** and return it. Returns None if not found.
        """
        image = self.image_library.image_info( image_name )
        if image is not None:
            for item in self.items:
                if image is item.image:
                    return item

        return None

#-- EOF ------------------------------------------------------------------------