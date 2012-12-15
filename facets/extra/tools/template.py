"""
Defines the Template tool for generating text from templates.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
   import Str, View, UItem, TemplateEditor, SyncValue

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'Template' class:
#-------------------------------------------------------------------------------

class Template ( Tool ):
    """ Defines the Template tool for generating text from templates.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Template' )

    # The input template:
    template = Str( connect = 'to: template' )

    # The string genmerated from the template:
    result = Str( connect = 'from: result' )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'result',
                   editor = TemplateEditor(
                       template = SyncValue( self, 'template' ) )
            )
        )

#-- EOF ------------------------------------------------------------------------
