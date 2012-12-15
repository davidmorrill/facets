""" Defines the 'core' facets for the Facets package. A facet is a type
    definition that can be used for normal Python object attributes, giving the
    attributes some additional characteristics:

    Initialization:
        Facets have predefined values that do not need to be explicitly
        initialized in the class constructor or elsewhere.
    Validation:
        Facet attributes have flexible, type-checked values.
    Delegation:
        Facet attributes' values can be delegated to other objects.
    Notification:
        Facet attributes can automatically notify interested parties when
        their values change.
    Visualization:
        Facet attributes can automatically construct (automatic or
        programmer-defined) user interfaces that allow their values to be
        edited or displayed)

    Note: 'facet' is a synonym for 'property', but is used instead of the
    word 'property' to differentiate it from the Python language 'property'
    feature.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import facet_handlers

from cfacets \
    import cFacet

from facet_base \
    import SequenceTypes, Self, Undefined, Missing, TypeTypes, add_article, \
           BooleanType

from facet_errors \
    import FacetError

from facet_handlers \
    import FacetHandler, FacetInstance, FacetFunction, FacetCoerceType, \
           FacetCastType, FacetCompound, FacetMap, FacetString, ThisClass, \
           FacetType, _arg_count, _read_only, _write_only, _undefined_get, \
           _undefined_set

from types \
    import NoneType, IntType, LongType, FloatType, ComplexType, StringType, \
           UnicodeType, ListType, TupleType, DictType, FunctionType, \
           ClassType, MethodType, InstanceType, TypeType

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from 'cfacet' default value types to a string representation:
KindMap = {
   0: 'value',
   1: 'value',
   2: 'self',
   3: 'list',
   4: 'dict',
   5: 'list',
   6: 'dict',
   7: 'factory',
   8: 'method'
}

#-------------------------------------------------------------------------------
#  Editor factory functions:
#-------------------------------------------------------------------------------

PasswordEditor      = None
MultilineTextEditor = None
SourceCodeEditor    = None
HTMLTextEditor      = None
PythonShellEditor   = None


def password_editor ( ):
    """ Factory function that returns an editor for passwords.
    """
    global PasswordEditor

    if PasswordEditor is None:
        from facets.api import TextEditor
        PasswordEditor = TextEditor( password = True )

    return PasswordEditor


def multi_line_text_editor ( ):
    """ Factory function that returns a text editor for multi-line strings.
    """
    global MultilineTextEditor

    if MultilineTextEditor is None:
        from facets.api import TextEditor
        MultilineTextEditor = TextEditor( multi_line = True )

    return MultilineTextEditor


def code_editor ( ):
    """ Factory function that returns an editor that treats a multi-line string
    as source code.
    """
    global SourceCodeEditor

    if SourceCodeEditor is None:
        from facets.api import CodeEditor
        SourceCodeEditor = CodeEditor()

    return SourceCodeEditor


def html_editor ( ):
    """ Factory function for an "editor" that displays a multi-line string as
    interpreted HTML.
    """
    global HTMLTextEditor

    if HTMLTextEditor is None:
        from facets.api import HTMLEditor
        HTMLTextEditor = HTMLEditor()

    return HTMLTextEditor


def shell_editor ( ):
    """ Factory function that returns a Python shell for editing Python values.
    """
    global PythonShellEditor

    if PythonShellEditor is None:
        from facets.api import ShellEditor
        PythonShellEditor = ShellEditor()

    return PythonShellEditor

#-------------------------------------------------------------------------------
#  'CFacet' class (extends the underlying cFacet c-based type):
#-------------------------------------------------------------------------------

class CFacet ( cFacet ):
    """ Extends the underlying C-based cFacet type.
    """

    #-- Public Methods ---------------------------------------------------------

    def __call__ ( self, *args, **metadata ):
        """ Allows a derivative facet to be defined from this one.
        """
        handler = self.handler
        if isinstance( handler, FacetType ):
            dict = ( self.__dict__ or {} ).copy()
            dict.update( metadata )

            return handler( *args, **dict )

        metadata.setdefault( 'parent', self )

        return Facet( *( args + ( self, ) ), **metadata )

    #-- (Python) Property Definitions ------------------------------------------

    def __get_default ( self ):
        kind, value = self.default_value()
        if kind in ( 2, 7, 8 ):
            return Undefined

        if kind in ( 4, 6 ):
            return value.copy()

        if kind in ( 3, 5 ):
            return value[:]

        return value

    default = property( __get_default )


    def __get_default_kind ( self ):
        return KindMap[ self.default_value()[ 0 ] ]

    default_kind = property( __get_default_kind )


    def __get_facet_type ( self ):
        from facet_types import Any

        handler = self.handler
        if handler is not None:
            return handler

        return Any

    facet_type = property( __get_facet_type )


    def __get_inner_facets ( self ):
        handler = self.handler
        if handler is not None:
            return handler.inner_facets()

        return ()

    inner_facets = property( __get_inner_facets )

    #-- Public Methods ---------------------------------------------------------

    def string_value ( self, object, name, value ):
        """ Returns a string representation of the specified *value*.
        """
        format_func = self.format_func
        if format_func is not None:
            return format_func( value )

        format_str = self.format_str
        if format_str is not None:
            return (format_str % value)

        handler = self.handler
        if handler is not None:
            return handler.string_value( object, name, value )

        return str( value )


    def is_facet_type ( self, facet_type ):
        """ Returns whether or not this facet is of a specified facet type.
        """
        return isinstance( self.facet_type, facet_type )


    def get_editor ( self ):
        """ Returns the user interface editor associated with the facet.
        """
        from facets.api import EditorFactory

        # See if we have an editor:
        editor = self.editor
        if editor is None:

            # Else see if the facet handler has an editor:
            handler = self.handler
            if handler is not None:
                editor = handler.get_editor( self )

            # If not, give up and use a default text editor:
            if editor is None:
                from facets.api import TextEditor
                editor = TextEditor

        # If the result is not an EditoryFactory:
        if not isinstance( editor, EditorFactory ):
            # Then it should be a factory for creating them:
            args   = ()
            facets = {}
            if type( editor ) in SequenceTypes:
                for item in editor[:]:
                    if type( item ) in SequenceTypes:
                        args = tuple( item )
                    elif isinstance( item, dict ):
                        facets = item
                        if facets.get( 'facet', 0 ) is None:
                            facets = facets.copy()
                            facets[ 'facet' ] = self
                    else:
                        editor = item
            editor = editor( *args, **facets )

        # Cache the result:
        self.editor = editor

        # Return the resulting EditorFactory object:
        return editor


    def get_help ( self, full = True ):
        """ Returns the help text for a facet.

        Parameters
        ----------
        full : Boolean
            Indicates whether to return the value of the *help* attribute of
            the facet itself.

        Description
        -----------
        If *full* is False or the facet does not have a **help** string,
        the returned string is constructed from the **desc** attribute on the
        facet and the **info** string on the facet's handler.
        """
        if full:
            help = self.help
            if help is not None:
                return help

        handler = self.handler
        if handler is not None:
            info = 'must be %s.' % handler.info()
        else:
            info = 'may be any value.'

        desc = self.desc
        if self.desc is None:
            return info.capitalize()

        return 'Specifies %s and %s' % ( desc, info )


    def full_info ( self, object, name, value ):
        """ Returns a description of the facet.
        """
        handler = self.handler
        if handler is not None:
            return handler.full_info( object, name, value )

        return 'any value'


    def info ( self ):
        """ Returns a description of the facet.
        """
        handler = self.handler
        if handler is not None:
            return handler.info()

        return 'any value'


    def __reduce_ex__ ( self, protocol ):
        return ( __newobj__, ( self.__class__, 0 ), self.__getstate__() )


    def _register ( self, object, name ):
        """ Registers listeners on an assigned 'FacetValue' object's 'value'
            property.
        """
        def handler ( ):
            object.facet_property_set( name, None )

        tv       = self._facet_value
        handlers = tv._handlers
        if handlers is None:
            tv._handlers = handlers = {}

        handlers[ ( id( object ), name ) ] = handler

        tv.on_facet_set( handler, 'value' )


    def _unregister ( self, object, name ):
        """ Unregisters listeners on an assigned 'FacetValue' object's 'value'
            property.
        """
        tv       = self._facet_value
        handlers = tv._handlers
        key      = ( id( object ), name )
        handler  = handlers.get( key )
        if handler is not None:
            del handlers[ key ]
            tv.on_facet_set( handler, 'value', remove = True )

# Make sure the Python-level version of the facet class is known to all
# interested parties:
import cfacets
cfacets._cfacet( CFacet )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

ConstantTypes    = ( NoneType, IntType, LongType, FloatType, ComplexType,
                     StringType, UnicodeType )

PythonTypes      = ( StringType,   UnicodeType,  IntType,    LongType,
                     FloatType,    ComplexType,  ListType,   TupleType,
                     DictType,     FunctionType, MethodType, ClassType,
                     InstanceType, TypeType,     NoneType )

CallableTypes    = ( FunctionType, MethodType )

FacetTypes       = ( FacetHandler, CFacet )

DefaultValues = {
    StringType:  '',
    UnicodeType: u'',
    IntType:     0,
    LongType:    0L,
    FloatType:   0.0,
    ComplexType: 0j,
    ListType:    [],
    TupleType:   (),
    DictType:    {},
    BooleanType: False
 }

DefaultValueSpecial = [ Missing, Self ]
DefaultValueTypes   = [ ListType, DictType ]

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def __newobj__ ( cls, *args ):
    """ Unpickles new-style objects.
    """
    return cls.__new__( cls, *args )


def _default_value_type ( default_value ):
    """ Returns the type of default value specified.
    """
    try:
        return DefaultValueSpecial.index( default_value ) + 1
    except:
        try:
            return DefaultValueTypes.index( type( default_value ) ) + 3
        except:
            return 0

#-------------------------------------------------------------------------------
#  'FacetFactory' class:
#-------------------------------------------------------------------------------

class FacetFactory ( object ):
    """ Deprecated function for creating Facets.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, maker_function = None ):
        """ Initializes the object.
        """
        if maker_function is not None:
            self.maker_function = maker_function


    def __call__ ( self, *args, **metadata ):
        """ Creates a CFacet instance.
        """
        return self.maker_function( *args, **metadata )

#-------------------------------------------------------------------------------
#  'FacetImportError' class:
#-------------------------------------------------------------------------------

class FacetImportError ( FacetFactory ):
    """ Defines a factory class for deferring import problems until encountering
        code that actually tries to use the unimportable facet.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, message ):
        """ Initializes the object.
        """
        self.message = message


    def __call__ ( self, *args, **metadata ):
        """ Creates a CFacet instance.
        """
        raise FacetError( self.message )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

_facet_factory_instances = {}

def facet_factory ( facet ):
    """ Returns a facet created from a FacetFactory instance.
    """
    global _facet_factory_instances

    tid = id( facet )
    if tid not in _facet_factory_instances:
        _facet_factory_instances[ tid ] = facet()

    return _facet_factory_instances[ tid ]


def facet_cast ( something ):
    """ Casts a CFacet, FacetFactory or FacetType to a CFacet but returns None
        if it is none of those.
    """
    if isinstance( something, CFacet ):
        return something

    if isinstance( something, FacetFactory ):
        return facet_factory( something )

    if isinstance( something, type ) and issubclass( something, FacetType ):
        return something().as_cfacet()

    if isinstance( something, FacetType ):
        return something.as_cfacet()

    return None


def try_facet_cast ( something ):
    """ Attempts to cast a value to a facet. Returns either a facet or the
        original value.
    """
    return facet_cast( something ) or something


def facet_from ( something ):
    """ Returns a facet derived from its input.
    """
    from facet_types import Any

    if isinstance( something, CFacet ):
        return something

    if something is None:
        something = Any

    if isinstance( something, FacetFactory ):
        return facet_factory( something )

    if isinstance( something, type ) and issubclass( something, FacetType ):
        return something().as_cfacet()

    if isinstance( something, FacetType ):
        return something.as_cfacet()

    return Facet( something )

# Patch the reference to 'facet_from' in 'facet_handlers.py':
facet_handlers.facet_from = facet_from

#--- 'instance' facets ---------------------------------------------------------

class _InstanceArgs ( object ):

    def __init__ ( self, factory, args, kw ):
        self.args = ( factory, ) + args
        self.kw   = kw

#--- Defines a run-time default value ------------------------------------------

class Default ( object ):
    """ Generates a value the first time it is accessed.

        A Default object can be used anywhere a default facet value would
        normally be specified, to generate a default value dynamically.
    """
    def __init__ ( self, func = None, args = ( ), kw = None ):
        self.default_value = ( func, args, kw )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def Facet ( *value_type, **metadata ):
    """ Creates a facet definition.

    Parameters
    ----------
    This function accepts a variety of forms of parameter lists:

    +-------------------+---------------+-------------------------------------+
    | Format            | Example       | Description                         |
    +===================+===============+=====================================+
    | Facet(*default*)  | Facet(150.0)  | The type of the facet is inferred   |
    |                   |               | from the type of the default value, |
    |                   |               | which must be in *ConstantTypes*.   |
    +-------------------+---------------+-------------------------------------+
    | Facet(*default*,  | Facet(None,   | The facet accepts any of the        |
    | *other1*,         | 0, 1, 2,      | enumerated values, with the first   |
    | *other2*, ...)    | 'many')       | value being the default value. The  |
    |                   |               | values must be of types in          |
    |                   |               | *ConstantTypes*, but they need not  |
    |                   |               | be of the same type. The *default*  |
    |                   |               | value is not valid for assignment   |
    |                   |               | unless it is repeated later in the  |
    |                   |               | list.                               |
    +-------------------+---------------+-------------------------------------+
    | Facet([*default*, | Facet([None,  | Similar to the previous format, but |
    | *other1*,         | 0, 1, 2,      | takes an explicit list or a list    |
    | *other2*, ...])   | 'many'])      | variable.                           |
    +-------------------+---------------+-------------------------------------+
    | Facet(*type*)     | Facet(Int)    | The *type* parameter must be a name |
    |                   |               | of a Python type (see               |
    |                   |               | *PythonTypes*). Assigned values     |
    |                   |               | must be of exactly the specified    |
    |                   |               | type; no casting or coercion is     |
    |                   |               | performed. The default value is the |
    |                   |               | appropriate form of zero, False,    |
    |                   |               | or emtpy string, set or sequence.   |
    +-------------------+---------------+-------------------------------------+
    | Facet(*class*)    |::             | Values must be instances of *class* |
    |                   |               | or of a subclass of *class*. The    |
    |                   | class MyClass:| default value is None, but None     |
    |                   |    pass       | cannot be assigned as a value.      |
    |                   | foo = Facet(  |                                     |
    |                   | MyClass)      |                                     |
    +-------------------+---------------+-------------------------------------+
    | Facet(None,       |::             | Similar to the previous format, but |
    | *class*)          |               | None *can* be assigned as a value.  |
    |                   | class MyClass:|                                     |
    |                   |   pass        |                                     |
    |                   | foo = Facet(  |                                     |
    |                   | None, MyClass)|                                     |
    +-------------------+---------------+-------------------------------------+
    | Facet(*instance*) |::             | Values must be instances of the     |
    |                   |               | same class as *instance*, or of a   |
    |                   | class MyClass:| subclass of that class. The         |
    |                   |    pass       | specified instance is the default   |
    |                   | i = MyClass() | value.                              |
    |                   | foo =         |                                     |
    |                   |   Facet(i)    |                                     |
    +-------------------+---------------+-------------------------------------+
    | Facet(*handler*)  | Facet(        | Assignment to this facet is         |
    |                   | FacetEnum )   | validated by an object derived from |
    |                   |               | **facets.core.FacetHandler**.  |
    +-------------------+---------------+-------------------------------------+
    | Facet(*default*,  | Facet(0.0, 0.0| This is the most general form of    |
    | { *type* |        | 'stuff',      | the function. The notation:         |
    | *constant* |      | TupleType)    | ``{...|...|...}+`` means a list of  |
    | *dict* | *class* ||               | one or more of any of the items     |
    | *function* |      |               | listed between the braces. Thus, the|
    | *handler* |       |               | most general form of the function   |
    | *facet* }+ )      |               | consists of a default value,        |
    |                   |               | followed by one or more of several  |
    |                   |               | possible items. A facet defined by  |
    |                   |               | multiple items is called a          |
    |                   |               | "compound" facet.                   |
    +-------------------+---------------+-------------------------------------+

    All forms of the Facet function accept both predefined and arbitrary
    keyword arguments. The value of each keyword argument becomes bound to the
    resulting facet object as the value of an attribute having the same name
    as the keyword. This feature lets you associate metadata with a facet.

    The following predefined keywords are accepted:

    desc : string
        Describes the intended meaning of the facet. It is used in
        exception messages and fly-over help in user interfaces.
    label : string
        Provides a human-readable name for the facet. It is used to label user
        interface editors for facets.
    editor : instance of a subclass of facets.core_api.Editor
        Object to use when creating a user interface editor for the facet. See
        the "Facets UI User Guide" for more information on facet editors.
    comparison_mode : integer
        Indicates when facet change notifications should be generated based upon
        the result of comparing the old and new values of a facet assignment:
            0 (NO_COMPARE): The values are not compared and a facet change
                notification is generated on each assignment.
            1 (OBJECT_IDENTITY_COMPARE): A facet change notification is
                generated if the old and new values are not the same object.
            2 (RICH_COMPARE): A facet change notification is generated if the
                old and new values are not equal using Python's
                'rich comparison' operator. This is the default.
    rich_compare : Boolean (DEPRECATED: Use comparison_mode instead)
        Indicates whether the basis for considering a facet attribute value to
        have changed is a "rich" comparison (True, the default), or simple
        object identity (False). This attribute can be useful in cases
        where a detailed comparison of two objects is very expensive, or where
        you do not care whether the details of an object change, as long as the
        same object is used.

    """
    return _FacetMaker( *value_type, **metadata ).as_cfacet()

#  Handle circular module dependencies:
facet_handlers.Facet = Facet

#-------------------------------------------------------------------------------
#  '_FacetMaker' class:
#-------------------------------------------------------------------------------

class _FacetMaker ( object ):

    #-- Class Constants --------------------------------------------------------

    # Cfacet type map for special facet types:
    type_map = {
       'event':    2,
       'constant': 7
    }

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, *value_type, **metadata ):
        """ Initializes the object.
        """
        metadata.setdefault( 'type', 'facet' )
        self.define( *value_type, **metadata )


    def define ( self, *value_type, **metadata ):
        """ Defines the facet.
        """
        default_value_type = -1
        default_value      = handler = clone = None

        if len( value_type ) > 0:
            default_value = value_type[0]
            value_type    = value_type[1:]

            if ((len( value_type ) == 0) and
                (type( default_value ) in SequenceTypes)):
                default_value, value_type = default_value[0], default_value

            if len( value_type ) == 0:
                default_value = try_facet_cast( default_value )

                if default_value in PythonTypes:
                    handler       = FacetCoerceType( default_value )
                    default_value = DefaultValues.get( default_value )

                elif isinstance( default_value, CFacet ):
                    clone = default_value
                    default_value_type, default_value = clone.default_value()
                    metadata[ 'type' ] = clone.type

                elif isinstance( default_value, FacetHandler ):
                    handler       = default_value
                    default_value = None

                elif default_value is ThisClass:
                    handler       = ThisClass()
                    default_value = None

                else:
                    typeValue = type( default_value )

                    if isinstance( default_value, basestring ):
                        string_options = self.extract( metadata, 'min_len',
                                                       'max_len', 'regex' )
                        if len( string_options ) == 0:
                            handler = FacetCastType( typeValue )
                        else:
                            handler = FacetString( **string_options )

                    elif typeValue in TypeTypes:
                        handler = FacetCastType( typeValue )

                    else:
#                       from facet_types import Instance
#
                        metadata.setdefault( 'instance_handler',
                                             '_instance_changed_handler' )
#                       handler = Instance( default_value )
#                       if default_value is handler.klass:
                        handler = FacetInstance( default_value )
                        if default_value is handler.aClass:
                            default_value = DefaultValues.get( default_value )
            else:
                enum  = []
                other = []
                map   = {}
                self.do_list( value_type, enum, map, other )

                if (((len( enum )  == 1) and (enum[0] is None)) and
                    ((len( other ) == 1) and
                     isinstance( other[0], FacetInstance ))):
                    enum = []
                    other[0].allow_none()
                    metadata.setdefault( 'instance_handler',
                                         '_instance_changed_handler' )
                if len( enum ) > 0:
                    if (((len( map ) + len( other ) ) == 0) and
                        (default_value not in enum )):
                        enum.insert( 0, default_value )

                    from facet_types import Enum

                    other.append( Enum( enum ) )

                if len( map ) > 0:
                    other.append( FacetMap( map ) )

                if len( other ) == 0:
                    handler = FacetHandler()

                elif len( other ) == 1:
                    handler = other[0]
                    if isinstance( handler, CFacet ):
                        clone, handler = handler, None
                        metadata[ 'type' ] = clone.type

                    elif isinstance( handler, FacetInstance ):
                        metadata.setdefault( 'instance_handler',
                                             '_instance_changed_handler' )

                        if default_value is None:
                            handler.allow_none()

                        elif isinstance( default_value, _InstanceArgs ):
                            default_value_type = 7
                            default_value = ( handler.create_default_value,
                                default_value.args, default_value.kw )

                        elif (len( enum ) == 0) and (len( map ) == 0):
                            aClass    = handler.aClass
                            typeValue = type( default_value )

                            if typeValue is dict:
                                default_value_type = 7
                                default_value = ( aClass, (), default_value )
                            elif not isinstance( default_value, aClass ):
                                if typeValue is not tuple:
                                    default_value = ( default_value, )
                                default_value_type = 7
                                default_value = ( aClass, default_value, None )
                else:
                    for i, item in enumerate( other ):
                        if isinstance( item, CFacet ):
                            if item.type != 'facet':
                                raise FacetError(
                                    "Cannot create a complex facet containing "
                                    "%s facet." % add_article( item.type )
                                )

                            handler = item.handler
                            if handler is None:
                                break

                            other[ i ] = handler
                    else:
                        handler = FacetCompound( other )

        # Save the results:
        self.handler = handler
        self.clone   = clone

        if default_value_type < 0:
            if isinstance( default_value, Default ):
                default_value_type = 7
                default_value      = default_value.default_value
            else:
                if (handler is None) and (clone is not None):
                    handler = clone.handler

                if handler is not None:
                    default_value_type = handler.default_value_type
                    if default_value_type < 0:
                        try:
                            default_value = handler.validate( None, '',
                                                              default_value )
                        except:
                            pass

                if default_value_type < 0:
                    default_value_type = _default_value_type( default_value )

        self.default_value_type = default_value_type
        self.default_value      = default_value
        self.metadata           = metadata.copy()


    def do_list ( self, list, enum, map, other ):
        """ Determines the correct FacetHandler for each item in a list.
        """
        for item in list:
            if item in PythonTypes:
                other.append( FacetCoerceType( item ) )
            else:
                item     = try_facet_cast( item )
                typeItem = type( item )

                if typeItem in ConstantTypes:
                    enum.append( item )

                elif typeItem in SequenceTypes:
                    self.do_list( item, enum, map, other )

                elif typeItem is DictType:
                    map.update( item )

                elif typeItem in CallableTypes:
                    other.append( FacetFunction( item ) )

                elif item is ThisClass:
                    other.append( ThisClass() )

                elif isinstance( item, FacetTypes ):
                    other.append( item )

                else:
                    other.append( FacetInstance( item ) )
#                   from facet_types import Instance
#
#                   other.append( Instance( item ) )


    def as_cfacet ( self ):
        """ Returns a properly initialized 'CFacet' instance.
        """
        metadata = self.metadata
        facet    = CFacet( self.type_map.get( metadata.get( 'type' ), 0 ) )
        clone    = self.clone
        if clone is not None:
            facet.clone( clone )
            if clone.__dict__ is not None:
                facet.__dict__ = clone.__dict__.copy()

        facet.default_value( self.default_value_type, self.default_value )

        handler = self.handler
        if handler is not None:
            facet.handler = handler
            validate      = getattr( handler, 'fast_validate', None )
            if validate is None:
                validate = handler.validate

            facet.set_validate( validate )

            post_setattr = getattr( handler, 'post_setattr', None )
            if post_setattr is not None:
                facet.post_setattr = post_setattr
                facet.is_mapped( handler.is_mapped )

        # Note: The use of 'rich_compare' metadata is deprecated; use
        # 'comparison_mode' metadata instead:
        rich_compare = metadata.get( 'rich_compare' )
        if rich_compare is not None:
            facet.rich_comparison( rich_compare is True )

        comparison_mode = metadata.get( 'comparison_mode' )
        if comparison_mode is not None:
            facet.comparison_mode( comparison_mode )

        facet.value_allowed( metadata.get( 'facet_value', False ) is True )

        if len( metadata ) > 0:
            if facet.__dict__ is None:
                facet.__dict__ = metadata
            else:
                facet.__dict__.update( metadata )

        return facet


    def extract ( self, from_dict, *keys ):
        """ Extracts a set of keywords from a dictionary.
        """
        to_dict = {}
        for key in keys:
            if key in from_dict:
                to_dict[ key ] = from_dict[ key ]
                del from_dict[ key ]
        return to_dict

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def Property ( fget = None, fset = None, fvalidate = None, force = False,
               handler = None, facet = None, **metadata ):
    """ Returns a facet whose value is a Python property.

        Parameters
        ----------
        fget : function
            The "getter" function for the property
        fset : function
            The "setter" function for the property
        fvalidate : function
            The validation function for the property
        force : Boolean
            Indicates whether to use only the function definitions spedficied by
            **fget** and **fset**, and not look elsewhere on the class.
        handler : function
            A facet handler function for the facet
        facet : a facet definition or value that can be converted to a facet
            A facet definition that constrains the values of the property facet

        Description
        -----------
        If no getter or setter functions are specified (and **force** is not
        True), it is assumed that they are defined elsewhere on the class whose
        attribute this facet is assigned to. For example::

            class Bar(HasFacets):
                foo = Property(Float)
                # Shadow facet attribute
                _foo = Float

                def _set_foo(self,x):
                    self._foo = x

                def _get_foo(self):
                    return self._foo

        You can use the **depends_on** metadata attribute to indicate that the
        property depends on the value of another facet. The value of
        **depends_on** is an extended name specifier for facets that the
        property depends on. The property will a facet change notification if
        any of the facets specified by **depends_on** change. For example::

            class Wheel ( Part ):
                axle     = Instanced( Axle )
                position = Property( depends_on = 'axle.chassis.position' )

        For details of the extended facet name syntax, refer to the
        on_facet_set() method of the HasFacets class.
    """
    metadata[ 'type' ] = 'property'

    # If no parameters specified, must be a forward reference (if not forced):
    if (not force) and (fset is None):
        sum = ((fget      is not None) +
               (fvalidate is not None) +
               (facet     is not None))
        if sum <= 1:
            if sum == 0:
                return ForwardProperty( metadata )

            handler = None
            if fget is not None:
                facet = fget

            if facet is not None:
                facet = facet_cast( facet )
                if facet is not None:
                    fvalidate = handler = facet.handler
                    if fvalidate is not None:
                        fvalidate = handler.validate

            if (fvalidate is not None) or (facet is not None):
                if 'editor' not in metadata:
                    if (facet is not None) and (facet.editor is not None):
                        metadata[ 'editor' ] = facet.editor

                return ForwardProperty( metadata, fvalidate, handler )

    if fget is None:
        metadata[ 'transient' ] = True
        if fset is None:
            fget = _undefined_get
            fset = _undefined_set
        else:
            fget = _write_only

    elif fset is None:
        fset = _read_only
        metadata[ 'transient' ] = True

    if facet is not None:
        facet   = facet_cast( facet )
        handler = facet.handler
        if (fvalidate is None) and (handler is not None):
            fvalidate = handler.validate

        if ('editor' not in metadata) and (facet.editor is not None):
            metadata[ 'editor' ] = facet.editor

    metadata.setdefault( 'depends_on', getattr( fget, 'depends_on', None ) )
    if ((metadata.get( 'depends_on' ) is not None) and
         getattr( fget, 'cached_property', False )):
        metadata.setdefault( 'cached', True )

    n     = 0
    facet = CFacet( 4 )
    facet.__dict__ = metadata.copy()
    if fvalidate is not None:
        n = _arg_count( fvalidate )

    facet.property( fget,      _arg_count( fget ),
                    fset,      _arg_count( fset ),
                    fvalidate, n )
    facet.handler = handler

    return facet

Property = FacetFactory( Property )

#-------------------------------------------------------------------------------
#  'ForwardProperty' class:
#-------------------------------------------------------------------------------

class ForwardProperty ( object ):
    """ Used to implement Property facets where accessor functions are defined
        implicitly on the class.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, metadata, validate = None, handler = None ):
        """ Initializes the object.
        """
        self.metadata = metadata.copy()
        self.validate = validate
        self.handler  = handler

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Dictionary used to handle return type mapping special cases:
SpecialNames = {
###   'int':     facet_factory( Int ),
###   'long':    facet_factory( Long ),
###   'float':   facet_factory( Float ),
###   'complex': facet_factory( Complex ),
###   'str':     facet_factory( Str ),
###   'unicode': facet_factory( Unicode ),
###   'bool':    facet_factory( Bool ),
###   'list':    facet_factory( List ),
###   'tuple':   facet_factory( Tuple ),
###   'dict':    facet_factory( Dict )
}

# Generic facet with 'object' behavior:
generic_facet = CFacet( 8 )

#-------------------------------------------------------------------------------
#  User interface related color and font facets:
#-------------------------------------------------------------------------------

def Color ( *args, **metadata ):
    """ Returns a facet whose value must be a GUI toolkit-specific color.

        Description
        -----------
        The returned facet accepts any of the following values:

        * A GUI toolkit specific color instance
        * An integer whose hexadecimal form is 0x*RRGGBB*, where *RR* is the red
          value, *GG* is the green value, and *BB* is the blue value

        Default Value
        -------------
        White
    """
    from facets.ui.core_editors import ColorFacet

    return ColorFacet( *args, **metadata )

Color = FacetFactory( Color )


def RGBColor ( *args, **metadata ):
    """ Returns a facet whose value must be a GUI toolkit-specific RGB-based
        color.

        Description
        -----------
        The returned facet accepts any of the following values:

        * A tuple of the form (*r*, *g*, *b*), in which *r*, *g*, and *b*
          represent red, green, and blue values, respectively, and are floats in the range
          from 0.0 to 1.0
        * An integer whose hexadecimal form is 0x*RRGGBB*, where *RR* is the red
          value, *GG* is the green value, and *BB* is the blue value

        Default Value
        -------------
        White
    """
    from facets.ui.core_editors import RGBColorFacet

    return RGBColorFacet( *args, **metadata )

RGBColor = FacetFactory( RGBColor )


def Font ( *args, **metadata ):
    """ Returns a facet whose value must be a GUI toolkit-specific font.

        Description
        -----------
        The returned facet accepts any of the following:

        * A GUI toolkit specific font instance
        * A string describing the font, including one or more of the font
          family, size, weight, style, and typeface name.

        Default Value
        -------------
        'Arial 10'
    """
    from facets.ui.core_editors import FontFacet

    return FontFacet( *args, **metadata )

Font = FacetFactory( Font )

#-- EOF ------------------------------------------------------------------------