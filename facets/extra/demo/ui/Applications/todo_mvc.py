"""
Demonstrates a version of the commonly implemented Javascript To Do list
MVC-based application using Facets' ListViewEditor.

While not identical in every aspect to the typically web-based implementations,
this version does provide the following features:

  - Check an item to mark it as completed.
  - Completed items automatically move down the list, leaving uncompleted items
    at the top of the list.
  - New items are created by clicking the "dot" at the left side of any item.
    The new item is a duplicate of the original item clicked.
  - Items are deleted using a "long press click" on the dot of any item.
    Alternatively, you can also alt-click an item to delete it immediately.
  - Items can be manually re-ordered by dragging an item's dot up or down in the
    list.
"""

#-- Imports --------------------------------------------------------------------

from facets.api import HasFacets, Bool, Str, View, HGroup, UItem, ListViewEditor

#-- ToDo class -----------------------------------------------------------------

class ToDo ( HasFacets ):
    """ Represents a single to do list task.
    """
    # Has the item been completed?
    done = Bool( False )

    # The task to be performed:
    task = Str( 'What needs to be done?' )

    # The view of the task:
    view = View(
        HGroup(
            UItem( 'done' ),
            UItem( 'task', springy = True )
        )
    )

#-- ToDoList class -------------------------------------------------------------

class ToDoList ( HasFacets ):
    """ Represents the collection of tasks in the to do list.
    """

    # The list of to do tasks:
    todos = List

    # The view of all to do tasks:
    view = View(
        UItem( 'todos', editor = ListViewEditor( factory = ToDo ) ),
        title  = 'To Do',
        id     = 'facets.extra.demo.ui.Applications.todo_mvc',
        width  = 0.2,
        height = 0.5
    )

    def _todos_default ( self ):
        """ Returns the default value for the to do list.
        """
        return [ ToDo() ]

    @on_facet_set( 'todos:done' )
    def _done_modified ( self ):
        """ Handles any to do list task being completed/uncompleted by resorting
            all tasks so that completed items appear last.
        """
        self.todos = sorted( self.todos, key = lambda todo: todo.done )

#-- Create the demo ------------------------------------------------------------

demo = ToDoList

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------