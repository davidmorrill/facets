"""
Defines the ObjectSource tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from os.path \
    import join, exists, basename

from facets.api \
    import HasFacets, HasPrivateFacets, Any, Instance, List, Property, File, \
           Directory, Str, View, Item, NotebookEditor, TreeEditor

from facets.ui.value_tree \
    import FacetsNode

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.tools.class_browser \
    import CBModuleFile, cb_tree_nodes

from facets.extra.api \
    import HasPayload, FilePosition

from facets.extra.helper.themes \
    import TTitle

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ObjectDebugger' class:
#-------------------------------------------------------------------------------

class ObjectDebugger ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The object that created this view:
    object_source = Any

    # The path of the file being debugged:
    file_name = File

    # The Python path the file was found in:
    python_path = Directory

    # The name to use on the debugger page:
    name = Property

    # The object being debugged:
    object = Any

    # The module descriptor for the file:
    module = Instance( CBModuleFile )

    # The currently selected object class:
    selected = Any

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'module',
              id         = 'browser',
              show_label = False,
              editor     = TreeEditor( nodes    = cb_tree_nodes,
                                       editable = False,
                                       selected = 'selected' ),
              resizable  = True
        ),
        id        = 'facets.extra.tools.object_source.ObjectDebugger',
        resizable = True
    )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, **facets ):
        """ Initializes the object.
        """
        super( ObjectDebugger, self ).__init__( **facets )
        self.module = CBModuleFile( path        = self.file_name,
                                    python_path = self.python_path,
                                    object      = self.object )
        do_later( self.select_object )


    def select_object ( self ):
        """ Selects the class of the current object in the class browser.
        """
        name = self.object.__class__.__name__
        for cb_class in self.module.get_children():
            if name == cb_class.name:
                self.selected = cb_class
                break

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, selected ):
        """ Handles a tree node being selected.
        """
        # Read the object's text to force it to calculate the starting
        # line number of number of lines in the text fragment:
        ignore = selected.text

        # Set the file position for the object:
        self.object_source.file_position = FilePosition(
                                           name      = selected.name,
                                           file_name = selected.path,
                                           line      = selected.line_number + 1,
                                           lines     = selected.lines,
                                           object    = self.object )

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        return basename( self.file_name )

#-------------------------------------------------------------------------------
#  'ObjectSource' class:
#-------------------------------------------------------------------------------

class ObjectSource ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Object Source' )

    # The current item being inspected:
    item = Instance( HasFacets,
                     droppable = 'Drop an object with facets here.',
                     connect   = 'both: object with facets' )

    # Description of the current object being inspected:
    description = Str( 'Drag an object to the circular image above to view '
                       'its source' )

    # The currently selected file position:
    file_position = Instance( FilePosition,
                        draggable = 'Drag currently selected file position.',
                        connect   = 'from: file position' )

    # Current list of items being inspected:
    inspectors = List

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        TTitle( 'description' ),
        Item( 'inspectors@',
              show_label = False,
              editor     = NotebookEditor( deletable  = True,
                                           page_name  = '.name',
                                           export     = 'DockWindowShell',
                                           dock_style = 'auto' )
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def inspector_for ( self, module, object ):
        """ Returns the inspector object for a specified class (if possible).
        """
        for path in sys.path:
            file_name = join( path, module + '.py' )
            if exists( file_name ):
                if file_name in self._file_names:
                    break

                return ObjectDebugger( object_source = self,
                                       file_name     = file_name,
                                       python_path   = path,
                                       object        = object )

        return None

    #-- Facet Event Handlers ---------------------------------------------------

    def _item_set ( self, item ):
        """ Handles the 'item' facet being changed.
        """
        if isinstance( item, HasPayload ):
            item = item.payload

        if isinstance( item, FacetsNode ):
            item = item.value

        if item is not None:
            inspectors       = []
            self._file_names = []
            description      = ''
            for klass in item.__class__.__mro__:
                module = klass.__module__.split( '.' )
                module_name = module[ -1 ]
                if module_name != '__builtin__':
                    module_name += '.py'

                if len( description ) > 0:
                    description += ' -> '

                description += '%s[%s]' % ( klass.__name__, module_name )
                inspector = self.inspector_for( join( * module ), item )
                if inspector is not None:
                    inspectors.append( inspector )
                    self._file_names.append( inspector.file_name )

            self.inspectors  = inspectors
            self.description = description
            do_later( self.set, item = None )

#-- EOF ------------------------------------------------------------------------