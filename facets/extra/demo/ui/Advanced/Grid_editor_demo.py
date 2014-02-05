"""
# GridEditor Demo #

This example defines three classes:

- **Person**: A single person.
- **MarriedPerson**: A married person (subclass of Person).
- **Report**: Defines a report based on a list of single and married people.

It creates a grid display of 10,000 single and married people showing the
following information:

- Name of the person.
- Age of the person.
- The person's address.
- The name of the person's spouse (if any).

In addition:

- It uses a Courier 10 point font for each line in the table.
- It displays age column right, instead of left, justified.
- If the person is a minor (age < 18) and married, it displays a red flag image
  in the age column.
- If the person is married, it makes the background color for that row a light
  blue.

This example demonstrates:

- How to set up a **GridEditor**.
- The display speed of the **GridEditor**.
- How to create a **GridAdapter** that meets each of the specified display
  requirements.

Additional notes:

- You can change the current selection using the up and down arrow keys.
- You can move a selected row up and down in the table using the left and right
  arrow keys.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from random \
    import randint, choice, shuffle

from facets.api \
    import HasFacets, Str, Int, Float, List, Instance, Property, Tuple, Enum, \
           Color, ATheme, Image, Event, Bool, Callable, implements,           \
           on_facet_set, View, HGroup, VGroup, VSplit, Item, GridEditor,      \
           RangeSliderEditor, MultipleInstanceEditor, property_depends_on

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.i_filter \
    import IFilter, Filter

#-- Person Class Definition ----------------------------------------------------

class Person ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    name    = Str
    address = Str
    age     = Int
    color   = Color( 'red' )
    color2  = Color( 'white' )
    gender  = Enum( 'Male', 'Female' )

    #-- Facets View Definitions ------------------------------------------------

    view = View( 'name', 'address', 'age', 'gender' )

#-- MarriedPerson Class Definition ---------------------------------------------

class MarriedPerson ( Person ):

    partner = Instance( Person )

#-- PersonFilter Definition ----------------------------------------------------

class PersonFilter ( Person ):

    implements( IFilter )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'name', label = 'Filter by name' )
    )

    #-- IFilter Interface Implementation ---------------------------------------

    # Is the filter active?
    active = Property

    # Event fired when the filter criteria dfined by the filter has changed
    # (Thus necessitating that the filter be reapplied to all objects):
    changed = Event

    #-- Interface Methods ------------------------------------------------------

    def filter ( self, object ):
        """ Returns True if object is accepted by the filter, and False if it is
            not.
        """
        return (object.name.lower().find( self.name.strip().lower() ) >= 0)

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'name' )
    def _filter_modified ( self ):
        self.changed = True

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'name' )
    def _get_active ( self ):
        return (self.name != '')

#-- PersonSearch Definition ----------------------------------------------------

class PersonSearch ( Filter ):

    #-- Facet Definitions ------------------------------------------------------

    # The range of ages to include in the search:
    ages = Tuple( 10, 14 )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HGroup(
            Item( 'active', label  = 'Select by age range' ),
            Item( 'ages',
                  show_label = False,
                  editor     = RangeSliderEditor( low = 10, high = 90,
                                                  body_style = 25 )
            )
        )
    )

    #-- Interface Methods ------------------------------------------------------

    def filter ( self, object ):
        """ Returns True if object is accepted by the filter, and False if it is
            not.
        """
        return (self.ages[0] <= object.age <= self.ages[1])

#-- Name sorter ----------------------------------------------------------------

def name_cmp ( l, r ):
    """ Sorts the 'name' field of an object by last name then first name.
    """
    wl = l.name.split()
    wr = r.name.split()

    if len( wl ) == 0:
        return -1

    if len( wr ) == 0:
        return 1

    return (cmp( wl[-1].lower(), wr[-1].lower() ) or
            cmp( wl[ 0].lower(), wr[ 0].lower() ))

#-- Custom Cell Renderer -------------------------------------------------------

def painter ( cell ):
    g = cell.graphics
    if cell.selected:
        g.brush = ( 0, 0, 192 )
    else:
        g.brush = ( 192, 0, 0 )
    g.pen = None
    g.draw_rectangle( cell.x, cell.y, cell.width, cell.height )

#-- Grid Adapter Definition ----------------------------------------------------

class ReportAdapter ( GridAdapter ):

    columns = [ ( 'Name',    'name'    ),
                ( 'Age',     'age'     ),
                ( 'Gender',  'gender'  ),
                ( 'C1',      'color'   ),
                ( 'C2',      'color2'  ),
                ( 'Address', 'address' ),
                ( 'Spouse',  'spouse'  )
    ]

    default_value              = Person
    font                       = 'Courier 10'
    column_font                = 'Courier 8'
    age_alignment              = Str( 'right' )
    name_sorter                = Callable( name_cmp )
    spouse_sortable            = Bool( False )
    spouse_can_edit            = Bool( False )
    Person_spouse_text         = Str( '' )
    MarriedPerson_bg_color     = Color( 0xF6F2E9 )
    gender_alignment           = Str( 'center' )
    gender_clicked             = Bool( True )
    color_width                = Float( 30 )
    color_paint                = Str( 'Color' )
    color_clicked              = Str( 'edit' )
    color2_width               = Float( 30 )
    color2_paint               = Str( 'Color' )
    color2_clicked             = Str( 'popup' )
    search_address             = Property
    selected_bg_color          = 0xC8E0FF
    selected_text_color        = 0x202020
    grid_color                 = 0x505050
    #MarriedPerson_spouse_paint = Callable( painter )

    #-- Theme Related Facets (Uncomment to see a themed demo) ------------------
    #address_theme              = Property
    #gender_theme               = Property
    #spouse_theme               = ATheme( '@cells:bg' )
    #spouse_selected_theme      = ATheme( '@cells:bg' )
    #MarriedPerson_spouse_theme = ATheme( '@cells:lg' )
    #MarriedPerson_spouse_selected_theme = ATheme( '@cells:lj' )
    #selected_theme             = '@cells:lj'
    #theme                      = '@cells:lg'
    #name_selected_image        = Image( '@icons:bullet' )
    #grid_visible               = False
    #-- End of Theme Related Facets --------------------------------------------

    def MarriedPerson_age_image ( self ):
        return (( None, '@icons:dot2' )[ self.item.age < 18 ])

    def MarriedPerson_spouse_text ( self ):
        return self.item.partner.name

    def address_image ( self ):
        search_address = self.search_address.strip()
        if ((search_address != '') and
            (self.item.address.lower().find( search_address.lower() ) >= 0)):
            return '@icons:bullet'

        return None

    def gender_bg_color ( self ):
        return (( 0xFEE1E1, 0xD6F6FD )[ self.item.gender == 'Male' ])

    #-- Property Implementations -----------------------------------------------

    def _get_address_theme ( self ):
        search_address = self.search_address.strip()
        if ((search_address != '') and
            (self.item.address.lower().find( search_address.lower() ) >= 0)):
            return '@cells:lo'

        return '@cells:lg'

    def _get_gender_theme ( self ):
        return (( '@cells:lr', '@cells:lb' )[ self.item.gender == 'Male' ])

    @property_depends_on( 'object:address' )
    def _get_search_address ( self ):
        return self.object.address

    @on_facet_set( 'object:address' )
    def _search_address_modified ( self ):
        self.refresh = True

    #-- Adapter Methods --------------------------------------------------------

    def column_clicked ( self ):
        self._count  = (self._count or 0) + 1
        self.refresh = True


    def name_title ( self ):
        if self._count is None:
            return 'Name'

        return ('Name [%d]' % self._count)


    def column_double_clicked ( self ):
        print self.column, 'double clicked'

#-- Grid Editor Definitions ----------------------------------------------------

grid_editor = GridEditor(
    selection_mode = 'rows',
    monitor        = 'all',
    selected       = 'selected',
    adapter        = ReportAdapter,
    filter         = 'filter',
    search         = 'search',
    #operations     = [ 'edit', 'append', 'insert', 'delete', 'move', 'sort' ],
    operations     = [ 'edit', 'append', 'insert', 'delete', 'move' ],
)

selection_editor = GridEditor(
    adapter    = ReportAdapter,
    operations = [ 'move' ],
)

#-- Report Class Definition ----------------------------------------------------

class Report ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    people   = List( Person )
    selected = List( Person )
    filter   = Instance( PersonFilter, () )
    search   = Instance( PersonSearch, () )
    address  = Str

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'filter',  style = 'custom', show_label = False ),
                Item( 'search',  style = 'custom', show_label = False ),
                Item( 'address', label = 'Search for address' )
            ),
            '_',
            VSplit(
                Item( 'people',
                      id     = 'table',
                      editor = grid_editor
                ),
                Item( 'selected',
                      id     = 'selection',
                      editor = selection_editor
                ),
                Item( 'selected',
                      editor = MultipleInstanceEditor(),
                      height = 100
                ),
                show_labels = False,
                id          = 'splitter'
            )
        ),
        title     = 'Grid Editor Demo',
        id        = 'facets.extra.demo.ui.Advanced.grid_editor_demo',
        width     = 0.60,
        height    = 0.75,
        resizable = True
    )

#-- Generate 10,000 random single and married people ---------------------------

male_names = [ 'Michael', 'Edward', 'Timothy', 'James', 'George', 'Ralph',
    'David', 'Martin', 'Bryce', 'Richard', 'Eric', 'Travis', 'Robert', 'Bryan',
    'Alan', 'Harold', 'John', 'Stephen', 'Gael', 'Frederic', 'Eli', 'Scott',
    'Samuel', 'Alexander', 'Tobias', 'Sven', 'Peter', 'Albert', 'Thomas',
    'Horatio', 'Julius', 'Henry', 'Walter', 'Woodrow', 'Dylan', 'Elmer'
]

female_names = [ 'Leah', 'Jaya', 'Katrina', 'Vibha', 'Diane', 'Lisa', 'Jean',
    'Alice', 'Rebecca', 'Delia', 'Christine', 'Marie', 'Dorothy', 'Ellen',
    'Victoria', 'Elizabeth', 'Margaret', 'Joyce', 'Sally', 'Ethel', 'Esther',
    'Suzanne', 'Monica', 'Hortense', 'Samantha', 'Tabitha', 'Judith', 'Ariel',
    'Helen', 'Mary', 'Jane', 'Janet', 'Jennifer', 'Rita', 'Rena', 'Rianna'
]

male_name   = lambda: choice( male_names )
female_name = lambda: choice( female_names )
age         = lambda: randint( 15, 72 )

family_name = lambda: choice( [ 'Jones', 'Smith', 'Thompson', 'Hayes', 'Thomas',
    'Boyle', "O'Reilly", 'Lebowski', 'Lennon', 'Starr', 'McCartney', 'Harrison',
    'Harrelson', 'Steinbeck', 'Rand', 'Hemingway', 'Zhivago', 'Clemens',
    'Heinlien', 'Farmer', 'Niven', 'Van Vogt', 'Sturbridge', 'Washington',
    'Adams', 'Bush', 'Kennedy', 'Ford', 'Lincoln', 'Jackson', 'Johnson',
    'Eisenhower', 'Truman', 'Roosevelt', 'Wilson', 'Coolidge', 'Mack', 'Moon',
    'Monroe', 'Springsteen', 'Rigby', "O'Neil", 'Philips', 'Clinton',
    'Clapton', 'Santana', 'Midler', 'Flack', 'Conner', 'Bond', 'Seinfeld',
    'Costanza', 'Kramer', 'Falk', 'Moore', 'Cramdon', 'Baird', 'Baer',
    'Spears', 'Simmons', 'Roberts', 'Michaels', 'Stuart', 'Montague',
    'Miller'
] )

address = lambda: '%d %s %s' % ( randint( 11, 999 ), choice( [ 'Spring',
    'Summer', 'Moonlight', 'Winding', 'Windy', 'Whispering', 'Falling',
    'Roaring', 'Hummingbird', 'Mockingbird', 'Bluebird', 'Robin', 'Babbling',
    'Cedar', 'Pine', 'Ash', 'Maple', 'Oak', 'Birch', 'Cherry', 'Blossom',
    'Rosewood', 'Apple', 'Peach', 'Blackberry', 'Strawberry', 'Starlight',
    'Wilderness', 'Dappled', 'Beaver', 'Acorn', 'Pecan', 'Pheasant', 'Owl' ] ),
    choice( [ 'Way', 'Lane', 'Boulevard', 'Street', 'Drive', 'Circle',
    'Avenue', 'Trail'
] ) )

people = ([ Person( name    = '%s %s' % ( male_name(), family_name() ),
                    age     = age(),
                    gender  = 'Male',
                    address = address() )
            for i in range( 250 ) ] +
          [ Person( name    = '%s %s' % ( female_name(), family_name() ),
                    age     = age(),
                    gender  = 'Female',
                    address = address() )
            for i in range( 250 ) ])

marrieds = [ ( MarriedPerson( name    = '%s %s' % ( female_name(), last_name ),
                              age     = age(),
                              gender  = 'Female',
                              address = address ),
               MarriedPerson( name    = '%s %s' % ( male_name(), last_name ),
                              age     = age(),
                              gender  = 'Male',
                              address = address ) )
             for last_name, address in
                 [ ( family_name(), address() ) for i in range( 250 ) ] ]

for female, male in marrieds:
    female.partner = male
    male.partner   = female
    people.extend( [ female, male ] )

shuffle( people )

#-- Create the demo ------------------------------------------------------------

demo = Report( people = people )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------