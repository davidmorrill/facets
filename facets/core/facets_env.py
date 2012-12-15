"""
Defines the singleton FacetsEnv class that provides access to the FACETS_XXX
environment variables in a consistent manner.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import environ

from facets.core.has_facets \
    import SingletonHasFacets

from facets.core.facet_types \
    import Any, Bool, Int, Str

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def as_bool ( value ):
    """ Returns a string argument converted to a boolean value.
    """
    try:
        return bool( int( value ) )
    except:
        value = value.lower()
        if value in ( 'true', 'yes' ):
            return True

        if value in ( 'false', 'no' ):
            return False

        raise

#-------------------------------------------------------------------------------
#  'FacetsEnv' class:
#-------------------------------------------------------------------------------

class FacetsEnv ( SingletonHasFacets ):
    """ Defines the FacetsEnv singleton class that provides access to the
        FACETS_XXX environment variables in a consistent manner.
    """

    #-- Facets Definitions -----------------------------------------------------

    # The saved FBI breakpoints file name:
    bp = Any

    # The configuration files directory:
    config = Any

    # Are developer features enabled?
    dev = Bool( initial = False, kind = as_bool )

    # The debug information level:
    debug = Int( initial = 0, kind = int )

    # The FBI debugger start-up mode:
    fbi = Int( initial = 0, kind = int )

    # Addition directories to add to the ImageLibrary search path:
    images = Any

    # The user interface initialization mode:
    init = Str( initial = 'app' )

    # The DockWindow default theme to use:
    theme = Any

    # The back-end GUI toolkit to use:
    ui = Str( initial = '' )

    # Should each DockWindow's right-click context menu be enabled?
    menu = Bool( initial = True, kind = as_bool )

    #-- Facet Default Values ---------------------------------------------------

    def _bp_default     ( self ): return self._env_var_for( 'bp'     )
    def _config_default ( self ): return self._env_var_for( 'config' )
    def _dev_default    ( self ): return self._env_var_for( 'dev'    )
    def _debug_default  ( self ): return self._env_var_for( 'debug'  )
    def _fbi_default    ( self ): return self._env_var_for( 'fbi'    )
    def _image_default  ( self ): return self._env_var_for( 'images' )
    def _init_default   ( self ): return self._env_var_for( 'init'   )
    def _theme_default  ( self ): return self._env_var_for( 'theme'  )
    def _ui_default     ( self ): return self._env_var_for( 'ui'     )
    def _menu_default   ( self ): return self._env_var_for( 'menu'   )

    #-- Private Methods --------------------------------------------------------

    def _env_var_for ( self, name ):
        facet = self.facet( name )
        value = environ.get( 'FACETS_' + name.upper(), None )
        if value is None:
            return facet.initial

        kind = facet.kind
        if kind is not None:
            try:
                value = kind( value )
            except:
                value = facet.initial

        return value

#-- Create the instance for easier usage ---------------------------------------

facets_env = FacetsEnv()

#-- EOF ------------------------------------------------------------------------