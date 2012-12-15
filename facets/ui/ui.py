"""
Defines the UI class used to represent an active facets-based user interface.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traceback \
    import print_exc

from facets.core_api \
    import HasPrivateFacets, DictStrAny, Any, List, Int, Instance, FacetError, \
           Property, Bool, Event, Callable, Str, on_facet_set,                 \
           property_depends_on

from facets.core.facet_base \
    import is_str

from facets.ui.pyface.timer.api \
    import do_later

from ui_facets \
    import AKind

from editor \
    import Editor

from view_elements \
    import ViewElements

from handler \
    import Handler, ViewHandler

from toolkit \
    import toolkit

from ui_info \
    import UIInfo

from helper \
    import save_window

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# List of **kind** types for views that must have a **parent** window specified
kind_must_have_parent = ( 'panel', 'subpanel' )

#-------------------------------------------------------------------------------
#  'UI' class:
#-------------------------------------------------------------------------------

class UI ( HasPrivateFacets ):
    """ Information about the user interface for a View.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ViewElements object from which this UI resolves Include items:
    view_elements = Instance( ViewElements )

    # Context objects that the UI is editing:
    context = DictStrAny

    # Handler object used for event handling:
    handler = Instance( Handler )

    # View template used to construct the user interface:
    view = Instance( 'facets.ui.view.View' )

    # Panel or dialog associated with the user interface:
    control = Any

    # Is the ui 'control' a control (True) or a layout (False)?
    is_control = Bool( True )

    # The parent UI (if any) of this UI:
    parent = Instance( 'UI' )

    # Toolkit-specific object that "owns" **control**:
    owner = Any

    # The top-level DockWindow for this user interface (if any):
    dock_window = Instance( 'facets.ui.dock.dock_window.DockWindow' )

    # UIInfo object containing context or editor objects:
    info = Instance( UIInfo )

    # Result from a modal or wizard dialog:
    result = Bool( False )

    # Undo and Redo history:
    history = Any

    # The KeyBindings object (if any) for this UI:
    key_bindings = Property # Instance( KeyBindings )

    # The unique ID for this UI for persistence:
    id = Str

    # Have any modifications been made to UI contents?
    modified = Bool( False )

    # Event when the user interface has changed:
    updated = Event( Bool )

    # Title of the dialog, if any:
    title = Str

    # The ImageResource of the icon, if any:
    icon = Any

    # Should the created UI have scroll bars?
    scrollable = Bool( False )

    # The number of currently pending editor error conditions:
    errors = Int

    # The code used to rebuild an updated user interface:
    rebuild = Callable

    # The kind of user interface:
    kind = AKind

    #-- Private Facets ---------------------------------------------------------

    # Original context when used with a modal dialog:
    _context = DictStrAny

    # Copy of original context used for reverting changes:
    _revert = DictStrAny

    # List of methods to call once the user interface is created:
    _defined = List

    # List of (visible_when,Editor) pairs:
    _visible = List

    # List of (enabled_when,Editor) pairs:
    _enabled = List

    # List of (checked_when,Editor) pairs:
    _checked = List

    # Search stack used while building a user interface:
    _search = List

    # List of dispatchable Handler methods:
    _dispatchers = List

    # List of editors used to build the user interface:
    _editors = List

    # List of names bound to the **info** object:
    _names = List

    # Index of currently the active group in the user interface:
    _active_group = Int

    # List of top-level groups used to build the user interface:
    _groups = Property
    _groups_cache = Any

    # Count of levels of nesting for undoable actions:
    _undoable = Int( -1 )

    # Code used to rebuild an updated user interface:
    _rebuild = Callable

    # The statusbar listeners that have been set up:
    _statusbar = List

    # Does the UI contain any scrollable widgets?
    #
    # The _scrollable facet is set correctly, but not used currently because
    # its value is arrived at too late to be of use in building the UI:
    _scrollable = Bool( False )

    # List of facets that are reset when a user interface is recycled
    # (i.e. rebuilt):
    recyclable_facets = [
        '_context', '_revert', '_defined', '_visible', '_enabled', '_checked',
        '_search', '_dispatchers', '_editors', '_names', '_active_group',
        '_undoable', '_rebuild', '_groups_cache', 'dock_window'
    ]

    # List of additional facets that are discarded when a user interface is
    # disposed:
    disposable_facets = [
        'view_elements', 'info', 'handler', 'context', 'view', 'history',
        'key_bindings', 'icon', 'rebuild',
    ]

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes the facets object.
        """
        self.info = UIInfo( ui = self )
        self.handler.init_info( self.info )


    def ui ( self, parent ):
        """ Creates a user interface from the associated View template object.
        """
        if (parent is None) and (self.kind in kind_must_have_parent):
            self.kind = 'live'

        self.view.on_facet_set( self._updated_set, 'updated', dispatch = 'ui' )
        self.rebuild = getattr( self, '_create_' + self.kind )
        self.rebuild( self, toolkit().as_toolkit_adapter( parent ) )


    def rebuild_ui ( self ):
        """ Rebuilds the user interface.
        """
        parent = size = None

        control = self.control
        if control is not None:
            parent = self.control.parent
            self.recycle()
            self.info.ui = self

        self.rebuild( self, parent )

        if control is not None:
            control.destroy()

        if parent is not None:
            layout = parent.layout
            if layout is not None:
                layout.add( self.control, stretch = 1 )


    def dispose ( self, result = None, abort = False ):
        """ Disposes of the contents of a user interface.
        """
        if result is not None:
            self.result = result

        # Only continue if the view has not already been disposed of:
        if self.control is not None:
            # Save the user preference information for the user interface:
            if not abort:
                self.save_prefs()

            # Finish disposing of the user interface:
            self.finish()


    def recycle ( self ):
        """ Recycles the user interface prior to rebuilding it.
        """
        # Reset all user interface editors:
        self.reset( destroy = False )

        # Discard any context object associated with the ui view control:
        self.control._object = None

        # Reset all recyclable facets:
        self.reset_facets( self.recyclable_facets )


    def finish ( self ):
        """ Finishes disposing of a user interface.
        """
        if self.info.ui is not None:

            # Reset the contents of the user interface:
            self.reset( destroy = False )

            # Notify the handler that the view has been closed:
            self.handler.closed( self.info, self.result )

            # Clear the back-link from the UIInfo object to us:
            self.info.ui = None

            # Dispose of any KeyBindings object we reference:
            if self.key_bindings is not None:
                self.key_bindings.dispose()

            # Destroy the view control (if necessary):
            self.control._object = None
            self.control.destroy()
            self.control = None

            # Break the linkage to any objects in the context dictionary:
            self.context.clear()

            # Remove specified symbols from our dictionary to aid in clean-up:
            self.reset_facets( self.recyclable_facets )
            self.reset_facets( self.disposable_facets )


    def reset ( self, destroy = True ):
        """ Resets the contents of a user interface.
        """
        for editor in self._editors:
            if editor._ui is not None:
                # Propagate result to enclosed ui objects:
                editor._ui.result = self.result

            editor.dispose()

            # Zap the control. If there are pending events for the control in
            # the UI queue, the editor's '_update_editor' method will see that
            # the control is None and discard the update request:
            editor.control = None

        # Remove any statusbar listeners that have been set up:
        for object, handler, name in self._statusbar:
            object.on_facet_set( handler, name, remove = True )

        del self._statusbar[:]

        if destroy:
            self.control.destroy_children()

        for dispatcher in self._dispatchers:
            dispatcher.remove()


    def find ( self, include ):
        """ Finds the definition of the specified Include object in the current
            user interface building context.
        """
        context = self.context
        result  = None

        # Get the context 'object' (if available):
        if len( context ) == 1:
            object = context.values()[ 0 ]
        else:
            object = context.get( 'object' )

        # Try to use our ViewElements objects:
        ve = self.view_elements

        # If none specified, try to get it from the UI context:
        if (ve is None) and (object is not None):
            # Use the context object's ViewElements (if available):
            ve = object.facet_view_elements()

        # Ask the ViewElements to find the requested item for us:
        if ve is not None:
            result = ve.find( include.id, self._search )

        # If not found, then try to search the 'handler' and 'object' for a
        # method we can call that will define it:
        if result is None:
            handler = context.get( 'handler' )
            if handler is not None:
                method = getattr( handler, include.id, None )
                if callable( method ):
                    result = method()

            if (result is None) and (object is not None):
                method = getattr( object, include.id, None )
                if callable( method ):
                    result = method()

        return result


    def push_level ( self ):
        """ Returns the current search stack level.
        """
        return len( self._search )


    def pop_level ( self, level ):
        """ Restores a previously pushed search stack level.
        """
        del self._search[ : len( self._search ) - level ]


    def prepare_ui ( self ):
        """ Performs all processing that occurs after the user interface is
            created.
        """
        # Invoke all of the editor 'name_defined' methods we've accumulated:
        info = self.info.set( initialized = False )
        for method in self._defined:
            method( info )

        # Then reset the list, since we don't need it anymore:
        del self._defined[:]

        # Synchronize all context facets with associated editor facets:
        self.sync_view()

        # Hook all keyboard events:
        toolkit().hook_events( self, self.control, 'keys', self.key_handler )

        # Hook all events if the handler is an extended 'ViewHandler':
        handler = self.handler
        if isinstance( handler, ViewHandler ):
            toolkit().hook_events( self, self.control )

        # Invoke the handler's 'init' method, and abort if it indicates failure:
        if handler.init( info ) == False:
            raise FacetError( 'User interface creation aborted' )

        # For each Handler method whose name is of the form
        # 'object_name_changed', where 'object' is the name of an object in the
        # UI's 'context', create a facet notification handler that will call
        # the method whenever 'object's 'name' facet changes. Also invoke the
        # method immediately so initial user interface state can be correctly
        # set:
        context = self.context
        for name in self._each_facet_method( handler ):
            if name[-8:] == '_changed':
                prefix = name[:-8]
                col    = prefix.find( '_', 1 )
                if col >= 0:
                    object = context.get( prefix[ : col ] )
                    if object is not None:
                        method     = getattr( handler, name )
                        facet_name = prefix[ col + 1: ]
                        self._dispatchers.append( Dispatcher(
                             method, info, object, facet_name ) )
                        if object.base_facet( facet_name ).type != 'event':
                            method( info )

        # If there are any Editor object's whose 'visible', 'enabled' or
        # 'checked' state is controlled by a 'visible_when', 'enabled_when' or
        # 'checked_when' expression, set up an 'anyfacet' changed notification
        # handler on each object in the 'context' that will cause the 'visible',
        # 'enabled' or 'checked' state of each affected Editor to be set. Also
        # trigger the evaluation immediately, so the visible, enabled or checked
        # state of each Editor can be correctly initialized:
        if (len( self._visible ) +
            len( self._enabled ) +
            len( self._checked )) > 0:
            for object in context.values():
                object.on_facet_set( self._evaluate_when, dispatch = 'ui' )

            self._evaluate_when()

        # Indicate that the user interface has been initialized:
        info.initialized = True


    def sync_view ( self ):
        """ Synchronize context object facets with view editor facets.
        """
        for name, object in self.context.items():
            self._sync_view( name, object, 'sync_to_view',   'from' )
            self._sync_view( name, object, 'sync_from_view', 'to'   )
            self._sync_view( name, object, 'sync_with_view', 'both' )


    def _sync_view ( self, name, object, metadata, direction ):
        info = self.info
        for facet_name, facet in object.facets( **{metadata: is_str} ).items():
            for sync in getattr( facet, metadata ).split( ',' ):
                try:
                    editor_id, editor_name = [ item.strip()
                                               for item in sync.split( '.' ) ]
                except:
                    raise FacetError(
                        ("The '%s' metadata for the '%s' facet in the '%s' "
                         "context object should be of the form: "
                         "'id1.facet1[,...,idn.facetn].") %
                        ( metadata, facet_name, name )
                    )

                editor = getattr( info, editor_id, None )
                if editor is not None:
                    editor.sync_value( '%s.%s' % ( name, facet_name ),
                                       editor_name, direction )
                else:
                    raise FacetError(
                        ("No editor with id = '%s' was found for the '%s' "
                         "metadata for the '%s' facet in the '%s' context "
                         "object.") %
                        ( editor_id, metadata, facet_name, name )
                    )


    def get_extended_value ( self, name ):
        """ Gets the current value of a specified extended facet name.
        """
        names = name.split( '.' )
        if len( names ) > 1:
            value = self.context[ names[ 0 ] ]
            del names[ 0 ]
        else:
            value = self.context[ 'object' ]

        for name in names:
            value = getattr( value, name )

        return value


    def restore_prefs ( self, id = None ):
        """ Retrieves and restores any saved user preference information
            associated with the UI.
        """
        if id is None:
            id = self.id
        elif (len( id ) == 1) and (id in '~#$'):
            id += self.id

        if id != '':
            ui_prefs = self.facet_db_get( id )
            if (ui_prefs is None) and (id[:1] not in '~#$'):
                ui_prefs = self.facet_db_get( '$' + id )

            try:
                return self.set_prefs( ui_prefs )
            except:
                print_exc()

        return None


    def set_prefs ( self, prefs ):
        """ Sets the values of user preferences for the UI.
        """
        if isinstance( prefs, dict ):
            info = self.info
            for name in self._names:
                editor = getattr( info, name, None )
                if isinstance( editor, Editor ) and (editor.ui is self):
                    editor_prefs = prefs.get( name )
                    if editor_prefs is not None:
                        editor.restore_prefs( editor_prefs )

            if self.key_bindings is not None:
                key_bindings = prefs.get( '$' )
                if key_bindings is not None:
                    self.key_bindings.merge( key_bindings )

            return prefs.get( '' )

        return None


    def save_prefs ( self, prefs = None, path = '' ):
        """ Saves any user preference information associated with the UI.
        """
        if prefs is None:
            save_window( self, path )

            return

        if self.id != '':
            self.facet_db_set( path + self.id, self.get_prefs( prefs ) )


    def get_prefs ( self, prefs = None ):
        """ Gets the preferences to be saved for the user interface.
        """
        ui_prefs = {}
        if prefs is not None:
            ui_prefs[ '' ] = prefs

        if self.key_bindings is not None:
            ui_prefs[ '$' ] = self.key_bindings

        info = self.info
        for name in self._names:
            editor = getattr( info, name, None )
            if isinstance( editor, Editor ) and (editor.ui is self):
                prefs = editor.save_prefs()
                if prefs != None:
                    ui_prefs[ name ] = prefs

        return ui_prefs


    def get_error_controls ( self ):
        """ Returns the list of editor error controls contained by the user
            interface.
        """
        controls = []
        for editor in self._editors:
            control = editor.get_error_control()
            if isinstance( control, list ):
                controls.extend( control )
            else:
                controls.append( control )

        return controls


    def add_defined ( self, method ):
        """ Adds a Handler method to the list of methods to be called once the
            user interface has been constructed.
        """
        self._defined.append( method )


    def add_visible ( self, visible_when, editor ):
        """ Adds a conditionally enabled Editor object to the list of monitored
            'visible_when' objects.
        """
        try:
            self._visible.append( ( compile( visible_when, '<string>', 'eval' ),
                                    editor ) )
        except:
            print_exc()


    def add_enabled ( self, enabled_when, editor ):
        """ Adds a conditionally enabled Editor object to the list of monitored
            'enabled_when' objects.
        """
        try:
            self._enabled.append( ( compile( enabled_when, '<string>', 'eval' ),
                                    editor ) )
        except:
            print_exc()


    def add_checked ( self, checked_when, editor ):
        """ Adds a conditionally enabled (menu) Editor object to the list of
            monitored 'checked_when' objects.
        """
        try:
            self._checked.append( ( compile( checked_when, '<string>', 'eval' ),
                                    editor ) )
        except:
            print_exc()


    def do_undoable ( self, action, *args, **kw ):
        """ Performs an action that can be undone.
        """
        undoable = self._undoable
        try:
            if (undoable == -1) and (self.history is not None):
                self._undoable = self.history.now

            action( *args, **kw )
        finally:
            if undoable == -1:
                self._undoable = -1


    def route_event ( self, event ):
        """ Routes a "hooked" event to the correct handler method.
        """
        toolkit().route_event( self, event )


    def key_handler ( self, event, skip = True ):
        """ Handles key events.
        """
        key_bindings = self.key_bindings
        handled      = ((key_bindings is not None) and
                         key_bindings.do( event, [], self.info ))

        if (not handled) and (self.parent is not None):
            handled = self.parent.key_handler( event, False )

        if (not handled) and skip:
            event.Skip()

        return handled


    def evaluate ( self, function, *args, **kw_args ):
        """ Evaluates a specified function in the UI's **context**.
        """
        if function is None:
            return None

        if callable( function ):
            return function( *args, **kw_args )

        context = self.context.copy()
        context[ 'ui' ]      = self
        context[ 'handler' ] = self.handler

        return eval( function, globals(), context )( *args, **kw_args )


    def eval_when ( self, when, result = True ):
        """ Evaluates an expression in the UI's **context** and returns the
            result.
        """
        context = self._get_context()
        try:
            result = eval( when, globals(), context )
        except:
            print_exc()

        return result

    #-- User Interface Creation Methods ----------------------------------------

    def _create_panel ( self, ui, parent ):
        """ Creates a GUI toolkit neutral panel-based user interface using
            information from the specified UI object.
        """
        from ui_panel import ui_panel

        ui_panel( ui, parent )


    def _create_subpanel ( self, ui, parent ):
        """ Creates a GUI toolkit neutral subpanel-based user interface using
            information from the specified UI object.
        """
        from ui_panel import ui_subpanel

        ui_subpanel( ui, parent )


    def _create_livemodal ( self, ui, parent ):
        """ Creates a GUI toolkit neutral modal "live update" dialog user
            interface using information from the specified UI object.
        """
        from ui_live import ui_livemodal

        ui_livemodal( ui, parent )


    def _create_live ( self, ui, parent ):
        """ Creates a GUI toolkit neutral non-modal "live update" window user
            interface using information from the specified UI object.
        """
        from ui_live import ui_live

        ui_live( ui, parent )


    def _create_modal ( self, ui, parent ):
        """ Creates a GUI toolkit neutral modal dialog user interface using
            information from the specified UI object.
        """
        from ui_modal import ui_modal

        ui_modal( ui, parent )


    def _create_nonmodal ( self, ui, parent ):
        """ Creates a GUI toolkit neutral non-modal dialog user interface using
            information from the specified UI object.
        """
        from ui_modal import ui_nonmodal

        ui_nonmodal( ui, parent )


    def _create_popup ( self, ui, parent ):
        """ Creates a GUI toolkit neutral temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        from ui_live import ui_popup

        ui_popup( ui, parent )


    def _create_popout ( self, ui, parent ):
        """ Creates a GUI toolkit neutral temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        from ui_live import ui_popout

        ui_popout( ui, parent )


    def _create_popover ( self, ui, parent ):
        """ Creates a GUI toolkit neutral temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        from ui_live import ui_popover

        ui_popover( ui, parent )


    def _create_info ( self, ui, parent ):
        """ Creates a GUI toolkit neutral temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        from ui_live import ui_info

        ui_info( ui, parent )


    def _create_editor ( self, ui, parent ):
        """ Creates a GUI toolkit neutral Facets editor implemented as a Facets
            UI view.
        """
        from ui_panel import ui_editor

        ui_editor( ui, parent )


    def _create_wizard ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific wizard dialog user interface using
            information from the specified UI object.
        """
        from ui_wizard import ui_wizard

        ui_wizard( ui, parent )

    #-- Private Methods --------------------------------------------------------

    def _get_context ( self, context = None ):
        """ Gets the context to use for evaluating an expression.
        """
        if context is None:
            context = self.context

        name = 'object'
        n    = len( context )
        if (n == 2) and ('handler' in context):
            for name, value in context.iteritems():
                if name != 'handler':
                    break
        elif n == 1:
            name = context.keys()[0]

        value = context.get( name )
        if value is not None:
            context2 = value.facet_get( value.editable_facets() )
            context2.update( context )
        else:
            context2 = context.copy()

        context2[ 'ui' ] = self

        return context2


    def _evaluate_when ( self ):
        """ Sets the 'visible', 'enabled', and 'checked' states for all Editors
            controlled by a 'visible_when', 'enabled_when' or 'checked_when'
            expression.
        """
        context = self._get_context()
        self._evaluate_condition( self._visible, 'visible', context )
        self._evaluate_condition( self._enabled, 'enabled', context )
        self._evaluate_condition( self._checked, 'checked', context )


    def _evaluate_condition ( self, conditions, facet, context ):
        """ Evaluates a list of (eval,editor) pairs and sets a specified facet
            on each editor to reflect the Boolean value of the expression.
        """
        for when, editor in conditions:
            value = True
            try:
                if not eval( when, globals(), context ):
                    value = False
            except:
                print_exc()

            setattr( editor, facet, value )


    def _get__groups ( self ):
        """ Returns the top-level Groups for the view (after resolving
            Includes. (Implements the **_groups** property.)
        """
        if self._groups_cache is None:
            self._groups_cache = [ self.view.content.get_shadow( self ) ]

        return self._groups_cache

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'view, context' )
    def _get_key_bindings ( self ):
        view, context = self.view, self.context
        if (context is None) or (view is None) or (view.key_bindings is None):
            return None

        return view.key_bindings.clone( controllers = context.values() )

    #-- Facets Event Handlers --------------------------------------------------

    def _updated_set ( self ):
        if self.rebuild is not None:
            do_later( self.rebuild_ui )


    def _title_set ( self, title ):
        if self.control is not None:
            self.control.value = title


    def _icon_set ( self, icon ):
        if (self.control is not None) and (icon is not None):
            self.control.icon = icon.create_icon()


    @on_facet_set( 'parent, view, context' )
    def _pvc_modified ( self ):
        parent = self.parent
        if (parent is not None) and (self.key_bindings is not None):
            # If we don't have our own history, use our parent's:
            if self.history is None:
                self.history = parent.history

            # Link our KeyBindings object as a child of our parent's
            # KeyBindings object (if any):
            if parent.key_bindings is not None:
                parent.key_bindings.children.append( self.key_bindings )

#-------------------------------------------------------------------------------
#  'Dispatcher' class:
#-------------------------------------------------------------------------------

class Dispatcher ( object ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, method, info, object, method_name ):
        """ Initializes the object.
        """
        self.method      = method
        self.info        = info
        self.object      = object
        self.method_name = method_name
        object.on_facet_set( self.dispatch, method_name, dispatch = 'ui' )


    def dispatch ( self ):
        """ Dispatches the method.
        """
        self.method( self.info )


    def remove ( self ):
        """ Removes the dispatcher.
        """
        self.object.on_facet_set( self.dispatch, self.method_name,
                                  remove = True )

#-- EOF ------------------------------------------------------------------------