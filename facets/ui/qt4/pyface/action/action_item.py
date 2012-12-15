"""
The PyQt specific implementations the action manager internal classes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from inspect \
    import getargspec

from PyQt4.QtGui \
    import QActionGroup

from facets.core_api \
    import Any, Bool, HasFacets

from facets.ui.pyface.action.action_event \
    import ActionEvent

#-------------------------------------------------------------------------------
#  '_MenuItem' class:
#-------------------------------------------------------------------------------

class _MenuItem ( HasFacets ):
    """ A menu item representation of an action item.
    """

    #-- '_MenuItem' interface --------------------------------------------------

    # Is the item checked?
    checked = Bool( False )

    # The controller object we delegate taking actions through (if any):
    controller = Any

    # Is the item enabled?
    enabled = Bool( True )

    # Is the item visible?
    visible = Bool( True )

    # The radio group we are part of (None if the menu item is not part of such
    # a group):
    group = Any

    #-- object Interface -------------------------------------------------------

    def __init__ ( self, parent, menu, item, controller ):
        """ Creates a new menu item for an action item.
        """
        self.item = item
        action    = item.action

        # FIXME v3: This is a wx'ism and should be hidden in the toolkit code:
        self.control_id = None

        if action.image is None:
            control = menu.addAction(
                action.name, self._qt4_on_triggered, action.accelerator
            )
        else:
            control = menu.addAction(
                action.image.create_icon(), action.name, self._qt4_on_triggered,
                action.accelerator
            )

        self.control = control
        control.setToolTip(   action.tooltip )
        control.setWhatsThis( action.description )
        control.setEnabled(   action.enabled )
        control.setVisible(   action.visible )

        if action.style == 'toggle':
            control.setCheckable( True )
            control.setChecked( action.checked )

        elif action.style == 'radio':
            # Create an action group if it hasn't already been done:
            try:
                ag = item.parent._qt4_ag
            except AttributeError:
                ag = item.parent._qt4_ag = QActionGroup( parent )

            control.setActionGroup( ag )
            control.setCheckable( True )
            control.setChecked( action.checked )

        # Listen for facet changes on the action (so that we can update its
        # enabled/disabled/checked state etc):
        action.on_facet_set( self._on_action_enabled_modified, 'enabled' )
        action.on_facet_set( self._on_action_visible_modified, 'visible' )
        action.on_facet_set( self._on_action_checked_modified, 'checked' )
        action.on_facet_set( self._on_action_name_modified,    'name'    )

        if controller is not None:
            self.controller = controller
            controller.add_to_menu( self )

    #-- Private Methods --------------------------------------------------------

    def _qt4_on_triggered ( self ):
        """ Called when the menu item has been clicked.
        """
        action       = self.item.action
        action_event = ActionEvent()
        is_checkable = action.style in [ 'radio', 'toggle' ]

        # Perform the action!
        if self.controller is not None:
            if is_checkable:
                # fixme: There is a difference here between having a controller
                # and not in that in this case we do not set the checked state
                # of the action! This is confusing if you start off without a
                # controller and then set one as the action now behaves
                # differently!
                self.checked = self.control.isChecked()

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it. This is also
            # useful as Facets UI controllers *never* require the event.
            args, varargs, varkw, dflts = getargspec( self.controller.perform )

            # If the only arguments are 'self' and 'action' then don't pass
            # the event!
            if len( args ) == 2:
                self.controller.perform( action )

            else:
                self.controller.perform( action, action_event )

        else:
            if is_checkable:
                action.checked = self.control.isChecked()

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it.
            args, varargs, varkw, dflts = getargspec( action.perform )

            # If the only argument is 'self' then don't pass the event:
            if len( args ) == 1:
                action.perform()
            else:
                action.perform( action_event )

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self ):
        """ Called when our 'enabled' facet is changed.
        """
        self.control.setEnabled( self.enabled )


    def _visible_set ( self ):
        """ Called when our 'visible' facet is changed.
        """
        self.control.setVisible( self.visible )


    def _checked_set ( self ):
        """ Called when our 'checked' facet is changed.
        """
        self.control.setChecked( self.checked )


    def _on_action_enabled_modified ( self, object ):
        """ Called when the enabled facet is changed on an action.
        """
        self.control.setEnabled( object.enabled )


    def _on_action_visible_modified ( self, object ):
        """ Called when the visible facet is changed on an action.
        """
        self.control.setVisible( object.visible )


    def _on_action_checked_modified ( self, object ):
        """ Called when the checked facet is changed on an action.
        """
        self.control.setChecked( object.checked )


    def _on_action_name_modified ( self, object ):
        """ Called when the name facet is changed on an action.
        """
        self.control.setText( object.name )

#-------------------------------------------------------------------------------
#  '_Tool' class:
#-------------------------------------------------------------------------------

class _Tool ( HasFacets ):
    """ A tool bar tool representation of an action item.
    """

    #-- '_Tool' interface ------------------------------------------------------

    # Is the item checked?
    checked = Bool( False )

    # A controller object we delegate taking actions through (if any).
    controller = Any

    # Is the item enabled?
    enabled = Bool( True )

    # Is the item visible?
    visible = Bool( True )

    # The radio group we are part of (None if the tool is not part of such a
    # group).
    group = Any

    #-- object Interface -------------------------------------------------------

    def __init__ ( self, parent, tool_bar, image_cache, item, controller,
                         show_labels ):
        """ Creates a new tool bar tool for an action item.
        """
        self.item     = item
        self.tool_bar = tool_bar
        action        = item.action

        # FIXME v3: This is a wx'ism and should be hidden in the toolkit code:
        self.control_id = None

        if action.image is None:
            control = tool_bar.addAction( action.name, self._qt4_on_triggered )
        else:
            control = tool_bar.addAction(
                action.image.create_icon(), action.name, self._qt4_on_triggered
            )

        self.control = control
        control.setToolTip(   action.tooltip )
        control.setWhatsThis( action.description )
        control.setEnabled(   action.enabled )
        control.setVisible(   action.visible )

        if action.style == 'toggle':
            control.setCheckable( True )
            control.setChecked( action.checked )
        elif action.style == 'radio':
            # Create an action group if it hasn't already been done:
            try:
                ag = item.parent._qt4_ag
            except AttributeError:
                ag = item.parent._qt4_ag = QActionGroup( parent )

            control.setActionGroup( ag )

            control.setCheckable( True )
            control.setChecked( action.checked )

        # Keep a reference in the action.  This is done to make sure we live as
        # long as the action (and still respond to its signals) and don't die
        # if the manager that created us is garbage collected:
        control._tool_instance = self

        # Listen for facet changes on the action (so that we can update its
        # corresponding Qt object state):
        action.on_facet_set( self._on_action_enabled_modified, 'enabled' )
        action.on_facet_set( self._on_action_visible_modified, 'visible' )
        action.on_facet_set( self._on_action_checked_modified, 'checked' )
        action.on_facet_set( self._on_action_tooltip_changed,  'tooltip' )
        action.on_facet_set( self._on_action_name_changed,     'name'    )

        if controller is not None:
            self.controller = controller
            controller.add_to_toolbar( self )

    #-- Private Methods --------------------------------------------------------

    def _qt4_on_triggered ( self ):
        """ Called when the tool bar tool is clicked.
        """
        action       = self.item.action
        action_event = ActionEvent()

        # Perform the action!
        if self.controller is not None:
            # fixme: There is a difference here between having a controller
            # and not in that in this case we do not set the checked state
            # of the action! This is confusing if you start off without a
            # controller and then set one as the action now behaves
            # differently!
            self.checked = self.control.isChecked()

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it. This is also
            # useful as Facets UI controllers *never* require the event.
            args, varargs, varkw, dflts = getargspec( self.controller.perform )

            # If the only arguments are 'self' and 'action' then don't pass
            # the event!
            if len( args ) == 2:
                self.controller.perform( action )

            else:
                self.controller.perform( action, action_event )

        else:
            action.checked = self.control.isChecked()

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it.
            args, varargs, varkw, dflts = getargspec( action.perform )

            # If the only argument is 'self' then don't pass the event:
            if len( args ) == 1:
                action.perform()
            else:
                action.perform( action_event )

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self ):
        """ Handles the 'enabled' facet being changed.
        """
        self.control.setEnabled( self.enabled )


    def _visible_set ( self ):
        """ Handles the 'visible' facet being changed.
        """
        self.control.setVisible( self.visible )


    def _checked_set ( self ):
        """ Handles the 'checked' facet being changed.
        """
        self.control.setChecked( self.checked )


    def _on_action_enabled_modified ( self, action, facet_name, old, new ):
        """ Called when the 'enabled' facet is changed on an action.
        """
        self.control.setEnabled( action.enabled )


    def _on_action_visible_modified ( self, action, facet_name, old, new ):
        """ Called when the 'visible' facet is changed on an action.
        """
        self.control.setVisible( action.visible )


    def _on_action_checked_modified ( self, action, facet_name, old, new ):
        """ Called when the 'checked' facet is changed on an action.
        """
        self.control.setChecked( action.checked )


    def _on_action_tooltip_changed ( self, action, facet_name, old, new ):
        """ Called when the 'tooltip' facet is changed on an action.
        """
        self.control.setToolTip( action.tooltip )


    def _on_action_name_changed ( self, action, facet_name, old, new ):
        """ Called when the 'name' facet is changed on an action.
        """
        self.control.setText( action.name )

#-------------------------------------------------------------------------------
#  '_PaletteTool' class:
#-------------------------------------------------------------------------------

class _PaletteTool ( HasFacets ):
    """ A tool palette representation of an action item.
    """

    #-- '_PaletteTool' interface -----------------------------------------------

    # The radio group we are part of (None if the tool is not part of such a
    # group).
    group = Any

    #-- object Interface -------------------------------------------------------

    def __init__ ( self, tool_palette, image_cache, item, show_labels ):
        """ Creates a new tool palette tool for an action item.
        """
        self.item         = item
        self.tool_palette = tool_palette

        action = self.item.action
        label  = action.name

        # Tool palette tools never have '...' at the end:
        if label.endswith( '...' ):
            label = label[:-3]

        # And they never contain shortcuts:
        label   = label.replace( '&', '' )
        image   = action.image.create_image()
        path    = action.image.absolute_path
        bmp     = image_cache.get_bitmap( path )
        kind    = action.style
        tooltip = action.tooltip
        longtip = action.description

        if not show_labels:
            label = ''

        # Add the tool to the tool palette:
        self.tool_id = tool_palette.add_tool(
            label, bmp, kind, tooltip, longtip
        )
        tool_palette.toggle_tool(   self.tool_id, action.checked )
        tool_palette.enable_tool(   self.tool_id, action.enabled )
        tool_palette.on_tool_event( self.tool_id, self._on_tool  )

        # Listen to the facet changes on the action (so that we can update its
        # enabled/disabled/checked state etc):
        action.on_facet_set( self._on_action_enabled_modified, 'enabled' )
        action.on_facet_set( self._on_action_checked_modified, 'checked' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _on_action_enabled_modified ( self, action, facet_name, old, new ):
        """ Called when the enabled facet is changed on an action.
        """
        self.tool_palette.enable_tool( self.tool_id, action.enabled )


    def _on_action_checked_modified ( self, action, facet_name, old, new ):
        """ Called when the checked facet is changed on an action.
        """
        if action.style == 'radio':
            # If we're turning this one on, then we need to turn all the others
            # off.  But if we're turning this one off, don't worry about the
            # others.
            if new:
                for item in self.item.parent.items:
                    if item is not self.item:
                        item.action.checked = False

        # This will *not* emit a tool event:
        self.tool_palette.toggle_tool( self.tool_id, new )

    #-- Tool Palette Event Handlers --------------------------------------------

    def _on_tool ( self, event ):
        """ Called when the tool palette button is clicked.
        """
        action       = self.item.action
        action_event = ActionEvent()
        is_checkable = ((action.style == 'radio') or (action.style == 'check'))

        # Perform the action!
        action.checked = self.tool_palette.get_tool_state( self.tool_id ) == 1
        action.perform( action_event )

#-- EOF ------------------------------------------------------------------------