#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Range, Enum, Bool, Tuple, Float, Tuple, Property, View, \
           VGroup, Item, RangeEditor, RangeSliderEditor, SyncValue, \
           property_depends_on

#-------------------------------------------------------------------------------
#  'RangeEditorDemo' class:
#-------------------------------------------------------------------------------

custom_slider_editor = RangeEditor( body_style = 25 )

class RangeEditorDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The lowest/highest values the 'value' facet can take:
    low_high = Tuple( ( 0.0, 10.0 ) )

    # The low end of the slider range:
    low = Property

    # The high end of the slider range:
    high = Property

    # The smallest allowed increment:
    increment = Enum( 0.1, 0.01, 1.0 )

    # Where should the value be displayed:
    show_value = Enum( 'Tip', 'Body', 'None' )

    # The style to use for the slider tips:
    tip_style = Range( 1, 30, facet_value = True )

    # The style to use for the slider body:
    body_style = Range( 0, 30, facet_value = True )

    # The style to use for the slider track:
    track_style = Range( 1, 15, facet_value = True )

    # Is the slider enabled or not?
    enabled = Bool( True )

    # The actual value being edited:
    value = Float( 1.0 )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        """ Return the view to display.
        """
        return View(
            VGroup(
                Item( 'low_high',
                      editor = RangeSliderEditor(
                          low        = -10.0,
                          high       = 20.0,
                          increment  = 0.1,
                          min_range  = 0.1,
                          body_style = 25 )
                ),
                Item( 'increment' ),
                label       = 'Slider Bounds',
                show_border = True
            ),
            VGroup(
                Item( 'show_value' ),
                label       = 'Text Display',
                show_border = True
            ),
            VGroup(
                Item( 'tip_style',   editor = custom_slider_editor ),
                Item( 'body_style',  editor = custom_slider_editor ),
                Item( 'track_style', editor = custom_slider_editor ),
                label       = 'Slider Style',
                show_border = True
            ),
            VGroup(
                Item( 'enabled' ),
                show_border = True
            ),
            VGroup(
                Item( 'value',
                      label        = 'Normal',
                      enabled_when = 'enabled',
                      editor       = RangeEditor(
                          label_width  = 50,
                          low          = SyncValue( self, 'low' ),
                          high         = SyncValue( self, 'high' ),
                          increment    = SyncValue( self, 'increment' ),
                          show_value   = SyncValue( self, 'show_value' ),
                          tip_style    = SyncValue( self, 'tip_style' ),
                          body_style   = SyncValue( self, 'body_style' ),
                          track_style  = SyncValue( self, 'track_style' )
                      )
                ),
                Item( 'value',
                      label        = 'Readonly',
                      style        = 'readonly',
                      enabled_when = 'enabled',
                      editor       = RangeEditor(
                          label_width  = 50,
                          low          = SyncValue( self, 'low' ),
                          high         = SyncValue( self, 'high' ),
                          increment    = SyncValue( self, 'increment' ),
                          show_value   = SyncValue( self, 'show_value' ),
                          tip_style    = SyncValue( self, 'tip_style' ),
                          body_style   = SyncValue( self, 'body_style' ),
                          track_style  = SyncValue( self, 'track_style' )
                      )
                ),
                label       = 'RangeEditor',
                show_border = True
            )
        )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'low_high' )
    def _get_low ( self ):
        return self.low_high[0]

    @property_depends_on( 'low_high' )
    def _get_high ( self ):
        return self.low_high[1]

#-- Create a demo --------------------------------------------------------------

demo = RangeEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------