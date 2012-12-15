#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Range, Enum, Bool, Tuple, Tuple, Property, View, VGroup, \
           Item, RangeEditor, RangeSliderEditor, SyncValue, property_depends_on

#-------------------------------------------------------------------------------
#  'RangeSliderEditorDemo' class:
#-------------------------------------------------------------------------------

custom_slider_editor = RangeEditor( body_style = 25 )

class RangeSliderEditorDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The lowest/highest values the 'value' facet can take:
    low_high = Tuple( ( 0.0, 10.0 ) )

    # The low end of the slider range:
    low = Property

    # The high end of the slider range:
    high = Property

    # The smallest allowed increment:
    increment = Enum( 0.1, 0.01, 1.0 )

    # Is the range locked to a fixed size?
    range_locked = Bool( False )

    # The minimum/maximum size of the range for the 'value' facet:
    min_max_range = Tuple( ( 0.0, 10.0 ) )

    # The minimum value for the range:
    min_range = Property

    # The maximum value for the range:
    max_range = Property

    # Where should the high/low values be displayed:
    show_ends = Enum( 'Tip', 'Body', 'None' )

    # Where should the range be displayed:
    show_range = Enum( 'None', 'Body' )

    # The style to use for the slider tips:
    tip_style = Range( 1, 30, facet_value = True )

    # The style to use for the slider body:
    body_style = Range( 0, 30, facet_value = True )

    # The style to use for the slider track:
    track_style = Range( 1, 15, facet_value = True )

    # Is the range slider enabled or not?
    enabled = Bool( True )

    # The actual value being edited:
    value = Tuple( ( 1.0, 5.0 ) )

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
                          body_style = 25 )
                ),
                Item( 'increment' ),
                label       = 'Range Bounds',
                show_border = True
            ),
            VGroup(
                Item( 'range_locked' ),
                Item( 'min_max_range',
                      editor = RangeSliderEditor(
                          low        = 0.0,
                          high       = 30.0,
                          increment  = 0.1,
                          body_style = 25
                      )
                ),
                label       = 'Range Mode',
                show_border = True
            ),
            VGroup(
                Item( 'show_ends' ),
                Item( 'show_range' ),
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
                      enabled_when = 'enabled',
                      editor       = RangeSliderEditor(
                          low          = SyncValue( self, 'low' ),
                          high         = SyncValue( self, 'high' ),
                          increment    = SyncValue( self, 'increment' ),
                          range_locked = SyncValue( self, 'range_locked' ),
                          min_range    = SyncValue( self, 'min_range' ),
                          max_range    = SyncValue( self, 'max_range' ),
                          show_ends    = SyncValue( self, 'show_ends' ),
                          show_range   = SyncValue( self, 'show_range' ),
                          tip_style    = SyncValue( self, 'tip_style' ),
                          body_style   = SyncValue( self, 'body_style' ),
                          track_style  = SyncValue( self, 'track_style' ) )
                ),
                label       = 'RangeSliderEditor',
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

    @property_depends_on( 'min_max_range' )
    def _get_min_range ( self ):
        return self.min_max_range[0]

    @property_depends_on( 'min_max_range' )
    def _get_max_range ( self ):
        return self.min_max_range[1]

#-- Create a demo --------------------------------------------------------------

demo = RangeSliderEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------