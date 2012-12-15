"""
Facet definitions related to the numpy library.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import warnings

from facet_base \
    import SequenceTypes

from facet_errors \
    import FacetError

from facet_handlers \
    import FacetType, OBJECT_IDENTITY_COMPARE

from facet_types \
    import Str, Any, Int as TInt, Float as TFloat

#-------------------------------------------------------------------------------
#  Deferred imports from numpy:
#-------------------------------------------------------------------------------

ndarray = None
asarray = None

#-------------------------------------------------------------------------------
#  numpy dtype mapping:
#-------------------------------------------------------------------------------

def dtype2facet ( dtype ):
    """ Get the corresponding facet for a numpy dtype.
    """

    import numpy

    if dtype.char in numpy.typecodes[ 'Float' ]:
        return TFloat

    elif dtype.char in numpy.typecodes[ 'AllInteger' ]:
        return TInt

    elif dtype.char[ 0 ] == 'S':
        return Str

    else:
        return Any

#-------------------------------------------------------------------------------
#  'AbstractArray' facet base class:
#-------------------------------------------------------------------------------

class AbstractArray ( FacetType ):
    """ Abstract base class for defining numpy-based arrays.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, dtype = None, shape = None, value = None,
                         coerce = False, typecode = None, **metadata ):
        """ Returns an AbstractArray facet.
        """
        global ndarray, asarray

        try:
            import numpy
        except ImportError:
            raise FacetError(
                'Using Array or CArray facet types requires the numpy package '
                'to be installed.'
            )

        from numpy import ndarray, zeros

        # Mark this as being an 'array' facet:
        metadata[ 'array' ] = True

        # Normally use object identity to detect array values changing:
        metadata.setdefault( 'comparison_mode', OBJECT_IDENTITY_COMPARE )

        if typecode is not None:
            warnings.warn( 'typecode is a deprecated argument; use dtype '
                           'instead', DeprecationWarning )

            if (dtype is not None) and (dtype != typecode):
                raise FacetError(
                    'Inconsistent usage of the dtype and typecode arguments; '
                    'use dtype alone.'
                )
            else:
                dtype = typecode

        if dtype is not None:
            try:
                # Convert the argument into an actual numpy dtype object:
                dtype = numpy.dtype( dtype )
            except TypeError:
                raise FacetError(
                    'could not convert %r to a numpy dtype' % dtype
                )

        if shape is not None:
            if isinstance( shape, SequenceTypes ):
                for item in shape:
                    if ((item is None) or (type( item ) is int) or
                        (isinstance( item, SequenceTypes) and
                         (len( item ) == 2) and
                         (type( item[0] ) is int) and (item[0] >= 0) and
                         ((item[1] is None) or ((type( item[1] ) is int) and
                          (item[0] <= item[1]))))):
                        continue

                    raise FacetError( 'shape should be a list or tuple' )
            else:
                raise FacetError( 'shape should be a list or tuple' )

            if (len( shape ) == 2) and (metadata.get( 'editor' ) is None):
                from facets.api import ArrayEditor

                metadata.setdefault( 'editor', ArrayEditor )

        if value is None:
            if dtype is None:
                # Compatibility with the default of Facets 2.0
                dt = int
            else:
                dt = dtype
            if shape is None:
                value = zeros( ( 0, ), dt )
            else:
                size = []
                for item in shape:
                    if item is None:
                        item = 1
                    elif type( item ) in SequenceTypes:
                        # XXX: what is this supposed to do?
                        item = item[0]
                    size.append( item )
                value = zeros( size, dt )

        self.dtype  = dtype
        self.shape  = shape
        self.coerce = coerce

        super( AbstractArray, self ).__init__( value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that the value is a valid array.
        """
        try:
            # Make sure the value is an array:
            type_value = type( value )
            if not isinstance( value, ndarray ):
                if not isinstance( value, SequenceTypes ):
                    self.error( object, name, value )
                if self.dtype is not None:
                    value = asarray( value, self.dtype )
                else:
                    value = asarray( value )

            # Make sure the array is of the right type:
            if ((self.dtype is not None) and
                (value.dtype != self.dtype)):
                if self.coerce:
                    value = value.astype( self.dtype )
                else:
                    # XXX: this also coerces.
                    value = asarray( value, self.dtype )

            # If no shape requirements, then return the value:
            facet_shape = self.shape
            if facet_shape is None:
                return value

            # Else make sure that the value's shape is compatible:
            value_shape = value.shape
            if len( facet_shape ) == len( value_shape ):
                for i, dim in enumerate( value_shape ):
                    item = facet_shape[ i ]
                    if item is not None:
                        if type( item ) is int:
                            if dim != item:
                                break
                        elif ((dim < item[0]) or
                              ((item[1] is not None) and (dim > item[1]))):
                            break
                else:
                    return value
        except:
            pass

        self.error( object, name, value )


    def info ( self ):
        """ Returns descriptive information about the facet.
        """
        dtype = shape = ''

        if self.shape is not None:
            shape = []
            for item in self.shape:
                if item is None:
                    item = '*'
                elif type( item ) is not int:
                    if item[1] is None:
                        item = '%d..' % item[0]
                    else:
                        item = '%d..%d' % item
                shape.append( item )
            shape = ' with shape %s' % ( tuple( shape ), )

        if self.dtype is not None:
            # FIXME: restore nicer descriptions of dtypes.
            dtype = ' of %s values' % self.dtype

        return 'an array%s%s' % ( dtype, shape )


    def get_editor ( self, facet = None ):
        """ Returns the default UI editor for the facet.
        """
        from facets.api import TupleEditor

        if self.dtype is None:
            types = Any
        else:
            types = dtype2facet( self.dtype )

        return TupleEditor( types  = types,
                            labels = self.labels or [ ],
                            cols   = self.cols or 1  )

    #-- Private Methods --------------------------------------------------------

    def get_default_value ( self ):
        """ Returns the default value constructor for the type (called from the
            facet factory.
        """
        return ( 7, ( self.copy_default_value,
                 ( self.validate( None, None, self.default_value ), ), None ) )

    def copy_default_value ( self, value ):
        """ Returns a copy of the default value (called from the C code on
            first reference to a facet with no current value).
        """
        return value.copy()

#-------------------------------------------------------------------------------
#  'Array' facet:
#-------------------------------------------------------------------------------

class Array ( AbstractArray ):
    """ Defines a facet whose value must be a numpy array.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, dtype = None, shape = None, value = None,
                   typecode = None, **metadata ):
        """ Returns an Array facet.

            Parameters
            ----------
            dtype : a numpy dtype (e.g., int32)
                The type of elements in the array; if omitted, no type-checking
                is performed on assigned values.
            shape : a tuple
                Describes the required shape of any assigned value. Wildcards
                and ranges are allowed. The value None within the *shape* tuple
                means that the corresponding dimension is not checked. (For
                example, ``shape=(None,3)`` means that the first dimension can
                be any size, but the second must be 3.) A two-element tuple
                within the *shape* tuple means that the dimension must be in the
                specified range. The second element can be None to indicate that
                there is no upper bound. (For example,
                ``shape=((3,5),(2,None))`` means that the first dimension must
                be in the range 3 to 5 (inclusive), and the second dimension
                must be at least 2.)
            value : numpy array
                A default value for the array

            Default Value
            -------------
            *value* or ``zeros(min(shape))``, where ``min(shape)`` refers to
            the minimum shape allowed by the array. If *shape* is not specified,
            the minimum shape is (0,).

            Description
            -----------
            An Array facet allows only upcasting of assigned values that are
            already numpy arrays. It automatically casts tuples and lists of the
            right shape to the specified *dtype* (just like numpy's **array**
            does).
        """
        super( Array, self ).__init__( dtype, shape, value, False,
                                       typecode = typecode, **metadata )

#-------------------------------------------------------------------------------
#  'CArray' facet:
#-------------------------------------------------------------------------------

class CArray ( AbstractArray ):
    """ Defines a facet whose value must be a numpy array, with casting
        allowed.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, dtype = None, shape = None, value = None,
                   typecode = None, **metadata ):
        """ Returns a CArray facet.

            Parameters
            ----------
            dtype : a numpy dtype (e.g., int32)
                The type of elements in the array
            shape : a tuple
                Describes the required shape of any assigned value. Wildcards
                and ranges are allowed. The value None within the *shape* tuple
                means that the corresponding dimension is not checked. (For
                example, ``shape=(None,3)`` means that the first dimension can
                be any size, but the second must be 3.) A two-element tuple
                within the *shape* tuple means that the dimension must be in the
                specified range. The second element can be None to indicate that
                there is no upper bound. (For example,
                ``shape=((3,5),(2,None))`` means that the first dimension must
                be in the range 3 to 5 (inclusive), and the second dimension
                must be at least 2.)
            value : numpy array
                A default value for the array

            Default Value
            -------------
            *value* or ``zeros(min(shape))``, where ``min(shape)`` refers to the
            minimum shape allowed by the array. If *shape* is not specified, the
            minimum shape is (0,).

            Description
            -----------
            The facet returned by CArray() is similar to that returned by
            Array(), except that it allows both upcasting and downcasting of
            assigned values that are already numpy arrays. It automatically
            casts tuples and lists of the right shape to the specified *dtype*
            (just like numpy's **array** does).
        """
        super( CArray, self ).__init__( dtype, shape, value, True,
                                        typecode = typecode, **metadata )

#-- EOF ------------------------------------------------------------------------