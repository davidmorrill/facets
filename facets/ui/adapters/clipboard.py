"""
Defines a Clipboard base class that each GUI toolkit backend must provide a
concrete implementation of.

The Clipboard class adapts a GUI toolkit clipboard to provide a set of toolkit
neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Property

#-------------------------------------------------------------------------------
#  'Clipboard' class:
#-------------------------------------------------------------------------------

class Clipboard ( HasPrivateFacets ):
    """ Defines a Clipboard base class that each GUI toolkit backend must
        provide a concrete implementation of.

        The Clipboard class adapts a GUI toolkit clipboard to provide a set of
        toolkit neutral properties and methods.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current contents of the clipboard rendered as a text string:
    text = Property

    # The current contents of the clipboard rendered as an ImageReource object:
    image = Property

    # The current contents of the clipboard rendered as a Python object:
    object = Property

    #-- Abstract Property Implementations --------------------------------------

    def _get_text ( self ):
        raise NotImplementedError

    def _set_text ( self, text ):
        raise NotImplementedError


    def _get_image ( self ):
        raise NotImplementedError

    def _set_image ( self, text ):
        raise NotImplementedError


    def _get_object ( self ):
        raise NotImplementedError

    def _set_object ( self, text ):
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------