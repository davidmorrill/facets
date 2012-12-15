"""
Pyface 'DockWindow' support.

This package implements a Pyface 'dockable' window component that allows
child windows to be reorganized within the DockWindow using drag and drop.
The component also allows multiple sub-windows to occupy the same
sub-region of the DockWindow, in which case each sub-window appears as a
separate notebook-like tab within the region.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from dock_constants \
    import DockStyle, DOCK_LEFT, DOCK_RIGHT, DOCK_TOP, DOCK_BOTTOM

from dock_window \
    import DockWindow

from dock_window_handler \
    import DockWindowHandler

from dock_sizer \
    import DockSizer

from dock_control \
    import DockControl, dock_control_for

from dock_group \
    import DockGroup

from dock_section \
    import DockSection

from dock_region \
    import DockRegion

from idockable \
    import IDockable

from idock_ui_provider \
    import IDockUIProvider

from ifeature_tool \
    import IFeatureTool

from dock_window_shell \
    import DockWindowShell

from dock_window_feature \
    import DockWindowFeature, add_feature

#-- EOF ------------------------------------------------------------------------