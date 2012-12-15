"""
Defines useful package-wide constants.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Platform identification flags:
is_windows = sys.platform.startswith( 'win' )
is_mac     = (sys.platform == 'darwin')
is_linux   = (not (is_windows or is_mac))

# The maximum floating point value:
try:
    max_float = sys.float_info.max
except:
    max_float = 1.7976931348623157e+308

#-- EOF ------------------------------------------------------------------------
