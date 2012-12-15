"""
Defines the base editor class for creating GUI toolkit specific editors.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Editor as BaseEditor

#-------------------------------------------------------------------------------
#  'Editor' class:
#-------------------------------------------------------------------------------

class Editor ( BaseEditor ):
    """ Represents an editing control for an object facet in a Facets-based
        user interface.
    """

    #-- Class Constants --------------------------------------------------------

    # Is the editor implementation GUI toolkit neutral?
    is_toolkit_neutral = False

#-- EOF ------------------------------------------------------------------------