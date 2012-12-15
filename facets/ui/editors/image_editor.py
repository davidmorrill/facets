"""
Facets UI 'display only' image editor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, BasicEditorFactory, ATheme

from facets.ui.ui_facets \
    import Image

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.ui.controls.image_control \
    import ImageControl

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_ImageEditor' class:
#-------------------------------------------------------------------------------

class _ImageEditor ( Editor ):
    """ Facets UI 'display only' image editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ImageControl useb by the editor:
    image_control = Instance( ImageControl, () )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.adapter = self.image_control.set(
            image   = self.factory.image or self.value,
            theme   = self.factory.theme,
            padding = 0,
            parent  = parent
        )()
        self.adapter.size_policy = ( 'expanding', 'expanding' )

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self.factory.image is None:
            value = self.value
            if isinstance( value, AnImageResource ):
                self.image_control.image = value

#-------------------------------------------------------------------------------
#  'ImageEditor' class:
#-------------------------------------------------------------------------------

class ImageEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ImageEditor

    # The optional image resource to be displayed by the editor (if not
    # specified, the editor's object value is used as the ImageResource to
    # display):
    image = Image

    # The optional theme to display as the background for the image:
    theme = ATheme

#-- EOF ------------------------------------------------------------------------