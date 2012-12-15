"""
Defines the WatchedFileName class used for monitoring a specified file for
changes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, File

from facets.extra.services.file_watch \
    import file_watch

from facets.core.facet_base \
    import read_file

#-------------------------------------------------------------------------------
#  'WatchedFileName' interface:
#-------------------------------------------------------------------------------

class WatchedFileName ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The file_name being watched:
    watched_file_name = File

    #-- Facet Event Handlers ---------------------------------------------------

    def _watched_file_name_set ( self, old, new ):
        """ Handles the 'watched_file_name' facet being changed.
        """
        if old != '':
            file_watch.watch( self.watched_file_name_updated, old,
                              remove = True )

        if new != '':
            file_watch.watch( self.watched_file_name_updated, new )

        self.watched_file_name_updated( new )

    #-- Private Methods --------------------------------------------------------

    def watched_file_name_updated ( self, file_name ):
        self.watched_file_name_data( read_file( file_name ) )


    def watched_file_name_data ( self, data ):
        """ Handles new data being read from an updated file.
        """
        pass

#-- EOF ------------------------------------------------------------------------