"""
Defines the ThemeSampler tool for viewing what a specified Theme will look like
when applied to different types of widgets.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api                                                         \
    import HasFacets, Str, Int, List, Enum, Bool, Any, Color, Property, \
           Instance, View, VGroup, Item, Theme, NullEditor, GridEditor, \
           ColorPaletteEditor

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.editors.list_canvas_editor \
    import ListCanvasEditor, ListCanvasAdapter

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The default shopping list for the ShoppingList class:
default_shopping_list = [
    'Carrots',
    'Potatoes (5 lb. bag)',
    'Cocoa Puffs',
    'Ice Cream (French Vanilla)',
    'Peanut Butter',
    'Whole wheat bread',
    'Ground beef (2 lbs.)',
    'Paper towels',
    'Soup (3 cans)',
    'Laundry detergent'
]

#-------------------------------------------------------------------------------
#  'ListGridAdapter' class:
#-------------------------------------------------------------------------------

class ListGridAdapter ( GridAdapter ):
    """ Adapts a list of strings for editing using th grid editor.
    """

    columns = [ ( 'Shopping List', 'string' ) ]
    text    = Property

    def _get_text ( self ):
        return self.item

#-------------------------------------------------------------------------------
#  'ThemeEditorAdapter' class:
#-------------------------------------------------------------------------------

class ThemeEditorAdapter ( ListCanvasAdapter ):

    #-- Facet Definitions ------------------------------------------------------

    # The tool this adapter is working on behalf of:
    tool = Any

    # Disable minimizing all items:
    can_minimize = False

    # Make sure the list canvas item reacts to all theme changes made by the
    # tool:
    mutable_theme = True

    # The themes to use for list canvas items:
    theme_active   = Property
    theme_inactive = Property
    theme_hover    = Property

    # The titles to display for the various test items:
    Person_title       = Str( 'A Test Person' )
    ColorItem_title    = Str( 'A Color Item' )
    ShoppingList_title = Str( 'A Shopping List' )
    ShoppingList_size  = Any( ( 250, 250 ) )
    ALabel_title       = Str( 'A Label' )
    title              = Str

    # Turn debugging on for the Debug instance:
    Debug_debug = Bool( True )

    def _get_theme_active ( self ):
        return self.tool.theme

    def _get_theme_inactive ( self ):
        return self.tool.theme

    def _get_theme_hover ( self ):
        return self.tool.theme

#-- Test classes for use with the ListCanvasEditor -----------------------------

#-------------------------------------------------------------------------------
#  'Person' class:
#-------------------------------------------------------------------------------

class Person ( HasFacets ):

    name   = Str
    age    = Int
    gender = Enum( 'Male', 'Female' )

    view = View(
        VGroup( 'name', 'age', 'gender' )
    )

#-------------------------------------------------------------------------------
#  'ShoppingList' class:
#-------------------------------------------------------------------------------

class ShoppingList ( HasFacets ):

    shopping_list = List( Str, default_shopping_list )

    view = View(
        Item( 'shopping_list',
              show_label = False,
              width      = 160,
              height     = 130,
              padding    = -4,
              editor     = GridEditor( adapter    = ListGridAdapter,
                                       operations = [] )
        )
    )

#-------------------------------------------------------------------------------
#  'ALabel' class:
#-------------------------------------------------------------------------------

class ALabel ( HasFacets ):

    empty = Str

    view = View(
        Item( 'empty',
              show_label = False,
              width      = -100,
              height     = -2,
              editor     = NullEditor()
        )
    )

#-------------------------------------------------------------------------------
#  'Debug' class:
#-------------------------------------------------------------------------------

class Debug ( HasFacets ):

    empty = Str

    view = View(
        Item( 'empty',
              show_label = False,
              width      = 100,
              height     = 100,
              editor     = NullEditor()
        )
    )

#-------------------------------------------------------------------------------
#  'ColorItem' class:
#-------------------------------------------------------------------------------

class ColorItem ( HasFacets ):

    color = Color( 0xFF0000 )

    view = View(
        Item( 'color',
              show_label = False,
              editor     = ColorPaletteEditor( alpha = True )
        )
    )

#-------------------------------------------------------------------------------
#  'ThemeSampler' class:
#-------------------------------------------------------------------------------

class ThemeSampler ( Tool ):
    """ Defines the ThemeSampler tool for viewing what a specified Theme will
        look like when applied to different types of widgets.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Theme Sampler' )

    # The theme the sampler is showcasing:
    theme = Instance( Theme, connect = 'to' )

    # The list of items to apply the test theme to via a ListCanvasEditor:
    items = List( [ Debug(), Person(), ShoppingList(), ColorItem(), ALabel() ] )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            Item( 'items',
                  show_label = False,
                  editor     = ListCanvasEditor(
                      theme      = Theme( '@xform:b?H61L20S9',
                                          content = ( 5, 5, 5, 5 ) ),
                      adapter    = ThemeEditorAdapter( tool = self ),
                      operations = [ 'size' ] )
            ),
            title  = 'Theme Sampler Tool',
            width  = 0.67,
            height = 0.50
        )

    #-- Facet Default Values ---------------------------------------------------

    def _theme_default ( self ):
        return Theme( '@facets:default_active' )

#-- Run the tool (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    ThemeSampler().edit_facets()

#-- EOF ------------------------------------------------------------------------
