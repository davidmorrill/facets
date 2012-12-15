"""
Demonstrates how to define a GridAdapter that automatically supports filtering
and searching GridEditor column values using the <i>auto_filter</i> and
<i>auto_search</i> adapter attributes.

In this demo, we use a GridEditor to display a list of Person objects with
four columns:
 - First name (has column auto-filter)
 - Last name (has both column auto-filter and auto-search)
 - Age (has column auto-filter)
 - Gender (has column auto-search)

A grid column that only supports auto-filter is indicated by a filter icon that
appears to the left of the label in the grid column header. In this case, the
first and third columns only support auto-filter.

A grid column that only supports auto-search is indicated by a search icon that
appears to the left of the label in the grid column header. In this case, the
Gender column onlys support auto-search.

Auto-filter is enabled for a column by making its 'auto_filter' attribute True
(the default is False). For this demo, we turn on auto-filter for all columns
using the following definition in the PersonAdapter class:

  auto_filter = Bool( True )

We override this default value and turn off auto-filter for the Gender column
using the definition:

  gender_auto_column = Bool( False )

Auto-search is enabled for a column by making its 'auto_search' attribute True
(the default is False). For this demo, we turn on auto-search for both the
Gender and Last columns with the definitions:

  gender_auto_search = Bool( True )
  last_auto_search   = Bool( True )

Any column can support auto-filter, auto-search or both. If both auto-filter and
auto-search are enabled for a particular column, a question mark column icon is
displayed (refer to the Last column in the demo), and the pop-up contains both
filter and search fields.

A column with auto-filter or auto-search enabled can be in one of two states:
 - <b>Inactive</b>: The icon is dimmed and no filtering or searching is
    performed.
 - <b>Active</b>: The icon is bright and the current filter appears in square
   brackets to the right of the column label (e.g. 'Age [>40]'). In the case of
   a search, the current search string appears in parenthesis (e.g.
   'Gender (f)').

If auto-filter or auto-search is enabled for a column,, clicking its column
header displays a pop-up text entry field where you can enter your filter or
search text. Moving the mouse away from the text entry field closes the pop-up.

The text entered into the filter or search text pop-up can be preceded with one
of the following optional filter operators:
 - <b>=</b> (equals)
 - <b>!=</b> (not equals)
 - <b><</b> (less than)
 - <b><=</b> (less than or equal to)
 - <b>></b> (greater than)
 - <b>>=</b> (greater than or equal to)
 - <b>!</b> (does not contain)

If the filter or search string does not start with one of these operators, the
default <i>contains</i> operator is used.

You can also define a range of values to check for by separating the low and
high ends of the range by '..' (e.g. '10..20' means all values between 10 and
20). If the first character of the text is '!', the test becomes <i>not in
range</i> (e.g. '!10..20' means all values not in the range from 10 to 20).

Text comparisons can be either case sensitive or case insensitive. You change
the style of comparison by clicking the icon to the left of the text field. You
can also clear the contents of the text field by clicking the filter or search
icon at the beginning of the line.

If a grid cell value is numeric, the comparison is performed using the numeric
value of the filter or search text (or 0.0 if the text does not form a valid
number). The 'contains' and 'does not contain' operators are treated as 'equals'
and 'not equals' for numeric grid cell values.

For example, if you click the Age column header and enter '>40' into the
filter pop-up text field, the grid only displays rows where the 'age' value is
greater than 40. If you click the header again, then click the pop-up's filter
icon, the filter is cleared and all rows are displayed.

Each column can have an active filter or search. If this occurs, a row is
displayed only if the filter is satisfied for each column with an active filter.
Similarly, a row is selected only if the search is satisfied for each column
with an active search.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from random \
    import randint, choice

from facets.api \
    import HasFacets, Str, Range, List, Bool, Enum, View, Item, GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- PersonAdapter Class --------------------------------------------------------

class PersonAdapter ( GridAdapter ):

    columns = [ ( 'First Name', 'first'  ),
                ( 'Last Name',  'last'   ),
                ( 'Age',        'age'    ),
                ( 'Gender',     'gender' ) ]

    auto_filter        = Bool( True )  # 'auto_filter = True' would also be OK
    gender_auto_filter = Bool( False )
    gender_auto_search = Bool( True )
    last_auto_search   = Bool( True )

#-- Person Class ---------------------------------------------------------------

class Person ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    first_name = Str
    last_name  = Str
    age        = Range( 0, 99 )
    gender     = Enum( 'Male', 'Female' )

#-- Demo Class -----------------------------------------------------------------

class Demo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    people   = List
    selected = List

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'people',
              show_label = False,
              editor     = GridEditor(
                  adapter        = PersonAdapter,
                  operations     = [],
                  selection_mode = 'rows',
                  selected       = 'selected' )
        ),
        title  = 'GridAdapter AutoFilter Demo',
        id     = 'facets.extra.demo.ui.Advanced.GridAdapter_auto_filter_demo',
        width  = 0.5,
        height = 0.5,
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

first_names = [
    'Michael', 'Edward', 'Timothy', 'James', 'George', 'Ralph',
    'David', 'Martin', 'Bryce', 'Richard', 'Eric', 'Travis', 'Robert', 'Bryan',
    'Alan', 'Harold', 'John', 'Stephen', 'Gael', 'Frederic', 'Eli', 'Scott',
    'Samuel', 'Alexander', 'Tobias', 'Sven', 'Peter', 'Albert', 'Thomas',
    'Horatio', 'Julius', 'Henry', 'Walter', 'Woodrow', 'Dylan', 'Elmer', 'Leah',
    'Jaya', 'Katrina', 'Vibha', 'Diane', 'Lisa', 'Jean', 'Alice', 'Rebecca',
    'Delia', 'Christine', 'Marie', 'Dorothy', 'Ellen', 'Victoria', 'Elizabeth',
    'Margaret', 'Joyce', 'Sally', 'Ethel', 'Esther', 'Suzanne', 'Monica',
    'Hortense', 'Samantha', 'Tabitha', 'Judith', 'Ariel', 'Helen', 'Mary',
    'Jane', 'Janet', 'Jennifer', 'Rita', 'Rena', 'Rianna'
]

last_names = [
    'Jones', 'Smith', 'Thompson', 'Hayes', 'Thomas', 'Boyle', "O'Reilly",
    'Lebowski', 'Lennon', 'Starr', 'McCartney', 'Harrison', 'Harrelson',
    'Steinbeck', 'Rand', 'Hemingway', 'Zhivago', 'Clemens', 'Heinlien',
    'Farmer', 'Niven', 'Van Vogt', 'Sturbridge', 'Washington', 'Adams', 'Bush',
    'Kennedy', 'Ford', 'Lincoln', 'Jackson', 'Johnson', 'Eisenhower', 'Truman',
    'Roosevelt', 'Wilson', 'Coolidge', 'Mack', 'Moon', 'Monroe', 'Springsteen',
    'Rigby', "O'Neil", 'Philips', 'Clinton', 'Clapton', 'Santana', 'Midler',
    'Flack', 'Conner', 'Bond', 'Seinfeld', 'Costanza', 'Kramer', 'Falk',
    'Moore', 'Cramdon', 'Baird', 'Baer', 'Spears', 'Simmons', 'Roberts',
    'Michaels', 'Stuart', 'Montague', 'Miller'
]

def random_person ( ):
    return Person(
        first  = choice( first_names ),
        last   = choice( last_names  ),
        age    = randint( 0, 99 ),
        gender = choice( [ 'Male', 'Female' ] )
    )
    
#-- Create the demo ------------------------------------------------------------

demo = Demo( people = [ random_person() for i in xrange( 200 ) ] )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------
