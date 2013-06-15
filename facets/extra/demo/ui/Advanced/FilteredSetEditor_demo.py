"""
Demonstrates use of the FilteredSetEditor. A FilteredSetEditor is based on the
SetEditor, but adds an end user specified match string and ordering criteria
to help organize the presentation and selection of set items.

This can be useful in cases where the number of available set items is large,
which can make selecting items using the normal SetEditor tedious. By using the
FilteredSetEditor and specifying appropriate match criteria, the user can
usually move the desired items to the top of the editor list, making selection
easier.

The editor has a number of supported customizations, including the ability to
specify a custom key function that can tailor the matching process to the
application. The demo illustrates this by using a custom 'test_key' function
which ranks matches in the last name higher than matches in the first name.

The user can also exclude matching items by changing the ordering criteria for
matches from 'First' to 'Last'. When set to 'Last', set items are displayed in
reverse order, placing matching items after non-matching items.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, View, UItem, FilteredSetEditor

#-- Custom match function ------------------------------------------------------

def test_key ( filter, item ):
    if filter == '':
        return 0

    filter = filter.lower()
    cols   = [ name.find( filter ) for name in item.lower().split() ]

    return (((cols[1] if cols[1] >= 0 else 9999) * 10000) +
             (cols[0] if cols[0] >= 0 else 9999))

#-- FilteredSetEditorDemo class ------------------------------------------------

class FilteredSetEditorDemo ( HasFacets ):

    values = List
    items  = List

    def default_facets_view ( self ):
        return View(
            UItem( 'items',
                   editor = FilteredSetEditor(
                       values = self.values,
                       key    = test_key
                   )
            ),
            title  = 'FilteredSetEditor Test',
            width  = 200,
            height = 0.8
        )

    def _values_default ( self ):
        result = []
        firsts = [ 'David', 'Diane', 'Dwight', 'Duane', 'John', 'Tim', 'Tammy',
                   'William', 'Wilbur' ]
        lasts  = [ 'Johnson', 'Taylor', 'Smith', 'Jones', 'Jarvis', 'Simmons' ]
        for first in firsts:
            for last in lasts:
                result.append( '%s %s' % ( first, last ) )

        return result

#-- Create the demo ------------------------------------------------------------

demo = FilteredSetEditorDemo

#-- Run the demo (if invoked form the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------