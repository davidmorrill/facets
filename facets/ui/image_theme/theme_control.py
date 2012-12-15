"""
Defines the ThemeControl class which defines a control whose content is
defined by a ThemeContext object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, toolkit

from theme_context \
    import ThemeContext

#-------------------------------------------------------------------------------
#  'ThemeControl' class:
#-------------------------------------------------------------------------------

class ThemeControl ( HasPrivateFacets ):
    """ Defines the ThemeControl class which defines a control whose content is
        defined by a ThemeContext object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ThemeContext which defines the contents of the control:
    context = Instance( ThemeContext )

    #-- Public Methods ---------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the underlying GUI toolkit control.

            Must be overridden by a subclass.
        """
        self.context.control = toolkit().create_control( parent,
                                                         handle_keys = True )

#-- EOF ------------------------------------------------------------------------
