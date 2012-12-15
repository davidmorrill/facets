"""
Defines the VIPShellEditor class that displays an advanced interactive Python
shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import string
import facets.extra.helper.profiler as profiler

from sys \
    import exc_info

from exceptions \
    import Exception

from os \
    import getcwd

from os.path \
    import abspath, basename, join, isdir, splitext, exists

from glob \
    import glob

from time \
    import time

from rlcompleter \
    import Completer

from facets.api                                                                \
    import HasPrivateFacets, Any, Int, Float, Tuple, Range, Bool, Str, Enum,   \
           Code, List, Instance, Property, Event, Callable, RGBInt, Font,      \
           File, Constant, DelegatesTo, Button, View, Tabbed, VGroup, VSplit,  \
           HGroup, Item, UItem, Handler, BasicEditorFactory, UIEditor,         \
           PropertySheetEditor, RangeEditor, RangeSliderEditor, StackEditor,   \
           HLSColorEditor, NotebookEditor, GridEditor, DNDEditor, spring,      \
           property_depends_on, toolkit, Undefined, push_exception_handler,    \
           pop_exception_handler, on_facet_set

from facets.core.debug \
    import Debug

from facets.core.facet_errors \
    import FacetNotificationError

from facets.core.facet_base \
    import read_file, write_file

from facets.ui.menu \
    import Action

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.graphics_text \
    import ColorTableCode

from facets.ui.i_filter \
    import Filter

from facets.ui.property_sheet_adapter \
    import PropertySheetAdapter

from facets.ui.key_bindings \
    import KeyBindings, KeyBinding

from facets.ui.editors.themed_checkbox_editor \
    import ThemedCheckboxEditor

from facets.ui.pyface.api \
    import FileDialog, OK

from facets.ui.pyface.timer.api \
    import do_later

from facets.ui.stack_item_toolbar \
    import StackItemToolbar, ToolbarDelay

from facets.ui.stack_item_resizer \
    import StackItemResizer

from facets.ui.stack_item_expander \
    import StackItemExpander

from facets.ui.vip_shell.themes \
    import ShellTheme, CycleTheme

from facets.ui.vip_shell.color_tables \
    import theme_color_tables, DefaultColors

from facets.ui.vip_shell.helper \
    import TypeCodes, ItemSet, trim_margin, remove_color, replace_markers, \
           python_colorize, as_lines, as_string, file_class_for

from facets.ui.vip_shell.items.api \
    import ShellItem, CommandItem, PersistedCommandItem, GeneratedItem,      \
           ResultItem, OutputItem, ErrorItem, ExceptionItem, CalledFromItem, \
           LogItem, LocalsItem

from facets.ui.vip_shell.commands.api \
    import ShellCommand, standard_shell_commands

from facets.extra.editors.control_grabber_editor \
    import ControlGrabberEditor

from facets.extra.tools.text_file \
    import TextFile

from facets.extra.helper.has_payload \
    import HasPayload

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Line separator used in FileItems to separate the header fomr the content:
LineSeparator = '_' * 90

# Standard sequence types:
SequenceType = ( list, tuple )

# The valid characters that can appear in a code context:
ValidChars = (string.ascii_letters + string.digits + '_.')

# The common toolbar actions supported by each shell item:
ShellToolbarActions = {
    'increase_lod':
        Action( image        = '@icons2:ArrowLargeUp',
                tooltip      = 'Increase item level of detail',
                action       = 'item.increase_lod',
                enabled_when = 'item.lod < item.maximum_lod' ),

    'decrease_lod':
        Action( image        = '@icons2:ArrowLargeDown',
                tooltip      = 'Decrease item level of detail',
                action       = 'item.decrease_lod',
                enabled_when = 'item.lod > 0' ),

    'execute':
        Action( image        = '@icons2:Gear?H98l18S58',
                tooltip      = 'Execute the item',
                action       = 'item.execute',
                enabled_when = 'item.can_execute()' ),

    'delete':
        Action( image        = '@icons2:Delete',
                tooltip      = 'Hide item',
                action       = 'item.shell_hide_item(item)',
                visible_when = 'not item.detached' ),

    'new_window':
        Action( image        = '@icons2:Document_1?H98l24S19',
                tooltip      = 'Display item in a new window',
                action       = 'item.shell_tear_off_item(item)' ),

    'new_tab':
        Action( image        = '@icons2:EditTab?H48l10|H21l58',
                tooltip      = 'Display item in a new tab',
                action       = 'item.shell_add_code_item(item)' ),

    'save_file':
        Action( image        = '@icons2:Floppy?H95l16',
                tooltip      = 'Save item to a file',
                action       = 'item.save_file' ),

    'copy_clipboard':
        Action( image        = '@icons2:ClipboardCopy?Hl9S74|l77',
                tooltip      = 'Copy item to the clipboard',
                action       = 'item.copy_clipboard' ),

    'options':
        Action( image        = '@icons2:Tool_2?H58l7',
                tooltip      = 'Display shell options',
                action       = 'item.shell_edit_options',
                visible_when = 'not item.detached' ),

    'toggle_ids':
        Action( image        = '@icons2:CreditCard',
                tooltip      = 'Toggle item ids',
                action       = 'item.shell_toggle_ids',
                visible_when = 'not item.detached' ),

    'toggle_icons':
        Action( image        = '@icons:blue_ball_l',
                tooltip      = 'Toggle item icons',
                action       = 'item.shell_toggle_icons',
                visible_when = 'not item.detached' ),

    'toggle_line_numbers':
        Action( image        = '@icons:numbers',
                tooltip      = 'Toggle item line numbers',
                action       = 'item.shell_toggle_line_numbers',
                visible_when = 'not item.detached' ),

    'custom':
        None
}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def toggle_item ( item ):
    """ Toggles the value of a property sheet boolean value.
    """
    setattr( item.object, item.name, not getattr( item.object, item.name ) )

#-------------------------------------------------------------------------------
#  'DebugAdapter' class:
#-------------------------------------------------------------------------------

class DebugAdapter ( PropertySheetAdapter ):
    """ Adapts the Debug object for use with the PropertySheetEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of facets to display in the property sheet:
    facets = List( [
        'debug_enabled', 'info_enabled', 'warning_enabled', 'error_enabled',
        'critical_enabled', 'called_from_enabled', 'show_locals_enabled'
    ] )

    paint = 'Bool'
    mode  = Callable( toggle_item )

    debug_enabled_label       = Str( "Display debug requests" )
    info_enabled_label        = Str( "Display info requests" )
    warning_enabled_label     = Str( "Display warning requests" )
    error_enabled_label       = Str( "Display error requests" )
    critical_enabled_label    = Str( "Display critical requests" )
    called_from_enabled_label = Str( "Display called_from requests" )
    show_locals_enabled_label = Str( "Display show_locals requests" )

#-------------------------------------------------------------------------------
#  'ControlGrabberAdapter' class:
#-------------------------------------------------------------------------------

class ControlGrabberAdapter ( PropertySheetAdapter ):
    """ Adapts the editor's 'control grabber' related items for use with the
        PropertySheetEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of facets to display in the property sheet:
    facets = List( [
        'show_control', 'show_editor', 'show_object', 'show_value'
    ] )

    show_control_paint = Str( 'Bool' )
    show_editor_paint  = Str( 'Bool' )
    show_object_paint  = Str( 'Bool' )
    show_value_paint   = Str( 'Bool' )

    show_control_mode  = Callable( toggle_item )
    show_editor_mode   = Callable( toggle_item )
    show_object_mode   = Callable( toggle_item )
    show_value_mode    = Callable( toggle_item )

    show_control_label = Str( "Display control adapter" )
    show_editor_label  = Str( "Display editor" )
    show_object_label  = Str( "Display object" )
    show_value_label   = Str( "Display object value" )

#-------------------------------------------------------------------------------
#  'ToolbarInfoGridAdapter' class:
#-------------------------------------------------------------------------------

class ToolbarInfoGridAdapter ( GridAdapter ):

    columns = [
        ( 'Action', 'name'   ),
        ( 'Left',   'left'   ),
        ( 'Middle', 'middle' ),
        ( 'Right',  'right'  ),
    ]

    left_width       = Float( 50 )
    middle_width     = Float( 50 )
    right_width      = Float( 50 )

    left_alignment   = Constant( 'center' )
    middle_alignment = Constant( 'center' )
    right_alignment  = Constant( 'center' )

    left_paint       = Str( 'Bool' )
    middle_paint     = Str( 'Bool' )
    right_paint      = Str( 'Bool' )

    def left_clicked ( self ):
        self.toggle_item( 'left' )

    def middle_clicked ( self ):
        self.toggle_item( 'middle' )

    def right_clicked ( self ):
        self.toggle_item( 'right' )

    def toggle_item ( self, name ):
        setattr( self.item, name, not getattr( self.item, name ) )
        self.refresh = True

#-------------------------------------------------------------------------------
#  'ActionInfo' class:
#-------------------------------------------------------------------------------

class ActionInfo ( HasPrivateFacets ):
    """ Defines which toolbars an action applies to.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The unique id assigned to the action this applies to:
    id = Str

    # User interface name of the action this applies to:
    name = Str

    # Does the action appear in the left toolbar?
    left = Bool( False )

    # Does the action appear in the middle toolbar?
    middle = Bool( False )

    # Does the action appear in the right toolbar?
    right = Bool( False )

#-------------------------------------------------------------------------------
#  'ToolbarInfo' class:
#-------------------------------------------------------------------------------

class ToolbarInfo ( HasPrivateFacets ):
    """ Describes the contents of each VIP Shell toolbar.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of action info for each toolbar item:
    action_info = List( ActionInfo )

    # The delay time (in milliseconds) before displaying the toolbar:
    toolbar_delay = ToolbarDelay

    # Event fired when any action info item is modified:
    modified = Event

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'action_info',
                  editor = GridEditor( adapter    = ToolbarInfoGridAdapter,
                                       operations = [] )
            ),
            show_labels = False
        ),
        '_',
        VGroup(
            Item( 'toolbar_delay',
                  label   = 'Delay',
                  tooltip = 'Delay before displaying toolbar (in milliseconds)',
                  editor  = RangeEditor( body_style = 25 )
            )
        )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _action_info_default ( self ):
        return [
            ActionInfo( id   = 'delete',
                        name = 'Hide item',
                        left = True, middle = False, right = True ),
            ActionInfo( id   = 'increase_lod',
                        name = 'Increase item level of detail',
                        left = False, middle = True, right = True ),
            ActionInfo( id   = 'decrease_lod',
                        name = 'Decrease item level of detail',
                        left = False, middle = True, right = True ),
            ActionInfo( id   = 'execute',
                        name = 'Execute item',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'new_window',
                        name = 'Display item in a new window',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'new_tab',
                        name = 'Display item in a new tab',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'save_file',
                        name = 'Save item to a file',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'copy_clipboard',
                        name = 'Copy item to the clipboard',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'options',
                        name = 'Display shell options',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'toggle_ids',
                        name = 'Toggle item ids',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'toggle_icons',
                        name = 'Toggle item icons',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'toggle_line_numbers',
                        name = 'Toggle item line numbers',
                        left = False, middle = False, right = True ),
            ActionInfo( id   = 'custom',
                        name = 'Display custom item actions',
                        left = False, middle = False, right = True ),
        ]

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'action_info.+' )
    def _contents_modified ( self ):
        self.modified = True

#-------------------------------------------------------------------------------
#  'ShellItemToolbar' class:
#-------------------------------------------------------------------------------

class ShellItemToolbar ( StackItemToolbar ):
    """ Custom toolbar class for use with shell items.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The opacity used for drawing in the 'triggered' state:
    trigger_opacity = 0.2

    # The trigger radius for initially activating the toolbar:
    trigger_radius = Property

    # The list of toolbar actions (override):
    actions = Property

    # The delay time (in milliseconds) before displaying the toolbar (override):
    toolbar_delay = Property

    # The VIP Shell this toolbar is associated with:
    shell = Any # Instance( vipShellEditor )

    # The position of this toolbar relative to a shell item:
    position = Enum( 'left', 'middle', 'right' )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'item, shell:toolbar_info:modified' )
    def _get_actions ( self ):
        toolbar_info = self.shell.toolbar_info
        result       = []
        item         = self.item
        if item is not None:
            position    = self.position
            environment = globals()
            context     = { 'item': item }
            for info in toolbar_info.action_info:
                if getattr( info, position ):
                    actions = ShellToolbarActions[ info.id ]
                    if actions is None:
                        actions = item.actions
                    else:
                        actions = [ actions ]

                    for action in actions:
                        if ((action.visible_when == '') or
                            eval( action.visible_when, environment, context )):
                            result.append( action )

        return result


    def _get_toolbar_delay ( self ):
        return self.shell.toolbar_info.toolbar_delay


    def _get_trigger_radius ( self ):
        radius = ((22 * len( self.actions )) + 5)
        if self.position == 'middle':
            radius /= 2

        return radius

#-------------------------------------------------------------------------------
#  'vipShellColorTableEditor' class:
#-------------------------------------------------------------------------------

# Define a custom property for handling shell colors:
def get_shell_color ( self, name ):
    return self.colors[ int( name[1:] ) ]

def set_shell_colors ( self, name, value ):
    self.colors[ int( name[1:] ) ] = value[:3]

AShellColor = Property( get_shell_color, set_shell_colors )

# Define a custom view Item for shell colors:
class AShellColorItem ( Item ):
    editor = HLSColorEditor( cell_size = 17, cells = 9, border = 1, space = 0 )

class vipShellColorTableEditor ( UIEditor ):
    """ Defines an editor used to edit the color table codes for use with the
        VIP Shell's GraphicsText objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Representation of the various color table values:
    c0  = AShellColor
    c1  = AShellColor
    c2  = AShellColor
    c3  = AShellColor
    c4  = AShellColor
    c5  = AShellColor
    c6  = AShellColor
    c7  = AShellColor
    c8  = AShellColor
    c9  = AShellColor
    c10 = AShellColor
    c11 = AShellColor
    c12 = AShellColor
    c13 = AShellColor
    c14 = AShellColor
    c15 = AShellColor
    c16 = AShellColor
    c17 = AShellColor
    c18 = AShellColor
    c19 = AShellColor

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        AShellColorItem( 'c0',  label = 'Output item (stdout)' ),
        AShellColorItem( 'c1',  label = 'Error item (stderr)'  ),
        AShellColorItem( 'c2',  label = 'Result item'          ),
        AShellColorItem( 'c3',  label = 'Shell command item'   ),
        AShellColorItem( 'c4',  label = 'Exception item'       ),
        AShellColorItem( 'c5',  label = 'Directory item'       ),
        AShellColorItem( 'c6',  label = 'File item'            ),
        AShellColorItem( 'c7',  label = 'Python file item'     ),
        AShellColorItem( 'c8',  label = 'Line numbers'         ),
        AShellColorItem( 'c9',  label = 'Item Id'              ),
        AShellColorItem( 'c10', label = 'Omitted data'         ),
        AShellColorItem( 'c11', label = 'Emphasized'           ),
        AShellColorItem( 'c12', label = 'Example'              ),
        AShellColorItem( 'c13', label = 'Error'                ),
        AShellColorItem( 'c14', label = 'Python normal'        ),
        AShellColorItem( 'c15', label = 'Python literal'       ),
        AShellColorItem( 'c16', label = 'Python number'        ),
        AShellColorItem( 'c17', label = 'Python keyword'       ),
        AShellColorItem( 'c18', label = 'Python comment'       ),
        AShellColorItem( 'c19', label = 'Python special'       )
    )

    # The set of all colors in the current color table:
    colors = List

    # A dummy color defined just to avoid property errors:
    dummy_color = RGBInt( 0xFF0000 )

    #-- Facet Default Values ---------------------------------------------------

    def _colors_default ( self ):
        return ([ self.dummy_color ] * 20)

    #-- UIEditor Method Overrides ----------------------------------------------

    def init_ui ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        return self.edit_facets( parent = parent, kind = 'editor' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        colors = self.value
        n      = len( colors ) - 2
        if ((colors[:1] == ColorTableCode) and
            (colors[-1:] == '.') and ((n % 6) == 0)):
            self.colors = [ self._text_to_color( colors[ i: i + 6 ] )
                            for i in xrange( 1, n, 6 ) ]

            for i in xrange( len( self.colors ) ):
                self.facet_property_set( 'c%d' % i, self.dummy_color )

    #-- Facet Event Handlers ---------------------------------------------------

    def _colors_items_set ( self ):
        """ Handles any of the color table entries being changed.
        """
        self.value = '\x02%s.' % (''.join( [ '%02X%02X%02X' % c
                                             for c in self.colors ] ))

    #-- Private Methods --------------------------------------------------------

    def _text_to_color ( self, rrggbb ):
        """ Converts a text *rrggbb* string to a color value for the *index*th
            color table entry.
        """
        return tuple(
            [ int( rrggbb[ i: i + 2 ], 16 ) for i in xrange( 0, 6, 2 ) ]
        )

#-------------------------------------------------------------------------------
#  'VIPShellColorTableEditor' class:
#-------------------------------------------------------------------------------

class VIPShellColorTableEditor ( BasicEditorFactory ):

    # The class used to construct editor objects:
    klass = vipShellColorTableEditor

#-------------------------------------------------------------------------------
#  'StdFile' class:
#-------------------------------------------------------------------------------

class StdFile ( HasPrivateFacets ):
    """ A pseudo-file used to temporarily override stdout or stderr.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The type of file being overridden:
    type = Str

    # The original handle for stdout/stderr:
    file = Any

    # The output written to the file:
    output = Any( [] ) # List( Str )

    # Should normal Python 'print' soft spaces be allowed?
    softspace = Any( 0 )

    # Flag set when data has been written to the file:
    has_data = Bool( False )

    #-- Facet Event Handlers ---------------------------------------------------

    def _type_set ( self, type ):
        """ Handles the 'type' facet being changed.
        """
        self.file = getattr( sys, type )
        setattr( sys, type, self )

    #-- Public Methods ---------------------------------------------------------

    def __call__ ( self ):
        """ Restores the orginal stdout or stderr file handle and returns any
            output written to the pseudo-file.
        """
        setattr( sys, self.type, self.file )

        return ''.join( self.output )

    #-- Python 'file' Interface ------------------------------------------------

    def write ( self, text ):
        """ Write *text* to the output.
        """
        self.output.append( text )
        self.has_data = True


    def flush ( self ):
        """ Flushes the buffer.
        """

#-------------------------------------------------------------------------------
#  'HistoryFilter' class:
#-------------------------------------------------------------------------------

class HistoryFilter ( Filter ):
    """ Filters the results of a shell's history.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The text being filtered on:
    text = Str

    # Should commands be included in the filter?
    commands = Bool( True )

    # Should results be included in the filter?
    results = Bool( True )

    # Should output be included in the filter?
    output = Bool( True )

    # Should error output be included in the filter?
    errors = Bool( True )

    # Should exceptions be included in the filter?
    exceptions = Bool( True )

    # Should files be included in the filter?
    files = Bool( True )

    # Should views be included in the filter?
    views = Bool( True )

    # The list of currently included history item types:
    types = Property

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HGroup(
            UItem( 'commands',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@facets:shell_command',
                       off_image   = '@facets:shell_command?s90L30',
                       on_tooltip  = 'Display shell commands (click to hide)',
                       off_tooltip = 'Hide shell commands (click to display)' )
            ),
            UItem( 'results',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@facets:shell_result',
                       off_image   = '@facets:shell_result?s90L30',
                       on_tooltip  = 'Display shell results (click to hide)',
                       off_tooltip = 'Hide shell results (click to display)' )
            ),
            UItem( 'output',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@facets:shell_output',
                       off_image   = '@facets:shell_output?s90L30',
                       on_tooltip  = 'Display shell output (click to hide)',
                       off_tooltip = 'Hide shell output (click to display)' )
            ),
            UItem( 'errors',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@facets:shell_error',
                       off_image   = '@facets:shell_error?s90L30',
                       on_tooltip  = 'Display shell errors (click to hide)',
                       off_tooltip = 'Hide shell errors (click to display)' )
            ),
            UItem( 'exceptions',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@facets:shell_exception',
                       off_image   = '@facets:shell_exception?s90L30',
                       on_tooltip  = 'Display shell exceptions (click to hide)',
                       off_tooltip = 'Hide shell exceptions (click to display)')
            ),
            UItem( 'files',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@facets:shell_file',
                       off_image   = '@facets:shell_file?s90L30',
                       on_tooltip  = 'Display shell files (click to hide)',
                       off_tooltip = 'Hide shell files (click to display)' )
            ),
            UItem( 'views',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@facets:shell_view',
                       off_image   = '@facets:shell_view?s90L30',
                       on_tooltip  = 'Display shell views (click to hide)',
                       off_tooltip = 'Hide shell views (click to display)' )
            ),
            '_',
            Item( 'text', label = 'Filter', springy = True ),
            group_theme = '#themes:toolbar_group'
        )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'commands, results, output, errors, exceptions, files, views' )
    def _get_types ( self ):
        types = set()

        if self.commands:
            types.add( 'command' )

        if self.results:
            types.add( 'result' )

        if self.output:
            types.add( 'output' )

        if self.errors:
            types.add( 'error' )

        if self.exceptions:
            types.add( 'exception' )

        if self.files:
            types.add( 'file' )

        if self.views:
            types.add( 'view' )

        return types

    #-- Public Methods ---------------------------------------------------------

    def filter ( self, item ):
        """ Returns whether or not the specified *item* should be included in
            the filter results.
        """
        text   = self.text.strip().lower()
        result = ((item.type in self.types) and
                  (not item.hidden)         and
                  ((text == '') or (item.text.lower().find( text ) >= 0)))

        # Mark the item as being made hidden/visible by the filter so that the
        # item can make any necessary adjustments (e.g. ViewItem):
        item.filter_hidden = (not result)

        return result

#-------------------------------------------------------------------------------
#  'VIPShellProxy' class:
#-------------------------------------------------------------------------------

class VIPShellProxy ( HasPrivateFacets ):
    """ A proxy for the main shell editor object that can be inserted into the
        shell's 'locals' dictionary to give the user access to a subset of the
        shell's functionality, particularly with regard to access to the shell
        history.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The shell object this is a proxy for:
    shell = Any # Instance( vipShellEditor )

    # Reference to base class for new shell commands:
    ShellCommand = Constant( ShellCommand )

    #-- Public Methods ---------------------------------------------------------

    def __getitem__ ( self, index ):
        """ Returns the shell history item at the specified *index*.
        """
        result = self.shell.item_at( index )
        if isinstance( result, list ):
            return [ item.shell_value() for item in result ]

        return result.shell_value()


    def __call__ ( self, klass, value ):
        """ Returns a new history shell item of the specified *klass* and with
            the specified item *value*.
        """
        return self.shell.history_item_for( klass, value )

#-------------------------------------------------------------------------------
#  'VIPShellAdapter' class:
#-------------------------------------------------------------------------------

class VIPShellAdapter ( PropertySheetAdapter ):
    """ Adapts the VIPShellEditor for use with the PropertySheetEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of facets to display in the property sheet:
    facets = List( [
        'show_filter', 'show_status', 'show_id', 'show_icon',
        'show_line_numbers', 'theme', 'font', 'threshold', 'max_items',
        'context', 'expander_zone'
    ] )

    show_filter_paint           = Str( 'Bool' )
    show_status_paint           = Str( 'Bool' )
    show_id_paint               = Str( 'Bool' )
    show_icon_paint             = Str( 'Bool' )
    show_line_numbers_paint     = Str( 'Bool' )

    show_filter_label           = Str( 'Show filter bar' )
    show_status_label           = Str( 'Show status bar' )
    show_id_label               = Str( 'Show IDs' )
    show_icon_label             = Str( 'Show icons' )
    show_line_numbers_label     = Str( 'Show line numbers' )
    threshold_label             = Str( 'Maximum lines threshold' )
    max_items_label             = Str( 'Maximum collection items' )
    context_label               = Str( 'Traceback context lines' )
    expander_zone_label         = Str( 'Level of detail expander zone' )

    expander_zone_show_children = Bool( False )

    show_filter_mode            = Callable( toggle_item )
    show_status_mode            = Callable( toggle_item )
    show_id_mode                = Callable( toggle_item )
    show_icon_mode              = Callable( toggle_item )
    show_line_numbers_mode      = Callable( toggle_item )
    font_mode                   = Str( 'popout' )
    threshold_mode              = Str( 'popout' )
    max_items_mode              = Str( 'popout' )
    context_mode                = Str( 'popout' )
    expander_zone_mode          = Str( 'popout' )

#-------------------------------------------------------------------------------
#  'VIPShellHandler' class:
#-------------------------------------------------------------------------------

class VIPShellHandler ( Handler ):
    """ Handles keyboard events for the VIP shell code editor.
    """

    #-- Keyboard Event Handlers ------------------------------------------------

    def do_code ( self, info ):
        """ Handles a request to execute the current code.
        """
        self._shell_for( info ).do_code()


    def complete_code ( self, info ):
        """ Handles a request to perform code completion.
        """
        self._shell_for( info ).complete_code( info.text )


    def previous_command ( self, info ):
        """ Handles a request to scroll to the previous command executed.
        """
        self._shell_for( info ).previous_command()


    def next_command ( self, info ):
        """ Handles a request to scroll to the next command executed.
        """
        self._shell_for( info ).next_command()


    def previous_item ( self, info ):
        """ Handles a request to scroll to the previous history item.
        """
        self._shell_for( info ).previous_item()


    def next_item ( self, info ):
        """ Handles a request to scroll to the next history item.
        """
        self._shell_for( info ).next_item()


    def delete_hidden ( self, info ):
        """ Handles a request to delete all hidden history items.
        """
        self._shell_for( info ).delete_hidden( False )


    def delete_all ( self, info ):
        """ Handles a request to delete all history items.
        """
        self._shell_for( info ).delete_all()


    def delete_code ( self, info ):
        """ Handles a request to delete the contents of the code buffer.
        """
        info.object.file_name = ''
        self._shell_for( info ).delete_code()


    def undo_command ( self, info ):
        """ Hides the bottommost history item and its related items.
        """
        self._shell_for( info ).undo_command()


    def redo_command ( self, info ):
        """ Shows the first hidden item (and its related items) after the
            bottommost visible history item.
        """
        self._shell_for( info ).redo_command()


    def edit_options ( self, info ):
        """ Handles a request to edit the editor's user preference options.
        """
        self._shell_for( info ).edit_options()


    def new_tab ( self, info ):
        """ Creates a new, empty shell code editor tab.
        """
        self._shell_for( info ).add_code_item()


    def toggle_filter ( self, info ):
        """ Toggle the filter bar on or off.
        """
        self._shell_for( info ).toggle_filter()


    def toggle_status ( self, info ):
        """ Toggle the status bar on or off.
        """
        self._shell_for( info ).toggle_status()


    def clone_tab ( self, info ):
        """ Creates a new shell code editor tab with the same initial contents
            as this tab.
        """
        info.context.clone_tab()


    def save_file ( self, info ):
        """ Saves the contents of the code editor to a file.
        """
        info.context.save_file()


    def save_as_file ( self, info ):
        """ Saves the contents of the code editor to a user specified file.
        """
        info.context.save_as_file()

    #-- Private Methods --------------------------------------------------------

    def _shell_for ( self, info ):
        """ Returns the VIP Shell object associated with this code item.
        """
        code_item       = info.context
        shell           = code_item.shell
        shell.code_item = code_item

        return shell

#-------------------------------------------------------------------------------
#  Shell Code Editor Keybindings:
#-------------------------------------------------------------------------------

ShellKeyBindings = KeyBindings( [
    KeyBinding( binding = 'Ctrl-Enter',        method = 'do_code',
                rebinding = 'Ctrl-Shift-Enter'                             ),
    KeyBinding( binding = 'Ctrl-Tab',          method = 'complete_code'    ),
    KeyBinding( binding = 'Ctrl-Up',           method = 'previous_command' ),
    KeyBinding( binding = 'Ctrl-Down',         method = 'next_command'     ),
    KeyBinding( binding = 'Alt-Ctrl-Shift-Up',   method = 'previous_item'  ),
    KeyBinding( binding = 'Alt-Ctrl-Shift-Down', method = 'next_item'      ),
    KeyBinding( binding = 'Ctrl-Delete',       method = 'delete_hidden'    ),
    KeyBinding( binding = 'Ctrl-Shift-Delete', method = 'delete_all'       ),
    KeyBinding( binding = 'Ctrl-b',            method = 'undo_command'     ),
    KeyBinding( binding = 'Ctrl-o',            method = 'edit_options'     ),
    KeyBinding( binding = 'Ctrl-Shift-b',      method = 'redo_command'     ),
    KeyBinding( binding = 'Ctrl-q',            method = 'delete_code'      ),
    KeyBinding( binding = 'Ctrl-s',            method = 'save_file',
                alt_binding = 'F2'                                         ),
    KeyBinding( binding = 'Ctrl-Shift-s',      method = 'save_as_file'     ),
    KeyBinding( binding = 'Ctrl-t',            method = 'new_tab'          ),
    KeyBinding( binding = 'Ctrl-Shift-t',      method = 'clone_tab'        ),
    KeyBinding( binding = 'F3',                method = 'toggle_filter'    ),
    KeyBinding( binding = 'F4',                method = 'toggle_status'    ),
],
    controllers = [ VIPShellHandler() ]
)

#-------------------------------------------------------------------------------
#  'VIPShellCode' class:
#-------------------------------------------------------------------------------

class VIPShellCode ( HasPrivateFacets ):
    """ Defines an object used to edit Python source code within the VIP Shell.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The TextFile instance used to perform the actual editing:
    text_file = Instance( TextFile, { 'key_bindings': ShellKeyBindings } )

    # The shell this code item is associated with:
    shell = Any # Instance( vipShellEditor )

    # The (optional) name of the Python source file associated with this editor:
    file_name = DelegatesTo( 'text_file.file_name' )

    # The Python source code being edited:
    code = DelegatesTo( 'text_file.text' )

    # The current position of the code editor cursor:
    code_line   = DelegatesTo( 'text_file.line' )
    code_column = DelegatesTo( 'text_file.column' )

    # The currently selected line in the code editor:
    selected_line = DelegatesTo( 'text_file.selected_line' )

    # The name of this code item:
    name = Property

    # The persistence id to use with the view:
    id = Str

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'text_file', style = 'custom' ),
            title     = self.file_name or 'VIP Shell Code Editor',
            id        = self.id,
            width     = 0.40,
            height    = 0.75,
            resizable = True
        )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'file_name' )
    def _get_name ( self ):
        if self.file_name != '':
            return basename( self.file_name )

        return '<shell>'

    #-- Public Methods ---------------------------------------------------------

    def save_file ( self ):
        """ Saves the code to a file.
        """
        if self.file_name[:1] == '<':
            self.save_as_file()
        else:
            self.save_as_file( self.file_name )


    def save_as_file ( self, file_name = '' ):
        """ Saves the code to a file.
        """
        shell = self.shell
        if file_name == '':
            file_name = self.file_name or 'vip_shell.py'
            if file_name[:1] == '<':
                file_name = file_name[1:-1].replace( ':', '_' )

            fd = FileDialog(
                default_path = join( shell.cwd, file_name ),
                action       = 'save as'
            )
            if fd.open() != OK:
                return

            file_name = fd.path

        if write_file( file_name, self.code ):
            self.file_name = file_name
            shell.status   = 'Saved: %s' % file_name

        else:
            self.status = 'Error writing: %s' % file_name


    def clone_tab ( self ):
        """ Creates a new shell code editor tab with the same initial contents
            as this tab.
        """
        self.shell.add_code_item( VIPShellCode( file_name = self.file_name,
                                                code      = self.code ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        """ Handles the 'file_name' facet being changed.
        """
        if self.code == '':
            self.code = read_file( file_name ) or ''
            self.text_file.modified = False

#-------------------------------------------------------------------------------
#  'VIPShellItem' class:
#-------------------------------------------------------------------------------

class VIPShellItem ( HasPrivateFacets ):
    """ A container for displaying ShellItem's in a popup window.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The display name of the shell item:
    name = Str

    # The shell item being displayed:
    item = Any

    # The list of shell items being displayed:
    items = List

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'items',
              id         = 'items',
              show_label = False,
              editor     = StackEditor()
        ),
        title  = 'VIP Shell Item',
        id     = 'facets.ui.editors.vip_shell_editor.VIPShellItem',
        width  = 0.33,
        height = 0.75
    )

    #-- Facet Default Values ---------------------------------------------------

    def _name_default ( self ):
        return ('<item_%d>' % self.items[0].id)


    def _items_default ( self ):
        return [ self.item ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _item_set ( self, item ):
        """ Handles the 'item' facet being changed.
        """
        if item is not None:
           item.detached = True

#-------------------------------------------------------------------------------
#  'vipShellEditor' class:
#-------------------------------------------------------------------------------

class vipShellEditor ( UIEditor ):
    """ Defines an editor that displays a visual interactive Python shell.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the shell editor is scrollable? This value overrides the default.
    scrollable = True

    # An event fired whenever the user executes a command in the shell:
    executed = Event( Bool )

    # An external command to be executed by the interpreter:
    command = Event

    # The result from the most recently executed command:
    result = Event

    # The currently executing command (if any):
    active_command = Any # Instance( CommandItem )

    # The most recently executed command:
    last_command = Any # Instance( CommandItem )

    # The 'locals' dictionary used when executing a Python command:
    locals = Any

    # The completer to use for finding code completions:
    completer = Any

    # The most recent code completer context used:
    completer_context = Str( None )

    # The singleton facets 'debug' instance:
    debug = Constant( Debug() )

    # The currently selected shell code item:
    code_item = Instance( VIPShellCode )

    # The list of all active code items:
    code_items = List # ( Instance( CodeItem ) )

    # The current command being edited:
    code = DelegatesTo( 'code_item' )

    # The current position of the code editor cursor:
    code_line   = DelegatesTo( 'code_item' )
    code_column = DelegatesTo( 'code_item' )

    # Are the contents of the code editor locked?
    code_locked = Bool( False )

    # Event fired when code buffer is to be cleared:
    code_delete = Button( '@icons2:Delete?H49l8s20' )

    # Event fired when the clipboard is to be pasted into the code buffer:
    code_paste = Button( '@icons2:ClipboardPaste?l25s42' )

    # Event fired when the shell options dialog should be displayed:
    show_options = Button( '@icons2:Tool_2?H11l9s32|s39' )

    # Event fired when the shell help information should be displayed:
    show_help = Button( '@icons2:Info?H48s14' )

    # Should every successfully executed command be logged as a new entry to the
    # history (True), or should the most recent successfully executed command
    # replace any previous version of the same command in the history (False)?
    log_all = Bool( True )

    # The shell history:
    history = List

    # User specified initialization code:
    initialize = Code

    # The currently selected history item:
    selected = Any

    # The most recently exported item:
    export = Any

    # The most recently sent local item:
    send = Instance( ShellItem )

    # The most recently received external item:
    receive = Instance( ShellItem )

    # A value dropped onto the editor:
    dropped_value = Event

    # The event fired when the underlying stack editor needs to be
    # re-synchronized with the contents of the shell history:
    changed = Event

    # The next available history item id:
    id = Int( -1 )

    # The most recently referenced shell history command id used for scrolling:
    scroll_id = Int

    # Should the filter be displayed?
    show_filter = Bool( True )

    # Should the status bar be displayed?
    show_status = Bool( True )

    # Should the id for all items be displayed?
    show_id = Bool( False )

    # Should the icon for all items be displayed?
    show_icon = Bool( False )

    # Should line numbers be displayed for all items:
    show_line_numbers = Bool( False )

    # 'Control grabber' display options:
    show_control = Bool( False )
    show_editor  = Bool( False )
    show_object  = Bool( True )
    show_value   = Bool( False )

    # Should the code buffer be cleared if the current command executes
    # successfully?
    clear_buffer = Bool( True )

    # Is timing active for the current command?
    timing = Bool( False )

    # Is profiling active for the current command?
    profiling = Bool( False )

    # Should the profiling results be printed?
    print_profile = Bool( False )

    # The name of the most recently created profiler data file:
    profile = File

    # The current status message or the shell:
    status = Str

    # The current editor theme:
    theme = ShellTheme

    # The current color table being used to encode text:
    color_table = Str( DefaultColors )

    # The color tables associated with the various themes:
    color_tables = Any # Dict( Str, Str )

    # Resets the current theme color table back to the factory defaults:
    reset_colors = Button( 'Reset colors' )

    # The (optional) filter used to filter the shell history:
    filter = Instance( HistoryFilter, () )

    # The threshold number of item lines to display before eliding results:
    threshold = Int( 21,
        facet_value = True,
        editor = RangeEditor( low = 10, high = 1000, body_style = 25 )
    )

    # The maximum number of list/tuple/dict items to display in a result:
    max_items = Int( 100,
        facet_value = True,
        editor      = RangeEditor( low = 0, high = 500, body_style = 25 )
    )

    # The number of context lines to display in tracebacks:
    context = Int( 7,
        facet_value = True,
        editor      = RangeEditor( low = 0, high = 50, body_style = 25 )
    )

    # The position and size of the level of detail expander tool overlay:
    expander_zone = Tuple( ( 0, 60 ),
        editor = RangeSliderEditor( low = 0, high = 1000, body_style = 25 )
    )

    # The shell proxy added to the shell's 'locals' dictionary:
    proxy = Instance( VIPShellProxy, () )

    # The external shell commands that have been registered (the keys are the
    # command names, and the values are 2 elements lists of the form:
    # [ command_class, command_file_name ], where 'command_class' is a subclass
    # of ShellCommand, and 'command_file_name' is the name of the file
    # defining the class):
    registry = Any( {} )

    # The name of the file currently being executed by the 'execute_file'
    # method (or the empty string if 'execute_file' is not active):
    exec_file_name = Str

    # The most recently referenced list of 'execfile' file names:
    mru_execfile_names = Any( [] )

    # The font to use:
    font = Font( 'Consolas Bold 9, Courier Bold 9' )

    # The current working directory:
    cwd = Str

    # Key used to pop the facet notification exception handler stack:
    exception_handler_key = Any

    # The stdout/stderr files used to capture asynchronous output:
    stdout = Instance( StdFile )
    stderr = Instance( StdFile )

    # The original value of the 'sys.excepthook' handler:
    excepthook = Any

    # A mapping from command ids to command text (used for tracebacks):
    id_map = Any( {} ) # { id: command_text }

    # The shell item toolbars:
    left_toolbar   = Instance( ShellItemToolbar )
    middle_toolbar = Instance( ShellItemToolbar )
    right_toolbar  = Instance( ShellItemToolbar )

    # The shell item resizer:
    resizer = Instance( StackItemResizer, () )

    # The shell item expander:
    expander = Instance( StackItemExpander, () )

    # The user preference toolbar info for this shell:
    toolbar_info = Instance( ToolbarInfo, () )

    # The most recently grabbed control using the 'control grabber' editor:
    grabbed_control = Any # Instance( Control )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'filter',
              show_label   = False,
              style        = 'custom',
              visible_when = 'show_filter'
        ),
        VSplit(
            Item( 'history',
                  id         = 'history',
                  show_label = False,
                  dock       = 'horizontal',
                  editor     = StackEditor(
                      filter     = 'filter',
                      changed    = 'changed',
                      auto_focus = True
                  )
            ),
            Item( 'code_items',
                  show_label = False,
                  dock       = 'horizontal',
                  editor     = NotebookEditor(
                      deletable  = True,
                      dock_style = 'auto',
                      export     = 'DockWindowShell',
                      page_name  = '.name',
                      selected   = 'code_item'
                  )
            ),
            id = 'splitter'
        ),
        HGroup(
            Item( 'grabbed_control',
                  editor  = ControlGrabberEditor(),
                  tooltip = 'Click-drag over a control to display information '
                            'about it'
            ),
            Item( 'dropped_value',
                  style   = 'custom',
                  editor  = DNDEditor(
                      image = '@icons2:ArrowLargeDown?H49l4s4'
                  ),
                  tooltip = 'Drag an object here to display it in the shell'
            ),
            '_',
            Item( 'code_locked',
                  editor = ThemedCheckboxEditor(
                      image       = '@icons2:Padlock?l18S11',
                      off_image   = '@icons2:Padlock?L16s',
                      on_tooltip  = 'Code editor is locked (click to unlock)',
                      off_tooltip = 'Code editor is unlocked (click to lock)'
                  )
            ),
            Item( 'log_all',
                  editor = ThemedCheckboxEditor(
                      image       = '@icons:list_node?H55l9s24',
                      off_image   = '@icons:int_node?H55l9s24',
                      on_tooltip  = 'Create new history items (click to update '
                                    'existing items instead)',
                      off_tooltip = 'Update existing history items (click to '
                                    'create new items instead)'
                  )
            ),
            Item( 'code_delete',
                  tooltip = 'Click to clear the contents of the code editor'
            ),
            Item( 'code_paste',
                  tooltip = 'Click to paste the clipboard contents into the '
                            'code editor'
            ),
            '_',
            Item( 'show_options',
                  tooltip = 'Click to display the shell options dialog'
            ),
            Item( 'show_help',
                  tooltip = 'Click to display shell help information'
            ),
            '_',
            Item( 'status', style = 'readonly' ),
            show_labels  = False,
            visible_when = 'show_status',
            group_theme  = '#themes:toolbar_group'
        )
    )


    options_view = View(
        Tabbed(
            VGroup(
                Item( 'dummy',
                      editor = PropertySheetEditor(
                          adapter     = VIPShellAdapter,
                          edit_object = True
                      )
                ),
                show_labels = False,
                label       = 'Options',
                dock        = 'tab',
            ),
            VGroup(
                VGroup(
                    Item( 'debug',
                          editor = PropertySheetEditor( adapter = DebugAdapter )
                    ),
                    show_labels = False,
                    label       = 'Debug'
                ),
                '4',
                VGroup(
                    Item( 'dummy',
                          editor = PropertySheetEditor(
                              adapter     = ControlGrabberAdapter,
                              edit_object = True
                          )
                    ),
                    show_labels = False,
                    label       = 'Control Grabber'
                ),
                show_labels = False,
                label       = 'Debug',
                dock        = 'tab',
            ),
            VGroup(
                Item( 'toolbar_info', style = 'custom' ),
                show_labels = False,
                label       = 'Toolbar',
                dock        = 'tab'
            ),
            VGroup(
                VGroup(
                    Item( 'color_table',
                          editor = VIPShellColorTableEditor()
                    ),
                    show_labels = False
                ),
                '_',
                HGroup(
                    spring,
                    Item( 'reset_colors',
                          show_label = False
                    )
                ),
                label = 'Theme Colors',
                dock  = 'tab'
            ),
            VGroup(
                Item( 'initialize', style = 'custom' ),
                show_labels = False,
                label       = 'Start-up Code',
                dock        = 'tab'
            ),
            id = 'tabs'
        ),
        title  = 'VIP Shell Properties',
        id     = 'facets.ui.editors.vip_shell_editor.VIPShellEditorOptions',
        width  = 330,
        height = 260
    )

    #-- Public Methods ---------------------------------------------------------

    def init_ui ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Make sure our proxy has been initialized:
        self._init_proxy()

        # Initialize the contents of the code editor:
        self.code = self.factory.code

        # Initialize the shell command registry:
        for command_name, command_class in standard_shell_commands:
            self.register( command_name, command_class, True )

        # Set up the threshold, max_items and context number of lines to
        # display:
        self.threshold = self.factory.facet_value( 'threshold' )
        self.max_items = self.factory.facet_value( 'max_items' )
        self.context   = self.factory.facet_value( 'context' )

        # Set up the toolbars:
        self.left_toolbar   = ShellItemToolbar( position = 'left',
                                                location = ( 4.0, 4.0 ),
                                                shell    = self )
        self.middle_toolbar = ShellItemToolbar( position = 'middle',
                                                location = ( 0.5, 4.0 ),
                                                shell    = self )
        self.right_toolbar  = ShellItemToolbar( position = 'right',
                                                location = ( -4.0, 4.0 ),
                                                shell    = self )

        # Synchronize any editor events:
        self.sync_value( self.factory.executed, 'executed', 'to'   )
        self.sync_value( self.factory.command,  'command',  'from' )
        self.sync_value( self.factory.result,   'result',   'to'   )
        self.sync_value( self.factory.export,   'export',   'to'   )
        self.sync_value( self.factory.profile,  'profile',  'to'   )
        self.sync_value( self.factory.send,     'send',     'to'   )
        self.sync_value( self.factory.receive,  'receive',  'from' )

        # Set up the 'debug' event listeners:
        dofs = self.debug.on_facet_set
        dofs( self._debug_object_modified, 'object' )
        dofs( self._debug_stack_modified,  'stack'  )
        dofs( self._debug_caller_modified, 'caller' )

        # Attempt to set up a facet notification handler:
        try:
            self.exception_handler_key = push_exception_handler(
                self._notification_exception, main = True, locked = True
            )
            self.stdout = StdFile( type = 'stdout' )
            self.stderr = StdFile( type = 'stderr' )
            self.excepthook, sys.excepthook = sys.excepthook, self._excepthook
        except FacetNotificationError:
            pass

        # Create and return the editor view:
        return self.edit_facets( view   = 'view',
                                 parent = parent,
                                 kind   = 'editor' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        value = self.value
        if self.factory.share and isinstance( value, dict ):
            self.locals    = locals = value
            self.completer = Completer( locals )
            init           = True
        else:
            locals = self.locals
            init   = (locals is None)
            if init:
                self.locals    = locals = {}
                self.completer = Completer( locals )

            locals[ 'self' ] = value

        if init:
            locals[ '_' ] = locals[ '__' ] = Undefined
            self._initialize( self.factory.initialize )
            self._initialize( self.initialize )
            self._init_locals()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        for item in self.history:
            item.dispose()

        # Reset the 'debug' event listeners:
        dofs = self.debug.on_facet_set
        dofs( self._debug_object_modified, 'object', remove = True )
        dofs( self._debug_stack_modified,  'stack',  remove = True )
        dofs( self._debug_caller_modified, 'caller', remove = True )

        # Restore the previous facets notification exception handler, the
        # original system stdout/stderr file handles and the original system
        # exception hook (if necessary):
        if self.exception_handler_key is not None:
            pop_exception_handler( self.exception_handler_key )
            self.stdout()
            self.stderr()
            sys.excepthook = self.excepthook

        super( vipShellEditor, self ).dispose()

        del self.history[:]
        del self.code_items[:]

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        pget         = prefs.get
        toolbar_info = self.toolbar_info
        items        = pget( 'shell_history' )
        if items is not None:
            hif          = self.history_item_for
            self.history = [ hif( PersistedCommandItem, item )
                             for item in items ]

        color_tables = pget( 'shell_color_tables' )
        if color_tables is not None:
            self.color_tables = color_tables

        debug = self.debug
        debug.debug_enabled        = pget( 'shell_debug_enabled',       True  )
        debug.info_enabled         = pget( 'shell_info_enabled',        True  )
        debug.warning_enabled      = pget( 'shell_warning_enabled',     True  )
        debug.error_enabled        = pget( 'shell_error_enabled',       True  )
        debug.critical_enabled     = pget( 'shell_critical_enabled',    True  )
        debug.called_from_enabled  = pget( 'shell_called_from_enabled', True  )
        debug.show_locals_enabled  = pget( 'shell_show_locals_enabled', True  )
        self.show_filter           = pget( 'shell_show_filter',         True  )
        self.show_status           = pget( 'shell_show_status',         True  )
        self.show_id               = pget( 'shell_show_id',             False )
        self.show_icon             = pget( 'shell_show_icon',           False )
        self.show_line_numbers     = pget( 'shell_show_line_numbers',   False )
        self.show_control          = pget( 'shell_show_control',        False )
        self.show_editor           = pget( 'shell_show_editor',         False )
        self.show_object           = pget( 'shell_show_object',         True  )
        self.show_value            = pget( 'shell_show_value',          False )
        self.code_locked           = pget( 'shell_code_locked',         False )
        self.log_all               = pget( 'shell_log_all',             True  )
        self.theme                 = pget( 'shell_theme',           'default' )
        self.font                  = pget( 'shell_font',
                                           'Consolas Bold 9, Courier Bold 9')
        self.threshold             = pget( 'shell_threshold',              21 )
        self.max_items             = pget( 'shell_max_items',             100 )
        self.context               = pget( 'shell_context',                 7 )
        self.expander_zone         = pget( 'shell_expander_zone',   ( 0, 60 ) )
        self.initialize            = pget( 'shell_initialize',             '' )
        self.cwd                   = pget( 'shell_cwd',                    '' )
        self.mru_execfile_names    = pget( 'shell_mru_execfile_names',     [] )
        toolbar_info.toolbar_delay = pget( 'shell_toolbar_delay',         250 )
        action_info                = pget( 'shell_action_info' )
        if action_info is not None:
            ai_map      = dict( [ ( ai.id, ai ) for ai in action_info ] )
            action_info = toolbar_info.action_info
            for i, ai in enumerate( action_info ):
                user_ai = ai_map.get( ai.id )
                if user_ai is not None:
                    action_info[ i ].facet_set(
                        left   = user_ai.left,
                        middle = user_ai.middle,
                        right  = user_ai.right
                    )

        if self.cwd == '':
            self.cwd = getcwd()

        self.registry.update( dict(
            [ ( name, [ None, value ] )
              for name, value in pget( 'shell_registry', [] ) ] )
        )

        self._initialize( self.initialize )
        self.editor_ui.set_prefs( prefs )
        self.status = ("<-- Click the 'i' (info) button or type '/' then press "
                       "Ctrl-Enter for help...")


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        result = super( vipShellEditor, self ).save_prefs()
        if result is None:
            result = {}

        # Extract out the parts of the shell command registry to be saved:
        registry = [
            ( name, value[1] )
            for name, value in self.registry.iteritems()
            if value[1] not in ( None, '' )
        ]

        debug = self.debug
        result.update( dict(
            shell_history             = [ item.item
                                          for item in self.item_at( 'c' ) ],
            shell_debug_enabled       = debug.debug_enabled,
            shell_info_enabled        = debug.info_enabled,
            shell_warning_enabled     = debug.warning_enabled,
            shell_error_enabled       = debug.error_enabled,
            shell_critical_enabled    = debug.critical_enabled,
            shell_called_from_enabled = debug.called_from_enabled,
            shell_show_locals_enabled = debug.show_locals_enabled,
            shell_show_filter         = self.show_filter,
            shell_show_status         = self.show_status,
            shell_show_id             = self.show_id,
            shell_show_icon           = self.show_icon,
            shell_show_line_numbers   = self.show_line_numbers,
            shell_show_control        = self.show_control,
            shell_show_editor         = self.show_editor,
            shell_show_object         = self.show_object,
            shell_show_value          = self.show_value,
            shell_code_locked         = self.code_locked,
            shell_log_all             = self.log_all,
            shell_theme               = self.theme,
            shell_color_tables        = self.color_tables,
            shell_font                = str( self.font ),
            shell_threshold           = self.threshold,
            shell_max_items           = self.max_items,
            shell_context             = self.context,
            shell_expander_zone       = self.expander_zone,
            shell_initialize          = self.initialize,
            shell_cwd                 = self.cwd,
            shell_mru_execfile_names  = self.mru_execfile_names,
            shell_action_info         = self.toolbar_info.action_info,
            shell_toolbar_delay       = self.toolbar_info.toolbar_delay,
            shell_registry            = registry
        ) )

        return result

    #-- ShellItem and VIPShellHandler Support Methods --------------------------

    def register ( self, command_name, command_class, built_in = False ):
        """ Registers the specified *command_class*, which should be a subclass
            of ShellCommand, as the command processor for the *command_name*
            shell command.
        """
        # Validate that the arguments are correct:
        if not issubclass( command_class, ShellCommand ):
            raise ValueError(
                'The second argument must be a subclass of ShellCommand'
            )

        if ((not isinstance( command_name, basestring )) or
            (' ' in command_name)):
            raise ValueError(
                'Invalid command name specified by first argument'
            )

        # Save the specified values in the registry:
        file_name = self.exec_file_name
        info      = self.registry.get( command_name )
        if info is not None:
            if info[1] is None:
                print ('\x00B/%s\x000 is a built-in command and cannot be '
                       'redefined.' % command_name)

                return
            elif built_in:
                print ('The \x00B/%s\x000 command has been replaced by a '
                       'built-in command.' % command_name)
            else:
                print ('The \x00B/%s\x000 command has been redefined.' %
                       command_name)
        else:
            self.registry[ command_name ] = info = [ None, None ]
            if not built_in:
                print ('The \x00B/%s\x000 command has been defined.' %
                       command_name)

        info[0] = command_class
        if not built_in:
            info[1] = file_name


    def previous_command ( self ):
        """ Replaces the contents of the 'code' buffer with the previous
            command in the shell history.
        """
        self.previous_item( self.item_at( 'c' ) )


    def previous_item ( self, items = None ):
        """ Replaces the contents of the 'code' buffer with the previous
            item in the specified list of *items* (or the shell history if
            *items* is None or omitted).
        """
        if items is None:
            items = self.history

        if len( items ) > 0:
            id = self.scroll_id
            for i in xrange( len( items ) - 1, -1, -1 ):
                item = items[ i ]
                if item.id < id:
                    break
            else:
                item = items[-1]

            self.scroll_id = item.id
            self.selected  = item
            self.replace_code( item.str( item.item ) )


    def next_command ( self ):
        """ Replaces the contents of the 'code' buffer with the next command
            in the shell history.
        """
        self.next_item( self.item_at( 'c' ) )


    def next_item ( self, items = None ):
        """ Replaces the contents of the 'code' buffer with the next item in the
            specified list of *items* (or the shell history if *items* is None
            or omitted).
        """
        if items is None:
            items = self.history

        if len( items ) > 0:
            id = self.scroll_id
            for i in xrange( len( items ) ):
                item = items[ i ]
                if item.id > id:
                    break
            else:
                item = items[0]

            self.scroll_id = item.id
            self.selected  = item
            self.replace_code( item.str( item.item ) )


    def select ( self, item ):
        """ Selects the item specified by *item*.
        """
        self.selected = item


    def profile_code ( self, print_profile = False ):
        """ Profiles any subsequent Python code in the same compound command
            and optionally prints the results if *print_profile* is True.
        """
        self.print_profile = print_profile
        self.profiling     = True


    def execute_file ( self, file_name ):
        """ Executes the Python source file specified by *file_name*.
        """
        # Update the 'most recently used' executed files list:
        file_name  = abspath( file_name )
        file_names = self.mru_execfile_names
        if file_name in file_names:
            file_names.remove( file_name )
        elif len( file_names ) >= 10:
            del file_names[-1]

        file_names.insert( 0, file_name )

        # Now execute the file:
        now = time()
        self.exec_file_name = file_name
        try:
            if self.profiling:
                profiler.profile( execfile, file_name, self.locals )
            else:
                execfile( file_name, self.locals )
        finally:
            self.exec_file_name = ''

        self.status = 'Executed:  %s  in: %.2f seconds.' % (
                      basename( file_name ), time() - now )


    def execute_from ( self, item ):
        """ Executes all visible history items following (and including) the
            specified *item*.
        """
        for an_item in self._items_from( item ):
            an_item.execute()


    def complete_code ( self, editor ):
        """ Allows the user to select from a list of available code completions
            based upon the current code context.
        """
        context = None
        line    = self._current_line()
        choices = []

        # If it appears to be a command, try to do a file completion on it:
        if line[:1] in ( '/', '`' ):
            context, choices = self.complete_file( line, self.code_column - 1 )

        # If no context has been set yet, try to find choices for a Python
        # context:
        if context is None:
            context = self.code_context( line )
            if len( context ) == 0:
                return

            col = context.rfind( '.' )
            if col >= 0:
                choices = self.completer.attr_matches( context )
                context = context[ col: ]
                choices = [ choice[ col: ] for choice in choices ]
            else:
                choices = self.completer.global_matches( context )

            # Eliminate any duplicates that sometimes show up:
            choices = list( set( choices ) )
            choices.sort()

        if len( choices ) > 0:
            if len( choices ) == 1:
                self.insert( choices[0][ len( context ): ] )
            else:
                # fixme: This is Qt specific code that needs to be replaced
                # with toolkit independent code...
                control = editor.control
                if self.completer_context is None:
                    from PyQt4.QtCore import SIGNAL
                    control.connect( control,
                        SIGNAL( 'userListActivated(int,QString)' ),
                        self._complete_code
                    )

                self.completer_context = context
                editor.control.showUserList( 1, choices )


    def code_context ( self, line ):
        """ Returns the current code 'context' based on the current cursor
            position of the editor.
        """
        context = ''
        text    = line[ : self.code_column - 1 ]
        for i in xrange( len( text ) - 1, -1, -1 ):
            if text[ i ] not in ValidChars:
                break

            context = text[ i ] + context

        return context


    def do_code ( self ):
        """ Executes the command specified by the current contents of the 'code'
            buffer.
        """
        command_item = None
        if not self.log_all:
            command_item = self.last_command

        success = self.do_command( self.code, command_item )
        if self.code_item.file_name == '':
            if success and (not self.code_locked):
                do_later( self.clear_code )
            else:
                do_later( self._trim_code )


    def do_command ( self, command, command_item = None, update = True ):
        """ Do the command specified by *command*.
        """
        command = self.strip_blank_lines_from( command )

        return ((command != '') and
                self._do_command( command, command_item, update ))


    def append_ref ( self, item ):
        """ Appends a reference to the specified *item* at the end of the
            current code.
        """
        self.append( '___[%d],' % item.id, False )


    def append_ref_from ( self, item ):
        """ Appends references to all visible history items following (and
            including) the specified *item* to the end of the current code.
        """
        self.append(
            ','.join( [ '___[%d]' % x.id for x in self._items_from( item ) ] ),
            False
        )


    def append ( self, text, add_cr = True ):
        """ Appends *text* to the current code. If *add_cr* is True, then the
            *text* is added starting on a new line; otherwise *text* is simply
            added to the end of the current code.
        """
        text = remove_color( text )
        code = self.code
        if add_cr:
            code = code.rstrip()
            if len( code ) > 0:
                text = ('\n' + text)

        self.replace_code( code + text )


    def append_from ( self, item ):
        """ Appends the text content of all visible items starting with the
            specified *item* to the contents of the current code.
        """
        self.append(
            '\n'.join( [ x.str( x.item ) for x in self._items_from( item ) ] )
        )


    def toggle_ids ( self ):
        """ Toggle the visiblity of ids for all items.
        """
        self.show_id = not self.show_id


    def toggle_icons ( self ):
        """ Toggle the visiblity of icons for all items.
        """
        self.show_icon = not self.show_icon


    def toggle_line_numbers ( self ):
        """ Toggle the visiblity of line numbers for all items.
        """
        self.show_line_numbers = not self.show_line_numbers


    def toggle_filter ( self ):
        """ Toggle the filter bar on or off.
        """
        self.show_filter = not self.show_filter


    def toggle_status ( self ):
        """ Toggle the status bar on or off.
        """
        self.show_status = not self.show_status


    def cycle_theme ( self ):
        """ Cycles through the available themes.
        """
        self.theme = CycleTheme[ self.theme ]


    def move_to_bottom ( self, item, related = False ):
        """ Move the item to the bottom of the shell history list. If *related*
            is True, all related items are moved as well.
        """
        history = self.history
        items   = self._related_to( item, related )
        for item in items:
            history.remove( item )

        history.extend( items )


    def move_to_top ( self, item, related = False ):
        """ Move the item to the bottom of the shell history list. If *related*
            is True, all related items are moved as well.
        """
        history = self.history
        items   = self._related_to( item, related )
        for item in items:
            history.remove( item )

        history[0:0] = items


    def move_to_selected ( self, item, before = False ):
        """ Moves the history item specified by *item* either before or after
            the current selected item. If *before* is True, the item is moved
            in front of the selected item; otherwise it is moved after the
            selected item.

            Returns True if the item was moved, and False otherwise.
        """
        selected = self.selected
        if (selected is None) or (selected is item):
            return False

        history = self.history
        index   = history.index( item )
        target  = history.index( selected )
        if not before:
            target += 1

        if index < target:
            target -= 1

        del history[ index ]
        history.insert( target, item )

        return True


    def move_up ( self, item ):
        """ Moves the specified *item* up in the shell history list. If there is
            a current selected item, the item is moved in front of it; otherwise
            the item is moved up in the history list by one item.
        """
        if not self.move_to_selected( item, True ):
            history = self.history
            index   = history.index( item )
            for i in xrange( index - 1, -1, -1 ):
                if not history[ i ].hidden:
                    del history[ index ]
                    history.insert( i, item )

                    break


    def move_down ( self, item ):
        """ Moves the specified *item* down in the shell history list. If there
            is a current selected item, the item is moved after it; otherwise
            the item is moved down in the history list by one item.
        """
        if not self.move_to_selected( item, False ):
            history = self.history
            index   = history.index( item )
            for i in xrange( index + 1, len( history ) ):
                if not history[ i ].hidden:
                    del history[ index ]
                    history.insert( i, item )

                    break


    def hide_item ( self, item ):
        """ Hides the specified *item* from the shell history.
        """
        item.hidden = True


    def hide_preceding ( self, item, same_type = False ):
        """ Hides all items preceding (and including) the specified *item* in
            the shell history.
        """
        type = item.type
        for an_item in self.history:
            if (not same_type) or (an_item.type == type):
                an_item.hidden = True

            if an_item is item:
                break


    def hide_following ( self, item, same_type = False ):
        """ Hides all items following (and including) the specified *item* in
            the shell history.
        """
        type = item.type
        for an_item in self._items_from( item ):
            if (not same_type) or (an_item.type == type):
                an_item.hidden = True


    def hide_similar ( self, item ):
        """ Hides all items similar to the specified *item* from the shell
            history.
        """
        self.hide_any( set( [ item.type ] ) )


    def hide_duplicates ( self, item = None ):
        """ Hides all duplicates of items similar to the specified *item*, or
            all duplicates across all types if *item* is None.
        """
        type = None
        if item is not None:
            type = item.type

        types = {}
        for an_item in self.history:
            a_type = an_item.type
            if (type is None) or (a_type == type):
                matches = types.get( a_type )
                if matches is None:
                    if a_type == 'result':
                        types[ a_type ] = matches = []
                    else:
                        types[ a_type ] = matches = set()

                value = an_item.item
                if value in matches:
                    an_item.hidden = True
                elif isinstance( matches, set ):
                    matches.add( value )
                else:
                    matches.append( value )


    def hide_to_selection ( self, item ):
        """ Hides all items between the current item and the current selection
            (inclusive). If there is no selection, only the current item is
            hidden.
        """
        history = self.history
        begin   = end = history.index( item )
        if self.selected is not None:
            end           = history.index( self.selected )
            self.selected = None

        for i in xrange( min( begin, end ), max( begin, end ) + 1 ):
            history[ i ].hidden = True


    def show_hide_related ( self, item, hidden = True, include_command = True ):
        """ Shows (or hides) all items related to the specified *item* from the
            shell history.
        """
        for item in self._related_to( item ):
            if (not isinstance( item, CommandItem )) or include_command:
                item.hidden = hidden


    def hide_any ( self, types ):
        """ Hide any visible history items that match any of the item types in
            the set specified by *types*.
        """
        for item in self.history:
            if item.type in types:
                item.hidden = True


    def show_similar ( self, item ):
        """ Shows only the non-hidden items similar to the specified *item* in
            the shell history.
        """
        self.show_any( set( [ item.type ] ) )


    def show_any ( self, types ):
        """ Shows only the non-hidden items matching any of the types in the set
            specified by *types* in the shell history.
        """
        for item in self.history:
            if item.type not in types:
                item.hidden = True


    def show_all ( self ):
        """ Shows all currently hidden items in the shell history.
        """
        for item in self.history:
            item.hidden = False


    def delete_all ( self ):
        """ Deletes the entire contents of the shell history.
        """
        for item in self.history:
            item.dispose()

        del self.history[:]


    def delete_hidden ( self, delete_last = True ):
        """ Deletes all hidden items from the shell history. Also deletes the
            last history item if *delete_last* is True (to handle the case of
            being called from a command).
        """
        # Mark the most recent command (the 'hide hidden' command) as hidden
        # if requested:
        if delete_last:
            self.history[-1].hidden = True

        # Replace the current history list with a new list containing only the
        # items in the old list which are not hidden:
        history = []
        for item in self.history:
            if item.hidden:
                item.dispose()
            else:
                history.append( item )

        self.history = history


    def undo_command ( self ):
        """ Hides the bottommost history item an its related items.
        """
        history = self.history
        for i in xrange( len( history ) - 1, -1, -1 ):
            if not history[ i ].hidden:
                self.show_hide_related( history[ i ] )

                break


    def redo_command ( self ):
        """ Shows the first hidden item (and its related items) after the
            bottommost visible history item.
        """
        history = self.history
        if len( history ) > 0:
            item = None
            for i in xrange( len( history ) - 1, -1, -1 ):
                if history[ i ].hidden:
                    item = history[ i ]
                else:
                    break

            if item is not None:
                self.show_hide_related( item, False )


    def item_at ( self, id ):
        """ Returns the history item with the id specified by *id*.
        """
        history = self.history

        if isinstance( id, slice ):
            start, stop, step = id.start, id.stop, id.step or 1
            n                 = self.id
            if start is None:
                start = 1
            elif start < 0:
                start = max( 0, n + start )

            if stop is None:
                stop = n
            elif stop < 0:
                stop = max( 0, n + stop )

            id = range( start, stop, step )

        if isinstance( id, SequenceType ):
            id = set( id )

            return [ item for item in history if item.id in id ]

        if isinstance( id, basestring ):
            if id in TypeCodes:
                id = TypeCodes[ id ]

                return [ item for item in history
                         if (id == item.type) and (not item.hidden) ]
            elif id.lower() in TypeCodes:
                id = TypeCodes[ id.lower() ]

            if id in ItemSet:
                return [ item for item in history if id == item.type ]

        for item in history:
            if id == item.id:
                return item

        raise IndexError( 'list index out of range' )


    def refresh ( self ):
        """ Schedules a refresh of the contents of the shell history.
        """
        if (self.selected is not None) and self.selected.hidden:
            self.selected = None

        do_later( self.facet_set, changed = True )


    def transfer_item ( self, item, delete = False ):
        """ Transfers the specified ShellItem *item* to another external shell.
            If *delete* is True, the *item* is deleted after the transfer;
            otherwise it is left in the history list.
        """
        self.send = item
        if delete:
            item.dispose()
            self.history.remove( item )


    def add_history_item_for ( self, klass, item, **facets ):
        """ Adds a new history item containing *item* of the specified *klass*
            associated with the specified *command*.
        """
        self.append_items( self.history_item_for( klass, item, **facets ) )


    def history_item_for ( self, klass, item, **facets ):
        """ Returns a history item containing *item* of the specified *klass*
            associated with the specified *command*.
        """
        hitem = klass( shell = self, id = self._next_id() )
        hitem.facet_set( **facets )
        hitem.item              = item
        hitem.theme_state       = self.theme
        hitem.font              = self.font
        hitem.show_id           = self.show_id
        hitem.show_icon         = self.show_icon
        hitem.show_line_numbers = self.show_line_numbers
        hitem.add_tool(
            self.left_toolbar, self.middle_toolbar, self.right_toolbar,
            self.expander
        )
        hitem.initialized()

        return hitem


    def edit_options ( self ):
        """ Allows the user to edit the editor's user preference options.
        """
        self.edit_facets( view = 'options_view', parent = self.adapter )


    def paste_code ( self ):
        """ Pastes the current contents of the clipboard at the current cursor
            position in the code buffer.
        """
        self.insert( toolkit().clipboard().text )


    def delete_code ( self ):
        """ Deletes the entire contents of the code buffer and copies it to the
            clipboard.
        """
        toolkit().clipboard().text = self.code
        self.clear_code()


    def clear_code ( self ):
        """ Deletes the entire contents of the code buffer.
        """
        self.replace_code( '' )

        # Clear any current last command executed to force any new attempts to
        # execute code to create a new command item:
        self.last_command = None


    def insert ( self, text ):
        """ Inserts *text* at the current cursor position in the code buffer.
        """
        lines        = self.code.split( '\n' )
        row, column  = self.code_line - 1, self.code_column - 1
        line         = lines[ row ]
        lines[ row ] = '%s%s%s' % ( line[ : column ], text, line[ column: ] )
        self.replace_code( '\n'.join( lines ) )
        self.code_column += len( text )


    def replace_code ( self, code ):
        """ Replaces the current contents of the 'code' buffer with the
            specified *code*.
        """
        self._no_update          = True
        self.code                = remove_color( code )
        self.code_item.file_name = ''
        self._no_update          = False


    def strip_blank_lines_from ( self, command ):
        """ Returns *command* with any leading and trailing blank lines removed.
        """
        lines = command.split( '\n' )
        for i in xrange( len( lines ) ):
            if lines[i].strip() != '':
                for j in xrange( len( lines ) - 1, i - 1, -1 ):
                    if lines[j].strip() != '':
                        return '\n'.join( lines[ i: j + 1 ] )

        return ''


    def goto_line ( self, line ):
        """ Go to the specified line in the code editor.
        """
        self.code_line = line


    def colorize ( self, text ):
        """ Returns the string *text* encoded using the current color table.
        """
        return (self.color_table + text)


    def shell_command ( self, command, items ):
        """ Process the shell command specified by *command* and return: None,
            a ShellItem, a list of ShellItem's or a bound method to be called
            later.
        """
        # Check to see if the user is attempting to unregister the command:
        command_name = command.split( ' ', 1 )[0][1:]
        if command_name[-1:] == '-':
            command_name = command_name[:-1]
            info         = self.registry.get( command_name )
            if info is None:
                print ('\x00B/%s\x000 is not a defined command name.' %
                       command_name)
            elif info[1] is None:
                print ('\x00B/%s\x000 is a built-in command and cannot be '
                       'deleted.' % command_name)
            else:
                del self.registry[ command_name ]
                print ('The \x00B/%s\x000 command has been deleted.' %
                       command_name)

            return

        # Try to find a command processor for it:
        processor = self._shell_command( command )
        if processor is None:
            print '%s is not a recognized shell command.' % command

            return

        # Process the request and its result:
        if processor.is_help:
            result = processor.show_help()
        else:
            processor.items = items
            result          = processor.execute()

        if isinstance( result, basestring ):
            result = self.history_item_for(
                OutputItem, replace_markers( result ), lod = 2
            )

        return result


    def complete_file ( self, command, column ):
        """ Returns a context string and list of possible file complettions for
            the specified shell *command* with cursor at the specified *column*.
        """
        # If this is a unrecognized command or one that does not accept some
        # type of file, then let the caller resolve it:
        processor = self._shell_command( command )
        if ((processor is None) or
            (processor.options_type not in ( 'path', 'file', 'source' ))):
            return ( None, None )

        # Otherwise, find the list of files that match the cursor context:
        chunks = command[ : column ].split( ' ', 1 )
        if len( chunks ) == 2:
            dir_only    = (processor.options_type == 'path')
            py_only     = (processor.options_type == 'source')
            search_path = join( self.cwd, chunks[1].strip() + '*' )
            choices     = []
            for name in glob( search_path ):
                choice = basename( name )
                if isdir( name ):
                    choice = join( choice, '' )
                elif dir_only or (py_only and (splitext( choice )[1] != '.py')):
                    continue

                choices.append( choice )

            return ( basename( search_path )[:-1], choices )

        return ( '', [] )


    def shell_command_class_for ( self, command ):
        """ Returns the ShellCommand subclass that implements the specified
            *command*, or None if no implementation class could be found.
        """
        info = self.registry.get( command )
        if info is not None:
            command_class, command_file_name = info
            if command_class is None:
                self.execute_file( command_file_name )
                command_class = self.registry[ command ][0]

            if command_class is not None:
                return command_class

        return None


    def source_for ( self, file_name ):
        """ Returns the source code associated with a pseudo *file_name* of
            the form: <shell:nnn>'. If no matching command item can be found,
            None is returned.
        """
        if file_name[:7] == '<shell:':
            id   = int( file_name[7:-1] )
            item = self.item_at( id )
            if item is not None:
                source = remove_color( item.item )
            else:
                command = self.active_command
                if (command is not None) and (command.id == id):
                    source = remove_color( command.item )
                else:
                    source = self.id_map.get( id )
        else:
            source = read_file( file_name )

        return source


    def source_for_frame ( self, frame ):
        """ Returns a starting line number and list of source code lines for
            the code that was being executed by the specified frame in the form:
            (start_line,lines). If the requested source cannot be found,
            (None,None) is returned.
        """
        lines = self.source_for( frame.f_code.co_filename )
        if (lines is None) or (len( lines ) == 0):
            return ( None, None )

        start  = frame.f_code.co_firstlineno
        lines  = lines.split( '\n' )[ start - 1: ]
        line1  = lines[0]
        indent = len( line1 ) - len( line1.lstrip() )
        for end in xrange( 1, len( lines ) ):
            line = lines[ end ]
            n    = len( line.lstrip() )
            if (n > 0) and (indent >= (len( line ) - n )):
                lines = lines[ : end ]

                break

        return ( start, as_lines( as_string( lines ).rstrip() ) )


    def append_items ( self, items ):
        """ Appends the specified list of shell *items* to the history list.
        """
        # Allow a single item to be passed as an argument instead of a list:
        if isinstance( items, ShellItem ):
            items = [ items ]

        # Make sure that all of the items have a related 'parent' set if
        # possible:
        parent = None
        for item in items:
            if parent is None:
                parent = item
                if item.parent is not None:
                    parent = item.parent
            elif (isinstance( item, GeneratedItem ) and
                  (item.parent is None)):
                item.parent = parent

        # Check if we can insert the new items after the lastmost related item:
        history = self.history
        if parent is not None:
            for i in xrange( len( history ) - 1, -1, -1 ):
                item = history[ i ]
                if ((item is parent) or
                    (isinstance( item, GeneratedItem ) and
                    (item.parent is parent))):
                    history[ i + 1: i + 1 ] = items

                    return

        # If not, then just add them to the end of the history list:
        history.extend( items )


    def add_code_item ( self, item = None ):
        """ Adds a new *item* to the list of current shell "code" items.
        """
        if not isinstance( item, VIPShellCode ):
            if item is None:
                item = VIPShellCode()
            else:
                item = VIPShellItem(
                    item = self.history_item_for( item.__class__, item.item,
                                                  lod = 2, tags = item.tags ) )

        self.code_items.append( item )


    def add_item_for ( self, parent_item, new_item ):
        """ Adds a specified *new_item* as a child of the specified
            *parent_item*.
        """
        self.append_items( self._shell_item( new_item, parent_item ) )


    def tear_off_item ( self, item ):
        """ "Tears off" the specified shell *item* and displays it in a separate
            window.
        """
        if item in self.history:
            self.history.remove( item )

        VIPShellItem(
            item = self.history_item_for(
                       item.__class__, item.item, lod = 2, tags = item.tags )
        ).edit_facets()

        item.dispose()


    def set_result ( self, result ):
        """ Saves the specified result as the value of the '__' variable and
            also notifies any interested listeners.
        """
        self.result = self.locals[ '__' ] = result


    def lock_result ( self, result ):
        """ Saves the specified result as the value of the '_' variable and
            also notifies any interested listeners.
        """
        self.result = self.locals[ '_' ] = result

    #-- Facet Default Values ---------------------------------------------------

    def _code_item_default ( self ):
        return VIPShellCode( shell = self )


    def _code_items_default ( self ):
        return [ self.code_item ]


    def _color_tables_default ( self ):
        return theme_color_tables.copy()

    #-- Facet Event Handlers ---------------------------------------------------

    def _command_set ( self, command ):
        """ Handles a Python command being passed in externally.
        """
        self.do_command( command )


    def _receive_set ( self, item ):
        """ Handles a ShellItem being passed in externally.
        """
        if item is not None:
            self.add_history_item_for( item.__class__, item.item,
                                       lod = item.lod )


    def _show_id_set ( self ):
        """ Handles the 'show_id' facet being changed.
        """
        show_id = self.show_id
        for item in self.history:
            item.show_id = show_id


    def _show_icon_set ( self ):
        """ Handles the 'show_icon' facet being changed.
        """
        show_icon = self.show_icon
        for item in self.history:
            item.show_icon = show_icon


    def _show_line_numbers_set ( self ):
        """ Handles the 'show_line_numbers' facet being changed.
        """
        show_line_numbers = self.show_line_numbers
        for item in self.history:
            item.show_line_numbers = show_line_numbers


    def _font_set ( self ):
        """ Handles the 'font' facet being changed.
        """
        font = self.font
        for item in self.history:
            item.font = font


    def _theme_set ( self, theme ):
        """ Handles the 'theme' facet being changed.
        """
        # Note: We do it this way, rather than just doing a simple assignment,
        # since some themes use the same color table (which will not trigger a
        # change event), but we always need to force the UI to update to reflect
        # the theme change:
        self.facet_setq( color_table = self.color_tables.setdefault( theme,
                                            theme_color_tables[ theme ] ) )
        self._color_table_set()


    def _color_table_set ( self ):
        """ Handles the 'color_table' facet being changed.
        """
        theme                      = self.theme
        self.color_tables[ theme ] = self.color_table
        for item in self.history:
            item.update      = True
            item.theme_state = theme


    def _reset_colors_set ( self ):
        """ Handles the 'reset_colors' facet being changed.
        """
        self.color_table = theme_color_tables[ self.theme ]


    def _selected_set ( self, old, new ):
        """ Handles the 'selected' facet being changed.
        """
        if old is not None:
            old.selected = False

        if new is not None:
            new.selected = True


    def _profiling_set ( self, state ):
        """ Handles the 'profiling' facet being changed.
        """
        if state:
            profiler.begin_profiling( self.cwd )
        else:
            profiler.end_profiling()
            self.profile = profiler.profile_name


    @on_facet_set( 'stdout:has_data, stderr:has_data' )
    def _stdout_modified ( self ):
        """ Handles some code writing to stdout or stderr outside of the
            normally expected times.
        """
        do_later( self._handle_asynch_output )


    def _code_items_items_set ( self, event ):
        """ Handles the 'code_items' list facet being changed.
        """
        for item in event.removed:
            if isinstance( item, VIPShellCode ):
                item.shell = None

        code_item = None
        for item in event.added:
            if isinstance( item, VIPShellCode ):
                code_item  = item
                item.shell = self

        if code_item is not None:
            self.code_item = code_item

        for item in self.code_items:
            if isinstance( item, VIPShellCode ):
                break
        else:
            self.code_items.append( VIPShellCode() )


    # fixme: The following 3 'on_facet_set' decorators don't seem to work
    # because of the use of the 'DelegatesTo' or 'Constant' facets for 'debug'.
    # As a result, we are setting up explicit listeners in 'init_ui' and
    # removing them in 'dispose' as a work-around...

    #@on_facet_set( 'debug:object' )
    def _debug_object_modified ( self, value ):
        """ Handles the debug object's 'object' facet being modified.
        """
        self.add_history_item_for(
            LogItem, value,
            label  = self.debug.label,
            level  = self.debug.level,
            parent = self.active_command
        )


    #@on_facet_set( 'debug:stack' )
    def _debug_stack_modified ( self, stack ):
        """ Handles the debug object's 'stack' facet being modified.
        """
        frames = [ item[0] for item in stack ]
        self.add_history_item_for(
            CalledFromItem, frames[1:],
            callee = frames[0].f_code.co_name,
            parent = self.active_command,
        )


    #@on_facet_set( 'debug:caller' )
    def _debug_caller_modified ( self, caller ):
        """ Handles the debug object's 'caller' facet being modified.
        """
        frame, file_name, line_num, func_name, lines, index = caller
        if file_name[:7] != '<shell:':
            func_name = '%s [%s]' % ( func_name, file_name )

        self.add_history_item_for(
            LocalsItem, frame.f_locals,
            label  = func_name,
            parent = self.active_command
        )


    def _grabbed_control_set ( self, control ):
        """ Handles the 'grabbed_control' facet being modified.
        """
        if self.show_control:
            self.debug.debug( 'Control', control )

        editor = control.editor
        if editor not in ( None, self ):
            if self.show_editor:
                self.debug.debug( 'Editor', editor )

            if self.show_object and (editor.object is not self):
                self.debug.debug( 'Object', editor.object )

            if self.show_value and (editor.value is not self):
                self.debug.debug( "Value of '%s'" % editor.name, editor.value )


    def _dropped_value_set ( self, value ):
        """ Handles the 'dropped_value' facet being modified.
        """
        items  = []
        locals = self.locals
        if isinstance( value, HasPayload ):
            value = value.payload

        if isinstance( value, list ):
            file_names = []
            for item in value:
                if isinstance( item, basestring ):
                    file_name = item[3:] if item[:3] == '///' else item
                    if exists( file_name ):
                        items.append( self.history_item_for(
                            file_class_for( file_name ), file_name
                        ) )
                        file_names.append( file_name )

            n = len( file_names )
            if n > 0:
                self.history.extend( items )
                if n == len( value ):
                    if n == 1:
                        locals[ '_' ] = file_name
                        self.status   = ("The dropped file name has been "
                                         "assigned to '_'")
                    else:
                        locals[ '__' ] = file_names
                        self.status   = ("The dropped file names have been "
                                         "assigned to '_'")

                    return

        self.history.append( self.history_item_for( ResultItem, value ) )
        locals[ '_' ] = value
        self.status   = "The dropped value has been assigned to '_'"


    def _code_locked_set ( self, code_locked ):
        """ Handles the 'code_locked' facet being modified.
        """
        self.status = (
            'The code editor contents are unlocked.',
            'The code editor contents are locked.'
        )[ code_locked ]


    def _log_all_set ( self, log_all ):
        """ Handles the 'log_all' facet being modified.
        """
        self.status = (
            'A successful command execution will update an existing history '
            'command (if possible).',
            'A successful command execution will create a new history command.'
        )[ log_all ]


    def _code_delete_set ( self ):
        """ Handles the 'code_delete' event being fired.
        """
        self.delete_code()


    def _code_paste_set ( self ):
        """ Handles the 'code_paste' event being fired.
        """
        self.paste_code()


    def _show_options_set ( self ):
        """ Handles the 'show_options' event being fired.
        """
        self.edit_options()


    def _show_help_set ( self ):
        """ Handles the 'show_help' event being fired.
        """
        self.do_command( '/' )


    def _expander_zone_set ( self ):
        """ Handles the 'expander_zone' facet being changed.
        """
        self.expander.zone = self.expander_zone

    #-- Private Methods --------------------------------------------------------

    def _next_id ( self ):
        """ Returns the next available shell item id.
        """
        self.id += 1

        return self.id


    def _do_command ( self, command, command_item, update ):
        """ Process the command specified by *command*.

            If *command_item* is not None, it represents an existing history
            command item whose code is updated using *code* (unless *update* is
            False). Any items created by executing the *command* are added to
            the history at the end of the *command_item*'s children.

            If *command_item* is None, then a new history command item is
            created using *command* as its content. The new command item is then
            added to the history along with any items created as a result of
            executing the command.
        """
        lines = remove_color( command ).split( '\n' )
        lod   = 1
        if len( lines ) > 6:
            lod = 0

        status      = self.status
        commands    = self._parse_command( lines )
        content     = '\n'.join( [ c[1] for c in commands ] )
        new_command = (command_item is None)
        if new_command:
            command_item = self.history_item_for( CommandItem, content,
                                                  lod = lod )
        elif update:
            command_item.item = content

        items             = [ command_item ]
        failed            = executed = False
        callbacks         = []
        result            = Undefined
        start_time        = time()
        self.timing       = False
        self.clear_buffer = True

        # Set a reference to the currently executing command:
        self.active_command = self.last_command = command_item

        # Process each shell command and Python code chunk in the command:
        command_index = 0
        for is_shell_command, command_text in commands:
            command_index += 1
            command_text   = remove_color( command_text )

            # Create stdout/stderr interceptors for the next command:
            stdout = StdFile( type = 'stdout' )
            stderr = StdFile( type = 'stderr' )

            # Initialize command execution time:
            delta = 0.0

            if is_shell_command:
                # Process a shell command:
                command_item.theme = '@facets:shell_item?H32l10S53|l'
                try:
                    value = self.shell_command( command_text, items )
                    if isinstance( value, ShellItem ):
                        items.append( value )
                    elif isinstance( value, list ):
                        items.extend( value )
                    elif value is not None:
                        callbacks.append( value )
                except Exception:
                    failed = True
                    items.append( self._exception() )
            else:
                # Process normal Python code:
                module = '<shell:%d>' % command_item.id
                try:
                    # Attempt to execute the command (and save its result):
                    code = compile( command_text, module, 'eval' )
                    now  = time()
                    if self.profiling:
                        value = profiler.profile( eval, code, self.locals )
                    else:
                        value = eval( code, self.locals )

                    delta    = time() - now
                    executed = True

                    # Add the result (if any) to the list of history items:
                    if value is not None:
                        if isinstance( value, ShellItem ):
                            items.append( value )
                        elif self._all_shell_items( value ):
                            items.extend( value )
                        else:
                            result = value
                            items.append( self.history_item_for(
                                              ResultItem, result, lod = 1 ) )
                except SyntaxError:
                    try:
                        code = compile( command_text + '\n', module, 'exec' )
                        now  = time()
                        if self.profiling:
                            profiler.profile( eval, code, self.locals )
                        else:
                            exec code in self.locals

                        self.id_map[ command_item.id ] = command_text
                        delta    = time() - now
                        executed = True
                    except SyntaxError:
                        failed = True
                        items.append( self._exception( command_item ) )
                    except Exception:
                        executed = failed = True
                        items.append( self._exception( command_item ) )
                except Exception:
                    executed = failed = True
                    items.append( self._exception( command_item ) )

            # Add the contents of stdout/stderr (if any) to the list of history
            # items:
            items.extend( self._output( stdout ) )
            items.extend( self._output( stderr ) )

            # Log the execution time (if requested and necessary):
            if self.timing and (delta >= 0.001):
                items.append( self._log_time( command_index, delta ) )

        # Indicate no command is currently executing:
        self.active_command = None

        # If any Python code returned a result, save the last result returned:
        if result is not Undefined:
            # Save the result as the value of the '_' variable and also
            # notify any interested listeners:
            self.set_result( result )

        # Check if command execution was being profiled:
        if self.profiling:
            # If so, turn off profiling:
            self.profiling = False

            # Print profiler results if requested:
            if self.print_profile:
                stats = StdFile( type = 'stdout' )
                profiler.stats( 50 )
                items.append( self.history_item_for( ErrorItem,
                             'Profiling Results:\n' + trim_margin( stats() ) ) )

        # Make sure all items have the link to their command set:
        for item in items:
            self._shell_item( item, command_item )

        # If any callbacks were returned by a shell command, invoke them now:
        post_callbacks = []
        for callback in callbacks:
            try:
                value = callback()
                if isinstance( value, ShellItem ):
                    items.append( self._shell_item( value, command_item ) )
                elif isinstance( value, list ):
                    items.extend( [ self._shell_item( item, command_item )
                                    for item in value ] )
                elif value is not None:
                    post_callbacks.append( value )
            except Exception:
                failed = True
                items.append(
                    self._shell_item( self._exception(), command_item )
                )

        if new_command:
            # Add the new command and the items it created to the end of the
            # history:
            self.history.extend( items )

            # Save the last id for later arrow key retrieval by the user:
            self.scroll_id = items[-1].id + 1
            self.selected  = None
        elif len( items ) == 1:
            # When re-executing an existing command which does not produce any
            # new items, supress the command and re-use its id:
            self.id -= 1
        else:
            # Otherwise, add all new items to the end of the existing command:
            self.append_items( items[ 1: ] )

        # If there are any post history item processing callbacks, do them now:
        items = []
        for callback in post_callbacks:
            try:
                callback()
            except Exception:
                failed = True
                items.append(
                    self._shell_item( self._exception(), command_item )
                )

        if len( items ) > 0:
            self.history.extend( items )

        # If any Python code was executed (even if it raised an exception),
        # signal that execution occurred:
        if executed:
            self._init_locals()
            self.executed = True

        # Update the shell status message if none of the executed commands
        # changed it:
        if status == self.status:
            self.status = ('Executed command [%d] in %.2f seconds.' %
                           ( command_item.id, time() - start_time ))

        # Return whether all commands succeeded or any caused an exception:
        return ((not failed) and self.clear_buffer)


    def _exception ( self, command_item = None ):
        """ Returns a shell item for an exception that occurred while executing
            a command.
        """
        type, value, tb_entry = exc_info()

        return self._exception_for( type, value, tb_entry, command_item )


    def _exception_for ( self, type, value, tb_entry, command_item = None ):
        """ Returns a shell item for the exception specified by *type*, *value*
            and *tb_entry*. If *command_item is not None, it is used as the
            parent of the shell item created.
        """
        frames = []
        while tb_entry is not None:
            frames.append( tb_entry.tb_frame )
            tb_entry = tb_entry.tb_next

        frames.reverse()

        return self.history_item_for(
            ExceptionItem, frames,
            item_label = '%s: %s' % ( type.__name__, str( value ) )
        )


    def _notification_exception ( self, object, facet, old, new, notify ):
        """ Handles any asynchronous facet notification errors that may occur
            in other parts of the application.
        """
        self.append_items( self._exception() )


    def _excepthook ( self, type, value, tb_entry ):
        """ Handles an exception that was not caught anywhere else.
        """
        self.append_items( self._exception_for( type, value, tb_entry ) )


    def _output ( self, std_file ):
        """ Returns a shell item for the contents of the StdFile *std_file* (if
            it is not empty).
        """
        # Get the content of the file:
        text = std_file()
        if text == '':
            # Return nothing if the file was empty:
            return []

        # Determine the correct shell item class to use:
        klass = ErrorItem if std_file.type == 'stderr' else OutputItem

        return [ self.history_item_for( klass, text, lod = 1 ) ]


    def _trim_code ( self ):
        """ Trims all trailing white space from the end of the current 'code'
            value.
        """
        self.code = self.code.rstrip()


    def _current_line ( self ):
        """ Returns the contents of the 'code' line that the cursor is on.
        """
        return self.code.split( '\n' )[ self.code_line - 1 ]


    def _parse_command ( self, lines ):
        """ Parses a list of text *lines* into a series of either single line
            shell commands or possibly multi-line Python source code chunks, and
            returns a list of tuples of the form: [ ( True, shell_command ),
            ... ( False, python_source ) ].
        """
        result = []
        code   = []
        for line in lines:
            prefix = line[:1]
            if prefix == '/':
                if ((not self._help_command( code, result )) and
                    (len( code ) > 0)):
                    result.append(
                        ( False, python_colorize( '\n'.join( code ) ) )
                    )
                    del code[:]

                result.append( ( True, '\x003' + line ) )
            elif prefix == '`':
                result.append( ( True, '\x003/os ' + line[1:].strip() ) )
            else:
                code.append( line )

        if (not self._help_command( code, result )) and (len( code ) > 0):
            result.append( ( False, python_colorize( '\n'.join( code ) ) ) )

        return result


    def _help_command ( self, code, commands ):
        """ Checks to see if *code* contains a help command of the form:
            expression[?]?, and if so, converts it to the corresponding help
            command and adds it to *commands*. Returns True if *code* was a
            help command request, and False otherwise.
        """
        if len( code ) == 1:
            code = code[0].strip()
            if code[-1:] == '?':
                commands.append( ( True, '\x003/? ' + code.rstrip( '?' ) ) )

                return True

        return False


    def _shell_command ( self, command ):
        """ Returns a command object that can process the shell command
            specified by *command*. If no command is found, None is returned.
        """
        # Convert an OS command into a normal command:
        if command[:1] == '.':
            command = '/os ' + command[1:]

        # Parse the command into a verb and options:
        tokens  = command.split( ' ', 1 )
        command = tokens[0][1:]
        options = ''
        if len( tokens ) > 1:
            options = tokens[1].strip()

        # Determine whether this is an execute or help request:
        is_help = (command[-1:] == '?')
        if is_help:
            command = command[:-1]

        # Get the implementation class (if possible):
        command_class = self.shell_command_class_for( command )
        if command_class is None:
            return None

        return command_class(
            shell   = self,
            command = command,
            options = options,
            is_help = is_help
        )


    def _log_time ( self, index, time ):
        """ Returns a history item for the time it took to execute some code,
            where *index* is the command index, and *time* is the time it took
            to execute the command (in seconds).
        """
        return self.history_item_for( ErrorItem,
            '\x001Executed command \x00B#%d\x001 in: \x00B%.3f\x001 seconds' %
            ( index, time )
        )


    def _items_from ( self, item ):
        """ Returns a list of all visible history items following (and
            including) the specified item.
        """
        items = self.history

        return  [ x for x in items[ items.index( item ): ] if not x.hidden ]


    def _complete_code ( self, id, text ):
        """ fixme: This is a Qt specific handler for code completion. It needs
            to be made toolkit independent...
        """
        self.insert( text[ len( self.completer_context ): ] )


    def _shell_item ( self, shell_item, parent_item ):
        """ Initializes the ShellItem subclass instance *shell_item* for use in
            the shell history list. *parent_item* is the shell item that
            generated the item.
        """
        if isinstance( shell_item, GeneratedItem ):
            shell_item.parent = parent_item

        return shell_item


    def _all_shell_items ( self, value ):
        """ Returns whether or not *value* is a sequence of ShellItems.
        """
        return (isinstance( value, SequenceType ) and
                (len( value ) > 0)                and
                reduce( lambda x, y: x and isinstance( y, ShellItem ),
                        value, True ))


    def _related_to ( self, item, related = True ):
        """ Returns a list of all items related to *item* if *related* is True;
            otherwise it returns a list containing only *item*.
        """
        if not related:
            return [ item ]

        if isinstance( item, GeneratedItem ) and (item.parent is not None):
            item = item.parent

        items = []
        if item in self.history:
            items.append( item )

        for an_item in self.history:
            if getattr( an_item, 'parent', None ) is item:
                items.append( an_item )

        return items


    def _initialize ( self, initialize ):
        """ Executes some (optional) initialization code in the 'locals'
            namespace.
        """
        if initialize != '':
            self._init_locals()
            try:
                exec initialize in self.locals
            except Exception:
                pass


    def _init_locals ( self ):
        """ Make sure all 'special' local variables are set.
        """
        self.locals[ '___' ] = self.proxy


    def _init_proxy ( self ):
        """ Initializes the dynamic state of the shell proxy.
        """
        proxy       = self.proxy
        proxy.shell = self

        for klass in self._subclasses_of( ShellItem ):
            proxy.add_facet( klass.__name__, Constant( klass ) )


    def _subclasses_of ( self, klass, subclasses = None ):
        """ Returns a list of all subclasses of the specified *klass*.
        """
        if subclasses is None:
            subclasses = []

        subclasses.append( klass )
        for a_klass in klass.facet_subclasses():
            self._subclasses_of( a_klass, subclasses )

        return subclasses


    def _handle_asynch_output ( self ):
        """ Handles code writing to stdout/stderr outside of the normally
            expected times.
        """
        # Create a history item for any output written to stdout:
        text = self.stdout()
        if text != '':
            self.add_history_item_for( OutputItem, text, lod = 1 )

        # Create a history item for any output written to stderr:
        text = self.stderr()
        if text != '':
            self.add_history_item_for( ErrorItem, text, lod = 1 )

        # Create new stderr/stderr handlers:
        self.stdout = StdFile( type = 'stdout' )
        self.stderr = StdFile( type = 'stderr' )

#-------------------------------------------------------------------------------
#  'VIPShellEditor' class:
#-------------------------------------------------------------------------------

class VIPShellEditor ( BasicEditorFactory ):

    # The class used to construct editor objects:
    klass = vipShellEditor

    # Should the shell interpreter use the object value's dictionary?
    share = Bool( True )

    # A block of code to be executed when the editor is initially created:
    initialize = Str

    # The initial contents of the shell 'code' editor:
    code = Code

    # Extended facet name of the object event facet which is fired when a
    # command is executed:
    executed = Str

    # Extended facet name of the object facet to which Python commands can be
    # assigned in order to have the shell interpreter execute them:
    command = Str

    # Extended facet name of the object facet to which the result of executing
    # a command is assigned:
    result = Str

    # Extended facet name of the object facet to which an exported history item
    # is assigned:
    export = Str

    # Extended facet name of the object facet to which a local history items are
    # sent:
    send = Str

    # Extended facet name of the object facet from which external history items
    # are received:
    receive = Str

    # Extended facet name of the object facet to which the name of profiler
    # data files is assigned after a command has been profiled:
    profile = Str

    # Threshold number of intermediate lines to display before eliding results:
    threshold = Range( 10, None, 21, facet_value = True )

    # Maximum number of list/tuple/dict items to display in a result (a value
    # of 0 means there is no maximum):
    max_items = Range( 0, 500, 100, facet_value = True )

    # The number of context lines to display in tracebacks:
    context = Range( 1, None, 7, facet_value = True )

#-- EOF ------------------------------------------------------------------------
