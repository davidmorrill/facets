"""
# ImageEnumEditor Demo #

This examples demonstrates using the various styles of the **ImageEnumEditor**,
which allows a user to select a facet value from a finite set of legal values.
This is simiar to the **EnumEditor**, but allows the user to select values using
images representing each legal value rather than text.

For example, if the legal facet values are *"up"*, *"down"*, *"left"* and
*"right"*, the images displayed by the editor might be arrows pointing in each
of the four valid directions.
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