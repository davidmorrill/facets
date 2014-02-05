"""
# Multi-thread Demo 2 #

This demo shows a simple user interface being updated by a dynamic number of
threads.

When the *Create Threads* button is pressed, the *count* method is
dispatched on a new thread. It then creates a new **Counter** object and
adds it to the *counters* list (which causes the Counter to appear
in the user interface. It then counts by incrementing the Counter
object's *count* facet (which again causes a user interface update each
time the counter is incremented). After it reaches its maximum count, it
removes the Counter from the *counter* list (causing the counter
to be removed from the user interface) and exits (terminating the thread).

Note that repeated clicking of the *Create Thread* button will create
additional threads.

Also note the use of the *'allow_tabs = False'* option in the
**NotebookEditor**. This ensures that each new thread appears as a separate,
resizable item in the notebook view, and also allows the NotebookEditor to
automatically lay out all of the items when a new thread is created. Without
this option, each new thread would simply appear as a new tab within a single
tab group in the NotebookEditor view.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from time \
    import sleep

from facets.api \
    import HasFacets, Int, Button, List, View, VGroup, Item, NotebookEditor

#-- Counter Class --------------------------------------------------------------

class Counter ( HasFacets ):
    """ Defines the objects used to keep track of the current count. """

    # The current count:
    count = Int

    view = View( Item( 'count', style = 'readonly' ) )

#-- ThreadDemo Class -----------------------------------------------------------

class ThreadDemo ( HasFacets ):
    """ Defines the main demo class. """

    # The button used to start a new thread running:
    create = Button( 'Create Thread' )

    # The set of counter objects currently running:
    counters = List( Counter )

    view = View(
        VGroup(
            Item( 'create', width = -100 ),
            '_',
            Item( 'counters', style      = 'custom',
                              editor     = NotebookEditor(
                                  dock_style = 'tab',
                                  allow_tabs = False
                              )
            ),
            show_labels = False
        ),
        resizable = True
    )

    def __init__ ( self, **facets ):
        super( HasFacets, self ).__init__( **facets )

        # Set up the notification handler for the 'Create Thread' button so
        # that it is run on a new thread:
        self.on_facet_set( self.count, 'create', dispatch = 'new' )

    def count ( self ):
        """ This method is dispatched on a new thread each time the
            'Create Thread' button is pressed.
        """
        counter = Counter()
        self.counters.append( counter )
        for i in range( 1000 ):
            counter.count += 1
            sleep( 0.030 )

        self.counters.remove( counter )

#-- Create the demo ------------------------------------------------------------

demo = ThreadDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
