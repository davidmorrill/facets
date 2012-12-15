"""
Defines the Wiretap tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, Instance, Str, List, Bool, Color, \
           View, Item, GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.value_tree \
    import SingleValueTreeNodeObject, FacetsNode

from facets.extra.features.api \
    import CustomFeature

from facets.extra.helper.fbi \
    import fbi_wiretap

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'WiretapItem' class:
#-------------------------------------------------------------------------------

class WiretapItem ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The object being wiretapped:
    object = Instance( HasFacets )

    # The facet being wiretapped:
    name = Str

    # The condition (if any) for the wiretap:
    condition = Str

    # Wiretap entire object?
    entire_object = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def add ( self ):
        """ Adds the wiretap.
        """
        fbi_wiretap.wiretap( ( self.object, self.name, self.condition ), False )


    def remove ( self ):
        """ Removes the wiretap.
        """
        fbi_wiretap.wiretap( ( self.object, self.name, self.condition ), True )

    #-- Facet Event Handlers ---------------------------------------------------

    def _condition_set ( self, old, new ):
        """ Handles the 'condition' facet being changed.
        """
        fbi_wiretap.wiretap( ( self.object, self.name, old ), True )
        fbi_wiretap.wiretap( ( self.object, self.name, new ), False )


    def _entire_object_set ( self, state ):
        """ Handles the 'entire_object' facet being changed.
        """
        if state:
            fbi_wiretap.wiretap( ( self.object, self.name, self.condition ),
                                 True )
            fbi_wiretap.wiretap( ( self.object, None, self.condition ), False )
            self._name, self.name = self.name, ''
        else:
            self.name = self._name
            fbi_wiretap.wiretap( ( self.object, None, self.condition ), True )
            fbi_wiretap.wiretap( ( self.object, self.name, self.condition ),
                                 False )

#-------------------------------------------------------------------------------
#  'WiretapGridAdapter' class:
#-------------------------------------------------------------------------------

class WiretapGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping wiretap data into a GridEditor.
    """

    columns = [ ( 'Entire Object', 'entire_object' ),
                ( 'Object',        'object' ),
                ( 'Name',          'name' ),
                ( 'Condition',     'condition' ) ]

    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    object_can_edit      = Bool( False )
    name_can_edit        = Bool( False )


wiretap_grid_editor = GridEditor(
    adapter    = WiretapGridAdapter,
    operations = [ 'edit', 'delete' ]
)

#-------------------------------------------------------------------------------
#  'Wiretap' class:
#-------------------------------------------------------------------------------

class Wiretap ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Wiretap' )

    feature = CustomFeature(
        image    = '@facets:drop',
        can_drop = 'can_drop',
        drop     = 'drop',
        tooltip  = 'Drop a facet value here to wiretap it.'
    )

    # The current list of wiretap items:
    wiretaps = List( WiretapItem )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'wiretaps',
              id         = 'wiretap',
              show_label = False,
              editor     = wiretap_grid_editor
        ),
        id = 'facets.extra.tools.wiretap'
    )

    #-- CustomFeature Method Overrides -----------------------------------------

    def can_drop ( self, item ):
        """ Returns whether a specified item can be dropped on the view.
        """
        if (isinstance( item, SingleValueTreeNodeObject ) and
            isinstance( item.parent, FacetsNode )):
            name   = item.name[1:]
            object = item.parent.value
            for wiretap in self.wiretaps:
                if (object is wiretap.object) and (name == wiretap.name):
                    return False

            return True

        return False


    def drop ( self, item ):
        """ Handles a specified item being dropped on the view.
        """
        name    = item.name[1:]
        object  = item.parent.value
        wiretap = WiretapItem( object = object, name = name )
        self.wiretaps.append( wiretap )
        wiretap.add()

    #-- Facet Event Handlers ---------------------------------------------------

    def _wiretaps_items_set ( self, event ):
        """ Handles a wiretap item being deleted from the table.
        """
        for wiretap in event.removed:
            wiretap.remove()

#-- EOF ------------------------------------------------------------------------