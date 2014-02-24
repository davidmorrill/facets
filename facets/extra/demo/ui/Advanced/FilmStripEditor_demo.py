"""
# FilmStripEditor Demo #

This demonstrates use of the **FilmStripEditor** and creating a simple custom
**FilmStripAdapter**. It also showcases the **ControlGrabberEditor**, the
**ImageZoomEditor**, and the use of the **Control** *image* facet and the
*scale* method of an **AnImageResource** object.

The demo consists of a FilmStripEditor, a ControlGrabberEditor and an
ImageZoomEditor. Click-drag on the ControlGrabberEditor (represented by the
question mark icon) and release the mouse pointer over another part of the demo
(e.g. the tree view). The ControlGrabberEditor will set its value (the *control*
facet of the FilmStripDemo object) to the Control the mouse pointer is over at
the time that the mouse button is released.

The demo code responds by creating a *screen capture* of the control's contents
using the *image* facet of the control. It then creates a series of thumbnail
images in the FilmStripEditor using each of the different image filters
supported by AnImageResource object's *scale* method. The label for each
thumbnail is the name of the filter used to create it.

Finally, selecting any item in the FilmStripEditor by clicking on it will
display the corresponding screen capture image in the ImageZoomEditor at the
bottom of the view.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Event, List, Any, Image, View, VGroup, Item, \
           ControlGrabberEditor, FilmStripEditor, ImageZoomEditor

from facets.ui.filmstrip_adapter \
    import FilmStripAdapter

#-- Image filters supported by the AnImageResource 'scale' method --------------

image_filters = (
    'Bell', 'Box', 'CatmullRom', 'Cosine', 'CubicConvolution', 'CubicSpline',
    'Hermite', 'Lanczos3', 'Lanczos8', 'Mitchell', 'Quadratic',
    'QuadraticBSpline', 'Triangle'
)

#-- FSAdapter Class ------------------------------------------------------------

class FSAdapter ( FilmStripAdapter ):

    def get_image ( self, value ):
        return value[1]

    def get_label ( self, value ):
        return value[0]

#-- FilmStripDemo Class --------------------------------------------------------

class FilmStripDemo ( HasFacets ):

    # Facet definitions:
    control  = Event
    values   = List
    selected = Any
    image    = Image

    # Facet view definitions:
    view = View(
        VGroup(
            Item( 'control',
                  editor  = ControlGrabberEditor(),
                  tooltip = 'Drag this icon over another control and release.'
            ),
            Item( 'values',
                  height = -240,
                  editor = FilmStripEditor( adapter  = FSAdapter(),
                                            selected = 'selected' )
            ),
            '_',
            Item( 'image',
                  editor = ImageZoomEditor( channel = 'hue' )
            ),
            show_labels = False
        )
    )

    # Facet Event Handlers -----------------------------------------------------

    def _control_set ( self, control ):
        if control is not None:
            image       = control.image
            self.values = [ ( filter, image.scale( 0.25, filter ) )
                            for filter in image_filters ]

    def _selected_set ( self, selected ):
        if selected is not None:
            self.image = selected[1]

#-- Create The Demo ------------------------------------------------------------

demo = FilmStripDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
