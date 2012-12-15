"""
Defines constants used by the wxPython implementation of the various text
editors and text editor factories.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import wx

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Define platform and wx version constants:
is_mac   = (sys.platform == 'darwin')
is_win32 = (sys.platform == 'win32')
is_wx26  = (float( '.'.join( wx.__version__.split( '.' )[0:2] ) ) < 2.8)

# Default dialog title:
DefaultTitle = 'Edit properties'

# Color of valid input:
OKColor = wx.WHITE

# Color to highlight input errors:
ErrorColor = wx.Colour( 255, 192, 192 )

# Color for background of read-only fields:
ReadonlyColor = wx.Colour( 244, 243, 238 )

# Color for background of fields where objects can be dropped:
DropColor = wx.Colour( 215, 242, 255 )

# Color for an editable field:
EditableColor = wx.WHITE

# Color for background of windows (like dialog background color):
if is_mac:
    WindowColor = wx.Colour( 232, 232, 232 )
else:
    WindowColor = wx.SystemSettings_GetColour( wx.SYS_COLOUR_BTNFACE )

# Standard width of an image bitmap:
standard_bitmap_width = 120

# Width of a scrollbar:
scrollbar_dx = wx.SystemSettings_GetMetric( wx.SYS_VSCROLL_X )

# Screen size values:
screen_dx = wx.SystemSettings_GetMetric( wx.SYS_SCREEN_X )
screen_dy = wx.SystemSettings_GetMetric( wx.SYS_SCREEN_Y )

#-- EOF ------------------------------------------------------------------------