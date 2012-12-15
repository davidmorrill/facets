"""
A feature-enabled tool for diplaying theme-based layouts as a visualization aid.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api                                                              \
    import Str, Range, Any, Bool, Color, Image, Theme, ATheme, View, VGroup, \
           HGroup, UItem, Item, HLSColorEditor, RangeEditor,                 \
           ThemedCheckboxEditor, SyncValue, on_facet_set

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.extra.editors.theme_layout_editor \
    import ThemeLayoutEditor

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The group theme used around some of the editors:
group_theme = Theme( '@xform:btd?H61L20S9', content = 5 )

#-------------------------------------------------------------------------------
#  'RItem' class:
#-------------------------------------------------------------------------------

class RItem ( Item ):
    """ Custom Item class using a RangeEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Override the default editor to be a RangeEditor:
    editor = RangeEditor( body_style = 25 )

#-------------------------------------------------------------------------------
#  'ThemeLayout' class:
#-------------------------------------------------------------------------------

class ThemeLayout ( Tool ):
    """ A feature-enabled tool for diplaying theme-based layouts as a
        visualization aid.
    """

    #-- Facet Definitions ----------------------------------------------------------

    # The name of the tool:
    name = Str( 'Theme Layout' )

    # A value to convert to a theme to edit:
    value = Any( connect = 'to: image used to define a theme' )

    # An image to use as the basis for the theme to edit:
    image = Image

    # The theme being viewed by the tool:
    theme = ATheme( '@xform:li', connect = 'to: theme being displayed' )

    # The number of rows of theme layout items to display:
    rows = Range( 1, 20, 5 )

    # The number of columns of theme layout items to display:
    columns = Range( 1, 20, 2 )

    # The amount of vertical spacing between rows of items:
    vertical_spacing = Range( 0, 30, 0 )

    # The amount of horizontal spacing between columns of items:
    horizontal_spacing = Range( 0, 30, 0 )

    # The left margin to use in the editor:
    left_margin = Range( 0, 30, 0 )

    # The right margin to use in the editor:
    right_margin = Range( 0, 30, 0 )

    # The top margin to use in the editor:
    top_margin = Range( 0, 30, 0 )

    # The bottom margin to use in the editor:
    bottom_margin = Range( 0, 30, 0 )

    # Should the content text and label text be displayed in each layout item?
    show_text = Bool( True )

    # The content text to display in each layout item:
    text = Str( 'This is some sample content text' )

    # The label text to display in each layout item:
    label = Str( 'This is a sample label' )

    # The current content text being displayed:
    theme_text = Str( 'This is some sample content text' )

    # The current label text being displayed:
    theme_label = Str( 'This is a sample label' )

    # Should an icon be displayed:
    show_icon = Bool( False )

    # The icon to display to the left of the text in each layout item:
    icon = Image

    # The background color to use:
    bg_color = Color( 0x404040 )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                HGroup(
                    VGroup(
                        RItem( 'rows',
                                tooltip = 'Number of rows to display (text '
                                          'overrides this)'
                        ),
                        RItem( 'columns',
                               tooltip = 'Number of columns to display'
                        ),
                        RItem( 'horizontal_spacing',
                               tooltip = 'Amount of horizontal space between '
                                         'items'
                        ),
                        RItem( 'vertical_spacing',
                               tooltip = 'Amount of vertical space between '
                                         'items'
                        ),
                        label       = 'Grid',
                        group_theme = group_theme
                    ),
                    VGroup(
                        RItem( 'left_margin',
                               label   = 'Left',
                               tooltip = 'Amount of margin along the left edge'
                        ),
                        RItem( 'right_margin',
                               label   = 'Right',
                               tooltip = 'Amount of margin along the right edge'
                        ),
                        RItem( 'top_margin',
                               label   = 'Top',
                               tooltip = 'Amount of margin along the top edge'
                        ),
                        RItem( 'bottom_margin',
                               label   = 'Bottom',
                               tooltip = 'Amount of margin along the bottom '
                                         'edge'
                        ),
                        label       = 'Margin',
                        group_theme = group_theme
                    )
                ),
                HGroup(
                    Item( 'text',
                          springy = True,
                          width   = 0.2,
                          tooltip = "Content text to display (type '\\n' to "
                                    "insert a carriage return)"
                    ),
                    Item( 'label',
                          springy = True,
                          width   = 0.1,
                          tooltip = 'Label text to display'
                    ),
                    UItem( 'show_text',
                           editor  = ThemedCheckboxEditor(
                               image       = '@icons2:Pencil',
                               on_tooltip  = 'Display text (click to hide)',
                               off_tooltip = 'Hide text (click to display)' )
                    ),
                    UItem( 'show_icon',
                           editor  = ThemedCheckboxEditor(
                               image       = '@icons2:Clock_2',
                               on_tooltip  = 'Display icon (click to hide)',
                               off_tooltip = 'Hide icon (click to display)' )
                    ),
                    group_theme = '@xform:b?H61L20S9'
                ),
                VGroup(
                    Item( 'bg_color',
                          label   = 'Background',
                          editor  = HLSColorEditor( edit = 'lightness' ),
                          tooltip = 'Background color'
                    ),
                    group_theme = '@xform:b?H61L20S9'
                ),
                UItem( 'theme',
                       editor = ThemeLayoutEditor(
                           rows          = SyncValue( self, 'rows' ),
                           columns       = SyncValue( self, 'columns' ),
                           left_margin   = SyncValue( self, 'left_margin' ),
                           right_margin  = SyncValue( self, 'right_margin' ),
                           top_margin    = SyncValue( self, 'top_margin' ),
                           bottom_margin = SyncValue( self, 'bottom_margin' ),
                           text          = SyncValue( self, 'theme_text' ),
                           label         = SyncValue( self, 'theme_label' ),
                           icon          = SyncValue( self, 'icon' ),
                           bg_color      = SyncValue( self, 'bg_color' ),
                           horizontal_spacing = SyncValue(
                                                   self, 'horizontal_spacing' ),
                           vertical_spacing   = SyncValue(
                                                    self, 'vertical_spacing' ) )
                )
            ),
            title  = 'Theme Layout Tool',
            width  = 0.25,
            height = 0.75
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self, value ):
        """ Handles the 'value' facet being changed.
        """
        if isinstance( value, ( list, tuple ) ) and (len( value ) > 0):
            value = value[0]

        if isinstance( value, ( basestring, AnImageResource ) ):
            self.image = value
        else:
            self.image = '@xform:b'


    def _image_set ( self, image ):
        """ Handles the 'image' facet being changed.
        """
        self.theme = Theme( image )


    @on_facet_set( 'text, label, show_text' )
    def _text_modified ( self ):
        if self.show_text:
            self.theme_text  = self.text
            self.theme_label = self.label
        else:
            self.theme_text = self.theme_label = ''


    def _show_icon_set ( self, show_icon ):
        self.icon = '@icons2:Clock_2' if show_icon else None

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    ThemeLayout( value = '@xform:li' ).edit_facets()

#-- EOF ------------------------------------------------------------------------
