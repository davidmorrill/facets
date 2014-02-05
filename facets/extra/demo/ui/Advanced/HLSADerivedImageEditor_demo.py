"""
# HLSADerivedImageEditor Demo #

Demonstrates the **HLSADerivedImageEditor**, which allows you to interactively
set the mask and transform values for an **HLSADerivedImage** object.

An HLSADerivedImage is an **AnImageResource** image object that is derived from
a base AnImageResource image object by means of an **HLSAMask** color mask
object, and two **HLSATransform** color transform objects, one of which is
applied to the masked portion of the base image, and the other to the unmasked
part of the base image.

The net result is a new image, derived from the base image, which can have
completely different colors (i.e. Hues), Saturation, Lightness and Alpha values
applied to it (hence the name HLSADerivedImage). In practice, this allows an
application to create a wide variety of useful icons, images or themes all
derived from a single, base image (often stored in a Facets image library).

The Facets package provides an easy means for an application to create
HLSADerivedImage objects when needed using a simple string encoding technique.
This string encoding technique can be used anywhere an Image facet is used.

For example, given the class:

    class MyImage ( HasFacets ):
        image = Image

we can create a normal AnImageResource value for 'image' using:

    MyImage( image = '@xform:b6td' )

which assigns an image called *'b6td'* loaded from the standard Facets *xform*
image library. We could also write:

    MyImage( image = '@xform:b6td?H61S25~H61L12S31|L56' )

whichs assigns an HLSADerivedImage derived from the same *b6td* image with the
mask and transforms encoded in the string *'/H61S25~H61L12S27|L56'* applied to
it. In practice, understanding the encoded string contents is not important,
since this is what the HLSADerivedImageEditor helps you create automatically.

Any time you modify the contents of an HLSADerivedImageEditor, it copies the
string encoding of the current mask and transform values into the system
clipboard for easy pasting into your favorite text editor.

The demo is set up to use the same *'@xform:b6td'* library image we used in the
previous examples as the base image supplied to the HLSADerivedImageEditor. To
get a feel for how the editor works, try the following series of steps:

- Set the Unmasked Transform Saturation value to 0.25. You should notice that
  the bottom image now has a reddish tinge. By increasing the saturation of a
  basically grey scale image, we have in effect *injected* some color into the
  base image. Useful hint: increasing saturation on a grey scale image will
  always give it a reddish cast. This is due to the math used in the color
  space conversions. Any shade of grey, which basically has no hue, will be
  assigned (somewhat arbitrarilly) a hue value of 0, which in HLS math is the
  hue value for red. Hence the reddish cast that appears as saturation is
  increased.

- Set the Unmasked Transform Hue value to 0.61. We see that the bottom image
  now has nice shades of blue. By changing the hue value we have effectively
  changed the color of all pixels in the base image. The darker shades of grey
  become darker shades of blue, and the lighter greys become lighter blues.
  Up to now, all hue and saturation changes have been applied to all pixels in
  the base image. In the next step, we'll see how we can apply the changes to
  only a portion of the image by using a mask.

- Set the Mask Lightness value to 0.56. At this point we have now applied a
  mask based on the lightness value of each pixel in the base image. All base
  image pixels whose lightness value are in the range from 0.0 to 0.56 are now
  *masked* (meaning they are not affected by the Unmasked Transform values).
  You can see the mask better by zooming into the topmost image using the mouse
  wheel (i.e. place the mouse pointer over the image and scroll the mouse wheel
  upward). As you zoom in, you will see a checkboard pattern emerge in those
  portions of the image which are affected by the mask. If you look at the
  bottom image, you will see that the bottom portion of the image, which had
  turned light blue in the previous set, has now returned to its original
  light grey color, since the mask is preventing those pixels from being
  affected by the Unmasked Transform values.

- Set the Masked Transform Saturation value to 0.31. As in the first step,
  this adds a reddish cast, but only to the bottom part of the image, since
  the Masked Transform only affects those pixels which are *masked*.

- Set the Masked Transform Hue value to 0.61, This reapplies the same blue
  color we had set previously back to the masked pixels.

- Set the Masked Transform Lightness value to 0.12. This lightens the blue
  color of the bottom portion of the image, creating a nice two-tone color
  effect for the entire bottom image.

You'll notice as you perform the preceding steps that the Encoded field in the
bottom left corner of the view updates as you make changes. This value
represents the encoded value of the Mask, UmaskedTransform and Masked Transform
values shown in the editor. If you look closely enough, you can probably get a
good idea of how the encoding is performed.

At this point you also might want to switch over to a text editor and do a paste
operation, which inserts the same value shown in the *Encoded* field. This can
be handy when you are using the HLSADerivedImageEditor to customize an image and
you want to copy the image encoding into your source code.

If you are feeling really adventurous, you can try making changes to the
*Encoded* value directly. Strings which are legal encodings will result in the
HLSADerivedImageEditor being updated accordingly.

Hopefully, this provides some insight into how useful the HLSADerivedImageEditor
can be for creating custom images, icons and themes from shared base image
library assets, such as the ones provided with the Facets package, or ones you
create yourself. If interested, you may also want to look into the
ImageTransformer tool, provided in the *facets.extra.tools.image_transformer*
module, which uses the HLSADerivedImageEditor and allows you to specify the
base image to use with the editor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Image, Color, SyncValue, Theme, View, VGroup, \
           HGroup, Item, HLSColorEditor

from facets.extra.editors.hlsa_derived_image_editor \
    import HLSADerivedImageEditor

#-- Demo Class -----------------------------------------------------------------

class HLSADerivedImageEditorDemo ( HasFacets ):

    # The base image:
    image = Image( '@xform:b6td' )

    # The background color used with the editor:
    bg_color = Color( 0x303030 )

    # The current encoding of the derived image:
    encoded = Str

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                Item( 'image',
                      id     = 'image',
                      editor = HLSADerivedImageEditor(
                          bg_color = SyncValue( self, 'bg_color' ),
                          encoded  = 'encoded' )
                ),
                HGroup(
                    Item( 'encoded', width = 0.25 ),
                    '_',
                    Item( 'bg_color',
                          show_label = False,
                          editor     = HLSColorEditor( edit = 'lightness' ),
                          width      = 0.75,
                    ),
                    group_theme = Theme( '@xform:b?L30', content = 1 )
                ),
                show_labels = False
            ),
            title = 'HLSADerivedImageEditor Demo',
            id    = 'facets.extra.demo.ui.Advanced.HLSADerivedImageEditor_demo',
            width     = 0.50,
            height    = 0.75,
            resizable = True
        )

#-- Create the demo ------------------------------------------------------------

demo = HLSADerivedImageEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
