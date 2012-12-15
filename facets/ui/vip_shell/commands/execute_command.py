"""
Defines the ExecuteCommand VIP Shell command used to execute a Python source
file.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import join, isfile, splitext

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Help information for the 'x' command:
XHelp = """
Executes the Python source file specified by the command's options, which should
be the name of the source file to execute. The [[.py]] file extension is optional
and may be omitted.

Examples:
<</x mytest>>             = Executes the mytest.py file.
<</x C:\\test\\example.py>> = Executes the <<C:\\test\\example.py>> file
"""[1:-1]

#-------------------------------------------------------------------------------
#  'ExecuteCommand' class:
#-------------------------------------------------------------------------------

class ExecuteCommand ( ShellCommand ):
    """ Performs an 'execfile' on the command's options, which should be the
        name of a Python source file.
    """

    summary      = 'Executes a specified Python source file.'
    help         = XHelp
    options_type = 'source'


    def execute ( self ):
        """ Executes the Python source file specified by the command's options.
        """
        file = self.options
        if file == '':
            raise SyntaxError( 'A Python source file name must be specified.' )

        py_file = join( self.shell.cwd, file )
        if (not isfile( py_file )) and (splitext( file )[1] == ''):
            py_file += '.py'
            if not isfile( py_file ):
                raise ValueError( 'Invalid Python source file name.' )

        self.shell.execute_file( py_file )

#-- EOF ------------------------------------------------------------------------
