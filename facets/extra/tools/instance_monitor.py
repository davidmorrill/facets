"""
Defines the InstanceTracker and InstanceMonitor classes which together monitor
and display information about the instances of HasFacets subclasses.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from weakref \
    import ref

from gc \
    import get_referrers, collect

from collections \
    import Counter

from types \
    import MethodType

from facets.api \
    import HasFacets, Instance, Any, Bool, Int, Str, List, Constant, Color,  \
           Image, UIView, View, VGroup, HGroup, VSplit, Tabbed, Item, UItem, \
           GridEditor, ImageZoomEditor, FacetListObject, FacetDictObject, spring

from facets.ui.adapters.graphics \
    import Graphics

from facets.ui.adapters.ui_event \
    import UIEvent

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Facet collection classes:
FacetCollections = ( FacetListObject, FacetDictObject )

# Maximum number of history items:
HistoryItems = 10

# Classes which are ignored for global counts (because they are heavily used by
# the UI view):
IgnoredClasses = ( Graphics, UIEvent )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def monotonic ( values ):
    """ Returns the length of the maximum run of monotonically increasing values
        in the specified list of *values*.
    """
    n = len( values ) - 1
    for i in xrange( n, 0, -1 ):
        if values[ i ] <= values[ i - 1 ]:
            return (n - i)

    return (n + 1)

#-------------------------------------------------------------------------------
#  'InstanceTracker' class:
#-------------------------------------------------------------------------------

class InstanceTracker ( HasFacets ):
    """ Tracks various counts about the number of instances of HasFacets
        subclasses.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The total number of HasFacets instances ever created:
    total_count = Int

    # The total count of all currently live instances:
    count = Int

    # Mapping from id(HasFacets subclass) to a list of the form:
    # [ class_name, total_created, maximum_live, current_live ]:
    counts = Any( {} )

    # Mapping from weak references to live instances to their class:
    instances = Any( {} )

    # Is the instance counter active (True) or not (False)?
    active = Bool( False )

    #-- Facet Event Handlers ---------------------------------------------------

    def _active_set ( self, active ):
        """ Handles the 'active' facet being changed.
        """
        HasFacets.facet_monitor( self._increment, not active )

    #-- Private Methods --------------------------------------------------------

    def _increment ( self, object ):
        """ Increments the count for a HasFacets class when a new instance is
            created.
        """
        klass    = object.__class__
        id_class = id( klass )
        self.instances[ ref( object, self._decrement ) ] = id_class
        counts = self.counts.get( id_class )
        if counts is None:
            self.counts[ id_class ] = counts = [
                klass.__name__,
                (-1 if issubclass( klass, IgnoredClasses ) else 0), 0, 0
            ]

        if counts[1] >= 0:
            counts[1]        += 1
            self.total_count += 1

        self.count += 1
        counts[3]  += 1
        counts[2]   = max( counts[2], counts[3] )


    def _decrement ( self, ref ):
        """ Decrements the count for a HasFacets class when an instance is
            garbage collected.
        """
        self.count -= 1
        self.counts[ self.instances.pop( ref ) ][3] -= 1

#-------------------------------------------------------------------------------
#  'ReferrerAdapter' class:
#-------------------------------------------------------------------------------

class ReferrerAdapter ( GridAdapter ):
    """ Adapts InstanceView 'referrers' tuples for display using a GridEditor.
    """

    columns = [ ( 'Class', 'class'  ), ( 'Count', 'count'  ) ]

    class_sorter    = Constant( lambda l, r: cmp( l[0], r[0] ) )
    count_sorter    = Constant( lambda l, r: cmp( l[1], r[1] ) )
    count_alignment = Constant( 'right' )

    def class_text ( self ): return self.item[0]
    def count_text ( self ): return str( self.item[1] )

#-------------------------------------------------------------------------------
#  'MonitorAdapter' class:
#-------------------------------------------------------------------------------

class MonitorAdapter ( GridAdapter ):
    """ Adapts InstanceView 'counts' tuples for display using a GridEditor.
    """

    columns = [
        ( 'Class', 'class'   ),
        ( 'Total', 'total'   ),
        ( 'Max',   'maximum' ),
        ( 'Count', 'count'   ),
        ( 'Plot',  'plot'    )
    ]

    class_sorter    = Constant( lambda l, r: cmp( l[1], r[1] ) )
    total_sorter    = Constant( lambda l, r: cmp( l[2], r[2] ) )
    maximum_sorter  = Constant( lambda l, r: cmp( l[3], r[3] ) )
    count_sorter    = Constant( lambda l, r: cmp( l[4], r[4] ) )
    plot_sorter     = Constant( lambda l, r: cmp( monotonic( l[6] ),
                                                  monotonic( r[6] ) ) )

    def class_text   ( self ): return self.item[1]
    def total_text   ( self ): return str( self.item[2] )
    def maximum_text ( self ): return str( self.item[3] )
    def count_text   ( self ): return str( self.item[4] )

    def count_bg_color ( self ):
        count = self.item[4]
        total = self.item[2]
        if ((count > 4) and (total > 0) and (self.item[6][-4] >= 0) and
            ((float( count ) / total) > 0.8)):
            return 0xFF8080

        return 0xFFFFFF

    total_alignment   = Constant( 'right' )
    maximum_alignment = Constant( 'right' )
    count_alignment   = Constant( 'right' )

    plot_text_color          = Color( 0x4976B0 )
    plot_selected_text_color = Color( 0x4976B0 )

    def plot_content ( self ): return self.item[6]
    def plot_paint   ( self ): return self.plot_cell

    def plot_cell ( self, cell ):
        """ Paints the grid cell for the specified cell.
        """
        g            = cell.graphics
        g.anti_alias = True
        g.pen        = None
        x, y, dx, dy = g.clipping_bounds

        if cell.paint_background:
            g.brush = cell.state_bg_color
            g.draw_rectangle( x, y, dx, dy )

        values = cell.content
        n      = len( values )
        if n > 0:
            g.brush = cell.state_text_color
            x      += 1
            yb      = y + dy
            dy     -= 1
            vdx     = float( dx - 1 ) / n
            vdy     = float( max( values ) )
            if vdy == 0.0:
                vdy = 1.0

            for value in values:
                if value > 0:
                    dyv = int( round( (value / vdy) * dy ) )
                    x0  = int( round( x ) )
                    g.draw_rectangle(
                        x0, yb - dyv, int( round( x + vdx - x0 ) ) - 1, dyv
                    )

                x += vdx

    def bg_color ( self ):
        return (0xFFFFFF if self.item[5] == 0 else 0xE0E0E0)

#-------------------------------------------------------------------------------
#  'InstanceMonitor' class:
#-------------------------------------------------------------------------------

class InstanceMonitor ( UIView ):
    """ Presents a grid view of data collected from an InstanceTracker.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Instance Monitor' )

    # The InstanceTracker used to track live HasFacets instances:
    monitor = Instance( InstanceTracker, () )

    # The total count of all instamces ever created:
    total_count = Int

    # The total count of all currently live instances:
    count = Int

    # A list of tuples of the form ( id(class), class_name, total, max, count,
    # change, history = [count0, count1,...,countn] ):
    counts = List

    # The currently selected list tuple:
    selected = Any

    # Identifies the last selected info used to calculate the referrers list:
    last_selected_info = Any

    # Dictionary mapping previous cycle's classes to counts:
    last_counts = Any( {} )

    # A list of tuples of the form: ( class, count ) which count the number of
    # referrers to the currently selected item by class type:
    referrers = List

    #-- Graph Related Facets ---------------------------------------------------

    # The list of items waiting to be processed. Items are of the form:
    # ( object_ref, level, target_node_name ):
    to_do = Any( [] )

    # Mapping from id(object.__dict__) -> object_class_name:
    sources = Any( {} )

    # Shortcut mapping from source_class_name:target_class_name -> attr_name
    # used to speed up trying to match a source.attr is target reference:
    links = Any( {} )

    # Mapping from reference_name -> [ count, type ] used to build the list of
    # graph nodes:
    nodes = Any( {} )

    # Mapping from (reference_name->target_name) -> count used to build the list
    # of graph edges:
    edges = Any( {} )

    # The image containing the current referrer's graph:
    graph = Image( cache = False )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'total_count',
                      label = 'Total',
                      style = 'readonly',
                      width = -50
                ),
                '_',
                Item( 'count',
                      label = 'Live',
                      style = 'readonly',
                      width = -50
                ),
                '_',
                spring,
                group_theme = '#themes:toolbar_group'
            ),
            VSplit(
                UItem( 'counts',
                       id     = 'counts',
                       editor = GridEditor( adapter    = MonitorAdapter,
                                            row_height = 25,
                                            operations = [ 'sort' ],
                                            selected   = 'selected' )
                ),
                Tabbed(
                    UItem( 'referrers',
                           id     = 'referrers',
                           editor = GridEditor( adapter    = ReferrerAdapter,
                                                operations = [ 'sort' ] )
                    ),
                    UItem( 'graph',
                           editor = ImageZoomEditor()
                    )
                ),
                id = 'splitter'
            )
        ),
        title     = 'Instance Monitor',
        id        = 'facets.extra.help.instance_monitor.InstanceMonitor',
        width     = 0.5,
        height    = 0.75,
        resizable = True
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _ui_info_set ( self, ui_info ):
        """ Handles 'the 'UIInfo' facet being changed.
        """
        self.monitor.active = (ui_info is not None)
        if ui_info is not None:
            do_after( 1000, self._update )


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if selected is not None:
            id_class = selected[0]
            info     = ( id_class, selected[2] )
            if info != self.last_selected_info:
                self.last_selected_info = info
                self._update_referrers( id_class )
        else:
            self.last_selected_info = None

    #-- Private Methods --------------------------------------------------------

    def _dict_ref_for ( self, dict, object, class_name ):
        for name, value in dict.iteritems():
            if value is object:
                return '%s.%s' % ( class_name, name )

        return class_name


    def _update ( self ):
        """ Updates the current set of active instance counts.
        """
        # Force a garbage collection:
        collect()

        selected         = self.selected
        selected_class   = None if selected is None else selected[0]
        last_counts      = self.last_counts
        monitor          = self.monitor
        self.total_count = monitor.total_count
        self.count       = monitor.count
        items            = []
        for id_class, counts in monitor.counts.iteritems():
            count   = counts[3]
            history = last_counts.get( id_class )
            if history is None:
                last_counts[ id_class ] = history = [ -1 ] * HistoryItems

            change = count - history[-1]
            if change != 0:
                history.append( count )
                if len( history ) > HistoryItems:
                    del history[0]

            items.append(
                ( id_class, counts[0], counts[1], counts[2], count, change,
                  history )
            )
            if id_class == selected_class:
                selected = items[-1]

        self.counts   = items
        self.selected = selected

        if self.ui_info is not None:
            do_after( 1000, self._update )


    def _update_referrers ( self, id_class ):
        """ Updates the referrer classes and counts for the class whose
            id(class) is specified by *id_class*.
        """
        sources = {}
        objects = []
        mcounts = self.monitor.counts
        for object_ref, object_class in self.monitor.instances.iteritems():
            object                           = object_ref()
            sources[ id( object.__dict__ ) ] = mcounts[ object_class ][0]
            if object_class == id_class:
                objects.append( object_ref )

        counts = Counter()
        for i in xrange( len( objects ) ):
            for referrer in get_referrers( objects[ i ]() ):
                name = referrer.__class__.__name__
                if isinstance( referrer, FacetCollections ):
                    name = '%s.%s%s' % (
                        referrer.object().__class__.__name__,
                        referrer.name,
                        '[]' if isinstance( referrer, FacetListObject )
                        else '{}'
                    )
                elif isinstance( referrer, MethodType ):
                    name = '%s.%s()' % (
                        referrer.im_self.__class__.__name__,
                        referrer.im_func.func_name
                    )
                elif isinstance( referrer, dict ):
                    item   = sources.get( id( referrer ) )
                    object = objects[ i ]()
                    if item is not None:
                        name = self._dict_ref_for( referrer, object,
                                                   item )
                    else:
                        owners = [
                            owner for owner in get_referrers( referrer )
                            if getattr( owner, '__dict__', None ) is
                               referrer
                        ]
                        if len( owners ) == 1:
                            name = self._dict_ref_for( referrer, object,
                                          owners[0].__class__.__name__ )

                counts.update( [ name ] )

        self.referrers = [
            ( name, count ) for name, count in counts.iteritems()
        ]

        #self._build_graph( mcounts[ id_class ][0], objects, sources )


    def _build_graph ( self, target, objects, sources ):
        """ Creates an image representing the current graph of referrers to the
            currently selected object class.
        """
        self.to_do = to_do = [ ( object_ref, 0, target )
                               for object_ref in objects ]
        self.nodes[ target ] = [ len( objects ), 'object' ]
        while len( to_do ) > 0:
            object_ref, level, target = to_do[0]
            del to_do[0]
            level += 1
            refs   = [ object for object in get_referrers( object_ref() ) ]
            object = None
            for i in xrange( len( refs ) ):
                self._process_reference(
                    refs[ i ], object_ref, level, target
                )

        self._create_graph()

        del self.to_do[:]
        self.sources.clear()
        self.links.clear()
        self.nodes.clear()
        self.edges.clear()


    def _process_reference ( self, reference, object_ref, level, target ):
        """ Process a reference to *object_ref* by *referrer*. The logical name
            for *object_ref* is specified by *target* and the level of reference
            is given by *level*. Both *referrer* and *object_ref* are weak
            references.
        """
        name = reference.__class__.__name__
        kind = 'object'
        if isinstance( reference, FacetCollections ):
            is_list = isinstance( reference, FacetListObject )
            kind    = 'list' if is_list else 'dict'
            name    = '%s.%s%s' % (
                reference.object().__class__.__name__,
                reference.name, '[]' if is_list else '{}'
            )
        elif isinstance( reference, MethodType ):
            kind = 'method'
            name = '%s.%s()' % (
                reference.im_self.__class__.__name__,
                reference.im_func.func_name
            )
        elif isinstance( reference, dict ):
            item   = self.sources.get( id( reference ) )
            object = object_ref()
            if item is not None:
                name = self._dict_ref_for( reference, object, item )
                kind = 'attribute' if name.find( '.' ) >= 0 else 'object'
            else:
                owners = [
                    owner for owner in get_referrers( reference )
                    if getattr( owner, '__dict__', None ) is reference
                ]
                if len( owners ) == 1:
                    name = self._dict_ref_for( reference, object,
                                  owners[0].__class__.__name__ )
                    kind = 'attribute' if name.find( '.' ) >= 0 else 'object'

        info = self.nodes.get( name )
        if info is None:
            self.nodes[ name ] = info = [ 0, kind ]

        info[0] += 1
        edge     = '%s:%s' % ( name, target )
        self.edges[ edge ] = self.edges.get( edge, 0 ) + 1

        if level < 2:
            try:
                self.to_do.append( ( ref( reference ), level, name ) )
            except:
                print 'failed on:', type(reference)


    def _create_graph ( self ):
        """ Creates the referrer graph based on the accumulated analysis
            information.
        """
        nodes = dict( [ ( node, i )
                        for i, node in enumerate( self.nodes.iterkeys() ) ] )
        edges = []
        for edge in self.edges.iterkeys():
            n1, n2 = edge.split( ':', 1 )
            edges.append( 'node_%d -> node_%d;' % ( nodes[ n1 ], nodes[ n2 ] ) )

        nodes = [ 'node_%d [label="%s"];' % ( i, node )
                  for node, i in nodes.iteritems() ]
        graph = (
            'digraph G {\n    graph [bgcolor="#D8D8D8"];\n'
            '    node [fontname="Helvetica-Bold",style=filled,fillcolor="#FFFDA9"];\n'
            '    %s\n    %s\n}' % (
            '\n    '.join( nodes ), '\n    '.join( edges ) ))

        print graph
        print ('-' * 70)

#-- EOF ------------------------------------------------------------------------
