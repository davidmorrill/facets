"""
# HistogramEditor Demo #

A few simple examples of using the **HistogramEditor** to display a series of
values in a histogram plot format.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Any, List, Button, View, HGroup, VSplit, UItem, \
           HistogramEditor, spring

from random \
     import random, randint

#-- HistogramEditorDemo class --------------------------------------------------

class HistogramEditorDemo ( HasFacets ):

    data1 = List
    data2 = List
    data3 = Any
    reset = Button( 'Reset' )

    view = View(
        VSplit(
            UItem( 'data1',
                   label  = 'Histogram 1',
                   editor = HistogramEditor(
                       title     = 'Animated Histogram',
                       subtitle  = '30 data points %s',
                       spacing   = 0.5,
                       bar_color = 0xFF5656,
                       animate   = True
                   ),
                   dock = 'tab'
            ),
            UItem( 'data2',
                   label  = 'Histogram 2',
                   editor = HistogramEditor(
                       title   = 'Normal Histogram',
                       spacing = 0.15,
                       x_units = ' px',
                       y_units = '%'
                   ),
                   dock = 'tab'
            ),
            UItem( 'data3',
                   label  = 'Histogram 3',
                   editor = HistogramEditor(
                       spacing      = -1.5,
                       bar_color    = 0xFACA0A,
                       bg_color     = 0x606060,
                       label_color  = 0xFFFFFF,
                       format_str   = '%0.2f',
                       show_tooltip = False,
                       show_cursor  = False,
                       animate      = True
                  ),
                   dock = 'tab'
            ),
            id = 'splitter'
        ),
        HGroup( spring, UItem( 'reset' ) ),
        title  = 'HistogramEditor Demo',
        id     = 'facets.extra.demo.ui.Graphics_and_Animation.'
                 'HistogramEditor_demo.HistogramDemo',
        width  = 0.50,
        height = 0.67
    )

    def _data1_default ( self ):
        return [ randint( 1, 100 ) for i in xrange( 30 ) ]

    def _data2_default ( self ):
        return [ 2500.0 * random() for i in xrange( 15 ) ]

    def _data3_default ( self ):
        import numpy

        return numpy.histogram( numpy.random.random( 10000 ), 25 )

    def _reset_set ( self ):
        del self.data1
        del self.data2
        del self.data3

#-- Create the demo ------------------------------------------------------------

demo = HistogramEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------