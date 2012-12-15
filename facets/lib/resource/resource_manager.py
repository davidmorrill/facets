"""
The default resource manager.

A resource manager locates and loads application resources such as images and
sounds etc.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import glob, inspect, operator, os

from os.path \
    import join

from zipfile \
    import is_zipfile, ZipFile

from facets.core_api \
    import HasFacets, Instance

from facets.lib.util.resource \
    import get_path

from resource_factory \
    import ResourceFactory

from resource_reference \
    import ImageReference

#-------------------------------------------------------------------------------
#  'ResourceManager' class:
#-------------------------------------------------------------------------------

class ResourceManager ( HasFacets ):
    """ The default resource manager.

        A resource manager locates and loads application resources such as
        images and sounds etc.
    """

    #-- Class Constants --------------------------------------------------------

    # Allowed extensions for image resources:
    IMAGE_EXTENSIONS = [ '.png', '.jpg', '.bmp', '.gif', '.ico' ]

    #-- Facet Definitions ------------------------------------------------------

    # The resource factory is responsible for actually creating resources.
    # This is used so that (for example) different GUI toolkits can create
    # a images in the format that they require:
    resource_factory = Instance( ResourceFactory )

    #-- 'ResourceManager' Interface --------------------------------------------

    def locate_image ( self, image_name, path, size = None ):
        """ Locates an image.
        """
        if not operator.isSequenceType( path ):
            path = [ path ]

        resource_path = []
        for item in path:
            if isinstance( item, basestring ):
                resource_path.append( item )
            else:
                resource_path.extend( self._get_resource_path( item ) )

        return self._locate_image( image_name, resource_path, size )


    def load_image ( self, image_name, path, size = None ):
        """ Loads an image.
        """
        reference = self.locate_image( image_name, path, size )
        if reference is not None:
            return reference.load()

        return None

    #-- Private Methods --------------------------------------------------------

    def _locate_image ( self, image_name, resource_path, size ):
        """ Attempts to locate an image resource.

            If the image is found, an image resource reference is returned.
            If the image is NOT found None is returned.
        """
        # If the image name contains a file extension (eg. '.jpg') then we will
        # only accept an an EXACT filename match:
        basename, extension = os.path.splitext( image_name )
        if len( extension ) > 0:
            extensions = [ extension ]
            pattern    = image_name

        # Otherwise, we will search for common image suffixes:
        else:
            extensions = self.IMAGE_EXTENSIONS
            pattern    = image_name + '.*'

        for dirname in resource_path:
            # Try the 'images' sub-directory first (since that is commonly
            # where we put them!).  If the image is not found there then look
            # in the directory itself:
            if size is None:
                subdirs = [ 'images', '' ]

            else:
                subdirs = [
                    'images/%dx%d' % ( size[0], size[1] ), 'images', ''
                ]

            for path in subdirs:
                # Is there anything resembling the image name in the directory?
                filenames = glob.glob( join( dirname, path, pattern ) )
                for filename in filenames:
                    not_used, extension = os.path.splitext( filename )
                    if extension in extensions:
                        return ImageReference(
                            self.resource_factory, filename = filename
                        )

            # Is there an 'images' zip file in the directory?
            zip_filename = join( dirname, 'images.zip' )
            if os.path.isfile( zip_filename ):
                zip_file = ZipFile( zip_filename, 'r' )
                # Try the image name itself, and then the image name with
                # common images suffixes.
                for extension in extensions:
                    try:
                        image_data = zip_file.read( basename + extension )

                        return ImageReference(
                            self.resource_factory, data = image_data )
                    except:
                        pass

            # Is this a path within a zip file?
            # First, find the zip file in the path:
            filepath = dirname
            zippath  = ''
            while ((not is_zipfile( filepath )) and
                   os.path.splitdrive( filepath )[1].startswith( '\\' ) and
                   os.path.splitdrive( filepath )[1].startswith( '/' )):
                filepath, tail = os.path.split( filepath )
                if zippath != '':
                    zippath = tail + '/' + zippath
                else:
                    zippath = tail

            # If we found a zipfile, then look inside it for the image:
            if is_zipfile( filepath ):

                zip_file = ZipFile( filepath )
                for subpath in [ 'images', '' ]:
                    for extension in extensions:
                        try:
                            # This is a little messy. since zip files don't
                            # recognize a leading slash, we have to be very
                            # particular about how we build this path when
                            # there are empty strings:
                            if zippath != '':
                                path = zippath + '/'
                            else:
                                path = ''

                            if subpath != '':
                                path += (subpath + '/')

                            path = path + basename + extension
                            # Now that we have the path we can attempt to load
                            # the image:
                            image_data = zip_file.read( path )
                            reference  = ImageReference(
                                self.resource_factory, data = image_data
                            )

                            # If there was no exception then return the result:
                            return reference

                        except:
                            pass

        return None


    def _get_resource_path ( self, object ):
        """ Returns the resource path for an object.
        """
        if hasattr( object, 'resource_path' ):
            return object.resource_path

        return self._get_default_resource_path( object )


    def _get_default_resource_path ( self, object ):
        """ Returns the default resource path for an object.
        """
        resource_path = []
        for klass in inspect.getmro( object.__class__ ):
            try:
                resource_path.append( get_path( klass ) )

            # We get an attribute error when we get to a C extension type (in
            # our case it will most likley be 'CHasFacets'.  We simply ignore
            # everything after this point:
            except AttributeError:
                break

        return resource_path

#-- EOF ------------------------------------------------------------------------