"""
Defines the standard themes distributed as part of the Facets package.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Theme

from facets.core.facet_db \
    import facet_db

#-------------------------------------------------------------------------------
#  Define the standard themes:
#-------------------------------------------------------------------------------

# item_theme to use for a ScrubberEditor:
facet_db.set( '#themes:ScrubberEditor',
    Theme( '@xform:e4?H53L18S28', content = ( 0, 0, -2, -4 ) )
)

# group_theme to use for a tool's 'options' view:
facet_db.set( '#themes:tool_options_group',
    Theme( '@xform:b?L40' )
)

# group_theme to use for an embedded toolbar:
facet_db.set( '#themes:toolbar_group',
    Theme( '@xform:b?L10' )
)

# group_theme to use for an embedded toolbar:
facet_db.set( '#themes:toolbar',
    Theme( '@xform:b?L30' )
)

# group_theme/item_theme to use for content needing some padding (like a title):
facet_db.set( '#themes:title',
    Theme( '@xform:b?L30', content = ( 6, 4 ) )
)

#-- EOF ------------------------------------------------------------------------
