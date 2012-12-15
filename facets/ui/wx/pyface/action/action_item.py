"""
The wx specific implementations the action manager internal classes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from inspect \
    import getargspec

import wx

from facets.core_api \
    import Any, Bool, HasFacets

from facets.ui.pyface.action.action_event \
    import ActionEvent

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

_STYLE_TO_KIND_MAP = {
    'push'   : wx.ITEM_NORMAL,
    'radio'  : wx.ITEM_RADIO,
    'toggle' : wx.ITEM_CHECK
}

#-------------------------------------------------------------------------------
#  '_MenuItem' class:
#-------------------------------------------------------------------------------

class _MenuItem ( HasFacets ):
    """ A menu item representation of an action item.
    """

    #-- '_MenuItem' interface --------------------------------------------------

    # Is the item checked?
    checked = Bool( False )

    # A controller object we delegate taking actions through (if any):
    controller = Any

    # Is the item enabled?
    enabled = Bool( True )

    # Is the item visible?
    visible = Bool( True )

    # The radio group we are part of (None if the menu item is not part of such
    # a group):
    group = Any

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, parent, menu, item, controller ):
        """ Creates a new menu item for an action item.
        """
        self.item = item

        # Create an appropriate menu item depending on the style of the action.
        #
        # N.B. Don't try to use -1 as the Id for the menu item... wx does not
        # ---- like it!
        action  = item.action
        label   = action.name
        kind    = _STYLE_TO_KIND_MAP[ action.style ]
        longtip = action.description

        if len( action.accelerator ) > 0:
            label = label + '\t' + action.accelerator

        # This just helps with debugging when people forget to specify a name
        # for their action (without this wx just barfs which is not very
        # helpful!).
        if len( label ) == 0:
            label = item.action.__class__.__name__

        self.control_id = wx.NewId()
        self.control    = wx.MenuItem( menu, self.control_id, label, longtip,
                                       kind )

        # If the action has an image then display it:
        if action.image is not None:
            self.control.SetBitmap( action.image.create_bitmap() )

        menu.AppendItem( self.control )
        menu.menu_items.append( self )

        # Set the initial enabled/disabled state of the action:
        self.control.Enable( action.enabled and action.visible )

        # Set the initial checked state:
        if action.style in [ 'radio', 'toggle' ]:
            self.control.Check( action.checked )

        # Wire it up...create an ugly flag since some platforms dont skip the
        # event when we thought they would:
        self._skip_menu_event = False
        wx.EVT_MENU( parent, self.control_id, self._on_menu )

        # Listen for facet changes on the action (so that we can update its
        # enabled/disabled/checked state etc):
        action.on_facet_set( self._on_action_enabled_modified, 'enabled' )
        action.on_facet_set( self._on_action_visible_modified, 'visible' )
        action.on_facet_set( self._on_action_checked_modified, 'checked' )
        action.on_facet_set( self._on_action_name_modified,    'name' )

        if controller is not None:
            self.controller = controller
            controller.add_to_menu( self )


    def dispose ( self ):
        action = self.item.action
        action.on_facet_set( self._on_action_enabled_modified, 'enabled',
                             remove = True )
        action.on_facet_set( self._on_action_visible_modified, 'visible',
                             remove = True )
        action.on_facet_set( self._on_action_checked_modified, 'checked',
                             remove = True )
        action.on_facet_set( self._on_action_name_modified, 'name',
                             remove = True )

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self ):
        """ Handles the 'enabled' facet being changed.
        """
        self.control.Enable( self.enabled and self.visible )


    def _visible_set ( self ):
        """ Handles the 'visible' facet being changed.
        """
        self.control.Enable( self.visible and self.enabled )


    def _checked_set ( self ):
        """ Handles the 'checked' facet being changed.
        """
        if self.item.action.style == 'radio':
            # fixme: Not sure why this is even here, we had to guard it to
            # make it work? Must take a look at svn blame!
            # FIXME v3: Note that menu_checked() doesn't seem to exist, so we
            # comment it out and do the following instead.
            #if self.group is not None:
            #    self.group.menu_checked(self)

            # If we're turning this one on, then we need to turn all the others
            # off.  But if we're turning this one off, don't worry about the
            # others.
            if self.checked:
                for item in self.item.parent.items:
                    if item is not self.item:
                        item.action.checked = False

        self.control.Check( self.checked )


    def _on_action_enabled_modified ( self, object ):
        """ Called when the enabled facet is changed on an action.
        """
        self.control.Enable( object.enabled and object.visible )


    def _on_action_visible_modified ( self, object ):
        """ Called when the visible facet is changed on an action.
        """
        self.control.Enable( object.visible and object.enabled )


    def _on_action_checked_modified ( self, object ):
        """ Called when the checked facet is changed on an action.
        """
        if self.item.action.style == 'radio':
            # fixme: Not sure why this is even here, we had to guard it to
            # make it work? Must take a look at svn blame!
            # FIXME v3: Note that menu_checked() doesn't seem to exist, so we
            # comment it out and do the following instead.
            #if self.group is not None:
            #    self.group.menu_checked(self)

            # If we're turning this one on, then we need to turn all the others
            # off.  But if we're turning this one off, don't worry about the
            # others.
            if object.checked:
                for item in self.item.parent.items:
                    if item is not self.item:
                        item.action.checked = False

        # This will *not* emit a menu event because of this ugly flag
        self._skip_menu_event = True
        self.control.Check( object.checked )
        self._skip_menu_event = False


    def _on_action_name_modified ( self, object ):
        """ Called when the name facet is changed on an action.
        """
        self.control.SetText( object.name )

    #-- wx Event Handlers ------------------------------------------------------

    def _on_menu ( self, event ):
        """ Called when the menu item is clicked.
        """
        # If the ugly flag is set, do not perform the menu event:
        if self._skip_menu_event:
            return

        action = self.item.action
        action_event = ActionEvent()

        is_checkable = action.style in [ 'radio', 'toggle' ]

        # Perform the action:
        if self.controller is not None:
            if is_checkable:
                # fixme: There is a difference here between having a controller
                # and not in that in this case we do not set the checked state
                # of the action! This is confusing if you start off without a
                # controller and then set one as the action now behaves
                # differently!
                self.checked = self.control.IsChecked() == 1

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
                action.checked = self.control.IsChecked() == 1

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it.
            args, varargs, varkw, dflts = getargspec( action.perform )

            # If the only argument is 'self' then don't pass the event:
            if len( args ) == 1:
                action.perform()
            else:
                action.perform( action_event )

#-------------------------------------------------------------------------------
#  '_Tool' class:
#-------------------------------------------------------------------------------

class _Tool ( HasFacets ):
    """ A tool bar tool representation of an action item.
    """

    #-- '_Tool' interface ------------------------------------------------------

    # Is the item checked?
    checked = Bool( False )

    # A controller object we delegate taking actions through (if any):
    controller = Any

    # Is the item enabled?
    enabled = Bool( True )

    # Is the item visible?
    visible = Bool( True )

    # The radio group we are part of (None if the tool is not part of such a
    # group):
    group = Any

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, parent, tool_bar, image_cache, item, controller,
                         show_labels ):
        """ Creates a new tool bar tool for an action item.
        """
        self.item = item
        self.tool_bar = tool_bar

        # Create an appropriate tool depending on the style of the action:
        action  = self.item.action
        label   = action.name

        # Tool bar tools never have '...' at the end!:
        if label.endswith( '...' ):
            label = label[ : -3 ]

        # And they never contain shortcuts:
        label = label.replace( '&', '' )

        # If the action has an image then convert it to a bitmap (as required
        # by the toolbar):
        if action.image is not None:
            image = action.image.create_image(
                self.tool_bar.GetToolBitmapSize()
            )
            path = action.image.absolute_path
            bmp  = image_cache.get_bitmap( path )

        else:
            from facets.ui.pyface.api import ImageResource

            image = ImageResource( 'foo' )
            bmp   = image.create_bitmap()

        kind    = _STYLE_TO_KIND_MAP[ action.style ]
        tooltip = action.tooltip
        longtip = action.description

        if not show_labels:
            label = ''

        else:
            self.tool_bar.SetSize( ( -1, 50 ) )

        self.control_id = wx.NewId()
        self.control    = tool_bar.AddLabelTool(
            self.control_id, label, bmp, wx.NullBitmap, kind, tooltip, longtip
        )

        # Set the initial checked state:
        tool_bar.ToggleTool( self.control_id, action.checked )

        # Set the initial enabled/disabled state of the action:
        tool_bar.EnableTool( self.control_id,
                             action.enabled and action.visible )

        # Wire it up:
        wx.EVT_TOOL( parent, self.control_id, self._on_tool )

        # Listen for facet changes on the action (so that we can update its
        # enabled/disabled/checked state etc):
        action.on_facet_set( self._on_action_enabled_modified, 'enabled' )
        action.on_facet_set( self._on_action_visible_modified, 'visible' )
        action.on_facet_set( self._on_action_checked_modified, 'checked' )

        if controller is not None:
            self.controller = controller
            controller.add_to_toolbar( self )

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self ):
        """ Handles the 'enabled' facet being changed.
        """
        self.tool_bar.EnableTool( self.control_id,
                                  self.enabled and self.visible )


    def _visible_set ( self ):
        """ Handles the 'visible' facet being changed.
        """
        self.tool_bar.EnableTool( self.control_id,
                                  self.visible and self.enabled )


    def _checked_set ( self ):
        """ Handles the 'checked' facet being changed.
        """
        if self.item.action.style == 'radio':
            # FIXME v3: Note that toolbar_checked() doesn't seem to exist, so
            # we comment it out and do the following instead.
            #self.group.toolbar_checked(self)

            # If we're turning this one on, then we need to turn all the others
            # off.  But if we're turning this one off, don't worry about the
            # others.
            if self.checked:
                for item in self.item.parent.items:
                    if item is not self.item:
                        item.action.checked = False

        self.tool_bar.ToggleTool( self.control_id, self.checked )


    def _on_action_enabled_modified ( self, action, facet_name, old, new ):
        """ Called when the enabled facet is changed on an action.
        """
        self.tool_bar.EnableTool( self.control_id,
                                  action.enabled and action.visible )


    def _on_action_visible_modified ( self, action, facet_name, old, new ):
        """ Called when the visible facet is changed on an action.
        """
        self.tool_bar.EnableTool( self.control_id,
                                  action.visible and action.enabled )


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
        self.tool_bar.ToggleTool( self.control_id, new )

    #-- wx Event Handlers ------------------------------------------------------

    def _on_tool ( self, event ):
        """ Called when the tool bar tool is clicked.
        """
        action       = self.item.action
        action_event = ActionEvent()

        is_checkable = ( action.style == 'radio' or action.style == 'check' )

        # Perform the action:
        if self.controller is not None:
            # fixme: There is a difference here between having a controller
            # and not in that in this case we do not set the checked state
            # of the action! This is confusing if you start off without a
            # controller and then set one as the action now behaves
            # differently!
            self.checked = self.tool_bar.GetToolState( self.control_id ) == 1

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
            action.checked = self.tool_bar.GetToolState( self.control_id ) == 1

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it.
            args, varargs, varkw, dflts = getargspec( action.perform )

            # If the only argument is 'self' then don't pass the event:
            if len( args ) == 1:
                action.perform()
            else:
                action.perform( action_event )

#-------------------------------------------------------------------------------
#  '_PaletteTool' class:
#-------------------------------------------------------------------------------

class _PaletteTool ( HasFacets ):
    """ A tool palette representation of an action item.
    """

    #-- '_PaletteTool' interface -----------------------------------------------

    # The radio group we are part of (None if the tool is not part of such a
    # group):
    group = Any

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, tool_palette, image_cache, item, show_labels ):
        """ Creates a new tool palette tool for an action item.
        """
        self.item = item
        self.tool_palette = tool_palette

        action = self.item.action
        label  = action.name

        # Tool palette tools never have '...' at the end:
        if label.endswith( '...' ):
            label = label[ : -3 ]

        # And they never contain shortcuts:
        label = label.replace( '&', '' )
        image = action.image.create_image()
        path  = action.image.absolute_path
        bmp   = image_cache.get_bitmap( path )

        kind    = action.style
        tooltip = action.tooltip
        longtip = action.description

        if not show_labels:
            label = ''

        # Add the tool to the tool palette:
        self.tool_id = tool_palette.add_tool( label, bmp, kind, tooltip,
                                              longtip )
        tool_palette.toggle_tool( self.tool_id, action.checked )
        tool_palette.enable_tool( self.tool_id, action.enabled )
        tool_palette.on_tool_event( self.tool_id, self._on_tool )

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

        # This will *not* emit a tool event.
        self.tool_palette.toggle_tool( self.tool_id, new )

    #-- Tool Palette Event Handlers --------------------------------------------

    def _on_tool ( self, event ):
        """ Called when the tool palette button is clicked.
        """
        action       = self.item.action
        action_event = ActionEvent()
        is_checkable = ( action.style == 'radio' or action.style == 'check' )

        # Perform the action:
        action.checked = self.tool_palette.get_tool_state( self.tool_id ) == 1
        action.perform( action_event )

#-- EOF ------------------------------------------------------------------------