"""
Defines the LSCommand VIP Shell command used to list file system files.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import abspath, join, dirname, isdir

from glob \
    import glob

from facets.ui.vip_shell.items.api \
    import DirectoryItem

from facets.ui.vip_shell.helper \
    import file_class_for

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Help information about using the 'ls' command:
LSHelp = """
Lists all files and directories matching the command's options, which should be
a path possibly containing wildcard characters such as [['*']] and [['?']].

If no options are specified, then all file and directories in the current
working directories are listed.

Examples:
<</ls>>                = List all file and directories in the current directory.
<</ls *.txt>>          = List all files with a .txt extension in the current directory.
<</ls examples\\*.py*>> = List all Python related files in the examples subdirectory.
"""[1:-1]

# Help information about using the 'l' command:
LSPythonHelp = """
Lists all Python [[.py]] files matching the command's options, which should be
a path to a directory containing Python source code.

If no options are specified, then all Python source file in the current working
directories are listed.

Examples:
<</l>>          = List all Python source files in the current directory.
<</l examples>> = List all Python source files in the examples subdirectory.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'LSCommand' class:
#-------------------------------------------------------------------------------

class LSCommand ( ShellCommand ):
    """ Lists files in the current working directory (or elsewhere).
    """

    def execute ( self ):
        """ Displays files in the current working directory, or elsewhere if an
            explicit path is provided in the command's options.
        """
        search      = self.options
        files       = []
        directories = []
        search_path = abspath( join( self.shell.cwd, search ) )
        if isdir( search_path ):
            if self.command == 'l':
                search_path = join( search_path, '*.py' )
            else:
                search_path = join( search_path, '*' )

        base_path = dirname( search_path )
        for name in glob( search_path ):
            if isdir( join( base_path, name ) ):
                directories.append( name )
            else:
                files.append( name )

        hif = self.shell.history_item_for

        return ([ hif( DirectoryItem, name )          for name in directories ]
              + [ hif( file_class_for( name ), name ) for name in files ])


    def show_help ( self ):
        """ Displays help for using the 'l/ls' command.
        """
        if self.command == 'l':
            return LSPythonHelp

        return LSHelp

    #-- Facet Default Values ---------------------------------------------------

    def _summary_default ( self ):
        if self.command == 'l':
            return 'Display the names of Python source files in a directory.'

        return 'Display the names of wildcard matching files in a directory.'


    def _options_type_default ( self ):
        if self.command == 'l':
            return 'source'

        return 'file'

#-- EOF ------------------------------------------------------------------------
