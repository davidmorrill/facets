"""
A feature-enabled file sieve tool.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from threading \
    import Thread

from time \
    import sleep, time, localtime, strftime

from os \
    import walk, stat

from os.path \
    import abspath, dirname, basename, splitext, isdir, split, join

from stat \
    import ST_SIZE, ST_MTIME

from facets.api \
    import HasPrivateFacets, Str, Int, Long, Enum, List, Float, Bool, \
           Property, Button, Instance, Directory, FacetType, FacetError, \
           cached_property, property_depends_on, View, VGroup, HGroup, \
           Item, GridEditor, TitleEditor, DirectoryEditor, Handler

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.i_filter \
    import Filter

from facets.ui.helper \
    import commatize

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# How many files need to be processed before adding to files list:
BatchSize = 100

# How long to sleep (in seconds) before rebuilding the file list:
SleepInterval = 600

# Mapping from standard Python-like relation to legal method name version:
RelationMap = {
    '>=': 'ge',
    '>':  'gt',
    '<=': 'le',
    '<':  'lt',
    '=':  'eq',
    '==': 'eq',
    '!=': 'ne'
 }

# Mapping from date units to seconds:
DateMap = {
    's': 1,
    'M': 60,
    'h': 60 * 60,
    'd': 60 * 60 * 24,
    'w': 60 * 60 * 24 * 7,
    'm': 60 * 60 * 24 * 30,
    'y': 60 * 60 * 24 * 365
 }

#-------------------------------------------------------------------------------
#  Grid adapter/editor definitions:
#-------------------------------------------------------------------------------

class FilesGridAdapter ( GridAdapter ):

    # The columns to display:
    columns = [
        'root', 'ext' , 'dir' , 'size', 'date_time',
        # 'name', 'path', 'date', 'time'
    ]
    even_bg_color = 0xF8F8F8

    # Column titles:
    root_title      = Str( 'File Root' )
    ext_title       = Str( 'Ext.' )
    dir_title       = Str( 'Directory' )
    size_title      = Str( 'Size' )
    date_time_title = Str( 'Date/Time' )
    name_title      = Str( 'File Name' )

    # Column widths:
    root_width          = Float( 0.20 )
    path_width          = Float( 0.40 )
    name_width          = Float( 0.20 )
    ext_width           = Float( 0.07 )
    dir_width           = Float( 0.49 )
    size_width          = Float( 0.08 )
    date_width          = Float( 0.10 )
    time_width          = Float( 0.10 )
    date_time_width     = Float( 0.14 )

    # Field value properties:
    path_text           = Property
    size_text           = Property
    date_text           = Property
    time_text           = Property
    date_time_text      = Property

    # Column formatting string:
    date_format         = Str( '%m/%d/%y' )
    time_format         = Str( '%I:%M %p' )
    date_time_format    = Str( '%m/%d/%y %I:%M %p' )

    # Column alignments:
    size_alignment      = Str( 'right' )
    date_alignment      = Str( 'center' )
    time_alignment      = Str( 'center' )
    date_time_alignment = Str( 'center' )

    #-- Property Implementations -----------------------------------------------

    def _get_path_text ( self ):
        item   = self.item
        result = item.path[ item.prefix: ]
        if result != '':
            return result

        return '\\'


    def _get_size_text ( self ):
        return commatize( self.item.size )


    def _get_date_text ( self ):
        return strftime( self.date_format, localtime( self.item.date ) )


    def _get_time_text ( self ):
        return strftime( self.time_format, localtime( self.item.date ) )


    def _get_date_time_text ( self ):
        return strftime( self.date_time_format, localtime( self.item.date ) )


files_grid_editor = GridEditor(
    adapter        = FilesGridAdapter,
    selection_mode = 'rows',
    selected       = 'selected_files',
    filter         = 'filter',
    operations     = [ 'sort' ]
)

#-------------------------------------------------------------------------------
#  'Size' facet:
#-------------------------------------------------------------------------------

class Size ( FacetType ):

    is_mapped     = True
    default_value = ''
    info_text = "a file size of the form: ['<='|'<'|'>='|'>'|'='|'=='|'!=']ddd"

    def value_for ( self, value ):
        if isinstance( value, basestring ):
            value = value.strip()
            if len( value ) == 0:
                return ( 'ignore', 0 )

            relation = '<='
            c        = value[0]
            if c in '<>!=':
                relation = c
                value    = value[1:]
                c        = value[0:1]
                if c == '=':
                    relation += c
                    value     = value[1:]
                value = value.lstrip()

            relation = RelationMap[ relation ]

            try:
                size = int( value )
                if size >= 0:
                    return ( relation, size )
            except:
                pass

        raise FacetError

    mapped_value = value_for


    def post_setattr ( self, object, name, value ):
        object.__dict__[ name + '_' ] = value


    def as_cfacet ( self ):
        """ Returns a CFacet corresponding to the facet defined by this class.
        """
        # Tell the C code that the 'post_setattr' method wants the modified
        # value returned by the 'value_for' method:
        return super( Size, self ).as_cfacet().setattr_original_value( True )

#-------------------------------------------------------------------------------
#  'Age' facet:
#-------------------------------------------------------------------------------

class Age ( Size ):

    info_text = ( "a time interval of the form: ['<='|'<'|'>='|'>'|'='|'=='"
                 "|'!=']ddd['s'|'m'|'h'|'d'|'w'|'M'|'y']" )

    def value_for ( self, value ):
        if isinstance( value, basestring ):
            value = value.strip()
            if len( value ) == 0:
                return ( 'ignore', 0 )

            units = value[-1:].lower()
            if units in 'smhdwy':
                if units == 'm':
                    units = value[-1:]
                value = value[:-1].strip()
            else:
                units = 'd'

            if (len( value ) == 0) or (value[-1:] not in '0123456789'):
                value += '1'

            try:
                relation, time = super( Age, self ).value_for( value )
                return ( relation, time * DateMap[ units ] )
            except:
                pass

        raise FacetError

#-------------------------------------------------------------------------------
#  'FileFilter' class:
#-------------------------------------------------------------------------------

class FileFilter ( Filter ):
    """ Filter for FileSieve files.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The full file name path:
    path = Str

    # The root portion of the file name:
    root = Str

    # The extension portion of the file name:
    ext = Str

    # The extension matching rule:
    ext_rule = Enum( 'in', 'eq', 'ne', 'not' )

    # The actual extension to match:
    ext_match = Str

    # The file size:
    size = Size

    # How recently was the file updated?
    age = Age

    # Should the file be read-only or not?
    mode = Enum( "Don't care", "Read only", "Read/Write" )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'root', label = 'File Root' ),
        Item( 'ext',  label = 'Ext.', width = -40 ),
        Item( 'path', label = 'Directory' ),
        Item( 'size', width = -60 ),
        Item( 'age', width = -60 ),
#        '_',
#        Item( 'mode' ),
    )

    #-- Filter Method Overrides ------------------------------------------------

    def filter ( self, object ):
        """ Returns whether a specified object meets the filter criteria.
        """
        return ((object.path.find( self.path ) >= 0)       and
                (object.root.find( self.root ) >= 0)       and
                self._ext_test(  object.ext )              and
                self._size_test( object.size )             and
                self._age_test(  object.date, object.now ) and
                self._mode_test( object.read_only ))

    #-- Event Handlers ---------------------------------------------------------

    def _ext_set ( self, ext ):
        """ Handles the 'ext' facet being changed.
        """
        ext = ext.strip()
        if ext[0:1] == '=':
            self.ext_rule = 'eq'
            ext           = ext[1:]
            if ext[0:1] == '=':
                ext = ext[1:]
        elif ext[0:2] == '!=':
            self.ext_rule = 'ne'
            ext           = ext[2:]
        elif ext[0:1] == '!':
            self.ext_rule = 'not'
            ext           = ext[1:]
        else:
            self.ext_rule = 'in'

        self.ext_match = ext

    #-- Private Methods --------------------------------------------------------

    def _ext_test ( self, ext ):
        """ Returns whether a specified file extension passes the ext relation.
        """
        return getattr( self, '_ext_' + self.ext_rule )( ext, self.ext_match )


    def _ext_in ( self, ext, match ):
        return (ext.find( match ) >= 0)


    def _ext_not ( self, ext, match ):
        return (ext.find( match ) < 0)


    def _ext_eq ( self, ext, match ):
        return (ext == match)


    def _ext_ne ( self, ext, match ):
        return (ext != match)


    def _size_test ( self, size ):
        """ Returns whether a specified file size passes the size relation.
        """
        relation, limit = self.size_

        return getattr( self, '_size_' + relation )( size, limit )


    def _size_le ( self, size, limit ):
        return (size <= limit)


    def _size_lt ( self, size, limit ):
        return (size < limit)


    def _size_ge ( self, size, limit ):
        return (size >= limit)


    def _size_gt ( self, size, limit ):
        return (size > limit)


    def _size_eq ( self, size, limit ):
        return (size == limit)


    def _size_ne ( self, size, limit ):
        return (size != limit)


    def _size_ignore ( self, size, limit ):
        return True


    def _age_test ( self, date, now ):
        """ Returns whether a specified file date passes the age relation.
        """
        relation, age = self.age_

        return getattr( self, '_age_' + relation )( date, now - age )


    def _age_le ( self, date, age ):
        return (date >= age)


    def _age_lt ( self, date, age ):
        return (date > age)


    def _age_ge ( self, date, age ):
        return (date <= age)


    def _age_gt ( self, date, age ):
        return (date < age)


    def _age_eq ( self, date, age ):
        return (date == age)


    def _age_ne ( self, date, age ):
        return (date != age)


    def _age_ignore ( self, date, age ):
        return True


    def _mode_test ( self, readonly ):
        """ Returns whether a specified file's readonly state passes the mode
            relation.
        """
        return ((self.mode == "Don't care") or
               ((self.mode == "Read only")  and readonly) or
               ((self.mode == "Read/Write") and (not readonly)))

#-------------------------------------------------------------------------------
#  'File' class:
#-------------------------------------------------------------------------------

class File ( HasPrivateFacets ):
    """ Represents a single file in a FileSieve.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The fully-qualified name of a file:
    path = Str

    # The length of the common path prefix:
    prefix = Int

    # The file directory:
    dir = Property

    # The name of the file minus any directory information:
    name = Property

    # The root of the file name (name minus file extension information):
    root = Property

    # The file extension:
    ext = Property

    # The size of the file:
    size = Long

    # The last modified date of the file:
    date = Long

    # The time at which this object was created:
    now = Float

    # Is the file read-only?
    read_only = Bool

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_dir ( self ):
        return dirname( self.path )


    @cached_property
    def _get_name ( self ):
        return basename( self.path )


    @cached_property
    def _get_root ( self ):
        return splitext( self.name )[0]


    @cached_property
    def _get_ext ( self ):
        return splitext( self.name )[1][1:]

    #-- Facet Event Handlers ---------------------------------------------------

    def _path_set ( self, path ):
        try:
            info           = stat( path )
            self.size      = info[ ST_SIZE ]
            self.date      = info[ ST_MTIME ]
            self.read_only = False  # fixme: Implement this...
        except:
            pass

#-------------------------------------------------------------------------------
#  'FileWorker' class:
#-------------------------------------------------------------------------------

class FileWorker ( HasPrivateFacets ):
    """ Background thread for initializing and maintaining a list of files
        for a specified path.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The sieve object whose file list we are updating:
    sieve = Instance( 'FileSieve' )

    # The path being processed:
    path = Str

    # The file extension being processed:
    ext = Str

    # Should the thread be aborted?
    abort = Bool( False )

    #-- Event Handlers ---------------------------------------------------------

    def _path_set ( self ):
        thread = Thread( target = self._process )
        thread.setDaemon( True )
        thread.start()

    #-- Private Methods --------------------------------------------------------

    def _process ( self ):
        """ Process all of the files contained in the specified path.
        """
        path, ext, sieve = self.path, self.ext, self.sieve
        prefix = len( path )

        # Delete all current files (if any):
        del sieve.files[:]

        # Make sure the extension (if any) is in the correct format:
        if (ext != '') and (ext[:1] != '.'):
            ext = '.' + ext

        # Get the current time stamp:
        now = time()

        # Make the initial pass, emitting the file in small batches so that the
        # user gets some immediate feedback:
        files = []
        for dir, dir_names, file_names in walk( path ):
            for file_name in file_names:
                # Exit if the user has aborted us:
                if self.abort:
                    return

                # Add the file to the current batch if the extension matches:
                if (ext == '') or (ext == splitext( file_name )[1]):
                    files.append( File( path   = join( dir, file_name ),
                                        prefix = prefix,
                                        now    = now ) )

                # If we've reached the batch size, add to files to the sieve
                # object, and start a new batch:
                if len( files ) >= BatchSize:
                    sieve.files.extend( files )
                    del files[:]

        # Make sure we emit the last partial batch (may be empty):
        sieve.files.extend( files )

        # Continue to rebuild the list periodically as long as the user has not
        # aborted us:
        while not self.abort:

            # Sleep for a while:
            for i in range( SleepInterval ):
                sleep( 1 )
                if self.abort:
                    self.sieve = None
                    return

            # Get the current time stamp:
            now = time()

            # Iterate over the files again, this time just building a single,
            # large list:
            files = []
            for dir, dir_names, file_names in walk( path ):
                for file_name in file_names:
                    # Exit if the user has aborted us:
                    if self.abort:
                        self.sieve = None
                        return

                    # Add the file to the list if the extension matches:
                    if (ext == '') or (ext == splitext( file_name )[1]):
                        files.append( File( path   = join( dir, file_name ),
                                            prefix = prefix,
                                            now    = now ) )

            # Finally, send all files to the sieve at once, so that the user
            # just sees a single update:
            self.sieve.files = files

#-------------------------------------------------------------------------------
#  'FileSieveHandler' class:
#-------------------------------------------------------------------------------

class FileSieveHandler ( Handler ):

    #-- Public Methods ---------------------------------------------------------

    def closed ( self, info, is_ok ):
        """ Handles the FileSieve view being closed.
        """
        fs = info.object
        if fs.worker is not None:
            fs.worker.abort = True
            fs.worker       = None

#-------------------------------------------------------------------------------
#  'FileSieve' class:
#-------------------------------------------------------------------------------

class FileSieve ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'File Sieve'

    # The path specifying the files to be listed:
    path = Directory( save_state = True, connect = 'to: path to sieve' )

    # Extension to match on:
    ext = Str

    # Should subdirectories of the path be included?
    recursive = Bool( True )

    # The filter used to 'sieve' the list of files:
    filter = Instance( FileFilter, (), save_state = True )

    # The list of files containing in the specified path:
    files = List( File )

    # The list of currently selected files:
    selected_files = List( File )

    # The list of selected file names:
    selected_file_names = Property( connect = 'from: selected file names' )

    # The list of filtered files:
    filtered_files = Property( connect = 'from: filtered file objects' )

    # The list of filtered file names:
    filtered_file_names = Property( connect = 'from: filtered file names' )

    # The total number of files being displayed:
    num_files = Property

    # The total size of all filtered files:
    size = Property

    # Base path (in normalized form):
    base_path = Str

    # The list of components to show in the user interface (the valid values
    # are: path, filter, title:
    show = Str( 'title' )

    #-- Private Facet Definitions ----------------------------------------------

    # Select all listed files button:
    select_all = Button( 'Select All' )

    # The current file worker thread object we are using:
    worker = Instance( FileWorker )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'path',
              id           = 'path',
              editor       = DirectoryEditor( entries = 10 ),
              defined_when = "object.show.find('path')>=0"
        ),
        Item( 'filter',
              show_label   = False,
              style        = 'custom',
              defined_when = "object.show.find('filter')>=0"
        ),
#       '_',
#       Item( 'recursive' ),
        VGroup(
            HGroup(
                Item( 'base_path',
                      label   = 'Path',
                      editor  = TitleEditor(),
                      springy = True
                ),
                '_',
                Item( 'ext',
                      editor = TitleEditor()
                ),
                '_',
                Item( 'num_files',
                      label       = 'Files',
                      style       = 'readonly',
                      format_func = commatize,
                      width       = -40 ),
                '_',
                Item( 'size',
                      style       = 'readonly',
                      format_func = commatize,
                      width       = -70 ),
                '_',
                Item( 'select_all',
                      show_label   = False,
                      enabled_when = 'len( files ) > 0'
                ),
                defined_when = "object.show.find('title')>=0"
            ),
            Item( 'files',
                  id     = 'filtered_files',
                  editor = files_grid_editor
            ),
            dock        = 'horizontal',
            show_labels = False
        ),
        title     = 'File Sieve',
        id        = 'facets.extra.tools.file_sieve.FileSieve',
        width     = 0.6,
        height    = 0.7,
        resizable = True,
        handler   = FileSieveHandler
    )

    def options ( self ):
        show_path   = (self.show.find( 'path' )   < 0)
        show_filter = (self.show.find( 'filter' ) < 0)
        if show_path or show_filter:
            items = []
            if show_path:
                items.append( Item(
                    'path',
                    id     = 'path',
                    editor = DirectoryEditor( entries = 10 ),
                    width  = 400
                ) )

            if show_filter:
                items.append( Item(
                    'filter',
                    show_label = False,
                    style      = 'custom',
                    width      = 600
                ) )

            return View(
                VGroup( *items,
                        group_theme = '#themes:tool_options_group'
                )
            )

        return None

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'filtered_files' )
    def _get_num_files ( self ):
        return len( self.filtered_files )


    @property_depends_on( 'filtered_files' )
    def _get_size ( self ):
        return reduce( lambda l, r: l + r.size, self.filtered_files, 0L )


    @property_depends_on( 'selected_files' )
    def _get_selected_file_names ( self ):
        return [ f.path for f in self.selected_files ]


    @property_depends_on( 'files, filter:changed' )
    def _get_filtered_files ( self ):
        filter = self.filter.filter

        return [ f for f in self.files if filter( f ) ]


    @property_depends_on( 'filtered_files' )
    def _get_filtered_file_names ( self ):
        return [ f.path for f in self.filtered_files ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _path_set ( self, path ):
        """ Handles the 'path' facet being changed.
        """
        # Make sure the path has been normalized:
        path = abspath( path )

        # Determine the correct starting directory and optional file extension
        # to match on:
        ext = self.ext
        if not isdir( path ):
            path, name = split( path )
            if not isdir( path ):
                del self.files[:]
                return

            root, ext = splitext( name )

        self.base_path = path
        self.ext       = ext

        if self.worker is not None:
            self.worker.abort = True

        self.worker = FileWorker( sieve = self, ext = ext ).set( path = path )


    def _select_all_set ( self ):
        """ Handles the 'Select All' button being pressed.
        """
        self.selected_files = self.filtered_files


    def _recursive_set ( self, recursive ):
        """ Handles the 'recursive' facet being changed.
        """
        # fixme: Implement this...


#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import facet_db

    FileSieve(
        path = dirname( facet_db.__file__ ),
        show = 'path,filter,title'
    ).edit_facets()

#-- EOF ------------------------------------------------------------------------