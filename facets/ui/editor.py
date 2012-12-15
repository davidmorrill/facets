"""
Defines the abstract Editor class, which represents an editing control for
an object facet in a Facets-based user interface.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets, HasPrivateFacets, ReadOnly, Any, Property, Undefined, \
           Bool, Callable, FacetError, Str, Instance, FacetListEvent

from facets.core.facet_base \
    import not_none

from facets.ui.adapters.control \
    import Control

from facets.ui.pyface.message_dialog \
    import error as error_message

from undo \
    import UndoItem

from item \
    import Item

from colors \
    import WindowColor

from facets.ui.adapters.abstract_adapter \
    import AbstractAdapter

from facets.ui.adapters.control \
    import as_toolkit_control

from context_value \
    import ContextValue

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  'Editor' abstract base class:
#-------------------------------------------------------------------------------

class Editor ( HasPrivateFacets ):
    """ Represents an editing control for an object facet in a Facets-based
        user interface.
    """

    #-- Class Constants --------------------------------------------------------

    # Should the editor fill its layout space (True) or use its normal
    # size (False):
    fill = True

    # Is the editor implementation GUI toolkit neutral?
    is_toolkit_neutral = True

    #-- Facet Definitions ------------------------------------------------------

    # The UI (user interface) this editor is part of:
    ui = Instance( 'facets.ui.ui.UI' )

    # Full name of the object the editor is editing (e.g. 'object.link1.link2'):
    object_name = Str( 'object' )

    # The object this editor is editing (e.g. object.link1.link2):
    object = Instance( HasFacets )

    # The name of the facet this editor is editing (e.g. 'value'):
    name = Str

    # The context object the editor is editing (e.g. object):
    context_object = Instance( HasFacets )

    # The extended name of the object facet being edited. That is,
    # 'object_name.name' minus the context object name at the beginning. For
    # example: 'link1.link2.value':
    extended_name = Str

    # Text description of the object facet being edited:
    description = ReadOnly

    # The Item object used to create this editor:
    item = Instance( Item, () )

    # The GUI toolkit specific control defined by this editor:
    control = Any

    # The GUI toolkit neutral adapter for the control defined by the editor:
    adapter = Instance( AbstractAdapter )

    # The GUI label (if any) defined by this editor:
    label_control = Any

    # The GUI toolkit neutral adapter for the label defined by the editor:
    label_adapter = Instance( Control )

    # Is the underlying GUI widget enabled?
    enabled = Bool( True )

    # Is the underlying GUI widget visible?
    visible = Bool( True )

    # Is the underlying GUI widget scrollable?
    scrollable = Bool( False )

    # Is the value of the editor a list whose content changes should be handled
    # by the 'update_editor' method?
    is_list = Bool( False )

    # The EditorFactory used to create this editor:
    factory = Instance( 'facets.ui.editor_factory.EditorFactory' )

    # Is the editor updating the object.name value?
    updating = Bool( False )

    # Current value for object.name:
    value = Property

    # Current value of object facet as a string:
    str_value = Property

    # The facet the editor is editing (not its value, but the facet itself):
    value_facet = Property

    # The current editor invalid state status:
    invalid = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes the editor object.
        """
        # Synchronize the application invalid state status with the editor's:
        if self.factory is not None:
            self.sync_value( self.factory.invalid, 'invalid', 'from' )


    def prepare ( self, parent ):
        """ Finishes setting up the editor.
        """
        name = self.extended_name
        if name != 'None':
            if self.is_list:
                name += '[]'

            self.context_object.on_facet_set( self._update_editor,
                                              name, dispatch = 'ui' )

        if not self.is_toolkit_neutral:
            parent = as_toolkit_control( parent )

        self.init( parent )
        self._sync_values()
        self.update_editor()
        self._set_adapter( self )


    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        raise NotImplementedError


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self.ui is None:
            return

        name = self.extended_name
        if name != 'None':
            self.context_object.on_facet_set( self._update_editor,
                                              name + '[]', remove = True )

        if self._user_from is not None:
            for name, handler in self._user_from:
                self.on_facet_set( handler, name, remove = True )

        if self._user_to is not None:
            for object, name, handler in self._user_to:
                object.on_facet_set( handler, name, remove = True )

        # Remove all 'editor' references in the editor's adapter:
        self._set_adapter( None )

        # Break linkages to references we no longer need:
        self.object  = self.ui = self.item = self.factory = self.control = \
        self.adapter = self.label_control  = self.context_object = None


    def string_value ( self, value, format_func = None ):
        """ Returns the text representation of a specified object facet value.

            If the **format_func** attribute is set on the editor factory, then
            this method calls that function to do the formatting.  If the
            **format_str** attribute is set on the editor factory, then this
            method uses that string for formatting. If neither attribute is
            set, then this method just calls the built-in str() function.
        """
        factory = self.factory
        if factory.format_func is not None:
            return factory.format_func( value )

        if factory.format_str != '':
            return (factory.format_str % value)

        if format_func is not None:
            return format_func( value )

        return self.object.facet( self.name ).string_value(
                                                 self.object, self.name, value )


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.

            Can be overridden in a subclass.
        """
        error_message( self.adapter.parent, str( excp ),
                       self.description + ' value error' )


    def log_change ( self, undo_factory, *undo_args ):
        """ Logs a change made in the editor.
        """
        # Indicate that the contents of the user interface have been changed:
        ui          = self.ui
        ui.modified = True

        # Create an undo history entry if we are maintaining a history:
        undoable = ui._undoable
        if undoable >= 0:
            history = ui.history
            if history is not None:
                item = undo_factory( *undo_args )
                if item is not None:
                    if undoable == history.now:
                        # Create a new undo transaction:
                        history.add( item )
                    else:
                        # Extend the most recent undo transaction:
                        history.extend( item )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.

            Can be overridden in a subclass.
        """
        new_value = self.str_value
        if self.adapter.value != new_value:
            self.adapter.value = new_value


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self.adapter


    def in_error_state ( self ):
        """ Returns whether or not the editor is in an error state.
        """
        return False


    def set_error_state ( self, state = None, control = None ):
        """ Sets the editor's current error state.
        """
        from facets.ui.colors import OKColor, ErrorColor

        state = self.get_error_state( state )

        if control is None:
            control = self.get_error_control()

        controls = control
        if not isinstance( control, list ):
            controls = [ control ]

        for control in controls:
            # fixme: Eventually this code should not be necessary...
            control    = toolkit().as_toolkit_adapter( control )
            ui_control = control()
            if state:
                color = ErrorColor
                if getattr( ui_control, '_ok_color', None ) is None:
                    ui_control._ok_color = control.background_color
            else:
                color = getattr( ui_control, '_ok_color', None )
                if color is None:
                    color = OKColor
                    if control.is_panel:
                        color = WindowColor

            control.background_color = color
            control.refresh()


    def get_error_state ( self, state ):
        """ Returns the current editor error state.
        """
        if state is None:
            state = self.invalid

        return (state or self.in_error_state())


    def get_undo_item ( self, object, name, old_value, new_value ):
        """ Creates an undo history entry.

            Can be overridden in a subclass for special value types.
        """
        return UndoItem( object    = object,
                         name      = name,
                         old_value = old_value,
                         new_value = new_value )


    def set_tooltip ( self, control = None ):
        """ Sets the tooltip for a specified control.
        """
        desc = self.description
        if desc == '':
            desc = self.object.base_facet( self.name ).desc
            if desc is None:
                return False

            desc = 'Specifies ' + desc

        if control is None:
            control = self.adapter

        control.tooltip = desc

        return True


    def parse_extended_name ( self, name ):
        """ Returns a tuple of the form ( context_object, 'name[.name...],
            callable ) for a specified extended name of the form: 'name' or
            'context_object_name.name[.name...]'.
        """
        col = name.find( '.' )
        if col < 0:
            object = self.context_object
        else:
            object, name = self.ui.context[ name[ : col ] ], name[ col + 1: ]

        return ( object, name, eval( "lambda obj=object: obj." + name ) )


    def sync_value ( self, user_name, editor_name, mode = 'both',
                           is_list = False ):
        """ Sets or unsets synchronization between an editor facet and a user
            object facet.
        """
        if user_name != '':
            key = '%s:%s' % ( user_name, editor_name )

            if self._no_facet_update is None:
                self._no_facet_update = {}

            user_ref = 'user_object'
            col      = user_name.find( '.' )
            if col < 0:
                user_object = self.context_object
                xuser_name  = user_name
            else:
                user_object = self.ui.context[ user_name[ : col ] ]
                user_name   = xuser_name = user_name[ col + 1: ]
                col         = user_name.rfind( '.' )
                if col >= 0:
                    user_ref += ('.' + user_name[ : col ])
                    user_name = user_name[ col + 1: ]

            user_value = compile( '%s.%s' % ( user_ref, user_name ),
                                  '<string>', 'eval' )
            user_ref   = compile( user_ref, '<string>', 'eval' )

            if mode in ( 'from', 'both' ):

                def user_facet_modified ( new ):
                    # Need this to include 'user_object' in closure:
                    user_object
                    if key not in self._no_facet_update:
                        self._no_facet_update[ key ] = None
                        try:
                            setattr( self, editor_name, new )
                        except:
                            pass

                        del self._no_facet_update[ key ]

                user_object.on_facet_set( user_facet_modified, xuser_name )

                if self._user_to is None:
                    self._user_to = []

                self._user_to.append( ( user_object, xuser_name,
                                        user_facet_modified ) )

                if is_list:

                    def user_list_modified ( event ):
                        if isinstance( event, FacetListEvent ):
                            if key not in self._no_facet_update:
                                self._no_facet_update[ key ] = None
                                n = event.index
                                try:
                                    getattr( self, editor_name )[
                                        n: n + len( event.removed )
                                    ] = event.added
                                except:
                                    pass
                                del self._no_facet_update[ key ]

                    user_object.on_facet_set( user_list_modified,
                                              xuser_name + '_items' )
                    self._user_to.append( ( user_object, xuser_name + '_items',
                                            user_list_modified ) )

                try:
                    setattr( self, editor_name, eval( user_value ) )
                except:
                    pass

            if mode in ( 'to', 'both' ):

                def editor_facet_modified ( new ):
                    # Need this to include 'user_object' in closure:
                    user_object
                    if key not in self._no_facet_update:
                        self._no_facet_update[ key ] = None
                        try:
                            setattr( eval( user_ref ), user_name, new )
                        except:
                            pass
                        del self._no_facet_update[ key ]

                self.on_facet_set( editor_facet_modified, editor_name )

                if self._user_from is None:
                    self._user_from = []
                self._user_from.append( ( editor_name, editor_facet_modified ) )

                if is_list:

                    def editor_list_modified ( event ):
                        # Need this to include 'user_object' in closure:
                        user_object
                        if key not in self._no_facet_update:
                            self._no_facet_update[ key ] = None
                            n = event.index
                            try:
                                eval( user_value )[ n:
                                    n + len( event.removed ) ] = event.added
                            except:
                                pass
                            del self._no_facet_update[ key ]

                    self.on_facet_set( editor_list_modified,
                                       editor_name + '_items' )
                    self._user_from.append( ( editor_name + '_items',
                                              editor_list_modified ) )

                if mode == 'to':
                    try:
                        setattr( eval( user_ref ), user_name,
                                 getattr( self, editor_name ) )
                    except:
                        pass

    #-- Facet Default Values ---------------------------------------------------

    def _context_object_default ( self ):
        """ Returns the context object the editor is using.
        """
        object_name = self.object_name
        context_key = object_name.split( '.', 1 )[0]
        if (object_name != '') and (context_key in self.ui.context):
            return self.ui.context[ context_key ]

        # This handles the case of a 'ListItemProxy', which is not in the
        # ui.context, but is the editor 'object':
        return self.object


    def _extended_name_default ( self ):
        """ Returns the extended facet name being edited.
        """
        return ('%s.%s' % ( self.object_name, self.name )).split( '.', 1 )[1]

    #-- Property Implementations -----------------------------------------------

    def _get_value_facet ( self ):
        """ Returns the facet the editor is editing.
        """
        return self.object.facet( self.name )


    def _get_value ( self ):
        return getattr( self.object, self.name, Undefined )

    def _set_value ( self, value ):
        if self.name != 'None':
            self.ui.do_undoable( self.__set_value, value )

    def __set_value ( self, value ):
        self._no_update = True
        try:
            try:
                old      = self.value
                handler  = self.ui.handler
                obj_name = self.object_name
                name     = self.name
                method   = (getattr( handler, '%s_%s_setattr' % ( obj_name,
                                              name ), None ) or
                            getattr( handler, '%s_setattr' % name, None ) or
                            getattr( handler, 'setattr' ))
                method( self.ui.info, self.object, name, value )
                if old != self.value:
                    self.facet_property_set( 'value', old )
            except FacetError, excp:
                self.error( excp )
                raise
        finally:
            self._no_update = False


    def _get_str_value ( self ):
        """ Returns the text representation of the object facet.
        """
        return self.string_value( getattr( self.object, self.name, Undefined ) )

    #-- Private Methods --------------------------------------------------------

    def _str ( self, value ):
        """ Returns the text representation of a specified value.
        """
        return str( value )


    def _update_editor ( self, object, facet, old, new ):
        """ Performs updates when the object facet changes.
        """
        # If background threads have modified the facet the editor is bound to,
        # their facet notifications are queued to the UI thread. It is possible
        # that by the time the UI thread dispatches these events, the UI the
        # editor is part of has already been closed. So we need to check if we
        # are still bound to a live UI, and if not, exit immediately:
        if self.ui is None:
            return

        # If the notification is for an object different than the one actually
        # being edited, it is due to editing an item of the form:
        # object.link1.link2.name, where one of the 'link' objects may have
        # been modified. In this case, we need to rebind the current object
        # being edited:
        if object is not self.object:
            self.object = eval( self.object_name, globals(), self.ui.context )

        # If the editor has gone away for some reason, disconnect and exit:
        if self.control is None:
            self.context_object.on_facet_set(
                self._update_editor, self.extended_name, remove = True
            )

            return

        # Log the change that was made (as long as it is not for an event):
        if object.base_facet( facet ).type != 'event':
            self.log_change( self.get_undo_item, object, facet, old, new )

        # If the change was not caused by the editor itself:
        if not self._no_update:
            # Update the editor control to reflect the current object state:
            self.update_editor()

            # Indicate that the editor's 'value' facet has changed as well:
            self.facet_property_set( 'value', None )


    def _sync_values ( self ):
        """ Initializes and synchronizes (as needed) editor facets with the
            value of corresponding factory facets.
        """
        factory = self.factory
        for name, facet in factory.facets( sync_value = not_none ):
            value = getattr( factory, name )
            if isinstance( value, ContextValue ):
                self_facet = self.facet( name )
                self.sync_value( value.name, name,
                                 self_facet.sync_value or facet.sync_value,
                                 self_facet.is_list is True )
            elif value is not Undefined:
                setattr( self, name, value )


    def _set_adapter ( self, value ):
        """ Initializes the 'editor' facet of the editor 'adapter' to a
            specified value.
        """
        control = self.adapter
        if isinstance( control, Control ):
            control.editor = value
        else:
            self._init_layout( control, value )


    def _init_layout ( self, layout, value ):
        """ Initialize the 'editor' facet of all controls contained within a
            specified *layout* object.
        """
        for item in layout.children:
            child_control = item.control
            if child_control is not None:
                if child_control.editor is None:
                    child_control.editor = value
            else:
                child_layout = item.layout
                if child_layout is not None:
                    self._init_layout( child_layout, value )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the 'control' facet being changed.
        """
        if control is None:
            self.adapter = None
        elif (self.adapter is None) or (self.adapter() is not control):
            self.adapter    = toolkit().adapter_for( control )
            control._editor = self


    def _adapter_set ( self, adapter ):
        """ Handles the 'adapter' facet being changed.
        """
        if adapter is None:
            self.control = None
        else:
            self.control = adapter()


    def _label_control_set ( self, control ):
        """ Handles the 'label_control' facet being changed.
        """
        if control is None:
            self.label_adapter = None
        elif ((self.label_adapter is None) or
              (self.label_adapter() is not control)):
            self.label_adapter = toolkit().control_adapter_for( control )


    def _label_adapter_set ( self, adapter ):
        """ Handles the 'label_adapter' facet being changed.
        """
        if adapter is None:
            self.label_control = None
        else:
            self.label_control = adapter()


    def _enabled_set ( self, enabled ):
        """ Handles the **enabled** state of the editor being changed.
        """
        control = self.adapter
        if control is not None:
            control.enabled = enabled
            control.refresh()


    def _visible_set ( self, visible ):
        """ Handles the **visible** state of the editor being changed.
        """
        if self.label_adapter is not None:
            self.label_adapter.visible = visible

        control         = self.adapter
        control.visible = visible

        layout = control.parent_layout
        if layout is not None:
            layout.do_layout()

        # Handle the case where the item whose visibility has changed is a
        # notebook page:
        page = control.parent

        ## fixme: is this OK ?
        if page is None:
            return

        page_control = page()
        page_name    = getattr( page_control, '_page_name', '' )
        if page_name != '':
            notebook = page.parent
            for i in range( 0, notebook.count ):
                if notebook.get_item( i )() is page_control:
                    break
            else:
                i = -1

            if visible:
                if i < 0:
                    notebook.add_page( page_name, page )

            elif i >= 0:
                notebook.remove_item( i )


    def _invalid_set ( self, state ):
        """ Handles the editor's invalid state changing.
        """
        self.set_error_state()

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.

            Should be overridden in subclasses if needed.
        """
        pass


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.

            Should be overridden in subclasses if needed.
        """
        return None

#-------------------------------------------------------------------------------
#  'EditorWithList' class:
#-------------------------------------------------------------------------------

class EditorWithList ( Editor ):
    """ Editor for an object that contains a list.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Object containing the list being monitored:
    list_object = Instance( HasFacets )

    # Name of the monitored facet:
    list_name = Str

    # Function used to evaluate the current list object value:
    list_value = Callable

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Initializes the object.
        """
        factory = self.factory
        name    = factory.name
        if name != '':
            self.list_object, self.list_name, self.list_value = \
                self.parse_extended_name( name )
        else:
            self.list_object, self.list_name = factory, 'values'
            self.list_value = lambda: factory.values

        self.list_object.on_facet_set(
            self._list_updated, self.list_name + '[]', dispatch = 'ui'
        )

        self._list_updated()


    def dispose ( self ):
        """ Disconnects the listeners set up by the constructor.
        """
        self.list_object.on_facet_set(
            self._list_updated, self.list_name + '[]', remove = True
        )

        super( EditorWithList, self ).dispose()


    def _list_updated ( self ):
        """ Handles the monitored facet being updated.
        """
        self.list_updated( self.list_value() )


    def list_updated ( self, values ):
        """ Handles the monitored list being updated.
        """
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------