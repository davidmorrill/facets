"""
Defines the ShowHideCommand VIP Shell command used to show or hide shell history
items.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.vip_shell.helper \
    import TypeCodes, ItemSet

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Help information about using the 'show_hide' command:
ShowHideHelp = """
Shows or hides items in the shell history list based upon the options provided.
If no options are specified, then all currently hidden history items are made
visible again.

If specified, The options should be a string of the form:[[ [+|-]types]], where
'types' can be a string containing zero, one or more of the following history
item type codes:

[[c]]: Commands
[[o]]: Output (i.e. [[stdout]])
[[e]]: Errors (i.e. [[stderr]])
[[r]]: Results
[[x]]: Exceptions
[[f]]: Files (and directories)

If no 'types' are specified, then all types are assumed.

The list of types may optionally be preceded by a [['+']] or [['-']] character. If [['+']]
is specified, then only the currently visible history items matching 'types'
will remain visible; all other items will be hidden.

If a leading [['-']] is specified, then all currently visible history items matching
'types' will be hidden; all other items will remain visible.

If no leading [['+']] or [['-']] is specified, [['+']] is assumed.

Examples:
<<//>>     = Show all currently hidden history items.
<<// +c>>  = Show only currently visible command items.
<<// -ex>> = Hide all currently visible stderr output and expeptions items.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'ShowHideCommand' class:
#-------------------------------------------------------------------------------

class ShowHideCommand ( ShellCommand ):
    """ Hides or shows items in the shell history.
    """

    summary = 'Shows or hides history list items.'
    help    = ShowHideHelp

    #-- Public Methods ---------------------------------------------------------

    def execute ( self ):
        """ Hides or shows items in the shell history.
        """
        # Indicate that we want to do the processing later:
        return self.pre_callback


    def pre_callback ( self ):
        """ Hides or shows items in the shell history.
        """
        # Indicate that we want to do the processing later:
        return self.post_callback


    def post_callback ( self ):
        """ Hides or shows items in the shell history.
        """
        options = self.options
        if options == '':
            self.shell.show_all()
        else:
            show    = True
            leading = options[:1]
            if leading in '+-':
                show    = leading == '+'
                options = options[1:]

            types = []
            for c in options:
                if c != ' ':
                    type = TypeCodes.get( c )
                    if type is not None:
                        types.append( type )


            if len( types ) == 0:
                types = ItemSet
            else:
                types = set( types )

            if show:
                self.shell.show_any( types )
            else:
                self.shell.hide_any( types )

#-- EOF ------------------------------------------------------------------------
