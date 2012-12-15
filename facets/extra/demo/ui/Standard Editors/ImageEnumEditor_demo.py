"""
Implementation of an ImageEnumEditor demo plugin for the Facets UI demo program.

This demo shows each of the four styles of the ImageEnumEditor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Str, Facet

from facets.api \
    import Item, Group, View, ImageEnumEditor

#-- Constants ------------------------------------------------------------------

# This list of image names (with the standard suffix "_origin") is used to
# construct an image enumeration facet to demonstrate the ImageEnumEditor:
image_list = [ 'top_left', 'top_right', 'bottom_left', 'bottom_right' ]

#-- Dummy Class ----------------------------------------------------------------

class Dummy ( HasFacets ):
    """ Dummy class for ImageEnumEditor
    """
    x = Str

    view = View()

#-- ImageEnumEditorDemo Class --------------------------------------------------

class ImageEnumEditorDemo ( HasFacets ):
    """ Defines the ImageEnumEditor demo class.
    """

    # Define a facet to view:
    image_from_list = Facet( editor = ImageEnumEditor(
            values = image_list,
            prefix = '@icons:',
            suffix = '_origin',
            cols   = 4,
            klass  = Dummy
        ),
        *image_list
    )

    # Items are used to define the demo display, one Item per editor style:
    img_group = Group(
        Item( 'image_from_list', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'image_from_list', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'image_from_list', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'image_from_list', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        img_group,
        title     = 'ImageEnumEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = ImageEnumEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------