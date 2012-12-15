"""
Defines the API exported by the facets.ui.vip_shell.commands package.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from cd_command \
    import CDCommand

from dir_command \
    import DirCommand

from execute_command \
    import ExecuteCommand

from file_explorer_command \
    import FileExplorerCommand

from filter_command \
    import FilterCommand

from help_command \
    import HelpCommand

from list_implementation_command \
    import ListImplementationCommand

from lod_command \
    import LODCommand

from ls_command \
    import LSCommand

from lx_command \
    import LXCommand

from no_clear_command \
    import NoClearCommand

from noop_command \
    import NoopCommand

from options_command \
    import OptionsCommand

from os_command \
    import OSCommand

from profile_command \
    import ProfileCommand

from pwd_command \
    import PWDCommand

from shell_command \
    import ShellCommand

from show_hide_command \
    import ShowHideCommand

from time_command \
    import TimeCommand

from view_command \
    import ViewCommand

#-------------------------------------------------------------------------------
#  List of standard shell commands:
#-------------------------------------------------------------------------------

# The list of standard shell commands:
standard_shell_commands = [
    ( 'cd',   CDCommand                 ),
    ( 'dir',  DirCommand                ),
    ( 'fx',   FileExplorerCommand       ),
    ( 'l',    LSCommand                 ),
    ( 'li',   ListImplementationCommand ),
    ( 'lod',  LODCommand                ),
    ( 'ls',   LSCommand                 ),
    ( 'lx',   LXCommand                 ),
    ( 'p',    ProfileCommand            ),
    ( 'pp',   ProfileCommand            ),
    ( 'pwd',  PWDCommand                ),
    ( 'o',    OptionsCommand            ),
    ( 'os',   OSCommand                 ),
    ( 't',    TimeCommand               ),
    ( 'view', ViewCommand               ),
    ( 'x',    ExecuteCommand            ),
    ( '=',    FilterCommand             ),
    ( '/',    ShowHideCommand           ),
    ( '#',    NoopCommand               ),
    ( '~',    NoClearCommand            ),
    ( '',     HelpCommand               ),
]

#-- EOF ------------------------------------------------------------------------
