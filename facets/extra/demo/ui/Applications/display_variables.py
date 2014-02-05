"""
# Display Variables #

A mock application that demonstrates several advanced Facets UI techniques.

The scenario is as follows...

We are conducting a simulated experiment. The experiment contains a number of
variables, each of which will have a value for each of some number of sample
points. We wish to display a table containing a column for each variable in the
experiment, and a row for each sample point.

We will use the *MVC* (Model/View/Controller) design pattern to implement
this application. The model will consist of:

- **Experiment**: Defines the experiment, the set of variables, and the
  number of sample points.

- **Variable**: Defines a single experimental variable: its name, units,
  description and the set of values for each experimental sample point.

Techniques worth studying:

- Use of MVC (The **Experiment** and **Variable** model classes contain
  no UI code).
- The main UI class (i.e. **ExperimentView**) is almost 100% declarative.
  Most of the UI logic is in the **VariableAdapter** class, which adapts
  the non-tabular model objects into a tabular format.
- Use of the *dock* facet to allow the user to reorganize the UI.
- Use of the *export* facet to allow the user to drag sub-views out of the main
  window to make optimum use of all available screen real estate.
- Use of themes to enhance UI appearance.
- Use of the **VerticalNotebookEditor** to allow easy access to the various
  **Variable** parameters.
- Definition of the **Slider** class to simplify **View** creation.
- The use of the **Controller** class to bind the model and view classes.
- The *on_facet_set* decorator preceding the *_calculate_values* method. It
  allows multiple events to trigger the same event handler.
- The *on_facet_set decorator* preceding the *_register_variables* method. It
  provides a simpler form of event handling for list events.
- The *columns* property of the **VariableAdapter** class. It allows the
  **VariableAdapter** class to dynamically adapt to the number of variables in
  the **Experiment** model.

Notes:

- This demo requires the *numpy* package.
- Try commenting out the line *multiple_open = True*, which allows more
  than one **Variable** object to be open at once.
- Try dragging the handles along the top part of each view to reorganize the
  view layout. Whatever changes you make will be persisted from one invocation
  of the program to another. The persistence is enabled through the use of the
  *id* facets in the **View** and **Group** objects. The ability to
  rearrange the views is enabled via the *dock* facet set in several of
  the **Group** objects.
- Try dragging a view completely out of the Facets UI demo program window and
  dropping it on your desktop. This feature is enabled via the *export*
  facet set in several of the **Group** objects.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from numpy \
    import arange

from facets.api \
    import HasFacets, Str, List, Instance, Expression, Array, Range, Property, \
           Any, FacetListEvent, on_facet_set, cached_property, Controller, \
           View, HSplit, HGroup, VGroup, UItem, Item, GridEditor, RangeEditor, \
           VerticalNotebookEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- Variable Class -------------------------------------------------------------

class Variable ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the variable:
    name = Str

    # The units in which the variable is measured:
    units = Str

    # A description of what the variable is:
    description = Str

    # The value of the variable at each sample point:
    values = Array

    # The experiment the variable belongs to:
    experiment = Any

    # A formula used to calculate the values (for purposes of this demo only):
    formula = Expression

    # Formula coefficients (for purposes of this demo only):
    a = Range( -2.0, 2.0, 1.0 )
    b = Range( -2.0, 2.0, 0.0 )

    #-- Event Handlers ---------------------------------------------------------

    @on_facet_set( 'formula, a, b, experiment.index_values' )
    def _calculate_values ( self ):
        try:
            self.values = eval( self.formula_, globals(),
                                { 'x': self.experiment.index_values,
                                  'a': self.a,
                                  'b': self.b } )
        except:
            # You might not be keying in a valid formula...
            pass

#-- Experiment Class -----------------------------------------------------------

class Experiment ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the experiment:
    name = Str( 'Experiment' )

    # The set of experimental variables:
    variables = List( Variable )

    # The number of sample points:
    sample_points = Range( 2, 1000, 20 )

    # The index values for each sample point:
    index_values = Array

    #-- Event Handlers ---------------------------------------------------------

    @on_facet_set( 'variables[]' )
    def _register_variables ( self, removed, added ):
        """ Registers/unregisters the experiment a variable belongs to when it
            is added to or deleted from the experiment.
        """
        for variable in removed:
            variable.experiment = None

        for variable in added:
            variable.experiment = self


    def _sample_points_set ( self, n ):
        """ Recalculates index values when the number of sample points changes.
        """
        self.index_values = arange( 0.0, 1.000001, 1.0 / (n - 1) )

#-- Grid Adapter Definition ----------------------------------------------------

class VariableAdapter ( GridAdapter ):

    columns      = Property
    font         = 'Courier 10'
    alignment    = 'right'
    format       = '%.4f'
    index_format = Str( '%d' )

    def index_text ( self ):
        return str( self.row )

    def at_text ( self ):
        return '%.3f' % self.object.index_values[ self.row ]

    #-- Adapter Method Overrides -----------------------------------------------

    def len ( self ):
        """ Returns the number of items in the specified *object.facet" list.
        """
        return self.object.sample_points

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_columns ( self ):
        variables = getattr( self.object, self.name )
        for i in range( len( variables ) ):
            self.add_facet( 'v_%d_text' % i,
                            Property( VariableAdapter._get_variable_value ) )

        return ([ ( 'i', 'index' ), ( 'at', 'at' ) ] +
                [ ( var.name, 'v_%d' % i )
                  for i, var in enumerate( variables ) ])

    #-- Private Methods --------------------------------------------------------

    def _get_variable_value ( self, name ):
        variables = getattr( self.object, self.name )

        return '%.3f' % variables[ int( name[2:-5] ) ].values[ self.row ]

#-- Variable Facets View -------------------------------------------------------

class Slider ( Item ):
    editor = RangeEditor( body_style = 25 )

variable_view = View(
    Item( 'units' ),
    Item( 'description', style = 'custom' ),
    Item( 'formula' ),
    Slider( 'a', label = 'a' ),
    Slider( 'b', label = 'b' )
)

#-- ExperimentView Controller Class --------------------------------------------

class ExperimentView ( Controller ):

    #-- Facets Views -----------------------------------------------------------

    view = View(
        HSplit(
            VGroup(
                UItem( 'variables',
                      show_label = False,
                      editor = VerticalNotebookEditor(
                          multiple_open = True,
                          scrollable    = True,
                          page_name     = '.name',
                          view          = variable_view
                      )
                ),
                group_theme = '@xform:btd?L30',
                label       = 'Variables',
                dock        = 'horizontal',
                export      = 'DockWindowShell'
            ),
            VGroup(
                UItem( 'variables',
                       editor = GridEditor( adapter    = VariableAdapter,
                                            operations = [] ),
                       id     = 'variables'
                ),
                HGroup(
                    Slider( 'sample_points', springy = True ),
                    group_theme = '@xform:b?L25'
                ),
                group_theme = '@xform:btd?L30',
                label       = 'Summary',
                dock        = 'horizontal',
                export      = 'DockWindowShell'
            ),
            id = 'splitter'
        ),
        id = 'facets.ui.demo.application.display_variables.'
             'ExperimentView',
    )

    #-- Event Handlers ---------------------------------------------------------

    @on_facet_set( 'model:variables:values, model:sample_points' )
    def _update_variables ( self ):
        """ Force an update to the experiment variables if any of the
            values get recalculated.
        """
        self.model.facet_property_set(
            'variables_items', None, FacetListEvent( self.model, 'variables' )
        )

#-- Set Up ---------------------------------------------------------------------

# Create the experiment model:
experiment = Experiment(
    name      = 'Gravitational Constant',
    variables = [
        Variable( name = 'alpha', units = 'muons',   description = 'a thingy',
                  formula = 'a*x*x-b*x' ),
        Variable( name = 'beta',  units = 'm/s',     description = 'a watzit',
                  formula = '-a*x+b' ),
        Variable( name = 'gamma', units = 'quarks/s', description = 'a ducky',
                  formula = 'a-x' )
    ],
    sample_points = 50
)

# Create the controller:
def demo ( ):
    return ExperimentView( model = experiment )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    # Note: The following code is a work-around for a current design bug in
    # the Facets 'configure_facets' method that occurs when the object is a
    # subclass of Handler (as ExperimentView is):
    class ShowDemo ( HasFacets ):
        demo = Instance( ExperimentView )

        view = View(
            Item( 'demo', style = 'custom', show_label = False ),
            title     = 'Experimental Results',
            id        = 'facets.ui.demo.application.'
                        'display_variables',
            width     = 0.5,
            height    = 0.7,
            resizable = True
        )

    ShowDemo( demo = demo() ).edit_facets()

#-- EOF ------------------------------------------------------------------------