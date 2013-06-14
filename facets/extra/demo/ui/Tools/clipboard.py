"""
Clipboard: A Facets component tool.

Generated by:
  facets.extra.tools.tools

Perspective:
  Clipboard

Date/Time:
  Friday, September 09, 2011 at 06:30:59 PM

Component Tools:
  Clipboard
  ImageKnife
  ImagePalette
  TextFile
  UniversalInspector

Supported Features:
  DebugFeature
  DragDropFeature
  OptionsFeature
  SaveStateFeature
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from cPickle \
    import loads

from facets.api \
    import HasPrivateFacets, List, Any, Instance, View, Item, NotebookEditor

from facets.extra.tools.tools \
    import Connection

from facets.extra.tools.clipboard \
    import Clipboard

from facets.extra.tools.image_knife \
    import ImageKnife

from facets.extra.tools.image_palette \
    import ImagePalette

from facets.extra.tools.text_file \
    import TextFile

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
#  'Clipboard' class:
#-------------------------------------------------------------------------------

class Clipboard ( HasPrivateFacets ):

    #-- Class Constants --------------------------------------------------------

    # The pickled string form of the layout template used by the tool contents:
    _template = "cfacets.core.facet_defs\n__newobj__\np1\n(cfacets.ui.dock.dock_section\nDockSection\np2\ntRp3\n(dp4\nS'splitters'\np5\nccopy_reg\n_reconstructor\np6\n(cfacets.core.facet_collections\nFacetListObject\np7\nc__builtin__\nlist\np8\n(ltRp9\n(dp10\nS'name_items'\np11\nS'splitters_items'\np12\nsS'object'\np13\ng3\nsS'name'\np14\ng5\nsbsS'selected'\np15\nI00\nsS'features'\np16\ng6\n(g7\ng8\n(ltRp17\n(dp18\ng11\nS'features_items'\np19\nsg13\ng3\nsg14\ng16\nsbsS'parent'\np20\nNsS'width'\np21\nI1667\nsS'feature_mode'\np22\nI-1\nsS'max_tab_length'\np23\nI30\nsS'bounds'\np24\n(I0\nI0\nI0\nI0\ntp25\nsS'drag_bounds'\np26\ng25\nsS'dock_window'\np27\nNsS'drop_features'\np28\ng6\n(g7\ng8\n(ltRp29\n(dp30\ng11\nS'drop_features_items'\np31\nsg13\ng3\nsg14\ng28\nsbsS'__facets_version__'\np32\nS'0.1'\np33\nsS'contents'\np34\ng6\n(g7\ng8\n(lp35\ng1\n(g2\ntRp36\n(dp37\ng5\ng6\n(g7\ng8\n(ltRp38\n(dp39\ng11\nS'splitters_items'\np40\nsg13\ng36\nsg14\ng5\nsbsg15\nI00\nsg16\ng6\n(g7\ng8\n(ltRp41\n(dp42\ng11\nS'features_items'\np43\nsg13\ng36\nsg14\ng16\nsbsg20\ng3\nsg21\nI1667\nsg22\nI-1\nsg23\nI30\nsg24\ng25\nsg26\ng25\nsg27\nNsg28\ng6\n(g7\ng8\n(ltRp44\n(dp45\ng11\nS'drop_features_items'\np46\nsg13\ng36\nsg14\ng28\nsbsg32\ng33\nsg34\ng6\n(g7\ng8\n(lp47\ng1\n(cfacets.ui.dock.dock_region\nDockRegion\np48\ntRp49\n(dp50\ng15\nI00\nsg16\ng6\n(g7\ng8\n(ltRp51\n(dp52\ng11\nS'features_items'\np53\nsg13\ng49\nsg14\ng16\nsbsg20\ng36\nsg21\nI432\nsg22\nI-1\nsS'max_tab'\np54\nI0\nsS'tab_scroll_index'\np55\nI-1\nsg23\nI30\nsg24\ng25\nsg26\ng25\nsg28\ng6\n(g7\ng8\n(ltRp56\n(dp57\ng11\nS'drop_features_items'\np58\nsg13\ng49\nsg14\ng28\nsbsg32\ng33\nsg34\ng6\n(g7\ng8\n(lp59\ng1\n(cfacets.ui.dock.dock_control\nDockControl\np60\ntRp61\n(dp62\nS'control'\np63\nNsg16\ng6\n(g7\ng8\n(ltRp64\n(dp65\ng11\nS'features_items'\np66\nsg13\ng61\nsg14\ng16\nsbsS'image'\np67\nNsS'height'\np68\nI682\nsS'num_window_features'\np69\nI0\nsS'visible'\np70\nI00\nsS'export'\np71\nS''\nsS'id'\np72\nS'Clipboard'\np73\nsS'num_global_features'\np74\nI0\nsS'style'\np75\nS'tab'\np76\nsS'resizable'\np77\nI01\nsg22\nI-1\nsg15\nI00\nsg21\nI426\nsS'user_style'\np78\nI00\nsS'user_name'\np79\nI00\nsg32\ng33\nsg20\ng49\nsg26\ng25\nsS'on_close'\np80\nNsS'tab_state'\np81\nNsS'dockable'\np82\nNsS'locked'\np83\nI00\nsg14\ng73\nsg28\ng6\n(g7\ng8\n(ltRp84\n(dp85\ng11\nS'drop_features_items'\np86\nsg13\ng61\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsS'closeable'\np87\nI01\nsbatRp88\n(dp89\ng11\nS'contents_items'\np90\nsg13\ng49\nsg14\ng34\nsbsS'active'\np91\nI-1\nsg68\nI707\nsS'left_tab'\np92\nI0\nsg81\nNsbag1\n(g48\ntRp93\n(dp94\ng15\nI00\nsg16\ng6\n(g7\ng8\n(ltRp95\n(dp96\ng11\nS'features_items'\np97\nsg13\ng93\nsg14\ng16\nsbsg20\ng36\nsg21\nI1667\nsg22\nI-1\nsg54\nI0\nsg55\nI-1\nsg23\nI30\nsg24\ng25\nsg26\ng25\nsg28\ng6\n(g7\ng8\n(ltRp98\n(dp99\ng11\nS'drop_features_items'\np100\nsg13\ng93\nsg14\ng28\nsbsg32\ng33\nsg34\ng6\n(g7\ng8\n(lp101\ng1\n(g60\ntRp102\n(dp103\ng63\nNsg16\ng6\n(g7\ng8\n(ltRp104\n(dp105\ng11\nS'features_items'\np106\nsg13\ng102\nsg14\ng16\nsbsg67\nNsg68\nI967\nsg69\nI0\nsg70\nI01\nsg71\nS''\nsg72\nS'Universal Inspector'\np107\nsg74\nI0\nsg75\ng76\nsg77\nI01\nsg22\nI-1\nsg15\nI00\nsg21\nI1661\nsg78\nI00\nsg79\nI00\nsg32\ng33\nsg20\ng93\nsg26\ng25\nsg80\nNsg81\nNsg82\nNsg83\nI00\nsg14\ng107\nsg28\ng6\n(g7\ng8\n(ltRp108\n(dp109\ng11\nS'drop_features_items'\np110\nsg13\ng102\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsg87\nI00\nsbag1\n(g60\ntRp111\n(dp112\ng63\nNsg16\ng6\n(g7\ng8\n(ltRp113\n(dp114\ng11\nS'features_items'\np115\nsg13\ng111\nsg14\ng16\nsbsg67\nNsg68\nI967\nsg69\nI0\nsg70\nI01\nsg71\nS''\nsg72\nS'Image Knife'\np116\nsg74\nI0\nsg75\ng76\nsg77\nI01\nsg22\nI-1\nsg15\nI00\nsg21\nI1661\nsg78\nI00\nsg79\nI00\nsg32\ng33\nsg20\ng93\nsg26\ng25\nsg80\nNsg81\nNsg82\nNsg83\nI00\nsg14\ng116\nsg28\ng6\n(g7\ng8\n(ltRp117\n(dp118\ng11\nS'drop_features_items'\np119\nsg13\ng111\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsg87\nI00\nsbag1\n(g60\ntRp120\n(dp121\ng63\nNsg16\ng6\n(g7\ng8\n(ltRp122\n(dp123\ng11\nS'features_items'\np124\nsg13\ng120\nsg14\ng16\nsbsg67\nNsg68\nI967\nsg69\nI0\nsg70\nI01\nsg71\nS''\nsg72\nS'Image Palette'\np125\nsg74\nI0\nsg75\ng76\nsg77\nI01\nsg22\nI-1\nsg15\nI00\nsg21\nI1661\nsg78\nI00\nsg79\nI00\nsg32\ng33\nsg20\ng93\nsg26\ng25\nsg80\nNsg81\nNsg82\nNsg83\nI00\nsg14\ng125\nsg28\ng6\n(g7\ng8\n(ltRp126\n(dp127\ng11\nS'drop_features_items'\np128\nsg13\ng120\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsg87\nI00\nsbag1\n(g60\ntRp129\n(dp130\ng63\nNsg16\ng6\n(g7\ng8\n(ltRp131\n(dp132\ng11\nS'features_items'\np133\nsg13\ng129\nsg14\ng16\nsbsg67\nNsg68\nI967\nsg69\nI0\nsg70\nI01\nsg71\nS''\nsg72\nS'Text'\np134\nsg74\nI0\nsg75\ng76\nsg77\nI01\nsg22\nI-1\nsg15\nI00\nsg21\nI1661\nsg78\nI00\nsg79\nI00\nsg32\ng33\nsg20\ng93\nsg26\ng25\nsg80\nNsg81\nNsg82\nNsg83\nI00\nsg14\ng134\nsg28\ng6\n(g7\ng8\n(ltRp135\n(dp136\ng11\nS'drop_features_items'\np137\nsg13\ng129\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsg87\nI00\nsbatRp138\n(dp139\ng11\nS'contents_items'\np140\nsg13\ng93\nsg14\ng34\nsbsg91\nI2\nsg68\nI992\nsg92\nI0\nsg81\nNsbatRp141\n(dp142\ng11\nS'contents_items'\np143\nsg13\ng36\nsg14\ng34\nsbsg68\nI992\nsg81\nNsS'is_row'\np144\nI01\nsbatRp145\n(dp146\ng11\nS'contents_items'\np147\nsg13\ng3\nsg14\ng34\nsbsg68\nI992\nsg81\nNsg144\nI00\nsb."

    #-- Facet Definitions ------------------------------------------------------

    # The component tools:
    tool_1 = Instance( Clipboard, { 'name': 'Clipboard' } )
    tool_2 = Instance( ImageKnife, { 'name': 'Image Knife' } )
    tool_3 = Instance( ImagePalette, { 'name': 'Image Palette' } )
    tool_4 = Instance( TextFile, { 'name': 'Text' } )
    tool_5 = Instance( UniversalInspector, { 'name': 'Universal Inspector' } )

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
            title     = 'Clipboard Tool',
            id        = 'facets.extra.tools.tools.generated.Clipboard',
            resizable = True,
            width     = 0.5,
            height    = 0.298
        )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        """ Initializes all of the inter-tool connections.
        """
        self.tools = [
            self.tool_1,
            self.tool_2,
            self.tool_3,
            self.tool_4,
            self.tool_5
        ]
        self.connections = [
            Connection( connection = 'both',
                        object1    = self.tool_1,
                        name1      = 'object',
                        object2    = self.tool_5,
                        name2      = 'item'
            ),
            Connection( connection = 'from',
                        object1    = self.tool_1,
                        name1      = 'image',
                        object2    = self.tool_2,
                        name2      = 'input_image'
            ),
            Connection( connection = 'from',
                        object1    = self.tool_3,
                        name1      = 'output_image',
                        object2    = self.tool_2,
                        name2      = 'input_image'
            ),
            Connection( connection = 'both',
                        object1    = self.tool_4,
                        name1      = 'text',
                        object2    = self.tool_1,
                        name2      = 'text'
            ),
            Connection( connection = 'from',
                        object1    = self.tool_1,
                        name1      = 'image',
                        object2    = self.tool_3,
                        name2      = 'input_image'
            )
        ]

    #-- Facet Default Values ---------------------------------------------------

    def _template_default ( self ):
        return loads( self._template )

#-- Create the demo version of the tool ----------------------------------------

demo = Clipboard

#-- Start the tool (if invoked from the command line) --------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------