"""
Define a set of test classes for exercising the capabilities of the MongoDB
database support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.extra.mongodb.api \
    import MongoDBObject, DBStr, DBInt, DBFloat, DBList, DBRange, DBObject, \
           DBObjects, DBRef, DBRefs, DBLink, DBLinks

#-------------------------------------------------------------------------------
#  'DBCount' class:
#-------------------------------------------------------------------------------

class DBCount ( MongoDBObject ):
    n = DBInt

#-------------------------------------------------------------------------------
#  'DBColor' class:
#-------------------------------------------------------------------------------

class DBColor ( MongoDBObject ):
    red   = DBRange( 0, 255 )
    green = DBRange( 0, 255 )
    blue  = DBRange( 0, 255 )
    count = DBObject( DBCount )


    def _count_default ( self ):
        return DBCount()


    def __repr__ ( self ):
        return ('Color(%d,%d,%d)[%d]' % (
                self.red, self.green, self.blue, self.count.n ))

#-------------------------------------------------------------------------------
#  'DBPalette' class:
#-------------------------------------------------------------------------------

class DBPalette ( MongoDBObject ):
    name      = DBStr
    colors    = DBRefs(  DBColor )
    favorite  = DBLink(  DBColor )
    favorites = DBLinks( DBColor )

#-------------------------------------------------------------------------------
#  'DBPerson' class:
#-------------------------------------------------------------------------------

class DBPerson ( MongoDBObject ):
    name = DBStr( index = 'descending' )

#-------------------------------------------------------------------------------
#  'DBPatient' class:
#-------------------------------------------------------------------------------

class DBPatient ( DBPerson ):
    collection = True

    age    = DBInt
    weight = DBFloat
    #age    = DBInt(   index = 'age_weight 1 unique' )
    #weight = DBFloat( index = 'age_weight 2 descending' )

#-------------------------------------------------------------------------------
#  'DBPainter' class:
#-------------------------------------------------------------------------------

class DBPainter ( DBPerson ):
    color  = DBObject(  DBColor )
    color2 = DBRef(     DBColor )
    colors = DBObjects( DBColor )

#-------------------------------------------------------------------------------
#  'DBFriend' class:
#-------------------------------------------------------------------------------

class DBFriend ( DBPerson ):
    friends = DBList

#-- EOF ------------------------------------------------------------------------
