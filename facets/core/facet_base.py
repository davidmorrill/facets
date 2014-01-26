"""
Defines common, low-level capabilities needed by the Facets package.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from os \
    import getcwd, mkdir

from os.path \
    import abspath, dirname, exists, isdir, join, splitext

from string \
    import lowercase, uppercase, ascii_uppercase

from math \
    import log10

from types \
    import ListType, TupleType, DictType, StringType, UnicodeType, IntType, \
           LongType, FloatType, ComplexType, ClassType, TypeType, MethodType

#-- Set the Python version being used ------------------------------------------

vi             = sys.version_info
python_version = vi[0] + (float( vi[1] ) / 10.0)

#-------------------------------------------------------------------------------
#  Provide Python 2.3+ compatible definitions (if necessary):
#-------------------------------------------------------------------------------

try:
    from types import BooleanType
except ImportError:
    BooleanType = IntType

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

ClassTypes    = ( ClassType, TypeType )
SequenceTypes = ( list, tuple )
IntegerTypes  = ( int, long )
ComplexTypes  = ( float, int )
TypeTypes     = ( StringType,  UnicodeType, int, long, float, ComplexType, list,
                  tuple, dict, BooleanType )

FacetNotifier = '__facet_notifier__'

# The standard Facets property cache prefix:
FacetsCache = '_facets_cache_'

# Mapping from numbers to their equivalent string form:
NumberToString = {
    0:  'no',
    1:  'one',
    2:  'two',
    3:  'three',
    4:  'four',
    5:  'five',
    6:  'six',
    7:  'seven',
    8:  'eight',
    9:  'nine',
    10: 'ten'
}

#-------------------------------------------------------------------------------
#  Singleton 'Uninitialized' object:
#-------------------------------------------------------------------------------

class Uninitialized ( object ):
    """ The singleton value of this class represents the uninitialized state
        of a facet and is specified as the 'old' value in the facet change
        notification that occurs when the value of a facet is read before being
        set.
    """

    def __repr__ ( self ):
        return '<uninitialized>'

# When the first reference to a facet is a 'get' reference, the default value of
# the facet is implicitly assigned and returned as the value of the facet.
# Because of this implicit assignment, a facet change notification is
# generated with the Uninitialized object as the 'old' value of the facet, and
# the default facet value as the 'new' value. This allows other parts of the
# facets package to recognize the assignment as the implicit default value
# assignment, and treat it specially.
Uninitialized = Uninitialized()

#-------------------------------------------------------------------------------
#  Singleton 'Undefined' object (used as undefined facet name and/or value):
#-------------------------------------------------------------------------------

class _Undefined ( object ):

    def __repr__ ( self ):
        return '<undefined>'

    def __eq__ ( self, other ):
        return type( self ) == type( other )

    def __ne__ ( self, other ):
        return type( self ) != type( other )

# Singleton object that indicates that a facet attribute has not yet had a
# value set (i.e., its value is undefined). This object is used instead of
# None, because None often has other meanings, such as that a value is not
# used. When a facet attribute is first assigned a value, and its associated
# facet notification handlers are called, Undefined is passed as the *old*
# parameter, to indicate that the attribute previously had no value.
Undefined = _Undefined()

# Tell the C-base code about singleton 'Undefined' and 'Uninitialized' objects:
import cfacets
cfacets._undefined( Undefined, Uninitialized )

#-------------------------------------------------------------------------------
#  Singleton 'Missing' object (used as missing method argument marker):
#-------------------------------------------------------------------------------

class Missing ( object ):

    def __repr__ ( self ):
        return '<missing>'

# Singleton object that indicates that a method argument is missing from a
# type-checked method signature.
Missing = Missing()

#-------------------------------------------------------------------------------
#  Singleton 'Self' object (used as object reference to current 'object'):
#-------------------------------------------------------------------------------

class Self ( object ):

    def __repr__ ( self ):
        return '<self>'

# Singleton object that references the current 'object'.
Self = Self()

#-------------------------------------------------------------------------------
#  Define a special 'string' coercion function:
#-------------------------------------------------------------------------------

def strx ( arg ):
    """ Wraps the built-in str() function to raise a TypeError if the
        argument is not of a type in StringTypes.
    """
    if type( arg ) in StringTypes:
        return str( arg )

    raise TypeError

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

StringTypes = ( StringType, UnicodeType, IntType, LongType, FloatType,
                ComplexType )

# Mapping of coercable types.
CoercableTypes = {
    LongType:    ( 11, long, int ),
    FloatType:   ( 11, float, int ),
    ComplexType: ( 11, complex, float, int ),
    UnicodeType: ( 11, unicode, str )
}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def class_of ( object ):
    """ Returns a string containing the class name of an object with the
        correct indefinite article ('a' or 'an') preceding it (e.g., 'an Image',
        'a PlotValue').
    """
    if isinstance( object, basestring ):
        return add_article( object )

    return add_article( object.__class__.__name__ )


def add_article ( name ):
    """ Returns a string containing the correct indefinite article ('a' or 'an')
        prefixed to the specified string.
    """
    if name[:1].lower() in 'aeiou':
        return 'an ' + name

    return 'a ' + name


def plural_of ( value, format, expand = 10 ):
    plural = '' if value == 1 else 's'
    if 0 <= value <= expand:
        value = NumberToString.get( value, value )

    return format % ( value, plural )


def user_name_for ( name ):
    """ Returns a "user-friendly" version of a string, with the first letter
        capitalized and with underscore characters replaced by spaces. For
        example, ``user_name_for('user_name_for')`` returns ``'User name for'``.
    """
    name       = name.replace( '_', ' ' )
    result     = ''
    last_lower = False

    for c in name:
        if (c in uppercase) and last_lower:
            result += ' '

        last_lower = (c in lowercase)
        result    += c

    return result.capitalize()


def class_name_to_file_name ( class_name ):
    """ Returns the camel-cased class class name specified by *class_name* as a
        Python source file name (e.g. 'MyClass' returns 'my_class.py').
    """
    last_capital = True
    file_name    = ''
    for c in class_name:
        is_capital   = (c in ascii_uppercase)
        file_name   += '_'[ (not is_capital) or last_capital: ]
        file_name   += c.lower()
        last_capital = is_capital

    return (file_name + '.py')


def class_name_to_user_name ( class_name ):
    """ Returns the camel-cased class class name specified by *class_name* as a
        user friendly name (e.g. 'MyClass' returns 'My Class').
    """
    last_capital = True
    user_name    = ''
    for c in class_name:
        is_capital   = (c in ascii_uppercase)
        user_name   += ' '[ (not is_capital) or last_capital: ]
        user_name   += c
        last_capital = is_capital

    return user_name


def verify_path ( path ):
    """ Verify that a specified path exists, and try to create it if it
        does not exist.
    """
    if not exists( path ):
        try:
            mkdir( path )
        except:
            pass

    return path


def file_with_ext ( file_name, ext ):
    """ Returns a copy of the specified *file_name* with its current (if any)
        extension set to *ext*.
    """
    return ('%s.%s' % ( splitext( file_name )[0], ext.lstrip( '.' ) ))


def get_module_name ( level = 2 ):
    """ Returns the name of the module that the caller's caller is located in.
    """
    return sys._getframe( level ).f_globals.get( '__name__', '__main__' )


def get_resource_path ( level = 2 ):
    """Returns a resource path calculated from the caller's stack.
    """
    while True:
        try:
            module = sys._getframe( level ).f_globals.get( '__name__',
                                                           '__main__' )
            break
        except:
            level -= 1

    if module != '__main__':
        # Return the path to the module:
        try:
            return dirname( getattr( sys.modules.get( module ), '__file__' ) )
        except:
            # Apparently 'module' is not a registered module...treat it like
            # '__main__':
            pass

    # '__main__' is not a real module, so we need a work around:
    for path in [ dirname( sys.argv[ 0 ] ), getcwd() ]:
        if exists( path ):
            break

    return path


def get_resource ( *path_items ):
    """ Returns the fully qualified path for the file whose elements are
        specified by *path_items*. The resource is assumed to be relative to the
        caller's module.
    """
    return abspath( join( get_resource_path(), join( *path_items ) ) )


def read_file ( file_name, mode = 'rb' ):
    """ Returns the contents of a text file as a string, or None if the file
        could not be opened or read.
    """
    fh = result = None

    try:
        fh     = file( file_name, mode )
        result = fh.read()
    except:
        pass

    if fh is not None:
        try:
            fh.close()
        except:
            pass

    return result


def write_file ( file_name, data ):
    """ Writes the specified *data* to the specified *file_name*. Returns True
        if the operation was successful, and False otherwise.
    """
    try:
        file = open( file_name, 'wb' )
        file.write( data )
        file.close()

        return True
    except:
        return False


def save_file ( file_name, data = None ):
    """ Saves the specified *data* to the specified *file_name* after prompting
        the user for a new name. *data* can either be a string or a callable
        which will return the data to be saved. If *data* is omitted (or None),
        no data will have been written upon return. In this case, the result
        can be used to complete the operation.

        Returns the name of the file the data was successfully saved to, or None
        if the user cancelled the operation.

        Raises a FacetError if an error occurs writing the data to the file.
    """
    from facets.ui.pyface.api import FileDialog, OK
    from facet_errors         import FacetError

    fd = FileDialog( default_path = file_name, action = 'save as' )
    if fd.open() == OK:
        file_name = fd.path
        if data is None:
            return file_name

        if callable( data ):
            try:
                data = data( file_name )
            except:
                data = data()

        if write_file( file_name, data ):
            return file_name

        raise FacetError( "Error occurred writing '%s'" % file_name )

    return None


def xgetattr ( object, xname, default = Undefined ):
    """ Returns the value of an extended object attribute name of the form:
        name[.name2[.name3...]].
    """
    names = xname.split( '.' )
    for name in names[:-1]:
        if default is Undefined:
            object = getattr( object, name )
        else:
            object = getattr( object, name, None )
            if object is None:
                return default

    if default is Undefined:
        return getattr( object, names[-1] )

    return getattr( object, names[-1], default )


def xsetattr ( object, xname, value ):
    """ Sets the value of an extended object attribute name of the form:
        name[.name2[.name3...]].
    """
    names = xname.split( '.' )
    for name in names[:-1]:
        object = getattr( object, name )

    setattr( object, names[-1], value )


def clamp ( value, min_value, max_value ):
    """ Returns the specified *value*, ensuring that it is in the range between
        the specified *min_value* and *max_value*.
    """
    return max( min( value, max_value ), min_value )


def arg_count_for ( function ):
    """ Returns the argument count for the specified function, method or
        bound method specified by *function*.
    """
    if type( function ) is MethodType:
        return (function.im_func.func_code.co_argcount -
                (function.im_self is not None))

    return function.func_code.co_argcount


def invoke ( function, *args ):
    """ Returns the result of invoking *function* with the argument list
        specified by *args*.

        If the length of *args* is greater than the number of arguments 'n'
        expected by *function*, then only the first 'n' elements of *args* are
        passed to the function.
    """
    return function( *(args[ : arg_count_for( function ) ]) )


def ui_number ( number ):
    """ Formats a number for presentation in a user interface.
    """
    if isinstance( number, ( int, long, basestring ) ):
        return str( number )

    as_int = int( number )
    if as_int == number:
        return str( as_int )

    digits = max( 3 - int( log10( abs( number ) ) ), 0 )
    if digits == 0:
        return '%.f' % number

    return (('%%.%df' % digits) % number).rstrip( '0' ).rstrip( '.' )


class inn ( object ):
    """ Defines the 'if_not_none' (inn) class/function which allows the
        caller to invoke methods on a value even if the value is None. In other
        words, it provides a shortcut for the common idiom of:
            if self.value is not None:
                self.value.do_somthing(...)
        which, using 'inn', can be written as:
            inn( self.value ).do_something(...)

        It can also be used to safely invoke methods which may not exist on an
        object. For example:
            inn( object, 'non_existent_method' )(...)
    """

    def __call__ ( self, arg, method_name = None ):
        if method_name is None:
            return (self if arg is None else arg)

        method = getattr( arg, method_name, None )

        return (self.do_nothing if method is None else method)


    def __getattr__ ( self, name ):
        return self.do_nothing


    def do_nothing ( self, *args, **kw ):
        return None

# Convert the 'inn' class into a singleton, since it has no state:
inn = inn()


def time_stamp ( ):
    """ Returns a human readable time stamp.
    """
    from datetime import datetime

    return datetime.now().strftime( '%A, %B %d, %Y at %I:%M:%S %p' )

#-------------------------------------------------------------------------------
#  Facets metadata selection functions:
#-------------------------------------------------------------------------------

def is_none ( value ):
    return ( value is None )


def not_none ( value ):
    return ( value is not None )


def not_false ( value ):
    return ( value is not False )


def not_event ( value ):
    return ( value != 'event' )


def is_str ( value ):
    return isinstance( value, basestring )

#-------------------------------------------------------------------------------
#  Additional helper functions:
#-------------------------------------------------------------------------------

def normalized_color ( color, has_alpha = False, as_int = True ):
    """ Returns the value of *color* as a normalized color tuple of the form:
        ( red, green, blue [, alpha] ), where reg, green, blue and alpha are
        integers in the range 0..255 if *as_int* is True and are floats in the
        range 0.0..1.0 otherwise. If *has_alpha* is True, the result will have
        four elements; otherwise it will have three.

        The *color* value can be:
        - a 'web' color string of the form: '#rgb' or '#rrggbb'.
        - an integer value of the form: 0xAARRGGBB.
        - a tuple or list of the form: ( hue, level, saturation [, alpha] )
          representing an HLS(A) encoded color, where hue is an integer value in
          the range 0..359, and level, saturation and alpa are float values in
          the range 0.0..1.0.
        - a tuple or list of the form: ( red, green, blue [, alpha] ), where
          red, green, blue and alpha can all be integer values in the range
          0..255, or float values in the range 0.0..1.0.
        - a GUI toolkit specific color object.

        Any input value not matching this description will cause a FacetError to
        be raised.
    """
    # Handle case of 'web' color of the form: '#rgb' or '#rrggbb':
    if isinstance( color, basestring ) and color.startswith( '#' ):
        code = color[1:]
        if len( code ) == 3:
            r, g, b = code
            code    = '%s%s%s%s%s%s' % ( r, r, g, g, b, b )

        if len( code ) == 6:
            try:
                color = int( code, 16 )
            except:
                pass

    # Initialize the component types (True = int, False = float):
    r = g = b = a = True

    if isinstance( color, IntegerTypes ):
        alpha = 255 - int( (color >> 24) & 0xFF )
        red   = int( (color >> 16) & 0xFF )
        green = int( (color >>  8) & 0xFF )
        blue  = int( color         & 0xFF )
    elif isinstance( color, SequenceTypes ) and (3 <= len( color ) <= 4):

        def color_component ( color, index, upper = 255 ):
            value = color[ index ] if index < len( color ) else 255
            if isinstance( value, IntegerTypes ):
                if 0 <= value <= upper:
                    return ( True, value )
            elif isinstance( value, float ) and (0.0 <= value <= 1.0):
                return ( False, value )

            raise FacetError

        a, alpha = color_component( color, 3 )
        if (isinstance( color[0], IntegerTypes ) and
            isinstance( color[1], float )        and
            isinstance( color[2], float )):
            # Handle an HLS(A) encoded tuple, which has the form:
            # ( int, float, float [, float ] ):
            from colorsys import hls_to_rgb

            r = g = b = False
            red, green, blue = hls_to_rgb(
                color_component( color, 0, 359 )[1] / 360.0,
                color_component( color, 1 )[1],
                color_component( color, 2 )[1]
            )
        else:
            r, red   = color_component( color, 0 )
            g, green = color_component( color, 1 )
            b, blue  = color_component( color, 2 )
    else:
        from facets.ui.toolkit import toolkit

        try:
            value = toolkit().from_toolkit_color( color )
            if len( value ) == 3:
                red, green, blue = value
                alpha            = 255
            else:
                red, green, blue, alpha = value
        except:
            raise FacetError

    if as_int:
        if not r: red   = int( 255.0 * red   )
        if not g: green = int( 255.0 * green )
        if not b: blue  = int( 255.0 * blue  )
        if not a: alpha = int( 255.0 * alpha )
    else:
        if r: red   /= 255.0
        if g: green /= 255.0
        if b: blue  /= 255.0
        if a: alpha /= 255.0

    return (( red, green, blue, alpha ) if has_alpha else ( red, green, blue ))


def system_drives ( ):
    """ Returns a list of available system drives. For Linux and Mac systems,
        the list  is [ '/' ]. For Windows, it is a list of the form: [ 'C:\\',
        'D:\\', 'W:\\', ... ].
    """
    from constants import is_windows

    if not is_windows:
        return [ '/' ]

    from ctypes import windll

    drives  = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in uppercase:
        if (bitmask & 0x01) and isdir( letter + ':\\' ):
            drives.append( letter + ':\\' )

        bitmask >>= 1
        if bitmask == 0:
            break

    return drives

#-- EOF ------------------------------------------------------------------------