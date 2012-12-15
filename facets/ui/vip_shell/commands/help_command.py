"""
Defines the HelpCommand VIP Shell command used to display help information about
the shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from types \
    import UnboundMethodType

from facets.api \
    import Undefined

from facets.ui.graphics_text \
    import color_tag_for

from facets.ui.vip_shell.helper \
    import trim_margin, replace_markers

from facets.ui.vip_shell.items.shell_item \
    import ShellItem

from facets.ui.vip_shell.items.output_item \
    import OutputItem

from facets.ui.vip_shell.tags.api \
    import CommandTag, TextTag

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Help information about using the various shell commands:
ShellHelp = """
Click on any of the underlined keywords below for help on using the VIP Shell:
\x000
%scommands>>  = Shell commands.
%svariables>> = Special shell variables.
%skeys>>      = Code editor keyboard shortcuts.
%sitems>>     = Keyboard and mouse actions for history items.
%sdebug>>     = Debugging statements that can be added to your code.
"""[1:-1]


ShellCommands = """
The VIP Shell supports the following special commands:
\x000
%s

For more information about any of these commands, either click on the
underlined command name above or type: [[/cmd_name?]] (e.g. <</cd?>>) in the
code editor.
"""[1:-1]


ShellVariables = """
The VIP Shell defines the following special variables:
\x000
[[_]]  = Contains the result from the most recently executed command.
[[__]] = Provides indexed access to the shell history items, using either the
       history item ids (e.g. <<11>>) or type (e.g. '<<command>>' or '<<c>>').
\x000
Examples:
<<__[11]>>        = History item with id = 11.
<<__[11:16:2]>>   = List of history items with ids 11, 13, 15.
<<__['command']>> = List of all commands.
<<__['C']>>       = List of all commands.
<<__['c']>>       = List of all visible commands.
"""[1:-1]


ShellKeys = """
The VIP Shell code editor has the following key definitions:
\x000
[[Ctrl-Enter]]          = Execute the contents of the code editor as a command.
[[Ctrl-Shift-Enter]]    = Insert a new blank line after the current line with the same indenting.
[[Ctrl-Tab]]            = Do code completion based on the text preceding the cursor.
[[Ctrl-Up]]             = Copy the previous history command into the code editor.
[[Ctrl-Down]]           = Copy the next history command into the code editor.
[[Ctrl-Shift-Up]]       = Move the current line up one line.
[[Ctrl-Shift-Down]]     = Move the current line down one line.
[[Alt-Ctrl-Shift-Up]]   = Copy the previous history item into the code editor.
[[Alt-Ctrl-Shift-Down]] = Copy the next history item into the code editor.
[[Ctrl-Delete]]         = Delete all hidden history items.
[[Ctrl-Shift-Delete]]   = Delete all history items.
[[Ctrl-B]]              = Hides the bottommost history item and its related items.
[[Ctrl-Shift-B]]        = Unhides the bottommost hidden history item and its related items.
[[Ctrl-F]]              = Find the currently selected text (or <<symbol>> if no text is selected).
[[Ctrl-N]]              = Find the next occurrence of the current search string.
[[Ctrl-O]]              = Edit the shell's options.
[[Ctrl-P]]              = Find the previous occurrence of the current search string.
[[Ctrl-Q]]              = Copy code editor text to the clipboard and then delete it.
[[Ctrl-S]]              = Save the current contents of the code editor to a file.
[[Ctrl-Shift-S]]        = Save the current contents of the code editor to a user specified file.
[[Ctrl-T]]              = Create a new empty code editor tab.
[[Ctrl-Shift-T]]        = Create a new code editor containing a copy of the current code editor.
[[F2]]                  = Same as [[Ctrl-S]].
[[F3]]                  = Toggles the filter bar on or off.
[[F4]]                  = Toggles the status line on or off.
"""[1:-1]

ShellItems = """
The VIP Shell history item list supports a number of keyboard and mouse commands
that can be invoked when the mouse pointer is over a history item.

The available mouse commands are:
\x000
[[Click]]             = Execute the current item.
[[Ctrl-click]]        = Select the current item.
[[Shift-click]]       = Execute the current and all following visible items.
[[Right-click]]       = Copy the item to the text buffer, replacing its contents.
[[Ctrl-right-click]]  = Append the item to the end of the text buffer.
[[Shift-right-click]] = Append the current item and all following visible items to
                    the end of the text buffer.
[[Alt-right-click]]   = Append a reference to the item (e.g. <<__[11]>>) to the end of
                    the text buffer.
[[Alt-Shift-right-click]] = Append references to the item and all following visible
                    items (e.g. <<__[11],__[13],__[27]>>) to the end of the text
                    buffer.
\x000
The available keyboard commands are:
\x000
%s
\x000
[[Note]]: A name appearing in square brackets (e.g. <<[Python File]>>) indicates
a command that only applies to that type of history item. You can get additional
help information for some keyboard commands by clicking on their underlined key
name.
"""[1:-1]


ShellDebug = """
Facets contains a [[facets.core.debug]] module defining several functions that
can be added to your code to provide logging and debugging information that can
be filtered and presented by the VIP Shell.

The available functions are:
\x000
[[debug]]       = Display a debug message or object with an optional label.
[[info]]        = Display an informational message or object with an optional label.
[[warning]]     = Display a warning message or object with an optional label.
[[error]]       = Display an error message or object with an optional label.
[[critical]]    = Display a critical error message or object with an optional label.
[[called_from]] = Display a call stack of how control arrived at this point.
[[show_locals]] = Display the local variables for the current function or method.
\x000
The [[debug]], [[info]], [[warning]], [[error]] and [[critical]] functions can all be invoked as
follows:

    function( [[message]] )
    function( [[object]] )
    function( [[label]], [[object]] )

where [[message]] is a text string to be printed, [[object]] is an arbitrary
(non-string) object to be logged, and [[label]] is a text label used to identify
the [[object]] being logged.

The [[show_locals]] function displays a snapshot of all local variables in the
current function or method, and does not take any arguments.

The [[called_from]] function displays the call stack of how control reached the
current function or method. It takes a single argument, which is the number of
call stack entries to display (the default is 1). Each stack entry displayed can
be expanded to display the source code for the calling function or method, and
contains additional tags that can display the values of variables within the
caller's context.

In addition, the output displayed by any of the debug functions can be enabled
or disabled using the checkboxes shown on the [[Debug]] page of the shell options
dialog. If no VIP Shell is active, no output is displayed by any of the
functions.

Examples:
\x000
<<from facets.core.debug import debug, info, called_from, show_locals>>
<<debug( 'self', self )>>
<<info( '%d arguments received' % len( args ) )>>
<<called_from(10)>>
<<show_locals()>>
"""[1:-1]


# The mapping from command options to help text:
OptionsMap = {
   'variables': ShellVariables,
   'keys':      ShellKeys,
   'debug':     ShellDebug
}

# The mapping from key names to keys:
KeyMap = {
    'add':           'numpad +',
    'subtract':      'numpad -',
    'minus':         '-',
    'backslash':     '\\',
    'slash':         '/',
    'comma':         ',',
    'quote':         "'",
    'equal':         '=',
    'left_bracket':  '[',
    'right_bracket': ']',
    'period':        '.'
}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def cmp_key_name ( name_1, name_2 ):
    if len( name_1 ) == 1:
        if len( name_2 ) > 1:
            return -1
    elif len( name_2 ) == 1:
        return 1

    return cmp( name_1, name_2 )

#-------------------------------------------------------------------------------
#  'HelpCommand' class:
#-------------------------------------------------------------------------------

class HelpCommand ( ShellCommand ):
    """ Displays help information about using the shell commands.
    """

    summary      = 'Displays shell help information.'
    options_type = 'expression'


    def execute ( self ):
        """ Displays help information about using the shell commands.
        """
        method = getattr( self, 'help_for_' + self.options, None )
        if method is not None:
            return method()

        help = OptionsMap.get( self.options )
        if help is not None:
            return help

        # Create the tag links for the various help sections:
        items = []
        tags  = []
        for key in ( 'commands', 'variables', 'keys', 'items', 'debug' ):
            items.append( color_tag_for( 'B', tags ) )
            tags.append( CommandTag( command = '/ ' + key ) )

        # Return the final help text:
        return self.shell.history_item_for(
            OutputItem, (ShellHelp % tuple( items )).replace( '>>', '\x000' ),
            tags = tags, lod = 2
        )


    def show_help ( self ):
        """ Displays help information about shell values.
        """
        if len( self.options ) == 0:
            return self.execute()

        value = self.evaluate()
        doc   = getattr( value, '__doc__', Undefined )
        if isinstance( doc, basestring ):
            self._pretty_print( doc )
        else:
            print ("No information available for an instance of type '%s'" %
                   value.__class__.__name__)


    def help_for_commands ( self ):
        """ Returns help information about the available shell commands.
        """
        summaries = []
        codes     = []
        tags      = []
        sccf      = self.shell.shell_command_class_for
        registry  = self.shell.registry
        commands  = [ name for name, value in registry.iteritems() ]
        commands.sort()

        for command in commands:
            summary       = ''
            command_class = sccf( command )
            if command_class is not None:
                summary = command_class( command = command ).summary
                if summary != '':
                    summary = ' = ' + summary

            summaries.append( summary )

            cc = 'BC'[ registry[ command ][1] is not None ]
            codes.append( color_tag_for( cc, tags ) )
            tags.append( CommandTag( command = '/%s?' % command ) )

        # Generate the command related help text:
        max_len = -(reduce( lambda x, y: max( x, len( y ) ), commands, 0 ) + 2)
        items   = [ '\n'.join( [
            '%s/%*s%s' % ( code, max_len, command + '\x000', summary )
            for command, summary, code in zip( commands, summaries, codes )
        ] ) ]

        # Generate the final help text:
        help = (ShellCommands % tuple( items )).replace( '[[', '\x00B'
                                              ).replace( ']]', '\x000'
                                              ).replace( '<<', '\x00C'
                                              ).replace( '>>', '\x000' )

        return self.shell.history_item_for(
            OutputItem, help, tags = tags, lod = 2
        )


    def help_for_items ( self ):
        """ Returns help information about shell item keyboard and mouse
            shortcuts.
        """
        key_info    = {}
        method_info = set()
        self._item_keys_for( ShellItem, key_info, method_info )
        keys = key_info.keys()
        keys.sort( lambda l, r: cmp_key_name( l, r ) )
        max_len       = reduce( lambda x, y: max( x, len( y ) ), keys, 0 )
        format_tagged = '%%%ds = %%s%%s' % (-(max_len + 8))
        format_simple = '%%%ds = %%s%%s' % (-(max_len + 4))
        output        = []
        tags          = []
        for key in keys:
            for kind, info in key_info[ key ]:
                if kind == 'Shell':
                    kind = ''
                else:
                    kind = '\x00C[%s]\x000 ' % kind

                info = '\n'.join( [
                    line.strip() for line in info.split( '\n' )
                ] )
                items = info.split( '\n\n', 1 )
                info  = ('\n' + (' ' * (max_len + 3))).join(
                        items[0].split( '\n' ) )
                cc     = '\x00B'
                format = format_simple
                if len( items ) > 1:
                    cc     = color_tag_for( 'B', tags )
                    format = format_tagged
                    tags.append( TextTag( text = items[1] ) )

                output.append(
                    format % ( '%s%s\x000' % ( cc, key ), kind, info )
                )

        return self.shell.history_item_for(
            OutputItem, (replace_markers( ShellItems ) % ('\n'.join( output ))),
            tags = tags, lod = 2
        )

    #-- Private Methods --------------------------------------------------------

    def _pretty_print ( self, text ):
        """ Attempts to pretty print a docstring specified by *text*.
        """
        lines = text.split( '\n', 1 )
        print lines[0].strip()
        if len( lines ) > 1:
            print trim_margin( lines[1] )


    def _item_keys_for ( self, klass, key_info, method_info ):
        """ Extracts any new key shortcut information from the class specified
            by *klass*.
        """
        # Get the name of this class:
        class_name = getattr( klass, 'ui_name', klass.__name__[:-4] )

        # Extract out the key information for any new key methods we haven't
        # seen before:
        for name in dir( klass ):
            if name[:4] == 'key_':
                value = getattr( klass, name )
                if (isinstance( value, UnboundMethodType ) and
                    (value.im_func not in method_info)):
                    items = name[4:].replace( 'alt_',   'Alt-',
                                   ).replace( 'ctrl_',  'Ctrl-',
                                   ).replace( 'shift_', 'Shift-' ).split('-' )
                    last  = items[-1]
                    if len( last ) > 1:
                        items[-1] = KeyMap.get( last, last ).capitalize()

                    key_info.setdefault( '-'.join( items ), [] ).append(
                        ( class_name, value.__doc__.strip() )
                    )
                    method_info.add( value.im_func )

        # Recursively add information for all subclasses of this class:
        for subclass in klass.facet_subclasses():
            self._item_keys_for( subclass, key_info, method_info )

#-- EOF ------------------------------------------------------------------------
