"""
Defines a tool for creating and managing data watch points, which allow a
developer to be notified when changes occur to any of the objects being
monitored.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, SingletonHasPrivateFacets, Str, Constant, Instance, \
           List, Color, Button, Property, View, HGroup, Item, TextEditor, \
           EnumEditor, GridEditor, property_depends_on

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.helper.fbi \
    import FBI

from facets.extra.helper.wiretap \
    import FBIWiretap

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'DataWatch' class:
#-------------------------------------------------------------------------------

class DataWatch ( Tool ):

    #-- Public Facet Definitions -----------------------------------------------

    # The name of the tool:
    name = Str( 'DataWatch' )

    # Reference to the FBI debugging context:
    fbi = Constant( FBI() )

    # Expression used to evaluate and define 'object':
    expression = Str

    # Object being watched:
    object = Instance( HasFacets )

    # Facet being watched ('Any' == 'all facets'):
    facet = Str( 'Any' )

    # List of facets that can be watched:
    facets = List( Str, [ 'Any' ] )

    # Optional condition that must be true before watch triggers:
    condition = Str

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            HGroup(
                Item( 'expression{Object}',
                      editor = TextEditor( evaluate = self.eval_in_frame ) ),
                Item( 'facet',
                      editor = EnumEditor( name = 'facets' ) ),
                Item( 'condition' )
            ),
            title   = 'Create Data Watch',
            kind    = 'livemodal',
            buttons = [ 'OK', 'Cancel' ]
        )

    #-- Public Methods ---------------------------------------------------------

    def _expression_set ( self, expr ):
        """ Handles the 'expression' facet being changed.
        """
        try:
            self.object = eval( expr, globals(), self.fbi.frame.variable )
        except:
            pass

    #-- Facet Event Handlers ---------------------------------------------------

    def _object_set ( self, value ):
        """ Handles the 'object' facet being changed.
        """
        names = value.facet_names()
        names.sort()
        self.facets = ( [ 'Any' ] + names )

    #-- Private Methods --------------------------------------------------------

    def eval_in_frame ( self, value ):
        """ Evaluates an expression in the context of the current debugger stack
            frame.
        """
        try:
            if isinstance( eval( value, globals(), self.fbi.frame.variable ),
                           HasFacets ):
                return value
        except:
            pass

        return 0

#-------------------------------------------------------------------------------
#  'DataWatchGridAdapter' class:
#-------------------------------------------------------------------------------

class DataWatchGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping DataWatch objects to a GridEditor.
    """

    columns = [
        ( 'Object',    'object'    ),
        ( 'Facet',     'facet'     ),
        ( 'Condition', 'condition' ),
    ]

    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    facet_alignment      = Str( 'center' )


data_watch_grid_editor = GridEditor(
    adapter    = DataWatchGridAdapter,
    operations = [ 'delete', 'sort' ],
    selected   = 'selected'
)

#-------------------------------------------------------------------------------
#  'DataWatches' class:
#-------------------------------------------------------------------------------

class DataWatches ( SingletonHasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # Reference to the FBI wiretap manager:
    fbi_wiretap = Constant( FBIWiretap() )

    # List of currently active data watches:
    data_watches = List( DataWatch )

    # The currently selected data watch:
    selected = Instance( DataWatch )

    # The current data watch available for editing:
    data_watch = Instance( DataWatch, { 'expression': 'self' } )

    # Is the current data_watch being edited in a valid state?
    is_valid = Property

    # Add current data watch being edited button:
    add = Button( 'Add' )

    # Delete the currently selected data watch button:
    delete = Button( 'Delete' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'data_watches',
              show_label = False,
              editor     = data_watch_grid_editor
        ),
        HGroup(
            spring,
            Item( 'add',
                  enabled_when = 'is_valid'
            ),
            Item( 'delete',
                  enabled_when = 'selected is not None'
            ),
            show_labels = False
        ),
        Item( 'data_watch',
              show_label = False,
              style      = 'custom'
        )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'data_watch:object' )
    def _get_is_valid ( self ):
        return (self.data_watch.object is not None)

    #-- Facet Event Handlers ---------------------------------------------------

    def _add_set ( self ):
        """ Handles the 'Add' button being clicked.
        """
        self.data_watches.append( self.data_watch )
        self.data_watch = DataWatch( expression = 'self' )


    def _delete_set ( self ):
        """ Handles the 'Delete' button being clicked.
        """
        self.data_watches.remove( self.selected )


    def _data_watches_items_set ( self, event ):
        """ Handles a DataWatch item being added or deleted.
        """
        for dw in event.added:
            if dw.object is not None:
                facet = dw.facet
                if facet == 'Any':
                    facet = None
                self.fbi_wiretap.wiretap( ( dw.object, facet, dw.condition ),
                                          False )

        for dw in event.removed:
            if dw.object is not None:
                facet = dw.facet
                if facet == 'Any':
                    facet = None
                self.fbi_wiretap.wiretap( ( dw.object, facet, dw.condition ),
                                          True )

#-- EOF ------------------------------------------------------------------------