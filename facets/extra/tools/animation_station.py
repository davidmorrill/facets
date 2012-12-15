"""
A tool for interactively animating object facets.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import log10

from facets.api \
    import HasFacets, HasPrivateFacets, Any, Bool, Str, Range, Instance, Enum, \
           Int, Float, Theme, Event, Control, List, BaseRange, View, HGroup,   \
           UItem, NotebookEditor, ToolbarEditor, ThemedCheckboxEditor, spring

from facets.animation.api \
    import FacetAnimation, NoEasing, EaseIn, EaseOut, EaseOutEaseIn

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from tweener objects to tweener descriptions (for EnumEditor):
TweenerMapping = {
    'No easing':         NoEasing,
    'Ease in':           EaseIn,
    'Ease out':          EaseOut,
    'Ease out, ease in': EaseOutEaseIn
}

#-------------------------------------------------------------------------------
#  'AnimationItem' class:
#-------------------------------------------------------------------------------

class AnimationItem ( HasPrivateFacets ):
    """ Represents a single animatable facet for an object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The owner of this object:
    owner = Any # Instance( AnimationObject )

    # The FacetAnimation object used to create the animation:
    animation = Instance( FacetAnimation )

    # Is the animation currently running?
    running = Bool( False )

    # The group this item is part of:
    group = Range( 0, 9 )

    # The original facet value:
    original = Any

    # The name of the tweener to use:
    tweener = Enum( 'No easing', 'Ease in', 'Ease out', 'Ease out, ease in' )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        low, high, increment = self._range()

        return View(
            HGroup(
                UItem( 'object.animation.name',
                       style = 'readonly',
                       width = -80
                ),
                '_',
                UItem( 'running',
                       editor = ThemedCheckboxEditor(
                           image       = '@icons2:GearExecute',
                           off_image   = '@facets:minimize',
                           on_tooltip  = 'Click to stop animation',
                           off_tooltip = 'Click to start animation' )
                ),
                Scrubber( 'group', 'Animation group', 1, 0.0, 0.0, 20 ),
                '_',
                Scrubber( 'object.animation.time',  'Cycle time',  0.1 ),
                Scrubber( 'object.animation.begin', 'Begin value',
                          increment, low, high ),
                Scrubber( 'object.animation.end',   'End value',
                          increment, low, high ),
                UItem( 'object.animation.reverse',
                       editor = ThemedCheckboxEditor(
                           image       = '@icons2:Refresh?H99L6s26',
                           off_image   = '@icons2:Redo_1?H99L6s26',
                           on_tooltip  = 'Click to restart animation each '
                                         'cycle',
                           off_tooltip = 'Click to reverse animation each '
                                         'cycle' )
                ),
                '_',
                Scrubber( 'tweener', 'Tweener to use', 1, 0.0, 0.0, 105 ),
                spring,
                group_theme = Theme( '@xform:b?L40', content = 0 )
            )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _running_set ( self ):
        """ Handles the 'running' facet being changed.
        """
        animation = self.animation
        if self.running:
            animation.run()
        else:
            animation.halt()
            setattr( animation.object, animation.name, self.original )

        if self.group != 0:
            self.owner.item = self


    def _tweener_set ( self, tweener ):
        """ Handles the 'tweener' facet being changed.
        """
        self.animation.tweener = TweenerMapping[ tweener ]

    #-- Private Methods --------------------------------------------------------

    def _range ( self ):
        """ Returns the low, high and increment values to use for the 'begin'
            and 'end' values.
        """
        animation = self.animation
        handler   = animation.object.facet( animation.name ).handler
        value     = getattr( animation.object, animation.name )
        low       = high = 0.0
        increment = 1.0
        if isinstance( handler, BaseRange ):
            low, high = handler.range()
            low       = low  or 0.0
            high      = high or 0.0
            max_value = max( abs( low ), abs( high ) )
            if max_value > 0.0:
                increment = 10.0 ** (int( log10( max_value ) ) - 2)

        if isinstance( value, int ):
            increment = max( int( increment ), 1 )

        return ( low, high, increment )

#-------------------------------------------------------------------------------
#  'AnimationObject' class:
#-------------------------------------------------------------------------------

class AnimationObject ( HasPrivateFacets ):
    """ Represents a HasFacets object with animatble facets.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The HasFacets object whose facets are being animated:
    object = Instance( HasFacets )

    # The name of the object:
    name = Str

    # The list of animatable facet items:
    items = List

    # The item requesting an animation status change:
    item = Event # ( AnimationItem )

    #-- Facet Default Values ---------------------------------------------------

    view = View(
        UItem( 'items', editor = ToolbarEditor() )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _name_default ( self ):
        return self.object.__class__.__name__


    def _items_default ( self ):
        items  = []
        object = self.object
        for name, facet in object.facets().iteritems():
            if isinstance( facet.handler, ( Int, Float, Range ) ):
                items.append( AnimationItem(
                    owner     = self,
                    animation = object.animate_facet(
                        name, repeat = 0, start = False ),
                    original  = getattr( object, name )
                ) )

        items.sort( key = lambda x: x.animation.name )

        return items

    #-- Facet Event Handlers ---------------------------------------------------

    def _item_set ( self, item ):
        """ Handles the 'item' event being fired.
        """
        group   = item.group
        running = item.running
        for an_item in self.items:
            if an_item.group == group:
                an_item.running = running

#-------------------------------------------------------------------------------
#  'AnimationStation' class:
#-------------------------------------------------------------------------------

class AnimationStation ( Tool ):
    """ Allows a user to interactively animate object facets.
    """

    #-- Facet Definitions ----------------------------------------------------------

    # The name of the tool:
    name = Str( 'Animation Station' )

    # The most recently connected control:
    control = Instance( Control, connect = 'to: control' )

    # The most recently connected object to animate:
    object = Instance( HasFacets, connect = 'both: object to animate' )

    # The current list of AnimationObject's:
    objects = List # ( AnimationObject )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'objects',
               editor = NotebookEditor(
                   deletable  = True,
                   page_name  = '.name',
                   export     = 'DockWindowShell',
                   dock_style = 'auto'
               )
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the 'control' facet being changed.
        """
        if control is not None:
            editor = control.editor
            if (editor is not None) and isinstance( editor.object, HasFacets ):
                self.object = editor.object


    def _object_set ( self, value ):
        """ Handles the 'object' facet being changed.
        """
        self.objects.append( AnimationObject( object = value ) )

#-- EOF ------------------------------------------------------------------------
