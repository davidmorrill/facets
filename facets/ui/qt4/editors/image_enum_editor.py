"""
Defines the various image enumeration editors and the image enumeration
editor factory for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Module, Type, Unicode

from enum_editor \
    import EnumEditor

#-------------------------------------------------------------------------------
#  'ImageEnumEditor' class:
#-------------------------------------------------------------------------------

class ImageEnumEditor ( EnumEditor ):
    """ PyQt editor factory for image enumeration editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Suffix to add to values to form image names:
    suffix = Unicode

    # Path to use to locate image files:
    path = Unicode

    # Class used to derive the path to the image files:
    klass = Type

    # Module used to derive the path to the image files:
    module = Module

#-- EOF ------------------------------------------------------------------------