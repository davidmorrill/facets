"""
Core Facet definitions.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import re
import facet_handlers

from weakref \
    import ref

from os.path \
    import isfile, isdir

from facets.core.protocols.api \
    import adapt

from facet_base \
    import strx, get_module_name, class_of, SequenceTypes, TypeTypes, \
           ClassTypes, Undefined, Missing, FacetsCache, python_version

from facet_handlers \
    import FacetType, FacetInstance, RangeTypes

from facet_collections \
    import FacetListObject, FacetListEvent, FacetDictObject, FacetDictEvent, \
           FacetSetObject, FacetSetEvent

from facet_defs \
    import Facet, facet_from, _FacetMaker, _InstanceArgs, code_editor, \
           html_editor, password_editor, shell_editor

from facet_errors \
    import FacetError

from types \
    import FunctionType, MethodType, ClassType, InstanceType, ModuleType, \
           NoneType

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

MutableTypes = ( list, dict )
SetTypes     = SequenceTypes + ( set, )

# The has_facets.Interface class (patched once the class has been defined):
Interface = NoneType

#-------------------------------------------------------------------------------
#  Numeric type fast validator definitions:
#-------------------------------------------------------------------------------

if sys.modules.get( 'numpy' ) is not None:
    # The numpy enhanced definitions:
    from numpy import integer, floating, complexfloating, bool_

    int_fast_validate     = ( 11, int, integer )
    long_fast_validate    = ( 11, long, None, int, integer )
    float_fast_validate   = ( 11, float, floating, None, int, integer )
    complex_fast_validate = ( 11, complex, complexfloating, None,
                                  float, floating, int, integer )
    bool_fast_validate    = ( 11, bool, bool_ )
else:
    # The standard python definitions (without numpy):
    int_fast_validate     = ( 11, int )
    long_fast_validate    = ( 11, long,    None, int )
    float_fast_validate   = ( 11, float,   None, int )
    complex_fast_validate = ( 11, complex, None, float, int )
    bool_fast_validate    = ( 11, bool )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def default_text_editor ( facet, type = None ):
    """ Returns a default text editor.
    """
    auto_set = facet.auto_set
    if auto_set is None:
        auto_set = True

    enter_set = facet.enter_set or False

    from facets.api import TextEditor

    if type is None:
        return TextEditor( auto_set = auto_set, enter_set = enter_set )

    return TextEditor( auto_set  = auto_set,
                       enter_set = enter_set,
                       evaluate  = type )

#-------------------------------------------------------------------------------
#  'Any' facet:
#-------------------------------------------------------------------------------

class Any ( FacetType ):
    """ Defines a facet whose value can be anything.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = None

    # A description of the type of value this facet accepts:
    info_text = 'any value'

#-------------------------------------------------------------------------------
#  'Generic' facet:
#-------------------------------------------------------------------------------

class Generic ( Any ):
    """ Defines a facet whose value can be anything and whose definition can
        be redefined via assignment using a FacetValue object.
    """

    #-- Class Constants --------------------------------------------------------

    # The standard metadata for the facet:
    metadata = { 'facet_value': True }

#-------------------------------------------------------------------------------
#  'BaseInt' and 'Int' facets:
#-------------------------------------------------------------------------------

class BaseInt ( FacetType ):
    """ Defines a facet whose value must be a Python int.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = int

    # The default value for the facet:
    default_value = 0

    # A description of the type of value this facet accepts:
    info_text = 'an integer'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, int ):
            return value

        self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        return default_text_editor( self, int )


class Int ( BaseInt ):
    """ Defines a facet whose value must be a Python int using a C-level fast
        validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = int_fast_validate

#-------------------------------------------------------------------------------
#  'BaseLong' and 'Long' facets:
#-------------------------------------------------------------------------------

class BaseLong ( FacetType ):
    """ Defines a facet whose value must be a Python long.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = long

    # The default value for the facet:
    default_value = 0L

    # A description of the type of value this facet accepts:
    info_text = 'a long'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, long ):
            return value

        if isinstance( value, int ):
            return long( value )

        self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        return default_text_editor( self, long )


class Long ( BaseLong ):
    """ Defines a facet whose value must be a Python long using a C-level fast
        validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = long_fast_validate

#-------------------------------------------------------------------------------
#  'BaseFloat' and 'Float' facets:
#-------------------------------------------------------------------------------

class BaseFloat ( FacetType ):
    """ Defines a facet whose value must be a Python float.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = float

    # The default value for the facet:
    default_value = 0.0

    # A description of the type of value this facet accepts:
    info_text = 'a float'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, float ):
            return value

        if isinstance( value, int ):
            return float( value )

        self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        return default_text_editor( self, float )


class Float ( BaseFloat ):
    """ Defines a facet whose value must be a Python float using a C-level fast
        validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = float_fast_validate

#-------------------------------------------------------------------------------
#  'BaseComplex' and 'Complex' facets:
#-------------------------------------------------------------------------------

class BaseComplex ( FacetType ):
    """ Defines a facet whose value must be a Python complex.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = complex

    # The default value for the facet:
    default_value = 0.0 + 0.0j

    # A description of the type of value this facet accepts:
    info_text = 'a complex number'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, complex ):
            return value

        if isinstance( value, ( float, int ) ):
            return complex( value )

        self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        return default_text_editor( self, complex )


class Complex ( BaseComplex ):
    """ Defines a facet whose value must be a Python complex using a C-level
        fast validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = complex_fast_validate

#-------------------------------------------------------------------------------
#  'BaseStr' and 'Str' facets:
#-------------------------------------------------------------------------------

class BaseStr ( FacetType ):
    """ Defines a facet whose value must be a Python string.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = ''

    # A description of the type of value this facet accepts:
    info_text = 'a string'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, basestring ):
            return value

        self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        from facet_defs import multi_line_text_editor

        return multi_line_text_editor().set(
            **self.settings( 'auto_set', 'enter_set' )
        )


class Str ( BaseStr ):
    """ Defines a facet whose value must be a Python string using a C-level
        fast validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 11, basestring )


class Title ( Str ):
    """ Defines a string type which by default uses the facets ui TitleEditor
        when used in a View.
    """

    #-- Public Methods ---------------------------------------------------------

    def create_editor ( self ):
        """ Returns the default facets UI editor to use for a facet.
        """
        from facets.api import TitleEditor

        return TitleEditor()

#-------------------------------------------------------------------------------
#  'BaseUnicode' and 'Unicode' facets:
#-------------------------------------------------------------------------------

class BaseUnicode ( FacetType ):
    """ Defines a facet whose value must be a Python unicode string.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = u''

    # A description of the type of value this facet accepts:
    info_text = 'a unicode string'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, unicode ):
            return value

        if isinstance( value, str ):
            return unicode( value )

        self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        from facet_defs import multi_line_text_editor

        return multi_line_text_editor()


class Unicode ( BaseUnicode ):
    """ Defines a facet whose value must be a Python unicode string using a
        C-level fast validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 11, unicode, None, str )

#-------------------------------------------------------------------------------
#  'BaseBool' and 'Bool' facets:
#-------------------------------------------------------------------------------

class BaseBool ( FacetType ):
    """ Defines a facet whose value must be a Python boolean.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = bool

    # The default value for the facet:
    default_value = False

    # A description of the type of value this facet accepts:
    info_text = 'a boolean'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, bool ):
            return value

        self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        from facets.api import BooleanEditor

        return BooleanEditor()


class Bool ( BaseBool ):
    """ Defines a facet whose value must be a Python boolean using a C-level
        fast validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = bool_fast_validate

#-------------------------------------------------------------------------------
#  'BaseCInt' and 'CInt' facets:
#-------------------------------------------------------------------------------

class BaseCInt ( BaseInt ):
    """ Defines a facet whose value must be a Python int and which supports
        coercions of non-int values to int.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = int

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return int( value )
        except:
            self.error( object, name, value )


class CInt ( BaseCInt ):
    """ Defines a facet whose value must be a Python int and which supports
        coercions of non-int values to int using a C-level fast validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 12, int )

#-------------------------------------------------------------------------------
#  'BaseCLong' and 'CLong' facets:
#-------------------------------------------------------------------------------

class BaseCLong ( BaseLong ):
    """ Defines a facet whose value must be a Python long and which supports
        coercions of non-long values to long.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = long

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return long( value )
        except:
            self.error( object, name, value )


class CLong ( BaseCLong ):
    """ Defines a facet whose value must be a Python long and which supports
        coercions of non-long values to long using a C-level fast validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 12, long )

#-------------------------------------------------------------------------------
#  'BaseCFloat' and 'CFloat' facets:
#-------------------------------------------------------------------------------

class BaseCFloat ( BaseFloat ):
    """ Defines a facet whose value must be a Python float and which supports
        coercions of non-float values to float.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = float

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return float( value )
        except:
            self.error( object, name, value )


class CFloat ( BaseCFloat ):
    """ Defines a facet whose value must be a Python float and which supports
        coercions of non-float values to float using a C-level fast validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 12, float )

#-------------------------------------------------------------------------------
#  'BaseCComplex' and 'CComplex' facets:
#-------------------------------------------------------------------------------

class BaseCComplex ( BaseComplex ):
    """ Defines a facet whose value must be a Python complex and which supports
        coercions of non-complex values to complex.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = complex

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return complex( value )
        except:
            self.error( object, name, value )


class CComplex ( BaseCComplex ):
    """ Defines a facet whose value must be a Python complex and which supports
        coercions of non-complex values to complex using a C-level fast
        validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 12, complex )

#-------------------------------------------------------------------------------
#  'BaseCStr' and 'CStr' facets:
#-------------------------------------------------------------------------------

class BaseCStr ( BaseStr ):
    """ Defines a facet whose value must be a Python string and which supports
        coercions of non-string values to string.
    """

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return str( value )
        except:
            try:
                return unicode( value )
            except:
                self.error( object, name, value )


class CStr ( BaseCStr ):
    """ Defines a facet whose value must be a Python string and which supports
        coercions of non-string values to string using a C-level fast
        validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 7, ( ( 12, str ), ( 12, unicode ) ) )

#-------------------------------------------------------------------------------
#  'BaseCUnicode' and 'CUnicode' facets:
#-------------------------------------------------------------------------------

class BaseCUnicode ( BaseUnicode ):
    """ Defines a facet whose value must be a Python unicode string and which
        supports coercions of non-unicode values to unicode.
    """

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return unicode( value )
        except:
            self.error( object, name, value )


class CUnicode ( BaseCUnicode ):
    """ Defines a facet whose value must be a Python unicode string and which
        supports coercions of non-unicode values to unicode using a C-level
        fast validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 12, unicode )

#-------------------------------------------------------------------------------
#  'BaseCBool' and 'CBool' facets:
#-------------------------------------------------------------------------------

class BaseCBool ( BaseBool ):
    """ Defines a facet whose value must be a Python boolean and which supports
        coercions of non-boolean values to boolean.
    """

    #-- Class Constants --------------------------------------------------------

    # The function to use for evaluating strings to this type:
    evaluate = bool

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.

            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return bool( value )
        except:
            self.error( object, name, value )


class CBool ( BaseCBool ):
    """ Defines a facet whose value must be a Python boolean and which supports
        coercions of non-boolean values to boolean using a C-level fast
        validator.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 12, bool )

#-------------------------------------------------------------------------------
#  'String' facet:
#-------------------------------------------------------------------------------

class String ( FacetType ):
    """ Defines a facet whose value must be a Python string whose length is
        optionally in a specified range, and which optionally matches a
        specified regular expression.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = '', minlen = 0, maxlen = sys.maxint,
                   regex = '', **metadata ):
        """ Creates a String facet.

        Parameters
        ----------
        value : string
            The default value for the string
        minlen : integer
            The minimum length allowed for the string
        maxlen : integer
            The maximum length allowed for the string
        regex : string
            A Python regular expression that the string must match

        """
        super( String, self ).__init__( value, **metadata )
        self.minlen = max( 0, minlen )
        self.maxlen = max( self.minlen, maxlen )
        self.regex  = regex
        self._init()


    def _init ( self ):
        """ Completes initialization of the facet at construction or unpickling
            time.
        """
        self._validate = 'validate_all'
        if self.regex != '':
            self.match = re.compile( self.regex ).match
            if (self.minlen == 0) and (self.maxlen == sys.maxint):
                self._validate = 'validate_regex'
        elif (self.minlen == 0) and (self.maxlen == sys.maxint):
            self._validate = 'validate_str'
        else:
            self._validate = 'validate_len'


    def validate ( self, object, name, value ):
        """ Validates that the value is a valid string.
        """
        return getattr( self, self._validate )( object, name, value )


    def validate_all ( self, object, name, value ):
        """ Validates that the value is a valid string in the specified length
            range which matches the specified regular expression.
        """
        try:
            value = strx( value )
            if ((self.minlen <= len( value ) <= self.maxlen) and
                (self.match( value ) is not None)):
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def validate_str ( self, object, name, value ):
        """ Validates that the value is a valid string.
        """
        try:
            return strx( value )
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def validate_len ( self, object, name, value ):
        """ Validates that the value is a valid string in the specified length
            range.
        """
        try:
            value = strx( value )
            if self.minlen <= len( value ) <= self.maxlen:
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def validate_regex ( self, object, name, value ):
        """ Validates that the value is a valid string which matches the
            specified regular expression.
        """
        try:
            value = strx( value )
            if self.match( value ) is not None:
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def info ( self ):
        """ Returns a description of the facet.
        """
        msg = ''
        if (self.minlen != 0) and (self.maxlen != sys.maxint):
            msg = ' between %d and %d characters long' % (
                  self.minlen, self.maxlen )
        elif self.maxlen != sys.maxint:
            msg = ' <= %d characters long' % self.maxlen
        elif self.minlen != 0:
            msg = ' >= %d characters long' % self.minlen

        if self.regex != '':
            if msg != '':
                msg += ' and'
            msg += (" matching the pattern '%s'" % self.regex)

        return 'a string' + msg


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        return default_text_editor( self )


    def __getstate__ ( self ):
        """ Returns the current state of the facet.
        """
        result = self.__dict__.copy()
        for name in [ 'validate', 'match' ]:
            if name in result:
                del result[ name ]

        return result


    def __setstate__ ( self, state ):
        """ Sets the current state of the facet.
        """
        self.__dict__.update( state )
        self._init()

#-------------------------------------------------------------------------------
#  'Regex' facet:
#-------------------------------------------------------------------------------

class Regex ( String ):
    """ Defines a facet whose value is a Python string that matches a specified
        regular expression.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = '', regex = '.*', **metadata ):
        """ Creates a Regex facet.

        Parameters
        ----------
        value : string
            The default value of the facet
        regex : string
            The regular expression that the facet value must match.

        Default Value
        -------------
        *value* or ''
        """
        super( Regex, self ).__init__( value = value, regex = regex,
                                       **metadata )

#-------------------------------------------------------------------------------
#  'Code' facet:
#-------------------------------------------------------------------------------

class Code ( String ):
    """ Defines a facet whose value is a Python string that represents source
        code in some language.
    """

    #-- Class Constants --------------------------------------------------------

    # The standard metadata for the facet:
    metadata = { 'editor': code_editor }

#-------------------------------------------------------------------------------
#  'HTML' facet:
#-------------------------------------------------------------------------------

class HTML ( String ):
    """ Defines a facet whose value must be a string that is interpreted as
        being HTML. By default the value is parsed and displayed as HTML in
        FacetsUI views. The validation of the value does not enforce HTML
        syntax.
    """

    #-- Class Constants --------------------------------------------------------

    # The standard metadata for the facet:
    metadata = { 'editor': html_editor }

#-------------------------------------------------------------------------------
#  'Password' facet:
#-------------------------------------------------------------------------------

class Password ( String ):
    """ Defines a facet whose value must be a string, optionally of constrained
        length or matching a regular expression.

        The facet is indentical to a String facet except that by default it uses
        a PasswordEditor in FacetsUI views, which obscures text entered by the
        user.
    """

    #-- Class Constants --------------------------------------------------------

    # The standard metadata for the facet:
    metadata = { 'editor': password_editor }

#-------------------------------------------------------------------------------
#  'Callable' facet:
#-------------------------------------------------------------------------------

class Callable ( FacetType ):
    """ Defines a facet whose value must be a Python callable.
    """

    #-- Class Constants --------------------------------------------------------

    # The standard metadata for the facet:
    metadata = { 'copy': 'ref' }

    # The default value for the facet:
    default_value = None

    # A description of the type of value this facet accepts:
    info_text = 'a callable value'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that the value is a Python callable.
        """
        if (value is None) or callable( value ):
            return value

        self.error( object, name, self.repr( value ) )

#-------------------------------------------------------------------------------
#  'BaseType' base class:
#-------------------------------------------------------------------------------

class BaseType ( FacetType ):
    """ Defines a facet whose value must be an instance of a simple Python type.
    """

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that the value is a Python callable.
        """
        if isinstance( value, self.fast_validate[ 1: ] ):
            return value

        self.error( object, name, self.repr( value ) )


class This ( BaseType ):
    """ Defines a facet whose value must be an instance of the defining class.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 2, )

    # A description of the type of value this facet accepts:
    info_text = 'an instance of the same type as the receiver'

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = None, allow_none = True, **metadata ):
        super( This, self ).__init__( value, **metadata )

        if allow_none:
            self.fast_validate = ( 2, None )
            self.validate      = self.validate_none
            self.info          = self.info_none


    def validate ( self, object, name, value ):
        if isinstance( value, object.__class__ ):
            return value

        self.validate_failed( object, name, value )


    def validate_none ( self, object, name, value ):
        if isinstance( value, object.__class__ ) or ( value is None ):
            return value

        self.validate_failed( object, name, value )


    def info ( self ):
        return 'an instance of the same type as the receiver'


    def info_none ( self ):
        return 'an instance of the same type as the receiver or None'


    def validate_failed ( self, object, name, value ):
        kind = type( value )
        if kind is InstanceType:
            msg = 'class %s' % value.__class__.__name__
        else:
            msg = '%s (i.e. %s)' % ( str( kind )[ 1: -1 ], repr( value ) )

        self.error( object, name, msg )


class self ( This ):
    """ Defines a facet whose value must be an instance of the defining class
        and whose default value is the object containing the facet.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value type to use (i.e. 'self'):
    default_value_type = 2


class Function ( FacetType ):
    """ Defines a facet whose value must be a Python function.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 11, FunctionType )

    # A description of the type of value this facet accepts:
    info_text = 'a function'


class Method ( FacetType ):
    """ Defines a facet whose value must be a Python method.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 11, MethodType )

    # A description of the type of value this facet accepts:
    info_text = 'a method'


class Class ( FacetType ):
    """ Defines a facet whose value must be an old-style Python class.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 11, ClassType )

    # A description of the type of value this facet accepts:
    info_text = 'an old-style class'


class Module ( FacetType ):
    """ Defines a facet whose value must be a Python module.
    """

    #-- Class Constants --------------------------------------------------------

    # The C-level fast validator to use:
    fast_validate = ( 11, ModuleType )

    # A description of the type of value this facet accepts:
    info_text = 'a module'

#-------------------------------------------------------------------------------
#  'Python' facet:
#-------------------------------------------------------------------------------

class Python ( FacetType ):
    """ Defines a facet that provides behavior identical to a standard Python
        attribute. That is, it allows any value to be assigned, and raises an
        ValueError if an attempt is made to get the value before one has been
        assigned. It has no default value. This facet is most often used in
        conjunction with wildcard naming. See the *Facets User Manual* for
        details on wildcards.
    """

    #-- Class Constants --------------------------------------------------------

    # The standard metadata for the facet:
    metadata = { 'type': 'python' }

    # The default value for the facet:
    default_value = Undefined

#-------------------------------------------------------------------------------
#  'ReadOnly' facet:
#-------------------------------------------------------------------------------

class ReadOnly ( FacetType ):
    """ Defines a facet that is write-once, and then read-only.
        The initial value of the attribute is the special, singleton object
        Undefined. The facet allows any value to be assigned to the attribute
        if the current value is the Undefined object. Once any other value is
        assigned, no further assignment is allowed. Normally, the initial
        assignment to the attribute is performed in the class constructor,
        based on information passed to the constructor. If the read-only value
        is known in advance of run time, use the Constant() function instead of
        ReadOnly to define the facet.
    """

    #-- Class Constants --------------------------------------------------------

    # Defines the CFacet type to use for this facet:
    cfacet_type = 6

    # The default value for the facet:
    default_value = Undefined

# Create a singleton instance as the facet:
ReadOnly = ReadOnly()

#-------------------------------------------------------------------------------
#  'Disallow' facet:
#-------------------------------------------------------------------------------

class Disallow ( FacetType ):
    """ Defines a facet that prevents any value from being assigned or read.
        That is, any attempt to get or set the value of the facet attribute
        raises an exception. This facet is most often used in conjunction with
        wildcard naming, for example, to catch spelling mistakes in attribute
        names. See the *Facets User Manual* for details on wildcards.
    """

    #-- Class Constants --------------------------------------------------------

    # Defines the CFacet type to use for this facet:
    cfacet_type = 5

# Create a singleton instance as the facet:
Disallow = Disallow()

#-------------------------------------------------------------------------------
#  'missing' facet:
#-------------------------------------------------------------------------------

class missing ( FacetType ):
    """ Defines a facet used to indicate that a parameter is missing from a
        type-checked method signature. Allows any value to be assigned; no
        type-checking is performed; default value is the singleton Missing
        object.

        See the **facets.core.has_facets.method()**.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = Missing

# Create a singleton instance as the facet:
missing = missing()

#-------------------------------------------------------------------------------
#  'Constant' facet:
#-------------------------------------------------------------------------------

class Constant ( FacetType ):
    """  Defines a facet whose value is a constant.
    """

    #-- Class Constants --------------------------------------------------------

    # Defines the CFacet type to use for this facet:
    cfacet_type = 7

    # The standard metadata for the facet:
    metadata = { 'type': 'constant', 'transient': True }

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value, **metadata ):
        """ Returns a constant, read-only facet whose value is *value*.

            Parameters
            ----------
            value : any type except a list or dictionary
                The default value for the facet

            Default Value
            -------------
            *value*

            Description
            -----------
            Facets of this type are very space efficient (and fast) because
            *value* is not stored in each instance using the facet, but only in
            the facet object itself. The *value* cannot be a list or dictionary,
            because those types have mutable values.
        """
        if type( value ) in MutableTypes:
            raise FacetError(
                'Cannot define a constant using a mutable list or dictionary'
            )

        super( Constant, self ).__init__( value, **metadata )

#-------------------------------------------------------------------------------
#  'Delegate' facet:
#-------------------------------------------------------------------------------

class Delegate ( FacetType ):
    """ Defines a facet whose value is delegated to a facet on another object.
    """

    #-- Class Constants --------------------------------------------------------

    # Defines the CFacet type to use for this facet:
    cfacet_type = 3

    # The standard metadata for the facet:
    metadata = { 'type': 'delegate', 'transient': False }

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, delegate, prefix = '', modify = False,
                         listenable = True, **metadata ):
        """ Creates a Delegate facet.
        """
        # Handles the special case of delegate = 'object.value' as equivalent
        # to: delegate = 'object', prefix = 'value' if the prefix argument is
        # not specified:
        if prefix == '':
            dot = delegate.find( '.' )
            if dot >= 0:
                prefix   = delegate[ dot + 1: ]
                delegate = delegate[ : dot ]

        metadata[ '_delegate' ]   = delegate
        metadata[ '_prefix' ]     = prefix
        metadata[ '_listenable' ] = listenable

        super( Delegate, self ).__init__( **metadata )

        if prefix == '':
            prefix_type = 0
        elif prefix[-1:] != '*':
            prefix_type = 1
        else:
            prefix = prefix[:-1]
            if prefix != '':
                prefix_type = 2
            else:
                prefix_type = 3

        self.delegate    = delegate
        self.prefix      = prefix
        self.prefix_type = prefix_type
        self.modify      = modify


    def as_cfacet ( self ):
        """ Returns a CFacet corresponding to the facet defined by this class.
        """
        facet = super( Delegate, self ).as_cfacet()
        facet.delegate( self.delegate, self.prefix, self.prefix_type,
                        self.modify )

        return facet

#-------------------------------------------------------------------------------
#  'DelegatesTo' facet:
#-------------------------------------------------------------------------------

class DelegatesTo ( Delegate ):
    """ Defines a facet delegate that matches the standard 'delegate' design
        pattern.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, delegate, prefix = '', listenable = True, **metadata ):
        """ Creates a "delegator" facet, whose definition and default value are
            delegated to a *delegate* facet attribute on another object.

            Parameters
            ----------
            delegate : string
                Name of the attribute on the current object which references the
                object that is the facet's delegate
            prefix : string
                A prefix or substitution applied to the original attribute when
                looking up the delegated attribute
            listenable : Boolean
                Indicates whether a listener can be attached to this attribute
                such that changes to the delagate attribute will trigger it

            Description
            -----------
            An object containing a delegator facet attribute must contain a
            second attribute that references the object containing the delegate
            facet attribute. The name of this second attribute is passed as the
            *delegate* argument to the DelegatesTo() function.

            The following rules govern the application of the prefix parameter:

            * If *prefix* is empty or omitted, the delegation is to an attribute
              of the delegate object with the same name as the delegator
              attribute.
            * If *prefix* is a valid Python attribute name, then the delegation
              is to an attribute whose name is the value of *prefix*.
            * If *prefix* ends with an asterisk ('*') and is longer than one
              character, then the delegation is to an attribute whose name is
              the value of *prefix*, minus the trailing asterisk, prepended to
              the delegator attribute name.
            * If *prefix* is equal to a single asterisk, the delegation is to an
              attribute whose name is the value of the delegator object's
              __prefix__ attribute prepended to delegator attribute name.

            Note that any changes to the delegator attribute are actually
            applied to the corresponding attribute on the delegate object. The
            original object containing the delegator facet is not modified.
        """
        super( DelegatesTo, self ).__init__( delegate,
                                             prefix     = prefix,
                                             modify     = True,
                                             listenable = listenable,
                                             **metadata )

#-------------------------------------------------------------------------------
#  'PrototypedFrom' facet:
#-------------------------------------------------------------------------------

class PrototypedFrom ( Delegate ):
    """ Defines a facet delegate that matches the standard 'prototype' design
        pattern.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, prototype, prefix = '', listenable = True,
                         **metadata ):
        """ Creates a "prototyped" facet, whose definition and default value are
            obtained from a facet attribute on another object.

            Parameters
            ----------
            prototype : string
                Name of the attribute on the current object which references the
                object that is the facet's prototype
            prefix : string
                A prefix or substitution applied to the original attribute when
                looking up the prototyped attribute
            listenable : Boolean
                Indicates whether a listener can be attached to this attribute
                such that changes to the corresponding attribute on the
                prototype object will trigger it

            Description
            -----------
            An object containing a prototyped facet attribute must contain a
            second attribute that references the object containing the prototype
            facet attribute. The name of this second attribute is passed as the
            *prototype* argument to the PrototypedFrom() function.

            The following rules govern the application of the prefix parameter:

            * If *prefix* is empty or omitted, the prototype delegation is to an
              attribute of the prototype object with the same name as the
              prototyped attribute.
            * If *prefix* is a valid Python attribute name, then the prototype
              delegation is to an attribute whose name is the value of *prefix*.
            * If *prefix* ends with an asterisk ('*') and is longer than one
              character, then the prototype delegation is to an attribute whose
              name is the value of *prefix*, minus the trailing asterisk,
              prepended to the prototyped attribute name.
            * If *prefix* is equal to a single asterisk, the prototype
              delegation is to an attribute whose name is the value of the
              prototype object's __prefix__ attribute prepended to the
              prototyped attribute name.

            Note that any changes to the prototyped attribute are made to the
            original object, not the prototype object. The prototype object is
            only used to define to facet type and default value.

        """
        super( PrototypedFrom, self ).__init__( prototype,
                                                prefix     = prefix,
                                                modify     = False,
                                                listenable = listenable,
                                                **metadata )

#-------------------------------------------------------------------------------
#  'Expression' class:
#-------------------------------------------------------------------------------

class Expression ( FacetType ):
    """ Defines a facet whose value must be a valid Python expression. The
        compiled form of a valid expression is stored as the mapped value of
        the facet.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = '0'

    # A description of the type of value this facet accepts:
    info_text = 'a valid Python expression'

    # Indicate that this is a mapped facet:
    is_mapped = True

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            return compile( value, '<string>', 'eval' )
        except:
            self.error( object, name, value )


    def post_setattr ( self, object, name, value ):
        """ Performs additional post-assignment processing.
        """
        object.__dict__[ name + '_' ] = value


    def mapped_value ( self, value ):
        """ Returns the 'mapped' value for the specified **value**.
        """
        return compile( value, '<string>', 'eval' )


    def as_cfacet ( self ):
        """ Returns a CFacet corresponding to the facet defined by this class.
        """
        # Tell the C code that 'setattr' should store the original, unadapted
        # value passed to it:
        return super( Expression, self
                    ).as_cfacet().setattr_original_value( True )

#-------------------------------------------------------------------------------
#  'PythonValue' facet:
#-------------------------------------------------------------------------------

class PythonValue ( Any ):
    """ Defines a facet whose value can be of any type, and whose default
    editor is a Python shell.
    """

    #-- Class Constants --------------------------------------------------------

    # The standard metadata for the facet:
    metadata = { 'editor': shell_editor }

#-------------------------------------------------------------------------------
#  'File' facet:
#-------------------------------------------------------------------------------

class File ( BaseStr ):
    """ Defines a facet whose value must be the name of a file.
    """

    #-- Class Constants --------------------------------------------------------

    # A description of the type of value this facet accepts:
    info_text = 'a file name'

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = '', filter = None, auto_set = False,
                         entries = 0, exists = False, **metadata ):
        """ Creates a File facet.

        Parameters
        ----------
        value : string
            The default value for the facet
        filter : string
            A wildcard string to filter filenames in the file dialog box used by
            the attribute facet editor.
        auto_set : boolean
            Indicates whether the file editor updates the facet value after
            every key stroke.
        exists : boolean
            Indicates whether the facet value must be an existing file or
            not.

        Default Value
        -------------
        *value* or ''
        """
        from facets.ui.core_editors import FileEditor

        metadata.setdefault( 'editor', FileEditor( filter   = filter or [],
                                                   auto_set = auto_set,
                                                   entries  = entries ) )
        self.exists = exists

        super( File, self ).__init__( value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        # fixme: We are really trying to test for the value being a File object,
        # but we can't import it here (raises an import cycle exception), so we
        # we just try to access the facet we need and catch any errors:
        if not isinstance( value, basestring ):
            try:
                value = value.absolute_path
            except:
                self.error( object, name, value )

        if not self.exists:
            return super( File, self ).validate( object, name, value )

        if isinstance( value, basestring) and isfile( value ):
            return value

        self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'Directory' facet:
#-------------------------------------------------------------------------------

class Directory ( BaseStr ):
    """ Defines a facet whose value must be the name of a directory.
    """

    #-- Class Constants --------------------------------------------------------

    # A description of the type of value this facet accepts:
    info_text = 'a directory name'

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = '', auto_set = False, entries = 0,
                         exists = False, **metadata ):
        """ Creates a Directory facet.

        Parameters
        ----------
        value : string
            The default value for the facet
        auto_set : boolean
            Indicates whether the directory editor updates the facet value
            after every key stroke.
        exists : boolean
            Indicates whether the facet value must be an existing directory or
            not.

        Default Value
        -------------
        *value* or ''
        """
        from facets.ui.core_editors import DirectoryEditor

        metadata.setdefault( 'editor', DirectoryEditor( auto_set = auto_set,
                                                        entries  = entries ) )
        self.exists = exists

        super( Directory, self ).__init__( value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        from facets.lib.io.file import File

        if isinstance( value, File ):
            value = value.absolute_path

        if not self.exists:
            return super( Directory, self ).validate( object, name, value )

        if isinstance( value, basestring ) and isdir( value ):
            return value

        self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'BaseRange' and 'Range' facets:
#-------------------------------------------------------------------------------

class BaseRange ( FacetType ):
    """ Defines a facet whose numeric value must be in a specified range.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, low = None, high = None, value = None,
                         exclude_low = False, exclude_high = False,
                         **metadata ):
        """ Creates a Range facet.

        Parameters
        ----------
        low : integer, float or string (i.e. extended facet name)
            The low end of the range.
        high : integer, float or string (i.e. extended facet name)
            The high end of the range.
        value : integer, float or string (i.e. extended facet name)
            The default value of the facet
        exclude_low : Boolean
            Indicates whether the low end of the range is exclusive.
        exclude_high : Boolean
            Indicates whether the high end of the range is exclusive.

        The *low*, *high*, and *value* arguments must be of the same type
        (integer or float), except in the case where either *low* or *high* is
        a string (i.e. extended facet name).

        Default Value
        -------------
        *value*; if *value* is None or omitted, the default value is *low*,
        unless *low* is None or omitted, in which case the default value is
        *high*.
        """
        if value is None:
            if low is not None:
                value = low
            else:
                value = high

        super( BaseRange, self ).__init__( value, **metadata )

        vtype = type( high )
        if ((low is not None) and
            (not issubclass( vtype, ( float, basestring ) ))):
            vtype = type( low )

        is_static = (not issubclass( vtype, basestring ))
        if is_static and (vtype not in RangeTypes):
            raise FacetError(
                ('Range can only be use for int, long or float values, but a '
                 'value of type %s was specified.') % vtype
            )

        self._low_name = self._high_name = ''
        self._vtype    = Undefined

        if vtype is float:
            self._validate  = 'float_validate'
            kind            = 4
            self._type_desc = 'a floating point number'
            if low is not None:
                low = float( low )

            if high is not None:
                high = float( high )

        elif vtype is long:
            self._validate  = 'long_validate'
            self._type_desc = 'a long integer'
            if low is not None:
                low = long( low )

            if high is not None:
                high = long( high )

        elif vtype is int:
            self._validate  = 'int_validate'
            kind            = 3
            self._type_desc = 'an integer'
            if low is not None:
                low = int( low )

            if high is not None:
                high = int( high )
        else:
            self.get, self.set, self.validate = self._get, self._set, None
            self._vtype     = None
            self._type_desc = 'a number'

            if isinstance( high, basestring ):
                self._high_name = high = 'object.' + high
            else:
                self._vtype = type( high )

            high = compile( str( high ), '<string>', 'eval' )

            if isinstance( low, basestring ):
                self._low_name = low = 'object.' + low
            else:
                self._vtype = type( low )

            low = compile( str( low ), '<string>', 'eval' )

            if isinstance( value, basestring ):
                value = 'object.' + value

            self._value = compile( str( value ), '<string>', 'eval' )
            self.default_value_type = 8
            self.default_value      = self._get_default_value

        exclude_mask = 0
        if exclude_low:
            exclude_mask |= 1

        if exclude_high:
            exclude_mask |= 2

        if is_static and (vtype is not long):
            self.init_fast_validator( kind, low, high, exclude_mask )

        # Assign type-corrected arguments to handler attributes:
        self._low          = low
        self._high         = high
        self._exclude_low  = exclude_low
        self._exclude_high = exclude_high


    def init_fast_validator ( self, *args ):
        """ Does nothing for the BaseRange class. Used in the Range class to
            set up the fast validator.
        """
        pass


    def range ( self ):
        """ Returns the range for the facet as a tuple of the form: (low, high).
        """
        return ( self._low, self._high )


    def validate ( self, object, name, value ):
        """ Validate that the value is in the specified range.
        """
        return getattr( self, self._validate )( object, name, value )


    def float_validate ( self, object, name, value ):
        """ Validate that the value is a float value in the specified range.
        """
        try:
            if (isinstance( value, RangeTypes ) and
                ((self._low is None) or
                 (self._exclude_low and (self._low < value)) or
                 ((not self._exclude_low) and (self._low <= value))) and
                ((self._high is None) or
                 (self._exclude_high and (self._high > value)) or
                 ((not self._exclude_high) and (self._high >= value)))):
                return float( value )
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def int_validate ( self, object, name, value ):
        """ Validate that the value is an int value in the specified range.
        """
        try:
            if (isinstance( value, int ) and
                ((self._low is None) or
                 (self._exclude_low and (self._low < value)) or
                 ((not self._exclude_low) and (self._low <= value))) and
                ((self._high is None)  or
                 (self._exclude_high and (self._high > value)) or
                 ((not self._exclude_high) and (self._high >= value)))):
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def long_validate ( self, object, name, value ):
        """ Validate that the value is a long value in the specified range.
        """
        try:
            if (isinstance( value, long ) and
                ((self._low is None) or
                 (self._exclude_low and (self._low < value)) or
                 ((not self._exclude_low) and (self._low <= value))) and
                ((self._high is None) or
                 (self._exclude_high and (self._high > value)) or
                 ((not self._exclude_high) and (self._high >= value)))):
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def _get_default_value ( self, object ):
        """ Returns the default value of the range.
        """
        return eval( self._value )


    def _get ( self, object, name, facet ):
        """ Returns the current value of a dynamic range facet.
        """
        cname = '_facets_cache_' + name
        value = object.__dict__.get( cname, Undefined )
        if value is Undefined:
            object.__dict__[ cname ] = value = eval( self._value )

        low  = eval( self._low )
        high = eval( self._high )
        if (low is not None) and (value < low):
            value = low
        elif (high is not None) and (value > high):
            value = high

        return self._typed_value( value, low, high )


    def _set ( self, object, name, value ):
        """ Sets the current value of a dynamic range facet.
        """
        if not isinstance( value, basestring ):
            try:
                low  = eval( self._low )
                high = eval( self._high )
                if (low is None) and (high is None):
                    if isinstance( value, RangeTypes ):
                        self._set_value( object, name, value )

                        return
                else:
                    new_value = self._typed_value( value, low, high )
                    if (((low is None) or
                        (self._exclude_low and (low < new_value)) or
                        ((not self._exclude_low) and (low <= new_value))) and
                        ((high is None) or
                        (self._exclude_high and (high > new_value)) or
                        ((not self._exclude_high) and (high >= new_value)))):
                        self._set_value( object, name, new_value )

                        return
            except:
                pass

        self.error( object, name, self.repr( value ) )


    def _typed_value ( self, value, low, high ):
        """ Returns the specified value with the correct type for the current
            dynamic range.
        """
        vtype = self._vtype
        if vtype is None:
            if low is not None:
                vtype = type( low )
            elif high is not None:
                vtype = type( high )
            else:
                vtype = lambda x: x

        return vtype( value )


    def _set_value ( self, object, name, value ):
        """ Sets the specified value as the value of the dynamic range.
        """
        cname = '_facets_cache_' + name
        old   = object.__dict__.get( cname, Undefined )
        if old is Undefined:
            old = eval( self._value )

        object.__dict__[ cname ] = value

        if value != old:
            object.facet_property_set( name, old, value )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        if self._vtype is not Undefined:
            low       = eval( self._low )
            high      = eval( self._high )
            low, high = ( self._typed_value( low,  low, high ),
                          self._typed_value( high, low, high ) )
        else:
            low  = self._low
            high = self._high

        if low is None:
            if high is None:
                return self._type_desc

            return '%s <%s %s' % (
                   self._type_desc, '='[ self._exclude_high: ], high )

        elif high is None:
            return  '%s >%s %s' % (
                    self._type_desc, '='[ self._exclude_low: ], low )

        return '%s <%s %s <%s %s' % (
               low, '='[ self._exclude_low: ], self._type_desc,
               '='[ self._exclude_high: ], high )


    def create_editor ( self ):
        """ Returns the default UI editor for the facet.
        """

        from facets.api import RangeEditor

        return RangeEditor()


class Range ( BaseRange ):
    """ Defines a facet whose numeric value must be in a specified range using
        a C-level fast validator.
    """

    def init_fast_validator ( self, *args ):
        """ Set up the C-level fast validator.
        """
        self.fast_validate = args

#-------------------------------------------------------------------------------
#  'BaseEnum' and 'Enum' facets:
#-------------------------------------------------------------------------------

class BaseEnum ( FacetType ):
    """ Defines a facet whose value must be one of a specified set of values.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, *args, **metadata ):
        """ Returns an Enum facet.

            Parameters
            ----------
            values : list or tuple
                The enumeration of all legal values for the facet

            Default Value
            -------------
            values[0]
        """
        values = metadata.pop( 'values', None )
        if isinstance( values, basestring ):
            n = len( args )
            if n == 0:
                default_value = None
            elif n == 1:
                default_value = args[0]
            else:
                raise FacetError(
                    "Incorrect number of arguments specified when using the "
                    "'values' keyword"
                )

            self.name   = values
            self.values = compile( 'object.' + values, '<string>', 'eval' )
            self.get, self.set, self.string_value, self.validate = \
                self._get, self._set, self._string_value, None
        else:
            self.name     = ''
            default_value = args[0]
            if len( args ) == 1:
                if (isinstance( default_value, SequenceTypes ) and
                   (len( default_value ) > 0)):
                    args          = default_value
                    default_value = args[0]
                elif (isinstance( default_value, dict ) and
                     (len( default_value ) > 0)):
                    self.values = default_value
                    keys        = default_value.keys()
                    keys.sort()
                    default_value = keys[0]
                    args          = None

            elif len( args ) == 2:
                arg_1 = args[1]
                if isinstance( arg_1, SequenceTypes ) and (len( arg_1 ) > 0):
                    args = arg_1
                elif isinstance( arg_1, dict ) and (len( arg_1 ) > 0):
                    self.values = arg_1
                    args        = None

            if args is not None:
                self.values = tuple( args )
                self.init_fast_validator( 5, self.values )

        super( BaseEnum, self ).__init__( default_value, **metadata )


    def init_fast_validator ( self, *args ):
        """ Does nothing for the BaseEnum class. Used in the Enum class to set
            up the fast validator.
        """
        pass


    def validate ( self, object, name, value ):
        """ Validates that the value is one of the enumerated set of valid
            values.
        """
        if value in self.values:
            return value

        self.error( object, name, self.repr( value ) )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        if self.name == '':
            values = self.values
        else:
            values = eval( self.values )

        return ' or '.join( [ repr( x ) for x in values ] )


    def create_editor ( self ):
        """ Returns the default UI editor for the facet.
        """
        from facets.api import EnumEditor

        values = self
        if self.name != '':
            values = None

        return EnumEditor( values   = values,
                           name     = self.name,
                           cols     = self.cols or 3,
                           evaluate = self.evaluate,
                           mode     = self.mode or 'radio' )


    def _get ( self, object, name, facet ):
        """ Returns the current value of a dynamic enum facet.
        """
        value  = self.get_value( object, name, facet )
        values = eval( self.values )
        if value not in values:
            value = None
            if len( values ) > 0:
                if isinstance( values, ( dict, FacetDictObject ) ):
                    values = values.keys()
                    values.sort()

                value = values[0]

        return value


    def _set ( self, object, name, value ):
        """ Sets the current value of a dynamic enum facet.
        """
        # fixme: This code allows 'None' to be set as the value when the list
        # of legal values is empty. Technically this is not valid, but is
        # currently being allowed in order to allow pickling/unpickling to work,
        # since otherwise the pickler saves 'None' as the value (see the get
        # code), but the unpickler raises an exception when attempting to later
        # 'set' None as the value:
        values = eval( self.values )
        if (value in values) or ((value is None) and (len( values ) == 0)):
            self.set_value( object, name, value )
        else:
            self.error( object, name, self.repr( value ) )


    def _string_value ( self, object, name, value ):
        """ Returns the string value of the specified *value* in the case where
            the enum has a dynamic set of possible values which may be
            represented using a dictionary.
        """
        values = eval( self.values )
        if isinstance( values, dict ):
            value = values.get( value, value )

        return str( value )


class Enum ( BaseEnum ):
    """ Defines a facet whose value must be one of a specified set of values
        using a C-level fast validator.
    """

    #-- Public Methods ---------------------------------------------------------

    def init_fast_validator ( self, *args ):
        """ Set up the C-level fast validator.
        """
        self.fast_validate = args

#-------------------------------------------------------------------------------
#  'BaseTuple' and 'Tuple' facets:
#-------------------------------------------------------------------------------

class BaseTuple ( FacetType ):
    """ Defines a facet whose value must be a tuple of specified facet types.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, *types, **metadata ):
        """ Returns a Tuple facet.

            Parameters
            ----------
            types : zero or more arguments
                Definition of the default and allowed tuples. If the first item
                of *types* is a tuple, it is used as the default value.
                The remaining argument list is used to form a tuple that
                constrains the  values assigned to the returned facet. The
                facet's value must be a tuple of the same length as the
                remaining argument list, whose elements must match the types
                specified by the corresponding items of the remaining argument
                list.

            Default Value
            -------------
             1. If no arguments are specified, the default value is ().
             2. If a tuple is specified as the first argument, it is the default
                value.
             3. If a tuple is not specified as the first argument, the default
                value is a tuple whose length is the length of the argument
                list, and whose values are the default values for the
                corresponding facet types.

            Example for case #2::

                mytuple = Tuple(('Fred', 'Betty', 5))

            The facet's value must be a 3-element tuple whose first and second
            elements are strings, and whose third element is an integer. The
            default value is ('Fred', 'Betty', 5).

            Example for case #3::

                mytuple = Tuple('Fred', 'Betty', 5)

            The facet's value must be a 3-element tuple whose first and second
            elements are strings, and whose third element is an integer. The
            default value is ('','',0).
        """
        if len( types ) == 0:
            self.init_fast_validator( 11, tuple, None, list )

            super( BaseTuple, self ).__init__( (), **metadata )

            return

        default_value = None

        if isinstance( types[0], tuple ):
            default_value, types = types[0], types[1:]
            if len( types ) == 0:
                types = [ Facet( element ) for element in default_value ]

        self.types = tuple( [ facet_from( type ) for type in types ] )
        self.init_fast_validator( 9, self.types )

        if default_value is None:
            default_value = tuple( [ type.default_value()[1]
                                     for type in self.types ] )

        super( BaseTuple, self ).__init__( default_value, **metadata )


    def init_fast_validator ( self, *args ):
        """ Saves the validation parameters.
        """
        self.no_type_check = (args[0] == 11)


    def validate ( self, object, name, value ):
        """ Validates that the value is a valid tuple.
        """
        if self.no_type_check:
            if isinstance( value, tuple ):
                return value

            if isinstance( value, list ):
                return tuple( value )

            self.error( object, name, value )

        try:
            if isinstance( value, list ):
                value = tuple( value )

            if isinstance( value, tuple ):
                types = self.types
                if len( value ) == len( types ):
                    values = [ ]
                    for i, type in enumerate( types ):
                        values.append( type.validate( object, name, value[i] ) )

                    return tuple( values )
        except:
            pass

        self.error( object, name, value )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        if self.no_type_check:
            return 'a tuple'

        return ('a tuple of the form: (%s)' % ( ', '.join(
            [ type.full_info( object, name, value )
              for type in self.types ] ) ))


    def create_editor ( self ):
        """ Returns the default UI editor for the facet.
        """
        from facets.api import TupleEditor

        # Set up the auto_set, enter_set facets for the editor if specified in
        # the metadata for this facet.
        auto_set = self.auto_set
        if auto_set is None:
            auto_set = True

        enter_set = self.enter_set or False

        # Set the format_str for the editor if specified in the metadata for
        # this facet.
        return TupleEditor( types      = self.types,
                            labels     = self.labels or [ ],
                            cols       = self.cols or 1,
                            format_str = self.format_str or '',
                            auto_set   = auto_set,
                            enter_set  = enter_set )


class Tuple ( BaseTuple ):
    """ Defines a facet whose value must be a tuple of specified facet types
        using a C-level fast validator.
    """

    #-- Public Methods ---------------------------------------------------------

    def init_fast_validator ( self, *args ):
        """ Set up the C-level fast validator.
        """
        super( Tuple, self ).init_fast_validator( *args )

        self.fast_validate = args

#-------------------------------------------------------------------------------
#  'List' facet:
#-------------------------------------------------------------------------------

class List ( FacetType ):
    """ Defines a facet whose value must be a list whose items are of the
        specified facet type.
    """

    #-- Class Constants --------------------------------------------------------

    info_facet          = None
    default_value_type  = 5
    default_value_class = FacetListObject
    collection_type     = 'list'
    _items_event        = None

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, facet = None, value = None, minlen = 0,
                   maxlen = sys.maxint, items = True, **metadata ):
        """ Returns a List facet.

            Parameters
            ----------
            facet : a facet or value that can be converted to a facet using
                    Facet()
                The type of item that the list contains. If not specified, the
                list can contain items of any type.
            value :
                Default value for the list
            minlen : integer
                The minimum length of a list that can be assigned to the facet.
            maxlen : integer
                The maximum length of a list that can be assigned to the facet.

            The length of the list assigned to the facet must be such that::

                minlen <= len(list) <= maxlen

            Default Value
            -------------
            *value* or None
        """
        metadata.setdefault( 'copy', 'deep' )

        if isinstance( facet, SequenceTypes ):
            facet, value = value, list( facet )

        if value is None:
            value = []

        self.item_facet = facet_from( facet )
        self.minlen     = max( 0, minlen )
        self.maxlen     = max( minlen, maxlen )
        self.has_items  = items

        if self.item_facet.instance_handler == '_instance_changed_handler':
            metadata.setdefault( 'instance_handler', '_list_changed_handler' )

        super( List, self ).__init__( value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that the specified *value* is a valid list.
        """
        if (isinstance( value, list ) and
           (self.minlen <= len( value ) <= self.maxlen)):
            if object is None:
                return value

            return self.default_value_class( self, object, name, value )

        self.error( object, name, value )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        if self.minlen == 0:
            if self.maxlen == sys.maxint:
                size = 'items'
            else:
                size = 'at most %d items' % self.maxlen
        else:
            if self.maxlen == sys.maxint:
                size = 'at least %d items' % self.minlen
            else:
                size = 'from %s to %s items' % (
                       self.minlen, self.maxlen )

        return 'a list of %s which are %s' % (
                   size, self.item_facet.full_info( object, name, value ) )


    def create_editor ( self ):
        """ Returns the default UI editor for the facet.
        """
        from facets.core_api import HasFacets

        handler = self.item_facet.handler
        if (isinstance( handler, FacetInstance ) and
            (self.mode != 'list')                and
            issubclass( handler.aClass, HasFacets )):
            from facets.api             import GridEditor
            from facets.ui.grid_adapter import GridAdapter

            return GridEditor( adapter = GridAdapter, operations = [] )

        from facets.api import ListEditor

        return ListEditor( facet_handler = self,
                           rows          = self.rows or 5)


    def inner_facets ( self ):
        """ Returns the *inner facet* (or facets) for this facet.
        """
        return ( self.item_facet, )

    #-- Private Methods --------------------------------------------------------

    def items_event ( self ):
        cls = self.__class__
        if cls._items_event is None:
            cls._items_event = Event(
                FacetListEvent, is_base = False
            ).as_cfacet()

        return cls._items_event

#-------------------------------------------------------------------------------
#  'CList' facet:
#-------------------------------------------------------------------------------

class CList ( List ):
    """ Defines a facet whose values must be a list whose items are of the
        specified facet type or which can be coerced to a list whose values are
        of the specified facet type.
    """

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that the values is a valid list.
        """
        if not isinstance( value, list ):
            try:
                # Should work for all iterables as well as strings (which do
                # not define an __iter__ method)
                value = list( value )
            except ( ValueError, TypeError ):
                value = [ value ]

        return super( CList, self ).validate( object, name, value )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        return '%s or %s' % (
                   self.item_facet.full_info( object, name, value ),
                   super( CList, self ).full_info( object, name, value ) )

#-------------------------------------------------------------------------------
#  'Set' facet:
#-------------------------------------------------------------------------------

class Set ( FacetType ):
    """ Defines a facet whose value must be a set whose items are of the
        specified facet type.
    """

    #-- Class Constants --------------------------------------------------------

    info_facet          = None
    default_value_type  = 5
    default_value_class = FacetSetObject
    collection_type     = 'set'
    _items_event        = None

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, facet = None, value = None, items = True, **metadata ):
        """ Returns a Set facet.

            Parameters
            ----------
            facet : a facet or value that can be converted to a facet using
                    Facet()
                The type of item that the list contains. If not specified, the
                list can contain items of any type.
            value :
                Default value for the set

            Default Value
            -------------
            *value* or None
        """
        metadata.setdefault( 'copy', 'deep' )

        if isinstance( facet, SetTypes ):
            facet, value = value, set( facet )

        if value is None:
            value = set()

        self.item_facet = facet_from( facet )
        self.has_items  = items

        super( Set, self ).__init__( value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that the values is a valid set.
        """
        if isinstance( value, set ):
            if object is None:
                return value

            return FacetSetObject( self, object, name, value )

        self.error( object, name, value )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        return 'a set of %s' % self.item_facet.full_info( object, name, value )


    def create_editor ( self ):
        """ Returns the default UI editor for the facet.
        """
        from facets.core_api import HasFacets

        # fixme: Needs to be customized for sets.
        handler = self.item_facet.handler
        if (isinstance( handler, FacetInstance ) and
            (self.mode != 'list')                and
            issubclass( handler.aClass, HasFacets )):
            from facets.api             import GridEditor
            from facets.ui.grid_adapter import GridAdapter

            return GridEditor( adapter = GridAdapter, operations = [] )

        from facets.api import ListEditor

        return ListEditor( facet_handler = self,
                           rows          = self.rows or 5 )


    def inner_facets ( self ):
        """ Returns the *inner facet* (or facets) for this facet.
        """
        return ( self.item_facet, )

    #-- Private Methods --------------------------------------------------------

    def items_event ( self ):
        cls = self.__class__
        if cls._items_event is None:
            cls._items_event = Event(
                FacetSetEvent, is_base = False
            ).as_cfacet()

        return cls._items_event

#-------------------------------------------------------------------------------
#  'CSet' facet:
#-------------------------------------------------------------------------------

class CSet ( Set ):
    """ Defines a facet whose values must be a set whose items are of the
        specified facet type or which can be coerced to a set whose values are
        of the specified facet type.
    """

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that the values is a valid list.
        """
        if not isinstance( value, set ):
            try:
                # Should work for all iterables as well as strings (which do
                # not define an __iter__ method)
                value = set( value )
            except ( ValueError, TypeError ):
                value = set( [ value ] )

        return super( CList, self ).validate( object, name, value )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        return '%s or %s' % (
                   self.item_facet.full_info( object, name, value ),
                   super( CSet, self ).full_info( object, name, value ) )

#-------------------------------------------------------------------------------
#  'Dict' facet:
#-------------------------------------------------------------------------------

class Dict ( FacetType ):
    """ Defines a facet whose value must be a dictionary, optionally with
        specified types for keys and values.
    """

    #-- Class Constants --------------------------------------------------------

    info_facet          = None
    default_value_type  = 5
    default_value_class = FacetDictObject
    collection_type     = 'dict'
    _items_event        = None

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, key_facet = None, value_facet = None, value = None,
                   items = True, **metadata ):
        """ Returns a Dict facet.

            Parameters
            ----------
            key_facet : a facet or value that can convert to a facet using
                        Facet()
                The facet type for keys in the dictionary; if not specified, any
                values can be used as keys.
            value_facet : a facet or value that can convert to a facet using
                          Facet()
                The facet type for values in the dictionary; if not specified,
                any values can be used as dictionary values.
            value : a dictionary
                The default value for the returned facet
            items : Boolean
                Indicates whether the value contains items

            Default Value
            -------------
            *value* or {}
        """
        if isinstance( key_facet, dict ):
            key_facet, value_facet, value = value_facet, value, key_facet

        if value is None:
            value = {}

        self.key_facet   = facet_from( key_facet )
        self.value_facet = facet_from( value_facet )
        self.has_items   = items

        handler = self.value_facet.handler
        if (handler is not None) and handler.has_items:
            handler = handler.clone()
            handler.has_items = False

        self.value_handler = handler

        super( Dict, self ).__init__( value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that the value is a valid dictionary.
        """
        if isinstance( value, dict ):
            if value is None:
                return value

            return FacetDictObject( self, object, name, value )

        self.error( object, name, value )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        return ('a dictionary with keys which are %s and with values which '
                'are %s') % (
                self.key_facet.full_info(   object, name, value ),
                self.value_facet.full_info( object, name, value ) )


    def create_editor ( self ):
        """ Returns the default UI editor for the facet.
        """
        from facets.api import TextEditor

        return TextEditor( evaluate = eval )


    def inner_facets ( self ):
        """ Returns the *inner facet* (or facets) for this facet.
        """
        return ( self.key_facet, self.value_facet )

    #-- Private Methods --------------------------------------------------------

    def items_event ( self ):
        cls = self.__class__
        if cls._items_event is None:
            cls._items_event = Event(
                FacetDictEvent, is_base = False
            ).as_cfacet()

        return cls._items_event

#-------------------------------------------------------------------------------
#  'BaseInstance' and 'Instance' facets:
#-------------------------------------------------------------------------------

# Allowed values and mappings for the 'adapt' keyword:
AdaptMap = {
   'no':      0,
   'yes':     1,
   'default': 2
 }

class BaseClass ( FacetType ):
    """ Base class for types which have an associated class which can be
        determined dynamically by specifying a string name for the class (e.g.
        'package1.package2.module.class'.

        Any subclass must define instances with 'klass' and 'module' attributes
        that contain the string name of the class (or actual class object) and
        the module name that contained the original facet definition (used for
        resolving local class names (e.g. 'LocalClass')).

        This is an abstract class that only provides helper methods used to
        resolve the class name into an actual class object.
    """

    #-- Public Methods ---------------------------------------------------------

    def resolve_class ( self, object, name, value ):
        klass = self.validate_class( self.find_class( self.klass ) )
        if klass is None:
            self.validate_failed( object, name, value )

        self.klass = klass


    def validate_class ( self, klass ):
        return klass


    def find_class ( self, klass ):
        module = self.module
        col    = klass.rfind( '.' )
        if col >= 0:
            module = klass[ : col ]
            klass = klass[ col + 1: ]

        theClass = getattr( sys.modules.get( module ), klass, None )
        if ( theClass is None ) and ( col >= 0 ):
            try:
                mod = __import__( module )
                for component in module.split( '.' )[ 1: ]:
                    mod = getattr( mod, component )

                theClass = getattr( mod, klass, None )
            except:
                pass

        return theClass


    def validate_failed ( self, object, name, value ):
        kind = type( value )
        if kind is InstanceType:
            msg = 'class %s' % value.__class__.__name__
        else:
            msg = '%s (i.e. %s)' % ( str( kind )[ 1: -1 ], repr( value ) )

        self.error( object, name, msg )


def validate_implements ( value, klass, unused = None ):
    """ Checks to see if a specified value implements the instance class
        interface (if it is an interface).
    """
    from interface_checker import check_implements
    from protocols.api     import declareImplementation

    rc = ( issubclass( klass, Interface ) and
          check_implements( value.__class__, klass ) )
    if rc:
        declareImplementation( value.__class__, instancesProvide = [ klass ] )

    return rc

# Tell the C-base code about the 'validate_implements' function (used by the
# 'fast_validate' code for Instance types):
import cfacets
cfacets._validate_implements( validate_implements )


class BaseInstance ( BaseClass ):
    """ Defines a facet whose value must be an instance of a specified class,
        or one of its subclasses.
    """

    #-- Class Constants --------------------------------------------------------

    adapt_default = 'no'

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, klass = None, factory = None, args = None, kw = None,
                   allow_none = True, adapt = None, module = None,
                   **metadata ):
        """ Returns an Instance facet.

            Parameters
            ----------
            klass : class or instance
                The object that forms the basis for the facet; if it is an
                instance, then facet values must be instances of the same class
                or a subclass. This object is not the default value, even if it
                is an instance.
            factory : callable
                A callable, typically a class, that when called with *args* and
                *kw*, returns the default value for the facet. If not specified,
                or *None*, *klass* is used as the factory.
            args : tuple
                Positional arguments for generating the default value.
            kw : dictionary
                Keyword arguments for generating the default value.
            allow_none : boolean
                Indicates whether None is allowed as a value.
            adapt : string
                A string specifying how adaptation should be applied. The
                possible values are:

                    - 'no': Adaptation is not allowed.
                    - 'yes': Adaptation is allowed. If adaptation fails, an
                        exception should be raised.
                    - 'default': Adapation is allowed. If adaptation fails, the
                        default value for the facet should be used.

            Default Value
            -------------
            **None** if *klass* is an instance or if it is a class and *args*
            and *kw* are not specified. Otherwise, the default value is the
            instance obtained by calling ``klass(*args, **kw)``. Note that the
            constructor call is performed each time a default value is assigned,
            so each default value assigned is a unique instance.
        """
        if klass is None:
            raise FacetError(
                'A %s facet must have a class specified.' %
                self.__class__.__name__
            )

        metadata.setdefault( 'copy', 'deep' )
        metadata.setdefault( 'instance_handler', '_instance_changed_handler' )

        adapt = adapt or self.adapt_default
        if adapt not in AdaptMap:
            raise FacetError( "'adapt' must be 'yes', 'no' or 'default'." )

        if isinstance( factory, tuple ):
            if args is None:
                args, factory = factory, klass
            elif isinstance( args, dict ):
                factory, args, kw = klass, factory, args

        elif (kw is None) and isinstance( factory, dict ):
            kw, factory = factory, klass

        elif ((args is not None) or (kw is not None)) and (factory is None):
            factory = klass

        self._allow_none = allow_none
        self.adapt       = AdaptMap[ adapt ]
        self.module      = module or get_module_name()

        if isinstance( klass, basestring ):
            self.klass = klass
        else:
            if not isinstance( klass, ClassTypes ):
                klass = klass.__class__

            self.klass = klass
            self.init_fast_validate()

        value = factory
        if value is not None:
            if args is None:
                args = ()

            if kw is None:
                if isinstance( args, dict ):
                    kw   = args
                    args = ()
                else:
                    kw = {}
            elif not isinstance( kw, dict ):
                raise FacetError( "The 'kw' argument must be a dictionary." )

            if ((not callable( factory )) and
                (not isinstance( factory, basestring ))):
                if (len( args ) > 0) or (len( kw ) > 0):
                    raise FacetError( "'factory' must be callable" )
            else:
                value = _InstanceArgs( factory, args, kw )

        self.default_value = value

        super( BaseInstance, self ).__init__( value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that the value is a valid object instance.
        """
        if value is None:
            if self._allow_none:
                return value

            self.validate_failed( object, name, value )

        if isinstance( self.klass, basestring ):
            self.resolve_class( object, name, value )

        if self.adapt == 0:
            try:
                if value is adapt( value, self.klass ):
                    return value
            except:
                if validate_implements( value, self.klass ):
                    return value

        elif self.adapt == 1:
            try:
                return adapt( value, self.klass )
            except:
                if validate_implements( value, self.klass ):
                    return value

        else:
            result = adapt( value, self.klass, None )
            if result is None:
                if validate_implements( value, self.klass ):
                    return value

                result = self.default_value
                if isinstance( result, _InstanceArgs ):
                    result = result[ 0 ]( * result[ 1 ], **result[ 2 ] )

            return result

        self.validate_failed( object, name, value )


    def info ( self ):
        """ Returns a description of the facet.
        """
        klass = self.klass
        if not isinstance( klass, basestring ):
            klass = klass.__name__

        if self.adapt == 0:
            result = class_of( klass )
        else:
            result = ('an implementor of, or can be adapted to implement, %s' %
                      klass)

        if self._allow_none:
            return result + ' or None'

        return result


    def get_default_value ( self ):
        """ Returns a tuple of the form: ( default_value_type, default_value )
            which describes the default value for this facet.
        """
        dv  = self.default_value
        dvt = self.default_value_type
        if dvt < 0:
            if not isinstance( dv, _InstanceArgs ):
                return super( BaseInstance, self ).get_default_value()

            self.default_value_type = dvt = 7
            self.default_value      = dv  = ( self.create_default_value,
                                              dv.args, dv.kw )

        return ( dvt, dv )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        from facets.api import InstanceEditor

        return InstanceEditor( label = self.label or '',
                               view  = self.view  or '',
                               kind  = self.kind  or 'popup' )

    #-- Private Methods --------------------------------------------------------

    def create_default_value ( self, *args, **kw ):
        klass = args[0]
        if isinstance( klass, basestring ):
            klass = self.validate_class( self.find_class( klass ) )
            if klass is None:
                raise FacetError( 'Unable to locate class: ' + args[0] )

        return klass( *args[1:], **kw )


    # fixme: Do we still need this method using the new style?...
    def allow_none ( self ):
        self._allow_none = True
        self.init_fast_validate()


    def init_fast_validate ( self ):
        """ Does nothing for the BaseInstance' class. Used by the 'Instance',
            'AdaptedTo' and 'AdaptsTo' classes to set up the C-level fast
            validator.
        """
        pass


    def resolve_class ( self, object, name, value ):
        super( BaseInstance, self ).resolve_class( object, name, value )

        # fixme: The following is quite ugly, because it wants to try and fix
        # the facet referencing this handler to use the 'fast path' now that the
        # actual class has been resolved. The problem is finding the facet,
        # especially in the case of List(Instance('foo')), where the
        # object.base_facet(...) value is the List facet, not the Instance
        # facet, so we need to check for this and pull out the List
        # 'item_facet'. Obviously this does not extend well to other facets
        # containing nested facet references (Dict?)...
        self.init_fast_validate()
        facet   = object.base_facet( name )
        handler = facet.handler
        if handler is not self:
            set_validate = getattr( handler, 'set_validate', None )
            if set_validate is not None:
                set_validate()
            else:
                item_facet = getattr( handler, 'item_facet', None )
                if item_facet is not None:
                    facet   = item_facet
                    handler = self

        if handler.fast_validate is not None:
            facet.set_validate( handler.fast_validate )


class Instance ( BaseInstance ):
    """ Defines a facet whose value must be an instance of a specified class,
        or one of its subclasses using a C-level fast validator.
    """

    #-- Public Methods ---------------------------------------------------------

    def init_fast_validate ( self ):
        """ Sets up the C-level fast validator.
        """
        if (self.adapt == 0) and (not issubclass( self.klass, Interface )):
            fast_validate = [ 1, self.klass ]
            if self._allow_none:
                fast_validate = [ 1, None, self.klass ]

            if self.klass in TypeTypes:
                fast_validate[0] = 0

            self.fast_validate = tuple( fast_validate )
        else:
            self.fast_validate = ( 19, self.klass, self.adapt,
                                   self._allow_none )


class AdaptedTo ( Instance ):

    #-- Class Constants --------------------------------------------------------

    adapt_default = 'yes'

    #-- Public Methods ---------------------------------------------------------

    def post_setattr ( self, object, name, value ):
        """ Performs additional post-assignment processing.
        """
        # Save the original, unadapted value in the mapped facet:
        object.__dict__[ name + '_' ] = value


    def as_cfacet ( self ):
        """ Returns a CFacet corresponding to the facet defined by this class.
        """
        return self.modify_cfacet( super( AdaptedTo, self ).as_cfacet() )


    def modify_cfacet ( self, cfacet ):

        # Tell the C code that the 'post_setattr' method wants the original,
        # unadapted value passed to 'setattr':
        return cfacet.post_setattr_original_value( True )


class AdaptsTo ( AdaptedTo ):

    #-- Public Methods ---------------------------------------------------------

    def modify_cfacet ( self, cfacet ):
        # Tell the C code that 'setattr' should store the original, unadapted
        # value passed to it:
        return cfacet.setattr_original_value( True )

#-------------------------------------------------------------------------------
#  'Type' facet:
#-------------------------------------------------------------------------------

class Type ( BaseClass ):
    """ Defines a facet whose value must be a subclass of a specified class.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, value = None, klass = None, allow_none = True,
                         **metadata ):
        """ Returns an Type facet.

        Parameters
        ----------
        value : class or None

        klass : class or None

        allow_none : boolean
            Indicates whether None is allowed as an assignable value. Even if
            **False**, the default *value* may be **None**.

        Default Value
        -------------
        **None** if *klass* is an instance or if it is a class and *args* and
        *kw* are not specified. Otherwise, the default value is the instance
        obtained by calling ``klass(*args, **kw)``. Note that the constructor
        call is performed each time a default value is assigned, so each
        default value assigned is a unique instance.
        """
        if value is None:
            if klass is None:
                klass = object

        elif klass is None:
            klass = value

        if isinstance( klass, basestring ):
            self.validate = self.resolve

        elif not isinstance( klass, ClassTypes ):
            raise FacetError( "A Type facet must specify a class." )

        self.klass       = klass
        self._allow_none = allow_none
        self.module      = get_module_name()

        super( Type, self ).__init__( value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that the value is a valid object instance.
        """
        try:
            if issubclass( value, self.klass ):
                return value
        except:
            if (value is None) and self._allow_none:
                return value

        self.error( object, name, value )


    def resolve ( self, object, name, value ):
        """ Resolves a class originally specified as a string into an actual
            class, then resets the facet so that future calls will be handled by
            the normal validate method.
        """
        if isinstance( self.klass, basestring ):
            self.resolve_class( object, name, value )
            del self.validate

        return self.validate( object, name, value )


    def info ( self ):
        """ Returns a description of the facet.
        """
        klass = self.klass
        if not isinstance( klass, basestring ):
            klass = klass.__name__

        result = 'a subclass of ' + klass

        if self._allow_none:
            return result + ' or None'

        return result


    def get_default_value ( self ):
        """ Returns a tuple of the form: ( default_value_type, default_value )
            which describes the default value for this facet.
        """
        if not isinstance( self.default_value, basestring ):
            return super( Type, self ).get_default_value()

        return ( 7, ( self.resolve_default_value, (), None ) )


    def resolve_default_value ( self ):
        """ Resolves a class name into a class so that it can be used to
            return the class as the default value of the facet.
        """
        if isinstance( self.klass, basestring ):
            try:
                self.resolve_class( None, None, None )
                del self.validate
            except:
                raise FacetError(
                    'Could not resolve %s into a valid class' % self.klass
                )

        return self.klass

#-------------------------------------------------------------------------------
#  'Event' facet:
#-------------------------------------------------------------------------------

class Event ( FacetType ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, facet = None, **metadata ):
        metadata[ 'type' ]      = 'event'
        metadata[ 'transient' ] = True

        super( Event, self ).__init__( **metadata )

        self.facet = None
        if facet is not None:
            self.facet = facet_from( facet )
            validate   = self.facet.get_validate()
            if validate is not None:
                self.fast_validate = validate


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        facet = self.facet
        if facet is None:
            return 'any value'

        return facet.full_info( object, name, value )

# Define a reusable Event facet:
EventFacet = Event().as_cfacet()

#  Handle circular module dependencies:
facet_handlers.Event = Event

#-------------------------------------------------------------------------------
#  'Button' facet:
#-------------------------------------------------------------------------------

class Button ( Event ):
    """ Defines a facet whose UI editor is a button.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, label = '', image = None, style = 'button',
                         orientation = 'vertical', width_padding = 7,
                         height_padding = 5, view = None, **metadata ):
        """ Returns a facet event whose editor is a button.

            Parameters
            ----------
            label : string
                The label for the button
            image : ImageResource object
                An image to display on the button
            style : one of: 'button', 'radio', 'toolbar', 'checkbox'
                The style of button to display
            orientation : one of: 'horizontal', 'vertical'
                The orientation of the label relative to the image
            width_padding : integer between 0 and 31
                Extra padding (in pixels) added to the left and right sides of
                the button
            height_padding : integer between 0 and 31
                Extra padding (in pixels) added to the top and bottom of the
                button

            Default Value
            -------------
            No default value because events do not store values.
        """
        from facets.api import ThemedButtonEditor, ButtonEditor

        if (label[:1] == '@') and (image is None):
            label, image = '', label

        if (label == '') and (image is not None):
            self.editor = ThemedButtonEditor(
                theme = None,
                image = image,
                view  = view
            )
        else:
            self.editor = ButtonEditor(
                label          = label,
                image          = image,
                style          = style,
                orientation    = orientation,
                width_padding  = width_padding,
                height_padding = height_padding,
                view           = view
            )

        super( Button, self ).__init__( **metadata )

#-------------------------------------------------------------------------------
#  'ToolbarButton' facet:
#-------------------------------------------------------------------------------

class ToolbarButton ( Button ):
    """ Defines a facet whose UI editor is a button that can be used on a
        toolbar.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, label = '', image = None, style = 'toolbar',
                         orientation = 'vertical', width_padding = 2,
                         height_padding = 2, **metadata ):
        """ Returns a facet event whose editor is a toolbar button.

            Parameters
            ----------
            label : string
                The label for the button
            image : ImageResource object
                An image to display on the button
            style : one of: 'button', 'radio', 'toolbar', 'checkbox'
                The style of button to display
            orientation : one of: 'horizontal', 'vertical'
                The orientation of the label relative to the image
            width_padding : integer between 0 and 31
                Extra padding (in pixels) added to the left and right sides of
                the button
            height_padding : integer between 0 and 31
                Extra padding (in pixels) added to the top and bottom of the
                button

            Default Value
            -------------
            No default value because events do not store values.

        """
        super( ToolbarButton, self ).__init__( label, image, style, orientation,
                                               width_padding, height_padding,
                                               **metadata )

#-------------------------------------------------------------------------------
#  'Either' facet:
#-------------------------------------------------------------------------------

class Either ( FacetType ):
    """ Defines a facet whose value can be any of of a specified list of facets.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, *facets, **metadata ):
        """ Creates a facet whose value can be any of of a specified list of
            facets.
        """
        self.facet_maker = _FacetMaker( metadata.pop( 'default', None ),
                                        *facets, **metadata )


    def as_cfacet ( self ):
        """ Returns a CFacet corresponding to the facet defined by this class.
        """
        return self.facet_maker.as_cfacet()

#-------------------------------------------------------------------------------
#  'Symbol' facet:
#-------------------------------------------------------------------------------

class Symbol ( FacetType ):

    #-- Class Constants --------------------------------------------------------

    # A description of the type of value this facet accepts:
    info_text = ( "an object or a string of the form "
        "'[package.package...package.]module[:symbol[([arg1,...,argn])]]' "
        "specifying where to locate the object" )

    #-- Public Methods ---------------------------------------------------------

    def get ( self, object, name ):
        value = object.__dict__.get( name, Undefined )
        if value is Undefined:
            cache = FacetsCache + name
            ref   = object.__dict__.get( cache )
            if ref is None:
                object.__dict__[ cache ] = ref = \
                    object.facet( name ).default_value_for( object, name )

            if isinstance( ref, basestring ):
                object.__dict__[ name ] = value = self._resolve( ref )

        return value


    def set ( self, object, name, value ):
        dict = object.__dict__
        old  = dict.get( name, Undefined )
        if isinstance( value, basestring ):
            dict.pop( name, None )
            dict[ FacetsCache + name ] = value
            object.facet_property_set( name, old )
        else:
            dict[ name ] = value
            object.facet_property_set( name, old, value )


    def _resolve ( self, ref ):
        try:
            path   = ref.split( ':', 1 )
            module = __import__( path[0] )
            for component in path[0].split( '.' )[1:]:
                module = getattr( module, component )

            if len( path ) == 1:
                return module

            elements = path[1].split( '(', 1 )
            symbol   = getattr( module, elements[0] )
            if len( elements ) == 1:
                return symbol

            args = eval( '(' + elements[1] )
            if not isinstance( args, tuple ):
                args = ( args, )

            return symbol( *args )
        except:
            raise FacetError(
                "Could not resolve '%s' into a valid symbol." % ref
            )


if python_version >= 2.5:

    import uuid

    #---------------------------------------------------------------------------
    #  'UUID' facet:
    #---------------------------------------------------------------------------

    class UUID ( FacetType ):
        """ Defines a facet whose value is a globally unique UUID (type 4).
        """

        #-- Class Constants ----------------------------------------------------

        # A description of the type of value this facet accepts:
        info_text = 'a read-only UUID'

        #-- Public Methods -----------------------------------------------------

        def __init__ ( self, **metadata ):
            """ Returns a UUID facet.
            """
            super( UUID, self ).__init__( None, **metadata )


        def validate ( self, object, name, value ):
            """ Raises an error, since no values can be assigned to the facet.
            """
            raise FacetError(
                "The '%s' facet of %s instance is a read-only UUID." %
                ( name, class_of( object ) )
            )


        def get_default_value ( self ):
            return ( 7, ( self._create_uuid, (), None ) )

        #-- Private Methods ---------------------------------------------------

        def _create_uuid ( self ):
            return uuid.uuid4()

#-------------------------------------------------------------------------------
#  'WeakRef' facet:
#-------------------------------------------------------------------------------

class WeakRef ( Instance ):
    """ Returns a facet whose value must be an instance of the same type
        (or a subclass) of the specified *klass*, which can be a class or an
        instance. Note that the facet only maintains a weak reference to the
        assigned value.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, klass = 'facets.core.has_facets.HasFacets',
                         allow_none = False, adapt = 'yes', **metadata ):
        """ Returns a WeakRef facet.

            Only a weak reference is maintained to any object assigned to a
            WeakRef facet. If no other references exist to the assigned value,
            the value may be garbage collected, in which case the value of the
            facet becomes None. In all other cases, the value returned by the
            facet is the original object.

            Parameters
            ----------
            klass : class or instance
                The object that forms the basis for the facet. If *klass* is
                omitted, then values must be an instance of HasFacets.
            allow_none : boolean
                Indicates whether None can be assigned

            Default Value
            -------------
            **None** (even if allow_none==False)
        """

        metadata.setdefault( 'copy', 'ref' )

        super( WeakRef, self ).__init__( klass, allow_none = allow_none,
                         adapt = adapt, module = get_module_name(), **metadata )


    def get ( self, object, name ):
        value = getattr( object, name + '_', None )
        if value is not None:
            return value.value()

        return None


    def set ( self, object, name, value ):
        old = self.get( object, name )

        if value is None:
            object.__dict__[ name + '_' ] = None
        else:
            object.__dict__[ name + '_' ] = HandleWeakRef( object, name, value )

        if value is not old:
            object.facet_property_set( name, old, value )


    def resolve_class ( self, object, name, value ):
        # fixme: We have to override this method to prevent the 'fast validate'
        # from being set up, since the facet using this is a 'property' style
        # facet which is not currently compatible with the 'fast_validate'
        # style (causes internal Python SystemError messages).
        klass = self.find_class( self.klass )
        if klass is None:
            self.validate_failed( object, name, value )

        self.klass = klass

#-- Private Class --------------------------------------------------------------

class HandleWeakRef ( object ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, object, name, value ):
        self.object = ref( object )
        self.name   = name
        self.value  = ref( value, self._value_freed )


    def _value_freed ( self, ref ):
        object = self.object()
        if object is not None:
            object.facet_property_set( self.name, Undefined, None )

#-------------------------------------------------------------------------------
#  Create predefined, reusable facet instances:
#-------------------------------------------------------------------------------

# Synonym for Bool; default value is False.
false = Bool

# Boolean values only; default value is True.
true = Bool( True )

# Allows any value to be assigned; no type-checking is performed.
# Default value is Undefined.
undefined = Any( Undefined )

#-- List Facets ----------------------------------------------------------------

# List of integer values; default value is [].
ListInt = List( Int )

# List of float values; default value is [].
ListFloat = List( Float )

# List of string values; default value is [].
ListStr = List( Str )

# List of Unicode string values; default value is [].
ListUnicode = List( Unicode )

# List of complex values; default value is [].
ListComplex = List( Complex )

# List of Boolean values; default value is [].
ListBool = List( Bool )

# List of function values; default value is [].
ListFunction = List( FunctionType )

# List of method values; default value is [].
ListMethod = List( MethodType )

# List of class values; default value is [].
ListClass = List( ClassType )

# List of instance values; default value is [].
ListInstance = List( InstanceType )

# List of container type values; default value is [].
ListThis = List( This )

#-- Dictionary Facets ----------------------------------------------------------

# Only a dictionary of string:Any values can be assigned; only string keys can
# be inserted. The default value is {}.
DictStrAny = Dict( Str, Any )

# Only a dictionary of string:string values can be assigned; only string keys
# with string values can be inserted. The default value is {}.
DictStrStr = Dict( Str, Str )

# Only a dictionary of string:integer values can be assigned; only string keys
# with integer values can be inserted. The default value is {}.
DictStrInt = Dict( Str, Int )

# Only a dictionary of string:long-integer values can be assigned; only string
# keys with long-integer values can be inserted. The default value is {}.
DictStrLong = Dict( Str, Long )

# Only a dictionary of string:float values can be assigned; only string keys
# with float values can be inserted. The default value is {}.
DictStrFloat = Dict( Str, Float )

# Only a dictionary of string:Boolean values can be assigned; only string keys
# with Boolean values can be inserted. The default value is {}.
DictStrBool = Dict( Str, Bool )

# Only a dictionary of string:list values can be assigned; only string keys
# with list values can be assigned. The default value is {}.
DictStrList = Dict( Str, List )

#-- EOF ------------------------------------------------------------------------