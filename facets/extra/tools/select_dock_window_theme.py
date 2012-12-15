"""
A tool for selecting a new default DockWindow theme from the list of available
factory defined themes.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from string \
    import capwords

from facets.api \
    import Str, Enum, Bool, Event, Constant, View, HGroup, Item, \
           ThemedButtonEditor, on_facet_set

from facets.ui.dock.dock_window_theme_factory \
    import theme_factory

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The mapping of available themes to user formatted names:
theme_names = theme_factory.themes
themes      = dict( [ ( name, capwords( name.replace( '_', ' ' ) ) )
                      for name in theme_names ] )

#-------------------------------------------------------------------------------
#  'SelectDockWindowTheme' class
#-------------------------------------------------------------------------------

class SelectDockWindowTheme ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Select DockWindow Theme' )

    # The current theme:
    theme = Enum( themes )

    # Display the next/previous available theme:
    next_theme     = Event
    previous_theme = Event

    # Should the Next/Previous theme buttons be displayed?
    show_next_previous = Bool( True )

    # The DockWindowThemeFactory factory:
    factory = Constant( theme_factory )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HGroup(
            Item( 'theme',
                  springy = True
            ),
            Item( 'previous_theme',
                  show_label   = False,
                  visible_when = 'show_next_previous',
                  tooltip      = 'Select previous theme',
                  editor = ThemedButtonEditor(
                      theme = None,
                      image = '@icons2:ArrowLargeLeft' )
            ),
            Item( 'next_theme',
                  show_label   = False,
                  visible_when = 'show_next_previous',
                  tooltip      = 'Select next theme',
                  editor = ThemedButtonEditor(
                      theme = None,
                      image = '@icons2:ArrowLargeRight' )
            )
        )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _theme_default ( self ):
        theme = self.factory.name
        if theme == '':
            return 'default'

        return theme

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:name' )
    def _name_modified ( self ):
        """ Handles the theme factory default theme name being changed.
        """
        self.theme = self.factory.name


    def _theme_set ( self ):
        """ Handles the 'theme' facet being changed.
        """
        theme_factory.name = self.theme


    def _next_theme_set ( self ):
        """ Handles the 'next_theme' event being fired.
        """
        index = theme_names.index( self.theme ) + 1
        if index >= len( themes ):
            index = 0

        self.theme = theme_names[ index ]


    def _previous_theme_set ( self ):
        """ Handles the 'previous_theme' event being fired.
        """
        index = theme_names.index( self.theme ) - 1
        if index < 0:
            index = len( theme_names ) - 1

        self.theme = theme_names[ index ]

#-- EOF ------------------------------------------------------------------------
