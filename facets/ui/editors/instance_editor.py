"""
Defines the various GUI toolkit neutral instance editors and the instance
editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, List, Property, Enum, Type, Bool, Editor, toolkit, \
           EditorFactory

from facets.ui.view \
    import View

from facets.ui.ui_facets \
    import AView, AKind

from facets.ui.helper \
    import user_name_for

from facets.ui.handler \
    import Handler

from facets.ui.instance_choice \
    import InstanceChoice, InstanceChoiceItem

from facets.ui.colors \
    import DropColor

from facets.ui.pyface.timer.api \
    import do_later

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

OrientationMap = {
    'default':    None,
    'horizontal': False,
    'vertical':   True
}

#-------------------------------------------------------------------------------
#  'InstanceEditor' class:
#-------------------------------------------------------------------------------

class InstanceEditor ( EditorFactory ):
    """ GUI toolkit neutral editor factory for instance editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # List of items describing the types of selectable or editable instances:
    values = List( InstanceChoiceItem )

    # Extended name of the context object facet containing the list of types of
    # selectable or editable instances:
    name = Str

    # Is the current value of the object facet editable (vs. merely selectable)?
    editable = Bool( True )

    # Should the object facet value be selectable from a list of objects (a
    # value of True forces a selection list to be displayed, while a value of
    # False displays a selection list only if at least one object in the list
    # of possible object values is selectable):
    selectable = Bool( False )

    # Should the editor support drag and drop of objects to set the facet value
    # (a value of True forces the editor to allow drag and drop, while a value
    # of False only supports drag and drop if at least one item in the list of
    # possible objects supports drag and drop):
    droppable = Bool( False )

    # Should factory-created objects be cached?
    cachable = Bool( True )

    # Optional label for button:
    label = Str

    # Optional instance view to use:
    view = AView

    # Extended name of the context object facet containing the view, or name of
    # the view, to use:
    view_name = Str

    # The ID to use with the view:
    id = Str

    # Kind of pop-up editor (live, modal, nonmodal, wizard, ...):
    kind = AKind( 'popup' )

    # The orientation of the instance editor relative to the instance selector:
    orientation = Enum( 'default', 'horizontal', 'vertical' )

    # The default adapter class used to create InstanceChoice compatible
    # adapters for instance objects:
    adapter = Type( InstanceChoice, allow_none = False )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View( [ [ 'label{Button label}',
                            'view{View name}', '|[]' ],
                          [ 'kind@', '|[Pop-up editor style]<>' ] ] )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )


    def custom_editor ( self, ui, object, name, description ):
        return CustomEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( Editor ):
    """ Custom style of editor for instances. If selection among instances is
        allowed, the editor displays a combo box listing instances that can be
        selected. If the current instance is editable, the editor displays a
        panel containing facet editors for all the instance's facets.
    """

    #-- Class Constants --------------------------------------------------------

    # Background color when an item can be dropped on the editor:
    ok_color = DropColor

    # Is the orientation of the instance editor relative to the instance
    # selector vertical?
    is_vertical = True

    # Class constant:
    extra = 0

    #-- Facet Definitions ------------------------------------------------------

    # List of InstanceChoiceItem objects used by the editor:
    items = Property

    # The maximum extra padding that should be allowed around the editor:
    # (Override of the Editor base class facet)
    border_size = 0

    # The view to use for displaying the instance:
    view = AView

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if factory.name != '':
            self._object, self._name, self._value = \
                self.parse_extended_name( factory.name )

        # Build the instance selector if needed:
        editable   = factory.editable
        selectable = factory.selectable
        droppable  = factory.droppable
        items      = self.items
        for item in items:
            droppable  |= item.is_droppable()
            selectable |= item.is_selectable()

        choosable = (selectable or droppable)
        if not (choosable or editable):
            choosable = selectable = True

        # Create a panel to hold the object facet's view:
        if choosable and editable:
            self.adapter = parent = toolkit().create_panel( parent )

        if selectable:
            self._object_cache = {}
            item = self.item_for( self.value )
            if item is not None:
                self._object_cache[ id( item ) ] = self.value

            self._choice = choice = toolkit().create_combobox( parent )
            choice.set_event_handler( choose = self.update_object )

            if droppable:
                choice.background_color = self.ok_color

            self.set_tooltip( choice )

            if factory.name != '':
                self._object.on_facet_set( self.rebuild_items, self._name,
                                           dispatch = 'ui' )
                self._object.on_facet_set( self.rebuild_items,
                                        self._name + '_items', dispatch = 'ui' )

            factory.on_facet_set( self.rebuild_items, 'values',
                                  dispatch = 'ui' )
            factory.on_facet_set( self.rebuild_items, 'values_items',
                                  dispatch = 'ui' )

            self.rebuild_items()

        elif droppable:
            self._choice = choice = toolkit().create_text_input(
                                                      parent, read_only = True )
            choice.background_color = self.ok_color
            self.set_tooltip( choice )

        if droppable:
            self._choice.drop_target = self

        is_vertical = OrientationMap[ factory.orientation ]
        if is_vertical is None:
            is_vertical = self.is_vertical

        if choosable and editable:
            layout = toolkit().create_box_layout( is_vertical )
            extra  = self.extra
            layout.add( choice, left = extra, right = extra, top = extra,
                        bottom = extra )
            if is_vertical:
                layout.add( toolkit().create_separator( parent, False ),
                            top = 4, bottom = 4 )

            layout.add( self.create_editor( parent ), stretch = 1 )
            parent.layout = layout
        elif editable:
            self.adapter = self.create_editor( parent )
        else:
            self.adapter = choice

        # Synchronize the 'view' to use:
        # fixme: A normal assignment can cause a crash (for unknown reasons) in
        # some cases, so we make sure that no notifications are generated:
        self.facet_setq( view = factory.view )
        self.sync_value( factory.view_name, 'view', 'from' )


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        # Make sure we aren't hanging on to any object refs:
        self._object_cache = None

        if self._ui is not None:
            self._ui.dispose()

        choice = self._choice
        if choice is not None:
            choice.unset_event_handler( choose = self.update_object )

            if self._object is not None:
                self._object.on_facet_set( self.rebuild_items,
                                           self._name, remove = True )
                self._object.on_facet_set( self.rebuild_items,
                                          self._name + '_items', remove = True )

            self.factory.on_facet_set( self.rebuild_items, 'values',
                                       remove = True )
            self.factory.on_facet_set( self.rebuild_items,
                                       'values_items', remove = True )

        super( CustomEditor, self ).dispose()


    def create_editor ( self, parent ):
        """ Creates the editor control.
        """
        self._panel = toolkit().create_panel( parent )

        return self._panel


    def rebuild_items ( self ):
        """ Rebuilds the object selector list.
        """
        # Clear the current cached values:
        self._items = None

        # Rebuild the contents of the selector list:
        selection = -1
        value     = self.value
        choice    = self._choice
        choice.clear()
        for item in self.items:
            if item.is_selectable():
                item_name = item.get_name()
                index     = choice.add_item( item_name )
                if item.is_compatible( value ):
                    selection = index

        # Reselect the current item if possible:
        if selection is not None:
            choice.selection = selection
        else:
            # Otherwise, current value is no longer valid, try to discard it:
            try:
                self.value = None
            except:
                pass


    def item_for ( self, object ):
        """ Returns the InstanceChoiceItem for a specified object.
        """
        for item in self.items:
            if item.is_compatible( object ):
                return item

        return None


    def view_for ( self, object, item ):
        """ Returns the view to use for a specified object.
        """
        view = ''
        if item is not None:
            view = item.get_view()

        if view == '':
            view = self.view

        return self.ui.handler.facet_view_for( self.ui.info, view, object,
                                               self.object_name, self.name )


    def update_object ( self, event ):
        """ Handles the user selecting a new value from the combo box.
        """
        name = event.value
        for item in self.items:
            if name == item.get_name():
                id_item = id( item )
                object  = self._object_cache.get( id_item )
                if object is None:
                    object = item.get_object()
                    if (not self.factory.editable) and item.is_factory:
                        view = self.view_for( object, self.item_for( object ) )
                        view.ui( object, self.control, 'modal' )

                    if self.factory.cachable:
                        self._object_cache[ id_item ] = object

                self.value = object
                do_later( self.resynch_editor )

                break


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        # Attach the current object value to the control (for use by
        # DockWindowFeature):

        # fixme: This code is somewhat fragile since it assumes that if a
        # DockControl is involved, the parent of this editor will be the
        # control being managed by the DockControl.
        parent         = self.adapter.parent()
        parent._object = self.value
        dock_control   = getattr( parent, '_dock_control', None )
        if dock_control is not None:
            dock_control.reset_tab()

        # Update the selector (if any):
        choice = self._choice
        item   = self.item_for( self.value )
        if (choice is not None) and (item is not None):
            name = item.get_name( self.value )
            if self._object_cache is not None:
                index = choice.find_item( name )
                if index < 0:
                    index = choice.add_item( name )
                choice.selection = index
            else:
                choice.value = name

        # Synchronize the editor contents (if the editor has just been created,
        # as part of creating a new view, do the update immediately to prevent
        # layout problems for the view; otherwise the update has been caused by
        # a user action in the editor or elsewhere, so schedule the update to
        # occur after the current event has completed):
        if self._initialized:
            do_later( self.resynch_editor )
        else:
            self._initialized = True
            self.resynch_editor()


    def resynch_editor ( self ):
        """ Resynchronizes the contents of the editor when the object facet
            changes externally to the editor.
        """
        # To try and reduce the number of double updates caused by a new object
        # and synchronized view name being changed in response to the same
        # event, we check that either the object or its displayed view has been
        # changed before preceding with the update:
        view  = None
        value = self.value
        if isinstance( value, HasFacets ):
            view = self.view_for( value, self.item_for( value ) )

        if (value is self._last_value) and (view is self._last_view):
            return

        self._last_value, self._last_view = value, view
        panel = self._panel
        if panel is not None:
            # Dispose of the previous contents of the panel:
            if self._ui is not None:
                self._ui.dispose()
                self._ui = None
            else:
                panel.destroy_children()

            panel.layout = None

            # Create the new content for the panel:
            stretch = 0
            if not isinstance( value, HasFacets ):
                str_value = ''
                if value is not None:
                    str_value = self.str_value

                control    = toolkit().create_label( panel, str_value )
                is_control = True
            else:
                context = value.facet_context()
                handler = None
                if isinstance( value, Handler ):
                    handler = value

                context.setdefault( 'context', self.object )
                context.setdefault( 'context_handler', self.ui.handler )
                self._ui = ui = view.ui(
                    context, panel, 'editor', value.facet_view_elements(),
                    handler, self.factory.id
                )
                control         = ui.control
                is_control      = ui.is_control
                self.scrollable = ui._scrollable
                ui.parent       = self.ui

                if view.resizable or view.scrollable or ui._scrollable:
                    stretch = 1

            # Add the control to the layout:
            layout = panel.layout
            if is_control:
                if layout is None:
                    layout = toolkit().create_box_layout()
                layout.add( control, stretch = stretch )
            else:
                layout = control

            panel.layout = layout
            panel.update()

            # It is possible that this instance editor is embedded at some level
            # in a ScrolledWindow. If so, we need to inform the window that the
            # size of the editor's contents have (potentially) changed:
            # NB: There is a typo in the wxPython 2.6 code that prevents the
            # 'SendSizeEvent' from working correctly, so we just skip it.

            # fixme: Make this GUI toolkit neutral...
            if False: ###not is_wx26:
                while ((parent is not None) and
                       (not isinstance( parent(), wx.ScrolledWindow ))):
                    parent = parent.parent

                if parent is not None:
                    parent().SendSizeEvent()

            from facets.extra.helper.debug import log_if
            log_if( 2,  panel )


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        pass


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return (self._choice or self.control)

    #-- Private Methods --------------------------------------------------------

    def _get_items ( self ):
        """ Gets the current list of InstanceChoiceItem items.
        """
        if self._items is not None:
            return self._items

        factory = self.factory
        if self._value is not None:
            values = self._value() + factory.values
        else:
            values = factory.values

        items   = []
        adapter = factory.adapter
        for value in values:
            if not isinstance( value, InstanceChoiceItem ):
                value = adapter( object = value )

            items.append( value )

        self._items = items

        return items

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        ui = self._ui
        if (ui is not None) and (prefs.get( 'id' ) == ui.id):
            ui.set_prefs( prefs.get( 'prefs' ) )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        ui = self._ui
        if (ui is not None) and (ui.id != ''):
            return { 'id':    ui.id,
                     'prefs': ui.get_prefs() }

        return None

    #-- Drag and drop Event Handlers -------------------------------------------

    def drag_drop ( self, event ):
        """ Handles a Python object being dropped on the editor.
        """
        if event.has_object:
            data = event.object
            for item in self.items:
                if item.is_droppable() and item.is_compatible( data ):
                    if self._object_cache is not None:
                        self.rebuild_items()

                    self.value = data

                    event.result = event.request

                    return

        event.result = 'ignore'


    def drag_move ( self, event ):
        """ Handles a Python object being dragged over the editor.
        """
        if event.has_object:
            data = event.object
            for item in self.items:
                if item.is_droppable() and item.is_compatible( data ):
                    event.result = event.request

                    return

        event.result = 'ignore'

    #-- Facet Event Handlers ---------------------------------------------------

    def _view_set ( self ):
        do_later( self.resynch_editor )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( CustomEditor ):
    """ Simple style of editor for instances, which displays a button. Clicking
        the button displays a dialog box in which the instance can be edited.
    """

    #-- Class Constants --------------------------------------------------------

    # Is the orientation of the instance editor relative to the instance
    # selector vertical?
    is_vertical = False

    # Extra padding around control:
    extra = 2

    #-- Public Methods ---------------------------------------------------------

    def create_editor ( self, parent ):
        """ Creates the editor control (a button).
        """
        self._button = button = toolkit().create_button( parent )
        button.set_event_handler( clicked = self.edit_instance )

        return button


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self._button is not None:
            self._button.unset_event_handler( clicked = self.edit_instance )

        super( SimpleEditor, self ).dispose()


    def edit_instance ( self, event ):
        """ Edit the contents of the object facet when the user clicks the
            button.
        """
        # Create the user interface:
        factory = self.factory
        view    = self.ui.handler.facet_view_for( self.ui.info, factory.view,
                                                  self.value, self.object_name,
                                                  self.name )
        ui      = self.value.edit_facets( view, self.adapter, factory.kind,
                                          id = factory.id )

        # Check to see if the view was 'modal', in which case it will already
        # have been closed (i.e. is None) by the time we get control back:
        if ui.control is not None:
            # Chain our undo history to the new user interface if it does not
            # have its own:
            if ui.history is None:
                ui.history = self.ui.history


    def resynch_editor ( self ):
        """ Resynchronizes the contents of the editor when the object facet
            changes externally to the editor.
        """
        button = self._button
        if button is not None:
            label = self.factory.label
            if label == '':
                label = user_name_for( self.name )

            button.value   = label
            button.enabled = isinstance( self.value, HasFacets )

#-- EOF ------------------------------------------------------------------------