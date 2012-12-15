"""
Defines a DockWindowThemeFactory class that returns predefined standard
DockWindow themes.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import dock_window_theme

from os \
    import stat, listdir

from os.path \
    import join, dirname, isfile, splitext

from stat \
    import ST_MTIME

from facets.api \
    import SingletonHasFacets, Any, Str, Instance, Property, FacetError

from facets.core.facets_env \
    import facets_env

from facets.ui.theme \
    import Theme

from dock_window_theme \
    import DockWindowTheme

from dock_window_images \
    import DockWindowImages

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# The type of each factory theme:
ADockWindowTheme = Instance( DockWindowTheme, is_theme = True )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# White color:
white = ( 255, 255, 255 )

# The path from where dynamically loaded themes are loaded:
theme_path = join( dirname( dock_window_theme.__file__ ), 'themes' )

#-------------------------------------------------------------------------------
#  'DockWindowThemeFactory' class:
#-------------------------------------------------------------------------------

class DockWindowThemeFactory ( SingletonHasFacets ):
    """ Defines a factory for producing standard DockWindow themes.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The default theme:
    theme = Property

    # The factory name of the default theme (may be the empty string):
    name = Property

    # The list of all available theme names:
    themes = Property

    #-- Private Facets ---------------------------------------------------------

    # A cache of all dynamically loaded themes:
    _theme_cache = Any( {} ) # { name: ( theme, file_time_stamp ) }

    # The default theme:
    _theme = Instance( DockWindowTheme )

    # The factory name of the current theme (may be the empty string):
    _name = Str

    #-- Property Implementations -----------------------------------------------

    def _get_theme ( self ):
        if self._theme is None:
            name  = (facets_env.theme or
                     self.facet_db_get( 'default', 'default' ))
            theme = getattr( self, name, None )
            if theme is None:
                print ("The FACETS_THEME environment variable is '%s', which "
                       "is not a defined theme.\nThe default theme will be "
                       "used instead.\n\nThe defined themes are:") % name
                for name in self.themes:
                    print ' ', name

                theme = self.default
                name  = 'default'

            self._copy_theme( theme )
            self._name = name
            self.facet_property_set( 'name', '' )

        return self._theme

    def _set_theme ( self, theme ):
        if not isinstance( theme, DockWindowTheme ):
            raise FacetError( 'The value must be a DockWindowTheme' )

        self._copy_theme( theme )
        old_name, self._name = self._name, ''
        self.facet_property_set( 'name', old_name )


    def _get_name ( self ):
        return self._name

    def _set_name ( self, name ):
        old_name = self._name
        if name != old_name:
            self._copy_theme( getattr( self, name ) )
            self._name = name
            self.facet_db_set( 'default', name )
            self.facet_property_set( 'name', old_name )


    def _get_themes ( self ):
        themes = []
        for theme in listdir( theme_path ):
            theme, ext = splitext( theme )
            if ext == '.theme':
                themes.append( theme )

        themes.sort()

        return themes

    #-- object Method Overrides ------------------------------------------------

    def __getattr__ ( self, name ):
        """ Overrides attribute lookup failure to handle unknown attributes as
            possible theme names.
        """
        global theme_environment

        if name[:1] != '_':
            file_name = join( theme_path, name + '.theme' )
            if isfile( file_name ):
                file_time_stamp = stat( file_name )[ ST_MTIME ]
                cache           = self._theme_cache
                info            = cache.get( name )
                if info is not None:
                    theme, theme_time_stamp = info
                    if theme_time_stamp >= file_time_stamp:
                        return theme

                theme_environment[ 'theme' ] = None
                execfile( file_name, theme_environment )
                theme = theme_environment.get( 'theme' )
                if isinstance( theme, DockWindowTheme ):
                    cache[ name ] = ( theme, file_time_stamp )

                    return theme

        raise AttributeError(
            "'%s' object has no attribute '%s'" %
            ( self.__class__.__name__, name )
        )

    #-- Private Methods --------------------------------------------------------

    def _copy_theme ( self, theme ):
        """ Copies the specified DockWindowTheme *theme* into the global default
            theme and signals that the theme has been changed.
        """
        if self._theme is None:
            self._theme = DockWindowTheme()

        self._theme.copy_theme( theme )

#-------------------------------------------------------------------------------
#  'GradientTheme' base class:
#-------------------------------------------------------------------------------

class GradientTheme ( DockWindowTheme ):
    """ Base class for creating 'gradient' style themes.
    """

    #-- Facet Definitions ------------------------------------------------------

    use_theme_color     = False
    splitter_open_close = False
    tabs_at_top         = True
    tabs_are_full_width = True
    tab_spacing         = 1
    tab_background      = None,
    tab                 = Theme( '@facets:tab_transparent?a40|L90',
                                 label = ( -1, 0 ) )
    vertical_splitter   = Theme( '@facets:vertical_splitter2' )
    horizontal_splitter = Theme( '@facets:horizontal_splitter2' )
    vertical_drag       = Theme( '@facets:vertical_drag2'  )
    horizontal_drag     = Theme( '@facets:horizontal_drag2' )


def gradient_theme ( style, active, inactive, hover, close_tab, *make_white ):
    """ Helper function for creating instances of a 'gradient' style theme.
    """
    theme = GradientTheme(
        tab_active = Theme(
            '@facets:tab_gradient%s?%s' % ( style, active ),
            label   = ( 0, 0, 0, 2 ),
            content = ( 2, 0 )
        ),
        tab_inactive = Theme(
            '@facets:tab_gradient%s?%s' % ( style, inactive ),
            label   = ( 0, 0, 0, 2 ),
            content = ( 2, 0 )
        ),
        tab_hover = Theme(
            '@facets:tab_gradient%s?%s' % ( style, hover ),
            label   = ( 0, 0, 0, 2 ),
            content = ( 2, 0 )
        ),
        images = DockWindowImages(
            close_tab = '@facets:close_tab?' + close_tab
        )
    )

    for name in make_white:
        getattr( theme, 'tab_' + name ).content_color = white

    return theme

#-------------------------------------------------------------------------------
#  'SquareTheme' base class:
#-------------------------------------------------------------------------------

class SquareTheme ( DockWindowTheme ):
    """ Base class for creating 'square' style themes.
    """

    #-- Facet Definitions ------------------------------------------------------

    use_theme_color     = False
    splitter_open_close = False
    tabs_at_top         = True
    tabs_are_full_width = True
    tab_spacing         = 0
    tab_background      = None,
    tab                 = Theme( '@facets:tab_transparent2?a55|L90',
                                 label = ( -1, 0 ) )
    vertical_splitter   = Theme( '@facets:vertical_splitter2' )
    horizontal_splitter = Theme( '@facets:horizontal_splitter2' )
    vertical_drag       = Theme( '@facets:vertical_drag2' )
    horizontal_drag     = Theme( '@facets:horizontal_drag2' )


def square_theme ( active, inactive, hover, close_tab, *make_white ):
    """ Helper function for creating instances of a 'square' style theme.
    """
    theme = SquareTheme(
        tab_active = Theme(
            '@facets:tab_bevel?' + active,
            label   = ( 0, 0, -1, 1 ),
            content = ( 5, 0 )
        ),
        tab_inactive = Theme(
            '@facets:tab_bevel?' + inactive,
            label   = ( 0, 0, -1, 1 ),
            content = ( 5, 0 )
        ),
        tab_hover = Theme(
            '@facets:tab_bevel?' + hover,
            label   = ( 0, 0, -1, 1 ),
            content = ( 5, 0 )
        ),
        images = DockWindowImages(
            close_tab = '@facets:close_tab?' + close_tab
        )
    )

    for name in make_white:
        getattr( theme, 'tab_' + name ).content_color = white

    return theme

#-------------------------------------------------------------------------------
#  Module Initialization:
#-------------------------------------------------------------------------------

# Create the singleton theme factory:
theme_factory = DockWindowThemeFactory()

# Create the dynamic theme lookup execution environment:
theme_environment = dict( [ ( name, globals()[ name ] ) for name in (
    'DockWindowTheme', 'DockWindowImages', 'Theme', 'GradientTheme',
    'gradient_theme', 'SquareTheme', 'square_theme', 'theme_factory' )
] )

#-- EOF ------------------------------------------------------------------------
