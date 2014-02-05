"""
# MultipleInstanceEditor Demo #

Demonstrates use of the **MultipleInstanceEditor**, which allows you to edit the
facets of multiple **HasFacets** objects simultaneously using a single editor
view, rather than a separate view or editor for each object.

In this example we are simulating an airport flight board showing flight origin
and destination cities, as well as the current flight status, which can be
either: *On time*, *Delayed* or *Cancelled*.

Since bad weather may affect all flights into or out of a city, it would be
useful to be able to update the flight status for multiple affected flights
simultaneously, which is where the MultipleInstanceEditor comes in.

The demo is divided into two regions, with the top using a **GridEditor** to
display all current flight information, and the bottom using a
MultipleInstanceEditor to update the flight status of all currently selected
flights.

To use the demo, select one or more flights in the top part of the demo view
(using the *Shift* or *Control* keys to aid in the selection process if
necessary). After making a selection, the field labeled *Status* at the bottom
of the view (which is part of the MultipleInstanceEditor) will display the
current flight status of the first flight selected. When you modify the value
displayed in the *Status* field, all of the selected flight's status values will
be updated at the same time.

Of course, if you really enjoy playing airport manager, you can use the column
sorting capabilities of the GridEditor to make selecting all flights into or
out of a specific city easier.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from random \
    import choice

from facets.api \
    import HasFacets, Str, Enum, List, View, VGroup, Item, GridEditor, \
           MultipleInstanceEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- Flight Class ---------------------------------------------------------------

class Flight ( HasFacets ):

    origin      = Str
    destination = Str
    status      = Enum( 'On time', 'Delayed', 'Cancelled' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( Item( 'status' ) )

#-- FlightGridAdapter Class ----------------------------------------------------

class FlightGridAdapter ( GridAdapter ):

    columns  = [ ( 'Origin',      'origin' ),
                 ( 'Destination', 'destination' ),
                 ( 'Status',      'status' ) ]
    can_edit = False

#-- Demo Class -----------------------------------------------------------------

class Demo ( HasFacets ):

    # The list of all active flights:
    flights = List

    # The list of currently selected flights:
    selected = List

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'flights',
                  editor = GridEditor( adapter        = FlightGridAdapter,
                                       selection_mode = 'rows',
                                       monitor        = 'selected',
                                       selected       = 'selected' )
            ),
            Item( 'selected', editor = MultipleInstanceEditor() ),
            show_labels = False
        ),
        title     = 'MultipleInstanceEditor Demo',
        id        = 'facets.extra.demo.ui.Advanced.MultipleInstanceEditor_demo',
        width     = 0.30,
        height    = 0.50,
        resizable = True
    )

    #-- Facet Default Values ---------------------------------------------------

    def _selected_default ( self ):
        return [ self.flights[0] ]

#-- Create The Demo ------------------------------------------------------------

cities = [ 'New York', 'Chatanooga', 'Burlington', 'Cebu City', 'Manila',
           'Hong Kong', 'Paris', 'London', 'Los Angeles', 'San Francisico',
           'Berlin', 'Moscow', 'Singapore', 'Sydney', 'Tokyo' ]

def random_flight ( ):
    destination = origin = choice( cities )
    while destination == origin:
        destination = choice( cities )

    return Flight( origin = origin, destination = destination )

#-- Create the demo ------------------------------------------------------------

demo = Demo( flights = [ random_flight() for i in xrange( 30 ) ] )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == "__main__":
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------
