"""
The Use Script tool allows you to load a module previously generated from a
Script tool and use it as a normal tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Str, Instance, View, HGroup, Item, UItem, EnumEditor, \
           on_facet_set, spring

from tools \
    import XTool

from script \
    import ScriptTool, ExportedTools

#-------------------------------------------------------------------------------
#  'UseScript' class:
#-------------------------------------------------------------------------------

class UseScript ( XTool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Use Script'

    # The currently selected generated script tool name:
    tool_name = Str( 'None', save_state = True )

    # The current generated script tool:
    tool = Instance( ScriptTool )

    # The input to send to the currently loaded script tool:
    input = Any( connect = 'to' )

    # The output to forward from the currently loaded script tool:
    output = Any( connect = 'from' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'tool', style = 'custom' )
    )


    def options ( self ):
        tool_names = (
            [ 'None' ] +
            sorted( self.facet_db_get( ExportedTools, {} ).iterkeys() )
        )

        return View(
            HGroup(
                Item( 'tool_name', editor = EnumEditor( values = tool_names ) ),
                spring,
                group_theme = '#themes:tool_options_group'
            )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _tool_name_set ( self, tool_name ):
        """ Handles the 'tool_name' facet being changed.
        """
        info = None
        if tool_name != 'None':
            info = self.facet_db_get( ExportedTools, {} ).get( tool_name )

        if info is None:
            self.tool = None
        else:
            file_name, class_name = info
            locals                = {}
            try:
                execfile( file_name, locals )
                self.tool = locals[ class_name ]( tools = self.tools )
            except:
                import traceback
                traceback.print_exc()
                self.tool = None


    def _tool_set ( self, tool, old ):
        """ Handles the 'tool' facet being changed.
        """
        if old is not None:
            del old.tools[:]

        if (tool is not None) and (self.input is not None):
            tool.input = self.input


    def _input_set ( self, input ):
        """ Handles the 'input' facet being changed.
        """
        if self.tool is not None:
            self.tool.input = input


    @on_facet_set( 'tool:output' )
    def _output_modified ( self, output ):
        """ Handles the loaded tool's 'output' facet being changed.
        """
        self.output = output


    @on_facet_set( 'tools[]' )
    def _tools_modified ( self, added, removed ):
        """ Handles the 'tools' facet being changed.
        """
        tool = self.tool
        if tool is not None:
            tools = tool.tools
            for removed_tool in removed:
                tools.remove( removed_tool )

            for added_tool in added:
                tools.append( added_tool )

#-- EOF ------------------------------------------------------------------------
