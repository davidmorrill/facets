"""
Tests file operations.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

# Standard library imports:
import os, shutil, stat, unittest

# Facets library imports:
from facets.lib.io \
    import File


class FileTestCase ( unittest.TestCase ):
    """ Tests file operations on a local file system. """

    #---------------------------------------------------------------------------
    # 'TestCase' interface.
    #---------------------------------------------------------------------------

    def setUp ( self ):
        """ Prepares the test fixture before each test method is called. """

        try:
            shutil.rmtree( 'data' )

        except:
            pass

        os.mkdir( 'data' )

        return

    def tearDown ( self ):
        """ Called immediately after each test method has been called. """

        shutil.rmtree( 'data' )

        return

    #---------------------------------------------------------------------------
    # Tests.
    #---------------------------------------------------------------------------

    def test_properties ( self ):
        """ file properties """

        # Properties of a non-existent file.
        f = File( 'data/bogus.xx' )

        self.assert_( os.path.abspath( os.path.curdir ) in f.absolute_path )
        self.assertEqual( f.children, None )
        self.assertEqual( f.ext, '.xx' )
        self.assertEqual( f.exists, False )
        self.assertEqual( f.is_file, False )
        self.assertEqual( f.is_folder, False )
        self.assertEqual( f.is_package, False )
        self.assertEqual( f.is_readonly, False )
        self.assertEqual( f.mime_type, 'content/unknown' )
        self.assertEqual( f.name, 'bogus' )
        self.assertEqual( f.parent.path, 'data' )
        self.assertEqual( f.path, 'data/bogus.xx' )
        self.assert_( os.path.abspath( os.path.curdir ) in f.url )
        self.assertEqual( str( f ), 'File(%s)' % f.path )

        # Properties of an existing file.
        f = File( 'data/foo.py' )
        f.create_file()

        self.assert_( os.path.abspath( os.path.curdir ) in f.absolute_path )
        self.assertEqual( f.children, None )
        self.assertEqual( f.ext, '.py' )
        self.assertEqual( f.exists, True )
        self.assertEqual( f.is_file, True )
        self.assertEqual( f.is_folder, False )
        self.assertEqual( f.is_package, False )
        self.assertEqual( f.is_readonly, False )
        self.assertEqual( f.mime_type, 'text/x-python' )
        self.assertEqual( f.name, 'foo' )
        self.assertEqual( f.parent.path, 'data' )
        self.assertEqual( f.path, 'data/foo.py' )
        self.assert_( os.path.abspath( os.path.curdir ) in f.url )

        # Make it readonly.
        os.chmod( f.path, stat.S_IRUSR )
        self.assertEqual( f.is_readonly, True )

        # And then make it NOT readonly so that we can delete it at the end of
        # the test!
        os.chmod( f.path, stat.S_IRUSR | stat.S_IWUSR )
        self.assertEqual( f.is_readonly, False )

        return

    def test_copy ( self ):
        """ file copy """

        content = 'print "Hello World!"\n'

        f = File( 'data/foo.py' )
        self.assertEqual( f.exists, False )

        # Create the file.
        f.create_file( content )
        self.assertEqual( f.exists, True )
        self.failUnlessRaises( ValueError, f.create_file, content )

        self.assertEqual( f.children, None )
        self.assertEqual( f.ext, '.py' )
        self.assertEqual( f.is_file, True )
        self.assertEqual( f.is_folder, False )
        self.assertEqual( f.mime_type, 'text/x-python' )
        self.assertEqual( f.name, 'foo' )
        self.assertEqual( f.path, 'data/foo.py' )

        # Copy the file.
        g = File( 'data/bar.py' )
        self.assertEqual( g.exists, False )

        f.copy( g )
        self.assertEqual( g.exists, True )

        self.assertEqual( g.children, None )
        self.assertEqual( g.ext, '.py' )
        self.assertEqual( g.is_file, True )
        self.assertEqual( g.is_folder, False )
        self.assertEqual( g.mime_type, 'text/x-python' )
        self.assertEqual( g.name, 'bar' )
        self.assertEqual( g.path, 'data/bar.py' )

        # Attempt to copy a non-existent file (should do nothing).
        f = File( 'data/bogus.xx' )
        self.assertEqual( f.exists, False )

        g = File( 'data/bogus_copy.py' )
        self.assertEqual( g.exists, False )

        f.copy( g )
        self.assertEqual( g.exists, False )

        return

    def test_create_file ( self ):
        """ file creation """

        content = 'print "Hello World!"\n'

        f = File( 'data/foo.py' )
        self.assertEqual( f.exists, False )

        # Create the file.
        f.create_file( content )
        self.assertEqual( f.exists, True )
        self.assertEqual( file( f.path ).read(), content )

        # Try to create it again.
        self.failUnlessRaises( ValueError, f.create_file, content )

        return

    def test_delete ( self ):
        """ file deletion """

        content = 'print "Hello World!"\n'

        f = File( 'data/foo.py' )
        self.assertEqual( f.exists, False )

        # Create the file.
        f.create_file( content )
        self.assertEqual( f.exists, True )
        self.failUnlessRaises( ValueError, f.create_file, content )

        self.assertEqual( f.children, None )
        self.assertEqual( f.ext, '.py' )
        self.assertEqual( f.is_file, True )
        self.assertEqual( f.is_folder, False )
        self.assertEqual( f.mime_type, 'text/x-python' )
        self.assertEqual( f.name, 'foo' )
        self.assertEqual( f.path, 'data/foo.py' )

        # Delete it.
        f.delete()
        self.assertEqual( f.exists, False )

        # Attempt to delete a non-existet file (should do nothing).
        f = File( 'data/bogus.py' )
        self.assertEqual( f.exists, False )

        f.delete()
        self.assertEqual( f.exists, False )

        return

if __name__ == "__main__":
    unittest.main()

#-- EOF ------------------------------------------------------------------------