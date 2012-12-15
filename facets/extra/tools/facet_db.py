"""
Defines the Facet database browser tool.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, UIView, List, Str, Any, Instance, Enum, Property, \
           Button, View, VGroup, HGroup, UItem, GridEditor, spring, Missing,   \
           on_facet_set

from facets.ui.grid_adapter \
    import GridAdapter

from facets.core.facet_db \
    import facet_db

from facets.extra.api \
    import file_watch, HasPayload

#-------------------------------------------------------------------------------
#  'FacetDBAdapter' class:
#-------------------------------------------------------------------------------

class FacetDBAdapter ( GridAdapter ):
    """ Adapts TDBRecord objects for use with a GridEditor.
    """

    columns       = [ ( 'Id', 'id' ) ]
    auto_filter   = True
    even_bg_color = 0xF0F0F0

#-------------------------------------------------------------------------------
#  'TDBRecord' class:
#-------------------------------------------------------------------------------

class TDBRecord ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # Id of the database entry:
    id = Str

    # The name of the database the entry is from:
    database = Str

    #-- Public Methods ---------------------------------------------------------

    def delete ( self ):
        """ Deletes the 'id' from the facet database.
        """
        facet_db.set( self.id, db = self.database )

#-------------------------------------------------------------------------------
#  'FacetDB' class:
#-------------------------------------------------------------------------------

class FacetDB ( UIView ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Facet DB' )

    # The persistence id for this object:
    id = Str( 'facets.extra.tools.facet_db.state', save_state_id = True )

    # All items currently in the database:
    all_items = List( TDBRecord )

    # The value associated with the currently selected facets ui db id:
    value = Instance( HasPayload,
                      connect   = 'from: current selected value',
                      draggable = 'Drag current selected value.' )

    # The currently selected facets ui db row:
    selected = Any

    # The 'Delete selected id' button:
    delete = Button( 'Delete' )

    # The name of the Facet database currently being viewed:
    database = Enum( 'facet_db', values = 'databases', save_state = True )

    # The list of all defined Facet databases:
    databases = Property

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        VGroup(
            VGroup(
                UItem( 'database' ),
                UItem( 'all_items',
                       id         = 'all_items',
                       editor     = GridEditor(
                           adapter    = FacetDBAdapter,
                           operations = [],
                           selected   = 'selected' )
                ),
                group_theme = '#themes:tool_options_group'
            ),
            HGroup(
                spring,
                UItem( 'delete',
                      show_label   = False,
                      enabled_when = 'selected is not None'
                ),
                group_theme = '#themes:toolbar_group'
            )
        ),
        title     = 'Facet DB',
        id        = 'facets.extra.tools.facet_db',
        width     = 0.40,
        height    = 0.50,
        resizable = True
    )

    #-- Public Methods ---------------------------------------------------------

    @on_facet_set( 'database' )
    def update_all_items ( self, file_name = None ):
        """ Determines the set of available database keys.
        """
        database = self.database
        db       = facet_db( database )
        if db is not None:
            keys = db.keys()
            db.close()
            keys.sort()
            self.all_items = [ TDBRecord( id = key, database = database )
                               for key in keys ]

    #-- Property Implementations -----------------------------------------------

    def _get_databases ( self ):
        return facet_db.names()

    #-- Facet Event Handlers ---------------------------------------------------

    def _ui_info_set ( self ):
        """ Handles the 'ui_info' facet being changed.
        """
        remove = self.ui_info is None
        self._set_listener( remove = remove )
        if not remove:
            self.update_all_items()


    def _database_set ( self, old, new ):
        """ Handles the 'database' facet being changed.
        """
        self._set_listener( old, remove = True  )
        self._set_listener( new, remove = False )


    def _selected_set ( self, record ):
        """ Handles the user selecting a database record.
        """
        if record is not None:
            # Display the contents of the selected data base record:
            id      = record.id
            payload = facet_db.get( id, Missing, db = self.database )
            if payload is not Missing:
                self.value = HasPayload( payload      = payload,
                                         payload_name = id.split( '.' )[-1],
                                         payload_full_name = id )
        else:
            self.value = None


    def _delete_set ( self ):
        """ Handles the 'delete' button being clicked.
        """
        self.all_items.remove( self.selected )
        self.selected = None


    def _all_items_items_set ( self, event ):
        """ Handles items being deleted from the 'all_items' list.
        """
        for record in event.removed:
            record.delete()

    #-- Private Methods --------------------------------------------------------

    def _set_listener ( self, database = None, remove = False ):
        """ Adds/Removes a file watch for the database specified by *database*.
        """
        file_watch.watch(
            self.update_all_items, facet_db.db( database or self.database ),
            remove = remove
        )

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    FacetDB().edit_facets()

#-- EOF ------------------------------------------------------------------------