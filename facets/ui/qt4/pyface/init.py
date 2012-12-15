"""
Validate the Qt and PyQt versions.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 \
    import QtCore

#-------------------------------------------------------------------------------
#  Validate the Qt and PyQt versions:
#-------------------------------------------------------------------------------

if QtCore.QT_VERSION < 0x040200:
    raise RuntimeError(
        "Need Qt v4.2 or higher, but got v%s" % QtCore.QT_VERSION_STR
    )

if QtCore.PYQT_VERSION < 0x040100:
    raise RuntimeError(
        "Need PyQt v4.1 or higher, but got v%s" % QtCore.PYQT_VERSION_STR
    )

#-- EOF ------------------------------------------------------------------------