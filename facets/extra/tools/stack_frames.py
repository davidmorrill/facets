"""
Displays the stack frames associated with the current FBI debugger context
and allows the develop to select the current frame of interest.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import join

from facets.api \
    import Str, Float, Bool, Constant, Property, View, Item, GridEditor, \
           property_depends_on

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.helper.file_position \
    import FilePosition

from facets.extra.helper.fbi \
    import FBI

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'StackFrameAdapter' class:
#-------------------------------------------------------------------------------

class StackFrameAdapter ( GridAdapter ):
    """ Grid adapter for mapping StackFrame objects to a GridEditor.
    """

    columns = [
        ( 'Function',  'function_name' ),
        ( 'Source',    'source'        ),
        ( 'Line',      'line'          ),
        ( 'File Name', 'file_name'     ),
        ( 'File Path', 'file_path'     ),
    ]

    # Column alignments:
    line_alignment         = Str( 'center' )

    # Column widths:
    function_name_width    = Float( 0.20 )
    source_width           = Float( 0.44 )
    line_width             = Float( 0.06 )
    file_name_width        = Float( 0.20 )
    file_path_width        = Float( 0.10 )

    # Column tooltips:
    source_auto_tooltip    = Bool( True )
    file_path_auto_tooltip = Bool( True )


stack_frame_editor = GridEditor(
    adapter    = StackFrameAdapter,
    operations = [],
    selected   = 'object.fbi.frame'
)

#-------------------------------------------------------------------------------
#  'StackFrames' class:
#-------------------------------------------------------------------------------

class StackFrames ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Stack Frames' )

    # Reference to the FBI debugging context:
    fbi = Constant( FBI() )

    # The file position associated with the currently selected frame:
    file_position = Property( connect = 'from: file position' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'object.fbi.frames',
              id         = 'frames',
              show_label = False,
              editor     = stack_frame_editor
        ),
        id = 'facets.extra.tools.stack_frames'
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'fbi:frame' )
    def _get_file_position ( self ):
        frame = self.fbi.frame
        if frame is None:
            return None

        return FilePosition(
            name      = frame.function_name,
            file_name = join( frame.file_path, frame.file_name ),
            line      = frame.line
        )

#-- EOF ------------------------------------------------------------------------