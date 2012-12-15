"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

#-- Check that the version number is late enough -------------------------------

if wx.VERSION < ( 2, 6 ):
    raise RuntimeError(
        "Need wx version 2.6 or higher, but got %s" % str( wx.VERSION )
    )

#-- Initialize the application object ------------------------------------------

# It's possible that it has already been initialised:
_app = wx.GetApp()

if _app is None:
    _app = wx.PySimpleApp()

    # Before we can load any images we have to initialize wxPython's image
    # handlers:
    wx.InitAllImageHandlers()

#-- EOF ------------------------------------------------------------------------