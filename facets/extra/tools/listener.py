"""
Defines the Listener tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import basename, splitext

from facets.api \
    import HasPrivateFacets, Any, Instance, List, Property, Str, Color, View, \
           Item, GridEditor

from facets.core.facet_base \
    import read_file

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.api \
    import FilePosition, FacetValue

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ListenerItem' class:
#-------------------------------------------------------------------------------

class ListenerItem ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The facet notifier associated with this item:
    notifier = Any

    # The class name of the notifier object:
    class_name = Property

    # The notifier object:
    object = Property

    # The object id of the notifier object:
    object_id = Property

    # Module name of the notifier:
    module_name = Property

    # Method/Function name of the notifier:
    method_name = Property

    # Line number of the notifier:
    line = Property

    # Source file name of the notifier:
    file_name = Property

    # Source line of the notifier:
    source = Property

    # The notifier handler:
    handler = Property

    #-- Property Implementations -----------------------------------------------

    def _get_class_name ( self ):
        if self._class_name is None:
            self._class_name = ''
            if hasattr( self.notifier, 'object' ):
                self._class_name = self.notifier.object().__class__.__name__

        return self._class_name


    def _get_object ( self ):
        if hasattr( self.notifier, 'object' ):
            return self.notifier.object()

        return None


    def _get_object_id ( self ):
        if self._object_id is None:
            self._object_id = ''
            if hasattr( self.notifier, 'object' ):
                self._object_id = '0x%08X' % id( self.notifier.object() )

        return self._object_id


    def _get_module_name ( self ):
        if self._module_name is None:
            self._module_name = splitext( basename( self.file_name ) )[0]

        return self._module_name


    def _get_method_name ( self ):
        if self._method_name is None:
            self._method_name = self.handler.__name__

        return self._method_name


    def _get_line ( self ):
        if self._line is None:
            handler = self.handler
            if hasattr( handler, 'im_func' ):
                handler = handler.im_func
            self._line = handler.func_code.co_firstlineno

        return self._line


    def _get_file_name ( self ):
        if self._file_name is None:
            handler = self.handler
            if hasattr( handler, 'im_func' ):
                handler = handler.im_func
            self._file_name = handler.func_code.co_filename

        return self._file_name


    def _get_source ( self ):
        if self._source is None:
            self._source = ''
            source       = read_file( self.file_name )
            if source is not None:
                try:
                    self._source = source.split( '\n' )[ self.line - 1 ].strip()
                except:
                    pass

        return self._source


    def _get_handler ( self ):
        notifier = self.notifier
        if hasattr( notifier, 'object' ):
            return getattr( notifier.object(), notifier.name )

        return notifier.handler

#-------------------------------------------------------------------------------
#  'ListenerGridAdapter' class:
#-------------------------------------------------------------------------------

class ListenerGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping listener tool data to a GridEditor.
    """

    columns = [ ( 'Class Name',  'class_name'  ),
                ( 'Object Id',   'object_id'   ),
                ( 'Module Name', 'module_name' ),
                ( 'Method Name', 'method_name' ),
                ( 'Line',        'line'        ),
                ( 'File Name',   'file_name'   ),
                ( 'Source',      'source'      ) ]

    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    object_id_alignment  = Str( 'center' )
    line_alignment       = Str( 'center' )


listener_grid_editor = GridEditor(
    adapter    = ListenerGridAdapter,
    operations = [],
    selected   = 'selected'
)

#-------------------------------------------------------------------------------
#  'Listener' class:
#-------------------------------------------------------------------------------

class Listener ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Listener' )

    # The receiver of the facet whose listeners are to be displayed:
    facet_value = FacetValue(
                      droppable = 'Drop a facet here to display its listeners',
                      connect   = 'to: facet' )

    # The currently selected entry's file position:
    file_position = Instance( FilePosition,
                              draggable = 'Drag this file position.',
                              connect   = 'from: file position' )

    # The currently selected entry's object:
    object = Property( draggable = 'Drag this object.' )

    # The list of listener items for the current facet being inspected:
    items = List( ListenerItem )

    # The currently selected listener item:
    selected = Instance( ListenerItem )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'items',
              id         = 'items',
              show_label = False,
              editor     = listener_grid_editor
        ),
        id = 'facets.extra.tools.listener'
    )

    #-- Property Implementations -----------------------------------------------

    def _get_object ( self ):
        if self.selected is not None:
            return self.selected.object

        return None

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        self.file_position = FilePosition( file_name = selected.file_name,
                                           name      = selected.method_name,
                                           line      = selected.line )


    def _facet_value_set ( self, facet_value ):
        """ Handles the 'facet_value' facet being changed.
        """
        object, name = facet_value
        notifiers    = object._notifiers( 1 )[:]
        notifiers.extend( object._facet( name, 2 )._notifiers( 1 ) )
        self.items = [ ListenerItem( notifier = notifier )
                       for notifier in notifiers ]

#-- EOF ------------------------------------------------------------------------