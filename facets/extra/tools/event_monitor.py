"""
A feature-enabled tool for monitoring Facets notification events.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from time \
    import time

from facets.core.cfacets \
    import _facet_notification_handler

from facets.api \
    import HasPrivateFacets, Str, Int, Long, WeakRef, List, Range, Bool,      \
           Float, Any, Constant, Color, Property, Instance, Callable, Enum,   \
           View, HToolbar, VGroup, Item, Handler, GridEditor, on_facet_set

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.helper.themes \
    import Scrubber

#-------------------------------------------------------------------------------
#  'EventGridAdapter' class:
#-------------------------------------------------------------------------------

class EventGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping event tool data into a GridEditor.
    """

    columns = [
        ( 'Object Id',  'id'         ),
        ( 'Class Name', 'class_name' ),
        ( 'Name',       'name'       ),
        ( 'Old',        'old'        ),
        ( 'New',        'new'        ),
        ( 'Depth',      'depth'      ),
        ( 'Timestamp',  'timestamp'  ),
    ]

    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    # Column widths:
    class_name_width     = Float( 0.15 )
    id_width             = Float( 0.15 )
    name_width           = Float( 0.15 )
    old_width            = Float( 0.175 )
    new_width            = Float( 0.175 )
    depth_width          = Float( 0.05 )
    timestamp_width      = Float( 0.15 )

    # Column formatting:
    id_format            = Str( '%016X' )
    timestamp_format     = Str( '%.3f' )

    # Column alignment:
    depth_alignment      = Str( 'center' )
    timestamp_alignment  = Str( 'right' )

    # Text value:
    old_text             = Property
    new_text             = Property

    # Cell background color:
    depth_bg_color       = Property

    #-- Property Implementations -----------------------------------------------

    def _get_old_text ( self ):
        return str( self.get_content( self.row, self.column
                   ) ).replace( '\n', '\\n' ).replace( '\r', '\\r' )

    def _get_new_text ( self ):
        return self._get_old_text()


    def _get_depth_bg_color ( self ):
        depth = self.get_content( self.row, self.column )
        if depth == 0:
            return None

        return self.color_for( ( min( 255, int( 63.75 * ( depth - 1 ) ) ),
                                 max(   0, int( 63.75 * ( 5 - depth ) ) ),
                                 0 ) )


event_grid_editor = GridEditor(
    adapter    = EventGridAdapter,
    operations = [],
    selected   = 'selected'
)

#-------------------------------------------------------------------------------
#  'NotificationEvent' class:
#-------------------------------------------------------------------------------

class NotificationEvent ( HasPrivateFacets ):
    """ Represents a Facets notification event.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the receiving object's class:
    class_name = Str

    # The id of the receiving object:
    id = Long

    # A weak reference to the receiving object:
    object = WeakRef

    # The name of the facet that generated the notification:
    name = Str

    # The old value sent with the notification:
    old = Any

    # The new value sent with the notification:
    new = Any

    # The time stamp of when the event notification was generated:
    timestamp = Float

    # The recursion depth of the event handler:
    depth = Int

#-------------------------------------------------------------------------------
#  'EventMonitor' class:
#-------------------------------------------------------------------------------

class EventMonitor ( Handler ):
    """ A feature-enabled tool for monitoring Facets notification events.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Event Monitor' )

    # The persistence id for this object:
    id = Str( 'facets.extra.tools.event_monitor.state', save_state_id = True )

    # The list of recent events:
    events = List( NotificationEvent )

    # The currently selected event:
    selected = Instance( NotificationEvent )

    # The maximum number of events to keep:
    max_events = Range( 1, 100000, 30, save_state = True )

    # Total number of events logged:
    total_events = Int

    # Is event monitoring enabled?
    enabled = Bool( False )

    # The type of monitoring being performed:
    monitor = Enum( 'All', 'Selected class', 'Selected object' )

    # Text form of currently monitor item:
    monitor_text = Str

    # The current monitor check being performed:
    monitor_check = Callable

    # The previous Facet notification handler:
    previous_handler = Any

    # The time base used to define time 0:
    time_base = Constant( time() )

    # The current recursion depth of the event monitor:
    depth = Int

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HToolbar(
                Item( 'enabled' ),
                Scrubber( 'max_events', 'Maximum number of events to monitor',
                          label = 'Maximum events',
                          width = 50
                ),
                Item( 'monitor' ),
                Item( 'monitor_text',
                      label   = '=',
                      style   = 'readonly',
                      width   = 100,
                      springy = True
                ),
                #'_',
                Item( 'total_events',
                      style = 'readonly',
                      width = -50
                ),
                id = 'toolbar'
            ),
            Item( 'events',
                  id         = 'events',
                  show_label = False,
                  editor     = event_grid_editor
            )
        ),
        id        = 'facets.extra.tools.event_monitor.EventMonitor',
        title     = 'Facets Notification Event Monitor',
        width     = 0.5,
        height    = 0.5,
        resizable = True
    )

    #-- Handler Class Method Overrides -----------------------------------------

    def closed ( self, info, is_ok ):
        """ Handles a dialog-based user interface being closed by the user.
        """
        # Make sure the notification handler has been removed:
        self.enabled = False

    #-- Facets Default Values --------------------------------------------------

    def _monitor_check_default ( self ):
        return lambda obj: True

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self, enabled ):
        """ Handles the monitoring state being changed.
        """
        if enabled:
            self.previous_handler = _facet_notification_handler(
                                        self._handle_event )
        else:
            _facet_notification_handler( self.previous_handler )


    @on_facet_set( 'selected, monitor' )
    def _set_monitor ( self ):
        """ Sets up the type of monitoring to be performed.
        """
        selected = self.selected
        if (self.monitor == 'All') or (selected is None):
            self.monitor_text  = ''
            self.monitor_check = self._monitor_check_default()

        elif self.monitor == 'Selected class':
            self.monitor_text  = class_name = selected.class_name
            self.monitor_check = \
                lambda obj: obj.__class__.__name__ == class_name

        else:
            obj_id             = selected.id
            self.monitor_text  = '%s(%016X)' % ( selected.class_name, obj_id )
            self.monitor_check = lambda obj: id( obj ) == obj_id

    #-- Private Methods -------------------------------------------------------

    def _handle_event ( self, handler, args ):
        """ Handles a facets notification event being generated.
        """
        if (not self._ignore_event) and (args is not self._last_args):
            object, name, old, new, notify = args
            if ((not isinstance( object, IgnoreClasses )) and
                self.monitor_check( object )):
                self._ignore_event = True
                self._last_args    = args
                events = self.events
                events.append( NotificationEvent(
                    class_name = object.__class__.__name__,
                    id         = id( object ),
                    object     = object,
                    name       = name,
                    old        = old,
                    new        = new,
                    timestamp  = time() - self.time_base,
                    depth      = self.depth ) )

                delta = (len( events ) - self.max_events)
                if delta > 0:
                    del events[ : delta ]

                self.total_events += 1
                self._ignore_event = False

        self.depth += 1

        try:
            handler( *args )
        finally:
            self.depth -= 1

# The event classes that should be ignored:
IgnoreClasses = ( NotificationEvent, EventMonitor, EventGridAdapter )

#-- Run as a stand-alone program (if invoked from the command line) ------------

if __name__ == '__main__':
    EventMonitor().edit_facets()

#-- EOF ------------------------------------------------------------------------