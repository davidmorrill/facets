"""
Run the Facets UI demo.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.image \
    import ImageLibrary

from facets.extra.demo.demo \
    import demo

#-- Run the demo ---------------------------------------------------------------

# Add the demo images to the image library:
ImageLibrary().add_volume()

# Start the demo:
demo()

#-- EOF ------------------------------------------------------------------------