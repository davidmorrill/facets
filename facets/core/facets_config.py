"""
Defines the singleton facets_config object which contains global information
about the configuration of the Facets environment.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import facets_version

from os \
    import environ, makedirs

from os.path \
    import isdir, abspath, join, dirname, exists

#-------------------------------------------------------------------------------
#  'facets_config' class:
#-------------------------------------------------------------------------------

class facets_config ( object ):

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self ):
        """ Initializes the object.

            Note that this constructor can only ever be called from within
            this module, since we don't expose the class.
        """
        # Shadow attributes for properties:
        self._facets_library_path      = None
        self._application_library_path = None
        self._application_data         = None
        self._toolkit                  = None

    #-- Property Implementations -----------------------------------------------

    def _get_facets_library_path ( self ):
        """ The property getter for 'facets_library_path', the directory where
            all Facets package library .zip and database files are stored. This
            directory can be referenced using the logical path '#' within
            application code (e.g. '#themes>my_theme' ).
        """
        if self._facets_library_path is None:
            self._facets_library_path = abspath( join(
                dirname( facets_version.__file__ ), '..', 'library'
            ) )

        return self._facets_library_path

    facets_library_path = property( _get_facets_library_path )


    def _get_application_library_path ( self ):
        """ The property getter for 'application_library_path', the directory
            where an application can store predefined library .zip and database
            files that are shipped as part of the application. This directory
            can be referenced using the logical path '$' within application
            code (e.g. '$themes>my_theme' ).
        """
        if self._application_library_path is None:
            self._application_library_path = abspath(
                join( dirname( sys.argv[0] ), 'library' )
            )

        return self._application_library_path

    application_library_path = property( _get_application_library_path )


    def _get_application_data ( self ):
        """ The property getter for 'application_data', which is the directory
            that applications and packages can safely write non-user accessible
            data to (e.g. configuration information, preferences etc.).

            Do not put anything in here that the user might want to navigate
            to (e.g. projects, user data files, etc).

            The actual location differs between operating systems.
        """
        if self._application_data is None:
            self._application_data = self._initialize_application_data()

        return self._application_data


    def _set_application_data ( self, application_data ):
        """ Property setter.
        """
        self._application_data = application_data

    application_data = property( _get_application_data,
                                 _set_application_data )


    def _get_toolkit ( self ):
        """ The property getter for 'toolkit'. The value returned is, in
            order of preference: the value set by the application; the value
            passed on the command line using the '-toolkit' option; the value
            specified by the 'FACETS_UI' environment variable; otherwise the
            empty string.
        """
        if self._toolkit is None:
            self._toolkit = self._initialize_toolkit()

        return self._toolkit


    def _set_toolkit ( self, toolkit ):
        """ The property setter for 'toolkit'.  The toolkit can be set more than
            once, but only if it is the same value each time. An application
            that is written for a particular toolkit can explicitly set it
            before any other module that gets the value is imported.
        """
        if self._toolkit and (self._toolkit != toolkit):
            raise ValueError(
                'Cannot set toolkit to %s because it has already been set to %s'
                % ( toolkit, self._toolkit )
            )

        self._toolkit = toolkit

    toolkit = property( _get_toolkit, _set_toolkit )

    #-- Private Methods --------------------------------------------------------

    def _initialize_application_data ( self ):
        """ Initializes the (default) application data directory.
        """
        if sys.platform == 'win32':
            environment_variable = 'APPDATA'
            directory_name       = 'Facets'

        else:
            environment_variable = 'HOME'
            directory_name       = '.facets'

        directory_name = environ.get( 'FACETS_CONFIG', directory_name )
        if dirname( directory_name ) != '':
            application_data = abspath( directory_name )
        else:
            # Lookup the environment variable:
            parent_directory = environ.get( environment_variable, None )
            if parent_directory is None:
                raise ValueError(
                    "The '%s' environment variable is not set" %
                    environment_variable
                )

            application_data = join( parent_directory, directory_name )

        # If a file already exists with this name then make sure that it is
        # a directory:
        if exists( application_data ):
            if not isdir( application_data ):
                raise ValueError(
                    "Cannot create the directory '%s'. A file with that name "
                    "already exists." % application_data
                )

        # Otherwise, create the directory:
        else:
            makedirs( application_data )

        return application_data


    def _initialize_toolkit ( self ):
        """ Initializes the toolkit.
        """
        # We handle the command line option even though it doesn't have the
        # highest precedence because we always want to remove it from the
        # command line:
        if '-toolkit' in sys.argv:
            opt_idx = sys.argv.index( '-toolkit' )

            try:
                opt_toolkit = sys.argv[ opt_idx + 1 ]
            except IndexError:
                raise ValueError(
                    'The -toolkit command line argument must be followed by a '
                    'toolkit name'
                )

            # Remove the option:
            del sys.argv[ opt_idx: opt_idx + 1 ]
        else:
            opt_toolkit = None

        if self._toolkit is not None:
            toolkit = self._toolkit
        elif opt_toolkit is not None:
            toolkit = opt_toolkit
        else:
            toolkit = environ.get( 'FACETS_UI', '' )

        return toolkit

# Create the singleton instance of the class:
facets_config = facets_config()

#-- EOF ------------------------------------------------------------------------
