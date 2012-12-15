"""
Defines the CDCommand VIP Shell command used to change the current working
directory of the shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import abspath, join, isdir

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Help information about using the 'cd' command:
CDHelp = """
Changes the shell's current working directory to the directory specified by the
command's options, which should either be an absolute path, or a path relative
to the current working directory.

If no options are specified, the current working directory is not changed.

In any case, the new current working directory is displayed.

Examples:
<</cd ..>>         = Change to the parent of the current working directory.
<</cd ./examples>> = Change to the specified subdirectory of the current directory.
<</cd C:\\test>>    = Change to the specified absolute directory.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'CDCommand' class:
#-------------------------------------------------------------------------------

class CDCommand ( ShellCommand ):
    """ Changes/Displays the current working directory.
    """

    summary      = 'Change the current working directory.'
    help         = CDHelp
    options_type = 'path'


    def execute ( self ):
        """ Changes the current working directory.
        """
        shell = self.shell
        path  = self.options
        if path != '':
            path = abspath( join( shell.cwd, path ) )
            if not isdir( path ):
                raise ValueError(
                    "The path specified by '%s' is not a directory." %
                    self.options
                )

            shell.cwd = path

        print shell.cwd

#-- EOF ------------------------------------------------------------------------
