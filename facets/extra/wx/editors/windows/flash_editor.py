"""
Facets UI MS Flash editor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import  wx

if wx.Platform == '__WXMSW__':
    from wx.lib.flashwin import FlashWindow

from facets.ui.wx.editors.editor \
    import Editor

from facets.ui.wx.editors.basic_editor_factory \
    import BasicEditorFactory

#-------------------------------------------------------------------------------
#  '_FlashEditor' class:
#-------------------------------------------------------------------------------

class _FlashEditor ( Editor ):
    """ Facets UI Flash editor.
    """

    #---------------------------------------------------------------------------
    #  Facet definitions:
    #---------------------------------------------------------------------------

    # Is the table editor is scrollable? This value overrides the default.
    scrollable = True

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = FlashWindow( parent )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object facet changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        value = self.str_value.strip()
        if value.find( '://' ) < 0:
            value = 'file://' + value

        wx.BeginBusyCursor()
        self.control.LoadMovie( 0, value )
        wx.EndBusyCursor()

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for Flash editors:
class FlashEditor ( BasicEditorFactory ):

    # The editor class to be created:
    klass = _FlashEditor

#-- EOF ------------------------------------------------------------------------