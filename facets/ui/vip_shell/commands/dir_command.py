"""
Defines the DirCommand shell command that allows the user to perform a 'dir'
on a specified options object.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The help message for the command:
HELP = """
Prints out the result of dir( [[options]] ), where [[options]] should be a Python
expression that evaluates to the object to perform the <<dir()>> on. If [[options]]
is omitted, the current contents of the shell are displayed.
"""[1:-1]


class DirCommand ( ShellCommand ):
    """ Defines the DirCommand shell command that allows the user to perform a
        'dir' on a specified options object.
    """

    summary      = 'Prints out the result of dir( [[options]] ).'
    help         = HELP
    options_type = 'expression'


    def execute ( self ):
        """ Validate the options and request a callback when all commands have
            been run.
        """
        if self.options == '':
            items = self.shell.locals.keys()
            items.sort()
        else:
            items = dir( self.evaluate() )

        for name in items:
            print name

#-- EOF ------------------------------------------------------------------------
