"""
Facets UI 'display only' LED numeric editor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from wx.gizmos \
    import LEDNumberCtrl, LED_ALIGN_LEFT, LED_ALIGN_CENTER, LED_ALIGN_RIGHT

from facets.api \
    import Enum, Editor, BasicEditorFactory

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# LED alignment styles:
LEDStyles = {
    'left':   LED_ALIGN_LEFT,
    'center': LED_ALIGN_CENTER,
    'right':  LED_ALIGN_RIGHT,
}

#-------------------------------------------------------------------------------
#  '_LEDEditor' class:
#-------------------------------------------------------------------------------

class _LEDEditor ( Editor ):
    """ Facets UI 'display only' LED numeric editor.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = LEDNumberCtrl( parent, -1 )
        self.control.SetAlignment( LEDStyles[ self.factory.alignment ] )
        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.control.SetValue( self.str_value )

#-------------------------------------------------------------------------------
#  'LEDEditor' class:
#-------------------------------------------------------------------------------

class LEDEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _LEDEditor

    # The alignment of the numeric text within the control:
    alignment = Enum( 'right', 'left', 'center' )

#-- EOF ------------------------------------------------------------------------