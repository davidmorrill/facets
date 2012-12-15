"""
Defines the OSCommand shell command that allows the user to perform an operating
system shell command (e.g. cat or ls).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from subprocess \
    import Popen, PIPE

from facets.ui.vip_shell.items.api \
    import OutputItem, ErrorItem

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The help message for the command:
HELP = """
Executes the OS command specified by [[options]], where [[options]] should be a
an operating system command and its argument (e.g. cat foo.py). The command
should not require console input from stdin, but send output sent to stdout or
stderr. Any output produced by the command is displayed as normal shell stdout
or stderr history items.
"""[1:-1]


class OSCommand ( ShellCommand ):
    """ Defines the OSCommand shell command that allows the user to perform an
        operating system shell command (e.g. cat or ls).
    """

    summary      = 'Executes the OS command specified by [[options]].'
    help         = HELP
    options_type = 'path'


    def execute ( self ):
        """ Validate the options and request a callback when all commands have
            been run.
        """
        if self.options == '':
            raise SyntaxError( 'No command specified.' )

        process = Popen( self.options,
            stdout = PIPE,
            stderr = PIPE,
            shell  = True
        )

        stdout, stderr = process.communicate()
        result         = []
        hif            = self.shell.history_item_for
        if len( stdout ) > 0:
            result.append( hif( OutputItem, stdout, lod = 2 ) )

        if len( stderr ) > 0:
            result.append( hif( ErrorItem, stderr, lod = 2 ) )

        rc = process.poll()
        if rc:
            result.append( hif( ErrorItem, 'Return code was: %d' % rc ) )

        return result

#-- EOF ------------------------------------------------------------------------
