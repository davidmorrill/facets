"""
Defines the ListImplementationCommand VIP Shell command used to list the Python
source files used to implement to specified Python object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.vip_shell.items.api \
    import PythonFileItem

from facets.ui.vip_shell.helper \
    import source_files_for

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Help information about using the 'li' (list implementation) command:
ListImplementationHelp = """
Lists all Python source files used in the implementation of the object
specified in the command's options, which should be a Python expression that
evaluates to the object whose implementation is to be found.

Examples:
<</li my_view>>: List all files used in the implementation of <<my_view>>.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'ListImplementationCommand' class:
#-------------------------------------------------------------------------------

class ListImplementationCommand ( ShellCommand ):
    """ Lists all Python source files used in the implementation of the object
        specified by the command's options, which should be a Python expression.
    """

    summary      = ('Display the names of Python source files used to '
                    'implement an object.')
    help         = ListImplementationHelp
    options_type = 'expression'

    #-- Public Methods ---------------------------------------------------------

    def execute ( self ):
        """ Displays the source files used to implement an object.
        """
        if self.options == '':
            raise ValueError( 'An object must be specified.' )

        # Get the implementation source files for the specified object:
        file_names = source_files_for( self.evaluate() )
        if file_names is None:
            print 'No implementation information available.'

            return None

        self.shell.status = '%d source files found.' % len( file_names )

        # Return PythonFileItem's for all of the source files found:
        hif = self.shell.history_item_for

        return [ hif( PythonFileItem, file_name ) for file_name in file_names ]

#-- EOF ------------------------------------------------------------------------
