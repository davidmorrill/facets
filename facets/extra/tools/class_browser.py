"""
Defines the ClassBrowser tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import pyclbr

from time \
    import time, sleep

from os \
    import listdir, environ, stat

from os.path \
    import join, isdir, exists, splitext, abspath, basename, dirname

from threading \
    import Thread, Lock

from facets.api \
    import HasPrivateFacets, Str, Int, Float, List, Instance, File,        \
           Directory, Property, Any, Delegate, Bool, TreeEditor, TreeNode, \
           ObjectTreeNode, TreeNodeObject, View, Item

from facets.core.facet_db \
    import facet_db

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.api \
    import FilePosition, PythonFilePosition

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def get_cb_db ( mode = 'r' ):
    """ Gets a reference to the class browser database.
    """
    return facet_db( 'class_browser', mode )


# The lock used to manage access to the class browser data base:
cb_db_lock = Lock()

def get_pyclbr ( file_path, python_path, update_only = False ):
    """ Returns the 'pyclbr' class browser data for a specified file.
    """
    global cb_db_lock

    # Make sure the file path is a str (db doesn't like unicode):
    file_path = str( file_path )

    # Strip any trailing path separators off (just in case):
    if python_path[-1:] in '/\\':
        python_path = python_path[:-1]

    cb_db_lock.acquire()
    try:
        db      = get_cb_db()
        py_stat = stat( file_path )
        if db is not None:
            pyclbr_stat = db.get( file_path )
            if pyclbr_stat is not None:
                if pyclbr_stat.st_mtime >= py_stat.st_mtime:
                    dic = None
                    if not update_only:
                        dic = db[ file_path + '*' ]

                    return dic

            db.close()

        module, ext = splitext( file_path[ len( python_path ) + 1: ] )
        module      = module.replace( '/', '.' ).replace( '\\', '.' )
        dic         = pyclbr.readmodule( module, [ python_path ] )
        db          = get_cb_db( mode = 'c' )
        if db is not None:
            db[ file_path ]       = py_stat
            db[ file_path + '*' ] = dic

        return dic
    finally:
        if db is not None:
            db.close()

        cb_db_lock.release()

#-------------------------------------------------------------------------------
#  'CBTreeNodeObject' class:
#-------------------------------------------------------------------------------

class CBTreeNodeObject ( TreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # Cached result of 'tno_has_children':
    _has_children = Any

    # Cached result of 'tno_get_children':
    _get_children = Any

    #-- Tree Node Method Overrides ---------------------------------------------

    def tno_allows_children ( self, node ):
        """ Returns whether children of this object are allowed or not.
        """
        return True


    def tno_has_children ( self, node = None ):
        """ Returns whether or not the object has children.
        """
        if self._has_children is None:
            self._has_children = self.has_children()

        return self._has_children


    def tno_get_children ( self, node ):
        """ Gets the object's children.
        """
        if self._get_children is None:
            self._get_children = self.get_children()

        return self._get_children


    def tno_get_drag_object ( self, node ):
        """ Returns the 'draggable' version of a specified object.
        """
        return self.path


    def has_children ( self, node ):
        """ Returns whether or not the object has children.
        """
        raise NotImplementedError


    def get_children ( self ):
        """ Gets the object's children.
        """
        raise NotImplementedError

    #-- Public Methods ---------------------------------------------------------

    def extract_text ( self, text ):
        """ Extracts the Python source code for a specified item.
        """
        line_number = self.line_number
        lines       = text.split( '\n' )
        indent      = self.indent( lines[ line_number - 1 ] )

        for j in xrange( line_number, len( lines ) ):
            line = lines[j]
            if (not self.ignore( line )) and (self.indent( line ) <= indent):
                break
        else:
            j = len( lines )

        for j in xrange( j - 1, line_number - 2, -1 ):
            if not self.ignore( lines[j] ):
                j += 1
                break

        for i in xrange( line_number - 2, -1, -1 ):
            if not self.ignore( lines[i] ):
                break
        else:
            i = -1

        for i in xrange( i + 1, line_number ):
            if not self.is_blank( lines[i] ):
                break

        # Save the starting line and number of lines in the extracted text:
        self.line_number = i
        self.lines       = j - i

        # Return the extracted text fragment:
        return '\n'.join( [ line[ indent: ] for line in lines[ i: j ] ] )


    def indent ( self, line ):
        """ Returns the amount of indenting of a specified line.
        """
        return (len( line ) - len( line.lstrip() ))


    def ignore ( self, line ):
        """ Returns whether or not a specified line should be ignored.
        """
        line = line.lstrip()
        return ((len( line ) == 0) or (line.lstrip()[:1] == '#'))


    def is_blank ( self, line ):
        """ Returns whether or not a specified line is blank.
        """
        return (len( line.strip() ) == 0)

#-------------------------------------------------------------------------------
#  'CBMethod' class:
#-------------------------------------------------------------------------------

class CBMethod ( CBTreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # The class containing this method:
    parent = Any

    # The name of the file containing this class:
    path = Property

    # Name of the method:
    name = Str

    # The starting line number of the method within the source file:
    line_number = Int

    # The number of source code lines in the method:
    lines = Int

    # The text of the method:
    text = Property

    # An object associated with this class (HACK):
    object = Delegate( 'parent' )

    # The additional PythonFilePosition information provided by this object:
    file_position_info = Property

    #-- Property Implementations -----------------------------------------------

    def _get_path ( self ):
        return self.parent.path


    def _get_text ( self ):
        if self._text is None:
            self._text = self.extract_text( self.parent.parent.text )

        return self._text

    def _set_text ( self, value ):
        pass


    def _get_file_position_info ( self ):
        if self._file_position_info is None:
            self._file_position_info = self.parent.file_position_info.copy()
            self._file_position_info[ 'method_name' ] = self.name

        return self._file_position_info

    #-- Tree Node Method Overrides ---------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        return False


    def get_children ( self ):
        """ Gets the object's children.
        """
        return []


    def tno_get_drag_object ( self, node ):
        """ Returns the 'draggable' version of a specified object.
        """
        # Get the text to force 'line_number' to be set correctly:
        self.text

        return PythonFilePosition( name      = self.name,
                                   file_name = self.path,
                                   line      = self.line_number + 1,
                                   lines     = self.lines ).set(
                                   **self.file_position_info )

#-------------------------------------------------------------------------------
#  'CBClass' class:
#-------------------------------------------------------------------------------

class CBClass ( CBTreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # The module containing this class:
    parent = Any

    # The name of the file containing this class:
    path = Property

    # Name of the class:
    name = Str

    # The 'pyclbr' class descriptor:
    descriptor = Any

    # The starting line number of the class within the source file:
    line_number = Int

    # The number of source code lines in the class:
    lines = Int

    # Methods defined on the class:
    methods = List( CBMethod )

    # Should methods be displayed:
    show_methods = Delegate( 'parent' )

    # The text of the class:
    text = Property

    # An object associated with this class (HACK):
    object = Delegate( 'parent' )

    # The additional PythonFilePosition information provided by this object:
    file_position_info = Property

    #-- Property Implementations -----------------------------------------------

    def _get_path ( self ):
        return self.parent.path


    def _get_text ( self ):
        if self._text is None:
            self._text = self.extract_text( self.parent.text )

        return self._text

    def _set_text ( self ):
        pass


    def _get_file_position_info ( self ):
        if self._file_position_info is None:
            self._file_position_info = self.parent.file_position_info.copy()
            self._file_position_info[ 'class_name' ] = self.name

        return self._file_position_info

    #-- Facet Event Handlers ---------------------------------------------------

    def _descriptor_set ( self, descriptor ):
        """ Handles the 'descriptor' facet being changed.
        """
        self.line_number = descriptor.lineno

    #-- Tree Node Method Overrides ---------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        return (self.show_methods and (len( self.descriptor.methods ) > 0))


    def get_children ( self ):
        """ Gets the object's children.
        """
        methods = [ CBMethod( parent      = self,
                              name        = name,
                              line_number = line_number )
                    for name, line_number in self.descriptor.methods.items() ]
        methods.sort( lambda l, r: cmp( l.name, r.name ) )
        #self.methods = methods
        return methods


    def tno_get_drag_object ( self, node ):
        """ Returns the 'draggable' version of a specified object.
        """
        # Get the text to force 'line_number' to be set correctly:
        self.text

        return PythonFilePosition(
            name      = self.name,
            file_name = self.path,
            line      = self.line_number + 1,
            lines     = self.lines
        ).set(
            **self.file_position_info
        )

#-------------------------------------------------------------------------------
#  'CBModule' class:
#-------------------------------------------------------------------------------

class CBModule ( CBTreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # Parent of this module:
    parent = Any

    # Name of file system path to this module:
    path = Property

    # Name of the module:
    name = Str

    # The starting line number of the module:
    line_number = Int( 0 )

    # The number of source code lines in the modules:
    lines = Int( -1 )

    # Classes contained in the module:
    classes = List( CBClass )

    # Should methods be displayed:
    show_methods = Delegate( 'parent' )

    # The text of the module:
    text = Property

    # An object associated with this module:
    object = Any

    # The additional PythonFilePosition information provided by this object:
    file_position_info = Property

    #-- Property Implementations -----------------------------------------------

    def _get_path ( self ):
        return join( self.parent.path, self.name + '.py' )


    def _get_text ( self ):
        if self._text is None:
            fh = open( self.path, 'rb' )
            self._text = fh.read()
            fh.close()

        return self._text

    def _set_text ( self ):
        pass


    def _get_file_position_info ( self ):
        if self._file_position_info is None:
            self._file_position_info = self.parent.file_position_info.copy()
            self._file_position_info[ 'module_name' ] = self.name

        return self._file_position_info

    #-- Tree Node Method Overrides ---------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        dic     = get_pyclbr( self.path, self.parent.cb_path.path )
        path    = abspath( self.path )
        classes = [ CBClass( parent     = self,
                             name       = name,
                             descriptor = descriptor )
                    for name, descriptor in dic.items()
                        if path == abspath( descriptor.file ) ]
        classes.sort( lambda l, r: cmp( l.name, r.name ) )
        self.classes = classes

        return (len( self.classes ) > 0)


    def get_children ( self ):
        """ Gets the object's children.
        """
        self.tno_has_children()

        return self.classes


    def tno_get_drag_object ( self, node ):
        """ Returns the 'draggable' version of a specified object.
        """
        return PythonFilePosition( file_name = self.path ).set(
                                   **self.file_position_info )

#-------------------------------------------------------------------------------
#  'CBModuleFile' class:
#-------------------------------------------------------------------------------

class CBModuleFile ( CBTreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # Name of file system path to this module:
    path = File

    # The Python path this module is located in:
    python_path = Directory

    # Name of the module:
    name = Property

    # The starting line number of the module:
    line_number = Int( 0 )

    # The number of source code lines in the module:
    lines = Int( -1 )

    # Classes contained in the module:
    classes = List( CBClass )

    # Should methods be displayed:
    show_methods = Bool( True )

    # The text of the module:
    text = Property

    # An object associated with this module (HACK):
    object = Any

    # The additional PythonFilePosition information provided by this object:
    file_position_info = Property

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        return splitext( basename( self.path ) )[ 0 ]


    def _get_text ( self ):
        if self._text is None:
            fh = open( self.path, 'rb' )
            self._text = fh.read()
            fh.close()

        return self._text

    def _set_text ( self ):
        pass


    def _get_file_position_info ( self ):
        if self._file_position_info is None:
            path        = abspath( dirname( self.path ) )
            python_path = abspath( self.python_path )
            self._file_position_info = { 'module_name': self.name,
                                         'package_name':
                 path[ len( python_path ) + 1: ].replace( '/',  '.' ).replace(
                                                          '\\', '.' ) }

        return self._file_position_info

    #-- Tree Node Method Overrides ---------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        dic     = get_pyclbr( self.path, self.python_path )
        path    = abspath( self.path )
        classes = [ CBClass( parent     = self,
                             name       = name,
                             descriptor = descriptor )
                    for name, descriptor in dic.items()
                        if path == abspath( descriptor.file ) ]
        classes.sort( lambda l, r: cmp( l.name, r.name ) )
        self.classes = classes

        return (len( self.classes ) > 0)


    def get_children ( self ):
        """ Gets the object's children.
        """
        self.tno_has_children()
        return self.classes


    def tno_get_drag_object ( self, node ):
        """ Returns the 'draggable' version of a specified object.
        """
        return PythonFilePosition( file_name = self.path ).set(
                                   **self.file_position_info )

    #-- object Method Overrides ------------------------------------------------

    def __getstate__ ( self ):
        """ Returns the persistent state of the object.
        """
        return self.get( 'path', 'python_path', 'show_methods' )

#-------------------------------------------------------------------------------
#  'CBPackageBase' class:
#-------------------------------------------------------------------------------

class CBPackageBase ( CBTreeNodeObject ):

    #-- Tree Node Method Overrides ---------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        path = self.path
        for name in listdir( path ):
            cur_path = join( path, name )
            if isdir( cur_path ) and exists( join( cur_path, '__init__.py' ) ):
                return True

            module, ext = splitext( name )
            if ((ext == '.py') and
                CBModule( parent = self, name = module ).tno_has_children() ):
                return True

        return False


    def get_children ( self ):
        """ Gets the object's children.
        """
        packages = []
        modules  = []
        path     = self.path
        cb_path  = self.cb_path
        for name in listdir( path ):
            cur_path = join( path, name )
            if isdir( cur_path ) and exists( join( cur_path, '__init__.py' ) ):
                packages.append( CBPackage( cb_path = cb_path,
                                            parent  = self,
                                            name    = name ) )
            else:
                module, ext = splitext( name )
                if ext == '.py':
                    modules.append( CBModule( parent = self, name = module ) )

        packages.sort( lambda l, r: cmp( l.name, r.name ) )
        modules.sort(  lambda l, r: cmp( l.name, r.name ) )

        return ( packages + modules )

#-------------------------------------------------------------------------------
#  'CBPackage' class:
#-------------------------------------------------------------------------------

class CBPackage ( CBPackageBase ):

    #-- Facet Definitions ------------------------------------------------------

    # The Python path this package is part of:
    cb_path = Instance( 'CBPath' )

    # Parent of this package:
    parent = Any

    # Name of file system path to this package:
    path = Property

    # Name of the package:
    name = Str

    # The starting line number of the module:
    line_number = Int( 0 )

    # The number of source code lines in the module:
    lines = Int( -1 )

    # Should methods be displayed:
    show_methods = Delegate( 'parent' )

    # The text of the package (i.e. the '__init__.py' file):
    text = Property

    # An object associated with this package (HACK):
    object = Any

    # The additional PythonFilePosition information provided by this object:
    file_position_info = Property

    #-- Property Implementations -----------------------------------------------

    def _get_path ( self ):
        return join( self.parent.path, self.name )


    def _get_text ( self ):
        if self._text is None:
            fh = open( join( self.path, '__init__.py' ), 'rb' )
            self._text = fh.read()
            fh.close()

        return self._text

    def _set_text ( self ):
        pass


    def _get_file_position_info ( self ):
        if self._file_position_info is None:
            path    = abspath( self.path )
            cb_path = abspath( self.cb_path.path )
            self._file_position_info = { 'package_name':
                 path[ len( cb_path ) + 1: ].replace( '/',  '.' ).replace(
                                                      '\\', '.' ) }

        return self._file_position_info

#-------------------------------------------------------------------------------
#  'CBPath' class:
#-------------------------------------------------------------------------------

class CBPath ( CBPackageBase ):

    #-- Facet Definitions ------------------------------------------------------

    # The Python path this path represents (i.e. itself):
    cb_path = Property

    # Name of a file system directory used as a Python path:
    path = Str

    # Should methods be displayed:
    show_methods = Bool( True )

    # The additional PythonFilePosition information provided by this object:
    file_position_info = Property

    #-- Property Implementations -----------------------------------------------

    def _get_cb_path ( self ):
        return self


    def _get_file_position_info ( self ):
        if self._file_position_info is None:
            self._file_position_info = {}

        return self._file_position_info

#-------------------------------------------------------------------------------
#  'ClassBrowserPaths' class:
#-------------------------------------------------------------------------------

class ClassBrowserPaths ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # List of all Python source file paths in the name space:
    paths = List( CBPath )

    #-- Facet Event Handlers ---------------------------------------------------

    def _paths_set ( self, paths ):
        """ Handles the 'paths' facet being changed.
        """
        global module_analyzer

        module_analyzer.add_paths( paths )

#-------------------------------------------------------------------------------
#  'ModuleAnalyzer' class:
#-------------------------------------------------------------------------------

class ModuleAnalyzer ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The interval (in seconds) between successive scans:
    interval = Float( 600.0 )

    # The queue lock:
    lock = Any

    # The work queue:
    queue = List

    # The paths already placed on the queue:
    paths = List( Str )

    # The number of packages processed:
    packages = Int

    # The number of modules processed:
    modules = Int

    # The number of modules analyzed:
    analyzed = Int

    # The number of errors encountered:
    errors = Int

    #-- Public Methods ---------------------------------------------------------

    def add_paths ( self, paths ):
        """ Adds paths to the work queue.
        """
        paths = [ cb_path.path for cb_path in paths
                  if cb_path.path not in self.paths ]

        if len( paths ) > 0:
            self.paths.extend( paths )
            if self.lock is None:
                self.lock = Lock()
                do_later( self.start_thread )

            self.init_queue( paths )


    def init_queue ( self, paths ):
        """ Initializes the work queue.
        """
        self.lock.acquire()
        self.packages += len( paths )
        do_path        = self.do_path
        self.queue.extend( [ ( do_path, path, path ) for path in paths ] )
        self.lock.release()


    def start_thread ( self ):
        """ Starts a background class analysis thread running.
        """
        thread = Thread( target = self.process_queue )
        thread.setDaemon( True )
        thread.start()


    def process_queue ( self ):
        """ Processes items in the work queue.
        """
        start_time = time()
        while True:
            self.lock.acquire()

            if len( self.queue ) == 0:
                self.lock.release()
                start_time = time()
                while time() < ( start_time + self.interval ):
                    sleep( 1.0 )

                self.init_queue( self.paths )
                #print ('Analyzed %d out of %d modules in %d directories '
                #       'with %d errors in %.2f seconds' % ( self.analyzed,
                #       self.modules, self.packages, self.errors,
                #       time() - start_time ))
            else:
                item = self.queue.pop()
                try:
                    item[0]( *item[1:] )
                except:
                    #print 'Error processing:', item[1]
                    self.errors += 1

                self.lock.release()


    def do_path ( self, path, python_path ):
        """ Processes a Python path.
        """
        do_path   = self.do_path
        do_pyclbr = self.do_pyclbr
        dirs      = []
        files     = []
        for name in listdir( path ):
            cur_path = join( path, name )
            if isdir( cur_path ) and exists( join( cur_path, '__init__.py' ) ):
                self.packages += 1
                dirs.append( ( do_path, cur_path, python_path ) )
            else:
                module, ext = splitext( name )
                if ext == '.py':
                    self.modules += 1
                    files.append( ( do_pyclbr, cur_path, python_path ) )

        self.queue.extend( dirs + files )


    def do_pyclbr ( self, cur_path, python_path ):
        """ Processes a Python module.
        """
        if get_pyclbr( cur_path, python_path, True ) is not None:
            self.analyzed += 1

# Create a singleton module analyzer:
module_analyzer = ModuleAnalyzer()

#-------------------------------------------------------------------------------
#  Defines the class browser tree editor(s):
#-------------------------------------------------------------------------------

# Common tree nodes:
cb_tree_nodes = [
    TreeNode(       node_for   = [ ClassBrowserPaths ],
                    auto_open  = True,
                    auto_close = True,
                    children   = 'paths',
                    label      = '=Python Path' ),
    ObjectTreeNode( node_for   = [ CBPath ],
                    label      = 'path',
                    auto_close = True ),
    ObjectTreeNode( node_for   = [ CBPackage ],
                    label      = 'name',
                    auto_close = True,
                    icon_group = '@facets:package',
                    icon_open  = '@facets:package' ),
    ObjectTreeNode( node_for   = [ CBModule, CBModuleFile ],
                    label      = 'name',
                    children   = 'ignore',
                    auto_close = True,
                    icon_group = '@facets:module',
                    icon_open  = '@facets:module' ),
    ObjectTreeNode( node_for   = [ CBClass ],
                    label      = 'name',
                    auto_close = True,
                    icon_group = '@facets:class',
                    icon_open  = '@facets:class' ),
    ObjectTreeNode( node_for   = [ CBMethod ],
                    label      = 'name',
                    icon_group = '@facets:method',
                    icon_open  = '@facets:method' )
 ]

# Define a tree-only version:
cb_tree_editor = TreeEditor(
    editable = False,
    selected = 'object',
    nodes    = cb_tree_nodes
)

#-------------------------------------------------------------------------------
#  'ClassBrowser' class:
#-------------------------------------------------------------------------------

class ClassBrowser ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Class Browser' )

    # Root of the class browser tree:
    root = Instance( ClassBrowserPaths )

    # Currently selected object node:
    object = Any

    # The currently selected file position:
    file_position = Instance( FilePosition,
                        draggable = 'Drag currently selected file position.',
                        connect   = 'from:file position' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( name       = 'root',
              editor     = cb_tree_editor,
              show_label = False
        )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _root_default ( self ):
        try:
            paths = environ[ 'PYTHONPATH' ].split( ';' )
        except:
            paths = []

        if len( paths ) == 0:
            import sys
            paths = sys.path[:]

        paths.sort()

        return ClassBrowserPaths( paths = [ CBPath( path = path )
                                            for path in paths ] )

    #-- Facet Event Handlers ---------------------------------------------------

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
            self.file_position = PythonFilePosition(
                name      = value.name,
                file_name = value.path,
                line      = value.line_number + 1,
                lines     = value.lines
            ).set( **value.file_position_info )

#-------------------------------------------------------------------------------
#  Displays a class browser:
#-------------------------------------------------------------------------------

def class_browser_for ( paths = [], show_methods = True ):
    """ Displays a class browser.
    """
    if len( paths ) == 0:
        import sys

        paths = sys.path[:]

    paths.sort()

    return ClassBrowser(
        root = ClassBrowserPaths(
            paths = [ CBPath( path = path, show_methods = show_methods )
                      for path in paths ]
        )
    )

#-- EOF ------------------------------------------------------------------------