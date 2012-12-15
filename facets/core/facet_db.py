"""
Defines the singleton facet_db object which provides access to various Facets
databases located in one of three paths:

~: The Facets application data library (read/write).
#: The Facets library (part of the Facets installation and usually read-only).
$: The application library (part of the application installation and usually
   read-only).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import shelve

from os \
    import listdir

from os.path \
    import join

from facet_base \
    import Missing, Undefined, verify_path

from facets_config \
    import facets_config

#-------------------------------------------------------------------------------
#  'facet_db' class:
#-------------------------------------------------------------------------------

class facet_db ( object ):
    """ Defines a simple interface for manipulating facet databases.
    """

    def __init__ ( self ):
        self.cache            = {}
        self.application_data = None


    def __call__ ( self, db = None, mode = 'r', path = None ):
        """ Returns an open facet database with the specified *name* and access
            *mode* within the specified logical *path*.

            The name specified by *db* should be a simple name and should not
            include any path information. The mode can either be 'r' (read-only)
            or 'c' (read-write and create database if it does not exist). The
            logical path specified by *path* should be '~', '#' or '$' (see the
            'path' method for more informarion about their meaning). If *path*
            is **None** or omitted, it defaults to '~'.

            If the database cannot be opened for any reason, **None** is
            returned. It is the caller's responsibility to close the database
            when done by calling returned object's 'close()' method.
        """
        try:
            return shelve.open( self.db( db, path ),
                                flag = mode, protocol = -1 )
        except:
            return None


    def get ( self, name, value = None, object = None, db = None ):
        """ Returns the database value with the specified *name*. If no value
            is associated with the specified name, or the database cannot be
            opened, the specified default *value* is returned. The optional
            *object* argument is used to further qualify the name in cases where
            the specified name does not contain an '.' characters. The name of
            the facet database to access can optionally by specified by the *db*
            argument, and defaults to the standard facet database.

            The *name* argument can also include logical path and database name
            information using the syntax: [{?|~|#|$}[db_name>]]item_name, where
            the '~@#$' character specifies the logical path, *db_name* specifies
            the database name, and *item_name* specifies the name of the item
            within the specified database. If *db_name* is omitted, it defaults
            to the database specified by the *db* argument.
        """
        paths, db_name, item_name = self.parse( db, name, object )
        for path in paths:
            key  = '%s%s>%s' % ( path, db_name, item_name )
            data = self.cache.get( key, Undefined )
            if data is Missing:
                continue

            if data is not Undefined:
                return data

            db = self( db_name, path = path )
            if db is not None:
                try:
                    try:
                        data = db.get( item_name, Undefined )
                        if data is not Undefined:
                            self.cache[ key ] = data

                            return data
                    except:
                        pass
                finally:
                    db.close()

            self.cache[ key ] = Missing

        return value


    def set ( self, name, value = Missing, object = None, db = None ):
        """ Sets or deletes the database value with the specified name. If
            value is Missing (the default), the database value associated with
            name is deleted. In all other cases, value is stored as the database
            value associated with the specified name. The optional object
            argument is used to further qualify the name in cases where the
            specified name does not contain an '.' characters. The name of the
            facet database to access can optionally by specified by the db
            argument, and defaults to the standard facet database.
        """
        paths, db_name, item_name = self.parse( db, name, object )
        path = paths[:1]
        key  = '%s%s>%s' % ( path, db_name, item_name )
        db   = self( db_name, 'c', path )
        if db is not None:
            try:
                if value is Missing:
                    self.cache.pop( key, None )
                    del db[ item_name ]
                else:
                    db[ item_name ] = self.cache[ key ] = value
            except:
                import traceback
                traceback.print_exc()

            db.close()


    def db ( self, db = None, path = None ):
        """ Returns the fully qualified name of a specified facet database. The
            name should be a simple name and not include any path information.
            *path* specifies the logical path of the data base. If **None** or
            omitted, the logical path defaults to the Facets application data
            directory (i.e. '~').
        """
        return join( self.path( path ), db or 'facet_db' )


    def names ( self, path = None ):
        """ Returns the names of all currently defined Facet databases in the
            logical path specified by *path*. If *path* is **None** or omitted,
            it defaults to the Facets addplication data directory (i.e. '~').
        """
        result = []
        for name in listdir( self.path( path ) ):
            db = self( name, path = path )
            if db is not None:
                result.append( name )
                db.close()

        result.sort()

        return result


    def name ( self, name, object ):
        """ Returns the correctly specified database item name to use with a
            database get/set request. If *name* contains at least one '.', or
            *object* is **None**, the *name* is returned as is. Otherwise, the
            original *name* is returned prepended with the module and class name
            of the specified *object*.

            Normally an application *object* is provided to qualify a simple
            *name* to ensure that it is unique within a Facets database.
        """
        if (object is not None) and (name.find( '.' ) < 0):
            name = '%s.%s:%s' % ( object.__class__.__module__,
                                  object.__class__.__name__, name )

        return str( name )


    def parse ( self, db_name, item_name, object ):
        """ Parses the database name specified by *db_name*, the item name
            within the database specified by *item_name* for the object
            specified by *object*, and returns a tuple of the form: (paths,
            db_name, item_name), where *path* is a string containing a list of
            logical paths to look in, *db_name* is the name of the database
            to use, and *item_name* is the complete name of the item within the
            specified database.
        """
        db_name = db_name or 'facet_db'
        paths   = item_name[:1]
        if paths not in '$~#?':
            paths = '~'
        else:
            if paths == '?':
                paths = '$~#'

            col = item_name.find( ':' )
            if col < 0:
                item_name = item_name[1:].strip()
            else:
                db_name   = item_name[ 1: col ].strip()
                item_name = item_name[ col + 1: ].strip()

        return ( paths, db_name, self.name( item_name, object ) )


    def path ( self, path = None ):
        """ Returns the path of the directory corresponding to the logical path
            specified by *path*, which should have one of the following values:

            '~': The Facets application data directory.
            '#': The Facets library directory.
            '$': The application library directory.

            Note that if the value of *path* is not one of the above values, it
            returns the Facets application data directory.
        """
        if path == '#':
            return facets_config.facets_library_path

        if path == '$':
            return facets_config.application_library_path

        if self.application_data is None:
            self.application_data = verify_path(
                facets_config.application_data
            )

        return self.application_data

# Define the singleton instance:
facet_db = facet_db()

#-- EOF ------------------------------------------------------------------------
