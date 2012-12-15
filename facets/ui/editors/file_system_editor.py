"""
Defines a file system editor used for viewing/selecting files or directories in
a file system.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import stat, listdir

from os.path \
    import join, abspath, basename, isdir, isfile, splitext

from time \
    import localtime, strftime

from fnmatch \
    import fnmatch

from facets.api \
    import HasPrivateFacets, Any, Constant, Int, Long, Str, Bool, List, Enum, \
           Event, View, Item, UIEditor, BasicEditorFactory, GridEditor, \
           on_facet_set

from facets.ui.hierarchical_grid_adapter \
    import HierarchicalGridAdapter

from facets.ui.helper \
    import commatize

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from column names to adapter column tuples:
ColumnsMap = {
    'size':     ( 'Size',          'size'     ),
    'type':     ( 'Type',          'type'     ),
    'modified': ( 'Date modified', 'modified' ),
    'created':  ( 'Date created',  'created'  ),
}

#-------------------------------------------------------------------------------
#  'PathItem' class:
#-------------------------------------------------------------------------------

class PathItem ( HasPrivateFacets ):
    """ Base class used for representing objects displayed in the file system
        editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The file system editor this item is associated with:
    editor = Any # Instance( _FileSystemEditor )

    # The path for the file system object:
    path = Str

    # The name of the item:
    name = Str

    # Does this item have children?
    has_children = Bool

    # The children of this item:
    children = List # ( PathItem )

    # The size of the item:
    size = Long

    # The last modified date/time of the item:
    modified = Str

    # The creation date/time of the item:
    created = Str

    # The type of the item:
    type = Str

    # The file system 'stat' information for this item:
    stat = Any

    # Event fired when the item should update itself:
    update = Event

    #-- Facet Default Values ---------------------------------------------------

    def _name_default ( self ):
        return basename( self.path )


    def _size_default ( self ):
        return self.stat.st_size


    def _modified_default ( self ):
        return strftime( '%m/%d/%Y  %I:%M:%S %p',
                         localtime( self.stat.st_mtime ) )


    def _created_default ( self ):
        return strftime( '%m/%d/%Y  %I:%M:%S %p',
                         localtime( self.stat.st_ctime ) )


    def _type_default ( self ):
        return splitext( self.path )[1][1:].upper()


    def _stat_default ( self ):
        return stat( self.path )

#-------------------------------------------------------------------------------
#  'DirectoryItem'
#-------------------------------------------------------------------------------

class DirectoryItem ( PathItem ):
    """ Defines the class used to represent file system directories.
    """

    #-- Facet Definitions ------------------------------------------------------

    has_children = True

    # Should the item monitor itself for changes?
    monitoring = Bool( False )

    #-- Facet Default Values ---------------------------------------------------

    def _size_default ( self ):
        return 0L


    def _type_default ( self ):
        return ''

    #-- Facet Default Values ---------------------------------------------------

    def _children_default ( self ):
        self.monitoring = True

        return self._update_children()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'editor:glob' )
    def _glob_modified ( self ):
        """ Handles the editor's 'glob' facet being modified.
        """
        self.children = self._update_children( self.children )


    def _update_set ( self ):
        """ Handles the 'update' event being fired.
        """
        if self.monitoring:
            self.children = self._update_children( self.children )
            for item in self.children:
                item.update = True

    #-- Private Methods --------------------------------------------------------

    def _update_children ( self, previous = None ):
        """ Returns an updated list of the children for this item.
        """
        old_dirs = {}
        if previous is not None:
            old_dirs = dict( [ (item.name, item )
                               for item in previous
                               if isinstance( item, DirectoryItem ) ] )
        directories = []
        files       = []
        path        = self.path
        editor      = self.editor
        show_files  = editor.show_files
        globs       = editor.glob.split( ',' )
        for name in listdir( path ):
            new_path = join( path, name )
            if isdir( new_path ):
                if name in old_dirs:
                    directories.append( old_dirs[ name ] )
                else:
                    directories.append(
                        DirectoryItem( path = new_path, editor = editor )
                    )
            elif show_files and isfile( new_path ):
                for glob in globs:
                    if fnmatch( new_path, glob ):
                        files.append(
                            FileItem( path = new_path, editor = editor )
                        )

                        break

        return (directories + files)

#-------------------------------------------------------------------------------
#  'RootItem' class:
#-------------------------------------------------------------------------------

class RootItem ( DirectoryItem ):
    """ Defines the class representing the root of the file system editor path.
    """

    #-- Facet Default Values ---------------------------------------------------

    def _name_default ( self ):
        return self.path

#-------------------------------------------------------------------------------
#  'FileItem' class:
#-------------------------------------------------------------------------------

class FileItem ( PathItem ):
    """ Defines the lass used to represent normal file system files.
    """

    #-- Facet Definitions ------------------------------------------------------

    has_children = False

#-------------------------------------------------------------------------------
#  'FileSystemAdapter':
#-------------------------------------------------------------------------------

class FileSystemAdapter ( HierarchicalGridAdapter ):
    """ Defines a hierarchical grid adapter for viewing file system objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    size_alignment          = Str( 'right' )
    even_bg_color           = 0xE4E4E4
    PathItem_size_formatter = Constant( lambda x: '' )
    FileItem_size_formatter = Constant( lambda x: commatize( x ) )

    #-- Hierarchical Grid Adapter Interface ------------------------------------

    def has_children ( self, item ):
        return item.has_children


    def children ( self, item ):
        return item.children


    def on_children_changed ( self, item, listener, remove ):
        if isinstance( item, DirectoryItem ):
            item.on_facet_set( listener, 'children', remove )

    #-- Grid Adapter Interface -------------------------------------------------

    def PathItem_double_clicked ( self ):
        self.object.double_clicked = self.item.path

    #-- Facet Default Values ---------------------------------------------------

    def _columns_default ( self ):
        return ([ ( 'Name', 'name' ) ] +
                [ ColumnsMap[ column ]
                  for column in self.object.factory.columns ])

#-------------------------------------------------------------------------------
#  '_FileSystemEditor' class:
#-------------------------------------------------------------------------------

class _FileSystemEditor ( UIEditor ):
    """ Defines a file system editor used for viewing/selecting files or
        directories in a file system.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The root of the file system to display:
    root = Str( facet_value = True )

    # The 'glob' pattern to use when matching files:
    glob = Str( '*', facet_value = True )

    # The file system path the user most recently double-clicked on:
    double_clicked = Str( facet_value = True )

    # Should files be shown (True) or only directories (False)?
    show_files = Bool( True )

    # Can directories be selected (True) or only files (False)?
    select_directories = Bool( True )

    # The list of pathitems being displayed:
    items = List # Instance( PathItem )

    # The currently selected file/directory item:
    selected = Any # Instance( PathItem )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'items',
              show_label = False,
              editor     = GridEditor( adapter    = FileSystemAdapter,
                                       selected   = 'selected',
                                       operations = [ 'sort' ] )
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def init_ui ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        self.facet_set( show_files         = factory.show_files,
                        select_directories = factory.select_directories )

        # Set up the threshold and context number of lines to display:
        self.glob = factory.facet_value( 'glob' )
        self.root = factory.facet_value( 'root' )

        # Set up the name of the file the user double-clicked on:
        self.double_clicked = factory.facet_value( 'double_clicked' )

        # Schedule an automatic refresh (if requested):
        if factory.refresh > 0:
            do_after( factory.refresh, self._refresh )

        # Create and return the editor view:
        return self.edit_facets( parent = parent, kind = 'editor' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _root_set ( self, root ):
        """ Handles the 'root' facet being modified.
        """
        if isdir( root ):
            self.items = [ RootItem( path = abspath( root ), editor = self ) ]


    def _selected_set ( self, item ):
        """ Handles the 'selected' facet being changed.
        """
        if (isinstance( item, FileItem ) or
            (isinstance( item, DirectoryItem) and self.select_directories)):
            self.value = item.path

    #-- Private Methods --------------------------------------------------------

    def _refresh ( self ):
        """ Refreshes the contents of the editor.
        """
        # Make sure the editor has not already been closed before proceeding:
        if self.object is not None:
            for item in self.items:
                item.update = True

            refresh = self.factory.refresh
            if refresh > 0:
                do_after( refresh, self._refresh )

#-------------------------------------------------------------------------------
#  'FileSystemEditor' class:
#-------------------------------------------------------------------------------

class FileSystemEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _FileSystemEditor

    # The root of the file system to display:
    root = Str( '/', facet_value = True )

    # The 'glob' pattern to use when matching files. More than one glob pattern
    # can be specified by separating the patterns with commas (i.e. ','):
    glob = Str( '*', facet_value = True )

    # The file system path the user most recently double-clicked on:
    double_clicked = Str( facet_value = True )

    # The interval (in milliseconds) the editor's contents are refreshed at
    # (<= 0 means no refresh occurs):
    refresh = Int( 0 )

    # Should files be shown (True) or only directories (False)?
    show_files = Bool( True )

    # Can directories be selected (True) or only files (False)?
    select_directories = Bool( False )

    # The list of file system information columns to be displayed:
    columns = List( Enum( 'size', 'type', 'modified', 'created' ),
                    [ 'size', 'type', 'modified' ] )

#-- EOF ------------------------------------------------------------------------
