"""
Defines the Control Stack tool which displays GUI toolkit specific information
about connected Control objects.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, Str, Instance, Property, List, Control, View, HSplit, \
           Item, Handler, GridEditor, property_depends_on

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.pyface.timer.api \
    import do_later

#-------------------------------------------------------------------------------
#  'ControlStackGridAdapter' class:
#-------------------------------------------------------------------------------

class ControlStackGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping from control stack tool data to the GridEditor.
    """

    columns = [
        ( 'Type', 'type'     ),
        ( 'Id',   'id'       ),
        ( 'Bounds', 'bounds' )
    ]

    #-- Column Value Methods ---------------------------------------------------

    def type_text ( self ):
        return self.item().__class__.__name__


    def id_text ( self ):
        return ('%016X' % id( self.item() ))

#-------------------------------------------------------------------------------
#  'ControlStack' class:
#-------------------------------------------------------------------------------

class ControlStack ( Handler ):
    """ Displays information about a control and all of its parents.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Control Stack' )

    # The current control whose control stack is being displayed:
    control = Instance( Control, connect = 'to: a control' )

    # The stack of control objects for the current control:
    stack = Property( List )

    # The currently selected control in the stack:
    selected = Instance( Control, connect = 'from: selected control' )

    # An image of the currently selected control:
    image = Property( connect = 'from: selected control image' ) # ( Image )

    # The children of the currently selected control:
    children = Property( List )

    # The currently selected child control:
    child = Instance( Control )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HSplit(
            Item( 'stack',
                  id         = 'stack',
                  show_label = False,
                  editor     = GridEditor(
                      adapter    = ControlStackGridAdapter,
                      operations = [],
                      selected   = 'selected' )
            ),
            Item( 'children',
                  id         = 'children',
                  show_label = False,
                  editor     = GridEditor(
                      adapter    = ControlStackGridAdapter,
                      operations = [],
                      selected   = 'child' )
            ),
            id = 'splitter'
        ),
        id        = 'facets.extra.tools.control_stack.ControlStack',
        height    = 0.5,
        width     = 0.5,
        resizable = True
    )

    #-- Handler Interface ------------------------------------------------------

    def init ( self, info ):
        self.control = info.ui.control

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'control' )
    def _get_stack ( self ):
        result  = []
        control = self.control
        if control is not None:
            while True:
                result.insert( 0, control )
                parent = control.parent
                if parent is None:
                    break

                control = parent

        return result


    @property_depends_on( 'control' )
    def _get_image ( self ):
        return (None if self.selected is None else self.selected.image)


    @property_depends_on( 'selected' )
    def _get_children ( self ):
        if self.selected is None:
            return []

        return self.selected.children

    #-- Facets Event Handlers --------------------------------------------------

    def _control_set ( self, control ):
        do_later( self.set, selected = control )


    def _selected_set ( self, selected ):
        do_later( self.set, child = None )


    def _child_set ( self, child ):
        if child is not None:
            self.control = child

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    ControlStack().edit_facets()

#-- EOF ------------------------------------------------------------------------