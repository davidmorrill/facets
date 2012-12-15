"""
Defines the IDataCell interface used to calculate geometry sizes and render the
contents of a single data or label cell displayed within a DataGrid.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Interface, Tuple, Int, Instance

from i_data_grid \
    import IDataGrid

#-------------------------------------------------------------------------------
#  'IDataCell' interface:
#-------------------------------------------------------------------------------

class IDataCell ( Interface ):
    """ Defines the IDataCell interface used to calculate geometry sizes and
        render the contents of a single data or label cell displayed within an
        IDataGrid.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The object implementing the IDataGrid interface associated with this cell:
    grid = Instance( IDataGrid )

    # The minimum size needed to render the cell's contents specified as a tuple
    # of the form ( width, height ):
    size = Tuple( Int, Int )

    # The current bounds of the cell specified as a tuple of the form
    # ( x, y, dx, dy ):
    bounds = Tuple( Int, Int, Int, Int )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Paints the contents of the cell into the graphics context specified
            by *g*. The area the cell should be painted into is specified by the
            current value of the 'bounds' attribute.
        """

#-- EOF ------------------------------------------------------------------------
