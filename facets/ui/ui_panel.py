"""
Creates a panel-based GUI toolkit neutral user interface for a specified UI
object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from cgi \
    import escape

from facets.api \
    import Any, Instance, Undefined, Group, Item, Editor, Control

from facets.core.facets_env \
    import facets_env

from facets.ui.adapters.layout \
    import Layout

from facets.ui.dock.api \
    import DockWindow, DockSizer, DockSection, DockRegion, DockControl

from facets.ui.dock.dockable_view_element \
    import DockableViewElement

from facets.ui.controls.image_text \
    import ImageText

from facets.ui.controls.image_panel \
    import ImagePanel

from ui_base \
    import BasePanel

from undo \
    import UndoHistory

from help_template \
    import help_template

from toolkit \
    import toolkit

from helper \
    import default_font

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Pattern of all digits
all_digits = re.compile( r'\d+' )

# Global font used for emphasis
emphasis_font = None

# Global color used for emphasis
emphasis_color = ( 0, 0, 127 )

# Group layouts that result in a DockWindow being created:
dock_window_layouts = ( 'split', 'tabbed' )

# The types of sizing policies:
size_policy = ( 'fixed', 'expanding' )

#-------------------------------------------------------------------------------
#  Create the different panel-based GUI toolkit neutral user interfaces:
#-------------------------------------------------------------------------------

def ui_panel ( ui, parent ):
    """ Creates a panel-based GUI toolkit neutral user interface for a
        specified UI object.
    """
    ui_panel_for( ui, parent, True, False )


def ui_subpanel ( ui, parent ):
    """ Creates a subpanel-based GUI toolkit neutral user interface for a
        specified UI object. A subpanel does not allow control buttons (other
        than those specified in the UI object).
    """
    ui_panel_for( ui, parent, False, False )


def ui_editor ( ui, parent ):
    """ Creates a panel-based GUI toolkit neutral Facets UI editor for editing
        a specific object facet.
    """
    ui_panel_for( ui, parent, False, True )


def ui_panel_for ( ui, parent, buttons, create_panel ):
    """ Creates a panel-based GUI toolkit neutral user interface for a
        specified UI object.
    """
    # Disable screen updates on the parent control while we build the view:
    parent.frozen = True

    # Build the view:
    ui.control    = control = Panel( ui, parent, buttons, create_panel ).control
    ui.is_control = isinstance( control, Control )

    # Allow screen updates to occur again:
    parent.frozen = False

    control._parent = parent
    control._object = ui.context.get( 'object' )
    control._ui     = ui

    try:
        ui.prepare_ui()
    except:
        control.destroy()
        ui.control = None
        ui.result  = False

        raise

    ui.restore_prefs()
    ui.result = True

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def dw_id ( ui, group ):
    """ Returns the composite DockWindow id for a specified UI and Group object.
    """
    if ui.id == '':
        return ''

    if group is not None:
        return '%s[%s]' % ( ui.id, group.id )

    return (ui.id + '[]')


def display_vip_shell ( event ):
    """ Displays a copy of the VIP Shell tool.
    """
    from facets.extra.tools.vip_shell import VIPShell

    VIPShell( name = 'Developer VIP Shell' ).edit_facets()

#-------------------------------------------------------------------------------
#  'Panel' class:
#-------------------------------------------------------------------------------

class Panel ( BasePanel ):
    """ GUI toolkit neutral user interface panel for Facets-based user
        interfaces.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, ui, parent, allow_buttons, create_panel ):
        """ Initializes the object.
        """
        self.ui = ui
        view    = ui.view
        title   = view.title

        # Reset any existing history listeners:
        history = ui.history
        if history is not None:
            history.on_facet_set( self._on_undoable, 'undoable',
                                  remove = True )
            history.on_facet_set( self._on_redoable, 'redoable',
                                  remove = True )
            history.on_facet_set( self._on_revertable, 'undoable',
                                  remove = True )

        # Determine if we need any buttons or an 'undo' history:
        buttons  = self.get_buttons( view )
        nbuttons = len( buttons )

        if allow_buttons and (history is None):
            for button in buttons:
                if (self.is_button( button, 'Undo' ) or
                    self.is_button( button, 'Revert' )):
                    history = ui.history = UndoHistory()

                    break

        # Determine whether the panel has any 'extras':
        has_title   = ((title != '') and (not isinstance(
                               getattr( parent, 'owner', None ), DockWindow )))
        has_toolbar = (self.ui.view.toolbar is not None)
        has_buttons = (allow_buttons and ((nbuttons != 1) or
                      (not self.is_button( buttons[0], '' ))))

        # Create a container panel to put everything in if there are any
        # 'extras':
        if not (has_title or has_toolbar or has_buttons):
            self.control = panel( ui, parent, create_panel )

            return

        # Create a panel (if necessary) to hold all of the various content
        # items:
        layout = toolkit().create_box_layout()
        if create_panel:
            self.control  = parent = toolkit().create_panel( parent )

        # Add the title control (if needed):
        if has_title:
            layout.add( toolkit().create_heading_text( parent, text = title ),
                        bottom = 4 * (1 - has_toolbar) )

        # Add the toolbar (if needed):
        if has_toolbar:
            self.add_toolbar( layout )

        # Add the facets ui:
        layout.add( panel( ui, parent ), stretch = 1 )

        # Add the buttons (if needed):
        if has_buttons:
            # Add the special function buttons:
            layout.add( toolkit().create_separator( parent ) )
            b_layout = toolkit().create_box_layout( False )
            for button in buttons:
                if self.is_button( button, 'Undo' ):
                    self.undo = self.add_button( button, b_layout,
                                                 self._on_undo, False )
                    self.redo = self.add_button( button, b_layout,
                                                 self._on_redo, False, 'Redo' )
                    history.on_facet_set( self._on_undoable, 'undoable',
                                          dispatch = 'ui' )
                    history.on_facet_set( self._on_redoable, 'redoable',
                                          dispatch = 'ui' )
                elif self.is_button( button, 'Revert' ):
                    self.revert = self.add_button( button, b_layout,
                                                   self._on_revert, False )
                    history.on_facet_set( self._on_revertable, 'undoable',
                                          dispatch = 'ui' )
                elif self.is_button( button, 'Help' ):
                    self.add_button( button, b_layout, self._on_help )
                elif not self.is_button( button, '' ):
                    self.add_button( button, b_layout )

            layout.add( b_layout, align = 'right', fill = False, left = 5,
                        right = 5, top = 5, bottom = 5 )

        if not hasattr( self, 'control' ):
            self.control = layout
        else:
            parent.layout = layout

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def panel ( ui, parent, create_panel = False ):
    """ Creates a panel-based GUI toolkit neutral user interface for a
        specified UI object.

        This function does not modify the UI object passed to it
    """
    # Bind the context values to the 'info' object:
    ui.info.bind_context()

    # Get the content that will be displayed in the user interface:
    content = ui._groups
    ngroups = len( content )

    # Embed the created control in a scrollable window (if requested):
    scrollable = ui.scrollable
    if scrollable:
        parent = toolkit().create_scrolled_panel( parent )

    # If there is 0 or 1 Groups in the content, create a single panel for it:
    if ngroups == 0:
        panel = toolkit().create_panel( parent )
    elif ngroups == 1:
        # Create a control containing the group's content:
        panel = GroupPanel( parent, content[0], ui,
                            create_panel = create_panel or scrollable ).control
    else:
        # Create a notebook which will contain a page for each group in the
        # content:
        panel = create_notebook_for_items( content, ui, parent, None )
        panel.ui = ui

        # fixme: notice when the notebook page changes (to display the correct
        # help)...

    if scrollable:
        # Finish embedding the created control in a scrollable window:
        layout = toolkit().create_box_layout()
        layout.add( panel, stretch = 1 )

        parent.layout  = layout
        parent.content = panel
        panel          = parent

    return panel


def create_notebook_for_items ( content, ui, parent, group,
                                item_handler = None, is_dock_window = False ):
    """ Creates a notebook and adds a list of groups or items to it as separate
        pages.
    """
    if is_dock_window:
        nb = parent
    else:
        dw = DockWindow( parent, handler      = ui.handler,
                                 handler_args = ( ui.info, ),
                                 id           = dw_id( ui, group ) )
        if ui.dock_window is None:
            ui.dock_window = dw

        if group is not None:
            dw.theme = group.dock_theme

        nb = dw.control

    pages     = []
    count     = 0
    has_theme = ((group is not None) and (group.group_theme is not None))

    # Create a notebook page for each group or item in the content:
    active = 0
    for index, item in enumerate( content ):
        if isinstance( item, Group ):
            # Create the group as a nested DockWindow item:
            if item.selected:
                active = index

            contents = GroupPanel( nb, item, ui, suppress_label = True,
                                   is_dock_window = True ).dock_contents

            # If the result is a region (i.e. notebook) with only one page,
            # collapse it down into just the contents of the region:
            if (isinstance( contents, DockRegion ) and
               (len( contents.contents ) == 1)):
                contents = contents.contents[0]

            # Add the content to the notebook as a new page:
            pages.append( contents )
        else:
            # Create the new page as a simple DockControl containing the
            # specified set of controls:
            page_name = item.get_label( ui )
            count    += 1
            if page_name == '':
                page_name = 'Page %d' % count

            layout = toolkit().create_box_layout()
            if has_theme:
                image_panel, image_layout = add_image_panel( nb, group )
                panel = image_panel.control
                image_layout.add( layout, stretch = 1 )
                item_handler( item, panel, layout )
            elif is_a_control( item ):
                panel = item_handler( item, nb, layout )
            else:
                panel = toolkit().create_panel( nb )
                panel.layout = layout
                item_handler( item, panel, layout )

            pages.append( DockControl(
                name     = page_name,
                image    = item.image,
                id       = item.get_id(),
                style    = item.dock,
                dockable = DockableViewElement( ui = ui, element = item ),
                export   = item.export,
                control  = panel
            ) )

    region = DockRegion( contents = pages, active = active )

    # If the caller is a DockWindow, return the region as the result:
    if is_dock_window:
        return region

    dw.dock_sizer = DockSizer( contents = DockSection( contents = [ region ] ) )

    # Return the notebook as the result:
    return nb


def add_image_panel ( window, group ):
    """ Creates a themed ImagePanel for the specified group and parent window.
    """
    image_panel = ImagePanel(
        theme  = group.group_theme,
        text   = group.label,
        parent = window
    )

    return ( image_panel, image_panel().layout )


def show_help ( ui, button ):
    """ Displays a help window for the specified UI's active Group.
    """
    group    = ui._groups[ ui._active_group ]
    template = help_template()
    if group.help != '':
        header = template.group_help % escape( group.help )
    else:
        header = template.no_group_help

    fields = []
    for item in group.get_content( False ):
        if not item.is_spacer():
            fields.append( template.item_help % (
                           escape( item.get_label( ui ) ),
                           escape( item.get_help( ui ) ) ) )

    html = template.group_html % ( header, '\n'.join( fields ) )
    # fixme: What should this be now...
    ### HTMLHelpWindow( button, html, .25, .33 )


def is_a_control ( item ):
    """ Returns True if the specified 'item' will generate a single control;
        and False otherwise.
    """
    if isinstance( item, Group ):
        if item.layout in dock_window_layouts:
            return True

        content = item.get_content()
        if len( content ) == 1:
            return is_a_control( content[0] )
    elif isinstance( item, Item ):
        name = item.name
        return (not (item.show_label or
                    (name == '')     or
                    (name == '_')    or
                    (name == ' ')    or
                    all_digits.match( name )))
    elif len( item ) == 1:
        return is_a_control( item[0] )

    return False

#-------------------------------------------------------------------------------
#  'GroupPanel' class:
#-------------------------------------------------------------------------------

class GroupPanel ( object ):
    """ A subpanel for a single group of items.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, parent, group, ui,
                         suppress_label = False,
                         is_dock_window = False,
                         create_panel   = False,
                         is_horizontal  = False ):
        """ Initializes the object.
        """
        # Initialize attributes:
        self.ui            = ui
        self.group         = group
        self.is_horizontal = (group.orientation == 'horizontal')
        self.resizable     = False
        self.control       = None
        self.layout        = None
        self.dock_contents = None
        self.item_control  = None

        # Initialize locals:
        editor             = None
        layout             = group.layout
        is_scrolled_panel  = group.scrollable
        is_splitter        = (layout == 'split')
        is_tabbed          = (layout == 'tabbed')
        is_toolbar         = (layout == 'toolbar')
        id                 = group.id

        # Get the contents of the group:
        content = group.get_content()

        # Handle adding a group to an existing DockWindow:
        if is_dock_window and (is_splitter or is_tabbed):
            if is_splitter:
                self.dock_contents = self.add_dock_window_splitter_items(
                                              parent, content, group )
            else:
                self.resizable     = group.springy
                self.dock_contents = create_notebook_for_items(
                    content, ui, parent, group, self.add_notebook_item, True
                )

            return

        # Discard splitter/tabbed settings if there is not enough content to
        # bother (e.g. 'defined_when' clauses caused items to be omitted):
        if (is_splitter or is_tabbed) and (len( content ) < 2):
            is_splitter = is_tabbed = False

        # Create a scrolling container (if needed):
        scrollable = None
        if is_scrolled_panel:
            self.top_control( toolkit().create_scrolled_panel( parent ) )
            self.control.min_size = parent.min_size
            scrollable = parent   = self.control
            self.resizable        = True

        # Create a group theme container (if needed):
        image_panel = None
        theme       = group.group_theme
        if theme is not None:
            image_panel, image_layout = add_image_panel( parent, group )
            control = image_panel.control
            if scrollable is not None:
                scrollable.content = control
                scrollable         = None
            parent          = self.top_control( control )
            suppress_label |= image_panel.can_show_text
            self.layout     = image_layout
            if not is_a_control( group ):
                parent        = toolkit().create_panel( parent )
                parent.layout = self.layout = toolkit().create_box_layout(
                                                        not self.is_horizontal )
                image_layout.add( parent, stretch = 1 )
        elif (scrollable is not None) and (not is_a_control( group )):
            scrollable.layout  = layout = toolkit().create_box_layout(
                                                        not self.is_horizontal )
            scrollable.content = parent = toolkit().create_panel( scrollable )
            scrollable         = None
            layout.add( parent, stretch = 1 )

        # Set up a group with or without a border around its contents:
        label = ''
        if not suppress_label:
            label = group.label

        if group.show_border:
            self.control, self.layout = toolkit().create_groupbox_layout(
                                  not self.is_horizontal, parent, label, group )
        elif layout == 'flow':
            self.layout = toolkit().create_flow_layout( not self.is_horizontal )
            if self.control is not None:
                self.control.layout = self.layout

        if ((id != '') or
            (group.visible_when != '') or
            (group.enabled_when != '')):
            if is_splitter or is_tabbed:
                editor = DockWindowGroupEditor( ui = ui )
            elif is_toolbar:
                editor = ToolbarGroupEditor( ui = ui )
            else:
                editor = GroupEditor()

            ui._editors.append( editor )

            if id != '':
                ui.info.bind( group.id, editor )

            if group.visible_when != '':
                ui.add_visible( group.visible_when, editor )

            if group.enabled_when != '':
                ui.add_enabled( group.enabled_when, editor )

        # Force the creation of a panel if one is needed but not yet created:
        if ((self.control is None) and
            (create_panel or
             ((is_dock_window or (editor is not None)) and
              (not is_a_control( group ))))):
            parent = self.top_control( toolkit().create_panel( parent ) )
            if self.layout is not None:
                self.control.layout = self.layout

        # Add a group title if needed:
        if (label != '') and (not group.show_border):
            self.get_layout().add(
                toolkit().create_heading_text( parent, label ),
                left = 4, right = 4, top = 4
            )

        # Set up scrolling now that the layout has been set:
        if is_scrolled_panel:
            if self.is_horizontal:
                self.control.scroll_vertical = False
            else:
                self.control.scroll_horizontal = False

        if len( content ) > 0:
            # Create a DockWindow with splitter bars (if needed):
            if is_splitter:
                dw = DockWindow( parent, handler      = ui.handler,
                                         handler_args = ( ui.info, ),
                                         id           = dw_id( ui, group ),
                                         theme        = group.dock_theme )
                if ui.dock_window is None:
                    ui.dock_window = dw

                dwc = dw.control
                if editor is not None:
                    editor.dock_window = dwc

                dw.dock_sizer = DockSizer( contents =
                    self.add_dock_window_splitter_items( dwc, content, group ) )
                self.get_layout().add( dwc, stretch = 1 )

            # Create a DockWindow with tabs (if needed):
            elif is_tabbed:
                self.resizable = group.springy
                dw = create_notebook_for_items( content, ui, parent, group,
                                                self.add_notebook_item )
                if editor is not None:
                    editor.dock_window = dw

                self.get_layout().add( dw, stretch = self.resizable )

            elif layout == 'fold':
                self.resizable = True
                self.get_layout().add(
                    self.create_fold_for_items( panel, content ), stretch = 1
                )

            elif is_toolbar:
                toolbar = self.create_toolbar_for_items( parent, content,
                                                         group )
                self.get_layout().add( toolbar() )
                if editor is not None:
                    editor.toolbar = toolbar

            # Otherwise, add the groups or items:
            elif isinstance( content[0], Group ):
                self.add_groups( content, parent, self.is_horizontal )

            else:
                self.add_items( content, parent, self.layout )

        # If the caller is a DockWindow, we need to define the content we are
        # adding to it:
        if is_dock_window:
            # Create the appropriate DockWindow contents for the control:
            self.dock_contents = DockRegion( contents = [
                DockControl(
                    name     = group.get_label( self.ui ),
                    image    = group.image,
                    id       = group.get_id(),
                    style    = group.dock,
                    dockable = DockableViewElement( ui = ui, element = group ),
                    export   = group.export,
                    control  = self.get_control()
                ) ]
            )

        # Make sure the editor 'control' attribute has been initialized:
        if editor is not None:
            editor.adapter = self.control

        # If no container control was created, use the layout as the item to be
        # added to the parent's layout:
        if self.control is None:
            self.control = self.get_layout()

        if scrollable is not None:
            scrollable.content = self.layout.children[0].control

        # If we used an ImagePanel, set its sizing policy as appropriate:
        if image_panel is not None:
            self.layout = None
            image_panel.control.size_policy = (
                'expanding',
                size_policy[ self.resizable or
                             (is_horizontal and (not self.is_horizontal)) ]
            )


    def top_control ( self, control ):
        """ Marks the specified control as the top-level control of the panel
            if we do not already have one.
        """
        if self.control is None:
            self.control = control

        return control


    def get_control ( self ):
        """ Returns the control associated with this panel.
        """
        control = self.control
        if control is None:
            control = self.layout

        if isinstance( control, Layout ):
            items = control.children
            while True:
                item    = items.pop( 0 )
                control = item.control
                if control is not None:
                    layout = control.parent_layout
                    if layout is not None:
                        layout.remove( control )

                    break

                item = item.layout
                if item is not None:
                    items.extend( item.children )

        return control


    def get_layout ( self, layout = None, control = None ):
        """ Returns the layout being used for the panel being created.
        """
        if self.layout is None:
            if layout is None:
                layout = toolkit().create_box_layout( not self.is_horizontal )
                from facets.extra.helper.debug import created_from
                created_from( layout )

            self.layout = layout

            if self.control is not None:
                (control or self.control).layout = layout

        return self.layout


    def add_dock_window_splitter_items ( self, window, content, group ):
        """ Adds a set of groups or items separated by splitter bars to a
            DockWindow.
        """
        contents = [ self.add_dock_window_splitter_item( window, item, group )
                     for item in content ]

        # Create a splitter group to hold the contents:
        result = DockSection( contents = contents, is_row = self.is_horizontal )

        # If nothing is resizable, then mark each DockControl as such:
        if not self.resizable:
            for item in result.get_controls():
                item.resizable = False

        # Return the DockSection we created:
        return result


    def add_dock_window_splitter_item ( self, window, item, group ):
        """ Adds a single group or item to a DockWindow.
        """
        if isinstance( item, Group ):
            pg = GroupPanel( window, item, self.ui, suppress_label = True,
                             is_dock_window = True )
            self.resizable |= pg.resizable

            return pg.dock_contents

        layout = toolkit().create_box_layout( not self.is_horizontal )

        if group.group_theme is not None:
            image_panel, image_layout = add_image_panel( window, group )
            panel = image_panel.control
            image_layout.add( layout, stretch = 1 )
            self.add_items( [ item ], panel, layout )
            image_panel.control.size_policy = ( 'expanding',
                                                size_policy[ self.resizable ] )
        else:
            panel = toolkit().create_panel( window )
            panel.layout = layout
            self.add_items( [ item ], panel, layout )

        return DockRegion( contents = [
                DockControl( name     = item.get_label( self.ui ),
                             image    = item.image,
                             id       = item.get_id(),
                             style    = item.dock,
                             dockable = DockableViewElement(
                                            ui = self.ui, element = item ),
                             export   = item.export,
                             control  = panel
                )
            ]
        )


    def create_fold_for_items ( self, window, content ):
        """ Adds a set of groups or items as vertical notebook pages to a
            vertical notebook.
        """
        from facets.ui.controls.vertical_notebook \
            import VerticalNotebook

        # Create the vertical notebook:
        nb     = VerticalNotebook( scrollable = True, multiple_open = True )
        result = nb.create_control( window )

        # Create the notebook pages:
        nb.pages = [ self.create_fold_for_item( nb, item ) for item in content ]

        # Return the notebook we created:
        return result


    def create_fold_for_item ( self, notebook, item ):
        """ Adds a single group or item to a vertical notebook.
        """
        # fixme: Does this need to be changed to work with the abstraction
        # layout, or is it just a matter of making the VerticalNotebook GUI
        # toolkit neutral?

        # Create a new notebook page:
        page = notebook.create_page()

        # Create the page contents:
        if isinstance( item, Group ):
            panel = GroupPanel( page.parent, item, self.ui,
                        suppress_label = True, create_panel = True ).control
        else:
            panel        = toolkit().create_panel( page.parent )
            layout       = toolkit().create_box_layout()
            panel.layout = layout
            self.add_items( [ item ], panel, layout )

        # Set the page name and control:
        page.name    = item.get_label( self.ui )
        page.control = panel
        page.is_open = True

        # Return the new notebook page:
        return page


    def create_toolbar_for_items ( self, window, content, group ):
        """ Adds a set of groups or items as controls within a ToolbarControl
            (either horizontal or vertical).
        """
        from facets.ui.controls.toolbar_control \
            import ToolbarControl

        # Create the toolbar control:
        toolbar = ToolbarControl(
            parent      = window,
            spacing     = group.spacing,
            margin      = group.padding,  # Use group padding as toolbar margin
            orientation = group.orientation,
            alignment   = group.alignment,
            full_size   = group.springy
        )

        # If the group has a theme, then tell the toolbar control not to use
        # its default theme:
        if group.group_theme is not None:
            toolbar.theme = None

        control = toolbar.container

        # Create the toolbar items:
        labels = []
        for item in content:
            if isinstance( item, Group ):
                gp = GroupPanel( control, item, self.ui, suppress_label = True,
                                                         create_panel   = True )
                gp_control = gp.control
                if gp_control is not None:
                    size = gp_control.best_size
                    if size[0] > 0:
                        gp_control.size = size

                    gp_control._id = item.get_id()
                    if item.springy:
                        gp_control._stretch = True
            else:
                self.add_toolbar_item( item, control, labels )

        # For a vertical toolbar which has more then one item with a label, make
        # sure all labels have the same width so they will be visually aligned:
        if (not self.is_horizontal) and (len( labels ) >= 2):
            max_width = reduce( lambda m, c: max( m, c.size[0] ), labels, 0 )
            for control in labels:
                control.min_size = ( max_width, control.min_size[1] )

        # Make sure the toolbar has been initialized:
        toolbar.init()

        # Return the toolbar control we created:
        return toolbar


    def add_toolbar_item ( self, item, toolbar, labels ):
        """ Adds the Item specified by *item* to the toolbar specified by
            *toolbar*.
        """
        global dummy_layout

        if item.show_label and (item.name != '_'):
            panel        = toolkit().create_panel( toolbar )
            layout       = toolkit().create_box_layout( is_vertical = False )
            panel.layout = layout
            panel._id    = item.get_id()
            self.add_items( [ item ], panel, layout )
            if item.springy:
                panel._stretch = True

            dx = dy = 0
            for i, control in enumerate( panel.children ):
                if control.best_size[0] > 0:
                    control.size = control.best_size

                bdx, bdy = control.size
                dx      += bdx
                dy       = max( dy, bdy )
                if i == 0:
                    labels.append( control )
                elif control.editor is not None:
                    # fixme: This is another horrible hack caused by the fact
                    # that several different pieces of code are setting the
                    # control.editor facet, including the one on  the 'panel',
                    # which we try to fix by resetting it to the 'correct' value
                    # here. One culprit is in the facets.ui.editor module which
                    # does a recursive setting of the 'editor' facet on all
                    # child controls if a layout object is returned...
                    panel.editor = control.editor

            panel.size = ( dx + 3, dy )
        else:
            self.add_items( [ item ], toolbar, dummy_layout )


    def add_notebook_item ( self, item, parent, layout ):
        """ Adds a single Item to a notebook.
        """
        self.add_items( [ item ], parent, layout )

        return self.item_control


    def add_groups ( self, content, parent, is_horizontal ):
        """ Adds a list of Group objects to the specified parent.
        """
        if len( content ) == 1:
            layout = self.layout
        else:
            layout = self.get_layout( control = parent )

        # Process each group:
        for subgroup in content:
            # Add the sub-group to the parent:
            pg = GroupPanel(
                parent, subgroup, self.ui, is_horizontal = is_horizontal
            )

            # If the sub-group is resizable:
            align   = ''
            stretch = 1
            if pg.resizable:
                # Then so are we:
                self.resizable = True
            else:
                stretch = 0
                if self.is_horizontal:
                    if subgroup.springy:
                        stretch = 1

                    if subgroup.orientation == 'horizontal':
                        align = 'vcenter'

            if layout is not None:
                layout.add( pg.control, stretch = stretch, align = align )
            else:
                self.get_layout( pg.layout, parent )
                if pg.layout is None:
                    self.layout.add( pg.control, stretch = stretch,
                                                 align   = align )

        if (len( content ) == 1) and (self.control is None):
            self.control = pg.control


    def add_items ( self, content, parent, layout ):
        """ Adds a list of Item objects to the specified parent.
        """
        # Get local references to various objects we need:
        ui               = self.ui
        info             = ui.info
        handler          = ui.handler
        group            = self.group
        show_left        = group.show_left
        padding          = group.padding
        col              = -1
        col_incr         = 1
        self.label_align = []
        show_labels      = False

        for item in content:
            show_labels |= item.show_label

        if (not self.is_horizontal) and (show_labels or (group.columns > 1)):
            # For a vertical list of Items with labels or multiple columns, use
            # a grid layout:
            self.label_pad = 0
            cols           = group.columns
            if show_labels:
                cols    *= 2
                col_incr = 2

            lr_factor   = 0
            border_size = 0
            item_layout = toolkit().create_grid_layout( 0, cols, 3, 6 )
            if layout is None:
                layout = self.get_layout( item_layout, parent )

            if show_left:
                self.label_align = [ 'right' ]
                if show_labels:
                    for i in range( 1, cols, 2 ):
                        item_layout.set_stretchable_column( i )
        else:
            # Otherwise, the current layout will work as is:
            self.label_pad = 4
            cols           = 1
            lr_factor      = 1
            border_size    = 5
            if layout is None:
                layout = self.get_layout( control = parent )

            item_layout = layout

        # Process each Item in the list:
        item_last = len( content ) - 1
        for item_index, item in enumerate( content ):

            # Get the item theme (if any):
            theme = item.item_theme

            # Get the name in order to determine its type:
            name = item.name

            # Check if is a label:
            if name == '':
                label = item.label
                if label != '':
                    # Update the column counter:
                    col += col_incr

                    # If we are building a multi-column layout with labels,
                    # just add space in the next column:
                    if (cols > 1) and show_labels:
                        item_layout.add( ( 1, 1 ) )

                    if theme is not None:
                        label = ImageText(
                            theme = theme,
                            text  = label
                        ).create_control( parent )
                        item_layout.add( label )
                    elif item.style == 'simple':
                        # Add a simple text label:
                        label = toolkit().create_label( parent, label )
                        item_layout.add( label )
                    else:
                        # Add the label to the sizer:
                        label = toolkit().create_heading_text( parent, label )
                        item_layout.add( label, top = 3, bottom = 3 )

                    if item.emphasized:
                        self._add_emphasis( label )

                # Continue on to the next Item in the list:
                continue

            # Update the column counter:
            col += col_incr

            # Check if it is a separator:
            if name == '_':
                item_layout.add_separator( parent )
                ### self._set_owner( line, item )

                continue

            # Convert a blank to a 5 pixel spacer:
            if name == ' ':
                name = '5'

            # Check if it is a spacer:
            if all_digits.match( name ):

                # If so, add the appropriate amount of space to the sizer:
                n = int( name )
                if self.is_horizontal:
                    item_layout.add( ( n, 1 ) )
                else:
                    spacer = ( 1, n )
                    item_layout.add( spacer )
                    if show_labels:
                        item_layout.add( spacer )

                # Continue on to the next Item in the list:
                continue

            # Otherwise, it must be a facet Item:
            object = eval( item.object, globals(), ui.context )
            facet  = object.base_facet( name )
            desc   = facet.desc or ''
            label  = None

            # If we are displaying labels on the left, add the label to the
            # user interface:
            if show_left:
                if item.show_label:
                    label = self.create_label( item, ui, desc, parent,
                                               item_layout, item_index == 0 )
                elif (cols > 1) and show_labels:
                    label = self.dummy_label( parent, item_layout )

            # Get the editor factory associated with the Item:
            editor_factory = item.editor
            if editor_factory is None:
                editor_factory = facet.get_editor()

                # If still no editor factory found, use a default text editor:
                if editor_factory is None:
                    from facets.ui.editors.text_editor import TextEditor

                    editor_factory = TextEditor()

                # If the item has formatting facets set them in the editor
                # factory:
                if item.format_func is not None:
                    editor_factory.format_func = item.format_func

                if item.format_str != '':
                    editor_factory.format_str = item.format_str

                # If the item has an invalid state extended facet name, set it
                # in the editor factory:
                if item.invalid != '':
                    editor_factory.invalid = item.invalid

            # Set up the background image (if used):
            item_panel = parent
            if theme is not None:
                text = ''
                if item.show_label:
                    text = item.get_label( ui )

                image_panel = ImagePanel(
                    theme  = theme,
                    text   = text,
                    parent = parent
                )
                item_panel = image_panel()

            # Create the requested type of editor from the editor factory:
            factory_method = getattr( editor_factory, item.style + '_editor' )
            editor = factory_method(
                ui, object, name, item.tooltip
            ).set(
                item        = item,
                object_name = item.object
            )

            # Tell editor to actually build the editing widget:
            editor.prepare( item_panel )
            control = editor.adapter

            # Set the user specified font (if necessary):
            font = editor_factory.font
            if font is not default_font():
                control.font = font

            # Set the initial 'enabled' state of the editor from the factory:
            editor.enabled = editor_factory.enabled

            # Add emphasis to the editor control if requested:
            if item.emphasized:
                self._add_emphasis( control )

            # Give the editor focus if it requested it:
            if item.has_focus:
                control.set_focus()

            # fixme: Do we need this?...
            # Adjust the maximum border size based on the editor's settings:
            ###border_size = min( border_size, editor.border_size )

            # Set up the reference to the correct 'control' to use in the
            # following section, depending upon whether we have wrapped an
            # ImagePanel around the editor control or not:
            if theme is None:
                width, height = control.size
            else:
                item_panel.layout.add( control, stretch = 1 )
                control       = item_panel
                width, height = image_panel.adjusted_size

            # Set the correct size on the control, as specified by the user:
            scrollable  = editor.scrollable
            item_width  = item.width
            item_height = item.height
            growable    = 0

            if (item_width != -1.0) or (item_height != -1.0):
                if (0.0 < item_width <= 1.0) and self.is_horizontal:
                    growable   = int( 1000.0 * item_width )
                    item_width = -1

                item_width = int( item_width )
                if item_width < -1:
                    item_width = -item_width
                elif item_width != -1:
                    item_width = max( item_width, width )

                if (0.0 < item_height <= 1.0) and (not self.is_horizontal):
                    growable    = int( 1000.0 * item_height )
                    item_height = -1

                item_height = int( item_height )
                if item_height < -1:
                    item_height = -item_height
                elif item_height != -1:
                    item_height = max( item_height, height )

                control.min_size = ( item_width, item_height )

            # Bind the item to the control and all of its children:
            self._set_owner( control, item )

            # Bind the editor into the UIInfo object name space so it can be
            # referred to by a Handler while the user interface is active:
            id = item.id or name
            info.bind( id, editor, item.id )

            # Also, add the editors to the list of editors used to construct
            # the user interface:
            ui._editors.append( editor )

            # If the handler wants to be notified when the editor is created,
            # add it to the list of methods to be called when the UI is
            # complete:
            defined = getattr( handler, id + '_defined', None )
            if defined is not None:
                ui.add_defined( defined )

            # If the editor is conditionally visible, add the visibility
            # 'expression' and the editor to the UI object's list of monitored
            # objects:
            if item.visible_when != '':
                ui.add_visible(
                    item.visible_when,
                    editor if item_panel is parent else item_panel
                )

            # If the editor is conditionally enabled, add the enabling
            # 'expression' and the editor to the UI object's list of monitored
            # objects:
            if item.enabled_when != '':
                ui.add_enabled( item.enabled_when, editor )

            # Add the created editor control to the sizer with the appropriate
            # layout flags and values:
            ui._scrollable |= scrollable
            item_resizable  = ((item.resizable is True) or
                               ((item.resizable is Undefined) and scrollable))
            if item_resizable:
                growable = growable or 500
                self.resizable = True
            elif item.springy:
                growable = growable or 500

            # The following is a hack to allow 'readonly' text fields to
            # work correctly (wx has a bug that setting wx.EXPAND on a
            # StaticText control seems to cause the text to be aligned higher
            # than it would be otherwise, causing it to misalign with its
            # label).
            fill = editor.fill
            if not show_labels:
                fill = True

            if item_last == 0:
                bottom = extra = 0
            else:
                bottom = extra = max( 0, border_size + padding + item.padding )
                if (lr_factor == 0) or (item_index < item_last):
                    bottom = 0

            item_layout.add( control,
                stretch = growable,
                fill    = fill,
                align   = 'vcenter',
                left    = lr_factor * extra,
                right   = lr_factor * extra,
                top     = extra,
                bottom  = bottom
            )

            # If we are displaying labels on the right, add the label to the
            # user interface:
            if not show_left:
                if item.show_label:
                    label = self.create_label( item, ui, desc, parent,
                             item_layout, item_index == item_last, '', 'right' )
                elif (cols > 1) and show_labels:
                    label = self.dummy_label( parent, item_layout )

            # If the Item is resizable, and we are using a multi-column grid:
            if item_resizable and (cols > 1):
                # Mark the entire row as growable:
                item_layout.set_stretchable_row( col / cols )

            # Save the reference to the label control (if any) in the editor:
            editor.label_adapter = label

            self.item_control = control

        # If we created a grid sizer, add it to the original sizer:
        if item_layout is not layout:
            growable = 0
            if self.resizable:
                growable = 1

            layout.add( item_layout, stretch = growable, left = 2, right = 2,
                        top = 2, bottom = 2 )


    def create_label ( self, item, ui, desc, parent, layout, is_end,
                       suffix = ':', pad_side = 'left' ):
        """ Creates an item label.
        """
        label = item.get_label( ui )
        if (label == '') or (label[-1:] in '?=:;,.<>/\\"\'-+#|'):
            suffix = ''

        control = ImageText( theme = item.label_theme,
                             text  = label + suffix ).create_control( parent )

        if facets_env.dev:
            control.set_event_handler( right_up = display_vip_shell )

        self._set_owner( control, item )

        if item.emphasized:
            self._add_emphasis( control )

        align = self.label_align + [ 'vcenter' ]
        left  = self.label_pad * (not is_end)
        right = 5 * self.is_horizontal
        if pad_side == 'right':
            left, right = right, left

        layout.add( control, align = align, left = left, right = right )

        if desc != '':
            control.tooltip = 'Specifies ' + desc

        return control


    def dummy_label ( self, parent, layout ):
        """ Creates a dummy item label.
        """
        control = toolkit().create_label( parent, align = 'right' )
        layout.add( control, fill = False )

        return control


    def _add_emphasis ( self, control ):
        """ Adds emphasis to a specified control's font.
        """
        global emphasis_font

        control.foreground_color = emphasis_color
        if emphasis_font is None:
            emphasis_font = control.font
            # fixme: How do we do this in a GUI toolkit neutral manner...
            ### emphasis_font = wx.Font( font.GetPointSize() + 1,
            ###                          font.GetFamily(),
            ###                          font.GetStyle(),
            ###                          wx.BOLD )

        control.font = emphasis_font


    # fixme: Who is using _owner and why?...
    def _set_owner ( self, control, owner ):
        control()._owner = owner
        for child in control.children:
            self._set_owner( child, owner )

#-------------------------------------------------------------------------------
#  'GroupEditor' class:
#-------------------------------------------------------------------------------

class GroupEditor ( Editor ):
    """ Base class for the pseudo-Editor objects associated with Groups.
    """

#-------------------------------------------------------------------------------
#  'DockWindowGroupEditor' class:
#-------------------------------------------------------------------------------

class DockWindowGroupEditor ( GroupEditor ):
    """ Editor for a group which displays a DockWindow.
    """

    #-- Facet Definitions ------------------------------------------------------

    # DockWindow for the group:
    dock_window = Instance( Control )

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        self.dock_window.owner.restore_prefs( prefs )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return self.dock_window.owner.save_prefs()


    def dispose ( self ):
        """ Handles the user interface being closed.
        """
        self.dock_window.owner.close()

#-------------------------------------------------------------------------------
#  'ToolbarGroupEditor' class:
#-------------------------------------------------------------------------------

class ToolbarGroupEditor ( GroupEditor ):
    """ Editor for a group which displays a ToolbarControl.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ToolbarControl for this group:
    toolbar = Any # Instance( ToolbarControl )

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        self.toolbar.restore_prefs( prefs )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return self.toolbar.save_prefs()

#-------------------------------------------------------------------------------
#  'DummyLayout' class:
#-------------------------------------------------------------------------------

class DummyLayout ( object ):
    """ Dummy layout class used for creating toolbar groups.
    """

    def add ( self, item, stretch = 0, **kw ):
        # fixme: This horrible hack is needed to detect when a stretchable
        # control is being added to a HToolbar/VToolbar via a call to
        # 'add_items'. We don't have direct access to the control that gets
        # added by the call so we intercept it via the DummyLayout object that
        # is used and annotate the control with the '_stretch' flag, which is
        # checked for (using another hack) in the ToolbarControl...
        if stretch > 0:
            item._stretch = True


    def add_separator ( self, *args, **kw ):
        pass

# Create a reusable instance:
dummy_layout = DummyLayout()

#-------------------------------------------------------------------------------
#  'HTMLHelpWindow' class:
#-------------------------------------------------------------------------------

# fixme: Redo this as a Facets UI View to make it GUI toolkit neutral...
### class HTMLHelpWindow ( wx.Frame ):
###     """ Window for displaying Facets-based help text with HTML formatting.
###     """
###
###     #-- Public Methods ---------------------------------------------------------
###
###     def __init__ ( self, parent, html, scale_dx, scale_dy ):
###         """ Initializes the object.
###         """
###         wx.Frame.__init__( self, parent, -1, 'Help', style = wx.SIMPLE_BORDER )
###         self.SetBackgroundColour( WindowColor )
###
###         # Wrap the dialog around the image button panel:
###         sizer        = wx.BoxSizer( wx.VERTICAL )
###         html_control = wh.HtmlWindow( self )
###         html_control.SetBorders( 2 )
###         html_control.SetPage( html )
###         sizer.Add( html_control, 1, wx.EXPAND )
###         sizer.Add( wx.StaticLine( self, -1 ), 0, wx.EXPAND )
###         b_sizer = wx.BoxSizer( wx.HORIZONTAL )
###         button  = wx.Button( self, -1, 'OK' )
###         wx.EVT_BUTTON( self, button.GetId(), self._on_ok )
###         b_sizer.Add( button, 0 )
###         sizer.Add( b_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )
###         self.SetSizer( sizer )
###         self.SetSize( wx.Size( int( scale_dx * screen_dx ),
###                                int( scale_dy * screen_dy ) ) )
###
###         # Position and show the dialog:
###         position_window( self, parent = parent )
###         self.Show()
###
###
###     def _on_ok ( self, event ):
###         """ Handles the window being closed.
###         """
###         self.Destroy()

#-- EOF ------------------------------------------------------------------------
