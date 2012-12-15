"""
The implementation of a shared resource manager.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.lib.resource.api \
    import ResourceManager

from toolkit \
    import toolkit_object

#-------------------------------------------------------------------------------
#  Define the GUI toolkit specific implementation:
#-------------------------------------------------------------------------------

PyfaceResourceFactory = toolkit_object(
    'resource_manager:PyfaceResourceFactory'
)

# Define a shared instance:
resource_manager = ResourceManager(
    resource_factory = PyfaceResourceFactory()
)

#-- EOF ------------------------------------------------------------------------