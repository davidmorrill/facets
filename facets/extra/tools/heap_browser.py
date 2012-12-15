"""
A tool for browsing the contents of the Python object heap.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import gc
import weakref

from types \
    import FrameType

from sys \
    import getrefcount

from facets.api \
    import HasPrivateFacets, Str, Int, Any, Button, Property, Instance, List, \
           Float, Color, Event, Callable, cached_property, on_facet_set,      \
           View, VSplit, VGroup, HGroup, Item, Handler, spring, GridEditor,   \
           NotebookEditor, ValueEditor, TreeEditor, TreeNode, HistoryEditor

from facets.ui.grid_adapter \
    import GridAdapter, GridEventHandler

from facets.ui.key_bindings \
    import KeyBindings, KeyBinding

from facets.ui.helper \
    import commatize

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The maximum number of detail items to show for a specific class:
MAX_DETAILS = 16

# The list of types we handle specially:
SequenceTypes = ( list, tuple )

# Classes which should not show up in any of the statistics, since they are
# part of this tool itself:
ignored_classes = set( [
    'facets.extra.tools.heap_browser.HB_ClassCount',
    'facets.extra.tools.heap_browser.HB_Referrer',
    'facets.extra.tools.heap_browser.HB_Referrers',
    'facets.extra.tools.heap_browser.HB_ReferrerHandler',
    'facets.extra.tools.heap_browser.HB_Detail',
    'facets.extra.tools.heap_browser.HB_InstanceDetail',
    'facets.extra.tools.heap_browser.HB_Baseline',
    'facets.extra.tools.heap_browser.HB_BaselineCount',
    'facets.extra.tools.heap_browser.HB_HeapBrowser'
] )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def object_name ( object ):
    """ Returns the 'name' of a specified object (based on its class and module
        name.
    """
    try:
        if isinstance( object, type ):
            return '.<new-style class>'

        return '%s.%s' % ( object.__class__.__module__,
                           object.__class__.__name__ )
    except:
        return '.' + str( type( object ) )


def commatize_column ( adapter ):
    """ Returns the text value of the current numeric column's data formatted
        with commas (e.g. '12,345').
    """
    return commatize( adapter.get_content( adapter.row, adapter.column ) )


def class_name_for ( item ):
    """ Returns the class name for a specified item with a fully-qualified name.
    """
    name = item.name

    return name[ name.rfind( '.' ) + 1: ]


def module_name_for ( item ):
    """ Returns the module name for a specified item with a fully-qualified
        name.
    """
    name = item.name

    return name[ : name.rfind( '.' ) ]


def percent_change_for ( item ):
    """ Returns the percentage change for a specified baseline count item.
    """
    return ((100.0 * (item.baseline_count - item.current_count)) /
             item.baseline_count)


def cmp_class_name ( l, r ):
    """ Defines a sort compatible comparison function for use with pseudo-class
        names.
    """
    return cmp( class_name_for( l ), class_name_for( r ) )


def cmp_module_name ( l, r ):
    """ Defines a sort compatible comparison function for use with pseudo-module
        names.
    """
    return cmp( module_name_for( l ), module_name_for( r ) )


def cmp_change ( l, r ):
    """ Defines a sort compatible comparison function for use with the baseline
        count change column
    """
    return cmp( l.baseline_count - l.current_count,
                r.baseline_count - r.current_count )


def cmp_percent_change ( l, r ):
    """ Defines a sort compatible comparison function for use with pseudo-module
        names.
    """
    return cmp( percent_change_for( l ), percent_change_for( r ) )

#-------------------------------------------------------------------------------
#  Heap browser key bindings:
#-------------------------------------------------------------------------------

heap_browser_key_bindings = KeyBindings(
    KeyBinding( binding     = 'Ctrl-b',
                method      = '_baseline_set',
                description = 'Creates a new baseline set.' ),
    KeyBinding( binding     = 'Ctrl-d',
                method      = '_show_details_set',
                description = 'Shows the instances of the selected heap '
                              'classes.' ),
    KeyBinding( binding     = 'Ctrl-k',
                method      = 'edit_bindings',
                description = 'Edits the keyboard bindings.' ),
    KeyBinding( binding     = 'Ctrl-r',
                method      = '_refresh_set',
                description = 'Refreshes the heap statistics.' ),
    KeyBinding( binding     = 'Ctrl-c',
                method      = '_set_filter_change_1',
                description = 'Sets the filter change value to 1.' ),
    KeyBinding( binding     = 'Ctrl-f',
                method      = '_clear_filter',
                description = 'Resets all filter values back to their '
                              'defaults.' ),
    KeyBinding( binding     = 'Ctrl-a',
                method      = '_select_all',
                description = 'Selects all currently displayed count '
                              'entries.' ),
    KeyBinding( binding     = 'Ctrl-Shift-a',
                method      = '_unselect_all',
                description = 'Unselects all currently selected count '
                              'entries.' ),
    KeyBinding( binding     = 'Ctrl-h',
                method      = '_hide_selected_set',
                description = 'Hides all currently selected count entries.' ),
    KeyBinding( binding     = 'Ctrl-s',
                method      = '_show_selected_set',
                description = 'Shows only the currently selected count '
                              'entries.' ),
    KeyBinding( binding     = 'Ctrl-Shift-s',
                method      = '_show_all_set',
                description = 'Shows all count entries.' )
)

baseline_key_bindings = KeyBindings(
    KeyBinding( binding     = 'Ctrl-i',
                method      = '_show_details_set',
                description = 'Shows the instances of the selected baseline '
                              'classes.' ),
)

detail_key_bindings = KeyBindings(
    KeyBinding( binding     = 'Ctrl-u',
                method      = '_show_referrers_set',
                description = 'Shows the hierarchy of objects that refer to '
                              'the selected instance objects.' )
)

referrers_key_bindings = KeyBindings(
    KeyBinding( binding     = 'Ctrl-v',
                method      = '_view_referrer_set',
                description = 'Shows a view of the selected referrer object.' ),
    KeyBinding( binding     = 'Ctrl-z',
                method      = '_zap_set',
                description = 'Zaps the link from the selected referrer object '
                              'to the referred to object.' )
)

#-------------------------------------------------------------------------------
#  'DetailGridEventHandler' class:
#-------------------------------------------------------------------------------

class DetailGridEventHandler ( GridEventHandler ):
    """ Handles mouse events for a DetailGridAdapter.
    """

    def left_dclick ( self ):
        """ Handles a left double click on the column.
        """
        self.object.owner.referrers.append( HB_Referrers(
            name = self.item.title,
            root = HB_Referrer( ref = weakref.ref( self.item.object ) )
        ) )

#-------------------------------------------------------------------------------
#  'DetailGridAdapter' class:
#-------------------------------------------------------------------------------

class DetailGridAdapter ( GridAdapter ):
    """ Gird adapter for mapping detail data to a GridEditor.
    """

    columns = [
        ( 'Id',                         'object_id'   ),
        ( 'Ref Count',                  'ref_count'   ),
       #( 'Class Name',                 'class_name'  ),
       #( 'Module Name',                'module_name' ),
       #( 'Fully Qualified Class Name', 'name'        ),
    ]

    # Selection colors:
    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    # Event handler:
    handler              = DetailGridEventHandler()

    # Column widths:
    object_id_width      = Float( 0.50 )
    ref_count_width      = Float( 0.50 )
    class_name_width     = Float( 0.25 )
    module_name_width    = Float( 0.45 )
    name_width           = Float( 0.70 )

    # Column alignments:
    object_id_alignment  = Str( 'right' )
    ref_count_alignment  = Str( 'right' )

    # Column text:
    class_name_text      = Property
    module_name_text     = Property

    #-- Property Implementations -----------------------------------------------

    def _get_class_name_text ( self ):
        return class_name_for( self.item )


    def _get_module_name_text ( self ):
        return module_name_for( self.item )


detail_grid_editor = GridEditor(
    adapter        = DetailGridAdapter,
    operations     = [],
    selection_mode = 'rows',
    selected       = 'selected_instances'
)

#-------------------------------------------------------------------------------
#  'BaselineCountGridEventHandler' class:
#-------------------------------------------------------------------------------

class BaselineCountGridEventHandler ( GridEventHandler ):
    """ Handles mouse events for a BaselineCountGridAdapter.
    """

    def left_dclick ( self ):
        """ Handles a left double click on the column.
        """
        self.object.owner.details.append( HB_Detail(
            name       = self.item.name,
            owner      = self.object.owner,
            object_ids = self.object.object_ids
        ) )

#-------------------------------------------------------------------------------
#  'BaselineCountGridAdapter' class:
#-------------------------------------------------------------------------------

class BaselineCountGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping baseline count data to a GridEditor.
    """

    columns = [
        ( 'Class Name',                 'class_name'     ),
        ( 'Module Name',                'module_name'    ),
        ( 'Baseline',                   'baseline_count' ),
        ( 'Current',                    'current_count'  ),
        ( 'Change',                     'change'         ),
        ( '% Change',                   'percent_change' ),
       #( 'Fully Qualified Class Name', 'name' ),
    ]

    # Selection colors:
    selection_bg_color        = Color( 0xFBD391 )
    selection_text_color      = Color( 0x000000 )

    # Event handler:
    handler                   = BaselineCountGridEventHandler()

    # Column widths:
    class_name_width          = Float( 0.24 )
    module_name_width         = Float( 0.40 )
    baseline_count_width      = Float( 0.09 )
    current_count_width       = Float( 0.09 )
    change_width              = Float( 0.09 )
    percent_change_width      = Float( 0.09 )
    name_width                = Float( 0.62 )

    # Column alignments:
    baseline_count_alignment  = Str( 'right' )
    current_count_alignment   = Str( 'right' )
    change_alignment          = Str( 'right' )
    percent_change_alignment  = Str( 'right' )

    # Column formatting:
    percent_change_format     = Str( '%.2f%%' )

    # Column text:
    class_name_text           = Property
    module_name_text          = Property
    baseline_count_text       = Property
    current_count_text        = Property
    change_text               = Property

    # Column color:
    percent_change_bg_color   = Property
    percent_change_text_color = Property

    # Column content:
    percent_change_content    = Property

    # Column sorters:
    class_name_sorter         = Callable( cmp_class_name )
    module_name_sorter        = Callable( cmp_module_name )
    change_sorter             = Callable( cmp_change )
    percent_change_sorter     = Callable( cmp_percent_change )

    #-- Property Implementations -----------------------------------------------

    def _get_class_name_text ( self ):
        return class_name_for( self.item )


    def _get_module_name_text ( self ):
        return module_name_for( self.item )


    def _get_baseline_count_text ( self ):
        return commatize_column( self )


    def _get_current_count_text ( self ):
        return commatize_column( self )


    def _get_change_text ( self ):
        item = self.item

        return commatize( item.baseline_count - item.current_count )


    def _get_percent_change_content ( self ):
        return percent_change_for( self.item )


    def _get_percent_change_bg_color ( self ):
        value = self.get_content( self.row, self.column ) / 100.0

        return ((int( 255 * ( 1.0 - value ) ) * 65536 ) +
                ( int( 255 * value ) * 256))


    def _get_percent_change_text_color ( self ):
        if self.get_content( self.row, self.column ) >= 70.0:
            return 0x000000
        else:
            return 0xFFFFFF


baseline_count_grid_editor = GridEditor(
    adapter        = BaselineCountGridAdapter,
    operations     = [ 'sort' ],
    selection_mode = 'rows',
    selected       = 'selected_items'
)

#-------------------------------------------------------------------------------
#  'CountsGridEventHandler' class:
#-------------------------------------------------------------------------------

class CountsGridEventHandler ( GridEventHandler ):
    """ Handles mouse events for a CountsGridAdapter.
    """

    def left_dclick ( self ):
        """ Handles a left double click on the column.
        """
        self.object.details.append(
            HB_Detail( name = self.item.name, owner = self.object )
        )

#-------------------------------------------------------------------------------
#  'CountsGridAdapter' class:
#-------------------------------------------------------------------------------

class CountsGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping counts data to a GridEditor.
    """

    columns = [
        ( 'Class Name',                 'class_name'  ),
        ( 'Module Name',                'module_name' ),
        ( '# Instances',                'instances'   ),
        ( 'Change',                     'change'      ),
       #( 'Fully Qualified Class Name', 'name' ),
    ]

    # Selection colors:
    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    # Event handler:
    handler              = CountsGridEventHandler()

    # Column widths:
    class_name_width     = Float( 0.25 )
    module_name_width    = Float( 0.45 )
    instances_width      = Float( 0.15 )
    change_width         = Float( 0.15 )
    name_width           = Float( 0.70 )

    # Column alignments:
    instances_alignment  = Str( 'right' )
    change_alignment     = Str( 'right' )

    # Column text:
    class_name_text      = Property
    module_name_text     = Property
    instances_text       = Property
    change_text          = Property

    # Column sorters:
    class_name_sorter    = Callable( cmp_class_name )
    module_name_sorter   = Callable( cmp_module_name )

    #-- Property Implementations -----------------------------------------------

    def _get_class_name_text ( self ):
        return class_name_for( self.item )


    def _get_module_name_text ( self ):
        return module_name_for( self.item )


    def _get_instances_text ( self ):
        return commatize_column( self )


    def _get_change_text ( self ):
        return commatize_column( self )


counts_grid_editor = GridEditor(
    adapter        = CountsGridAdapter,
    operations     = [ 'sort' ],
    selection_mode = 'rows',
    selected       = 'selected_counts'
)

#-------------------------------------------------------------------------------
#  'HB_ClassCount' class:
#-------------------------------------------------------------------------------

class HB_ClassCount ( HasPrivateFacets ):
    """ Information about a single class of heap instances.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The class name:
    name = Str

    # The lower case version of the name:
    lower_name = Property

    # The number of active instances:
    instances = Int

    # The net change in active instances since the last refresh:
    change = Int

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_lower_name ( self ):
        return self.name.lower()

#---------------------------------------------------------------------------
#  'HB_InstanceDetail' class:
#---------------------------------------------------------------------------

class HB_InstanceDetail ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # A weak reference to the heap object:
    ref = Any

    # The actual object:
    object = Property

    # The name of the object class:
    name = Property

    # The title for this object:
    title = Property

    # The object id for the object:
    object_id = Property

    # The reference count for the object:
    ref_count = Property

    #-- Property Implementations -----------------------------------------------

    def _get_object ( self ):
        return self.ref()


    @cached_property
    def _get_name ( self ):
        return object_name( self.object )


    @cached_property
    def _get_object_id ( self ):
        return '%08X' % id( self.object )


    @cached_property
    def _get_title ( self ):
        name = self.name
        return '%s(%s)' % ( name[ name.rfind( '.' ) + 1: ], self.object_id )


    def _get_ref_count ( self ):
        return ( getrefcount( self.object ) - 1 )

#-------------------------------------------------------------------------------
#  'HB_ReferrerHandler' class:
#-------------------------------------------------------------------------------

class HB_ReferrerHandler ( Handler ):

    #-- Public Methods ---------------------------------------------------------

    def init ( self, info ):
        info.ui.title = info.object.name

        return True

#-------------------------------------------------------------------------------
#  'HB_Referrer' class:
#-------------------------------------------------------------------------------

class HB_Referrer ( HasPrivateFacets ):
    """ Describes the set of objects which refer to a specific object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # A weak reference to the heap object being described:
    ref = Any

    # The actual object:
    object = Property

    # The name of this item:
    name = Property

    # The facet name this object referred to its referent by:
    facet_name = Str

    # The objects that refer to this object:
    referrers = Property( depends_on = 'update' )

    # Event fired when the list of referrers should be updated:
    update = Event

    # The name space for all objects in this referrer graph:
    name_space = Any( {} )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'object',
              show_label = False,
              editor     = ValueEditor()
        ),
        id        = 'facets.extra.tools.heap_browser.HB_Referrer',
        width     = 0.20,
        height    = 0.25,
        resizable = True,
        handler   = HB_ReferrerHandler
    )

    #-- Property Implementations -----------------------------------------------

    def _get_object ( self ):
        return self.ref()


    @cached_property
    def _get_name ( self ):
        object     = self.object
        name       = object_name( object )
        instances  = self.name_space.setdefault( name, {} )
        n          = instances.setdefault( id( object ), len( instances ) + 1 )
        facet_name = self.facet_name
        if facet_name != '':
            facet_name = '.' + facet_name

        return '%s:%s%s[%s]' % ( name, n, facet_name,
                                 getrefcount( object ) - 2 )
        #return '%s:%s%s[%s]' % ( name[ name.rfind( '.' ) + 1: ], n, facet_name,
        #                         getrefcount( object ) - 2 )


    @cached_property
    def _get_referrers ( self ):
        instance = self.object
        if isinstance( instance, FrameType ):
            return []

        referrers  = []
        dicts      = set()
        seqs       = set()
        name_space = self.name_space
        for object in gc.get_referrers( instance ):
            try:
                referrers.append( HB_Referrer(
                    ref        = weakref.ref( object, self._instance_gone ),
                    name_space = name_space ) )
            except:
                if isinstance( object, dict ):
                    dicts.add( id( object ) )
                elif isinstance( object, SequenceTypes ):
                    seqs.add( id( object ) )
                else:
                    referrers.append( HB_Referrer(
                        ref        = lambda object = object: object,
                        name_space = name_space ) )

        len_dicts = len( dicts )
        len_seqs  = len( seqs )
        if (len_dicts > 0) or (len_seqs > 0):
            for object in gc.get_objects():
                try:
                    object_dict = object.__dict__
                    if ( len_dicts > 0 ) and ( id( object_dict ) in dicts ):
                        referrers.extend( [
                            HB_Referrer(
                                ref = weakref.ref( object, self._instance_gone ),
                                facet_name = name,
                                name_space = name_space )
                            for name, value in object_dict.iteritems()
                            if instance is value ] )

                    elif len_seqs > 0:
                        isect = seqs.intersect( [ id( value )
                                        for value in object_dict.itervalues() ] )
                        seqs.difference_update( isect )
                        for seq in isect:
                            seqs.remove( seq )
                            for name, value in object_dict.iteritems():
                                if seq == id( value ):
                                    referrers.append( HB_Referrer(
                                        ref = weakref.ref( object,
                                                       self._instance_gone ),
                                        facet_name = name,
                                        name_space = name_space ) )

                                    break
                except:
                    pass

        return referrers

    #-- Private Methods --------------------------------------------------------

    def _instance_gone ( self, ref ):
        """ Handles the instance an HB_Referrer object refers to being garbage
            collected.
        """
        self.update = True

#-------------------------------------------------------------------------------
#  Tree editor definitions:
#-------------------------------------------------------------------------------

tree_editor = TreeEditor(
    nodes = [
        TreeNode( node_for  = [ HB_Referrer ],
                  auto_open = False,
                  children  = 'referrers',
                  label     = 'name'
        )
    ],
    editable = False,
    selected = 'selected'
 )

#-------------------------------------------------------------------------------
#  'HB_Referrers' class:
#-------------------------------------------------------------------------------

class HB_Referrers ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of this object:
    name = Str

    # The root of the referrers tree:
    root = Instance( HB_Referrer )

    # The currently selected referrer item:
    selected = Instance( HB_Referrer )

    # View the currently selected referrer:
    view_referrer = Button( 'View' )

    # Zap the link that the referrer has to the target:
    zap = Button( 'Zap' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            Item( 'root',
                  show_label = False,
                  editor     = tree_editor
            ),
            HGroup(
                spring,
                Item( 'view_referrer',
                      tooltip = 'View the contents of this object in a pop-up '
                                'window',
                      enabled_when = 'selected is not None' ),
                Item( 'zap',
                      tooltip = 'Break the link this object holds to the '
                                'referred to object',
                      enabled_when = 'selected is not None' ),
                show_labels = False,
            )
        ),
        resizable    = True,
        key_bindings = referrers_key_bindings
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _view_referrer_set ( self, info = None ):
        """ Handles the 'View' button being clicked.
        """
        if self.selected is not None:
            self.selected.edit_facets()


    def _zap_set ( self, info = None ):
        """ Handles the 'Zap' button being clicked.
        """
        referrer = self.selected
        if referrer is not None:
            object   = referrer.object
            name     = referrer.facet_name
            if name == '':
                try:
                    object_dict = object.__dict__
                    for name in object_dict.keys():
                        if ( name[ : 2 ] != '__' ) or ( name[ -2: ] != '__' ):
                            del object_dict[ name ]
                    print 'zapped object dictionary'
                except:
                    print 'could not zap entire object dictionary.'
            else:
                value = getattr( object, name )
                try:
                    if isinstance( value, list ):
                        del value[ : ]
                        print 'zapped list'
                    elif isinstance( value, dict ):
                        value.clear()
                        print 'zapped dictionary'
                    else:
                        setattr( object, name, None )
                        print 'zapped instance'
                except:
                    try:
                        del object.__dict__[ name ]
                        print 'zapped object dictionary name'
                    except:
                        print 'Could not zap name'

#-------------------------------------------------------------------------------
#  'HB_Detail' class:
#-------------------------------------------------------------------------------

class HB_Detail ( HasPrivateFacets ):
    """ Information about a single heap class.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the class:
    short_name = Property

    # The fully qualified name of the class:
    name = Str

    # Optional dictionary of object ids the objects must come from:
    object_ids = Any # None or a dictionary with object ids as keys

    # Event fired when the instances should be updated:
    update = Event

    # Reference to each active instance of the class:
    instances = List( HB_InstanceDetail )

    # The currently selected instances:
    selected_instances = List( HB_InstanceDetail )

    # Show all current referrers button:
    show_referrers = Button( 'Referrers' )

    # The main tool object:
    owner = Instance( 'HB_HeapBrowser' )

    # Event fired when a 'instances' item is double-clicked:
    instances_dclick = Event

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            Item( 'instances',
                  id         = 'instances',
                  show_label = False,
                  editor     = detail_grid_editor,
            ),
            '_',
            HGroup(
                spring,
                Item( 'show_referrers',
                      tooltip = 'Show all objects that refer to the selected '
                                'objects',
                      enabled_when = 'len( selected_instances ) > 0' ),
                show_labels = False
            )
        ),
        id           = 'facets.extra.tools.heap_browser.HB_Detail',
        resizable    = True,
        key_bindings = detail_key_bindings
    )

    #-- Property Implementations -----------------------------------------------

    def _get_short_name ( self ):
        name = self.name

        return name[ name.rfind( '.' ) + 1: ]

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'name, update' )
    def _name_modified ( self ):
        """ Rebuilds the list of instances when an update occurs.
        """
        name       = self.name
        object_ids = self.object_ids
        instances  = [ ]
        for object in gc.get_objects():
            if ((name == object_name( object )) and
                ((object_ids is None) or (id( object ) in object_ids))):
                instances.append( HB_InstanceDetail(
                    ref = weakref.ref( object, self._instance_gone ) ) )

                if len( instances ) >= MAX_DETAILS:
                    break

        self.instances = instances


    def _show_referrers_set ( self, info = None ):
        """ Handles the 'Show Referrers' button being clicked.
        """
        self.owner.referrers.extend( [
            HB_Referrers(
                name = instance.title,
                root = HB_Referrer( ref = weakref.ref( instance.object ) ) )
            for instance in self.selected_instances
        ] )


    def _instances_dclick_set ( self, event ):
        """ Handles the user double-clicking an instance item in order to show
            its referrers.
        """
        instance, column = event
        self.owner.referrers.append( HB_Referrers(
            name = instance.title,
            root = HB_Referrer( ref = weakref.ref( instance.object ) ) ) )

    #-- Private Methods --------------------------------------------------------

    def _instance_gone ( self, ref ):
        """ Handles the instance an HB_InstanceDetail object refers to being
            garbage collected.
        """
        for item in self.instances:
            if ref is item.ref:
                if item in self.selected_instances:
                    self.selected_instances.remove( item )

                self.instances.remove( item )

                break

#-------------------------------------------------------------------------------
#  'HB_BaselineCount' class:
#-------------------------------------------------------------------------------

class HB_BaselineCount ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The fully-qualified class name:
    name = Str

    # The original baseline object count:
    baseline_count = Int

    # The current object count:
    current_count = Int

#-------------------------------------------------------------------------------
#  'HB_Baseline' class:
#-------------------------------------------------------------------------------

class HB_Baseline ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The owner of this view object:
    owner = Instance( 'HB_HeapBrowser' )

    # The current set of objects in the baseline set:
    object_ids = Any # ( { id(object): class_name } )

    # The list of baseline object classes/counts:
    items = List( HB_BaselineCount )

    # The current list of filtered_items:
    filtered_items = List( HB_BaselineCount )

    # The list of currently selected items:
    selected_items = List( HB_BaselineCount )

    # The name filter value:
    filter_name = Str

    # The minimum current objects filter value:
    filter_current = Int

    # The event fired when the heap statistics have been updated:
    update = Event # set( id( object ) )

    # Event fired after the heap statistics have been re-analyzed:
    update_done = Event

    # The number of baseline classes:
    classes = Property( depends_on = 'filtered_items' )

    # The total number of baseline objects:
    baseline_total = Property( depends_on = 'filtered_items' )

    # The total number of baseline objects still remaining:
    current_total = Property( depends_on = 'filtered_items, update_done' )

    # Show the instance details for the currently selected classes:
    show_details = Button( 'Show Details' )

    # Event fired when a filtered item is double-clicked:
    filtered_items_dclick = Event

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'show_details',
                      show_label   = False,
                      enabled_when = 'len( self.selected_items ) > 0'
                ),
                '_',
                Item( 'filter_name',
                      label = 'Name',
                      width = -80
                ),
                Item( 'filter_current',
                      label = 'Min Current',
                      width = -40
                ),
                '_',
                spring,
                '_',
                Item( 'classes',
                      style = 'readonly',
                      width = -30 ),
                '_',
                Item( 'baseline_total',
                      label = '# Baseline',
                      style = 'readonly',
                      width = -50 ),
                '_',
                Item( 'current_total',
                      label = '# Remaining',
                      style = 'readonly',
                      width = -50 ),
            ),
            Item( 'filtered_items',
                  show_label = False,
                  editor     = baseline_count_grid_editor
            )
        ),
        resizable    = True,
        key_bindings = baseline_key_bindings
    )

    #-- Property Implementations -----------------------------------------------

    def _get_classes ( self ):
        return len( self.filtered_items )


    def _get_baseline_total ( self ):
        return reduce( lambda l, r: l + r.baseline_count,
                       self.filtered_items, 0 )


    def _get_current_total ( self ):
        return reduce( lambda l, r: l + r.current_count,
                       self.filtered_items, 0 )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'filter_name, filter_current, items, update_done' )
    def _filter_values_modified ( self ):
        """ Handles one of the filter values changing.
        """
        name    = self.filter_name.lower()
        current = self.filter_current
        self.filtered_items = items = [
            item for item in self.items
                 if ((item.name.lower().find( name ) >= 0) and
                     (item.current_count >= current))
        ]
        self.selected_items = [ item for item in self.selected_items
                                     if item in items ]


    def _object_ids_set ( self, object_ids ):
        """ Handles the dictionary of object ids being set.
        """
        items = {}
        for object_id, name in object_ids.iteritems():
            item = items.get( name )
            if item is None:
                items[ name ] = item = HB_BaselineCount( name = name )

            item.baseline_count    += 1
            item.current_count     += 1
            object_ids[ object_id ] = item

        items = items.values()
        items.sort( lambda l, r: cmp( l.baseline_count, r.baseline_count ) )
        self.items = items


    def _update_set ( self, new_ids ):
        """ Handles a heap update.
        """
        object_ids = self.object_ids
        for object_id in object_ids.keys():
            if object_id not in new_ids:
                object_ids[ object_id ].current_count -= 1
                del object_ids[ object_id ]

        # fixme: This is a hack to get the GridEditor to re-sort the data (if
        # sorting is in effect) by appearing to cause a change to the data list:
        if len( self.filtered_items ) > 1:
            self.filtered_items[0] = self.filtered_items[0]

        self.update_done = True


    def _show_details_set ( self, info = None ):
        """ Handles the 'Show Details' button being clicked.
        """
        owner      = self.owner
        object_ids = self.object_ids
        owner.details.extend( [ HB_Detail( name       = item.name,
                                           owner      = owner,
                                           object_ids = object_ids )
                                for item in self.selected_items ] )


    def _filtered_items_dclick_set ( self, event ):
        """ Handles the user double-clicking a filtered items value to show its
            details.
        """
        item, column = event
        self.owner.details.append( HB_Detail( name       = item.name,
                                              owner      = self.owner,
                                              object_ids = self.object_ids ) )

#-------------------------------------------------------------------------------
#  'HB_HeapBrowser' class:
#-------------------------------------------------------------------------------

class HB_HeapBrowser ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Heap Browser' )

    # The current heap statistics table entries:
    current_counts = List( HB_ClassCount )

    # The list of currently selected counts:
    selected_counts = List( HB_ClassCount )

    # The sting that all class names must contain:
    filter_name = Str( event = 'heap_updated' )

    # The threshold for the number of instances to display:
    filter_instances = Int( event = 'heap_updated' )

    # The threshold for the amount of change to display:
    filter_change = Int( event = 'heap_updated' )

    # Number of items in the current_counts list:
    current_classes = Property( depends_on = 'current_counts' )

    # Total number of instances in the current_counts list:
    current_instances = Property( depends_on = 'current_counts' )

    # Total change in the current_counts list:
    current_change = Property( depends_on = 'current_counts' )

    # Indicates whether or not the selection set is empty or not:
    has_counts = Property

    # The set of all current active object ids:
    current_ids = Any( set() )

    # Current heap statistics:
    current_heap = Any( {} )

    # Previous heap statistics:
    previous_heap = Any( {} )

    # Event fired when anything changes that affects the heap statistics view:
    heap_updated = Event

    # The list of object classes currently being ignored:
    ignored_classes = Any( set() )

    # The list of object classes currently being shown:
    shown_classes = Any( set() )

    # Refresh button:
    refresh = Button( 'Refresh' )

    # Baseline button (to create a new 'baseline' set):
    baseline = Button( 'Baseline' )

    # Hide all selected items button:
    hide_selected = Button( 'Hide Selected' )

    # Show only the selected items button:
    show_selected = Button( 'Show Selected' )

    # Show all items button:
    show_all = Button( 'Show All' )

    # Show the details of the current selected items button:
    show_details = Button( 'Show Details' )

    # Event fired when a 'counts' item is double-clicked:
    counts_dclick = Event

    #-- View 2 Facets ----------------------------------------------------------

    # The list of objects which the user has requested detailed information for:
    details = List( HB_Detail )

    #-- View 3 Facets ----------------------------------------------------------

    # The list of object referrer trees:
    referrers = List( HB_Referrers )

    #-- View 4 Facets ----------------------------------------------------------

    # The list of object baselines:
    baselines = List( HB_Baseline )

    #-- Facets View Definitions ------------------------------------------------

    heap_stats_view = View(
        VSplit(
            VGroup(
                HGroup(
                    Item( 'filter_name',
                          id     = 'filter_name',
                          label  = 'Name',
                          width  = -90,
                          editor = HistoryEditor( auto_set = True ),
                    ),
                    '_',
                    Item( 'filter_instances',
                          label = 'Min Instances',
                          width = -36
                    ),
                    '_',
                    Item( 'filter_change',
                          label = 'Min Change',
                          width = -36
                    ),
                    '_',
                    spring,
                    '_',
                    Item( 'current_classes',
                          label       = 'Classes',
                          style       = 'readonly',
                          format_func = commatize,
                          width       = -35
                    ),
                    '_',
                    Item( 'current_instances',
                          label       = 'Instances',
                          style       = 'readonly',
                          format_func = commatize,
                          width       = -50
                    ),
                    '_',
                    Item( 'current_change',
                          label       = 'Change',
                          style       = 'readonly',
                          format_func = commatize,
                          width       = -50
                    ),
                ),
                Item( 'current_counts',
                      id     = 'current_counts',
                      editor = counts_grid_editor
                ),
                '_',
                HGroup(
                    Item( 'refresh',
                          tooltip = 'Refresh the heap statistics' ),
                    Item( 'baseline',
                          tooltip = 'Create a new baseline set' ),
                    spring,
                    Item( 'hide_selected',
                          tooltip = 'Remove all selected items from the view',
                          enabled_when = 'has_counts' ),
                    Item( 'show_selected',
                          tooltip = 'Show only the selected items in the view',
                          enabled_when = 'has_counts' ),
                    Item( 'show_all',
                          tooltip = 'Show all items again',
                          enabled_when = '(len( ignored_classes ) > 0) '
                                      'or (len( shown_classes ) > 0)' ),
                    '_',
                    Item( 'show_details',
                          tooltip = 'Show the instances of the selected '
                                    'classes',
                          enabled_when = 'has_counts' ),
                    show_labels = False,
                ),
                label       = 'Heap',
                show_labels = False,
                dock        = 'tab'
            ),
            Item( 'details',
                  id     = 'details',
                  style  = 'custom',
                  dock   = 'tab',
                  editor = NotebookEditor( deletable  = True,
                                           dock_style = 'auto',
                                           export     = 'DockWindowShell',
                                           page_name  = '.short_name' )
            ),
            Item( 'referrers',
                  id     = 'referrers',
                  style  = 'custom',
                  dock   = 'tab',
                  editor = NotebookEditor( deletable  = True,
                                           dock_style = 'auto',
                                           export     = 'DockWindowShell',
                                           page_name  = '.name' )
            ),
            Item( 'baselines',
                  id     = 'baselines',
                  style  = 'custom',
                  dock   = 'tab',
                  editor = NotebookEditor( deletable  = True,
                                           dock_style = 'auto',
                                           export     = 'DockWindowShell',
                                           page_name  = 'Baseline' )
            ),
            id          = 'splitter',
            show_labels = False
        ),
        title        = 'Heap Browser',
        id           = 'facets.extra.tools.heap_browser.HB_HeapBrowser',
        width        = 0.5,
        height       = 0.75,
        resizable    = True,
        key_bindings = heap_browser_key_bindings
    )

    #-- Property Implementations -----------------------------------------------

    def _get_has_counts ( self ):
        return ( len( self.selected_counts ) > 0 )


    def _get_current_classes ( self ):
        return len( self.current_counts )


    @cached_property
    def _get_current_instances ( self ):
        return reduce( lambda l, r: l + r.instances, self.current_counts, 0 )


    @cached_property
    def _get_current_change ( self ):
        return reduce( lambda l, r: l + r.change, self.current_counts, 0 )

    #-- Facet Event Handlers ---------------------------------------------------

    def _heap_updated_set ( self ):
        """ Handles the 'heap_updated' event being fired by rebuilding the
            heap class counts list.
        """
        ignored = ignored_classes
        shown   = self.shown_classes
        no_show = (len( shown ) == 0)
        if no_show:
            ignored = ignored_classes.union( self.ignored_classes )

        old              = self.previous_heap
        filter_name      = self.filter_name.lower()
        filter_instances = self.filter_instances
        filter_change    = self.filter_change
        counts = [ HB_ClassCount( name      = name,
                                  instances = instances,
                                  change    = instances - old.get( name, 0 ) )
                   for name, instances in self.current_heap.iteritems()
                   if (name not in ignored)                   and
                      (no_show or (name in shown))            and
                      (name.lower().find( filter_name ) >= 0) and
                      (instances >= filter_instances)         and
                      (abs( instances - old.get( name, 0 ) ) >= filter_change)
        ]
        counts.sort( lambda l, r: cmp( l.lower_name, r.lower_name ) )
        self.current_counts = counts


    def _refresh_set ( self, info = None ):
        """ Handles the 'Refresh' button being clicked.
        """
        self.update()


    def _baseline_set ( self, info = None ):
        """ Handles the 'Baseline' button being clicked.
        """
        self.baselines.append( self._create_baseline() )


    def _hide_selected_set ( self, info = None ):
        """ Handles the 'Hide Selected' button being clicked.
        """
        self.ignored_classes.update(
            set( [ item.name for item in self.selected_counts ] )
        )
        self.shown_classes.clear()
        del self.selected_counts[ : ]
        self.heap_updated = True


    def _show_selected_set ( self, info = None ):
        """ Handles the 'Show Selected' button being clicked.
        """
        self.shown_classes = set(
            set( [ item.name for item in self.selected_counts ] )
        )
        self.ignored_classes.clear()
        del self.selected_counts[ : ]
        self.heap_updated = True


    def _show_all_set ( self, info = None ):
        """ Handles the 'Show All' button being clicked.
        """
        self.ignored_classes.clear()
        self.shown_classes.clear()
        del self.selected_counts[ : ]
        self.heap_updated = True


    def _show_details_set ( self, info = None ):
        """ Handles the 'Show Details' button being clicked.
        """
        self.details.extend( [ HB_Detail( name = item.name, owner = self )
                               for item in self.selected_counts ] )


    def _counts_dclick_set ( self, event ):
        """ Handles the user double-clicking a 'counts' table entry in order
            to show its details.
        """
        item, column = event
        self.details.append( HB_Detail( name = item.name, owner = self ) )


    def _set_filter_change_1 ( self, info = None ):
        """ Sets the filter change value to 1.
        """
        self.filter_change = 1


    def _clear_filter ( self, info = None ):
        """ Clears all current filter variable settings back to their defaults.
        """
        self.filter_change = filter_instances = 0
        self.filter_name   = ''


    def _select_all ( self, info = None ):
        """ Selects all current displayed items.
        """
        self.selected_counts = self.current_counts


    def _unselect_all ( self, info = None ):
        """ Unselects all currently selected items.
        """
        self.selected_counts = [ ]

    #-- Public Methods ---------------------------------------------------------

    def update ( self ):
        """ Updates the heap statistics.
        """
        self.previous_heap = old = self.current_heap
        self.current_heap  = new = {}
        self.current_ids   = ids = set()

        gc.collect()

        for object in gc.get_objects():
            name = object_name( object )
            if name not in ignored_classes:
                new[ name ] = new.setdefault( name, 0 ) + 1
                ids.add( id( object ) )

        self.heap_updated = True

        # Indicate that each class detail should update its instance
        # information:
        for detail in self.details:
            detail.update = True

        # Indicate that each referrer should update its instance information:
        for referrer in self.referrers:
            referrer.root.update = True

        # Indicate that each baseline view should update its contents:
        for baseline in self.baselines:
            baseline.update = ids

    #-- Private Methods --------------------------------------------------------

    def _create_baseline ( self ):
        """ Creates a new baseline object.
        """
        current_ids = self.current_ids
        object_ids  = {}

        gc.collect()

        for object in gc.get_objects():
            if id( object ) not in current_ids:
                name = object_name( object )
                if name not in ignored_classes:
                    object_ids[ id( object ) ] = name

        return HB_Baseline( object_ids = object_ids, owner = self )

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    hb = HB_HeapBrowser()
    hb.update()
    hb.edit_facets()

#-- EOF ------------------------------------------------------------------------