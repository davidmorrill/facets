"""
Defines the ShellCommand class that is the concrete base class for all VIP shell
command implementations.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Str, Enum, Any, Bool

#-------------------------------------------------------------------------------
#  'ShellCommand' class
#-------------------------------------------------------------------------------

class ShellCommand ( HasPrivateFacets ):
    """ Base class for all dynamically loaded shell commands.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Short (one-liner) summary of what the command does:
    summary = Str

    # The complete help text description of what the command does:
    help = Str

    # The type of data the options specify:
    options_type = Enum( 'none', 'path', 'file', 'source', 'expression' )

    #-- Facets Set by Shell ----------------------------------------------------

    # The shell object this is a shell command for:
    shell = Any # Instance( vipShellEditor )

    # The current command:
    command = Str

    # The options for the current command:
    options = Str

    # The list of items that have been returned by prior sub-commands:
    items = Any( [] )

    # Is this a help request (or execute)?
    is_help = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def execute ( self ):
        """ Executes the command and returns either None, a string in shell
            help format, a ShellItem or a list of ShellItems.
        """


    def show_help ( self ):
        """ Returns a string containing the help information for the command.
            The string may wrap portions of the text in [[...]] for emphasis,
            or <<...>> for examples.
        """
        if self.help != '':
            return self.help

        return ('No help available for the [[/%s]] command.' % self.command)

    #-- Helper Methods ---------------------------------------------------------

    def evaluate ( self, code = None ):
        """ Attempts to return the result of evaluating *code*. If *code* is
            omitted, the command options are used instead.
        """
        if code is None:
            code = self.options

        try:
            return eval( code, self.shell.locals )
        except:
            raise SyntaxError( 'Could not evaluate command options.' )


    def bad_options ( self ):
        """ Raises a syntax error exception for an invalid command option.
        """
        raise SyntaxError( 'Unrecognized option: %s.' % self.options )


    def has_no_options ( self ):
        """ Verify that no options were specified for the current command.
        """
        if self.options != '':
            raise SyntaxError( 'No command options are defined.' )

#-- EOF ------------------------------------------------------------------------
