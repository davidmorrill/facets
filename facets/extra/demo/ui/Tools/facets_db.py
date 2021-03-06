"""
# FacetsDB: A Facets component tool. #

Perspective:

- Facets DB

Component Tools:

- FacetDB
- UniversalInspector

Supported Features:

- DebugFeature
- DragDropFeature
- OptionsFeature
- SaveStateFeature

Generated by:

- facets.extra.tools.tools

Date/Time:

- Thursday, June 09, 2011 at 12:09:44 PM
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from cPickle \
    import loads

from facets.api \
    import HasPrivateFacets, List, Any, Instance, View, Item, NotebookEditor

from facets.extra.helper.generated_tool \
    import Connection

from facets.extra.tools.facet_db \
    import FacetDB

from facets.extra.tools.universal_inspector \
    import UniversalInspector

from facets.extra.features.debug_feature \
    import DebugFeature

from facets.extra.features.drag_drop_feature \
    import DragDropFeature

from facets.extra.features.options_feature \
    import OptionsFeature

from facets.extra.features.save_state_feature \
    import SaveStateFeature

#-------------------------------------------------------------------------------
#  'FacetsDB' class:
#-------------------------------------------------------------------------------

class FacetsDB ( HasPrivateFacets ):

    #-- Class Constants --------------------------------------------------------

    # The pickled string form of the layout template used by the tool contents:
    _template = "cfacets.core.facet_defs\n__newobj__\np1\n(cfacets.ui.dock.dock_section\nDockSection\np2\ntRp3\n(dp4\nS'splitters'\np5\nccopy_reg\n_reconstructor\np6\n(cfacets.core.facet_collections\nFacetListObject\np7\nc__builtin__\nlist\np8\n(lp9\ng1\n(cfacets.ui.dock.dock_splitter\nDockSplitter\np10\ntRp11\n(dp12\nS'index'\np13\nI0\nsS'style'\np14\nS'horizontal'\np15\nsS'selected'\np16\nI00\nsS'features'\np17\ng6\n(g7\ng8\n(ltRp18\n(dp19\nS'name_items'\np20\nS'features_items'\np21\nsS'object'\np22\ng11\nsS'name'\np23\ng17\nsbsS'parent'\np24\ng3\nsS'width'\np25\nI-1\nsS'feature_mode'\np26\nI-1\nsS'max_tab_length'\np27\nI30\nsS'bounds'\np28\n(I0\nI0\nI0\nI0\ntp29\nsS'drag_bounds'\np30\ng29\nsS'drop_features'\np31\ng6\n(g7\ng8\n(ltRp32\n(dp33\ng20\nS'drop_features_items'\np34\nsg22\ng11\nsg23\ng31\nsbsS'__facets_version__'\np35\nS'0.1'\np36\nsS'height'\np37\nI-1\nsS'tab_state'\np38\nNsbatRp39\n(dp40\ng20\nS'splitters_items'\np41\nsg22\ng3\nsg23\ng5\nsbsg16\nI00\nsg17\ng6\n(g7\ng8\n(ltRp42\n(dp43\ng20\nS'features_items'\np44\nsg22\ng3\nsg23\ng17\nsbsg24\nNsg25\nI1366\nsg26\nI-1\nsg27\nI30\nsg28\ng29\nsg30\ng29\nsS'dock_window'\np45\nNsg31\ng6\n(g7\ng8\n(ltRp46\n(dp47\ng20\nS'drop_features_items'\np48\nsg22\ng3\nsg23\ng31\nsbsg35\ng36\nsS'contents'\np49\ng6\n(g7\ng8\n(lp50\ng1\n(cfacets.ui.dock.dock_region\nDockRegion\np51\ntRp52\n(dp53\ng16\nI00\nsg17\ng6\n(g7\ng8\n(ltRp54\n(dp55\ng20\nS'features_items'\np56\nsg22\ng52\nsg23\ng17\nsbsg24\ng3\nsg25\nI444\nsg26\nI-1\nsS'max_tab'\np57\nI0\nsS'tab_scroll_index'\np58\nI-1\nsg27\nI30\nsg28\ng29\nsg30\ng29\nsg31\ng6\n(g7\ng8\n(ltRp59\n(dp60\ng20\nS'drop_features_items'\np61\nsg22\ng52\nsg23\ng31\nsbsg35\ng36\nsg49\ng6\n(g7\ng8\n(lp62\ng1\n(cfacets.ui.dock.dock_control\nDockControl\np63\ntRp64\n(dp65\nS'control'\np66\nNsg17\ng6\n(g7\ng8\n(ltRp67\n(dp68\ng20\nS'features_items'\np69\nsg22\ng64\nsg23\ng17\nsbsS'image'\np70\nNsg37\nI700\nsS'num_window_features'\np71\nI0\nsS'visible'\np72\nI01\nsS'export'\np73\nS''\nsS'id'\np74\nS'Facet DB'\np75\nsS'num_global_features'\np76\nI0\nsg14\nS'tab'\np77\nsS'resizable'\np78\nI01\nsg26\nI-1\nsg16\nI00\nsg25\nI438\nsS'user_style'\np79\nI00\nsS'user_name'\np80\nI00\nsg35\ng36\nsg24\ng52\nsg30\ng29\nsS'on_close'\np81\nNsg38\nNsS'dockable'\np82\nNsS'locked'\np83\nI00\nsg23\ng75\nsg31\ng6\n(g7\ng8\n(ltRp84\n(dp85\ng20\nS'drop_features_items'\np86\nsg22\ng64\nsg23\ng31\nsbsg27\nI30\nsg28\ng29\nsS'closeable'\np87\nI00\nsbatRp88\n(dp89\ng20\nS'contents_items'\np90\nsg22\ng52\nsg23\ng49\nsbsS'active'\np91\nI0\nsg37\nI725\nsS'left_tab'\np92\nI0\nsg38\nNsbag1\n(g51\ntRp93\n(dp94\ng16\nI00\nsg17\ng6\n(g7\ng8\n(ltRp95\n(dp96\ng20\nS'features_items'\np97\nsg22\ng93\nsg23\ng17\nsbsg24\ng3\nsg25\nI920\nsg26\nI-1\nsg57\nI0\nsg58\nI-1\nsg27\nI30\nsg28\ng29\nsg30\ng29\nsg31\ng6\n(g7\ng8\n(ltRp98\n(dp99\ng20\nS'drop_features_items'\np100\nsg22\ng93\nsg23\ng31\nsbsg35\ng36\nsg49\ng6\n(g7\ng8\n(lp101\ng1\n(g63\ntRp102\n(dp103\ng66\nNsg17\ng6\n(g7\ng8\n(ltRp104\n(dp105\ng20\nS'features_items'\np106\nsg22\ng102\nsg23\ng17\nsbsg70\nNsg37\nI700\nsg71\nI0\nsg72\nI01\nsg73\nS''\nsg74\nS'Universal Inspector'\np107\nsg76\nI0\nsg14\ng77\nsg78\nI01\nsg26\nI-1\nsg16\nI00\nsg25\nI914\nsg79\nI00\nsg80\nI00\nsg35\ng36\nsg24\ng93\nsg30\ng29\nsg81\nNsg38\nNsg82\nNsg83\nI00\nsg23\ng107\nsg31\ng6\n(g7\ng8\n(ltRp108\n(dp109\ng20\nS'drop_features_items'\np110\nsg22\ng102\nsg23\ng31\nsbsg27\nI30\nsg28\ng29\nsg87\nI00\nsbatRp111\n(dp112\ng20\nS'contents_items'\np113\nsg22\ng93\nsg23\ng49\nsbsg91\nI0\nsg37\nI725\nsg92\nI0\nsg38\nNsbatRp114\n(dp115\ng20\nS'contents_items'\np116\nsg22\ng3\nsg23\ng49\nsbsg37\nI725\nsg38\nNsS'is_row'\np117\nI01\nsb."

    #-- Facet Definitions ------------------------------------------------------

    # The component tools:
    tool_1 = Instance( FacetDB, () )
    tool_2 = Instance( UniversalInspector, () )

    # The list of all component tools:
    tools = List

    # The layout template for the tools:
    template = Any

    # The list of all inter-tool connections:
    connections = List

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        """ Returns the View to use with this perspective.
        """
        return View(
            Item( 'tools',
                  style      = 'custom',
                  show_label = False,
                  id         = 'tools',
                  editor     = NotebookEditor(
                      features = [
                          DebugFeature,
                          DragDropFeature,
                          OptionsFeature,
                          SaveStateFeature
                      ],
                      dock_style = 'tab',
                      page_name  = '.name',
                      template   = 'template'
                  )
            ),
            title     = 'Facets DB Tool',
            id        = 'facets.extra.tools.tools.generated.FacetsDB',
            resizable = True,
            width     = 0.5,
            height    = 0.265
        )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        """ Initializes all of the inter-tool connections.
        """
        self.tools = [
            self.tool_1,
            self.tool_2
        ]
        self.connections = [
            Connection( connection = 'from',
                        object1    = self.tool_1,
                        name1      = 'value',
                        object2    = self.tool_2,
                        name2      = 'item'
            )
        ]

    #-- Facet Default Values ---------------------------------------------------

    def _template_default ( self ):
        return loads( self._template )

#-- Create the demo version of the tool ----------------------------------------

demo = FacetsDB

#-- Start the tool (if invoked from the command line) --------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------