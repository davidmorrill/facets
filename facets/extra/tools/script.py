"""
The Script tool provides a simple way to create new tools directly within the
tools framework by editing and running Python code that receives input and
produces output that can be connected to other tools.
"""

#-------------------------------------------------------------------------------
#  Issues:
#  - Sending data too fast through the pipeline can cause a mysterious window
#    whose contents are empty and whose title is 'python' to appear.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from os.path \
    import isdir, join

from facets.api \
    import HasPrivateFacets, Any, Str, Code, Directory, Instance, DelegatesTo, \
           Property, Button, View, HSplit, HGroup, VGroup, Item, UItem,        \
           CodeEditor, on_facet_set, property_depends_on

from facets.core.facet_base \
    import invoke, write_file, time_stamp, class_name_to_file_name, \
           class_name_to_user_name

from facets.ui.pyface.timer.api \
    import do_later

from text_file \
    import TextFile

from tools \
    import XTool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The Facets UI database key for all script generated tools:
ExportedTools = 'facets.extra.tools.script.ExportedTools'

# The default source code to use if no saved source is available:
DefaultSource = """
# Your code should define a value called 'run', which can be a function, a value
# or a class or instance derived from ScriptTool. Click the 'gear' icon to
# compile your script or the 'wrench' icon to generate a Python module.
#
# Some examples:
#
# run = range( 10 )
#
# def run ( input ):
#     return range( input ) if isinstance( input, int ) else []
#

class run ( ScriptTool ):
    n = Range( 0, 100, 10 )

    def _n_set ( self, n ):
        self.output = range( n )
"""[1:]

# The prologue code added to the user's source code:
PrologueCode = """
from facets.api import *
from facets.extra.tools.script import ScriptTool

"""[1:]

ScriptTemplate = '''
"""
%(class_name)s: A Facets Script tool.

Generated by: facets.extra.tools.script
Date/Time:    %(date)s
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \\
    import *

from facets.extra.tools.script \\
    import ScriptTool

#-------------------------------------------------------------------------------
#  User defined %(type)s:
#-------------------------------------------------------------------------------

%(source)s

#-------------------------------------------------------------------------------
#  '%(class_name)s' class:
#-------------------------------------------------------------------------------

class %(class_name)s ( %(super_class_name)s ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = '%(tool_name)s'%(extra_code)s

#-- EOF ------------------------------------------------------------------------
'''[1:-1]

# The extra code needed for a constant 'run' value:
ConstantExtraCode = """

    # The output from the tool:
    output = Constant( run, connect = 'from' )
"""[:-1]

# The extra code needed for a function 'run' value:
FunctionExtraCode = """

    # The function used to process input:
    run = Constant( run )
"""[:-1]

# The extra code needed for a ScriptTool subclass/instance 'run' value:
ClassExtraCode = ''

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def class_name_for ( class_name ):
    """ Returns a sanitized version of the class name specified by *class_name*.
    """
    return class_name.replace( ' ', '' )

#-------------------------------------------------------------------------------
#  'ScriptTool' class:
#-------------------------------------------------------------------------------

class ScriptTool ( XTool ):
    """ The ScriptTool class is the base class for classes created within a
        Script tool instance.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The input to the tool:
    input = Any( connect = 'to', editable = False )

    # The output from the tool:
    output = Any( connect = 'from', editable = False )

    # The text version of the output from the tool:
    text_output = Str( connect = 'from: text output', editable = False )

    #-- Facet Event Handlers ---------------------------------------------------

    def _input_set ( self, input ):
        """ Handles the 'input' facet being changed.
        """
        output = invoke( self.run, self.input )
        if output is not None:
            self.output      = output
            self.text_output = str( output )

    #-- Public Methods ---------------------------------------------------------

    def run ( self, input ):
        """ Processes the current input to the tool and produces optional
            output.
        """
        return input

#-------------------------------------------------------------------------------
#  'Script' class:
#-------------------------------------------------------------------------------

class Script ( XTool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Script'

    # Input being sent to the tool from other tools:
    input = Any( connect = 'to' )

    # Output generated by the tool:
    output = Any( connect = 'from' )

    # The text version of the output generated by the tool:
    text_output = Str( connect = 'from' )

    # The current Python source code being edited:
    source = DelegatesTo( 'text_file', 'text', connect = 'to: source code' )

    # The most recent version of the code that was successfully executed:
    saved_source = Code( save_state = True )

    # The most recently created 'run' function:
    run = Any # compiled Python function: run() or run(input)

    # The most recently created ScriptTool object:
    script_tool = Instance( ScriptTool )

    # The TextFile object used to edit the source code:
    text_file = Instance( TextFile )

    # The event fired when the user wants to run the current source code:
    execute = Button( '@icons2:Gear?l6S62' )

    # The event fired when the user wants to generate code for the script:
    generate = Button( '@icons2:Tool_2?H59' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HSplit(
            UItem( 'text_file',
                   label = 'Source',
                   style = 'custom',
                   dock  = 'tab'
            ),
            UItem( 'script_tool',
                   label = 'Tool UI',
                   style = 'custom',
                   dock  = 'tab'
            ),
            id = 'splitter'
        )
    )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        do_later( self._restore_source )

    #-- Facet Default Values ---------------------------------------------------

    def _text_file_default ( self ):
        return TextFile( toolbar_items = [
            UItem( 'context.execute',
                   tooltip = 'Compile the script'
            ),
            UItem( 'context.generate',
                   tooltip      = 'Generate a Python source module',
                   enabled_when = "context.saved_source != ''"
            )
        ] )

    #-- Facet Event Handlers ---------------------------------------------------

    def _input_set ( self ):
        """ Handles the 'input' facet being changed.
        """
        self._run_set()
        self._script_tool_set()


    @on_facet_set( 'script_tool:output' )
    def output_modified ( self, output ):
        """ Handles the current generated script tool's output being changed.
        """
        self.output      = output
        self.text_output = str( output )


    def _run_set ( self ):
        """ Handles the 'run' facet being changed.
        """
        if self.run is not None:
            output = invoke( self.run, self.input )
            if output is not None:
                self.output      = output
                self.text_output = str( output )


    def _script_tool_set ( self ):
        """ Handles the 'script_tool' facet being changed.
        """
        if self.script_tool is not None:
            self.script_tool.input = self.input


    def _execute_set ( self ):
        """ Handles the user clicking the 'execute' button.
        """
        text_file = self.text_file
        locals    = {}
        source    = self.source
        try:
            exec (PrologueCode + source) in locals
            run = locals.get( 'run' )
            if run is None:
                text_file.status = ('No run function, object or value is '
                                    'defined.')
                source           = None
            elif isinstance( run, ScriptTool ):
                self.script_tool = run.set( tools = self.tools )
                self.run         = None
            elif isinstance( run, type ) and issubclass( run, ScriptTool ):
                self.script_tool = run( tools = self.tools )
                self.run         = None
            elif callable( run ):
                self.run         = run
                self.script_tool = None
            else:
                self.run         = self.script_tool = None
                self.output      = run
                self.text_output = str( run )

            if source is not None:
                text_file.status  = 'Script successfully run'
                self.saved_source = source
        except Exception, excp:
            msg   = str( excp )
            match = re.search( r'(.*)\(<string>,\s*line\s+(\d+)\)', msg )
            if match:
                msg = match.group( 1 )
                text_file.selected_line = int( match.group( 2 ) ) - 3

            text_file.status = msg.capitalize()


    def _generate_set ( self ):
        """ Handles the user clicking the 'generate source module' button.
        """
        super_class_name = 'ScriptTool'
        if self.run is not None:
            extra_code = FunctionExtraCode
            type       = 'function'
        elif self.script_tool is None:
            extra_code = ConstantExtraCode
            type       = 'constant'
        else:
            super_class_name = self.script_tool.__class__.__name__
            extra_code       = ''
            type             = 'class'

        self._temp = ToolGenerator(
            source           = self.saved_source.rstrip(),
            super_class_name = super_class_name,
            extra_code       = extra_code,
            type             = type
        )
        self._temp.edit_facets()


    @on_facet_set( 'tools[]' )
    def _tools_modified ( self, added, removed ):
        """ Handles the 'tools' facet being changed.
        """
        tool = self.script_tool
        if tool is not None:
            tools = tool.tools
            for removed_tool in removed:
                tools.remove( removed_tool )

            for added_tool in added:
                tools.append( added_tool )

    #-- Private Methods --------------------------------------------------------

    def _restore_source ( self ):
        """ Restores any previously saved source when the tool is reloaded.
        """
        self.source = (self.saved_source if self.saved_source != '' else
                       DefaultSource)
        self._execute_set()

#-------------------------------------------------------------------------------
#  'ToolGenerator' class:
#-------------------------------------------------------------------------------

class ToolGenerator ( HasPrivateFacets ):
    """ Generates a new tool Python source file from a user script.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The user supplied source code used to build the tool:
    source = Str

    # The source code for the generated tool class:
    code = Property # ( Str )

    # The name of the tool:
    tool_name = Str( 'My Tool' )

    # The class name of the generated tool:
    class_name = Str( 'MyTool' )

    # The super class name of the generated tool class:
    super_class_name = Str( 'ScriptTool' )

    # The extra code to add to the generated code:
    extra_code = Str

    # The type of user supplied code:
    type = Str

    # The file path to save the generated tool to:
    path = Directory

    # The Python source file name (minus path) to save the generated tool to:
    file_name = Str( 'my_tool.py' )

    # Status message:
    status = Str

    # Save the source code to the specified file name:
    save = Button( 'Save' )

    # Is there source code ready to be saved?
    saveable = Property

    # Dictionary used to generate the source code from a template:
    data = Any

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            VGroup(
                HGroup(
                    Item( 'class_name', width   = -150 ),
                    Item( 'tool_name',  springy = True )
                ),
                HGroup(
                    Item( 'file_name', width   = -150, label = '   File name' ),
                    Item( 'path',      springy = True, label = '         Path' )
                ),
                group_theme = '@xform:b?L35'
            ),
            HGroup(
                UItem( 'status', style = 'readonly', springy = True ),
                UItem( 'save', enabled_when = 'saveable' ),
                group_theme = '@xform:b?L35',
            ),
            show_labels = False
        ),
        VGroup(
            UItem( 'code',
                   style  = 'readonly',
                   editor = CodeEditor( show_line_numbers = False )
            ),
        ),
        title     = 'Facets Script Tool Generator',
        id        = 'facets.extra.tools.script.ToolGenerator',
        width     = 0.5,
        height    = 0.5,
        resizable = True
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'class_name, tool_name' )
    def _get_code ( self ):
        self.data.update( {
            'class_name': class_name_for( self.class_name.strip() ),
            'tool_name':  self.tool_name.strip().replace( "'", "\\'" )
        } )

        return (ScriptTemplate % self.data)


    @property_depends_on( 'class_name, tool_name, file_name, path' )
    def _get_saveable ( self ):
        return ((self.class_name.strip() != '') and
                (self.tool_name.strip()  != '') and
                (self.file_name.strip()  != '') and
                isdir( self.path ))

    #-- Facet Default Values ---------------------------------------------------

    def _data_default ( self ):
        return {
            'source':           self.source,
            'super_class_name': self.super_class_name,
            'extra_code':       self.extra_code,
            'type':             self.type,
            'date':             time_stamp()
        }


    def _path_default ( self ):
        return self.facet_db_get( 'path', '' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _class_name_set ( self, class_name, old ):
        """ Handles the 'class_name' facet being changed.
        """
        self.file_name = class_name_to_file_name( class_name_for( class_name ) )
        do_later( self._update_tool_name, class_name_for( old ) )


    def _save_set ( self ):
        """ Handles the 'save' facet being changed.
        """
        file_name = join( self.path, self.file_name )
        if write_file( file_name, self.code ):
            exported_tools = self.facet_db_get( ExportedTools, {} )
            for tool_name, info in exported_tools.iteritems():
                if file_name == info[0]:
                    del exported_tools[ tool_name ]

                    break

            exported_tools[ self.tool_name ] = ( file_name, self.class_name )
            self.facet_db_set( ExportedTools, exported_tools )
            self.facet_db_set( 'path', self.path )
            self.status = '%s saved on %s' % ( file_name, time_stamp() )
        else:
            self.status = 'Error occurred trying to write %s' % file_name

    #-- Private Methods --------------------------------------------------------

    def _update_tool_name ( self, old_class_name ):
        """ Updates the tool name to one based on the latest class name if the
            previous tool name was also based on the old class name.
        """
        if class_name_to_user_name( old_class_name ) == self.tool_name:
            self.tool_name = class_name_to_user_name(
                class_name_for( self.class_name )
            )

#-- EOF ------------------------------------------------------------------------
