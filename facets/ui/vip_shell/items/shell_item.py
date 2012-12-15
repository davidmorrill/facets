"""
Defines the ShellItem class that is the concrete base class for all items
displayed by the VIP Shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import join, splitext

from facets.api \
    import Any, Image, Enum, Int, Bool, Str, List, Property, Button, View, \
           HGroup, Item, UItem, toolkit, on_facet_set, on_facet_set,       \
           property_depends_on

from facets.core.facet_base \
    import write_file

from facets.ui.i_stack_item \
    import StrStackItem

from facets.ui.pyface.api \
    import FileDialog, OK

from facets.ui.vip_shell.helper \
    import remove_color, ItemTypes

from facets.ui.vip_shell.theme_manager \
    import theme_manager

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The list of cursor shapes used by a shell item:
ItemCursor = ( 'arrow', 'hand' )

#-------------------------------------------------------------------------------
#  Special Property Definition:
#-------------------------------------------------------------------------------

def DummyMethod ( *args, **kwargs ):
    """ Do nothing method.
    """


def _get_shell_method ( self, method ):
    if self.detached:
        return DummyMethod

    return getattr( self.shell, method[6:] )

#-------------------------------------------------------------------------------
#  'ShellItem' class:
#-------------------------------------------------------------------------------

class ShellItem ( StrStackItem ):
    """ Base class for all shell history items.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Defines a rule to handle method calls of the form: self.shell_xxx(...):
    shell__ = Property( _get_shell_method )

    # The shell this item is associated with:
    shell = Any # Instance( vipShellEditor )

    # Is this item detached from the main shell editor?
    detached = Bool( False )

    # The font to use (override):
    font = 'Consolas Bold 9, Courier Bold 9'

    # The icon to display for the item:
    icon = Image( '@facets:shell_base' )

    # The maximum 'level of detail' supported by the item (override):
    maximum_lod = 2

    # The type of the item:
    type = Enum( *ItemTypes )

    # The id of the item:
    id = Int

    # Should the item display its id?
    show_id = Bool( False )

    # Should line numbers be displayed?
    show_line_numbers = Bool( False )

    # Should the icon be displayed?
    show_icon = Bool( False )

    # Is the item hidden (by the user)?
    hidden = Bool( False )

    # Is the item hidden (by the shell filter)?
    filter_hidden = Bool( False )

    # The current item filter in effect (this filters the contents of the item,
    # and is not the same as the shell filter, which filters the list of items):
    filter = Str

    # Event fired when the 'filter' string should be cleared:
    filter_clear = Button( '@icons2:Delete' )

    # The file name used to save the contents of the item:
    file_name = Str

    # The default file extension to use when saving the contents of the item:
    file_ext = Str( 'txt' )

    # The color code associated with this item:
    color_code = Str( '\x000' )

    # The list of ShellTag items associated with the item:
    tags = List # ( ShellTag )

    # The current stack item control width:
    stack_width = Property

    # The custom tool bar actions supported by the item (if any):
    actions = List # ( Action )

    #-- Facets View Definitions ------------------------------------------------

    filter_view = View(
        HGroup(
            UItem( 'filter_clear',
                   padding = -2,
                   tooltip = 'Clear the current filter'
            ),
            Item( 'filter', springy = True ),
        )
    )

    #-- Item Event Handlers ----------------------------------------------------

    def initialized ( self ):
        """ Called when the shell item has been fully initialized.
        """


    def text_value_for_0 ( self ):
        """ Returns the text to display for level of detail 0.
        """
        value   = self.str( self.item )
        lines   = value.split( '\n' )
        display = self.lookup( 'display' )
        if len( lines ) <= 1:
            return display( value )

        return display( '%s   \x00A[...%d lines...]%s' %
                        ( lines[0], len( lines ), self.color_code ) )


    def text_value_for_1 ( self ):
        """ Returns the text to display for level of detail 1.
        """
        display   = self.lookup( 'display' )
        value     = self.filtered( self.str( self.item ) )
        lines     = value.split( '\n' )
        n         = len( lines )
        threshold = self.shell.threshold
        if n <= threshold:
            return display( value )

        top    = threshold / 2
        bottom = threshold - top - 1
        lines[ top: n - bottom ] = [
            '\x00A[...%d lines omitted...]%s' % ( n - threshold + 1,
                                                  self.color_code ) ]

        return display( '\n'.join( lines ) )


    def text_value_for_2 ( self ):
        """ Returns the text to display for level of detail 2.
        """
        return self.lookup( 'display' )(
            self.filtered( self.str( self.item ) )
        )


    def image_value ( self ):
        """ Returns the correct icon to display.
        """
        if self.show_icon:
            return self.icon

        return None


    def tag_content ( self, index ):
        """ (Override) Returns the content associated with the *index*th tag for
            the item.
        """
        return self.tags[ index ].text


    def replace_code ( self, code ):
        """ Replace the code editor's current contents with the specified
            *code*.
        """
        self.shell.replace_code( code )


    def left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        tag = self.gtext.tag_at( event.x, event.y )
        if tag >= 0:
            self.tags[ tag ].on_click( event )
        elif event.shift_down:
            self.shell_execute_from( self )
        elif event.control_down:
            self.shell_select( self )
        else:
            self.execute()


    def right_up ( self, event ):
        """ Handles the right mouse button being released.
        """
        tag = self.gtext.tag_at( event.x, event.y )
        if tag >= 0:
            self.tags[ tag ].on_right_click( event )
        elif event.shift_down:
            if event.alt_down:
                self.shell_append_ref_from( self )
            else:
                self.shell_append_from( self )
        elif event.alt_down:
            self.shell.append_ref( self )
        else:
            self.click( event )


    def click ( self, event ):
        """ Handles the user clicking an item without the shift or alt
            modifiers.
        """
        value = self.str( self.item )
        if event.control_down:
            self.shell.append( value )
        else:
            self.replace_code( value )


    def motion ( self, event ):
        """ Handles the user moving the mouse.
        """
        tag_index   = self.gtext.tag_at( event.x, event.y )
        self.cursor = ItemCursor[ tag_index >= 0 ]
        tooltip     = ''
        if tag_index >= 0:
            tooltip = self.tags[ tag_index ].tooltip

        self.tooltip = tooltip


    def key_enter ( self, event ):
        """ Execute this item.
        """
        self.execute()


    def key_down ( self, event ):
        """ Move this item down in the history list (if possible).

            The [[Down]] key moves the item down in the history list. If there
            is a current selection, and the item itself is not selected, then
            the item is moved immediately after the selection. Otherwise the
            item is moved down one position in the history list unless it is
            already at the end of the history list
        """
        self.shell_move_down( self )


    def key_up ( self, event ):
        """ Move this item up in the history list (if possible).

            The [[Up]] key moves the item up in the history list. If there is a
            current selection, and the item itself is not selected, then the
            item is moved immediately before the selection. Otherwise the item
            is moved up one position in the history list unless it is already at
            the top of the history list.
        """
        self.shell_move_up( self )


    def key_left ( self, event ):
        """ Decrease the level of detail of this item (if possible).
        """
        self.decrease_lod()


    def key_right ( self, event ):
        """ Increase the level of detail of this item (if possible).
        """
        self.increase_lod()


    def key_f3 ( self, event ):
        """ Toggle the filter bar on or off.
        """
        self.shell_toggle_filter()


    def key_f4 ( self, event ):
        """ Toggle the status bar on or off.
        """
        self.shell_toggle_status()


    def key_b ( self, event ):
        """ Hide the bottommost visible history item and its related items.

            The [[b]] key hides the bottommost visible shell item and all
            associated items.

            You can use the [[b]] (backward) key, in conjunction with the [[n]]
            (next) key, to move backward and forward through the most recently
            executed commands.
        """
        self.shell_undo_command()


    def key_c ( self, event ):
        """ Copy this item to the clipboard.

            The [[c]] command copies the item, without any textual annotations
            such as item ids and line numbers, to the clipboard.

            You can use the [[Ctrl-c]] command to copy the item including all
            textual annotations to the clipboard.
        """
        self.copy_clipboard()


    def key_ctrl_c ( self, event ):
        """ Copy this item to the clipboard.

            The [[Ctrl-c]] command copies the item, including all textual
            annotations such as item ids and line numbers, to the clipboard.

            You can use the [[c]] command to copy the item without any
            annotations to the clipboard.
        """
        toolkit().clipboard().text = remove_color( self.text )


    def key_e ( self, event ):
        """ Add a tab containing a copy of this item to the shell.
        """
        self.shell.add_code_item( self )


    def key_E ( self, event ):
        """ Create a new window containing a copy of this item.
        """
        self.shell.tear_off_item( self )


    def key_f ( self, event ):
        """ Filter out wanted or unwanted lines from this item.

            The [[f]] key displays a pop-up dialog next to your mouse pointer.

            Only lines containing the text you type into the dialog are
            displayed in the item. If the text you type begins with '~', only
            lines not containing the remaining text you type are displayed in
            the item.

            The dialog closes automatically when you move the mouse pointer away
            from the dialog.
        """
        self.popup_for( 'filter_view' )


    def key_n ( self, event ):
        """ Show the first hidden item (and its related items) after the last
            visible history item.

            The [[n]] key shows the first hidden item (and its associated items)
            after the last visible history item.

            You can use the [[n]] (next) key, in conjunction with the [[b]]
            (backward) key, to move backward and forward through the most
            recently executed commands.
        """
        self.shell_redo_command()


    def key_o ( self, event ):
        """ Show the shell's options dialog.

            The [[o]] key displays the shell options dialog which allows you to
            change several types of shell options. The dialog is divided into
            three sections: [[Options]], [[Theme Colors]] and [[Start-up Code]]
            defined by tabs appearing at the top of the dialog.

            The [[Options]] tab allows you to modify the following shell
            properties:

            [[Show IDs]]: If enabled, each shell item displays its numeric id.
            If disabled, numeric ids are not displayed.

            [[Show icons]]: If enabled, each shell item displays a small
            graphic icon indicating the item's type. If disabled, no icons are
            displayed

            [[Show line numbers]]: If enabled, shell items containing more
            than one line of text display line numbers. If disabled, no line
            numbers are displayed.

            [[Theme]]: Allows you to select the graphical theme used to
            display shell items. Select the theme to use from the dropdown list
            of available themes.

            [[Font]]: Allows you to select the font used to display text in
            shell items. Select the font to use from the pop-up dialog that
            appears when you click on the current font's name.

            [[Maximum line threshold]]: Allows you to specify the maximum
            number of lines of text displayed in a shell item at its <<medium>>
            level of detail. Select the number of lines to display using the
            slider that appears when you click on the current line count.

            [[Traceback context lines]]: Allows you to specify the number of
            lines of contextual Python source code to display for each entry in
            a Python traceback. Select the number of lines to display using the
            slider that appears when you click on the current line count.

            The [[Theme Colors]] tab allows you to customize the text colors
            used for the theme most recently selected on the [[Options]] tab.
            Each theme has a number of different colors that it uses when
            displaying text. Select the text style using the dropdown list at
            the top of the tab, then use the color selector below it to adjust
            the color. Any changes you make are immediately reflected in the
            shell so that you can judge the effect the color change has on the
            display.

            Note that any color changes you make are remembered across future
            shell sessions, even if you change the current theme being used.

            You can reset all colors back to the default values for the current
            theme by clicking the <<Reset colors>> button.

            The [[Start-up Code]] tab allows you to specify Python code that
            is executed each time the shell is started. Simply type the code to
            be executed on start-up into the text editor provided on the tab.
        """
        self.shell.edit_options()


    def key_s ( self, event ):
        """ Save the contents of this item to a file.

            The [[s]] key saves the current textual contents of a shell item,
            not including any textual annotations such as items ids or line
            numbers, to a file.

            A file dialog appears prompting you for the name and location of
            where to save the file. The file dialog defaults to saving the file
            in the shell's current working directory with a name of the form:
            vip_shell_<<item_id>>.txt, where <<item_id>> is the id associated
            with the shell item.
        """
        self.save_file()


    def key_t ( self, event ):
        """ Transfer this item to another shell and then delete it.

            The [[t]] key allows you to transfer the shell item to an associated
            shell's history list (or to any other connected tool that accept's
            shell items as input). The transferred item is then removed from the
            current shell's history list. Use the [[T]] key if you want to keep
            the item in the history list after the transfer.

            Note that if no other shell or tool is associated with the current
            shell, the item is simply deleted.
        """
        self.shell_transfer_item( self, True )


    def key_T ( self, event ):
        """ Transfer this item to another shell and keep it.

            The [[T]] key allows you to transfer a copy of the shell item to an
            associated shell's history list (or to any other connected tool that
            accept's shell items as input).

            The original item remains in the current shell's history list. Use
            the [[t]] command if you want to delete the item after the transfer.
        """
        self.shell.transfer_item( self )


    def key_q ( self, event ):
        """ Clear the current contents of the code buffer.

            The [[q]] key clears the contents of the code buffer after first
            copying its contents to the system clipboard. Thus if you
            accidentally press the [[q]] key, you can in effect undo the
            operation by pasting the clipboard back into the code buffer using
            the [[Ctrl-v]] key.
        """
        self.shell.delete_code()


    def key_x ( self, event ):
        """ Export this item to an external program or tool.

            The [[x]] key allows you to export the current shell item to an
            external program or tool that has been connected to the shell using
            the Facets [[tools]] architecture. Refer to the Facets documentation
            for more information on how to connect an external tool to the
            shell.
        """
        self.shell.export = self.item


    def key_end ( self, event ):
        """ Move this item to the bottom of the history list.
        """
        self.shell_move_to_bottom( self )


    def key_ctrl_end ( self, event ):
        """ Move this item and all related items to the bottom of the history
            list.
        """
        self.shell_move_to_bottom( self, True )


    def key_home ( self, event ):
        """ Move this item to the top of the history list.
        """
        self.shell_move_to_top( self )


    def key_ctrl_home ( self, event ):
        """ Move this item and all related items to the top of the history list.
        """
        self.shell_move_to_top( self, True )


    def key_1 ( self, event ):
        """ Toggle the display of items ids for all items.
        """
        self.shell_toggle_ids()


    def key_2 ( self, event ):
        """ Toggle the display of icons for all items.
        """
        self.shell_toggle_icons()


    def key_3 ( self, event ):
        """ Toggle the display of line numbers for all items.
        """
        self.shell_toggle_line_numbers()


    def key_4 ( self, event ):
        """ Cycle to the next available theme.

            The [[4]] key selects the next available shell theme. You also also
            press the [[o]] key to display the shell options dialog, which
            allows you to select a theme from a dropdown list of all available
            shell themes.
        """
        self.shell_cycle_theme()


    def key_delete ( self, event ):
        """ Hide this item in the history list.
        """
        self.shell_hide_item( self )


    def key_ctrl_delete ( self, event ):
        """ Delete all hidden items from the history list.
        """
        self.shell_delete_hidden( False )


    def key_ctrl_shift_delete ( self, event ):
        """ Delete all items from the history list.
        """
        self.shell_delete_all()


    def key_backspace ( self, event ):
        """ Hide all items like this one in the history list.

            The [[backspace]] key hides all shell items of the same type
            (e.g. Python result items) in the history list.
        """
        self.shell_hide_similar( self )


    def key_quote ( self, event ):
        """ Hide all duplicate items in the history list.

            The [[']] key hides all duplicate items in the history list. For all
            items of the same type with the same content, only the first item
            found in the history list remains visible.
        """
        self.shell_hide_duplicates()


    def key_equal ( self, event ):
        """ Show only non-hidden history items of the same type as this item.

            The [[=]] key hides all items in the history list which are not of
            the same type as the current item.

            Note that this command will not make hidden items of the same type
            as the current item visible again.
        """
        self.shell_show_similar( self )


    def key_minus ( self, event ):
        """ Hide this item and any associated items in the history list.

            The [[-]] key hides the current item and any items associated with
            it.

            If the item is a command, then all items the command generated are
            also hidden. If the item is not a command, then its parent command,
            and all items generated by its parent command, are also hidden.

            If you only wish to hide the items generated by a command, use the
            [[0]] command instead.
        """
        self.shell_show_hide_related( self )


    def key_0 ( self, event ):
        """ Hide any items generated by this item's related command.

            The [[0]] key hides all items generated by a command.

            If the current item is a command, then all items the command
            generated are hidden. If the item is not a command, then all items
            generated by its parent command are hidden.

            If you wish to hide all items associated with a command, including
            the command itself, use the [[-]] command instead.
        """
        self.shell_show_hide_related( self, include_command = False )


    def key_comma ( self, event ):
        """ Hide all items in the history list preceding this item.

            The [[,]] key hides the current item and all items preceding it in
            the history list.
        """
        self.shell_hide_preceding( self )


    def key_period ( self, event ):
        """ Hide all items in the history list following this item.

            The [[.]] key hides the current item and all items following it in
            the history list.
        """
        self.shell_hide_following( self )


    def key_left_bracket ( self, event ):
        """ Hide all history list items preceding this item with the same type.

            The [[[]] key hides the current item and all items of the same type
            preceding it in the history list.
        """
        self.shell_hide_preceding( self, True )


    def key_right_bracket ( self, event ):
        """ Hide all history list items following this item with the same type.

            The [[] ]]key hides the current item and all items of the same type
            following it in the history list.
        """
        self.shell_hide_following( self, True )


    def key_slash ( self, event ):
        """ Show all hidden items in the history list.

            The [[/]] key makes any previously hidden items in the history list
            visible again.
        """
        self.shell_show_all()


    def key_backslash ( self, event ):
        """ Hide all history list items between this item and the selection.

            The [[\]] key hides all items between and including the current item
            and the current selection. If there is no selection, only the
            current item is hidden.
        """
        self.shell_hide_to_selection( self )

    #-- Public Methods ---------------------------------------------------------

    def can_execute ( self ):
        """ Returns True if the item can be 'executed' in some meaningful
            fashion, and False if it cannot.
        """
        return False


    def execute ( self ):
        """ Executes some action for this item.
        """


    def display ( self, item ):
        """ Returns the finalized value to be displayed for the item.
        """
        return self.shell.colorize(
            self.add_line_numbers( self.add_id( item ) )
        )


    def add_id ( self, item ):
        """ Returns the *item* with its id added (if needed).
        """
        if self.show_id:
            return '\x009[%d]:%s %s' % ( self.id, self.color_code, item )

        return item


    def add_line_numbers ( self, item ):
        """ Returns the *item* with line numbers added (if needed).
        """
        if self.show_line_numbers:
            lines = item.split( '\n' )
            n     = len( lines )
            if n > 1:
                format = '\x008%%%dd|%s %%s' % ( len( str( n ) ),
                                                 self.color_code )
                item   = '\n'.join( [ format % ( (i + 1), t )
                                      for i, t in enumerate( lines ) ] )

        return item


    def str ( self, item ):
        """ Returns the string value of *item*.
        """
        return str( item ).rstrip()


    def filtered ( self, text ):
        """ Returns *text* after applying the current filter (if any).
        """
        filter = self.filter
        if (filter != '') and (filter != '~'):
            lines  = text.split( '\n' )
            filter = filter.lower()
            if filter[:1] == '~':
                negation = ''
                filter   = filter[1:]
                filtered = [ line for line in lines
                                  if line.lower().find( filter ) < 0 ]
            else:
                negation = 'not '
                filtered = [ line for line in lines
                                  if line.lower().find( filter ) >= 0 ]

            removed = len( lines ) - len( filtered )
            if removed > 0:
                filtered.insert( 0,
                    "\x00A[...%d line%s %scontaining '%s' filtered out...]"
                    "%s" % ( removed, 's'[ removed == 1: ], negation, filter,
                             self.color_code )
                )

            text = '\n'.join( filtered )

        return text


    def dispose ( self ):
        """ Disposes of the item when it is no longer needed.
        """


    def copy_clipboard ( self ):
        """ Copy the item to the clipboard.

            The [[c]] command copies the item, without any textual annotations
            such as item ids and line numbers, to the clipboard.

            You can use the [[Ctrl-c]] command to copy the item including all
            textual annotations to the clipboard.
        """
        toolkit().clipboard().text = remove_color( self.str( self.item ) )


    def save_file ( self ):
        """ Save the contents of the item to a file.

            The [[s]] key saves the current textual contents of a shell item,
            not including any textual annotations such as items ids or line
            numbers, to a file.

            A file dialog appears prompting you for the name and location of
            where to save the file. The file dialog defaults to saving the file
            in the shell's current working directory with a name of the form:
            vip_shell_<<item_id>>.txt, where <<item_id>> is the id associated
            with the shell item.
        """
        from file_item        import FileItem
        from python_file_item import PythonFileItem

        fd = FileDialog( default_path = self.file_name, action = 'save as' )
        if fd.open() == OK:
            self.file_name = file_name = fd.path
            ext            = splitext( file_name )[1]
            write_file( file_name, remove_color( self.str( self.item ) ) )
            self.shell.add_history_item_for(
                ( FileItem, PythonFileItem )[ ext == '.py' ], file_name
            )


    def increase_lod ( self ):
        """ Increase the level of detail of the item (if possible).
        """
        self.lod = min( self.maximum_lod, self.lod + 1 )


    def decrease_lod ( self ):
        """ Decrease the level of detail of the item (if possible).
        """
        self.lod = max( 0, self.lod - 1 )


    def shell_value ( self ):
        """ Returns the item as a value the user can manipulate in the shell.
        """
        return self.item


    def __repr__ ( self ):
        """ Returns the string representation of the object.
        """
        return repr( self.str( self.item ) )

    #-- Facet Default Values ---------------------------------------------------

    def _file_name_default ( self ):
        return join( self.shell.cwd,
                     'vip_shell_%d.%s' % ( self.id, self.file_ext ) )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'theme_state, selected, lod' )
    def _get_current_theme ( self ):
        return theme_manager.theme_for( self )


    def _get_stack_width ( self ):
        return self.context.control.parent.client_size[0]

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'show_id, show_line_numbers' )
    def _show_modified ( self ):
        """ Handles something that affects the item appearance being changed.
        """
        self.set_text()
        self.set_label()


    def _show_icon_set ( self ):
        """ Handles the visibility of the icon being changed.
        """
        self.set_image()
        self.set_label_image()


    def _hidden_set ( self ):
        """ Handles the 'hidden' facet being changed.
        """
        self.shell.refresh()


    def _filter_set ( self ):
        """ Handles the 'filter' facet being changed.
        """
        self.set_text()


    def _filter_clear_set ( self ):
        """ Handles the ;filer clear' button being clicked.
        """
        self.filter = ''


    @on_facet_set( 'tags[]' )
    def _tags_modified ( self, removed, added ):
        """ Handles the 'tags' facet being modified.
        """
        for tag in removed:
            tag.shell_item = None

        for tag in added:
            tag.shell_item = self

#-- EOF ------------------------------------------------------------------------
