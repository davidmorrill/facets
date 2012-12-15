"""
Defines the GUI toolkit neutral notebook editor and the notebook editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, Bool, Str, List, Callable, Enum, Event, Any, Range, \
           Editor, BasicEditorFactory, on_facet_set

from facets.core.facet_base \
    import user_name_for, xgetattr

from facets.ui.ui_facets \
    import AView

from facets.ui.dock.api \
    import DockWindow, DockSizer, DockSection, DockRegion, DockControl

from facets.ui.dock.dock_window_theme \
    import DockWindowTheme

from facets.ui.dock.dockable_view_element \
    import DockableViewElement

from facets.extra.features.layout_feature \
    import LayoutFeature

#-------------------------------------------------------------------------------
#  '_NotebookEditor' class:
#-------------------------------------------------------------------------------

class _NotebookEditor ( Editor ):
    """ An editor for lists that displays the list as a "notebook" of tabbed
        pages.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the notebook editor scrollable? This values overrides the default:
    scrollable = True

    # The currently selected notebook page object:
    selected = Any

    # The most recently specified notebook layout template:
    template = Event

    # The view to use for displaying the instance:
    view = AView

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._uis = []

        # Create a DockWindow to hold each separate object's view:
        ui      = self.ui
        factory = self.factory
        theme   = factory.dock_theme or self.item.container.dock_theme
        id      = ''
        if (ui.id != '') and (self.item.id != ''):
            id = '%s[%s]' % ( ui.id, self.item.id )

        self._dock_window = dw = DockWindow( parent,
            theme    = theme,
            id       = id,
            max_tabs = (factory.layout != 'tabs') * (not factory.allow_tabs)
        )
        if ui.dock_window is None:
            ui.dock_window = dw

        self.adapter = dw.control
        if len( factory.features ) > 0:
            dw.add_feature( LayoutFeature )

        for feature in factory.features:
            dw.add_feature( feature )

        dw.dock_sizer = DockSizer(
            DockSection( dock_window = dw,
                         is_row      = (factory.layout == 'columns') )
        )

        # Set up the additional 'list items changed' event handler needed for
        # a list based facet:
        self.context_object.on_facet_set(
            self.update_editor_item, self.extended_name + '_items?',
            dispatch = 'ui'
        )

        # Set up layout template synchronization:
        self.sync_value( factory.template, 'template', 'from' )

        # Do the editor update now, so the initial selection (if any), will
        # work correctly:
        self.update_editor()

        # Since update is already done, make a note to skip the next update:
        self._skip_update = True

        # Set up selection synchronization:
        self.sync_value( factory.selected, 'selected' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        # If this is first post-init update, skip it (see comment in 'init'):
        if self._skip_update:
            del self._skip_update

            return

        # Make sure the DockWindow is in a correct state:
        self._dock_window.dock_sizer.reset( self.control )

        # Destroy the views on each current notebook page:
        self.close_all()

        # Create a DockControl for each object in the facet's value:
        uis           = self._uis
        dock_controls = []
        for object in self.value:
            dock_control, view_object, monitoring = self._create_page( object )

            # Remember the DockControl for later deletion processing:
            uis.append( [ dock_control, object, view_object, monitoring ] )

            dock_controls.append( dock_control )

        # Add the new items to the DockWindow:
        self.add_controls( dock_controls )

        # Make sure each DockControl has the correct style set:
        self._set_style()

        # Apply the most recent template (if any):
        if self._cached_template is not None:
            self._dock_window.update_layout( self._cached_template )

        # Otherwise, automatically lay out the notebook's contents if we are in
        # "no tabs" mode or are using row/column layout:
        elif ((not self.factory.layout == 'tabs') or
              (not self.factory.allow_tabs)):
            self._dock_window.auto_layout()


    def update_editor_item ( self, event ):
        """ Handles an update to some subset of the facet's list.
        """
        # Make sure the DockWindow is in a correct state:
        self._dock_window.dock_sizer.reset( self.control )

        index = event.index

        # Delete the page corresponding to each removed item:
        layout = ((len( event.removed ) + len( event.added )) <= 1)
        for i in event.removed:
            dock_control, object, view_object, monitoring = self._uis[ index ]
            if monitoring:
                view_object.on_facet_set(
                    self.update_page_name, self.factory.page_name[1:],
                    remove = True
                )

            dock_control.close( layout = layout, force = True )
            del self._uis[ index ]

        # Add a page for each added object:
        dock_controls = []
        for object in event.added:
            dock_control, view_object, monitoring  = self._create_page( object )
            self._uis[ index: index ] = [ [ dock_control, object, view_object,
                                            monitoring ] ]
            dock_controls.append( dock_control )
            index += 1

        # Add the new items to the DockWindow:
        n = len( dock_controls )
        if n > 0:
            self.add_controls( dock_controls )
            dock_controls[0].activate( layout = False )

        # Update the style information for each DockControl:
        self._set_style()

        # Automatically lay out the notebook's contents if any items were just
        # added and we are in "no tabs" mode:
        if (n > 0) and (not self.factory.allow_tabs):
            self._dock_window.auto_layout()


    def close_all ( self ):
        """ Closes all currently open notebook pages.
        """
        page_name = self.factory.page_name[1:]
        for dock_control, object, view_object, monitoring in self._uis:
            if monitoring:
                view_object.on_facet_set( self.update_page_name, page_name,
                                          remove = True )

            dock_control.close( layout = False, force = True )

        # Reset the list of ui's and dictionary of page name counts:
        self._uis   = []
        self._pages = {}


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_facet_set(
            self.update_editor_item, self.extended_name + '_items?',
            remove = True
        )
        self.close_all()
        self._dock_window.close()

        super( _NotebookEditor, self ).dispose()


    def add_controls ( self, controls ):
        """ Adds a group of new DockControls to the view.
        """
        if len( controls ) > 0:
            sizer   = self._dock_window.dock_sizer
            handler = getattr( self, 'add_' + self.factory.layout )
            for control in controls:
                handler( sizer, control )


    def add_tabs ( self, sizer, control ):
        """ Add the DockControl *control* to the DockSizer *sizer* as a new tab.
        """
        max_items = self.factory.max_items
        section   = sizer.contents
        contents  = section.contents
        for i in xrange( len( contents ) - 1, -1, -1 ):
            item = contents[ i ]
            if (isinstance( item, DockRegion ) and
                ((max_items == 0) or (max_items > len( item.contents )))):
                item.contents.append( control )

                break
        else:
            contents.append(
                DockRegion( contents = [ control ] )
            )


    def add_rows ( self, sizer, control ):
        """ Add the DockControl *control* to the DockSizer *sizer* as a new row.
        """
        self.add_row_column( sizer, control, False )


    def add_columns ( self, sizer, control ):
        """ Add the DockControl *control* to the DockSizer *sizer* as a new
            column.
        """
        self.add_row_column( sizer, control, True )


    def add_row_column ( self, sizer, control, is_row ):
        """ Adds the DockControl *control* to the DockSizer *sizer* as a new
            row (if *is_row* is True) or column (if *is_row* is False).
        """
        control   = DockRegion( contents = [ control ] )
        max_items = self.factory.max_items
        section   = sizer.contents
        if section.is_row == is_row:
            if (max_items == 0) or (max_items > len( section.contents )):
                section.contents.append( control )
            else:
                parent = section.parent
                if parent is None:
                    section.dock_window = None
                    sizer.contents = parent = DockSection(
                        is_row      = not is_row ).set(
                        contents    = [ section ],
                        dock_window = self._dock_window
                    )

                parent.contents.append(
                    DockSection( is_row = is_row, contents = [ control ] )
                )
        else:
            contents = section.contents
            for i in xrange( len( contents ) - 1, -1, -1 ):
                item = contents[ i ]
                if (isinstance( item, DockSection ) and
                    ((max_items == 0) or (max_items > len( item.contents )))):
                    item.contents.append( control )

                    break
            else:
                contents.append(
                    DockSection( is_row = is_row, contents = [ control ] )
                )


    def update_page_name ( self ):
        """ Handles the facet defining a particular page's name being changed.
        """
        changed = False
        for i, value in enumerate( self._uis ):
            dock_control, user_object, view_object, monitoring = value
            if dock_control.control is not None:
                name    = None
                handler = getattr( self.ui.handler, '%s_%s_page_name' %
                                   ( self.object_name, self.name ), None )
                if handler is not None:
                    name = handler( self.ui.info, user_object )

                if name is None:
                    name = str( xgetattr( view_object,
                                          self.factory.page_name[1:], '???' ) )

                changed |= ( dock_control.name != name )
                dock_control.name = name

        if changed:
            self.adapter.update()

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        dw    = self._dock_window
        sizer = dw.dock_sizer
        sizer.max_structure = prefs.get( 'max_structure' )
        sizer.set_structure( dw, prefs.get( 'structure' ) )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        sizer = self._dock_window.dock_sizer

        return {
            'structure':     sizer.get_structure(),
            'max_structure': sizer.max_structure
        }

    #-- Private Methods --------------------------------------------------------

    def _create_page ( self, object ):
        """ Creates a DockControl for a specified object.
        """
        # Create the view for the object:
        view_object = object
        factory     = self.factory
        if factory.factory is not None:
            view_object = factory.factory( object )

        self.facet_setq( view = factory.view )
        self.sync_value( factory.view_name, 'view', 'from' )
        ui = view_object.edit_facets(
            parent = self.control,
            view   = self.view,
            kind   = factory.ui_kind
        ).set(
            parent = self.ui
        )

        # Get the name of the page being added to the notebook:
        name       = ''
        monitoring = False
        prefix     = '%s_%s_page_' % ( self.object_name, self.name )
        page_name  = self.factory.page_name
        if page_name[:1] == '.':
            name       = xgetattr( view_object, page_name[1:], None )
            monitoring = (name is not None)
            if monitoring:
                handler_name = None
                method       = getattr( self.ui.handler, prefix + 'name', None )
                if method is not None:
                    handler_name = method( self.ui.info, object )

                if handler_name is not None:
                    name = handler_name
                else:
                    name = str( name ) or '???'

                view_object.on_facet_set(
                    self.update_page_name, page_name[1:], dispatch = 'ui'
                )
            else:
                name = ''
        elif page_name != '':
            name = page_name

        if name == '':
            name = user_name_for( view_object.__class__.__name__ )

        # Make sure the name is not a duplicate:
        if not monitoring:
            self._pages[ name ] = count = self._pages.get( name, 0 ) + 1
            if count > 1:
                name += (' %d' % count)

        # Return a new DockControl for the ui, and whether or not its name is
        # being monitored:
        image   = None
        method  = getattr( self.ui.handler, prefix + 'image', None )
        if method is not None:
            image = method( self.ui.info, object )

        dock_control = DockControl(
            max_tab_length = ( 256, 30 )[ factory.allow_tabs ] ).set(
            control        = ui.control,
            id             = name,
            name           = name,
            image          = image,
            export         = factory.export,
            closeable      = factory.deletable,
            dockable       = DockableListElement( ui = ui, editor = self )
        )
        self.set_dock_control_listener( dock_control )

        return ( dock_control, view_object, monitoring )


    def _set_style ( self ):
        """ Updates the 'style' and 'resizable' attributes of each DockControl
            in the DockWindow.
        """
        style = self.factory.dock_style
        if style == 'auto':
            if len( self.value ) == 1:
                style = 'fixed'
            else:
                style = 'tab'

        resizable = (style != 'locked')
        if not resizable:
            style = 'fixed'

        for control in self._dock_window.dock_sizer.get_controls( False ):
            control.style     = style
            control.resizable = resizable

        if self.ui.info.initialized:
            self.adapter.update()


    def set_dock_control_listener ( self, dock_control, remove = False ):
        """ Sets or removes the listener for a DockControl being activated.
        """
        dock_control.on_facet_set(
            self._tab_activated, 'activated', remove = remove, dispatch = 'ui'
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _tab_activated ( self, object ):
        """ Handles a notebook tab being "activated" (i.e. clicked on) by the
            user.
        """
        for dock_control, value, view_object, monitoring in self._uis:
            if object is dock_control:
                self.selected = value

                break


    def _selected_set ( self, selected ):
        """ Handles the **selected** facet being changed.
        """
        for dock_control, object, view_object, monitoring in self._uis:
            if selected is object:
                dock_control.select()

                break


    def _template_set ( self, template ):
        """ Handles the 'template' facet being changed.
        """
        self._cached_template = template
        if template is not None:
            self._dock_window.update_layout( template )


    @on_facet_set( 'factory:dock_style' )
    def _factory_dock_style_modified ( self ):
        """ Handles the factory 'dock_style' facet being changed.
        """
        self._set_style()

#-------------------------------------------------------------------------------
#  'DockableListElement' class:
#-------------------------------------------------------------------------------

class DockableListElement ( DockableViewElement ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor this dockable item is associated with:
    editor = Instance( _NotebookEditor )

    #-- Public Methods ---------------------------------------------------------

    def dockable_close ( self, dock_control, force ):
        """ Returns whether it is OK to close the control.
        """
        return self.close_dock_control( dock_control, force )


    def close_dock_control ( self, dock_control, abort ):
        """ Closes a DockControl.
        """
        if abort:
            self.editor.set_dock_control_listener( dock_control, remove = True )

            return super( DockableListElement, self ).close_dock_control(
                                                           dock_control, False )

        view_object = self.ui.context[ 'object' ]
        for i, value in enumerate( self.editor._uis ):
            if view_object is value[2]:
                value[0] = dock_control
                del self.editor.value[ i ]

                break

        return False

#-------------------------------------------------------------------------------
#  'NotebookEditor' class:
#-------------------------------------------------------------------------------

class NotebookEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _NotebookEditor

    # Are notebook items deletable?
    deletable = Bool( False )

    # The DockWindow graphical theme:
    dock_theme = Instance( DockWindowTheme )

    # Dock page style to use for each DockControl item:
    dock_style =  Enum( 'tab', 'horizontal', 'vertical', 'fixed', 'locked',
                        'auto', facet_value = True )

    # The type of DockWindow layout scheme to use:
    # - 'tabs':    Use a series of notebook tabs (default).
    # - 'rows':    Use a grid from a series of vertically split rows.
    # - 'columns': Use a grid from a series of horizontally split columns.
    layout = Enum( 'tabs', 'rows', 'columns' )

    # The maximum number of notebook items to allow before creating a new
    # DockWindow 'container' (e.g. in 'rows' mode, a new column is added to the
    # grid when the number of rows in the current column reaches the limit
    # specified). A value of 0 means there is no limit.
    max_items = Range( 0, 25 )

    # Should the user be able to create a tab group by dragging (only applies if
    # the 'layout' style is not 'tabs')?
    allow_tabs = Bool( True )

    # Export class for each notebook item:
    export = Str

    # Name of the view to use for each notebook page:
    view = AView

    # The type of UI to construct ('panel', 'subpanel', etc)
    ui_kind = Enum( 'editor', 'subpanel', 'panel' )

    # A factory function that can be used to define the actual object to be
    # edited (i.e. view_object = factory( object )):
    factory = Callable

    # Extended name to use for each notebook page. It can be either the actual
    # name or the name of an attribute on the object in the form:
    # '.name[.name...]'
    page_name = Str

    # Name of the [object.]facet[.facet...] to synchronize notebook page
    # selection with:
    selected = Str

    # Extended name of the context object facet containing the view, or name of
    # the view, to use:
    view_name = Str

    # Extended name of the context object facet containing the layout template
    # to apply to the current notebook contents:
    template = Str

    # The list of DockWindowfeature classes to use with the DockWindow:
    features = List # ( DockWindowFeature subclass )

#-- EOF ------------------------------------------------------------------------