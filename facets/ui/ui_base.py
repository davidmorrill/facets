"""
Defines the base class for the GUI toolkit neutral Facets UI modal and non-modal
dialogs, windows and panels.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasStrictFacets, Instance, List, Editor

from facets.core.facet_base \
    import invoke

from facets.ui.menu \
    import Action

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# List of all predefined system button names:
SystemButtons = [ 'Undo', 'Redo', 'Apply', 'Revert', 'OK', 'Cancel', 'Help' ]

# List of alternative context items that might handle an Action 'perform':
PerformHandlers = ( 'object', 'model' )

#-------------------------------------------------------------------------------
#  'RadioGroup' class:
#-------------------------------------------------------------------------------

class RadioGroup ( HasStrictFacets ):
    """ A group of mutually-exclusive menu or toolbar actions.
    """

    #-- Facet Definitions ------------------------------------------------------

    # List of menu or tool bar items
    items = List

    #-- Public Methods ---------------------------------------------------------

    def menu_checked ( self, menu_item ):
        """ Handles a menu item in the group being checked.
        """
        for item in self.items:
            if item is not menu_item:
                item.control.checked     = False
                item.item.action.checked = False


    def toolbar_checked ( self, toolbar_item ):
        """ Handles a tool bar item in the group being checked.
        """
        for item in self.items:
            if item is not toolbar_item:
                # fixme: Make GUI toolkit neutral...
                item.tool_bar.ToggleTool( item.control_id, False )
                item.item.action.checked = False

#-------------------------------------------------------------------------------
#  'ViewButtonEditor' class:
#-------------------------------------------------------------------------------

class ViewButtonEditor ( Editor ):
    """ An Editor for buttons displayed as part of a View's definition.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Action associated with the button
    action = Instance( Action )

    #-- Public Methods ---------------------------------------------------------

    def perform ( self, event ):
        """ Handles the associated button being clicked.
        """
        self.ui.do_undoable( self._perform, event )

    def _perform ( self, event ):
        method_name = self.action.action
        if method_name == '':
            method_name = '_%s_clicked' % ( self.action.name.lower() )

        method = getattr( self.ui.handler, method_name, None )
        if method is not None:
            method( self.ui.info )
        else:
            self.action.perform( event )

#-------------------------------------------------------------------------------
#  'BasePanel' class:
#-------------------------------------------------------------------------------

class BasePanel ( object ):
    """ Base class for Facets UI panels.
    """

    #-- Public Methods ---------------------------------------------------------

    def perform ( self, action, action_event ):
        """ Performs the action described by a specified Action object.
        """
        self.ui.do_undoable( self._perform, action, action_event )


    def _perform ( self, action, action_event ):
        """ Locates and invokes the action handler for the specified *action*,
            passing in the optional *action_event* if requested.
        """
        the_action = action.action
        method     = getattr( self.ui.handler, the_action, None )
        if method is not None:
            invoke( method, self.ui.info )
        else:
            context = self.ui.context
            for item in PerformHandlers:
                handler = context.get( item, None )
                if handler is not None:
                    method = getattr( handler, the_action, None )
                    if method is not None:
                        break
            else:
                method = getattr( self, the_action, action.perform )

            invoke( method, action_event )


    def get_buttons ( self, view ):
        """ Returns the set of valid buttons for the specified view.
        """
        buttons = [ self.coerce_button( button ) for button in view.buttons ]

        # If undo not supported, filter out any invalid buttons:
        if not view.undo:
            buttons = [ button for button in buttons
                        if not self.is_button( button, ( 'Undo', 'Revert' ) ) ]

        return buttons


    def check_button ( self, buttons, action ):
        """ Adds *action* to the system buttons list for this dialog, if it is
            not already in the list.
        """
        name = action.name
        for button in buttons:
            if self.is_button( button, name ):
                return

        buttons.append( action )


    def is_button ( self, action, name ):
        """ Returns whether a specified action button is a system button.
        """
        if not isinstance( action, basestring ):
            action = action.name

        if isinstance( name, basestring ):
            return (action == name)

        return (action in name)


    def coerce_button ( self, action ):
        """ Coerces a string to an Action if necessary.
        """
        if isinstance( action, basestring ):
            return Action( name   = action,
                           action = '?'[ ( not action in SystemButtons ): ] )

        return action


    def add_button ( self, action, layout, method  = None, enabled = True,
                           name = None ):
        """ Creates a user specified button.
        """
        ui = self.ui
        if ((action.defined_when != '') and
            (not ui.eval_when( action.defined_when ))):
            return None

        if name is None:
            name = action.name

        id     = action.id
        button = toolkit().create_button( self.control, name )
        button.enabled = enabled
        if (method is None) or (action.enabled_when != '') or (id != ''):
            editor = ViewButtonEditor( ui      = ui,
                                       action  = action,
                                       adapter = button )
            if id != '':
                ui.info.bind( id, editor )

            if action.visible_when != '':
                ui.add_visible( action.visible_when, editor )

            if action.enabled_when != '':
                ui.add_enabled( action.enabled_when, editor )

            if method is None:
                method = editor.perform

        button.set_event_handler( clicked = method )
        layout.add( button, fill = False, left = 5 )
        if action.tooltip != '':
            button.tooltip = action.tooltip

        return button


    def add_toolbar ( self, layout ):
        """ Adds an optional toolbar to the dialog.
        """
        toolbar = self.ui.view.toolbar
        if toolbar is not None:
            self._last_group = self._last_parent = None
            # fixme: Is this GUI toolkit neutral?...
            layout.add( toolbar.create_tool_bar( self.control, self ) )
            self._last_group = self._last_parent = None


    def _on_help ( self, event ):
        """ Handles the **Help** button being clicked.
        """
        # fixme: Make GUI toolkit neutral...
        self.ui.handler.show_help( self.ui.info, event.GetEventObject() )


    def _on_undo ( self, event ):
        """ Handles a request to undo a change.
        """
        self.ui.history.undo()


    def _on_undoable ( self, state ):
        """ Handles a change to the "undoable" state of the undo history.
        """
        self.undo.enabled = state


    def _on_redo ( self, event ):
        """ Handles a request to redo a change.
        """
        self.ui.history.redo()


    def _on_redoable ( self, state ):
        """ Handles a change to the "redoable" state of the undo history.
        """
        self.redo.enabled = state


    def _on_revert ( self, event ):
        """ Handles a request to revert all changes.
        """
        ui = self.ui
        if ui.history is not None:
            ui.history.revert()

        ui.handler.revert( ui.info )


    def _on_revertable ( self, state ):
        """ Handles a change to the "revert" state.
        """
        self.revert.enabled = state


    def _on_manage_layouts ( self ):
        """ Manages the layouts for the current window.
        """
        self.ui.dock_window.manage_layouts()


    def _on_select_theme ( self ):
        """ Select the DockWindow theme to use.
        """
        self.ui.dock_window.select_theme()


    def _on_save_preferences ( self ):
        """ Saves the current user preferences to the application data base (as
            a means of setting factory defaults).
        """
        self.ui.save_prefs( path = '$' )

#-------------------------------------------------------------------------------
#  'BaseDialog' class:
#-------------------------------------------------------------------------------

class BaseDialog ( BasePanel ):
    """ Base class for Facets UI dialog boxes.
    """

    #-- Public Methods ---------------------------------------------------------

    def set_icon ( self, icon = None ):
        """ Sets the frame's icon.
        """
        from facets.ui.ui_facets               import image_for
        from facets.ui.pyface.i_image_resource import AnImageResource

        if isinstance( icon, basestring ):
            icon = image_for( icon )

        if not isinstance( icon, AnImageResource ):
            icon = image_for( '@facets:frame.ico' )

        self.control.icon = icon.create_icon()


    # fixme: Make GUI toolkit neutral...
    def add_statusbar ( self ):
        """ Adds a status bar to the dialog.
        """
        ui        = self.ui
        statusbar = ui.view.statusbar
        context   = ui.context
        if statusbar is not None:
            widths    = []
            listeners = []
            control   = wx.StatusBar( self.control )
            control.SetFieldsCount( len( statusbar ) )
            for i, item in enumerate( statusbar ):
                width = abs( item.width )
                if width <= 1.0:
                    widths.append( -max( 1, int( 1000 * width ) ) )
                else:
                    widths.append( int( width ) )

                set_text = self._set_status_text( control, i )
                name     = item.name
                set_text( ui.get_extended_value( name ) )
                col    = name.find( '.' )
                object = 'object'
                if col >= 0:
                    object = name[ : col ]
                    name   = name[ col + 1: ]

                object = context[ object ]
                object.on_facet_set( set_text, name, dispatch = 'ui' )
                listeners.append( ( object, set_text, name ) )

            control.SetStatusWidths( widths )
            self.control.SetStatusBar( control )
            ui._statusbar = listeners

    # fixme: Make GUI toolkit neutral...
    def _set_status_text ( self, control, i ):
        def set_status_text ( text ):
            control.SetStatusText( text, i )

        return set_status_text


    def add_menubar ( self ):
        """ Adds a menu bar to the dialog.
        """
        menubar = self.ui.view.menubar
        if menubar is not None:
            self._last_group = self._last_parent = None
            self.control.menubar = menubar.create_menu_bar( self.control(),
                                                            self )
            self._last_group = self._last_parent = None


    def add_toolbar ( self ):
        """ Adds a toolbar to the dialog.
        """
        toolbar = self.ui.view.toolbar
        if toolbar is not None:
            self._last_group = self._last_parent = None
            self.control.toolbar = toolbar.create_tool_bar( self.control(),
                                                            self )
            self._last_group = self._last_parent = None


    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        item   = menu_item.item
        action = item.action

        if action.id != '':
            self.ui.info.bind( action.id, menu_item )

        if action.style == 'radio':
            if ((self._last_group is None) or
                (self._last_parent is not item.parent)):
                self._last_group = RadioGroup()
                self._last_parent = item.parent

            self._last_group.items.append( menu_item )
            menu_item.group = self._last_group

        if action.enabled_when != '':
            self.ui.add_enabled( action.enabled_when, menu_item )

        if action.checked_when != '':
            self.ui.add_checked( action.checked_when, menu_item )


    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the toolbar being constructed.
        """
        self.add_to_menu( toolbar_item )


    def can_add_to_menu ( self, action, action_event = None ):
        """ Returns whether the action should be defined in the user interface.
        """
        if action.defined_when == '':
            return True

        return self.ui.eval_when( action.defined_when )


    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return self.can_add_to_menu( action )

#-- EOF ------------------------------------------------------------------------