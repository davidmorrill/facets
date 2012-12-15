"""
Defines a tool to display the local variables of the currently selected FBI
debugger stack frame.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import SingletonHasPrivateFacets, Str, Any, Constant, Instance, View, \
           Item, GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.helper.fbi \
    import FBI, FBIValue

#-------------------------------------------------------------------------------
#  'FBIValueAdapter' class:
#-------------------------------------------------------------------------------

class FBIValueAdapter ( GridAdapter ):
    """ Grid adapter for mapping from FBIValue objects to a GridEditor.
    """

    columns = [
        ( 'Name',  'name' ),
        ( 'Type',  'type' ),
        ( 'Value', 'str_value' )
    ]

    type_alignment = Constant( 'center' )


fbi_value_editor = GridEditor(
    adapter    = FBIValueAdapter,
    operations = [],
    selected   = 'selected'
)

#-------------------------------------------------------------------------------
#  'LocalVariables' class:
#-------------------------------------------------------------------------------

class LocalVariables ( SingletonHasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Local Variables' )

    # Reference to the FBI debugger context:
    fbi = Constant( FBI() )

    # The currently selected local variable:
    selected = Instance( FBIValue )

    # The value of the currently selected local variable:
    value = Any( connect = 'from: selected local variable' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'object.fbi.local_variables',
              show_label = False,
              editor     = fbi_value_editor
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if selected is not None:
            self.value = selected.value

#-- EOF ------------------------------------------------------------------------