"""
The base implementation of all pyface widgets.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from toolkit \
    import toolkit_object

#-------------------------------------------------------------------------------
#  Define the GUI toolkit specific implementation:
#-------------------------------------------------------------------------------

Widget = toolkit_object( 'widget:Widget' )

#-- EOF ------------------------------------------------------------------------