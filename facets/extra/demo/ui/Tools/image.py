"""
Image: A Facets component tool.

Generated by:
  facets.extra.tools.tools

Perspective:
  Image

Date/Time:
  Monday, August 29, 2011 at 02:22:43 PM

Component Tools:
  FileStack
  ImageTransformer

Supported Features:
  DebugFeature
  SaveStateFeature
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

from facets.extra.tools.file_stack \
    import FileStack

from facets.extra.tools.image_transformer \
    import ImageTransformer

from facets.extra.features.debug_feature \
    import DebugFeature

from facets.extra.features.save_state_feature \
    import SaveStateFeature

#-------------------------------------------------------------------------------
#  'Image' class:
#-------------------------------------------------------------------------------

class Image ( HasPrivateFacets ):

    #-- Class Constants --------------------------------------------------------

    # The pickled string form of the layout template used by the tool contents:
    _template = "cfacets.core.facet_defs\n__newobj__\np1\n(cfacets.ui.dock.dock_section\nDockSection\np2\ntRp3\n(dp4\nS'splitters'\np5\nccopy_reg\n_reconstructor\np6\n(cfacets.core.facet_collections\nFacetListObject\np7\nc__builtin__\nlist\np8\n(lp9\ng1\n(cfacets.ui.dock.dock_splitter\nDockSplitter\np10\ntRp11\n(dp12\nS'control'\np13\nNsS'index'\np14\nI0\nsS'style'\np15\nS'horizontal'\np16\nsS'selected'\np17\nI00\nsS'features'\np18\ng6\n(g7\ng8\n(ltRp19\n(dp20\nS'name_items'\np21\nS'features_items'\np22\nsS'object'\np23\ng11\nsS'name'\np24\ng18\nsbsS'parent'\np25\ng3\nsS'feature_mode'\np26\nI-1\nsS'drop_features'\np27\ng6\n(g7\ng8\n(ltRp28\n(dp29\ng21\nS'drop_features_items'\np30\nsg23\ng11\nsg24\ng27\nsbsS'max_tab_length'\np31\nI30\nsS'bounds'\np32\n(I0\nI0\nI0\nI0\ntp33\nsS'height'\np34\nI-1\nsS'width'\np35\nI-1\nsS'__facets_version__'\np36\nS'0.1'\np37\nsS'drag_bounds'\np38\ng33\nsS'closeable'\np39\nI00\nsS'tab_state'\np40\nNsg24\nS''\nsbatRp41\n(dp42\ng21\nS'splitters_items'\np43\nsg23\ng3\nsg24\ng5\nsbsg17\nI00\nsg18\ng6\n(g7\ng8\n(ltRp44\n(dp45\ng21\nS'features_items'\np46\nsg23\ng3\nsg24\ng18\nsbsg25\nNsg35\nI1362\nsg26\nI-1\nsg31\nI30\nsg32\ng33\nsg38\ng33\nsS'dock_window'\np47\nNsg27\ng6\n(g7\ng8\n(ltRp48\n(dp49\ng21\nS'drop_features_items'\np50\nsg23\ng3\nsg24\ng27\nsbsg36\ng37\nsS'contents'\np51\ng6\n(g7\ng8\n(lp52\ng1\n(cfacets.ui.dock.dock_region\nDockRegion\np53\ntRp54\n(dp55\ng17\nI00\nsg18\ng6\n(g7\ng8\n(ltRp56\n(dp57\ng21\nS'features_items'\np58\nsg23\ng54\nsg24\ng18\nsbsg25\ng3\nsg35\nI259\nsg26\nI-1\nsS'max_tab'\np59\nI0\nsS'tab_scroll_index'\np60\nI-1\nsg31\nI30\nsg32\ng33\nsg38\ng33\nsg27\ng6\n(g7\ng8\n(ltRp61\n(dp62\ng21\nS'drop_features_items'\np63\nsg23\ng54\nsg24\ng27\nsbsg36\ng37\nsg51\ng6\n(g7\ng8\n(lp64\ng1\n(cfacets.ui.dock.dock_control\nDockControl\np65\ntRp66\n(dp67\ng13\nNsg18\ng6\n(g7\ng8\n(ltRp68\n(dp69\ng21\nS'features_items'\np70\nsg23\ng66\nsg24\ng18\nsbsS'image'\np71\nNsg34\nI696\nsS'num_window_features'\np72\nI0\nsS'visible'\np73\nI01\nsS'export'\np74\nS''\nsS'id'\np75\nS'File Stack'\np76\nsS'num_global_features'\np77\nI0\nsg15\nS'tab'\np78\nsS'resizable'\np79\nI01\nsg26\nI-1\nsg17\nI00\nsg35\nI253\nsS'user_style'\np80\nI00\nsS'user_name'\np81\nI00\nsg36\ng37\nsg25\ng54\nsg38\ng33\nsS'on_close'\np82\nNsg40\nNsS'dockable'\np83\nNsS'locked'\np84\nI00\nsg24\ng76\nsg27\ng6\n(g7\ng8\n(ltRp85\n(dp86\ng21\nS'drop_features_items'\np87\nsg23\ng66\nsg24\ng27\nsbsg31\nI30\nsg32\ng33\nsg39\nI00\nsbatRp88\n(dp89\ng21\nS'contents_items'\np90\nsg23\ng54\nsg24\ng51\nsbsS'active'\np91\nI0\nsg34\nI721\nsS'left_tab'\np92\nI0\nsg40\nNsbag1\n(g53\ntRp93\n(dp94\ng17\nI00\nsg18\ng6\n(g7\ng8\n(ltRp95\n(dp96\ng21\nS'features_items'\np97\nsg23\ng93\nsg24\ng18\nsbsg25\ng3\nsg35\nI1101\nsg26\nI-1\nsg59\nI0\nsg60\nI-1\nsg31\nI30\nsg32\ng33\nsg38\ng33\nsg27\ng6\n(g7\ng8\n(ltRp98\n(dp99\ng21\nS'drop_features_items'\np100\nsg23\ng93\nsg24\ng27\nsbsg36\ng37\nsg51\ng6\n(g7\ng8\n(lp101\ng1\n(g65\ntRp102\n(dp103\ng13\nNsg18\ng6\n(g7\ng8\n(ltRp104\n(dp105\ng21\nS'features_items'\np106\nsg23\ng102\nsg24\ng18\nsbsg71\nNsg34\nI696\nsg72\nI0\nsg73\nI01\nsg74\nS''\nsg75\nS'Image Transformer'\np107\nsg77\nI0\nsg15\ng78\nsg79\nI01\nsg26\nI-1\nsg17\nI00\nsg35\nI1095\nsg80\nI00\nsg81\nI00\nsg36\ng37\nsg25\ng93\nsg38\ng33\nsg82\nNsg40\nNsg83\nNsg84\nI00\nsg24\ng107\nsg27\ng6\n(g7\ng8\n(ltRp108\n(dp109\ng21\nS'drop_features_items'\np110\nsg23\ng102\nsg24\ng27\nsbsg31\nI30\nsg32\ng33\nsg39\nI00\nsbatRp111\n(dp112\ng21\nS'contents_items'\np113\nsg23\ng93\nsg24\ng51\nsbsg91\nI0\nsg34\nI721\nsg92\nI0\nsg40\nNsbatRp114\n(dp115\ng21\nS'contents_items'\np116\nsg23\ng3\nsg24\ng51\nsbsg34\nI721\nsg40\nNsS'is_row'\np117\nI01\nsb."

    #-- Facet Definitions ------------------------------------------------------

    # The component tools:
    tool_1 = Instance( FileStack, { 'name': 'File Stack' } )
    tool_2 = Instance( ImageTransformer, { 'name': 'Image Transformer' } )

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
                          SaveStateFeature
                      ],
                      dock_style = 'tab',
                      page_name  = '.name',
                      template   = 'template'
                  )
            ),
            title     = 'Image Tool',
            id        = 'facets.extra.tools.tools.generated.Image',
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
                        name1      = 'file_name',
                        object2    = self.tool_2,
                        name2      = 'value'
            )
        ]

    #-- Facet Default Values ---------------------------------------------------

    def _template_default ( self ):
        return loads( self._template )

#-- Create the demo version of the tool ----------------------------------------

demo = Image

#-- Start the tool (if invoked from the command line) --------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------