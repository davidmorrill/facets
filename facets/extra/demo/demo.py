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

from glob \
    import glob

from facets.api \
    import HasFacets, HasPrivateFacets, DelegatesTo, Str, Instance, Any, Bool, \
           List, Code, Button, HTML, Image, Theme, TreeEditor, ObjectTreeNode, \
           Property, TreeNodeObject, View, Item, UItem, HSplit, VSplit,        \
           Tabbed, VGroup, HGroup, Heading, Handler, UIInfo, InstanceEditor,   \
           ImageEditor, HTMLEditor, SlideshowEditor, Include, spring,          \
           on_facet_set, inn

from facets.core.facet_base \
    import file_with_ext

from facets.extra.helper.source_xref \
    import SourceXRef, RefFile

from facets.extra.tools.text_file \
    import TextFile

from facets.extra.markdown.markdown \
    import MarkdownEditor

from facets.ui.pyface.timer.api \
    import do_later

#-------------------------------------------------------------------------------
#  Global data:
#-------------------------------------------------------------------------------

# Define the code used to populate the 'execfile' dictionary:
exec_str =  """from facets.core_api \
    import *

"""

# The background theme used by DemoPath instances:
background_theme = Theme( '@tiles:TexturedCeiling1.jpg?s10', content = 25 )

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


    def closed ( self, info, is_ok ):
        """ Closes the view.
        """
        object = info.object
        inn( object.demo, 'dispose' )()
        del object.demo


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

    # The parent of this object:
    parent = Any

    # The name of the file system path to this object:
    path = Str

    # The name of the object:
    name = Str

    # The UI form of the 'name':
    nice_name = Str

    # The owner of this object:
    owner = Property

    # A description of the object:
    description = Str

    # The editor used to display the description:
    description_editor = Any # HTMLEditor or MarkdownEditor

    # Cached result of 'tno_has_children':
    _has_children = Any

    # Cached result of 'tno_get_children':
    _get_children = Any

    #-- Facet Default Values ---------------------------------------------------

    def _description_editor_default ( self ):
        if self.description.lstrip().startswith( '#' ):
            return MarkdownEditor()

        return HTMLEditor( format_text = True )

    #-- Property Implementations -----------------------------------------------

    def _get_owner ( self ):
        parent = self.parent
        if isinstance( parent, Demo ):
            return parent

        return parent.owner

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

    # Files don't allow children:
    allows_children = Bool( False )

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

    def facets_view ( self ):
        # Force the 'demo' object to be initialized:
        self.demo

        return View(
            Tabbed(
                UItem( 'demo',
                       style     = 'custom',
                       label     = 'Demo',
                       resizable = True
                ),
                UItem( 'description',
                       label  = 'Description',
                       style  = 'readonly',
                       editor = self.description_editor
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


    def _path_default ( self ):
        return join( self.parent.path, self.name + '.py' )


    def _nice_name_default ( self ):
        return user_name_for( self.name )


    def _demo_default ( self ):
        handles = sys.stdout, sys.stderr
        try:
            sys.stdout = sys.stderr = self

            # Read in the demo source file:
            path = self.path
            self.description, self.source = parse_source( path )

            # Try to run the demo source file:
            locals = self.parent.init_dic.copy()
            locals[ '__name__' ] = '___main___'
            sys.modules[ '__main__' ].__file__ = path
            try:
                execfile( path, locals, locals )

                return self.demo_for( locals )
            except Exception, excp:
                return DemoError( msg = str( excp ) )
        finally:
            sys.stdout, sys.stderr = handles

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

    #-- Handles 'print' Output -------------------------------------------------

    def write ( self, text ):
        self.log += text


    def flush ( self ):
        pass

#-------------------------------------------------------------------------------
#  'DemoPath' class:
#-------------------------------------------------------------------------------

class DemoPath ( DemoTreeNodeObject ):

    #-- Facet Definitions ------------------------------------------------------

    # Description of the contents of the directory:
    description = HTML

    # Source code contained in the '__init__.py' file:
    source = Code

    # Dictionary containing symbols defined by the path's '__init__.py' file:
    init_dic = Any

    # Should .py files be included?
    use_files = Bool( True )

    # Paths do allow children:
    allows_children = Bool( True )

    # An image to display:
    image = Image

    # The images to make a slide show from:
    images = List

    # The demo image currently selected by the user:
    selected = Any

    #-- Facet View Definitions -------------------------------------------------

    def facets_view ( self ):
        global background_theme

        self._init_description()
        if self.use_files:
            id    = 'facets.ui.demos.demo.path_view'
            items = [
                UItem( 'description',
                       label  = 'Description',
                       style  = 'readonly',
                       editor = self.description_editor
                ),
                UItem( 'source',
                       label = 'Source',
                       style = 'custom'
                )
            ]
            if len( self.images ) > 0:
                id += '_ss'
                items.insert( 0,
                    UItem( 'images',
                           editor = SlideshowEditor(
                               selected         = 'selected',
                               theme            = background_theme,
                               transitions      = 'down, left, up, right',
                               transition_order = 'shuffle',
                               image_order      = 'shuffle'
                           )
                    )
                )

            return View(
                Tabbed( *items,
                    dock   = 'tab',
                    export = 'DockWindowShell',
                    id     = 'tabbed'
                ),
                id = id
            )

        return View(
            UItem( 'image',
                   editor = ImageEditor( theme = background_theme )
            )
        )

    #-- Facet Default Values ---------------------------------------------------

    def _path_default ( self ):
        return join( self.parent.path, self.name )


    def _nice_name_default ( self ):
        return user_name_for( self.name )


    def _init_dic_default ( self ):
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

    def _init_description ( self ):
        """ Initializes the description or image for the directory.
        """
        if self.use_files:
            # Read in the '__init__.py' source file (if any):
            self.description, source = parse_source(
                join( self.path, '__init__.py' )
            )
            self.source = exec_str + source
            self.images = glob( join( self.path, '*.png' ) )
        else:
            self.image = join( self.path, 'demo.png' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self ):
        """ Handles the 'selected' facet being changed.
        """
        do_later(
            self.owner.set,
            selected = self.find( file_with_ext( self.selected.name, 'py' ) )
        )

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

#-- Function to create and optionally run the demo -----------------------------

def demo ( root = None, run = True ):
    """ Creates a Demo object corresponding to the demo contained in the
        specified *root* directory. If *root* is not specified, it uses the path
        to the 'facets.extra.demo.ui' user interface demo. If *run* is True, it
        immediately launches the resulting demo UI.

        Returns the Demo object for the specified demo.
    """
    if root is None:
        root = dirname( abspath( sys.argv[0] ) )

    path, name = split( root )
    demo       = Demo(
        path = path,
        root = DemoPath( name = name, use_files = False )
    )
    if run:
        demo.edit_facets()

    return demo

#-- Run the Facets UI demo (if invoked from the command line -------------------

if __name__ == '__main__':
    demo( join( dirname( abspath( sys.argv[0] ) ), 'ui' ) )

#-- EOF ------------------------------------------------------------------------