"""
Defines a custom file dialog editor that allows the user to customize the
presentation of the underlying file system (e.g. to represent a file system
running on a remote system). It also allows incuding additional information
about the selected file that can be passed back to the requesting application.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import listdir, getcwd, mkdir, access, R_OK, W_OK

from os.path \
    import abspath, exists, isdir, join, dirname, basename, splitext, getsize, \
           getmtime

from time \
    import strftime, localtime

from facets.api \
    import HasPrivateFacets, Any, Bool, Event, Str, Enum, List, Dict, Int, \
           Long, Float, Instance, Image, Callable, Property, Button, View, \
           VGroup, HGroup, HSplit, Handler, Item, UItem, ButtonEditor,     \
           EnumEditor, GridEditor, UIEditor, UIInfo, BasicEditorFactory,   \
           on_facet_set, property_depends_on, spring

from facets.core.constants \
    import is_windows

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.menu \
    import Action

from facets.ui.pyface.timer.api \
    import do_later

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Sort column specification:
SortColumn = Enum( 'Name', 'Size', 'Type', 'Date Modified' )

# The access mode the selected file must support (note: 'default': access is
# determined by the 'mode' value, 'any': do not check file access):
Access = Enum( 'default', 'read', 'write', 'any' )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Values for common file size units:
Kilobyte = 1024
Megabyte = 1024 * Kilobyte
Gigabyte = 1024 * Megabyte
Terabyte = 1024 * Gigabyte

# Mapping from dialog mode to access mode:
AccessMap = {
    'open':   'read',
    'create': 'write',
    'save':   'write',
    'accept': 'any',
    'select': 'any'
}

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def name_sorter ( l, r ):
    """ Returns the sort comparison of two FSItem objects based on their name.
    """
    if l.is_folder ^ r.is_folder:
        return (1 - (2 * l.is_folder))

    return cmp( l.ui_name, r.ui_name )

#-------------------------------------------------------------------------------
#  'FSItem' class:
#-------------------------------------------------------------------------------

class FSItem ( HasPrivateFacets ):
    """ A partially abstract base class for a file system item that can be used
        with the CustomFileDialogEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The full path for the item:
    path = Str

    # The FSExt (if any) associated with this item:
    ext = Instance( 'facets.ui.editors.custom_file_dialog_editor.FSExt',
                    transient = True )

    # The access mode a file must support:
    access = Access

    # The FSFilter (if any) associated with this item:
    filter = Instance( 'facets.ui.editors.custom_file_dialog_editor.FSFilter',
                       transient = True )

    # The parent FSItem (if any) for this item:
    parent = Instance( 'facets.ui.editors.custom_file_dialog_editor.FSItem',
                       transient = True )

    # Does this item exist?
    exists = Bool( False, transient = True )

    # Does this item represent some type of container/folder?
    is_folder = Bool( False, transient = True  )

    # Can a folder be created here?
    can_create_folder = Bool( False, transient = True )

    # The contents of this item (if it is a container/folder):
    children = List( transient = True ) # ( FSItem )

    # The short name for this item:
    name = Str( transient = True )

    # The size for this item:
    size = Long( transient = True )

    # The file type for this item:
    type = Str( transient = True )

    # The last date modified for this item:
    modified = Float( transient = True )

    # The name of the user interface icon to display for this item:
    ui_icon = Str( transient = True )

    # The user interface complete path name for this item:
    ui_path = Str( transient = True )

    # The user interface name for this item:
    ui_name = Str( transient = True )

    # The user interface name for this item as it should appear in the favorites
    # list:
    ui_favorite = Str( transient = True )

    # The user interface file size for this item:
    ui_size = Str( transient = True )

    # The user interface file type for this item:
    ui_type = Str( transient = True )

    # The user interface last date modified for this item:
    ui_modified = Str( transient = True )

    # Is this item enabled for selection in the user interface?
    ui_enabled = Bool( True, transient = True )

    #-- Helper Facet Definitions -----------------------------------------------

    # Default icon names:
    root_icon = Str( '@icons2:Earth',  transient = True )
    dir_icon  = Str( '@icons2:Folder', transient = True )
    file_icon = Str( '@icons2:Document_3?H91l16S26~l39|l85', transient = True )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, path = '', **facets ):
        """ Initializes the object.
        """
        self.path = path

        super( FSItem, self ).__init__( **facets )


    def create_folder ( self, name ):
        """ Creates a folder (i.e. directory) with the specified name in the
            item's path. This method is only ever called if 'can_create_folder'
            is **True**.

            Returns **None** if the folder was created successfully and a string
            describing the reason for failure if not.
        """
        return 'Method not implemented'


    def item_for ( self, name ):
        """ Returns a new FSItem which describes the file system item obtained
            by logically joining the item's 'path' with the file name specified
            by *name*. Note that the resulting FSItem may not represent an
            existing file.
        """
        raise NotImplementedError


    def refresh ( self ):
        """ Refreshes the data for the item.
        """

    #-- object Method Overrides ------------------------------------------------

    def __eq__ ( self, other ):
        """ Returns **True** if this object and *other* are equal, and **False**
            otherwise.
        """
        return (isinstance( other, FSItem) and (self.path == other.path))


    def __ne__ ( self, other ):
        """ Returns **True** if this object and *other* are not equal, and
            **False** otherwise.
        """
        return (not isinstance( other, FSItem) or (self.path != other.path))

#-------------------------------------------------------------------------------
#  'BaseFSItem' class:
#-------------------------------------------------------------------------------

class BaseFSItem ( FSItem ):
    """ A slightly more concrete implementation of the FSItem class which uses a
        default value framework to provide the values for the various FSItem
        attributes.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The category for this item:
    category = Enum( 'file', 'dir', 'root', transient = True )

    #-- Public Methods ---------------------------------------------------------

    def refresh ( self ):
        """ Refreshes the data for the item.
        """
        del self.children

    #-- Facet Default Values ---------------------------------------------------

    def _can_create_folder_default ( self ):
        return self._resolve( 'can_create_folder' )

    def _parent_default      ( self ): return self._resolve( 'parent' )
    def _exists_default      ( self ): return self._resolve( 'exists' )
    def _is_folder_default   ( self ): return self._resolve( 'is_folder' )
    def _children_default    ( self ): return self._resolve( 'children' )
    def _name_default        ( self ): return self._resolve( 'name' )
    def _size_default        ( self ): return self._resolve( 'size' )
    def _type_default        ( self ): return self._resolve( 'type' )
    def _modified_default    ( self ): return self._resolve( 'modified' )
    def _ui_icon_default     ( self ): return self._resolve( 'ui_icon' )
    def _ui_path_default     ( self ): return self._resolve( 'ui_path' )
    def _ui_name_default     ( self ): return self._resolve( 'ui_name' )
    def _ui_favorite_default ( self ): return self._resolve( 'ui_favorite' )
    def _ui_size_default     ( self ): return self._resolve( 'ui_size' )
    def _ui_type_default     ( self ): return self._resolve( 'ui_type' )
    def _ui_modified_default ( self ): return self._resolve( 'ui_modified' )
    def _ui_enabled_default  ( self ): return self._resolve( 'ui_enabled' )

    #-- Private Methods --------------------------------------------------------

    def _resolve ( self, name ):
        """ Returns the result of resolving the specified facet value specified
            by *name* using the item's category.
        """
        handler = getattr( self, '_%s_%s' % ( name, self.category ), None )
        if handler is None:
            handler = getattr( self, '_' + name )

        return handler()

#-------------------------------------------------------------------------------
#  'LocalFSItem' class:
#-------------------------------------------------------------------------------

class LocalFSItem ( BaseFSItem ):
    """ A concrete implementation of the FSItem interface used for
        representing files on the local file system.
    """

    #-- Public Methods ---------------------------------------------------------

    def create_folder ( self, name ):
        """ Creates a folder (i.e. directory) with the specified name in the
            item's path. This method is only ever called if 'can_create_folder'
            is **True**.

            Returns **None** if the folder was created successfully and a string
            describing the reason for failure if not.
        """
        path = join( self.path, name )
        if exists( path ):
            return ("'%s' already exists" % name)

        try:
            mkdir( path )
        except:
            return ("Error creating '%s'" % name)


    def item_for ( self, name ):
        """ Returns a new FSItem which describes the file system item obtained
            by logically joining the item's 'path' with the file name specified
            by *name*. Note that the resulting FSItem may not represent an
            existing file.
        """
        return self.__class__( abspath( join( self.path, name ) ) )

    #-- Facet Default Values ---------------------------------------------------

    def _category_default ( self ):
        if self.path == '':
            return 'root'  # Windows only!

        if isdir( self.path ):
            return 'dir'

        return 'file'

    #-- Private Methods --------------------------------------------------------

    def _parent_root ( self ):
        return None

    def _parent_dir ( self ):
        parent = dirname( self.path )
        if parent == self.path:
            if not is_windows:
                return None

            parent = ''

        return self.__class__( parent, access = self.access )

    def _parent_file ( self ):
        return self.__class__( dirname( self.path ), access = self.access )


    def _exists ( self ):
        return exists( self.path )


    def _is_folder_root ( self ):
        return True

    def _is_folder_dir ( self ):
         return True

    def _is_folder_file ( self ):
        return False


    def _can_create_folder_dir ( self ):
        return access( self.path, W_OK )

    def _can_create_folder ( self ):
        return False


    def _children_root ( self ):
        # Note: This method should only be called on Windows systems...
        from facets.core.facet_base import system_drives

        return [ self.__class__( drive, access = self.access )
                 for drive in system_drives() ]

    def _children_dir ( self ):
        dirs  = []
        files = []
        path  = self.path
        for name in listdir( path ):
            item = self.__class__( join( path, name ), access = self.access )
            if isdir( item.path ):
                dirs.append( item )
            else:
                files.append( item )

        return (dirs + files)

    def _children_file ( self ):
        # Note: This method should never be called...
        return []


    def _name ( self ):
        name = basename( self.path )
        if name == '':
            name = self.path

        return name


    def _size_dir ( self ):
        return 0

    def _size ( self ):
        return getsize( self.path )


    def _type_dir ( self ):
        return ''

    def _type ( self ):
        return splitext( self.path )[1][1:]


    def _modified ( self ):
        return getmtime( self.path )


    def _ui_icon_root ( self ):
        return self.root_icon

    def _ui_icon_dir ( self ):
        return self.dir_icon

    def _ui_icon_file ( self ):
        return self.file_icon


    def _ui_path_root ( self ):
        return 'My Computer'

    def _ui_path ( self ):
        return self.path


    def _ui_name ( self ):
        return self.name


    def _ui_favorite ( self ):
        return self.name


    def _ui_size_dir ( self ):
        return ''

    def _ui_size ( self ):
        size = self.size
        if size < Kilobyte:
            return ('%d bytes' % size)

        if size < Megabyte:
            return ('%.1f KB' % (float( size ) / Kilobyte))

        if size < Gigabyte:
            return ('%.1f MB' % (float( size ) / Megabyte ))

        if size < Terabyte:
            return ('%.1f GB' % (float( size ) / Gigabyte ))

        return ('%.1f TB' % (float( size ) / Terabyte ))


    def _ui_type_dir ( self ):
        return 'File Folder'

    def _ui_type ( self ):
        return (self.type + ' File')


    def _ui_modified ( self ):
        return strftime( '%m/%d/%Y %I:%M:%S %p', localtime( self.modified ) )


    def _ui_enabled_file ( self ):
        if self.access == 'read':
            return access( self.path, R_OK )

        if self.access == 'write':
            return access( self.path, W_OK )

        return True

    def _ui_enabled ( self ):
        return True

#-------------------------------------------------------------------------------
#  'FSExt' class:
#-------------------------------------------------------------------------------

class FSExt ( HasPrivateFacets ):
    """ A partially abstract base class for a set of additional values that the
        user can edit or specify when files having one of the file extensions
        specified by the class are selected.

        Subclasses should add whatever additional facets they need and provide
        a default view that will be displayed as part of the
        CustomFileDialogEditor view whenever a matching FSItem is selected.
    """

    #-- Class Constants --------------------------------------------------------

    # The file extensions this class applies to:
    types = ()

    #-- Facet Definitions ------------------------------------------------------

    # The FSItem object associated with this item:
    item = Instance( FSItem )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, item = None, **facets ):
        """ Initializes the object.
        """
        self.item = item

        super( FSExt, self ).__init__( **facets )

    #-- Class Methods ----------------------------------------------------------

    @classmethod
    def is_ext_for ( cls, fs_item ):
        """ Returns True if this class applies to the FSItem object specified by
            *fs_item*, and False otherwise.

            The default implementation returns True if the type of the *fs_item*
            is in the set of values defined by the 'types' class constant.

            This method can be overridden by a subclass.
        """
        return (fs_item.type.lower() in cls.types)

#-- A collection of reusable FSExt subclasses ----------------------------------

#-------------------------------------------------------------------------------
#  'ImageExt' class:
#-------------------------------------------------------------------------------

class ImageExt ( FSExt ):
    """ Image file extension handler.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Accepted file extensions:
    types = ( 'png', 'jpg', 'jpeg', 'bmp', 'gif' )

    # The image corresponding to the specified file:
    image = Image

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        from facets.api import ImageEditor

        return View(
            UItem( 'image', height = -200, editor = ImageEditor() )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _item_set ( self ):
        """ Handles the 'item' facet being changed.
        """
        self.image = self.item.path

#-------------------------------------------------------------------------------
#  'TextExt' class:
#-------------------------------------------------------------------------------

class TextExt ( FSExt ):
    """ Text file extension handler.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Accepted file extensions:
    types = (
        'txt', 'py', 'c', 'h', 'cpp', 'rb', 'js', 'coffee', 'css', 'php', 'xml',
        'java'
    )

    # The text corresponding to the specified file:
    text = Str

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        from facets.api import CodeEditor

        return View(
            UItem( 'text',
                   height = -200,
                   style  = 'readonly',
                   editor = CodeEditor( show_line_numbers = False )
            )
        )

    #-- Facet Default Values ---------------------------------------------------

    def _text_default ( self ):
        from facets.core.facet_base import read_file

        return (read_file( self.item.path ) or '')

#-------------------------------------------------------------------------------
#  'WebExt' class:
#-------------------------------------------------------------------------------

class WebExt ( FSExt ):

    # Accepted file extensions:
    types = ( 'htm', 'html' )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        from facets.api import HTMLEditor

        return View(
            UItem( 'object.item.path', height = -200, editor = HTMLEditor() )
        )

#-------------------------------------------------------------------------------
#  'MarkdownExt' class:
#-------------------------------------------------------------------------------

class MarkdownExt ( FSExt ):

    # Accepted file extensions:
    types = ( 'md', )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        from facets.extra.markdown.markdown import MarkdownEditor

        return View(
            UItem( 'object.item.path',
                   height = -200,
                   editor = MarkdownEditor()
            )
        )

#-------------------------------------------------------------------------------
#  'PresentationExt' class:
#-------------------------------------------------------------------------------

class PresentationExt ( FSExt ):

    # Accepted file extensions:
    types = ( 'pres', )

    # The tool used to render the presentation:
    presentation = Any # Instance( Presentation )

    #-- Facet View Definitions -------------------------------------------------

    view = View( UItem( 'presentation', style = 'custom', height = -200 ) )

    #-- Facet Default Values ---------------------------------------------------

    def _presentation_default ( self ):
        from facets.extra.tools.presentation import Presentation

        return Presentation( file_name = self.item.path )

#-------------------------------------------------------------------------------
#  'FSFilter' class:
#-------------------------------------------------------------------------------

class FSFilter ( HasPrivateFacets ):
    """ The base class for all custom file dialog filters.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The user interface description of this filter:
    description = Str( 'All files' )

    #-- Public Methods ---------------------------------------------------------

    def is_item_for ( self, item ):
        """ Returns **True** of the FSItem specified by *item* is included by
            the filter, and **False** is it is not.
        """
        return True

# The default list of filters to use if none are specified:
default_filters = [ FSFilter() ]

#-------------------------------------------------------------------------------
#  'FSTypeFilter' class:
#-------------------------------------------------------------------------------

class FSTypeFilter ( FSFilter ):
    """ A concrete implementation of the FSFilter class that accepts files
        matching a specified of file types (usually file extensions).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of file types accepted by the filter:
    types = List # ( Str )

    # Are file type matches case sensitive?
    case_sensitive = Bool( True )

    # A user interface description of the kind of file this filter represents
    # (used to create the full 'description' value):
    kind = Str( 'All files' )

    #-- Private Facet Definitions ----------------------------------------------

    # Lower case version of the file types:
    lower_case_types = List # ( Str )

    #-- Public Methods ---------------------------------------------------------

    def is_item_for ( self, item ):
        """ Returns **True** of the FSItem specified by *item* is included by
            the filter, and **False** is it is not.
        """
        if len( self.types ) == 0:
            return True

        type = item.type
        if self.case_sensitive:
            return (type in self.types)

        return (type.lower() in self.lower_case_types)

    #-- Default Facet Values ---------------------------------------------------

    def _description_default ( self ):
        if len( self.types ) == 0:
            return self.kind

        return ('%s (%s files)' %
                ( self.kind,
                ', '.join( ('.' + type) for type in self.types ) )).strip()


    def _lower_case_types_default ( self ):
        return [ type.lower() for type in self.types ]

#-- A collection of reusable FSTypeFilter objects ------------------------------

# Any files filter:
AnyFilter = FSTypeFilter()

# Image filter:
ImageFilter = FSTypeFilter(
    kind  = 'Image',
    types = [ 'png', 'jpg', 'jpeg', 'bmp', 'gif' ]
)

# Python source files:
PythonFilter = FSTypeFilter(
    kind  = 'Python',
    types = [ 'py' ]
)

# Web source files filter:
WebFilter = FSTypeFilter(
    kind  = 'Web',
    types = [ 'htm', 'html', 'css', 'js', 'php' ]
)

# Markdown source files filter:
MarkdownFilter = FSTypeFilter(
    kind  = 'Markdown',
    types = [ 'md' ]
)

# Facets presentation source files filter:
PresentationFilter = FSTypeFilter(
    kind  = 'Presentation',
    types = [ 'pres' ]
)

# C/C++ source files filter:
CFilter = FSTypeFilter(
    kind  = 'C/C++',
    types = [ 'c', 'cpp', 'h', 'hpp' ]
)

# Generic text files filter:
TextFilter = FSTypeFilter(
    kind  = 'Text',
    types = [ 'txt', 'py', 'c', 'cpp', 'h', 'hpp', 'rb', 'js', 'coffee', 'htm',
              'html', 'css', 'php', 'xml', 'java', 'pres' ]
)

#-------------------------------------------------------------------------------
#  'FavoritesAdapter' class:
#-------------------------------------------------------------------------------

class FavoritesAdapter ( GridAdapter ):
    """ Adapts FSItem objects for display in the Favorites list.
    """

    columns = [ ( 'Name', 'ui_favorite' ) ]

    grid_visible      = False
    selected_bg_color = None
    menu              = Action( name   = 'Remove from favorites',
                                action = 'adapter.remove(object)' )

    def text_color ( self ):
        return (0x000000 if self.item.ui_enabled else 0x808080)

    def image ( self ):
        return self.item.ui_icon

    def remove ( self, item ):
        getattr( self.object, self.name ).remove( item )

#-------------------------------------------------------------------------------
#  'FilesAdapter' class:
#-------------------------------------------------------------------------------

class FilesAdapter ( GridAdapter ):
    """ Adapts FSItem objects for display in the Files list.
    """

    columns = [ ( 'Name',          'ui_name' ),
                ( 'Size',          'ui_size' ),
                ( 'Type',          'ui_type' ),
                ( 'Date Modified', 'ui_modified' ) ]

    grid_visible       = False

    ui_name_width      = Float( 0.30 )
    ui_size_width      = Float( 0.15 )
    ui_type_width      = Float( 0.15 )
    ui_modified_width  = Float( 0.40 )
    ui_size_alignment  = Str( 'right' )
    ui_name_sorter     = Callable( name_sorter )
    ui_size_sorter     = Callable( lambda l, r: cmp( l.size, r.size ) )
    ui_modified_sorter = Callable( lambda l, r: cmp( l.modified, r.modified ) )

    def text_color ( self ):
        return (0x000000 if self.item.ui_enabled else 0x808080)

    def selected_text_color ( self ):
        return self.text_color()

    def selected_bg_color ( self ):
        if self.item.is_folder:
            return 0xA8FFA0

        return (0xC8E0FF if self.item.ui_enabled else 0xFFFFFF)

    def ui_name_image ( self ):
        return self.item.ui_icon

    def double_clicked ( self ):
        item = self.item
        if item.is_folder:
            self.object.directory = item
        elif item.ui_enabled:
            self.object.open_file()

#-------------------------------------------------------------------------------
#  'NewFolderHandler' class:
#-------------------------------------------------------------------------------

class NewFolderHandler ( Handler ):
    """ Handles for the create new folder dialog.
    """

    def object_folder_name_changed ( self, info ):
        """ Handles the 'folder_name' facet being changed.
        """
        folder_name    = info.object.folder_name.strip()
        info.ui.errors = (
            (folder_name == '') or
            info.object.directory.item_for( folder_name ).exists
        )


    def close ( self, info, is_ok ):
        """ Handles the user attempting to close the dialog.
        """
        return ((not is_ok) or info.object.create_new_folder())

#-------------------------------------------------------------------------------
#  '_CustomFileDialogEditor' class:
#-------------------------------------------------------------------------------

class _CustomFileDialogEditor ( UIEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # Go back to previous history item:
    back = Button( '@icons2:ArrowLeft' )

    # Go forward to next history item:
    forward = Button( '@icons2:ArrowRight' )

    # Go up to parent directory:
    up = Button( '@icons2:ArrowUp' )

    # Refresh the contents of the current directory:
    refresh = Button( '@icons2:Reload?H32L4' )

    # Request creating a new directory:
    new = Button( '@icons:folder-new' )

    # Create a new directory:
    create = Button( '@icons:folder-new' )

    # Open/Save the current file selected:
    open = Button

    # Should the 'open' button be enabled?
    can_open = Property

    # Cancel the dialog:
    cancel = Button( 'Cancel' )

    # Set to 0 when the user clicks the 'Yes' button:
    yes = Int

    # The current history stack:
    history = List # ( FSItem )

    # The index of the current history item:
    index = Int( -1 )

    # The list of current user favorites:
    favorites = List # ( FSItem )

    # The currently selected 'favorite' directory:
    favorite = Instance( FSItem )

    # The list of recently selected files:
    recent = List # ( FSItem )

    # The list of possible directories the user might want to look in using the
    # dropdown list:
    directories = Dict # ( { FSItem: directory_name } )

    # The currently selected directory:
    selected_directory = Instance( FSItem )

    # The current directory being viewed:
    directory = Instance( FSItem )

    # The name of the current directory:
    directory_name = Property

    # The list of directories/files in the currently selected directory:
    files = List # ( FSItem )

    # The currently selected file (if any):
    selected_file = Instance( FSItem )

    # The current file (if any):
    file = Instance( FSItem )

    # The FSExt object that applies to the current file (if any):
    ext = Instance( FSExt )

    # The available set of file filters the user can apply:
    filters = Dict # ( { FSFilter: description } )

    # The current selected file filter:
    filter = Instance( FSFilter )

    # The current file name entered by the user:
    file_name = Str

    # The name of the new folder (directory) the user wants to create:
    folder_name = Str

    # Current status message:
    status = Str

    # A message to be displayed to the user:
    message = Str

    # The event fired when the user clicks the open or cancel buttons
    done = Event

    # The UIInfo object for the editor view:
    ui_info = Instance( UIInfo )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        factory = self.factory
        mode    = factory.mode
        cancel  = ('Cancel', 'Clear' )[ mode == 'accept' ]
        groups  = [
            HGroup(
                Item( 'selected_directory',
                      label   = 'Look in',
                      springy = True,
                      editor  = EnumEditor( name = 'directories' ),
                      tooltip = 'Current location, click to see other '
                                'places to look'
                ),
                UItem( 'back',
                       enabled_when = 'index > 0',
                       tooltip      = 'Go back'
                ),
                UItem( 'forward',
                       enabled_when = 'index < (len( history ) - 1)',
                       tooltip      = 'Go forward'
                ),
                UItem( 'up',
                       enabled_when = 'directory.parent is not None',
                       tooltip      = 'Go up one directory level'
                ),
                UItem( 'refresh',
                       enabled_when = 'directory is not None',
                       tooltip      = 'Refresh the list of files'
                ),
                UItem( 'new',
                       enabled_when = 'directory.can_create_folder',
                       defined_when = 'factory.mode != "open"',
                       tooltip      = 'Create a new folder'
                ),
                group_theme = '#themes:toolbar'
            ),
            HSplit(
                UItem( 'favorites',
                       width  = -75,
                       editor = GridEditor(
                           adapter     = FavoritesAdapter,
                           operations  = [],
                           selected    = 'favorite',
                           show_titles = False
                       )
                ),
                UItem( 'files',
                       id      = 'files',
                       width   = -500,
                       springy = True,
                       editor = GridEditor(
                           adapter        = FilesAdapter,
                           operations     = [ 'sort' ],
                           sort_column    = factory.sort_column,
                           sort_ascending = factory.sort_ascending,
                           selected       = 'selected_file'
                       )
                ),
                id = 'splitter'
            )
        ]

        filter_item = Item( 'filter',
              editor  = EnumEditor( name = 'filters' ),
              tooltip = 'Current filter, click to see other filters'
        )

        if mode == 'select':
            groups.extend( [
                VGroup( filter_item, group_theme = '#themes:title' ),
                VGroup( UItem( 'ext', style = 'custom' ) )
            ] )
        else:
            groups.extend( [
                VGroup(
                    Item( 'file_name', tooltip = 'Name of file' ),
                    Item( 'filter',
                          editor  = EnumEditor( name = 'filters' ),
                          tooltip = 'Current filter, click to see other filters'
                    ),
                    group_theme = '#themes:title'
                ),
                UItem( 'ext', style = 'custom' ),
                HGroup(
                    spring,
                    UItem( 'open',
                           enabled_when = 'can_open',
                           tooltip = '%s file' % mode.capitalize(),
                           editor  = ButtonEditor( label = mode.capitalize() )
                    ),
                    UItem( 'cancel',
                           tooltip = '%s request' % cancel.lower(),
                           editor  = ButtonEditor( label = cancel )
                    ),
                    group_theme = '#themes:title'
                )
            ] )

        return View( VGroup( *groups ) )

    def new_folder_view ( self ):
        if self.factory.confirm_popup:
            return View(
                VGroup(
                    HGroup(
                        Item( 'folder_name',
                              label   = 'Name',
                              tooltip = 'Enter the name of the new folder'
                        ),
                        UItem( 'create',
                               enabled_when = "folder_name != ''",
                               tooltip      = 'Create the folder'
                        )
                    ),
                    VGroup(
                        UItem( 'status', style = 'readonly' ),
                        group_theme = '@xform:b?L25'
                    ),
                    group_theme = '@std:popup'
                ),
                kind = 'popup'
            )

        return View(
            VGroup(
                Item( 'folder_name',
                      label   = 'Name',
                      tooltip = 'Enter the name of the new folder'
                ),
                UItem( 'status', style = 'readonly' )
            ),
            title   = 'Create new folder',
            kind    = 'livemodal',
            handler = NewFolderHandler,
            width   = 0.25,
            buttons = [ 'OK', 'Cancel' ]
        )

    #-- Public Method Definitions ----------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        factory = self.factory
        file    = self.value
        if isinstance( file, basestring ):
            if file == '':
                file = getcwd()

            file = LocalFSItem( abspath( file ) )

        access      = factory.access
        file.access = (access if access != 'default' else
                       AccessMap[ factory.mode ])

        if file.is_folder:
            self.selected_directory = file
        else:
            self.selected_directory = file.parent
            self.selected_file      = file

        self.sync_value( factory.done, 'done', 'to' )

        ui           = self.edit_facets( parent = parent, kind = 'editor' )
        self.ui_info = ui.info

        return ui

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        super( _CustomFileDialogEditor, self ).restore_prefs ( prefs )

        self.favorites = prefs.get( 'favorites', [] )
        self.recent    = prefs.get( 'recent',    [] )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        prefs = super( _CustomFileDialogEditor, self ).save_prefs()

        prefs[ 'favorites' ] = self.favorites[:]
        prefs[ 'recent' ]    = self.recent[:]

        return prefs


    def open_file ( self ):
        """ Attempts to open the currently selected file (if allowed).
        """
        if self.can_open:
            if self.factory.mode == 'create':
                name = self.file.name
                for item in self.directory.children:
                    if name == item.name:
                        if not self._check_overwrite():
                            return

                        break

            self._open_done()

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'file_name, files' )
    def _get_can_open ( self ):
        file_name = self.file_name.strip()
        if file_name != '':
            if self.factory.mode == 'open':
                for item in self.files:
                    if file_name == item.name:
                        break
                else:
                    return False

            return True

        return False


    @property_depends_on( 'directory' )
    def _get_directory_name ( self ):
        if self.directory is None:
            return ''

        return self.directory.path

    #-- Facet Default Values ---------------------------------------------------

    def _filters_default ( self ):
        return dict(
            [ ( filter, '%03d:%s' % ( i, filter.description ) )
              for i, filter in enumerate( self.factory.filters or
                                          default_filters ) ]
          )


    def _filter_default ( self ):
        return ((self.factory.filters or default_filters)[0])

    #-- Public Methods ---------------------------------------------------------

    def create_new_folder ( self ):
        """ If possible, create the folder specified by the current value of
            'folder_name'. Returns **True** if successful, and **False** 
            otherwise.
        """
        result      = False
        folder_name = self.folder_name.strip()
        if (folder_name == '') or (dirname( folder_name ) != ''):
            message = 'Please enter a valid folder name.'
        else:
            message = self.directory.create_folder( folder_name )
            if message is None:
                self.directory.refresh()
                self.files = self.directory.children
                message    = 'Created: ' + folder_name
                result     = True

        self.status = message

        return result

    #-- Facet Event Handlers ---------------------------------------------------

    def _directory_set ( self ):
        """ Handles the 'directory' facet being changed.
        """
        if self.directory is not None:
            self._update_directories()
            if not self._no_selected_update:
                self.selected_directory = self.directory

            if not self._no_history_update:
                self.index += 1
                self.history[ self.index: ] = [ self.directory ]


    @on_facet_set( 'directory, filter' )
    def _files_modified ( self ):
        """ Handles any facet affecting the list of files displayed being
            changed.
        """
        files = []
        if self.directory is not None:
            filter = self.filter
            files  = [ item for item in self.directory.children
                            if item.is_folder or filter.is_item_for( item ) ]

        self.files = files
        if self.file not in files:
            self.selected_file = None
            self._file_name_set()


    def _recent_set ( self ):
        """ Handles the 'recent' facet being changed.
        """
        self._update_directories()


    def _selected_directory_set ( self, old, new ):
        """ Handles the 'selected_directory' facet being changed.
        """
        if new is not None:
            if new != old:
                self._no_selected_update = True
                self.directory           = new
                self._no_selected_update = False
        elif self.directory is not None:
            do_later( self.set, selected_directory = self.directory )


    def _selected_file_set ( self, selected_file ):
        """ Handles the 'selected_file' facet being changed.
        """
        if ((selected_file is not None)   and
            (not selected_file.is_folder) and
            selected_file.ui_enabled):
            self.file = selected_file


    def _file_set ( self, file ):
        """ Handles the 'file' facet being changed.
        """
        if file is not None:
            self._no_update = True
            self.file_name  = file.name
            self._no_update = False
            self._check_ext()
            if self.factory.mode == 'select':
                self._assign_file()
        else:
            self.ext = None


    def _file_name_set ( self ):
        """ Handles the 'file_name' facet being changed.
        """
        if not self._no_update:
            file_name = self.file_name.strip()
            if (file_name != '') and (self.directory is not None):
                self.file = self.directory.item_for( file_name )
            else:
                self.file = None


    def _favorite_set ( self, favorite ):
        """ Handles the 'favorite' facet being changed.
        """
        if favorite is not None:
            if favorite.ui_enabled:
                self.directory = favorite

            do_later( self.set, favorite = None )


    def _open_set ( self ):
        """ Handles the 'open' button being clicked.
        """
        self.open_file()


    def _cancel_set ( self ):
        """ Handles the 'cancel' button being clicked.
        """
        if self.factory.mode == 'accept':
            self.file_name = ''

        self.done = False


    def _back_set ( self ):
        """ Handles the 'back' button being clicked.
        """
        self._no_history_update = True
        self.index             -= 1
        self.directory          = self.history[ self.index ]
        self._no_history_update = False


    def _forward_set ( self ):
        """ Handles the 'forward' button being clicked.
        """
        self._no_history_update = True
        self.index             += 1
        self.directory          = self.history[ self.index ]
        self._no_history_update = False


    def _up_set ( self ):
        """ Handles the 'up' button being clicked.
        """
        self.directory = self.directory.parent


    def _refresh_set ( self ):
        """ Handles the 'refresh' button being clicked.
        """
        self.directory.refresh()
        self._files_modified()


    def _new_set ( self ):
        """ Handles the 'new folder' button being clicked.
        """
        self.status      = 'Enter the name of the folder to create'
        self.folder_name = ''
        ui               = self.edit_facets( view = 'new_folder_view' )


    def _create_set ( self ):
        """ Handles the 'create folder' button being clicked.
        """
        self.create_new_folder()


    def _yes_set ( self, yes ):
        """ Handles the 'yes' facet being changed.
        """
        if yes == 0:
            self._open_done()

    #-- Private Methods --------------------------------------------------------

    def _update_directories ( self ):
        """ Update the list of directories the user might want to look in using
            the drop down list.
        """
        directories = [ item for item in self.recent if item.ui_enabled ]
        if len( self.recent ) > 0:
            directories.insert( 0, None )

        directory = self.directory
        while directory is not None:
            directories.insert( 0, directory )
            directory = directory.parent
            if directory is None:
                break

        recent_files     = '----- Recent Places -------------------------------'
        self.directories = dict(
            [ ( directory, '%03d:%s' % ( i,
                directory.ui_path if directory is not None else recent_files ) )
              for i, directory in enumerate( directories ) ] )


    def _check_ext ( self ):
        """ Checks the current file against the list of supplied FSExt classes
            to see if any match. If so, the matching class is instantiated and
            set as the current 'ext'.
        """
        file = self.file
        for ext in self.factory.exts:
            if ext.is_ext_for( file ):
                self.ext = ext( file )

                return

        self.ext = None


    def _check_overwrite ( self ):
        """ Prompts the user to see if they want to overwrite an existing file.
        """
        message = ("'%s' already exists.\n\nDo you wish to overwrite it?" %
                   self.file.name)
        if self.factory.confirm_popup:
            self.yes     = 1
            self.message = message
            self.edit_facets( parent = self.ui_info.open, view =
                View(
                    VGroup(
                        UItem( 'message', style = 'readonly' ),
                        show_labels = False,
                        group_theme = '@xform:b?L40'
                    ),
                    HGroup(
                        spring,
                        UItem( 'yes',
                               editor       = ButtonEditor(),
                               enabled_when = 'yes == 1'
                        ),
                        group_theme = '@xform:b?L25'
                    ),
                    kind = 'popup'
                )
            )
        else:
            from facets.ui.pyface.api import confirm, YES

            parent = self.ui_info.open.control
            if confirm( parent, message, 'Overwrite file?' ) == YES:
                return True

        return False


    def _open_done ( self ):
        """ Handles completion of the processing when the 'open' button is
            clicked.
        """
        directory = self.directory
        path      = directory.path
        recent    = self.recent
        for item in recent:
            if path == item.path:
                recent.remove( item )

                break

        self.recent = ([ directory ] + recent)[:6]
        self._assign_file()
        self.done = True


    def _assign_file ( self ):
        """ Assigns the currently selected file as the value of the editor.
        """
        file = self.file
        if isinstance( self.value, basestring ):
            self.value = file.path
        else:
            file.ext    = self.ext
            file.filter = self.filter
            self.value  = file

#-------------------------------------------------------------------------------
#  'CustomFileDialogEditor' class:
#-------------------------------------------------------------------------------

class CustomFileDialogEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _CustomFileDialogEditor

    # The operation mode for the editor. 'create' is like 'save', but prompts
    # the user for overwriting if the selected file already exists, whereas
    # 'save' will not. 'accept' or 'select' should be used when the editor is
    # not being used as part of a modal dialog:
    mode = Enum( 'open', 'create', 'save', 'accept', 'select' )

    # The access mode the selected file must support:
    access = Access

    # The extended facet name set to True when the user clicks Open and False
    # when the user clicks Cancel:
    done = Str

    # List of FSFilter instances that can be used by the user to filter the list
    # of files included in the view:
    filters = List( FSFilter )

    # List of FSExt subclasses that can be used by the user to provide
    # additional information about any selected file:
    exts = List # ( FSExt subclass )

    # The facets UI persistence id to save the user preference data under:
    id = Str

    # Should the confirmation query for creating a new folder or for overwriting
    # a file in 'create' mode be a popup (True) or a modal dialog (False)?
    confirm_popup = Bool( True )

    # The initial sort column name:
    sort_column = SortColumn

    # Is the initial sort order ascending (True) or descending (False)?
    sort_ascending = Bool( True )

#-- EOF ------------------------------------------------------------------------
