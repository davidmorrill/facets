"""
A Facets UI demo framework.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import re

from os \
    import listdir

from os.path \
    import join, isdir, split, splitext, dirname, abspath

from facets.api \
    import HasFacets, HasPrivateFacets, DelegatesTo, Str, Instance, Property, \
           Any, Bool, Code, Button, HTML, TreeEditor, ObjectTreeNode,         \
           TreeNodeObject, View, Item, UItem, HSplit, VSplit, Tabbed, VGroup, \
           HGroup, Heading, Handler, UIInfo, InstanceEditor, HTMLEditor,      \
           Include, spring, on_facet_set, inn

from facets.extra.helper.source_xref \
    import SourceXRef, RefFile

from facets.extra.tools.text_file \
    import TextFile

#-------------------------------------------------------------------------------
#  Global data:
#-------------------------------------------------------------------------------

# Define the code used to populate the 'execfile' dictionary:
exec_str =  """from facets.core_api \
    import *

"""

#-------------------------------------------------------------------------------
#  Useful Helper Functions:
#-------------------------------------------------------------------------------

def user_name_for ( name ):
    """ Return a 'user-friendly' name for a specified string.
    """
    name = name.replace( '_', ' ' )

    return name[:1].upper() + name[1:]


def parse_source ( file_name ):
    """ Parses the contents of a specified source file into module comment and
        source text.
    """
    try:
        fh     = open( file_name, 'rb' )
        source = fh.read().strip()
        fh.close()

        # Extract out the module comment as the description:
        comment = ''
        quotes  = source[:3]
        if (quotes == '"""') or (quotes == "'''"):
            col = source.find( quotes, 3 )
            if col >= 0:
                comment = source[ 3: col ]
                source  = source[ col + 3: ].strip()

        return ( comment, source )
    except:
        return ( '', '' )

#-------------------------------------------------------------------------------
#  'DemoFileHandler' class:
#-------------------------------------------------------------------------------

class DemoFileHandler ( Handler ):

    #-- Facet Definitions ------------------------------------------------------

    # The current 'info' object (for use by the 'write' method):
    info = Instance( UIInfo )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, info ):
        """ Initializes the view.
        """
        # Save the reference to the current 'info' object:
        self.info = info

        # Set up the 'print' logger:
        df         = info.object
        df.log     = ''
        #sys.stdout = sys.stderr = self

        # Read in the demo source file:
        df.description, df.source = parse_source( df.path )

        # Try to run the demo source file:
        locals = df.parent.init_dic.copy()
        locals[ '__name__' ] = '___main___'
        sys.modules[ '__main__' ].__file__ = df.path
        try:
            execfile( df.path, locals, locals )
            df.demo = df.demo_for( locals )
        except Exception, excp:
            df.demo = DemoError( msg = str( excp ) )


    def closed ( self, info, is_ok ):
        """ Closes the view.
        """
        object = info.object
        inn( object.demo, 'dispose' )()
        object.demo = None

    #-- Handles 'print' Output -------------------------------------------------

    def write ( self, text ):
        self.info.object.log += text


    def flush ( self ):
        pass

# Create a singleton instance:
demo_file_handler = DemoFileHandler()

#-------------------------------------------------------------------------------
#  'DemoError' class:
#-------------------------------------------------------------------------------

class DemoError ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The error message text:
    msg = Code

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        VGroup(
            Heading( 'Error in source file' ),
            Item( 'msg', style = 'custom', show_label = False ),
        )
    )

#-------------------------------------------------------------------------------
#  'DemoButton' class:
#-------------------------------------------------------------------------------

class DemoButton ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The demo to be launched via a button:
    demo = Instance( HasFacets )

    # The demo view item to use:
    demo_item = Item( 'demo',
        show_label = False,
        editor     = InstanceEditor( label = 'Run demo...', kind = 'live' )
    )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        VGroup(
            VGroup(
                Heading( 'Click the button to run the demo:' ),
                '20'
            ),
            HGroup(
                spring,
                Include( 'demo_item' ),
                spring
            )
        ),
        resizable = True
    )

#-------------------------------------------------------------------------------
#  'ModalDemoButton' class:
#-------------------------------------------------------------------------------

class ModalDemoButton ( DemoButton ):

    #-- Facet Definitions ------------------------------------------------------

    # The demo view item to use:
    demo_item = Item( 'demo',
        show_label = False,
        editor     = InstanceEditor( label = 'Run demo...', kind = 'modal' )
    )

#-------------------------------------------------------------------------------
#  'DemoTreeNodeObject' class:
#-------------------------------------------------------------------------------

class DemoTreeNodeObject ( TreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # Cached result of 'tno_has_children':
    _has_children = Any

    # Cached result of 'tno_get_children':
    _get_children = Any

    #-- Public Methods ---------------------------------------------------------

    def find ( self, path ):
        """ Returns the node that matches the specified *path*, or None if no
            match is found.
        """
        self_path = self.path
        if path == self_path:
            return self

        if self.allows_children and (self_path == path[ : len( self_path ) ]):
            for node in self.tno_get_children():
                result = node.find( path )
                if result is not None:
                    return result

        return None


    def tno_allows_children ( self, node ):
        """ Returns whether chidren of this object are allowed or not.
        """
        return self.allows_children


    def tno_has_children ( self, node = None ):
        """ Returns whether or not the object has children.
        """
        if self._has_children is None:
            self._has_children = self.has_children()

        return self._has_children


    def tno_get_children ( self, node = None ):
        """ Gets the object's children.
        """
        if self._get_children is None:
            self._get_children = self.get_children()

        return self._get_children


    def has_children ( self, node ):
        """ Returns whether or not the object has children.
        """
        raise NotImplementedError


    def get_children ( self, node ):
        """ Gets the object's children.
        """
        raise NotImplementedError

#-------------------------------------------------------------------------------
#  'DemoFile' class:
#-------------------------------------------------------------------------------

class DemoFile ( DemoTreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # Parent of this file:
    parent = Any

    # Name of file system path to this file:
    path = Property

    # Name of the file:
    name = Str

    # UI form of the 'name':
    nice_name = Property

    # Files don't allow children:
    allows_children = Bool( False )

    # Description of what the demo does:
    description = HTML

    # Source code for the demo:
    source = DelegatesTo( 'text_file', 'text' )

    # Demo object whose facets UI is to be displayed:
    demo = Instance( HasFacets )

    # Log of all print messages displayed:
    log = Code

    # The TextFile object used to edit the source code:
    text_file = Instance( TextFile )

    # Event fired when the user wants to re-execute the demo code:
    execute = Button( '@icons2:Gear?l6S62' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Tabbed(
            UItem( 'demo',
                   style     = 'custom',
                   label     = 'Demo',
                   resizable = True
            ),
            UItem( 'description',
                   label  = 'Description',
                   style  = 'readonly',
                   editor = HTMLEditor( format_text = True )
            ),
            UItem( 'text_file',
                   style = 'custom',
                   label = 'Source'
            ),
            UItem( 'log',
                   style = 'readonly',
                   label = 'Log'
            ),
            dock   = 'tab',
            export = 'DockWindowShell',
            id     = 'tabbed'
        ),
        id      = 'facets.ui.demos.demo.file_view',
        handler = demo_file_handler
    )

    #-- Facet Default Values ---------------------------------------------------

    def _text_file_default ( self ):
        return TextFile( toolbar_items = [
            UItem( 'context.execute', tooltip = 'Reload the demo' )
        ] )

    #-- Property Implementations -----------------------------------------------

    def _get_path ( self ):
        return join( self.parent.path, self.name + '.py' )


    def _get_nice_name ( self ):
        return user_name_for( self.name )

    #-- Public Methods ---------------------------------------------------------

    def demo_for ( self, locals ):
        """ Returns the demo object found within the spwcified *locals*
            dictionary.
        """
        demo = self._get_object( 'modal_popup', locals )
        if demo is not None:
            demo = ModalDemoButton( demo = demo )
        else:
            demo = self._get_object( 'popup', locals )
            if demo is not None:
                demo = DemoButton( demo = demo )
            else:
                demo = self._get_object( 'demo', locals )

        return demo


    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        return False

    #-- Facet Event Handlers ---------------------------------------------------

    def _execute_set ( self ):
        """ Handles the user clicking the execute button.
        """
        # Try to run the current demo source view code:
        text_file = self.text_file
        locals    = self.parent.init_dic
        locals[ '__name__' ] = '___main___'
        sys.modules[ '__main__' ].__file__ = self.path
        try:
            exec (self.source + '\n') in locals
            demo = self.demo_for( locals )
            if demo is None:
                text_file.status = 'No demo object is defined.'
            else:
                self.demo        = demo
                text_file.status = 'The demo has been reloaded successfully.'
        except Exception, excp:
            msg   = str( excp )
            match = re.search( r'(.*)\(<string>,\s*line\s+(\d+)\)', msg )
            if match:
                msg = match.group( 1 )
                text_file.selected_line = int( match.group( 2 ) )

            text_file.status = msg.capitalize()

    #-- Private Methods --------------------------------------------------------

    def _get_object ( self, name, dic ):
        """ Get a specified object from the execution dictionary.
        """
        object = dic.get( name ) or dic.get( name.capitalize() )
        if (not isinstance( object, HasFacets )) and callable( object ):
            try:
                object = object()
            except:
                pass

        if isinstance( object, HasFacets ):
            return object

        return None

#-------------------------------------------------------------------------------
#  'DemoPath' class:
#-------------------------------------------------------------------------------

class DemoPath ( DemoTreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # Parent of this package:
    parent = Any

    # Name of file system path to this package:
    path = Property

    # Name of the directory:
    name = Str

    # UI form of the 'name':
    nice_name = Property

    # Description of the contents of the directory:
    description = Property( HTML )

    # Source code contained in the '__init__.py' file:
    source = Property( Code )

    # Dictionary containing symbols defined by the path's '__init__.py' file:
    init_dic = Property

    # Should .py files be included?
    use_files = Bool( True )

    # Paths do allow children:
    allows_children = Bool( True )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Tabbed(
            UItem( 'description',
                   label  = 'Description',
                   style  = 'readonly',
                   editor = HTMLEditor( format_text = True )
            ),
            UItem( 'source',
                   label = 'Source',
                   style = 'custom'
            ),
            dock   = 'tab',
            export = 'DockWindowShell',
            id     = 'tabbed'
        ),
        id = 'facets.ui.demos.demo.path_view'
    )

    #-- Property Implementations -----------------------------------------------

    def _get_path ( self ):
        return join( self.parent.path, self.name )


    def _get_nice_name ( self ):
        return user_name_for( self.name )


    def _get_description ( self ):
        if self._description is None:
            self._get_init()

        return self._description


    def _get_source ( self ):
        if self._source is None:
            self._get_init()

        return self._source


    def _get_init_dic ( self ):
        init_dic = {}
        description, source = parse_source( join( self.path, '__init__.py' ) )
        exec (exec_str + source) in init_dic

        return init_dic

        # fixme: The following code should work, but doesn't, so we use the
        #        preceding code instead. Changing any facet in the object in
        #        this method causes the tree to behave as if the DemoPath object
        #        had been selected instead of a DemoFile object. May be due to
        #        an 'anyfacet' listener in the TreeEditor?
        #if self._init_dic is None:
        #   self._init_dic = {}
        #   #exec self.source in self._init_dic
        #return self._init_dic.copy()

    #-- Public Methods ---------------------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        path = self.path
        for name in listdir( path ):
            cur_path = join( path, name )
            if isdir( cur_path ):
                return True

            if self.use_files:
                name, ext = splitext( name )
                if ( ext == '.py' ) and ( name != '__init__' ):
                    return True

        return False


    def get_children ( self ):
        """ Gets the object's children.
        """
        dirs  = []
        files = []
        path  = self.path
        for name in listdir( path ):
            cur_path = join( path, name )
            if isdir( cur_path ):
                if self.has_py_files( cur_path ):
                    dirs.append( DemoPath( parent = self, name = name ) )

            elif self.use_files:
                name, ext = splitext( name )
                if (ext == '.py') and (name != '__init__'):
                    files.append( DemoFile( parent = self, name = name ) )

        dirs.sort(  lambda l, r: cmp( l.name, r.name ) )
        files.sort( lambda l, r: cmp( l.name, r.name ) )

        return (dirs + files)


    def has_py_files ( self, path ):
        """ Returns whether the specified path contains any .py files.
        """
        for name in listdir( path ):
            cur_path = join( path, name )
            if isdir( cur_path ):
                if self.has_py_files( cur_path ):
                    return True

            else:
                name, ext = splitext( name )
                if ext == '.py':
                    return True

        return False

    #-- Private Methods --------------------------------------------------------

    def _get_init ( self ):
        """ Initializes the description and source from the path's
            '__init__.py' file.
        """
        if self.use_files:
            # Read in the '__init__.py' source file (if any):
            self._description, source = parse_source(
                                              join( self.path, '__init__.py' ) )
        else:
            image_name = join( self.path, 'demo.jpg' ).replace( '\\', '/' )
            self._description = ( '<img src="%s">' % image_name )
            source = ''

        self._source = exec_str + source

#-------------------------------------------------------------------------------
#  Defines the demo tree editor:
#-------------------------------------------------------------------------------

demo_tree_editor = TreeEditor(
    nodes = [
        ObjectTreeNode( node_for = [ DemoPath ],
                        label    = 'nice_name' ),
        ObjectTreeNode( node_for = [ DemoFile ],
                        label    = 'nice_name' )
    ],
    selected = 'selected',
    editable = False
)

#-------------------------------------------------------------------------------
#  'Demo' class:
#-------------------------------------------------------------------------------

class Demo ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # Path to the root demo directory:
    path = Str

    # Root path object for locating demo files:
    root = Instance( DemoPath )

    # Cross reference information for the demo files:
    xref = Instance( SourceXRef )

    # The currently selected demo node:
    selected = Instance( DemoTreeNodeObject )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HSplit(
            VSplit(
                Item( 'root',
                      label  = 'Demos',
                      editor = demo_tree_editor
                ),
                Item( 'xref',
                      label = 'XRef',
                      style = 'custom'
                ),
                show_labels = False
            ),
            UItem( 'selected',
                   id    = 'selected',
                   style = 'custom',
                   dock  = 'fixed'
            ),
            id = 'splitter',
        ),
        title     = 'Facets UI Demo',
        id        = 'facets.extra.demo.demo.Demo',
        dock      = 'tab',
        resizable = True,
        width     = 0.75,
        height    = 0.90
    )

    #-- Facet Default Values ---------------------------------------------------

    def _xref_default ( self ):
        return SourceXRef( root = self.root.path )


    def _selected_default ( self ):
        return self.root

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'xref:selected' )
    def _xref_modified ( self ):
        selected = self.xref.selected
        if isinstance( selected, RefFile ):
            self.selected = self.root.find( selected.file_name )


    def _root_set ( self ):
        """ Handles the 'root' facet being changed.
        """
        self.root.parent = self

#-- Function to run the demo ---------------------------------------------------

def demo ( root = None ):
    """ Runs the demo contained in the specified root directory.
    """
    if root is None:
        root = dirname( abspath( sys.argv[0] ) )

    path, name = split( root )
    Demo( path = path,
          root = DemoPath( name = name, use_files = False )
    ).edit_facets()

#-- Run the Facets UI demo (if invoked from the command line -------------------

if __name__ == '__main__':
    demo( join( dirname( abspath( sys.argv[0] ) ), 'ui' ) )

#-- EOF ------------------------------------------------------------------------