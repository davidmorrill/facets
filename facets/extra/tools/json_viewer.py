"""
Defines a tool for viewing a Python JSON object potentially generated from an
input string.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Bool, View, VGroup, Item, UItem, SyncValue

from facets.extra.editors.json_editor \
    import JSONEditor

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'JSONViewer' class:
#-------------------------------------------------------------------------------

class JSONViewer ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'JSON Viewer'

    # Should JSON nodes be automatically opened?
    auto_open = Bool( True, save_state = True )

    # The string used to generate the JSON object to be viewed:
    json = Str( connect = 'to: JSON string' )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'json',
                   editor = JSONEditor(
                       auto_open = SyncValue( self, 'auto_open' )
                   )
            )
        )


    options = View(
        VGroup(
            Item( 'auto_open', label = 'Automatically open JSON nodes' ),
            group_theme = '#themes:tool_options_group'
        )
    )

#-- EOF ------------------------------------------------------------------------
