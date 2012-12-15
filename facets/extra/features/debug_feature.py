"""
Adds a 'debug' feature to DockWindow which exposes the object associated with a
DockControl as a draggable item. This can be used to facilitate debugging when
used in conjunction with other plugins such as 'object source' and 'universal
inspector'.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Enum, Property, DelegatesTo, View, \
           Item, ValueEditor, implements

from facets.ui.menu \
    import Menu, Action

from facets.ui.dock.api \
    import DockControl, DockWindowFeature, IDockUIProvider

from facets.extra.api \
    import HasPayload

from facets.ui.pyface.timer.api \
    import do_later

from facets.ui.ui_facets \
    import image_for

#-------------------------------------------------------------------------------
#  Context menu definition:
#-------------------------------------------------------------------------------

object_action = Action(
    name   = 'Object',
    action = "self.set(mode='object')",
    style  = 'toggle'
)

dock_control_action = Action(
    name   = 'DockControl',
    action = "self.set(mode='dock_control')",
    style  = 'toggle'
)

control_action = Action(
    name   = 'Control',
    action = "self.set(mode='control')",
    style  = 'toggle'
)

ui_action = Action(
    name   = 'Facets UI',
    action = "self.set(mode='ui')",
    style  = 'toggle'
)

context_menu = Menu(
    object_action,
    dock_control_action,
    control_action,
    ui_action,
    name = 'popup'
)

#-------------------------------------------------------------------------------
#  Images:
#-------------------------------------------------------------------------------

feature_images = {
    'object':       image_for( '@facets:debug_object_feature' ),
    'dock_control': image_for( '@facets:debug_dock_control_feature' ),
    'control':      image_for( '@facets:debug_control_feature' ),
    'ui':           image_for( '@facets:debug_ui_feature' )
}

#-------------------------------------------------------------------------------
#  'DebugFeature' class:
#-------------------------------------------------------------------------------

class DebugFeature ( DockWindowFeature ):

    #-- Class Constants --------------------------------------------------------

    # The user interface name of the feature:
    feature_name = 'Debug'

    # Current feature state (0 = uninstalled, 1 = active, 2 = disabled):
    state = 2

    #-- Facet Definitions ------------------------------------------------------

    # The 'payload' mode:
    mode = Enum( 'object', 'dock_control', 'control', 'ui' )

    # The current payload value:
    payload = Property

    # The current image to display on the feature bar:
    image = '@facets:debug_object_feature'

    # The tooltip to display when the mouse is hovering over the image:
    tooltip = (
        "Click to create a pop-up VIPShell window for the object.\n"
        "Right click to set the debug options.\n"
        "Drag the selected debug object.\n"
        "Ctrl-drag the tab's object.\n"
        "Shift-drag the tab's DockControl.\n"
        "Alt-drag the tab's control."
    )

    #-- Property Implementations -----------------------------------------------

    def _get_payload ( self ):
        payload = self.dock_control

        if self.mode == 'object':
            return payload.object

        if self.mode == 'control':
            return payload.control

        if self.mode == 'ui':
            return getattr( payload.control, '_ui', None )

        return payload

    #-- Event Handlers ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left clicking on the feature image.
        """
        from facets.extra.tools.vip_shell import VIPShell

        shell = VIPShell(
            values = { 'info': DebugInfo( dock_control = self.dock_control ) }
        )
        do_later( shell.set, command = 'info' )
        shell.edit_facets()


    def right_click ( self ):
        """ Handles the user right clicking on the feature image.
        """
        object_action.checked       = (self.mode == 'object')
        dock_control_action.checked = (self.mode == 'dock_control')
        control_action.checked      = (self.mode == 'control')
        ui_action.checked           = (self.mode == 'ui')
        ui_action.enabled           = (getattr( self.dock_control.control,
                                                '_ui', None ) is not None)
        self.popup_menu( context_menu )


    def drag ( self ):
        """ Returns the object to be dragged when the user drags feature image.
        """
        return ObjectInspector( payload = self.payload )


    def control_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image while holding down the 'Ctrl' key:
        """
        return ObjectInspector( payload = self.dock_control.object )


    def shift_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image while holding down the 'Shift' key.
        """
        return ObjectInspector( payload = self.dock_control )


    def alt_drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image while holding down the 'Alt' key:
        """
        return ObjectInspector( payload = self.dock_control.control )

    #-- Overidable Class Methods -----------------------------------------------

    @classmethod
    def is_feature_for ( self, dock_control ):
        """ Returns whether or not the DockWindowFeature is a valid feature for
            a specified DockControl.
        """
        return (dock_control.object is not None)

    #-- Facet Event Handlers ---------------------------------------------------

    def _mode_set ( self, mode ):
        self.image = feature_images[ mode ]
        self.refresh()

#-------------------------------------------------------------------------------
#  'DebugInfo' class:
#-------------------------------------------------------------------------------

class DebugInfo ( HasPrivateFacets ):
    """ Provides information about an object being debugged.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The DockControl object for the object being debugged:
    dock_control = Instance( DockControl )

    # The object being debugged:
    object = DelegatesTo( 'dock_control' )

    # The Control associated with the DockControl:
    control = DelegatesTo( 'dock_control' )

    # The UI object associated with the object being debugged:
    ui = Property

    #-- Property Implementations -----------------------------------------------

    def _get_ui ( self ):
        return getattr( self.dock_control.control, '_ui', None )

#-------------------------------------------------------------------------------
#  'ObjectInspector' class:
#-------------------------------------------------------------------------------

class ObjectInspector ( HasPayload ):

    implements( IDockUIProvider )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'payload',
              show_label = False,
              editor     = ValueEditor()
        ),
        title     = 'Object Inspector',
        id        = 'facets.extra.tools.debug_inspector.ObjectInspector',
        kind      = 'live',
        resizable = True,
        width     = 0.3,
        height    = 0.4
    )

    #-- IDockUIProvider Interface ----------------------------------------------

    def get_dockable_ui ( self, parent ):
        """ Returns a Facets UI which a DockWindow can imbed.
        """
        return self.edit_facets( parent = parent, kind = 'editor' )

#-- EOF ------------------------------------------------------------------------