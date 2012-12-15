"""
Defines a tool for viewing the tokens for a Python source code input string.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, View, UItem

from facets.extra.editors.token_editor \
    import TokenEditor

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'TokenViewer' class:
#-------------------------------------------------------------------------------

class TokenViewer ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Token Viewer' )

    # The Python source code string used to generate the tokens to be viewed:
    code = Str( connect = 'to: Python source code' )

    #-- Facets View Definitions ------------------------------------------------

    view = View( UItem( 'code', editor = TokenEditor() ) )

#-- EOF ------------------------------------------------------------------------
