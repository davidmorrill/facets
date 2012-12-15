"""
ImageLibrary: A Facets component tool.

Generated by:
  facets.extra.tools.tools

Perspective:
  Image Library

Date/Time:
  Wednesday, August 17, 2011 at 12:07:53 PM

Component Tools:
  ImageLibraryViewer
  ImageTransformer
  ImageZoomer

Supported Features:
  DebugFeature
  DropFileFeature
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

from facets.extra.tools.image_library_viewer \
    import ImageLibraryViewer

from facets.extra.tools.image_transformer \
    import ImageTransformer

from facets.extra.tools.image_zoomer \
    import ImageZoomer

from facets.extra.features.debug_feature \
    import DebugFeature

from facets.extra.features.drop_file_feature \
    import DropFileFeature

from facets.extra.features.options_feature \
    import OptionsFeature

from facets.extra.features.save_state_feature \
    import SaveStateFeature

#-------------------------------------------------------------------------------
#  'ImageLibrary' class:
#-------------------------------------------------------------------------------

class ImageLibrary ( HasPrivateFacets ):

    #-- Class Constants --------------------------------------------------------

    # The pickled string form of the layout template used by the tool contents:
    _template = "cfacets.core.facet_defs\n__newobj__\np1\n(cfacets.ui.dock.dock_section\nDockSection\np2\ntRp3\n(dp4\nS'splitters'\np5\nccopy_reg\n_reconstructor\np6\n(cfacets.core.facet_collections\nFacetListObject\np7\nc__builtin__\nlist\np8\n(ltRp9\n(dp10\nS'name_items'\np11\nS'splitters_items'\np12\nsS'object'\np13\ng3\nsS'name'\np14\ng5\nsbsS'selected'\np15\nI00\nsS'features'\np16\ng6\n(g7\ng8\n(ltRp17\n(dp18\ng11\nS'features_items'\np19\nsg13\ng3\nsg14\ng16\nsbsS'parent'\np20\nNsS'width'\np21\nI1362\nsS'feature_mode'\np22\nI-1\nsS'max_tab_length'\np23\nI30\nsS'bounds'\np24\n(I0\nI0\nI0\nI0\ntp25\nsS'drag_bounds'\np26\ng25\nsS'dock_window'\np27\nNsS'drop_features'\np28\ng6\n(g7\ng8\n(ltRp29\n(dp30\ng11\nS'drop_features_items'\np31\nsg13\ng3\nsg14\ng28\nsbsS'__facets_version__'\np32\nS'0.1'\np33\nsS'contents'\np34\ng6\n(g7\ng8\n(lp35\ng1\n(g2\ntRp36\n(dp37\ng5\ng6\n(g7\ng8\n(lp38\ng1\n(cfacets.ui.dock.dock_splitter\nDockSplitter\np39\ntRp40\n(dp41\nS'control'\np42\nNsS'index'\np43\nI0\nsS'style'\np44\nS'horizontal'\np45\nsg15\nI00\nsg16\ng6\n(g7\ng8\n(ltRp46\n(dp47\ng11\nS'features_items'\np48\nsg13\ng40\nsg14\ng16\nsbsg20\ng36\nsg22\nI-1\nsg28\ng6\n(g7\ng8\n(ltRp49\n(dp50\ng11\nS'drop_features_items'\np51\nsg13\ng40\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsS'height'\np52\nI-1\nsg21\nI-1\nsg32\ng33\nsg26\ng25\nsS'closeable'\np53\nI00\nsS'tab_state'\np54\nNsg14\nS''\nsbatRp55\n(dp56\ng11\nS'splitters_items'\np57\nsg13\ng36\nsg14\ng5\nsbsg15\nI00\nsg16\ng6\n(g7\ng8\n(ltRp58\n(dp59\ng11\nS'features_items'\np60\nsg13\ng36\nsg14\ng16\nsbsg20\ng3\nsg21\nI1362\nsg22\nI-1\nsg23\nI30\nsg24\ng25\nsg26\ng25\nsg27\nNsg28\ng6\n(g7\ng8\n(ltRp61\n(dp62\ng11\nS'drop_features_items'\np63\nsg13\ng36\nsg14\ng28\nsbsg32\ng33\nsg34\ng6\n(g7\ng8\n(lp64\ng1\n(cfacets.ui.dock.dock_region\nDockRegion\np65\ntRp66\n(dp67\ng15\nI00\nsg16\ng6\n(g7\ng8\n(ltRp68\n(dp69\ng11\nS'features_items'\np70\nsg13\ng66\nsg14\ng16\nsbsg20\ng36\nsg21\nI749\nsg22\nI-1\nsS'max_tab'\np71\nI0\nsS'tab_scroll_index'\np72\nI-1\nsg23\nI30\nsg24\ng25\nsg26\ng25\nsg28\ng6\n(g7\ng8\n(ltRp73\n(dp74\ng11\nS'drop_features_items'\np75\nsg13\ng66\nsg14\ng28\nsbsg32\ng33\nsg34\ng6\n(g7\ng8\n(lp76\ng1\n(cfacets.ui.dock.dock_control\nDockControl\np77\ntRp78\n(dp79\ng42\nNsg16\ng6\n(g7\ng8\n(ltRp80\n(dp81\ng11\nS'features_items'\np82\nsg13\ng78\nsg14\ng16\nsbsS'image'\np83\nNsg52\nI696\nsS'num_window_features'\np84\nI0\nsS'visible'\np85\nI01\nsS'export'\np86\nS''\nsS'id'\np87\nS'Image Library Viewer'\np88\nsS'num_global_features'\np89\nI0\nsg44\nS'tab'\np90\nsS'resizable'\np91\nI01\nsg22\nI-1\nsg15\nI00\nsg21\nI743\nsS'user_style'\np92\nI00\nsS'user_name'\np93\nI00\nsg32\ng33\nsg20\ng66\nsg26\ng25\nsS'on_close'\np94\nNsg54\nNsS'dockable'\np95\nNsS'locked'\np96\nI00\nsg14\ng88\nsg28\ng6\n(g7\ng8\n(ltRp97\n(dp98\ng11\nS'drop_features_items'\np99\nsg13\ng78\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsg53\nI00\nsbatRp100\n(dp101\ng11\nS'contents_items'\np102\nsg13\ng66\nsg14\ng34\nsbsS'active'\np103\nI0\nsg52\nI721\nsS'left_tab'\np104\nI0\nsg54\nNsbag1\n(g65\ntRp105\n(dp106\ng15\nI00\nsg16\ng6\n(g7\ng8\n(ltRp107\n(dp108\ng11\nS'features_items'\np109\nsg13\ng105\nsg14\ng16\nsbsg20\ng36\nsg21\nI611\nsg22\nI-1\nsg71\nI0\nsg72\nI-1\nsg23\nI30\nsg24\ng25\nsg26\ng25\nsg28\ng6\n(g7\ng8\n(ltRp110\n(dp111\ng11\nS'drop_features_items'\np112\nsg13\ng105\nsg14\ng28\nsbsg32\ng33\nsg34\ng6\n(g7\ng8\n(lp113\ng1\n(g77\ntRp114\n(dp115\ng42\nNsg16\ng6\n(g7\ng8\n(ltRp116\n(dp117\ng11\nS'features_items'\np118\nsg13\ng114\nsg14\ng16\nsbsg83\nNsg52\nI696\nsg84\nI0\nsg85\nI01\nsg86\nS''\nsg87\nS'Image Transformer'\np119\nsg89\nI0\nsg44\ng90\nsg91\nI01\nsg22\nI-1\nsg15\nI00\nsg21\nI605\nsg92\nI00\nsg93\nI00\nsg32\ng33\nsg20\ng105\nsg26\ng25\nsg94\nNsg54\nNsg95\nNsg96\nI00\nsg14\ng119\nsg28\ng6\n(g7\ng8\n(ltRp120\n(dp121\ng11\nS'drop_features_items'\np122\nsg13\ng114\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsg53\nI00\nsbag1\n(g77\ntRp123\n(dp124\ng42\nNsg16\ng6\n(g7\ng8\n(ltRp125\n(dp126\ng11\nS'features_items'\np127\nsg13\ng123\nsg14\ng16\nsbsg83\nNsg52\nI696\nsg84\nI0\nsg85\nI01\nsg86\nS''\nsg87\nS'Image Zoomer'\np128\nsg89\nI0\nsg44\ng90\nsg91\nI01\nsg22\nI-1\nsg15\nI00\nsg21\nI605\nsg92\nI00\nsg93\nI00\nsg32\ng33\nsg20\ng105\nsg26\ng25\nsg94\nNsg54\nNsg95\nNsg96\nI00\nsg14\ng128\nsg28\ng6\n(g7\ng8\n(ltRp129\n(dp130\ng11\nS'drop_features_items'\np131\nsg13\ng123\nsg14\ng28\nsbsg23\nI30\nsg24\ng25\nsg53\nI00\nsbatRp132\n(dp133\ng11\nS'contents_items'\np134\nsg13\ng105\nsg14\ng34\nsbsg103\nI0\nsg52\nI721\nsg104\nI0\nsg54\nNsbatRp135\n(dp136\ng11\nS'contents_items'\np137\nsg13\ng36\nsg14\ng34\nsbsg52\nI721\nsg54\nNsS'is_row'\np138\nI01\nsbatRp139\n(dp140\ng11\nS'contents_items'\np141\nsg13\ng3\nsg14\ng34\nsbsg52\nI721\nsg54\nNsg138\nI00\nsb."

    #-- Facet Definitions ------------------------------------------------------

    # The component tools:
    tool_1 = Instance( ImageLibraryViewer, { 'name': 'Image Library Viewer' } )
    tool_2 = Instance( ImageTransformer, { 'name': 'Image Transformer' } )
    tool_3 = Instance( ImageZoomer, { 'name': 'Image Zoomer' } )

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
                          DropFileFeature,
                          OptionsFeature,
                          SaveStateFeature
                      ],
                      dock_style = 'tab',
                      page_name  = '.name',
                      template   = 'template'
                  )
            ),
            title     = 'Image Library Tool',
            id        = 'facets.extra.tools.tools.generated.ImageLibrary',
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
            self.tool_2,
            self.tool_3
        ]
        self.connections = [
            Connection( connection = 'from',
                        object1    = self.tool_1,
                        name1      = 'image_names',
                        object2    = self.tool_3,
                        name2      = 'value'
            ),
            Connection( connection = 'from',
                        object1    = self.tool_1,
                        name1      = 'image_names',
                        object2    = self.tool_2,
                        name2      = 'value'
            )
        ]

    #-- Facet Default Values ---------------------------------------------------

    def _template_default ( self ):
        return loads( self._template )

#-- Create the demo version of the tool ----------------------------------------

demo = ImageLibrary

#-- Start the tool (if invoked from the command line) --------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------