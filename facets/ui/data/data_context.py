"""
Defines the DataContext class which implements the IDataContext interface
and can be used as an abstract base class for concrete implementations of the
IDataContext interface.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Control, implements

from i_data_grid \
    import IDataGrid

from i_data_context \
    import IDataContext

#-------------------------------------------------------------------------------
#  'DataContext' class:
#-------------------------------------------------------------------------------

class DataContext ( HasPrivateFacets ):
    """ Defines the DataContext class which implements the IDataContext
        interface and can be used as an abstract base class for concrete
        implementations of the IDataContext interface.
    """

    implements( IDataContext )

    #-- Facet Definitions ------------------------------------------------------

    # The implementation of the IDataGrid interface used to defined the data to
    # to render:
    grid = Instance( IDataGrid )

    # The control the data is rendered into:
    control = Instance( Control )

    #-- Facet Event Handlers ---------------------------------------------------

    def _grid_set ( self, old, new ):
        """ Handles the 'grid' facet being changed.
        """
        if old is not None:
            old.context = None

        if new is not None:
            new.context = self

#-- EOF ------------------------------------------------------------------------
