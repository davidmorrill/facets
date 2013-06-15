"""
A representation of files and folders in a file system.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import hashlib

from mimetypes \
    import guess_type

from os \
    import listdir, stat, access, mkdir, makedirs, remove, walk, chmod, W_OK

from os.path \
    import abspath, join, exists, splitext, isfile, isdir, basename, dirname, \
           getsize, getatime, getmtime

from shutil \
    import copytree, copyfile, rmtree, move

from stat \
    import S_IWUSR

from facets.api \
    import HasPrivateFacets, Handler, Bool, Str, Instance, List, Float, Int,  \
           Long, Property, ReadOnly, Event,  Color, View, HGroup, Item,       \
           CodeEditor, GridEditor, ThemedButtonEditor, property_depends_on

from facets.ui.grid_adapter \
    import GridAdapter

from facets.core.facet_base \
    import read_file, write_file

#-------------------------------------------------------------------------------
#  'LinesAdapter' class:
#-------------------------------------------------------------------------------

class LinesAdapter ( GridAdapter ):
    """ Adapts the 'lines' list of a File object for use with the GridEditor.
    """

    columns          = [ ( '#', 'index' ), ( 'Text', 'line' ) ]
    grid_visible     = False
    auto_filter      = True
    auto_search      = True
    font             = 'Consolas 9, Courier 9'
    index_width      = Float( 40.0 )
    index_alignment  = Str( 'right' )
    index_text_color = Color( 0xFFFFFF )
    index_bg_color   = Color( 0x808080 )
    index_selected_bg_color = Color( 0x808080 )

    #-- Adapter Column Methods -------------------------------------------------

    def index_content ( self ):
        return (self.row + 1)


    def line_content ( self ):
        return self.item

#-------------------------------------------------------------------------------
#  'FileHandler' class:
#-------------------------------------------------------------------------------

class FileHandler ( Handler ):
    """ Defines a handler for the 'text_view' of a File object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The currently selected line number:
    selected_line = Int

    # The current cursor line:
    line = Int

    # The current cursor column:
    column = Int

    # The combined line:column information:
    line_column = Property

    # The current editor status:
    status = Str

    # Event fired when user wants to save the file:
    save = Event

    # Event fired when user wants to execute the file:
    execute = Event

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'line, column' )
    def _get_line_column ( self ):
        return ('%d:%d' % ( self.line, self.column ))

    #-- Handler Methods --------------------------------------------------------

    def handler_save_changed ( self, info ):
        """ Save the file contents when the 'save' button is clicked.
        """
        info.object.save()


    def handler_execute_changed ( self, info ):
        from time import time

        now = time()
        try:
            exec (info.object.text + '\n') in { '__name__': '__main__' }
            self.status = ('Executed in %.3f seconds' % (time() - now))
        except Exception, excp:
            import re

            msg   = str( excp )
            match = re.search( r'(.*)\(<string>,\s*line\s+(\d+)\)', msg )
            if match:
                msg = match.group( 1 )
                self.selected_line = int( match.group( 2 ) )

            self.status = msg.capitalize()

#-------------------------------------------------------------------------------
#  'File' class:
#-------------------------------------------------------------------------------

class File ( HasPrivateFacets ):
    """ A representation of files and folders in a file system.
    """

    #-- 'File' interface -------------------------------------------------------

    # The absolute path name of this file/folder:
    absolute_path = ReadOnly

    # The folder's children (for files this is always None):
    children = Property( List ) # File

    # The files contained in a directory (excludes folders):
    files = Property( List ) # File

    # The folders contained in a directory (excludes files):
    folders = Property( List ) # File

    # The file extension (for folders this is always the empty string):
    ext = Property( Str )

    # Does the file/folder exist?
    exists = Property( Bool )

    # Is this an existing file?
    is_file = Property( Bool )

    # Is this an existing folder?
    is_folder = Property( Bool )

    # Is this a Python package (ie. a folder contaning an '__init__.py' file)?
    is_package = Property( Bool )

    # Is the file/folder readonly?
    is_readonly = Property( Bool )

    # The MIME type of the file (for a folder this will always be
    # 'context/unknown' (is that what it should be?)):
    mime_type = Property( Str )

    # The last component of the path without the extension:
    name = Property( Str )

    # The parent of this file/folder (None if it has no parent):
    parent = Property( Instance( 'File' ) )

    # The path name of this file/folder:
    path = ReadOnly

    # A URL reference to the file:
    url = Property( Str )

    # The size of a file (always 0 for directories):
    size = Property( Long )

    # The time when the file was last accessed:
    last_accessed = Property

    # The time when the file was last modified:
    last_modified = Property

    # The md5 hash of the file's contents:
    md5 = Property

    # Have the contents of the file been modified:
    modified = Bool( False )

    # The data contained in the file (the empty string if it is a directory or
    # the file does not exist):
    data = Str

    # The text contents of the file (the empty string if it is a directory or a
    # file that does not exists or appears to contain binary data):
    text = Str

    # A list of text lines (i.e. text strings separated by '\n' characters)
    # contained in the file (an empty list if it is a directory, a non-existent
    # file or a file that does not appear to contain text data):
    lines = List( Str )

    #-- Facet View Definitions -------------------------------------------------

    facets_view = View(
        Item( 'lines',
              show_label = False,
              editor     = GridEditor(
                  adapter        = LinesAdapter,
                  operations     = [],
                  selection_mode = 'rows' )
        ),
        width     = 0.50,
        height    = 0.80,
        resizable = True
    )


    text_view = View(
        Item( 'text',
              show_label = False,
              editor     = CodeEditor(
                  selected_line = 'handler.selected_line',
                  line          = 'handler.line',
                  column        = 'handler.column' )
        ),
        HGroup(
            Item( 'handler.save',
                  enabled_when = 'modified',
                  tooltip      = 'Click to save file',
                  editor       = ThemedButtonEditor(
                      theme = None,
                      image = '@icons2:Floppy'
                  )
            ),
            Item( 'handler.execute',
                  defined_when = "ext == '.py'",
                  tooltip      = 'Click to execute file',
                  editor       = ThemedButtonEditor(
                      theme = None,
                      image = '@icons2:Gear?l6S62'
                  )
            ),
            '_',
            Item( 'handler.line_column',
                  style = 'readonly',
                  width = -45
            ),
            '_',
            Item( 'handler.status',
                  style   = 'readonly',
                  springy = True
            ),
            show_labels = False,
            group_theme = '#themes:toolbar_group'
        ),
        handler   = FileHandler,
        width     = 0.50,
        height    = 0.80,
        resizable = True
    )

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, path, **facets ):
        """ Creates a new representation of the specified path.
        """
        super( File, self ).__init__(
            path          = path,
            absolute_path = abspath( path ),
            **facets
        )


    def __cmp__ ( self, other ):
        """ Comparison operators.
        """
        if isinstance( other, File ):
            return cmp( self.absolute_path, other.absolute_path )

        return 1


    def __str__ ( self ):
        """ Returns an 'informal' string representation of the object.
        """
        return ('File(%s)' % self.absolute_path)

    #-- 'File' Interface -------------------------------------------------------

    #-- Property Implementations -----------------------------------------------

    def _get_children ( self ):
        """ Returns the folder's children.
        """
        return self._children_for( lambda x: True )


    def _get_files ( self ):
        """ Returns the folder's files.
        """
        return self._children_for( isfile )


    def _get_folders ( self ):
        """ Returns the folder's sub-folders.
        """
        return self._children_for( isdir )


    def _get_exists ( self ):
        """ Returns True if the file exists, otherwise False.
        """
        return exists( self.absolute_path )


    def _get_ext ( self ):
        """ Returns the file extension.
        """
        return splitext( self.absolute_path )[1]


    def _get_is_file ( self ):
        """ Returns True if the path exists and is a file.
        """
        return (self.exists and isfile( self.absolute_path ))


    def _get_is_folder ( self ):
        """ Returns True if the path exists and is a folder.
        """
        return (self.exists and isdir( self.absolute_path ))


    def _get_is_package ( self ):
        """ Returns True if the path exists and is a Python package.
        """
        return (self.is_folder and
                exists( join( self.absolute_path, '__init__.py' ) ))


    def _get_is_readonly ( self ):
        """ Returns True if the file/folder is readonly, otherwise False.
        """
        # If the File object is a folder, os.access cannot be used because it
        # returns True for both read-only and writable folders on Windows
        # systems:
        if self.is_folder:

            # Mask (i.e. 0x92) for the write-permission bits on the folder. If
            # these bits are set to zero, the folder is read-only:
            permissions = stat( self.absolute_path )[0]

            return ((permissions & 0x92) == 0)

        if self.is_file:
            return (not access( self.absolute_path, W_OK ))

        return False


    def _get_mime_type ( self ):
        """ Returns the mime-type of this file/folder.
        """
        mime_type, encoding = guess_type( self.absolute_path )
        if mime_type is None:
            mime_type = "content/unknown"

        return mime_type


    def _get_name ( self ):
        """ Returns the last component of the path without the extension.
        """
        return splitext( basename( self.absolute_path ) )[0]


    def _get_parent ( self ):
        """ Returns the parent of this file/folder.
        """
        return File( dirname( self.absolute_path ) )


    def _get_url ( self ):
        """ Returns the path as a URL.
        """
        return ('file://%s' % self.absolute_path)


    def _get_size ( self ):
        """ Returns the size of a file (returns 0 for directories).
        """
        return (getsize( self.absolute_path ) if self.is_file else 0)


    def _get_last_accessed ( self ):
        """ Returns the time at which the file was last accessed.
        """
        return (getatime( self.absolute_path ) if self.exists else 0)


    def _get_last_modified ( self ):
        """ Returns the time at which the file was last modified.
        """
        return (getmtime( self.absolute_path ) if self.exists else 0)


    def _get_md5 ( self ):
        """ Returns the md5 hash of the file's contents.
        """
        if not self.is_file:
            return ''

        return hashlib.md5( read_file( self.absolute_path ) ).hexdigest()

    #-- Facet Default Values ---------------------------------------------------

    def _data_default ( self ):
        if self.is_file:
            data = read_file( self.absolute_path )
            if data is not None:
                return data

        return ''


    def _text_default ( self ):
        text = self.data

        # If there is any suspicious data in the file, assume it is not text:
        if (text.find( '\x00' ) >= 0) or (text.find( 'xFF' ) >= 0):
            return ''

        return text


    def _lines_default ( self ):
        return self.text.split( '\n' )

    #-- Public Methods ---------------------------------------------------------

    def copy ( self, destination ):
        """ Copies this file/folder.
        """
        # Allow the destination to be a string:
        if not isinstance( destination, File ):
            destination = File( destination )

        if self.is_folder:
            copytree( self.absolute_path, destination.absolute_path )

        elif self.is_file:
            copyfile( self.absolute_path, destination.absolute_path )


    def create_file ( self, contents = '' ):
        """ Creates a file at this path.
        """
        if self.exists:
            raise ValueError( 'File %s already exists' % self.absolute_path )

        f = file( self.absolute_path, 'w' )
        f.write( contents )
        f.close()


    def create_folder ( self ):
        """ Creates a folder at this path.

            All intermediate folders MUST already exist.
        """
        if self.exists:
            raise ValueError( 'Folder %s already exists' % self.absolute_path )

        mkdir( self.absolute_path )


    def create_folders ( self ):
        """ Creates a folder at this path.

            This will attempt to create any missing intermediate folders.
        """
        if self.exists:
            raise ValueError( 'Folder %s already exists' % self.absolute_path )

        makedirs( self.absolute_path )


    def create_package ( self ):
        """ Creates a package at this path.

            All intermediate folders/packages MUST already exist.
        """
        if self.exists:
            raise ValueError( 'Package %s already exists' % self.absolute_path )

        mkdir( self.absolute_path )

        # Create the '__init__.py' file that actually turns the folder into a
        # package:
        File( join( self.absolute_path, '__init__.py' ) ).create_file()


    def delete ( self ):
        """ Deletes this file/folder.

            Does nothing if the file/folder does not exist.
        """
        if self.is_folder:
            # Try to make sure that everything in the folder is writeable:
            self.make_writeable()

            # Delete it:
            rmtree( self.absolute_path )

        elif self.is_file:
            # Try to make sure that the file is writeable:
            self.make_writeable()

            # Delete it:
            remove( self.absolute_path )


    def make_writeable ( self ):
        """ Attempt to make the file/folder writeable.
        """
        if self.is_folder:
            # Try to make sure that everything in the folder is writeable
            # (i.e., can be deleted). This comes in especially handy when
            # deleting '.svn' directories:
            for path, dirnames, filenames in walk( self.absolute_path ):
                for name in (dirnames + filenames):
                    filename = join( path, name )
                    if not access( filename, W_OK ):
                        chmod( filename, S_IWUSR )

        elif self.is_file:
            # Try to make sure the file is writeable (i.e. can be deleted):
            if not access( self.absolute_path, W_OK ):
                chmod( self.absolute_path, S_IWUSR )


    def move ( self, destination ):
        """ Moves this file/folder.
        """
        # Allow the destination to be a string:
        if not isinstance( destination, File ):
            destination = File( destination )

        # Try to make sure that everything in the directory is writeable:
        self.make_writeable()

        # Move it:
        move( self.absolute_path, destination.absolute_path )


    def save ( self ):
        """ Saves the current 'data' contents of the file back to the file
            system.
        """
        if write_file( self.absolute_path, self.data ):
            self.modified = False


    def files_of_type ( self, *extensions ):
        """ Returns all files within a folder than have any of the file
            extensions specified by *extensions*.
        """
        return self._children_for(
            lambda x: (splitext( x )[1] in extensions) and isfile( x )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _lines_set ( self ):
        """ Handles the file 'lines' list being replaced.
        """
        self.text = '\n'.join( self.lines )


    def _lines_items_set ( self ):
        """ Handles the file 'lines' list being changed.
        """
        self._lines_set()


    def _text_set ( self, text ):
        """ Handles the file 'text' string being changed.
        """
        self.data = text


    def _data_set ( self ):
        """ Handles the file 'data' being changed.
        """
        self.modified = True

    #-- Private Methods --------------------------------------------------------

    def _children_for ( self, filter ):
        """ Returns all children of the folder which match a specified filter.

            Returns an empty list if the item is not a folder or valid path.
        """
        files = []
        if self.is_folder:
            path  = self.absolute_path
            klass = self.__class__
            try:
                for name in listdir( path ):
                    file = join( path, name )
                    if filter( file ):
                        files.append( klass( file ) )
            except:
                # Handle the user not having read access to the directory:
                pass

        return files

#-- EOF ------------------------------------------------------------------------