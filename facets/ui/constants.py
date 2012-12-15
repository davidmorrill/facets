"""
Defines GUI toolkit neutral constants.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Define platform constants:
is_mac = (sys.platform == 'darwin')

# Default dialog title
DefaultTitle = 'Edit properties'

# Standard width of an image bitmap
standard_bitmap_width = 120

# Information about the size of the user's display(s):
screen_dx, screen_dy = toolkit().screen_size()
screen_info          = toolkit().screen_info()

# The standard width of a vertical scrollbar, and the standard height of a
# horizontal scrollbar:
scrollbar_dx, scrollbar_dy = toolkit().scrollbar_size()

# 2D alignment flags:
CENTER = 0
LEFT   = 1
RIGHT  = 2
TOP    = 4
BOTTOM = 8

TOP_LEFT = TOP | LEFT

# The mapping from 2D alignment values to 2D alignment flags:
AlignmentMap = {
    None:           TOP_LEFT,
    'top left':     TOP_LEFT,
    'top':          TOP    | CENTER,
    'top right':    TOP    | RIGHT,
    'left':         CENTER | LEFT,
    'center':       CENTER,
    'right':        CENTER | RIGHT,
    'bottom left':  BOTTOM | LEFT,
    'bottom':       BOTTOM | CENTER,
    'bottom right': BOTTOM | RIGHT
}

#-- EOF ------------------------------------------------------------------------