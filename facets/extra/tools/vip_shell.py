"""
Defines the VIP (Visual Interactive Python) shell tool.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Any, Instance, Event, Property, View, Item, VIPShellEditor, \
           Handler

from facets.extra.helper.has_payload \
    import HasPayload

from facets.ui.ui_info \
    import UIInfo

from facets.ui.vip_shell.items.api \
    import ShellItem

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'VIPShellHandler' class:
#-------------------------------------------------------------------------------

class VIPShellHandler ( Handler ):
    """ Custom handler class for a VIPShell instance view.
    """

    def init_info ( self, info ):
        """ Informs the handler what the UIInfo object for a View will be.
        """
        info.ui.context[ 'object' ].info = info

#-------------------------------------------------------------------------------
#  'VIPShell' class:
#-------------------------------------------------------------------------------

class VIPShell ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'VIP Shell' )

    # The 'locals' dictionary for use by the shell:
    values = Any( {} )

    # The value used to send external data into the shell via the '_' variable:
    input = Any( connect = 'to', droppable = True )

    # The current value of the '_' variable:
    output = Any( connect = 'from', draggable = True )

    # The most recently exported history item:
    export = Any( connect = 'from', draggable = True )

    # The most recently generated profiler data file:
    profile = Any( connect = 'from', draggable = True )

    # Shell history item to be sent to an external shell:
    send = Instance( ShellItem, connect = 'from' )

    # Shell history item received from an external shell:
    receive = Instance( ShellItem, connect = 'to' )

    # A Python command to be executed by the shell:
    command = Event

    # Event fired when the user executes a command in the shell:
    executed = Event

    # The UIInfo object associated with the shell's view:
    info = Instance( UIInfo )

    # A reference to the VIPShellEditor associated with the shell's view:
    shell = Property

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            Item( 'values',
                  id         = 'values',
                  show_label = False,
                  editor     = VIPShellEditor(
                      share    = True,
                      export   = 'export',
                      profile  = 'profile',
                      send     = 'send',
                      receive  = 'receive',
                      command  = 'command',
                      executed = 'executed'
                  )
            ),
            title   = 'VIP Shell',
            id      = 'facets.extra.tools.vip_shell.' + self.name,
            handler = VIPShellHandler
        )

    #-- Property Implementations -----------------------------------------------

    def _get_shell ( self ):
        return self.info.values

    #-- Facet Event Handlers ---------------------------------------------------

    def _input_set ( self, value ):
        """ Handles the 'input' facet being changed.
        """
        if isinstance( value, HasPayload ):
            self.values[ '__name' ]      = value.payload_name
            self.values[ '__full_name' ] = value.payload_full_name
            value                        = value.payload

        self.values[ '_' ] = self.output = value
        self.command = '_'


    def _executed_set ( self ):
        """ Handles the 'executed' event being fired.
        """
        value = self.values.get( '_' )
        if value is not None:
            self.output = value

#-- Run the tool (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    VIPShell().edit_facets()

#-- EOF ------------------------------------------------------------------------
