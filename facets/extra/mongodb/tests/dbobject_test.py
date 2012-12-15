"""
Defines a test case for exercising the capabilities of the MongoDB database
support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from time \
    import time

from facets.extra.mongodb.api \
    import mongodb, MongoDBObject

from test_objects \
    import DBPerson, DBPatient, DBFriend, DBPainter, DBPalette, DBColor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Number of each objects of each type to create:
n = 3

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def save ( message = 'Update' ):
    now = time()
    n   = mongodb().save()
    delta = time() - now
    print '%-7s: %.3f seconds total (%d objects, %d us each)' % (
          message, delta, n, int( round( (1000000.0 * delta) / max( n, 1 ) ) ) )
    now = time()


def fetch ( klass ):
    if isinstance( klass, MongoDBObject ):
        object = klass.load()
        klass  = klass.__class__
    else:
        object = klass.fetch()

    show( object, klass )

    return object


def show ( object, klass = None ):
    if klass is None:
        klass = object.__class__

    print '--------------------------------------------------------------------'
    print '%s: %s' % ( klass.__name__[2:], object )
    if object is not None:
        dic   = object.__dict__
        names = [ name for name in dic.iterkeys()
                       if not name.startswith( '__' ) ]
        names.sort()
        for name in names:
            print '   %-15s = %s' % ( name, dic[ name ] )


def query ( klass, query, limit = 0, skip = 0, sort = None ):
    print "-- %s( %s ) ---------------------------------------" % (
          klass.__name__, query )

    for object in klass().all( query, limit = limit, skip = skip, sort = sort ):
        show( object )
    print '--------------------------------------------------------------------'
    print


def query_large ( klass, query ):
    now     = time()
    objects = klass().all( query )
    delta   = time() - now
    n       = len( objects )
    print '%4d results in %.3f seconds (%d usecs each) for %s(%s)' % (
          n, delta, int( round( (delta * 1000000) / n ) ), klass.__name__,
          query )


def dump_cache ( ):
    print 'cache ----------------------------------------------'
    for key in mongodb().cache.keys(): print key
    print '----------------------------------------------------'

#-------------------------------------------------------------------------------
#  Test functions:
#-------------------------------------------------------------------------------

def create_db ( ):
    global n

    # Reset the database:
    mongodb().reset()

    # Creates some colors:
    colors = [ DBColor( red = i, green = i, blue = i ).save()
               for i in xrange( 5 ) ]

    # Create some objects:
    objects = []
    for i in xrange( 1, n + 1 ):
        objects.append(
            DBPalette( name     = 'Palette %d' % i,
                       colors   = colors,
                       favorite = DBColor( red   =  i      % 256,
                                           green = (i + 2) % 256,
                                           blue  = (i + 4) % 256 ),
                       favorites = [ DBColor( red   =  i      % 256,
                                              green = (i + 3) % 256,
                                              blue  = (i + 6) % 256 ),
                                     DBColor( red   =  i      % 256,
                                              green = (i + 4) % 256,
                                              blue  = (i + 8) % 256 ) ]
            )
        )

        objects.append(
            DBPerson(
                name = 'Person %d' % i
            )
        )

        objects.append(
            DBPatient(
                name   = 'Patient %d' % i,
                age    = 20 + i,
                weight = 120.0 + (5 * i)
            )
        )

        objects.append(
            DBFriend(
                name = 'Friend %d' % i
            )
        )

        color = DBColor(
            red = i % 256, green = (i + 1) % 256, blue = (i + 2) % 256
        ).save()
        objects.append(
            DBPainter(
                name   = 'Painter %d' % i,
                color  = DBColor( red = i % 256, green = i % 256, blue = i % 256 ),
                color2 = color,
                colors = [ DBColor( red   = (i + 1) % 256,
                                    green = (i + 2) % 256,
                                    blue  = (i + 3) % 256 ),
                           DBColor( red   = (i + 4) % 256,
                                    green = (i + 5) % 256,
                                    blue  = (i + 6) % 256 ) ]
            )
        )

    # Save the current time:
    now = time()

    # Add them to the database:
    for object in objects:
        object.save()

    # Print the execution time:
    delta = time() - now
    count = len( objects )
    print 'Create : %.3f seconds total (%d objects, %d us each)' % (
          delta, count, int( round( (1000000.0 * delta) / count ) ) )

    # Flush any pending objects to be saved (should not be any):
    save( 'Empty' )

    # Update each object:
    for object in objects:
        object.name += '*'

    # Update the database and display execution time:
    save( 'All' )

    # Update each friend:
    for object in objects:
        if isinstance( object, DBFriend ):
            object.friends.append( 'Sam' )

    # Update the database and display execution time:
    save( 'Friend' )

    # Update each painter:
    for object in objects:
        if isinstance( object, DBPainter ):
            object.color.red = (object.color.red + 1) % 256

    # Update the database and display execution time:
    save( 'Painter' )

    # Add a new color to each painter:
    for object in objects:
        if isinstance( object, DBPainter ):
            object.colors.append( DBColor( red = 1, green = 2, blue = 3 ) )

    # Update the database and display execution time:
    save( 'Painter' )

    return objects


def fetch_db ( ):
    # Now attempt to load the first object of each type in the database:
    fetch( DBPerson )
    fetch( DBPatient )
    fetch( DBFriend )
    fetch( DBPainter )
    palette = fetch( DBPalette )
    print 'favorite:', palette.favorite

    # Now try fetching based on prototype objects:
    fetch( DBPerson(  name = 'Person 2*'  ) )
    fetch( DBPatient( name = 'Person 2*'  ) )  # Should return None
    fetch( DBPatient( name = 'Patient 3*' ) )
    palette = fetch( DBPalette( name = 'Palette 2*' ) )
    print 'favorite:', palette.favorite
    palette.favorite = DBColor( red = 100, green = 100, blue = 100 )
    palette.colors[0] = palette.colors[1]
    palette.colors[0].red = 99

    # Verify that the same fetch returns the same object:
    p1 = fetch( DBPainter( name = 'Painter 2*' ) )
    p2 = fetch( DBPainter( name = 'Painter 2*' ) )
    print 'Cache working:', (p1 is p2)


def all_db ( ):
    print '-- All DBFriends ---------------------------------------------------'
    for friend in DBFriend().all():
        print friend
        friend.delete()
    print '--------------------------------------------------------------------'

    print '-- All DBFriends (should be empty now)------------------------------'
    for friend in DBFriend().all():
        print friend
    print '--------------------------------------------------------------------'


def delete_db ( ):
    fetch( DBPainter( name = 'Painter 2*' ) ).delete()


def query_db ( ):
    query( DBPatient, 'age >= 23' )
    query( DBPatient, 'age == [22, 24]' )
    query( DBPatient, 'age != [22, 24]' )
    query( DBPatient, 'age == 22' )
    query( DBPatient, 'age != 22', limit = 2 )
    query( DBPainter, 'color.red == 2' )
    query( DBPainter, 'colors( red == 2 )' )
    query( DBPainter, 'colors[1] == 4' )  # TEMPORARY, WON'T WORK
    query( DBPainter, 'colors.size == 3', limit = 2 )
    query( DBPainter, 'color.exists', limit = 2 )
    query( DBPerson,  'color.exists' )
    query( DBPatient, '(age % 2) == 1' )
    query( DBPatient, '(age % 2) != 1' )
    query( DBPatient, '(age == 23) and (age >= 22) and (weight >= 100)' )
    query( DBPatient, '(age == 23) or (weight == 90) or (age == 24) or '
                      '(weight == 80) or (age == 21) or (weight == [50,60]) or '
                      '(weight >= 130)' )
    query( DBPerson,  "name == '/2/'")
    query( DBPerson,  "name == '/ER/i'")


def query_db_large ( ):
    query_large( DBPatient, '(age % 25) == 11' )
    query_large( DBPatient, '(age >= 500) and (age < 600)' )
    query_large( DBPatient, '(age % 500) == 43' )
    query_large( DBPatient, '(age % 25) == 11' )
    query_large( DBPatient, '(age >= 500) and (age < 600)' )
    query_large( DBPatient, '(age % 500) == 43' )


def update_db ( ):
    painter = DBPainter.fetch()
    #painter.color.count.n     += 1
    painter.colors[0].count.n += 2
    print 'DBPainter %s updated to: %d and %d' % (
          painter.name, painter.color.count.n, painter.colors[0].count.n )

#-------------------------------------------------------------------------------
#  Run the tests:
#-------------------------------------------------------------------------------

mongodb().configure()
#mongodb().configure( force = True )

print DBColor( blue = 2 ).load()
#for palette in DBPalette().iterall():
#    print palette.name

#palette = DBPalette.fetch()
#print palette.name
#print palette.favorites._values()
#print palette.favorites
#palette.favorites[-1] = DBColor( red = 55, green = 55, blue = 55 )

#update_db()
#create_db()
#dump_cache()
##query_db_large()
#fetch_db()
#query_db()
#all_db()
#delete_db()
#dump_cache()

#-- EOF ------------------------------------------------------------------------
