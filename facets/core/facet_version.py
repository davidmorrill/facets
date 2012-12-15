"""
Defines a Version class for implementing class version based systems.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from math \
    import fmod

from os \
    import stat

from stat \
    import ST_MTIME

from facets.api \
    import HasFacets, Int, Long, Property, property_depends_on

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The default version for a class or object:
DefaultVersion = ( 1, 0, 0, 0 )

# Tuple used to pad out a version missing some elements:
PadVersion = ( 0, 0, 0, 0 )

#-------------------------------------------------------------------------------
#  'Version' class:
#-------------------------------------------------------------------------------

class Version ( HasFacets ):
    """ Defines a Version object for implementing class version based systems.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The version of the associated class/object:
    version = Int( 1 )

    # The major version number of the associated class/object:
    major = Int

    # The minor version number of the associated class/object:
    minor = Int

    # The time stamp of the class implementation file:
    time_stamp = Long

    # The complete version tuple:
    full_version = Property

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'version, major, minor, time_stamp' )
    def _get_full_version ( self ):
        return ( self.version, self.major, self.minor, self.time_stamp )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = None, **facets ):
        """ Initializes the object. If specified, *value* should be a class or
            instance of a class whose version information is being extracted, or
            a four element tuple of the form: ( version, major, minor,
            time_stamp ) containing version information.
        """
        if value is not None:
            time_stamp = 0L
            version    = value
            if not isinstance( value, tuple ):
                if not isinstance( value, ( int, float, basestring ) ):
                    version = getattr( value, '__version__', DefaultVersion )
                    try:
                        file_name  = sys.modules[ value.__module__ ].__file__
                        time_stamp = stat( file_name )[ ST_MTIME ]
                    except:
                        pass

                if isinstance( version, int ):
                    version = ( version, )
                elif isinstance( version, float ):
                    version = ( int( version ),
                                int( str( fmod( version, 1.0 ) )[2:] ) )
                elif isinstance( version, basestring ):
                    version = tuple(
                        [ int( item ) for item in version.split( '.' ) ]
                    )
                elif not isinstance( version, tuple ):
                    raise ValueError(
                        "The __version__ information for a class or object "
                        "must be an int, float, string of the form "
                        "version[.major[.minor]]' or tuple of the form ( int, "
                        "int, int ), but a value of %s was specified" % version
                    )

            self.version, self.major, self.minor, self.time_stamp = \
                (version + PadVersion)[:4]

            if self.time_stamp == 0:
                self.time_stamp = time_stamp

        super( Version, self ).__init__( **facets )


    def __eq__ ( self, other ):
        """ Returns whether two objects have the same version or not.
        """
        return (self.full_version == self._check_other( other ).full_version)


    def __ne__ ( self, other ):
        return (self.full_version != self._check_other( other ).full_version)


    def __gt__ ( self, other ):
        return (self.full_version > self._check_other( other ).full_version)


    def __ge__ ( self, other ):
        return (self.full_version >= self._check_other( other ).full_version)


    def __lt__ ( self, other ):
        return (self.full_version < self._check_other( other ).full_version)


    def __le__ ( self, other ):
        return (self.full_version <= self._check_other( other ).full_version)


    def __repr__ ( self ):
        return '%d.%d.%d' % ( self.version, self.major, self.minor )

    #-- Private Methods --------------------------------------------------------

    def _check_other ( self, other ):
        """ Checks if *other* is a Version, and if not, attempts to coerce it to
            one.
        """
        if isinstance( other, Version ):
            return other

        return Version( other )

#-- EOF ------------------------------------------------------------------------
