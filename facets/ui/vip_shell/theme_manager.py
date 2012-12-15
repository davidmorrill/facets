"""
Defines the singleton ThemeManager class used to manage the ShellItem themes
for the VIP Shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import SingletonHasPrivateFacets, ATheme

from themes \
    import themes

#-------------------------------------------------------------------------------
#  'ThemeManager' class:
#-------------------------------------------------------------------------------

class ThemeManager ( SingletonHasPrivateFacets ):
    """ Defines the singleton ThemeManager class used to manage the ShellItem
        themes for the VIP Shell.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Used to convert theme names to Theme objects:
    theme = ATheme

    #-- Public Methods ---------------------------------------------------------

    def theme_for ( self, item ):
        """ Returns the Theme to use for the specified ShellItem subclass *item*
            in its current state.
        """
        full_name = '_%s_%s_for_%d' % (
                        item.theme_state,
                        self._class_name_for( item.__class__ ),
                        item.lod )
        if item.selected:
            full_name += '_selected'

        theme = getattr( self, full_name )
        if theme is None:
            self.theme = self._theme_for( item )
            theme      = self.theme
            setattr( self, full_name, theme )

        return theme

    #-- Private Methods --------------------------------------------------------

    def _class_name_for ( self, klass ):
        """ Returns the class name to use for a specified class.
        """
        name = klass.__name__
        if name[-4:] == 'Item':
            name = name[:-4]

        return name.lower()


    def _theme_for ( self, item ):
        """ Returns the theme to use for a specified ShellItem *item* using the
            information contained in the global 'themes' dictionary.
        """
        suffix = ''
        if item.selected:
            suffix = '_selected'

        if item.lod == 0:
            theme = self._find_theme_for(
                item, '%s_%%s_for_0%s' % ( item.theme_state, suffix )
            )
            if theme is not None:
                return theme

        return self._find_theme_for(
            item, '%s_%%s%s' % ( item.theme_state, suffix )
        )


    def _find_theme_for ( self, item, pattern ):
        """ Use the specified ShellItem *item*'s 'mro' chain to attempt to
            locate a key in the global 'theme' dictionary that matches the
            specified *pattern*.
        """
        global themes

        for klass in item.__class__.__mro__:
            class_name = self._class_name_for( klass )
            theme      = themes.get( pattern % class_name )
            if theme is not None:
                return theme

            if class_name == 'shell':
                break

        return None


# Create the singleton instance of the theme manager:
theme_manager = ThemeManager()

#-- EOF ------------------------------------------------------------------------
