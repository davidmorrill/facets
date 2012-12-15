"""
Defines the Shell tool.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Any, Event, View, Item, ShellEditor

from facets.extra.helper.has_payload \
    import HasPayload

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'Shell' class:
#-------------------------------------------------------------------------------

class Shell ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Shell' )

    # The 'locals' dictionary for use by the shell:
    values = Any( { '_': None } )

    # The value used to send external data into the shell via the '_' variable:
    input = Any( connect = 'to', droppable = True )

    # The current value of the '_' variable:
    output = Any( connect = 'from', draggable = True )

    # A Python command to be executed by the shell:
    command = Event

    # Event fired when the user executes a command in the shell:
    command_executed = Event

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'values',
              show_label = False,
              editor     = ShellEditor( share            = True,
                                        command          = 'command',
                                        command_executed = 'command_executed' )
        ),
        title = 'Shell'
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _input_set ( self, value ):
        """ Handles the 'input' facet being changed.
        """
        if isinstance( value, HasPayload ):
            self.values[ '__' ]  = value.payload_name
            self.values[ '___' ] = value.payload_full_name
            value                = value.payload

        self.values[ '_' ] = self.output = value
        self.command = '_'


    def _command_executed_set ( self ):
        """ Handles the 'command_executed' event being fired.
        """
        value = self.values.get( '_' )
        if value is not None:
            self.output = value

#-------------------------------------------------------------------------------
#  Create exported objects:
#-------------------------------------------------------------------------------

view = Shell()

#-- EOF ------------------------------------------------------------------------