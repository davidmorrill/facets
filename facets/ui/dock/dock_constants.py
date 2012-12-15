"""
Defines constants used by various parts of DockWindow.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Tuple, Int, Enum

from facets.ui.pen \
    import Pen

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard font text height:
text_dy = 13

# Padding size for 'fixed' splitter bars:
FixedSplitterPadding = 0

# Default maximum allowed length of a tab label:
MaxTabLength = 60

# Tab drawing states:
TabInactive = 1
TabActive   = 2
TabHover    = 3

NormalStates    = ( TabInactive, TabActive )
NotActiveStates = ( TabInactive, TabHover )

# Normal background color:
BGColor = None

# Feature overlay colors:
FeatureBrushColor = ( 255, 255, 255 )
FeaturePenColor   = (  92,  92,  92 )

# Color used to update the screen while dragging a splitter bar:
DragColor = ( 96, 96, 96 )

# The colors used for drawing engraved text on tabs:
ENGRAVED_DARK  = (  28,  28,  28 )
ENGRAVED_LIGHT = ( 255, 255, 255 )

# Colors and pens used while dragging a DockWindow tab/drag bar:
DragTabBrush      = ( 153, 255, 165, 160 )
DragSectionBrush1 = ( 163, 188, 239,  64 )
DragSectionBrush2 = ( 163, 188, 239, 224 )
DragTabPen        = Pen( color = ( 103, 213, 115, 192 ), width = 5 )
DragSectionPen1   = Pen( color = ( 255, 255, 255, 255 ), width = 1 )
DragSectionPen2   = Pen( color = (  80, 129, 229, 224 ), width = 5 )
DragSectionPen3   = Pen( color = (  80, 129, 229, 224 ), width = 3 )

# Drop Info kinds:
DOCK_TOP      = 0
DOCK_BOTTOM   = 1
DOCK_LEFT     = 2
DOCK_RIGHT    = 3
DOCK_XCHG     = 4
DOCK_TAB      = 5
DOCK_TABADD   = 6
DOCK_BAR      = 7
DOCK_NONE     = 8
DOCK_SPLITTER = 9
DOCK_EXPORT   = 10

# Splitter states:
SPLIT_VLEFT   = 0
SPLIT_VMIDDLE = 1
SPLIT_VRIGHT  = 2
SPLIT_HTOP    = 3
SPLIT_HMIDDLE = 4
SPLIT_HBOTTOM = 5

# Empty clipping area:
no_clip = ( 0, 0, 0, 0 )

# Valid sequence types:
SequenceType = ( list, tuple )

# Tab scrolling directions:
SCROLL_LEFT  = 1
SCROLL_RIGHT = 2
SCROLL_TO    = 3

# Feature modes:
FEATURE_NONE          = -1  # Has no features
FEATURE_NORMAL        = 0   # Has normal features
FEATURE_CHANGED       = 1   # Has changed or new features
FEATURE_DROP          = 2   # Has drag data compatible drop features
FEATURE_DISABLED      = 3   # Has feature icon, but is currently disabled
FEATURE_VISIBLE       = 4   # Has visible features (mouseover mode)
FEATURE_DROP_VISIBLE  = 5   # Has visible drop features (mouseover mode)
FEATURE_PRE_NORMAL    = 6   # Has normal features (but has not been drawn yet)
FEATURE_EXTERNAL_DRAG = 256 # A drag started in another DockWindow is active

# Feature sets:
NO_FEATURE_ICON  = ( FEATURE_NONE, FEATURE_DISABLED, FEATURE_VISIBLE,
                     FEATURE_DROP_VISIBLE )
FEATURES_VISIBLE = ( FEATURE_VISIBLE, FEATURE_DROP_VISIBLE )
FEATURE_END_DROP = ( FEATURE_DROP, FEATURE_VISIBLE, FEATURE_DROP_VISIBLE )
NORMAL_FEATURES  = ( FEATURE_NORMAL, FEATURE_DISABLED )

#-------------------------------------------------------------------------------
#  Global data:
#-------------------------------------------------------------------------------

# The list of available DockWindowFeatures:
features = []

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# Docking drag bar style:
DockStyle = Enum( 'tab', 'horizontal', 'vertical', 'fixed' )

# Bounds (i.e. x, y, dx, dy):
Bounds = Tuple( Int, Int, Int, Int )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

_no_dock_info = None

def no_dock_info ( ):
    """ Returns the reference to the 'no_dock_info' shared object.
    """
    global _no_dock_info

    if _no_dock_info is None:
        import dock_info

        _no_dock_info = dock_info.DockInfo( kind = DOCK_NONE )

    return _no_dock_info

#-- EOF ------------------------------------------------------------------------