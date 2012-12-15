"""
Defines the FontLibrary object used to provide information about the available
system fonts.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core.api \
    import SingletonHasPrivateFacets, List, Str

from facets.ui.toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# The set of all available fonts:
all_fonts = None

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def font_select ( font_description ):
    """ Returns a version of *font_description* where any occurrence of a font
        name list of the form: ( font_name_1, font_name_2, ..., font_name_n )
        has been replaced by: font_name, where font_name is the first font name
        from the specified list that is available (or the first font name in
        the list if none of the font names in the list are available). If the
        font description does not contain a font name list, it is returned
        unmodified.
    """
    lp = font_description.find( '(' )
    if lp >= 0:
        rp = font_description.find( ')', lp + 1 )
        if rp >= 0:
            font  = ''
            fonts = [ font.strip()
                      for font in font_description[ lp + 1: rp ].split( ',' ) ]
            if len( fonts ) > 0:
                global all_fonts

                if all_fonts is None:
                    all_fonts = set( FontLibrary().fonts )

                for font in fonts:
                    if font in all_fonts:
                        break
                else:
                    font = fonts[0]

            font_description = (font_description[ : lp ] + font +
                                font_description[ rp + 1: ])

    return font_description

#-------------------------------------------------------------------------------
#  'FontLibrary' class:
#-------------------------------------------------------------------------------

class FontLibrary ( SingletonHasPrivateFacets ):
    """ Manages lists of available system fonts.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of all available font names:
    fonts = List( Str )

    # The list of all available fixed space (i.e. monospace) fonts:
    fixed_fonts = List( Str )

    # The list of all available proportionally spaced fonts:
    proportional_fonts = List( Str )

    #-- Default Facet Values ---------------------------------------------------

    def _fonts_default ( self ):
        names = toolkit().font_names()
        names.sort()

        return names


    def _fixed_fonts_default ( self ):
        return self._fonts_matching( True )


    def _proportional_fonts_default ( self ):
        return self._fonts_matching( False )

    #-- Private Methods --------------------------------------------------------

    def _fonts_matching ( self, match_value ):
        """ Returns a list of all font names whose fixed versus proportional
            type is the same as *match_value* (a boolean).
        """
        font_cache     = self.facet_db_get( 'font_db', {} )
        cache_modified = False
        matching_fonts = []
        font_fixed     = toolkit().font_fixed
        for font in self.fonts:
            is_fixed = font_cache.get( font, None )
            if is_fixed is None:
                font_cache[ font ] = is_fixed = font_fixed( font )
                cache_modified     = True

            if is_fixed == match_value:
                matching_fonts.append( font )

        if cache_modified:
            self.facet_db_set( 'font_db', font_cache )

        matching_fonts.sort()

        return matching_fonts

#-- EOF ------------------------------------------------------------------------

