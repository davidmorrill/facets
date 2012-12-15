"""
Defines the PNG class used to read/write Portable Network Graphics (PNG) file
metadata.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import splitext

from zlib \
    import crc32

from struct \
    import unpack, pack

from facets.api \
    import HasPrivateFacets, File, List, Bool, Property, property_depends_on

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The PNG file signature:
PNGSignature = '\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

#-------------------------------------------------------------------------------
#  'PNG' class:
#-------------------------------------------------------------------------------

class PNG ( HasPrivateFacets ):
    """ A class for reading and writing Portable Network Graphics metadata.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the PNG file:
    file_name = File

    # Is the PNG data valid?
    is_valid = Bool( False )

    # The types of data contained in the PNG file:
    types = Property

    # The keywords contained in the 'tEXt' chunks in the PNG file:
    keywords = Property

    # The number of chunks contained in the PNG file:
    count = Property

    #-- Private Facets ---------------------------------------------------------

    # The list of chunks contained in the PNG file:
    chunks = List

    #-- Public Methods ---------------------------------------------------------

    def save ( self, file_name = '' ):
        """ Saves the current contents to the specified PNG file.
        """
        # Verify that there is a file name specified:
        file_name = file_name or self.file_name
        if file_name == '':
            return False

        # If it has no file extension, set the file extension to '.png':
        if splitext( file_name )[1] == '':
            file_name += '.png'

        # Create the new contents of the PNG file:
        file_data = ''.join( [
            '%s%s%s%s' % ( pack( '!I', len( data ) ), type, data, crc )
            for type, data, crc in self.chunks
        ] )

        # Write the data to the file (return any I/O errors to the caller):
        fh = None
        try:
            fh = open( file_name, 'wb' )
            fh.write( PNGSignature + file_data )
        finally:
            if fh is not None:
                fh.close()

        return True


    def find ( self, type ):
        """ Returns a list of the indices of the chunks of the specified type.
        """
        return [ i for i, chunk in enumerate( self.chunks )
                   if type == chunk[0] ]


    def find_keyword ( self, keyword ):
        """ Returns a list of all 'tEXt' chunks that match the specified
            keyword.
        """
        indices = []
        for index in self.find( 'tEXt' ):
            data = self.data( index )
            if keyword == data[ : data.find( '\x00' ) ]:
                indices.append( index )

        return indices


    def type ( self, index ):
        """ Returns the type of the chunk at the specified index.
        """
        return self.chunks[ index ][0]


    def data ( self, index ):
        """ Returns the data for the chunk at the specified index.
        """
        return self.chunks[ index ][1]


    def keyword ( self, index ):
        """ Returns the keyword associated with the 'tEXt' chunk at the
            specified index.
        """
        type, data, crc = self.chunks[ index ]
        if type != 'tEXt':
            return ''

        return data[ : data.find( '\x00' ) ]


    def value ( self, index ):
        """ Returns the value associated with the 'tEXt' chunk at the specified
            index.
        """
        type, data, crc = self.chunks[ index ]
        if type != 'tEXt':
            return ''

        return data[ data.find( '\x00' ) + 1: ]


    def replace ( self, index, data ):
        """ Replaces the chunk at the specified index which a new chunk with
            the specified data. Note that this can only be used to replace the
            data associated with the specified chunk, and not its type.
        """
        type = self.chunks[ index ][0]
        self.chunks[ index ] = ( type, data, self._crc( type, data ) )


    def insert ( self, index, type, data ):
        """ Inserts a new chunk of the specified type and data preceding the
            chunk at the specified index.
        """
        self.chunks.insert( index, ( type, data, self._crc( type, data ) ) )


    def replace_text ( self, index, keyword, value ):
        """ Replaces the 'tEXt' chunk at the specified index with a new 'tEXt'
            chunk containing the specified keyword and value.
        """
        type = self.chunks[ index ][0]
        if type != 'tEXt':
            raise ValueError(
                "The specified index does not contain a 'tEXt' chunk"
            )

        self.replace( index, '%s\x00%s' % ( keyword, value ) )


    def insert_text ( self, index, keyword, value ):
        """ Inserts a new 'tEXt' chunk containing the specified keyword and
            value data preceding the chunk at the specified index.
        """
        self.insert( index, 'tEXt', '%s\x00%s' % ( keyword, value ) )

    #-- Private Methods --------------------------------------------------------

    def _parse_png ( self, data ):
        """ Verify that the specified data represents a PNG file and parse
            the file data into its constituent 'chunks'.
        """
        # Verify that the data starts with the standard PNG signature:
        if data[:8] != PNGSignature:
            return False

        # Break up the file data into a list of tuples of the form
        # ( chunk_type, chunk_data, chunk_crc ) corresponding to the PNG
        # 'chunks' contained in the file:
        chunks = []
        i      = 8
        n      = len( data )
        while i < n:
            j = i + 8 + unpack( '!I', data[ i: i + 4 ] )[0]
            chunks.append( ( data[ i + 4: i + 8 ],
                             data[ i + 8: j ],
                             data[ j: j + 4 ] ) )
            i = j + 4

        self.chunks = chunks

        return True


    def _crc ( self, type, data ):
        """ Returns the PNG CRC value for the specified type and data.
        """
        return pack( '!i', crc32( data, crc32( type ) ) )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on ( 'file_name, chunks[]' )
    def _get_types ( self ):
        """ Returns a sorted list of the PNG chunk types contained in the file.
        """
        types = set()
        for type, content, crc in self.chunks:
            types.add( type )

        types = list( types )
        types.sort()

        return types


    @property_depends_on ( 'file_name, chunks[]' )
    def _get_keywords ( self ):
        """ Returns a sorted list of the keywords contained in the 'tEXt'
            chunks of the file.
        """
        keywords = set()
        for index in self.find( 'tEXt' ):
            keywords.add( self.keyword( index ) )

        keywords = list( keywords )
        keywords.sort()

        return keywords


    def _get_count ( self ):
        """ Returns the number of chunks contained in the PNG file.
        """
        return len( self.chunks )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        """ Handles the 'file_name' facet being changed.
        """
        fh = None
        try:
            fh            = open( file_name, 'rb' )
            self.is_valid = self._parse_png( fh.read() )
        except:
            self.chunks   = []
            self.is_valid = False

        if fh is not None:
            fh.close()

#-- EOF ------------------------------------------------------------------------