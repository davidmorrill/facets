"""
Defines the FileWatch service for monitoring changes to files.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from time \
    import time

from glob \
    import iglob

from os.path \
    import abspath, getsize, getmtime, exists

from facets.core_api \
    import HasPrivateFacets, SingletonHasPrivateFacets, Str, Long, Any, Bool, \
           List, Callable

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  'WatchedFile' class:
#-------------------------------------------------------------------------------

class WatchedFile ( HasPrivateFacets ):
    """ Represents a specific file in the set of files being monitored by the
        FileWatch service.
    """

    #-- Public Facet Definitions -----------------------------------------------

    # The name of the file being watched:
    file_name = Str

    # Does the file exist?
    file_exists = Bool( False )

    # The last time the file was updated:
    mtime = Any

    # The last known size of the file:
    size = Long

    # List of callables to be notified when the file changes:
    handlers = List( Callable )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self ):
        """ Handles the 'file_name' facet being changed.
        """
        self.update()

    #-- Public Methods ---------------------------------------------------------

    def update ( self ):
        """ Updates the current state of the file.
        """
        file_name        = self.file_name
        self.file_exists = exists( file_name )
        if self.file_exists:
            try:
                self.mtime = getmtime( file_name )
                self.size  = getsize(  file_name )
            except:
                self.mtime = self.size = -1


    def notify ( self ):
        """ Notifies all handlers of a change to the file.
        """
        file_name = self.file_name
        for handler in self.handlers:
            handler( file_name )


    def process ( self ):
        """ Process any file changes that may have occurred.
        """
        file_name   = self.file_name
        file_exists = exists( file_name )
        if not self.file_exists:
            if not file_exists:
                return
        else:
            try:
                if (file_exists and
                    (self.mtime == getmtime( file_name )) and
                    (self.size  == getsize(  file_name ))):
                    return
            except:
                return

        self.update()
        self.notify()


    def add_handler ( self, handler ):
        """ Adds a new handler.
        """
        if handler not in self.handlers:
            self.handlers.append( handler )


    def remove_handler ( self, handler ):
        """ Removes an existing handler.
        """
        try:
            self.handlers.remove( handler )

            return (len( self.handlers ) > 0)
        except:
            return True

#-------------------------------------------------------------------------------
#  'FileWatch' class:
#-------------------------------------------------------------------------------

class FileWatch ( SingletonHasPrivateFacets ):
    """ Defines the FileWatch service for monitoring changes to files.
    """

    #-- Public Facet Definitions -----------------------------------------------

    # List of files currently being watched:
    watched_files = List

    #-- Public Methods ---------------------------------------------------------

    def watch ( self, handler, file_name, remove = False ):
        """ Adds/Removes a file watch *handler* for the file specified by
            *file_name*, which may contain wildcard characters (e.g.
            '/tmp/*.py').
        """
        for name in iglob( file_name ):
            self._watch( handler, name, remove )

        if not remove:
            do_after( 500, self._check_watch )

    #-- Private Methods --------------------------------------------------------

    def _watch ( self, handler, file_name, remove ):
        """ Adds/Removes a file watch *handler* for the file specified by
            *file_name*.
        """
        file_name = abspath( file_name )
        for wf in self.watched_files:
            if file_name == wf.file_name:
                break
        else:
            wf = None

        if remove:
            if (wf is not None) and (not wf.remove_handler( handler )):
                self.watched_files.remove( wf )
        else:
            if wf is None:
                wf = WatchedFile( file_name = file_name )
                self.watched_files.append( wf )

            wf.add_handler( handler )


    def _check_watch ( self ):
        """ Watches a list of WatchedFile objects for changes.
        """
        now = time()
        for wf in self.watched_files:
            wf.process()

        if len( self.watched_files ) > 0:
            delta = max( 500, int( (time() - now) * 100000 ) )
            do_after( delta, self._check_watch )

#-- Create export objects ------------------------------------------------------

file_watch = FileWatch()
watch      = file_watch.watch

#-- EOF ------------------------------------------------------------------------