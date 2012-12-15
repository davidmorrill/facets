"""
Helper function to add all standard DockWindowFeature feature classes to
DockWindow.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from connect_feature \
    import ConnectFeature

from custom_feature \
    import ACustomFeature

from debug_feature \
    import DebugFeature

from dock_control_feature \
    import DockControlFeature

from drag_drop_feature \
    import DragDropFeature

from drop_file_feature \
    import DropFileFeature

from layout_feature \
    import LayoutFeature

from options_feature \
    import OptionsFeature

from popup_menu_feature \
    import PopupMenuFeature

from save_feature \
    import SaveFeature

from save_state_feature \
    import SaveStateFeature

from tool_feature \
    import ToolFeature

from facets.ui.dock.api \
    import add_feature

#-------------------------------------------------------------------------------
#  Adds all of the standard DockWindowFeature feature classes to DockWindow:
#-------------------------------------------------------------------------------

def add_standard_features ( ):
    """ Adds all of the standard DockWindowFeature feature classes to
        DockWindow.
    """
    for klass in [ ConnectFeature, ACustomFeature, DebugFeature,
                   DockControlFeature, DragDropFeature, DropFileFeature,
                   LayoutFeature, OptionsFeature, PopupMenuFeature, SaveFeature,
                   SaveStateFeature, SaveStateFeature, ToolFeature ]:
        add_feature( klass )

#-- EOF ------------------------------------------------------------------------