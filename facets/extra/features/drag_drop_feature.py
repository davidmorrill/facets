"""
Adds a 'drag and drop' feature to DockWindow which exposes facets on the object
associated with a DockControl as draggable or droppable items. If the object
contains one or more facets with 'draggable' metadata, then the value of those
facets will be draggable. If the object contains one or more facets with
'droppable' metadata, then each facet that will accept a specified item will
receive that item when it is dropped on the feature.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasStrictFacets, HasFacets, List, Str

from facets.ui.dock.api \
    import DockWindowFeature

from facets.ui.ui_facets \
    import image_for

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Feature settings:
settings = (
    image_for( '@facets:drag_feature' ),
    image_for( '@facets:drop_feature' ),
    image_for( '@facets:dragdrop_feature' )
)

#-------------------------------------------------------------------------------
#  'MultiDragDrop' class:
#-------------------------------------------------------------------------------

class MultiDragDrop ( HasStrictFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # List of object being dragged:
    objects = List

#-------------------------------------------------------------------------------
#  'DragDropFeature' class:
#-------------------------------------------------------------------------------

class DragDropFeature ( DockWindowFeature ):

    #-- Class Constants --------------------------------------------------------

    # The user interface name of the feature:
    feature_name = 'Drag and Drop'

    #-- Facet Definitions ------------------------------------------------------

    # The names of the object facets to drag from:
    drag_facets = List( Str )

    # The names of the object facets that can be dropped on:
    drop_facets = List( Str )

    #-- Event Handlers ---------------------------------------------------------

    def drag ( self ):
        """ Returns the object to be dragged when the user drags feature image.
        """
        item = self.dock_control.object
        n    = len( self.drag_facets )

        if n == 1:
            return getattr( item, self.drag_facets[0], None )

        if n > 1:
            objects = []
            for facet in self.drag_facets:
                object = getattr( item, facet, None )
                if object is not None:
                    objects.append( object )

            if len( objects ) == 1:
                return objects[0]

            if len( objects ) > 1:
                return MultiDragDrop( objects = objects )

        return None


    def drop ( self, object ):
        """ Handles the user dropping a specified object on the feature image.
        """
        item        = self.dock_control.object
        drop_facets = self.drop_facets

        if isinstance( object, MultiDragDrop ):
            for drag in object.objects:
                for drop_facet in drop_facets:
                    try:
                        setattr( item, drop_facet, drag )
                    except:
                        pass
        else:
            for drop_facet in drop_facets:
                try:
                    setattr( item, drop_facet, object )
                except:
                    pass


    def can_drop ( self, object ):
        """ Returns whether a specified object can be dropped on the feature
            image.
        """
        item        = self.dock_control.object
        drop_facets = self.drop_facets

        if isinstance( object, MultiDragDrop ):
            for drag in object.objects:
                for drop_facet in drop_facets:
                    try:
                        item.base_facet( drop_facet ).validate(
                            item, drop_facet, drag
                        )

                        return True
                    except:
                        pass
        else:
            for drop_facet in drop_facets:
                try:
                    item.base_facet( drop_facet ).validate(
                        item, drop_facet, object
                    )

                    return True
                except:
                    pass

        return False

    #-- Overidable Class Methods -----------------------------------------------

    @classmethod
    def feature_for ( cls, dock_control ):
        """ Returns a feature object for use with the specified DockControl (or
            None if the feature does not apply to the DockControl object).
        """
        from facets.extra.features.api import is_not_none

        object = dock_control.object
        if isinstance( object, HasFacets ):
            drag_tooltip = drop_tooltip = ''
            drag_facets  = []
            drop_facets  = []

            facets = object.facets( draggable = is_not_none )
            if len( facets ) >= 1:
                drag_facets = facets.keys()
                drag_facets.sort()
                drag_tooltips = [ facet.draggable
                                  for facet in facets.values()
                                  if isinstance( facet.draggable, str ) ]
                if len( drag_tooltips ) > 0:
                    drag_tooltip = '\n'.join( drag_tooltips )

                if drag_tooltip == '':
                    drag_tooltip = 'Drag this item.'

                drag_tooltip += '\n'

            facets = object.facets( droppable = is_not_none )
            if len( facets ) >= 1:
                drop_facets = facets.keys()
                drop_facets.sort()
                drop_tooltips = [ facet.droppable
                                  for facet in facets.values()
                                  if isinstance( facet.droppable, str ) ]
                if len( drop_tooltips ) > 0:
                    drop_tooltip = '\n'.join( drop_tooltips )

                if drop_tooltip == '':
                    drop_tooltip = 'Drop an item here.'

            if (drag_tooltip != '') or (drop_tooltip != ''):
                i = 1
                if drag_tooltip != '':
                    i = 0
                    if drop_tooltip != '':
                        i = 2

                return cls(
                    dock_control = dock_control,
                    image        = settings[ i ],
                    tooltip      = (drag_tooltip + drop_tooltip).strip(),
                    drag_facets  = drag_facets,
                    drop_facets  = drop_facets
                )

        return None

#-- EOF ------------------------------------------------------------------------