"""
Defines an Layout base class that each GUI toolkit backend must provide a
concrete implementation of.

The Layout class adapts a GUI toolkit layout manager to provide a set of toolkit
neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Any, Bool, Property

from facets.ui.i_abstract_layout \
    import IAbstractLayout

from abstract_adapter \
    import AbstractAdapter

#-------------------------------------------------------------------------------
#  'Layout' class:
#-------------------------------------------------------------------------------

class Layout ( AbstractAdapter ):
    """ Abstract adapter base class that allows a GUI toolkit specific layout
        manager to provide a set of toolkit neutral properties and methods.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The GUI toolkit specific layout manager being adapted:
    layout = Any

    # The items contained in the layout:
    children = Property

    # Is the layout oriented vertically?
    is_vertical = Bool( False )

    # The current size of the layout's contents:
    size = Property

    # The current bounds of the layout's contents:
    bounds = Property

    # The current bounds of the layout's contents (including its frame):
    frame_bounds = Property

    # Is the control maximized (True/False)?
    maximized = Bool( False )

    #-- Method Implementations -------------------------------------------------

    def __init__ ( self, layout, **facets ):
        """ Initializes the object by saving the layout manager being adapted.
        """
        super( Layout, self ).__init__( **facets )

        if (isinstance( layout, HasFacets ) and
            layout.has_facets_interface( IAbstractLayout )):
            ui_layout = layout.layout
            if ui_layout is None:
                layout.layout = ui_layout = self.create_generic_layout( layout )

            self.layout = ui_layout
        else:
            self.layout = layout

        self.layout.adapter = self


    def __call__ ( self ):
        """ Returns the layout manager being adapted.
        """
        return self.layout


    def dispose ( self ):
        """ Disposes of the layout.
        """
        del self.layout

    #-- Abstract Methods -------------------------------------------------------

    def do_layout ( self ):
        """ Lays out the controls belonging to the layout manager.
        """
        raise NotImplementedError


    def clear ( self ):
        """ Clears the contents of the layout.
        """
        raise NotImplementedError


    def add ( self, item, left = 0, right = 0, top = 0, bottom = 0,
        stretch = 0, fill = True, align = '' ):
        """ Adds a specified item to the layout manager with margins determined
            by the specified values for **left**, **right**, **top** and
            **bottom**.

            If **stretch** is 0, the item only receives as much space in the
            layout direction as it requires. If > 0, it receives an amount of
            space proportional to **stretch** when compared to the other items
            having a non-zero **stretch** value.

            If **fill** is False, the item only is the width or height it
            requests. If True, the item is expanded to fill the full width or
            height assigned to the layout manager.

            If **align** is one of the values: 'top', 'bottom', 'left',
            'right', 'hcenter' or 'vcenter', the item will be aligned
            accordingly; otherwise no special alignment is made. Note that a
            list of such values can also be specified.
        """
        raise NotImplementedError


    def add_separator ( self ):
        """ Adds a separator to the layout.
        """
        raise NotImplementedError


    def remove ( self, item ):
        """ Removes the specified adapted item from the layout manager.
        """
        raise NotImplementedError


    def set_stretchable_column ( self, column ):
        """ Marks the 'column'th column of a grid layout as 'stretchable'.
        """
        raise NotImplementedError


    def set_stretchable_row ( self, row ):
        """ Marks the 'row'th row of a grid layout as 'stretchable'.
        """
        raise NotImplementedError


    def create_generic_layout ( self, layout ):
        """ Returns a generic GUI toolkit specific layout manager that will
            delegate all of its toolkit specific layout methods to the
            corresponding methods in the IAbstractLayout interface implemented
            by the specified **layout** object.
        """
        raise NotImplementedError


    def destroy ( self ):
        """ Destroys the contents of the layout.
        """
        for child in self.children:
            child.destroy()

    #-- Property Implementations -----------------------------------------------

    def _get_children ( self ):
        raise NotImplementedError


    def _get_size ( self ):
        raise NotImplementedError

    def _set_size ( self, dx_dy ):
        raise NotImplementedError


    def _get_bounds ( self ):
        raise NotImplementedError


    def _get_frame_bounds ( self ):
        return self.bounds

#-- EOF ------------------------------------------------------------------------