"""
Defines the DataCell class which provides a (partially) abstract implementation
of the IDataCell interface that can be used as a base class for concrete
IDataCell implementations.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Tuple, Int, Property, implements

from i_data_cell \
    import IDataCell

from i_data_grid \
    import IDataGrid

#-------------------------------------------------------------------------------
#  'DataCell' class:
#-------------------------------------------------------------------------------

class DataCell ( HasPrivateFacets ):
    """ Defines the DataCell class which provides a (partially) abstract
        implementation of the IDataCell interface that can be used as a base
        class for concrete IDataCell implementations.
    """

    implements( IDataCell )

    #-- Facet Definitions ------------------------------------------------------

    # The object implementing the IDataGrid interface associated with this cell:
    grid = Instance( IDataGrid )

    # The minimum size needed to render the cell's contents specified as a tuple
    # of the form ( width, height ):
    size = Tuple( Int, Int )

    # The current bounds of the cell specified as a tuple of the form
    # ( x, y, dx, dy ):
    bounds = Tuple( Int, Int, Int, Int )

    # A graphics adapter that can be used for size calculations:
    graphics = Property

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Paints the contents of the cell into the graphics context specified
            by *g*. The area the cell should be painted into is specified by the
            current value of the 'bounds' attribute.

            This is an abstract method that must be overridden in a subclass.
        """
        raise NotImplementedError

    #-- Property Implementations -----------------------------------------------

    def _get_graphics ( self ):
        return self.grid.context.control.temp_graphics

#-- EOF ------------------------------------------------------------------------
