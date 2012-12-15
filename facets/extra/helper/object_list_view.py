"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, HasStrictFacets, Str, List, Constant, Any, View, \
           Item, NotebookEditor

from facets.extra.features.api \
    import CustomFeature, is_not_none

from facets.extra.features.connect_feature \
    import can_connect

from facets.ui.pyface.image_resource \
    import ImageResource

#-------------------------------------------------------------------------------
#  'ObjectListView' class:
#-------------------------------------------------------------------------------

class ObjectListView ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The class contained in the list:
    klass = Any

    # The list of all current objects:
    objects_list = List

    # The currently selected object:
    selected_object = Any

    # The name of the facet incoming/outgoing data is connected to:
    selected_facet = Str

    # Feature button for creating a new shell:
    new_object_button = CustomFeature(
        image   = ImageResource( 'new_object' ),
        click   = '_new_object',
        tooltip = 'Click to create a new view.'
    )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'objects_list',
              style      = 'custom',
              show_label = False,
              editor     = NotebookEditor( deletable  = True,
                                           selected   = 'selected_object',
                                           page_name  = '.name',
                                           export     = 'DockWindowShell',
                                           dock_style = 'tab' )
        )
    )

    #-- Object Class Methods ---------------------------------------------------

    def __init__ ( self, **facets ):
        """ Initializes the object.
        """
        super( ObjectListView, self ).__init__( **facets )

        selected_facet = None
        facets = self.facets( connect = can_connect )
        if len( facets ) == 1:
            selected_facet, facet = facets.items()[ 0 ]
            connect = facet.connect
            col     = connect.find( ':' )
            if col >= 0:
                connect = connect[ : col ].strip()
            if connect == 'both':
                connect = 'to'
        else:
            facets = self.facet_name( droppable = is_not_none )
            if len( facets ) == 1:
                selected_facet = facets[ 0 ]
                connect = 'to'
            else:
                facets = self.facet_names( draggable = is_not_none )
                if len( facets ) == 1:
                    selected_facet = facets[ 0 ]
                    connect = 'from'

        if selected_facet is not None:
            self.selected_facet = selected_facet
            self.new_object_button.enabled = ( connect == 'from' )
            if connect == 'to':
                self.on_facet_set( self._new_from_external, selected_facet )
            else:
                self.on_facet_set( self._select_from_external,
                                   selected_facet )
                self._new_object()

    #-- Overridable Methods ----------------------------------------------------

    def new_object ( self, **facets ):
        """ Returns a new object to be viewed (must be overridden).
        """
        return DefaultObject()

    #-- Feature Event Handlers -------------------------------------------------

    def _new_object ( self, **facets ):
        """ Creates a new view object.
        """
        object = self.new_object( **facets )
        self.objects_list.append( object )
        self.selected_object = object


    def _new_from_external ( self, data ):
        facet = self.selected_facet
        for object in self.objects_list:
            if data == getattr( object, facet ):
                self.selected_object = object
                break
        else:
            self._new_object( **{ self.selected_facet: data } )

    #-- Event Handlers ---------------------------------------------------------

    def _selected_object_default ( self ):
        """ Returns the default value for the 'selected_object' facet.
        """
        if len( self.objects_list ) > 0:
            return self.objects_list[ 0 ]

        return None


    def _selected_object_set ( self, selected ):
        """ Handles the 'selected_object' facet being changed.
        """
        if ( selected is not None ) and ( self.selected_facet != '' ):
            setattr( self, self.selected_facet,
                     getattr( selected, self.selected_facet ) )


    def _select_from_external ( self, data ):
        """ Connects externally supplied data to the current selected object.
        """
        if self.selected is not None:
            setattr( self.selected, self.selection_facet, data )
        else:
            self._new_from_external( data )

#-------------------------------------------------------------------------------
#  'DefaultObject' class:
#-------------------------------------------------------------------------------

class DefaultObject ( HasStrictFacets ):

    #-- Facet Definitions ------------------------------------------------------

    message = Constant( "You did not override the 'new_object' method or "
                        "specify a 'klass' value." )

    #-- Facets View Definitions ------------------------------------------------

    view = View( Item( 'message', style = 'readonly', show_label = False ) )

#-- EOF ------------------------------------------------------------------------