"""
Defines the NoopCommand VIP Shell command that performs no operation (useful as
a comment of python code block delimiter).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

NoopHelp = """
Performs no operation. It is, in effect, a comment and can be used to separate
several blocks of Python code. This is useful, for example, when using the
'time' command ([[/t]]) to display separate execution times for each block of Python
code to be executed.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'NoopCommand' class:
#-------------------------------------------------------------------------------

class NoopCommand ( ShellCommand ):
    """ Do nothing command.
    """

    summary = 'Does nothing (useful as a comment or Python code separator).'
    help    = NoopHelp

#-- EOF ------------------------------------------------------------------------
