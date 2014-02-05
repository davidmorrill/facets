"""
# ListCanvasEditor Demo #

This demo is currently just a pastiche of some of the very basic capabilities
of the **ListCanvasEditor**.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, File, Constant, Int, Str, Color, \
           Property, Instance, List, Tuple, Bool, Any, Range, Enum, \
           implements, cached_property, on_facet_set, View, Item, \
           NotebookEditor, ValueEditor, GridEditor, RangeEditor, \
           HLSColorEditor, ColorPaletteEditor, ATheme, Theme

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.editors.list_canvas_editor \
    import ListCanvasAdapter, IListCanvasAware, ListCanvasEditor, \
           ListCanvasItemMonitor, ListCanvasItem, SnapInfo, GridInfo, \
           GuideInfo, Modified

#-- ListCanvasEditor Control Objects -------------------------------------------

snap_info  = SnapInfo( distance = 10 )
grid_info  = GridInfo( visible = 'always', snapping = False )
guide_info = GuideInfo()

#-- Demonstration of a 'ListCanvasAware' object --------------------------------

class CanvasItemsGridAdapter ( GridAdapter ):

    columns = [ ( 'Title', 'title' ) ]

    def _get_text ( self ):
        return self.item


class CanvasItems ( HasPrivateFacets ):

    implements( IListCanvasAware )

    #-- IListCanvasAware Implementation ------------------------------------

    # The list canvas item associated with this object:
    list_canvas_item = Instance( ListCanvasItem )

    #-- Private Facets -----------------------------------------------------

    # The titles of all list canvas items:
    titles = Property( depends_on = 'list_canvas_item:canvas:items.title' )

    # The index of the currently selected title:
    index = Int

    #-- Facet View Definitions ---------------------------------------------

    view = View(
        Item( 'titles',
              show_label = False,
              editor     = GridEditor(
                               adapter    = CanvasItemsGridAdapter,
                               selected   = 'index',
                               operations = []
                           )
        )
    )

    #-- Property Implementations -------------------------------------------

    @cached_property
    def _get_titles ( self ):
        if self.list_canvas_item is None:
            return [ ]

        return [ item.title for item in self.list_canvas_item.canvas.items ]

    #-- Facet Event Handlers -----------------------------------------------

    def _index_set ( self, index ):
        """ Handles the user selecting a title row.
        """
        self.list_canvas_item.canvas.items[ index ].activate()

#-- Another demonstration of a 'ListCanvasAware' object ------------------------

class ItemSnoop ( HasPrivateFacets ):

    #-- Private Facets -----------------------------------------------------

    # The list canvas item being snooped:
    item = Instance( ListCanvasItem )

    # The item's title:
    title = Property # ( Str )

    #-- Facet View Definitions ---------------------------------------------

    view = View(
        Item( 'item',
              show_label = False,
              editor     = ValueEditor()
        )
    )

    #-- Property Implementations -------------------------------------------

    def _get_title ( self ):
        return self.item.title

class CanvasSnoop ( HasPrivateFacets ):

    implements( IListCanvasAware )

    #-- IListCanvasAware Implementation ------------------------------------

    # The list canvas item associated with this object:
    list_canvas_item = Instance( ListCanvasItem )

    #-- Private Facets -----------------------------------------------------

    # The titles of all list canvas items:
    neighbors = List( ItemSnoop )

    #-- Facet View Definitions ---------------------------------------------

    view = View(
        Item( 'neighbors',
              show_label = False,
              style      = 'custom',
              editor     = NotebookEditor( dock_style = 'tab',
                                           export     = 'DockWindowShell',
                                           page_name  = '.title' )
        )
    )

    #-- Facet Event Handlers -----------------------------------------------

    @on_facet_set( 'list_canvas_item:moved' )
    def _update_neighbors ( self ):
        if self.list_canvas_item is None:
            self.neighbors = []
        else:
            self.neighbors = [ ItemSnoop( item = item )
                               for item in self.list_canvas_item.neighbors ]

#-- A class for encapsulating another object's facet into a ListCanvas object --

class ObjectFacet ( HasPrivateFacets ):

    # The object whose facet is being displayed:
    object = Instance( HasFacets )

    # The name of the object facet being displayed:
    name = Str

    # The value of the specified object facet:
    value = Property

    #-- Property Implementations -------------------------------------------

    def _get_value ( self ):
        return getattr( self.object, self.name )

    def _set_value ( self, value ):
        old = getattr( self.object, self.name )
        if value != old:
            setattr( self.object, self.name, value )
            self.facet_property_set( 'value', old, value )

    #-- Method Overrides ---------------------------------------------------

    def facet_view ( self, *args, **facets ):
        name = self.name
        return View(
            Item( 'value',
                  label  = name,
                  editor = self.object.facet( name ).get_editor()
            )
        )

#-- An adapter for monitoring changes to a Person object on a ListCanvas -------

class PersonMonitor ( ListCanvasItemMonitor ):

    @on_facet_set( 'item:object:name' )
    def _name_modified ( self, new ):
        self.item.title = new

    @on_facet_set( 'item:moved' )
    def _position_modified ( self ):
        position = self.item.position
        self.adapter.status = '%s moved to (%s,%s) [%s]' % (
               self.item.title, position[0], position[1],
               ', '.join( [ item.title for item in self.item.neighbors ] ) )

#-- The main demo ListCanvas adapter class -------------------------------------

Person_theme_active = ATheme( Theme( '@std:GL5TB',
                                     label   = ( 14, 14, 25, 3 ),
                                     border  = ( 6, 6, 6, 6 ),
                                     content = ( 0, 6, 6, 2 ) ) )

Person_theme_inactive = ATheme( Theme( '@std:GL5T',
                                       label   = ( 14, 14, 25, 3 ),
                                       border  = ( 6, 6, 6, 6 ),
                                       content = ( 0, 6, 6, 2 ) ) )

class TestAdapter ( ListCanvasAdapter ):

    theme_active = Theme( '@facets:stackable_t_active',
                          label   = ( 13, 13, 10, 5 ),
                          content = ( 2, 2, 2, 2 ) )

    theme_inactive = Theme( '@facets:stackable_t_inactive',
                            label   = ( 13, 13, 10, 5 ),
                            content = ( 2, 2, 2, 2 ) )

    theme_hover = Theme( '@facets:stackable_t_hover',
                         label   = ( 13, 13, 10, 5 ),
                         content = ( 2, 2, 2, 2 ) )

    Person_theme_active        = Person_theme_active
    Person_theme_inactive      = Person_theme_inactive
    Person_theme_hover         = Person_theme_inactive
    ObjectFacet_theme_active   = ATheme( Theme( '@std:J08', content = 3 ) )
    ObjectFacet_theme_inactive = ATheme( Theme( '@std:J07', content = 3 ) )
    ObjectFacet_theme_hover    = ATheme( Theme( '@std:J0A', content = 3 ) )

    CanvasItems_size    = Tuple( ( 180, 250 ) )
    CanvasSnoop_size    = Tuple( ( 250, 250 ) )

    Person_tooltip      = Property
    Person_can_move     = Constant( 'y' )
    Person_can_resize   = Constant( 'x' )
    Person_can_drag     = Bool( True )
    Person_can_clone    = Bool( True )
    Person_can_delete   = Bool( True )
    # fixme: Why can't we use 'Constant' for this?...
    Person_monitor      = Any( PersonMonitor )
    Person_can_close    = Any( Modified )
    Person_title        = Property
    ListCanvas_can_receive_Person   = Bool( True )
    ListCanvas_can_receive_NoneType = Bool( True )
    AFile_size          = Tuple( 450, 200 )
    File_view           = Any( View( Item( 'path' ) ) )
    AnHLSColor_title    = Str( 'HLS Color Picker' )
    APaletteColor_title = Str( 'Palette Color Picker' )
    #debug               = True

    def _get_Person_title ( self ):
        return ( self.item.name or '<undefined>' )

    def _get_Person_tooltip ( self ):
        return ( 'A person named %s' % self.item.name )

#-- Some demo classes used to populate the canvas ------------------------------

class Person ( HasFacets ):
    name   = Str
    age    = Range( 0, 100 )
    gender = Enum( 'Male', 'Female' )

    view = View(
        Item( 'name' ),
        Item( 'age', editor = RangeEditor() ),
        Item( 'gender' )
    )

nick = Person( name = 'Nick Adams', age = 37, gender = 'Male' )

class AFile ( HasFacets ):
    file = File

    view = View(
        Item( 'file', style = 'custom', show_label = False )
    )

class AnHLSColor ( HasFacets ):
    color = Color( 0xFF8000 )

    view = View(
        Item( 'color',
              show_label = False,
              editor     = HLSColorEditor( edit = 'all', cell_size = 30,
                                           space = 0, alpha = True )
        )
    )

class APaletteColor ( HasFacets ):
    color = Color( 0xFF8000 )

    view = View(
        Item( 'color',
              show_label = False,
              editor     = ColorPaletteEditor( cell_size = 25, alpha = True )
        )
    )

class ListCanvasEditorDemo ( HasFacets ):

    items = List

    view = View(
        Item( 'items',
              show_label = False,
              editor     = ListCanvasEditor(
                  scrollable = True,
                  adapter    = TestAdapter(),
                  operations = [ 'add', 'clear', 'load', 'save', 'status' ],
                  add        = [ Person, AFile, AnHLSColor, APaletteColor ],
                  snap_info  = snap_info,
                  grid_info  = grid_info,
                  guide_info = guide_info
              )
        ),
        title     = 'List Canvas Test',
        #id        = 'facets.extra.demo.ui.Advanced.ListCanvasEditor_demo',
        width     = 0.75,
        height    = 0.75,
        resizable = True
    )

    def _items_default ( self ):
        return  [
            nick,
            Person( name   = 'Joan Thomas',
                    age    = 42,
                    gender = 'Female' ),
            Person( name   = 'John Jones',
                    age    = 27,
                    gender = 'Male' ),
            Person( name   = 'Tina Gerlitz',
                    age    = 51,
                    gender = 'Female' ),
            AFile(),
            AnHLSColor(),
            APaletteColor(),
            ObjectFacet( object = nick, name = 'name'   ),
            ObjectFacet( object = nick, name = 'age'    ),
            ObjectFacet( object = nick, name = 'gender' ),
            snap_info,
            grid_info,
            guide_info,
            CanvasItems(),
            CanvasSnoop()
        ]

#-- Create the demo ------------------------------------------------------------

demo = ListCanvasEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------