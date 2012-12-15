"""
Defines a set of GUI toolkit neutral function based common colors.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  Common Colors:
#-------------------------------------------------------------------------------

_constants  = toolkit().constants()

# Standard window frame background color:
WindowColor = _constants.get( 'WindowColor', 0xFFFFFF )

# Standard color of valid input:
OKColor = ( 255, 255, 255 )

# Standard color used to highlight input errors:
ErrorColor = ( 255, 192, 192 )

# Standard color for the background of a read only control:
ReadonlyColor = ( 244, 243, 238 )

# Standard color for marking a control as 'droppable':
DropColor = ( 215, 242, 255 )

# Default color for text:
TextColor = ( 0, 0, 0 )

# Default color for selections:
SelectionColor = ( 200, 224, 255 )

#-- EOF ------------------------------------------------------------------------