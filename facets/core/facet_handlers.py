"""
Defines the BaseFacetHandler class and a standard set of BaseFacetHandler
subclasses for use with the Facets package.

A facet handler mediates the assignment of values to object facets. It
verifies (via its validate() method) that a specified value is consistent
with the object facet, and generates a FacetError exception if it is not
consistent.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import re

from facets.core.protocols.api \
    import adapt

from types \
    import InstanceType, TypeType, FunctionType, MethodType

from cfacets \
    import CFacetMethod

from facet_base \
    import strx, SequenceTypes, Undefined, TypeTypes, ClassTypes, \
           CoercableTypes, FacetsCache, class_of, Missing

from facet_collections \
    import FacetListObject, FacetListEvent, FacetDictObject, FacetSetObject

from facet_errors \
    import FacetError

# Patched by 'facets.py' once class is defined!
Facet = Event = None

# Set up a logger:
import logging
logger = logging.getLogger( __name__ )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Facet 'comparison_mode' enum values:
NO_COMPARE              = 0
OBJECT_IDENTITY_COMPARE = 1
RICH_COMPARE            = 2

RangeTypes    = ( int, long, float )

CallableTypes = ( FunctionType, MethodType, CFacetMethod )

# Mapping from facet metadata 'type' to CFacet 'type':
facet_types = {
    'python': 1,
    'event':  2
}

#-------------------------------------------------------------------------------
#  Forward references:
#-------------------------------------------------------------------------------

facet_from = None  # Patched by 'facets.py' when real 'facet_from' is defined

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def deprecated ( value ):
    """ Displays a deprecation warning for *value*.
    """
    from facets.extra.helper.debug import log, called_from

    log( 'Use of %s is deprecated.' % value.__class__.__name__ )
    called_from(10)


def _arg_count ( func ):
    """ Returns the correct argument count for a specified function or method.
    """
    if (type( func ) is MethodType) and (func.im_self is not None):
        return (func.func_code.co_argcount - 1)

    return func.func_code.co_argcount

#-- Property Error Handling Functions ------------------------------------------

def _write_only ( object, name ):
    raise FacetError(
        "The '%s' facet of %s instance is 'write only'." %
        ( name, class_of( object ) )
    )


def _read_only ( object, name, value ):
    raise FacetError(
        "The '%s' facet of %s instance is 'read only'." %
        ( name, class_of( object ) )
    )


def _undefined_get ( object, name ):
    raise FacetError(
        ("The '%s' facet of %s instance is a property that has no 'get' or "
         "'set' method") % ( name, class_of( object ) )
    )


def _undefined_set ( object, name, value ):
    _undefined_get( object, name )

#-------------------------------------------------------------------------------
#  'BaseFacetHandler' class (base class for all user defined facets and facet
#  handlers):
#-------------------------------------------------------------------------------

class BaseFacetHandler ( object ):
    """ The task of this class and its subclasses is to verify the correctness
        of values assigned to object facet attributes.

        This class is an alternative to facet validator functions. A facet
        handler has several advantages over a facet validator function, due to
        being an object:

            * Facet handlers have constructors and state. Therefore, you can use
              them to create *parameterized types*.
            * Facet handlers can have multiple methods, whereas validator
              functions can have only one callable interface. This feature
              allows more flexibility in their implementation, and allows them
              to handle a wider range of cases, such as interactions with other
              components.
    """

    #-- Class Constants --------------------------------------------------------

    default_value_type = -1
    collection_type    = 'none'
    has_items          = False
    is_mapped          = False
    editor             = None
    info_text          = 'a legal value'

    #-- Public Methods ---------------------------------------------------------

    def is_valid ( self, object, name, value ):
        try:
            validate = self.validate
            try:
                validate( object, name, value )
                return True
            except:
                return False
        except:
            return True


    def error ( self, object, name, value ):
        """ Raises a FacetError exception.

            Parameters
            ----------
            object : object
                The object whose attribute is being assigned
            name : string
                The name of the attribute being assigned
            value
                The proposed new value for the attribute

            Description
            -----------
            This method is called by the validate() method when an assigned
            value is not valid. Raising a FacetError exception either notifies
            the user of the problem, or, in the case of compound facets,
            provides a chance for another facet handler to handle to validate
            the value.
        """
        raise FacetError(
            object, name, self.full_info( object, name, value ), value
        )


    def arg_error ( self, method, arg_num, object, name, value ):
        """ Raises a FacetError exception to notify the user that a method on
            an instance received a positional argument of an incorrect type.

            Parameters
            ----------
            method : function
                The method that encountered the error
            arg_num : integer
                The position of the incorrect argument in the argument list
            object : object
                The object whose method was called
            name : string
                The name of the parameter corresponding to the incorrect
                argument
            value
                The value passed to the argument

            Description
            -----------
            This method can be called when type-checking a method.
        """
        raise FacetError(
            ("The '%s' parameter (argument %d) of the %s method of %s instance "
             "must be %s, but a value of %s was specified.") %
            ( name, arg_num, method.tm_name, class_of( object ),
              self.full_info( object, name, value ), value )
        )


    def keyword_error ( self, method, object, name, value ):
        """ Raises a FacetError exception to notify the user that a method on
            an instance received a keyword argument of an incorrect type.

            Parameters
            ----------
            method : function
                The method that encountered the error
            object : object
                The object whose method was called
            name : string
                The name of the parameter corresponding to the incorrect
                argument
            value
                The value passed to the argument

            Description
            -----------
            This method can be called when type-checking a method.
        """
        raise FacetError(
            ("The '%s' keyword argument of the %s method of %s instance must "
             "be %s, but a value of %s was specified.") %
            ( name, method.tm_name, class_of( object ),
              self.info( object, name, value ), value )
        )


    def missing_arg_error ( self, method, arg_num, object, name ):
        """ Raises a FacetError exception to notify the user that a method on
            an instance failed to receive a required positional argument.

            Parameters
            ----------
            method : function
                The method that encountered the error
            arg_num : integer
                The position of the incorrect argument in the argument list
            object : object
                The object whose method was called
            name : string
                The name of the parameter corresponding to the incorrect
                argument

            Description
            -----------
            This method can be called when type-checking a method.
        """
        raise FacetError(
            ("The '%s' parameter (argument %d) of the %s method of %s instance "
             "must be specified, but was omitted.") %
            ( name, arg_num, method.tm_name, class_of( object ) )
        )


    def dup_arg_error ( self, method, arg_num, object, name ):
        """ Raises a FacetError exception to notify the user that a method on
            an instance received an argument as both a keyword argument and a
            positional argument.

            Parameters
            ----------
            method : function
                The method that encountered the error
            arg_num : integer
                The position of the incorrect argument in the argument list
            object : object
                The object whose method was called
            name : string
                The name of the parameter corresponding to the incorrect
                argument

            Description
            -----------
            This method can be called when type-checking a method.
        """
        raise FacetError(
            ("The '%s' parameter (argument %d) of the %s method of %s instance "
             "was specified as both a positional and keyword value.") %
            ( name, arg_num, method.tm_name, class_of( object ) )
        )


    def return_error ( self, method, object, value ):
        """ Raises a FacetError exception to notify the user that a method on
            an instance returned a value of incorrect type.

            Parameters
            ----------
            method : function
                The method that encountered the error
            object : object
                The object whose method was called
            value
                The value returned by the method

            Description
            -----------
            This method can be called when type-checking a method.
        """
        raise FacetError(
            ("The result of the %s method of %s instance must be %s, but a "
             "value of %s was returned.") %
            ( method.tm_name, class_of( object ), self.info(), value )
        )


    def full_info ( self, object, name, value ):
        """ Returns a string describing the type of value accepted by the
            facet handler.

            Parameters
            ----------
            object : object
                The object whose attribute is being assigned
            name : string
                The name of the attribute being assigned
            value
                The proposed new value for the attribute

            Description
            -----------
            The string should be a phrase describing the type defined by the
            FacetHandler subclass, rather than a complete sentence. For example,
            use the phrase, "a square sprocket" instead of the sentence, "The
            value must be a square sprocket." The value returned by full_info()
            is combined with other information whenever an error occurs and
            therefore makes more sense to the user if the result is a phrase.
            The full_info() method is similar in purpose and use to the **info**
            attribute of a validator function.

            Note that the result can include information specific to the
            particular facet handler instance. For example, a range handler
            might return a string indicating the range of values acceptable to
            the handler (e.g., "an integer in the range from 1 to 9"). If the
            full_info() method is not overridden, the default method returns the
            value of calling the info() method.
        """
        return self.info()


    def info ( self ):
        """ Must return a string describing the type of value accepted by the
            facet handler.

            The string should be a phrase describing the type defined by the
            FacetHandler subclass, rather than a complete sentence. For example,
            use the phrase, "a square sprocket" instead of the sentence, "The
            value must be a square sprocket." The value returned by info() is
            combined with other information whenever an error occurs and
            therefore makes more sense to the user if the result is a phrase.
            The info() method is similar in purpose and use to the **info**
            attribute of a validator function.

            Note that the result can include information specific to the
            particular facet handler instance. For example, a range handler
            might return a string indicating the range of values acceptable to
            the handler (e.g., "an integer in the range from 1 to 9"). If the
            info() method is not overridden, the default method returns the
            value of the 'info_text' attribute.
        """
        return self.info_text


    def repr ( self, value ):
        """ Returns a printable representation of a value.

            Parameters
            ----------
            value
                The value to be printed

            Description
            -----------
            If *value* is an instance, the method returns the printable
            representation of the instance's class.
        """
        if type( value ) is InstanceType:
            return 'class '  + value.__class__.__name__

        return repr( value )


    def string_value ( self, object, name, value ):
        """ Returns the string value for the specified *value*.
        """
        return str( value )


    def get_editor ( self, facet = None ):
        """ Returns a facet editor that allows the user to modify the *facet*
            facet.

            Parameters
            ----------
            facet : facet
                The facet to be edited

            Description
            -----------
            This method only needs to be specified if facets defined using this
            facet handler require a non-default facet editor in facet user
            interfaces. The default implementation of this method returns a
            facet editor that allows the user to type an arbitrary string as the
            value.

            For more information on facet user interfaces, refer to the *Facets
            UI User Guide*.
        """
        if self.editor is None:
            self.editor = self.create_editor()

        return self.editor


    def create_editor ( self ):
        """ Returns the default facets UI editor to use for a facet.
        """
        from facets.api import TextEditor

        return TextEditor()


    def inner_facets ( self ):
        """ Returns a tuple containing the *inner facets* for this facet. Most
            facet handlers do not have any inner facets, and so will return an
            empty tuple. The exceptions are **List** and **Dict** facet types,
            which have inner facets used to validate the values assigned to the
            facet. For example, in *List( Int )*, the *inner facets* for
            **List** are ( **Int**, ).
        """
        return ()

#-------------------------------------------------------------------------------
#  'FacetType' (base class for class-based facet definitions:
#-------------------------------------------------------------------------------

# Create a singleton object for use in the FacetType constructor:
class NoDefaultSpecified ( object ): pass
NoDefaultSpecified = NoDefaultSpecified()

class FacetType ( BaseFacetHandler ):
    """ Base class for new facet types.

        This class enables you to define new facets using a class-based
        approach, instead of by calling the Facet() factory function with an
        instance of a FacetHandler derived object.

        When subclassing this class, you can implement one or more of the
        method signatures below. Note that these methods are defined only as
        comments, because the absence of method definitions in the subclass
        definition implicitly provides information about how the facet should
        operate.

        The optional methods are as follows:

        * **get ( self, object, name ):**

          This is the getter method of a facet that behaves like a property.

          *Parameters*

          object : an object
              The object that the property applies to.
          name : string
              The name of the property on *object* property.

          *Description*

          If neither this method nor the set() method is defined, the value
          of the facet is handled like a normal object attribute. If this
          method is not defined, but the set() method is defined, the facet
          behaves like a write-only property. This method should return the
          value of the *name* property for the *object* object.

        * **set ( self, object, name, value )**

          This is the setter method of a facet that behaves like a property.

          *Parameters*

          object : instance
              The object that the property applies to.
          name : string
              The name of the property on *object*.
          value : any
              The value being assigned as the value of the property.

          *Description*

          If neither this method nor the get() method is implemented, the
          facet behaves like a normal facet attribute. If this method is not
          defined, but the get() method is defined, the facet behaves like a
          read-only property. This method does not need to return a value,
          but it should raise a FacetError exception if the specified *value*
          is not valid and cannot be coerced or adapted to a valid value.

        * **validate ( self, object, name, value )**

          This method validates, coerces, or adapts the specified *value* as
          the value of the *name* facet of the *object* object. This method
          is called when a value is assigned to an object facet that is
          based on this subclass of *FacetType* and the class does not
          contain a definition for either the get() or set() methods. This
          method must return the original *value* or any suitably coerced or
          adapted value that is a legal value for the facet. If *value* is
          not a legal value for the facet, and cannot be coerced or adapted
          to a legal value, the method should either raise a **FacetError** or
          call the **error** method to raise the **FacetError** on its behalf.

        * **is_valid_for ( self, value )**

          As an alternative to implementing the **validate** method, you can
          instead implement the **is_valid_for** method, which receives only
          the *value* being assigned. It should return **True** if the value is
          valid, and **False** otherwise.

        * **value_for ( self, value )**

          As another alternative to implementing the **validate** method, you
          can instead implement the **value_for** method, which receives only
          the *value* being assigned. It should return the validated form of
          *value* if it is valid, or raise a **FacetError** if the value is not
          valid.

        * **post_setattr ( self, object, name, value )**

          This method allows the facet to do additional processing after
          *value* has been successfully assigned to the *name* facet of the
          *object* object. For most facets there is no additional processing
          that needs to be done, and this method need not be defined. It is
          normally used for creating "shadow" (i.e., "mapped" facets), but
          other uses may arise as well. This method does not need to return
          a value, and should normally not raise any exceptions.
    """

    #-- Class Constants --------------------------------------------------------

    default_value = Undefined
    metadata      = {}

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, default_value = NoDefaultSpecified, **metadata ):
        """ This constructor method is the only method normally called
            directly by client code. It defines the facet. The
            default implementation accepts an optional, untype-checked default
            value, and caller-supplied facet metadata. Override this method
            whenever a different method signature or a type-checked
            default value is needed.
        """
        if default_value is not NoDefaultSpecified:
            self.default_value = default_value

        if len( metadata ) > 0:
            if len( self.metadata ) > 0:
                self._metadata = self.metadata.copy()
                self._metadata.update( metadata )
            else:
                self._metadata = metadata
        else:
            self._metadata = self.metadata

        self.init()


    def init ( self ):
        """ Allows the facet to perform any additional initialization needed.
        """
        pass


    def get_default_value ( self ):
        """ Returns a tuple of the form: (*default_value_type*, *default_value*)
            which describes the default value for this facet. The default
            implementation analyzes the value of the facet's **default_value**
            attribute and determines an appropriate *default_value_type* for
            *default_value*. If you need to override this method to provide a
            different result tuple, the following values are valid values for
            *default_value_type*:

                - 0, 1: The *default_value* item of the tuple is the default
                  value.
                - 2: The object containing the facet is the default value.
                - 3: A new copy of the list specified by *default_value* is
                  the default value.
                - 4: A new copy of the dictionary specified by *default_value*
                  is the default value.
                - 5: A new instance of the class specified by
                  *default_value_class* whose value is a copy of
                  *default_value*. Used to create default values which are some
                  type of collection (e.g. list, dict, set).
                - 7: *default_value* is a tuple of the form: (*callable*,
                  *args*, *kw*), where *callable* is a callable, *args* is a
                  tuple, and *kw* is either a dictionary or None. The default
                  value is the result obtained by invoking callable(\*args,
                  \*\*kw).
                - 8: *default_value* is a callable. The default value is the
                  result obtained by invoking *default_value*(*object*), where
                  *object* is the object containing the facet. If the facet has
                  a validate() method, the validate() method is also called to
                  validate the result.
        """
        dv  = self.default_value
        dvt = self.default_value_type
        if dvt < 0:
            dvt = 0
            if isinstance( dv, FacetListObject ):
                dvt = 5
                dv  = ( FacetListObject, dv )
            elif isinstance( dv, list ):
                dvt = 3
            elif isinstance( dv, FacetDictObject ):
                dvt = 5
                dv  = ( FacetDictObject, dv )
            elif isinstance( dv, dict ):
                dvt = 4
            elif isinstance( dv, FacetSetObject ):
                dvt = 5
                dv  = ( FacetSetObject, dv )

            self.default_value_type = dvt
        elif dvt == 5:
            dv = ( self.default_value_class, dv )

        return ( dvt, dv )


    def clone ( self, default_value = Missing, **metadata ):
        """ Clones the contents of this object into a new instance of the same
            class, and then modifies the cloned copy using the specified
            *default_value* and *metadata*. Returns the cloned object as the
            result.

            Note that subclasses can change the signature of this method if
            needed, but should always call the 'super' method if possible.
        """
        if 'parent' not in metadata:
            metadata[ 'parent' ] = self

        new      = self.__class__.__new__( self.__class__ )
        new_dict = new.__dict__
        new_dict.update( self.__dict__ )

        if 'editor' in new_dict:
            del new_dict[ 'editor' ]

        if '_metadata' in new_dict:
            new._metadata = new._metadata.copy()
        else:
            new._metadata = {}

        new._metadata.update( metadata )

        if default_value is not Missing:
            new.default_value = default_value
            if self.validate is not None:
                try:
                    new.default_value = self.validate( None, None,
                                                       default_value )
                except:
                    pass

        return new

    def get_value ( self, object, name, facet = None ):
        """ Returns the current value of a property-based facet.
        """
        cname = FacetsCache + name
        value = object.__dict__.get( cname, Undefined )
        if value is Undefined:
            if facet is None:
                facet = object.facet( name )

            object.__dict__[ cname ] = value = \
                facet.default_value_for( object, name )

        return value


    def set_value ( self, object, name, value ):
        """ Sets the cached value of a property-based facet and fires the
            appropriate facet change event.
        """
        cname = FacetsCache + name
        old   = object.__dict__.get( cname, Undefined )
        if value != old:
            object.__dict__[ cname ] = value
            object.facet_property_set( name, old, value )


    def settings ( self, *names ):
        """ Returns a dictionary containing the metadata values for the
            specified list of *names*. If the metadata value for a particular
            name is **None**, it is omitted from the results dictionary.
        """
        result = {}
        for name in names:
            value = getattr( self, name )
            if value is not None:
                result[ name ] = value

        return result

    #-- Private Methods --------------------------------------------------------

    def __call__ ( self, *args, **kw ):
        """ Allows a derivative facet to be defined from this one.
        """
        return self.clone( *args, **kw ).as_cfacet()


    def _is_valid_for ( self, object, name, value ):
        """ Handles a simplified validator that only returns whether or not the
            original value is valid.
        """
        if self.is_valid_for( value ):
            return value

        self.error( object, name, value )


    def _value_for ( self, object, name, value ):
        """ Handles a simplified validator that only receives the value
            argument.
        """
        try:
            return self.value_for( value )
        except FacetError:
            self.error( object, name, value )


    def as_cfacet ( self ):
        """ Returns a CFacet corresponding to the facet defined by this class.
        """
        from facet_defs import CFacet

        metadata = getattr( self, '_metadata', {} )
        getter   = getattr( self, 'get', None )
        setter   = getattr( self, 'set', None )
        if (getter is not None) or (setter is not None):
            if getter is None:
                getter = _write_only
                metadata.setdefault( 'transient', True )
            elif setter is None:
                setter = _read_only
                metadata.setdefault( 'transient', True )
            facet    = CFacet( 4 )
            n        = 0
            validate = getattr( self, 'validate', None )
            if validate is not None:
                n = _arg_count( validate )
            facet.property( getter,   _arg_count( getter ),
                            setter,   _arg_count( setter ),
                            validate, n )
            metadata.setdefault( 'type', 'property' )
        else:
            type = getattr( self, 'cfacet_type', None )
            if type is None:
                type = facet_types.get( metadata.get( 'type' ), 0 )
            facet = CFacet( type )

            validate = getattr( self, 'fast_validate', None )
            if validate is None:
                validate = getattr( self, 'validate', None )
                if validate is None:
                    validate = getattr( self, 'is_valid_for', None )
                    if validate is not None:
                        validate = self._is_valid_for
                    else:
                        validate = getattr( self, 'value_for', None )
                        if validate is not None:
                            validate = self._value_for

            if validate is not None:
                facet.set_validate( validate )

            post_setattr = getattr( self, 'post_setattr', None )
            if post_setattr is not None:
                facet.post_setattr = post_setattr
                facet.is_mapped( self.is_mapped )

            # Note: The use of 'rich_compare' metadata is deprecated; use
            # 'comparison_mode' metadata instead:
            rich_compare = metadata.get( 'rich_compare' )
            if rich_compare is not None:
                facet.rich_comparison( rich_compare is True )

            comparison_mode = metadata.get( 'comparison_mode' )
            if comparison_mode is not None:
                facet.comparison_mode( comparison_mode )

            metadata.setdefault( 'type', 'facet' )

        facet.default_value( * self.get_default_value() )

        facet.value_allowed( metadata.get( 'facet_value', False ) is True )

        facet.handler = self

        facet.__dict__ = metadata.copy()

        return facet


    def __getattr__ ( self, name ):
        if (name[:2] == '__') and (name[-2:] == '__'):
            raise AttributeError(
                "'%s' object has no attribute '%s'" %
                ( self.__class__.__name__, name )
            )

        return getattr( self, '_metadata', {} ).get( name, None )

#-------------------------------------------------------------------------------
#  'FacetHandler' class (base class for all facet handlers):
#-------------------------------------------------------------------------------

class FacetHandler ( BaseFacetHandler ):
    """ The task of this class and its subclasses is to verify the correctness
        of values assigned to object facet attributes.

        This class is an alternative to facet validator functions. A facet
        handler has several advantages over a facet validator function, due to
        being an object:

            * Facet handlers have constructors and state. Therefore, you can use
              them to create *parameterized types*.
            * Facet handlers can have multiple methods, whereas validator
              functions can have only one callable interface. This feature
              allows more flexibility in their implementation, and allows them
              to handle a wider range of cases, such as interactions with other
              components.

        The only method of FacetHandler that *must* be implemented by subclasses
        is validate().
    """

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Verifies whether a new value assigned to a facet attribute is valid.

            Parameters
            ----------
            object : object
                The object whose attribute is being assigned
            name : string
                The name of the attribute being assigned
            value
                The proposed new value for the attribute

            Returns
            -------
            If the new value is valid, this method must return either the
            original value passed to it, or an alternate value to be assigned in
            place of the original value. Whatever value this method returns is
            the actual value assigned to *object.name*.

            Description
            -----------
            This method *must* be implemented by subclasses of FacetHandler. It
            is called whenever a new value is assigned to a facet attribute
            defined using this facet handler.

            If the value received by validate() is not valid for the facet
            attribute, the method must called the predefined error() method to
            raise a FacetError exception
        """
        raise FacetError(
            ("The '%s' facet of %s instance has an unknown type. Contact the "
             "developer to correct the problem.") %
            ( name, class_of( object ) )
        )

#-------------------------------------------------------------------------------
#  'FacetString' class:  (DEPRECATED)
#-------------------------------------------------------------------------------

class FacetString ( FacetHandler ):
    """ Ensures that a facet attribute value is a string that satisfied some
        additional, optional constraints.

        The optional constraints include minimum and maximum lengths, and a
        regular expression that the string must match.

        If the value assigned to the facet attribute is a Python numeric type,
        the FacetString handler first coerces the value to a string. Values of
        other non-string types result in a FacetError being raised. The handler
        then makes sure that the resulting string is within the specified length
        range and that it matches the regular expression.

        Example
        -------
        ::

            class Person(HasFacets):
                name = Facet('', FacetString(maxlen=50, regex=r'^[A-Za-z]*$'))

        This example defines a **Person** class with a **name** attribute, which
        must be a string of between 0 and 50 characters that consist of only
        upper and lower case letters.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, minlen = 0, maxlen = sys.maxint, regex = '' ):
        ### deprecated( self )
        """ Creates a FacetString handler.

            Parameters
            ----------
            minlen : integer
                The minimum length allowed for the string
            maxlen : integer
                The maximum length allowed for the string
            regex : string
                A Python regular expression that the string must match

        """
        self.minlen = max( 0, minlen )
        self.maxlen = max( self.minlen, maxlen )
        self.regex  = regex
        self._init()


    def _init ( self ):
        if self.regex != '':
            self.match = re.compile( self.regex ).match
            if (self.minlen == 0) and (self.maxlen == sys.maxint):
                self.validate = self.validate_regex
        elif (self.minlen == 0) and (self.maxlen == sys.maxint):
            self.validate = self.validate_str
        else:
            self.validate = self.validate_len


    def validate ( self, object, name, value ):
        try:
            value = strx( value )
            if ((self.minlen <= len( value ) <= self.maxlen) and
                (self.match( value ) is not None)):
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def validate_str ( self, object, name, value ):
        try:
            return strx( value )
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def validate_len ( self, object, name, value ):
        try:
            value = strx( value )
            if self.minlen <= len( value ) <= self.maxlen:
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def validate_regex ( self, object, name, value ):
        try:
            value = strx( value )
            if self.match( value ) is not None:
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def info ( self ):
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


    def __getstate__ ( self ):
        result = self.__dict__.copy()
        for name in [ 'validate', 'match' ]:
            if name in result:
                del result[ name ]

        return result


    def __setstate__ ( self, state ):
        self.__dict__.update( state )
        self._init()

#-------------------------------------------------------------------------------
#  'FacetCoerceType' class:
#-------------------------------------------------------------------------------

class FacetCoerceType ( FacetHandler ):
    """ Ensures that a value assigned to a facet attribute is of a specified
        Python type, or can be coerced to the specified type.

        FacetCoerceType is the underlying handler for the predefined facets and
        factories for Python simple types. The FacetCoerceType class is also an
        example of a parameterized type, because the single FacetCoerceType
        class allows creating instances that check for totally different sets of
        values. For example::

            class Person(HasFacets):
                name = Facet('', FacetCoerceType(''))
                weight = Facet(0.0, FacetCoerceType(float))

        In this example, the **name** attribute must be of type ``str``
        (string), while the **weight** attribute must be of type ``float``,
        although both are based on instances of the FacetCoerceType class. Note
        that this example is essentially the same as writing::

            class Person(HasFacets):
                name = Facet('')
                weight = Facet(0.0)

        This simpler form is automatically changed by the Facet() function into
        the first form, based on FacetCoerceType instances, when the facet
        attributes are defined.

        For attributes based on FacetCoerceType instances, if a value that is
        assigned is not of the type defined for the facet, a FacetError
        exception is raised. However, in certain cases, if the value can be
        coerced to the required type, then the coerced value is assigned to the
        attribute. Only *widening* coercions are allowed, to avoid any possible
        loss of precision. The following table lists the allowed coercions.

        ----------- ------------------
         Facet Type   Coercible Types
        ----------- ------------------
        complex      float, int
        float        int
        long         int
        unicode      str
        ----------- ------------------
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, aType ):
        """ Creates a FacetCoerceType handler.

            Parameters
            ----------
            aType : type
                Either a Python type (e.g., ``str`` or types.StringType) or a
                Python value (e.g., 'cat')

            Description
            -----------
            If *aType* is a value, it is mapped to its corresponding type. For
            example, the string 'cat' is automatically mapped to ``str`` (i.e.,
            types.StringType).
        """
        if not isinstance( aType, TypeType ):
            aType = type( aType )

        self.aType = aType
        try:
            self.fast_validate = CoercableTypes[ aType ]
        except:
            self.fast_validate = ( 11, aType )


    def validate ( self, object, name, value ):
        fv = self.fast_validate
        tv = type( value )

        # If the value is already the desired type, then return it:
        if tv is fv[1]:
            return value

        # Else see if it is one of the coercable types:
        for typei in fv[2:]:
            if tv is typei:
                # Return the coerced value:
                return fv[1]( value )

        # Otherwise, raise an exception:
        if tv is InstanceType:
            kind = class_of( value )
        else:
            kind = repr( value )

        self.error( object, name, '%s (i.e. %s)' % ( str( tv )[1: -1], kind ) )


    def info ( self ):
        return 'a value of %s' % str( self.aType )[ 1: -1 ]


    def get_editor ( self, facet ):
        # Make the special case of a 'bool' type use the boolean editor:
        if self.aType is bool:
            if self.editor is None:
                from facets.api import BooleanEditor

                self.editor = BooleanEditor()

            return self.editor

        # Otherwise, map all other types to a text editor:
        auto_set = facet.auto_set
        if auto_set is None:
            auto_set = True

        from facets.api import TextEditor

        return TextEditor( auto_set  = auto_set,
                           enter_set = facet.enter_set or False,
                           evaluate  = self.fast_validate[ 1 ] )

#-------------------------------------------------------------------------------
#  'FacetCastType' class:
#-------------------------------------------------------------------------------

class FacetCastType ( FacetCoerceType ):
    """ Ensures that a value assigned to a facet attribute is of a specified
        Python type, or can be cast to the specified type.

        This class is similar to FacetCoerceType, but uses casting rather than
        coercion. Values are cast by calling the type with the value to be
        assigned as an argument. When casting is performed, the result of the
        cast is the value assigned to the facet attribute.

        Any facet that uses a FacetCastType instance in its definition ensures
        that its value is of the type associated with the FacetCastType
        instance. For example::

            class Person(HasFacets):
                name = Facet('', FacetCastType(''))
                weight = Facet(0.0, FacetCastType(float))

        In this example, the **name** facet must be of type ``str`` (string),
        while the **weight** facet must be of type ``float``. Note that this
        example is essentially the same as writing::

            class Person(HasFacets):
                name = CStr
                weight = CFloat

        To understand the difference between FacetCoerceType and FacetCastType
        (and also between Float and CFloat), consider the following example::

            >>>class Person(HasFacets):
            ...    weight = Float
            ...    cweight = CFloat
            >>>
            >>>bill = Person()
            >>>bill.weight = 180    # OK, coerced to 180.0
            >>>bill.cweight = 180   # OK, cast to 180.0
            >>>bill.weight = '180'  # Error, invalid coercion
            >>>bill.cweight = '180' # OK, cast to float('180')
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, aType ):
        """ Creates a FacetCastType handler.

            Parameters
            ----------
            aType : type
                Either a Python type (e.g., ``str`` or types.StringType) or a
                Python value (e.g., ``'cat``)

            Description
            -----------
            If *aType* is a Python value, it is automatically mapped to its
            corresponding Python type. For example, the string 'cat' is
            automatically mapped to ``str`` (i.e., types.StringType).
        """
        if not isinstance( aType, TypeType ):
            aType = type( aType )

        self.aType = aType
        self.fast_validate = ( 12, aType )


    def validate ( self, object, name, value ):

        # If the value is already the desired type, then return it:
        if type( value ) is self.aType:
            return value

        # Else try to cast it to the specified type:
        try:
            return self.aType( value )

        except:
            # Otherwise, raise an exception:
            tv = type( value )
            if tv is InstanceType:
                kind = class_of( value )
            else:
                kind = repr( value )

            self.error( object, name, '%s (i.e. %s)' % (
                                      str( tv )[ 1: -1 ], kind ) )

#-------------------------------------------------------------------------------
#  'ThisClass' class:  (DEPRECATED)
#-------------------------------------------------------------------------------

class ThisClass ( FacetHandler ):
    """ Ensures that the facet attribute values belong to the same class (or
        a subclass) as the object containing the facet attribute.

        ThisClass is the underlying handler for the predefined facets **This**
        and **self**, and the elements of ListThis.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, allow_none = False ):
        ### deprecated( self )
        """ Creates a ThisClass handler.

            Parameters
            ----------
            allow_none : Boolean
                Flag indicating whether None is accepted as a valid value
                (True or non-zero) or not (False or 0)
        """
        if allow_none:
            self.validate      = self.validate_none
            self.info          = self.info_none
            self.fast_validate = ( 2, None )
        else:
            self.fast_validate = ( 2, )


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


    def get_editor ( self, facet ):
        if self.editor is None:
            from facets.api import InstanceEditor

            self.editor = InstanceEditor( label = facet.label or '',
                                          view  = facet.view  or '',
                                          kind  = facet.kind  or 'live' )
        return self.editor

#-------------------------------------------------------------------------------
#  'FacetInstance' class:  (DEPRECATED)
#-------------------------------------------------------------------------------

# Mapping from 'adapt' parameter values to 'fast validate' values
AdaptMap = {
   'no':     -1,
   'yes':     0,
   'default': 1
 }

class FacetInstance ( ThisClass ):
    """ Ensures that facet attribute values belong to a specified Python class
        or type.

        FacetInstance is the underlying handler for the predefined facet
        **Instance** and the elements of List( Instance ).

        Any facet that uses a FacetInstance handler ensures that its values
        belong to the specified type or class (or one of its subclasses). For
        example::

            class Employee(HasFacets):
                manager = Facet(None, FacetInstance(Employee, True))

        This example defines a class Employee, which has a **manager** facet
        attribute, which accepts either None or an instance of Employee
        as its value.

        FacetInstance ensures that assigned values are exactly of the type
        specified (i.e., no coercion is performed).
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, aClass, allow_none = True, adapt = 'yes',
                   module = '' ):
        ### deprecated( self )
        """Creates a FacetInstance handler.

            Parameters
            ----------
            aClass : class or type
                A Python class, an instance of a Python class, or a Python type
            allow_none : boolean
                Flag indicating whether None is accepted as a valid value
                (True or non-zero) or not (False or 0)
            adapt : string
                Value indicating how adaptation should be handled:

                - 'no' (-1): Adaptation is not allowed.
                - 'yes' (0): Adaptation is allowed and should raise an exception
                  if adaptation fails.
                - 'default' (1): Adaption is allowed and should return the
                  default value if adaptation fails.
            module : module
                The module that the class belongs to.

            Description
            -----------
            If *aClass* is an instance, it is mapped to the class it is an instance
            of.
        """
        self._allow_none = allow_none
        self.adapt       = AdaptMap[ adapt ]
        self.module      = module

        if isinstance( aClass, basestring ):
            self.aClass = aClass
        else:
            if not isinstance( aClass, ClassTypes ):
                aClass = aClass.__class__

            self.aClass = aClass
            self.set_fast_validate()


    def allow_none ( self ):
        self._allow_none = True
        if hasattr( self, 'fast_validate' ):
            self.set_fast_validate()


    def set_fast_validate ( self ):
        if self.adapt < 0:
            fast_validate = [ 1, self.aClass ]
            if self._allow_none:
                fast_validate = [ 1, None, self.aClass ]

            if self.aClass in TypeTypes:
                fast_validate[0] = 0

            self.fast_validate = tuple( fast_validate )
        else:
            self.fast_validate = ( 19, self.aClass, self.adapt,
                                   self._allow_none )


    def validate ( self, object, name, value ):
        if value is None:
            if self._allow_none:
                return value
            else:
                self.validate_failed( object, name, value )

        if isinstance( self.aClass, basestring ):
            self.resolve_class( object, name, value )

        if self.adapt < 0:
            if isinstance( value, self.aClass ):
                return value

        elif self.adapt == 0:
            try:
                return adapt( value, self.aClass )
            except:
                pass
        else:
            # fixme: The 'None' value is not really correct. It should return
            # the default value for the facet, but the handler does not have
            # any way to know this currently. Since the 'fast validate' code
            # does the correct thing, this should not normally be a problem.
            return adapt( value, self.aClass, None )

        self.validate_failed( object, name, value )


    def info ( self ):
        aClass = self.aClass
        if type( aClass ) is not str:
            aClass = aClass.__name__

        if self.adapt < 0:
            result = class_of( aClass )
        else:
            result = ( 'an implementor of, or can be adapted to implement, %s' %
                      aClass )

        if self._allow_none:
            return result + ' or None'

        return result


    def resolve_class ( self, object, name, value ):
        aClass = self.validate_class( self.find_class( self.aClass ) )
        if aClass is None:
            self.validate_failed( object, name, value )

        self.aClass = aClass

        # fixme: The following is quite ugly, because it wants to try and fix
        # the facet referencing this handler to use the 'fast path' now that the
        # actual class has been resolved. The problem is finding the facet,
        # especially in the case of List(Instance('foo')), where the
        # object.base_facet(...) value is the List facet, not the Instance
        # facet, so we need to check for this and pull out the List
        # 'item_facet'. Obviously this does not extend well to other facets
        # containing nested facet references (Dict?)...
        self.set_fast_validate()
        facet   = object.base_facet( name )
        handler = facet.handler
        if ( handler is not self ) and hasattr( handler, 'item_facet' ):
            facet = handler.item_facet

        facet.set_validate( self.fast_validate )


    def find_class ( self, aClass ):
        module = self.module
        col    = aClass.rfind( '.' )
        if col >= 0:
            module = aClass[ : col ]
            aClass = aClass[ col + 1: ]

        theClass = getattr( sys.modules.get( module ), aClass, None )
        if ( theClass is None ) and ( col >= 0 ):
            try:
                mod = __import__( module )
                for component in module.split( '.' )[1:]:
                    mod = getattr( mod, component )

                theClass = getattr( mod, aClass, None )
            except:
                pass

        return theClass


    def validate_class ( self, aClass ):
        return aClass


    def create_default_value ( self, *args, **kw ):
        aClass = args[0]
        if isinstance( aClass, basestring ):
            aClass = self.validate_class( self.find_class( aClass ) )
            if aClass is None:
                raise FacetError( 'Unable to locate class: ' + args[0] )

        return aClass( *args[1:], **kw )

#-------------------------------------------------------------------------------
#  'FacetFunction' class:
#-------------------------------------------------------------------------------

class FacetFunction ( FacetHandler ):
    """ Ensures that assigned facet attribute values are acceptable to a
        specified validator function.

        FacetFunction is the underlying handler used for function references as
        arguments to the Facet() function.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, aFunc ):
        """ Creates a FacetFunction handler.

            Parameters
            ----------
            aFunc : function
                A function to validate facet attribute values

            Description
            -----------
            The signature of the function passed as an argument must be of the
            form *function* ( *object*, *name*, *value* ). The function must
            verify that *value* is a legal value for the *name* facet attribute
            of *object*. If it is, the value returned by the fucntion is the
            actual value assigned to the facet attribute. If it is not, the
            function must raise a FacetError exception.
        """
        if not isinstance( aFunc, CallableTypes ):
            raise FacetError( "Argument must be callable." )

        self.aFunc = aFunc
        self.fast_validate = ( 13, aFunc )


    def validate ( self, object, name, value ):
        try:
            return self.aFunc( object, name, value )
        except FacetError:
            self.error( object, name, self.repr( value ) )


    def info ( self ):
        try:
            return self.aFunc.info
        except:
            if self.aFunc.__doc__:
                return self.aFunc.__doc__

            return 'a legal value'

#-------------------------------------------------------------------------------
#  'FacetPrefixList' class:
#-------------------------------------------------------------------------------

class FacetPrefixList ( FacetHandler ):
    """ Ensures that a value assigned to a facet attribute is a member of a list
        of specified string values, or is a unique prefix of one of those
        values.

        FacetPrefixList is a variation on Enum. The values that can be assigned
        to a facet attribute defined using a FacetPrefixList handler is the set
        of all strings supplied to the FacetPrefixList constructor, as well as
        any unique prefix of those strings. That is, if the set of strings
        supplied to the constructor is described by [*s*\ :sub:`1`\,
        *s*\ :sub:`2`\ , ..., *s*\ :sub:`n`\ ], then the string *v* is a valid
        value for the facet if *v* == *s*\ :sub:`i[:j]` for one and only one
        pair of values (i, j). If *v* is a valid value, then the actual value
        assigned to the facet attribute is the corresponding *s*\ :sub:`i` value
        that *v* matched. For example::

            class Person(HasFacets):
                married = Facet('no', FacetPrefixList('yes', 'no')

        The Person class has a **married** facet that accepts any of the
        strings 'y', 'ye', 'yes', 'n', or 'no' as valid values. However, the
        actual values assigned as the value of the facet attribute are limited
        to either 'yes' or 'no'. That is, if the value 'y' is assigned to the
        **married** attribute, the actual value assigned will be 'yes'.

        Note that the algorithm used by FacetPrefixList in determining whether a
        string is a valid value is fairly efficient in terms of both time and
        space, and is not based on a brute force set of comparisons.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, * values ):
        """ Creates a FacetPrefixList handler.

            Parameters
            ----------
            values : list or tuple of strings
                Enumeration of all legal values for a facet

            Description
            -----------
            As with Enum, the list of legal values can be provided as a list of
            values.  That is, ``FacetPrefixList(['one', 'two', 'three'])`` and
            ``FacetPrefixList('one', 'two', 'three')`` are equivalent.
        """
        if (len( values ) == 1) and (type( values[0]) in SequenceTypes):
            values = values[0]

        self.values  = values[:]
        self.values_ = values_ = {}
        for key in values:
            values_[ key ] = key

        self.fast_validate = ( 10, values_, self.validate )


    def validate ( self, object, name, value ):
        try:
            if not self.values_.has_key( value ):
                match = None
                n     = len( value )
                for key in self.values:
                    if value == key[ : n ]:
                        if match is not None:
                            match = None

                            break

                        match = key

                if match is None:
                    self.error( object, name, self.repr( value ) )

                self.values_[ value ] = match

            return self.values_[ value ]

        except:
            self.error( object, name, self.repr( value ) )


    def info ( self ):
        return (' or '.join( [ repr( x ) for x in self.values ] ) +
                ' (or any unique prefix)')


    def get_editor ( self, facet ):
        from facets.api import EnumEditor

        return EnumEditor( values = self,
                           cols   = facet.cols or 3  )


    def __getstate__ ( self ):
        result = self.__dict__.copy()
        if 'fast_validate' in result:
            del result[ 'fast_validate' ]

        return result

#-------------------------------------------------------------------------------
#  'FacetMap' class:
#-------------------------------------------------------------------------------

class FacetMap ( FacetHandler ):
    """ Checks that the value assigned to a facet attribute is a key of a
        specified dictionary, and also assigns the dictionary value
        corresponding to that key to a *shadow* attribute.

        A facet attribute that uses a FacetMap handler is called *mapped* facet
        attribute. In practice, this means that the resulting object actually
        contains two attributes: one whose value is a key of the FacetMap
        dictionary, and the other whose value is the corresponding value of the
        FacetMap dictionary. The name of the shadow attribute is simply the base
        attribute name with an underscore ('_') appended. Mapped facet
        attributes can be used to allow a variety of user-friendly input values
        to be mapped to a set of internal, program-friendly values. For
        example::

            >>>class Person(HasFacets):
            ...    married = Facet('yes', FacetMap({'yes': 1, 'no': 0 })
            >>>
            >>>bob = Person()
            >>>print bob.married
            yes
            >>>print bob.married_
            1

        In this example, the default value of the **married** attribute of the
        Person class is 'yes'. Because this attribute is defined using
        FacetPrefixList, instances of Person have another attribute,
        **married_**, whose default value is 1, the dictionary value
        corresponding to the key 'yes'.
    """

    #-- Class Constants --------------------------------------------------------

    is_mapped = True

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, map ):
        """ Creates a FacetMap handler.

            Parameters
            ----------
            map : dictionary
                A dictionary whose keys are valid values for the facet
                attribute, and whose corresponding values are the values for the
                shadow facet attribute.
        """
        self.map = map
        self.fast_validate = ( 6, map )


    def validate ( self, object, name, value ):
        try:
            if self.map.has_key( value ):
                return value
        except:
            pass

        self.error( object, name, self.repr( value ) )


    def mapped_value ( self, value ):
        return self.map[ value ]


    def post_setattr ( self, object, name, value ):
        try:
            setattr( object, name + '_', self.mapped_value( value ) )
        except:
            # We don't need a fancy error message, because this exception
            # should always be caught by a FacetCompound handler:
            raise FacetError( 'Unmappable' )


    def info ( self ):
        keys = [ repr( x ) for x in self.map.keys() ]
        keys.sort()

        return ' or '.join( keys )


    def get_editor ( self, facet ):
        from facets.api import EnumEditor

        return EnumEditor( values = self,
                           cols   = facet.cols or 3  )

#-------------------------------------------------------------------------------
#  'FacetPrefixMap' class:
#-------------------------------------------------------------------------------

class FacetPrefixMap ( FacetMap ):
    """ A cross between the FacetPrefixList and FacetMap classes.

        Like FacetMap, FacetPrefixMap is created using a dictionary, but in this
        case, the keys of the dictionary must be strings. Like FacetPrefixList,
        a string *v* is a valid value for the facet attribute if it is a prefix
        of one and only one key *k* in the dictionary. The actual values
        assigned to the facet attribute is *k*, and its corresponding mapped
        attribute is *map*[*k*].

        Example
        -------
        ::

            boolean_map = Facet('true', FacetPrefixMap( {
                                            'true': 1,
                                            'yes': 1,
                                            'false': 0,
                                            'no': 0 } ))

        This example defines a Boolean facet that accepts any prefix of 'true',
        'yes', 'false', or 'no', and maps them to 1 or 0.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, map ):
        """ Creates a FacetPrefixMap handler.

            Parameters
            ----------
            map : dictionary
                A dictionary whose keys are strings that are valid values for
                the facet attribute, and whose corresponding values are the
                values for the shadow facet attribute.
        """
        self.map  = map
        self._map = _map = {}
        for key in map.keys():
            _map[ key ] = key

        self.fast_validate = ( 10, _map, self.validate )


    def validate ( self, object, name, value ):
        try:
            if not self._map.has_key( value ):
                match = None
                n     = len( value )
                for key in self.map.keys():
                    if value == key[ : n ]:
                        if match is not None:
                            match = None

                            break

                        match = key

                if match is None:
                    self.error( object, name, self.repr( value ) )

                self._map[ value ] = match

            return self._map[ value ]

        except:
            self.error( object, name, self.repr( value ) )


    def info ( self ):
        return super( FacetPrefixMap, self ).info() + ' (or any unique prefix)'

#-------------------------------------------------------------------------------
#  'FacetCompound' class:
#-------------------------------------------------------------------------------

class FacetCompound ( FacetHandler ):
    """ Provides a logical-OR combination of other facet handlers.

        This class provides a means of creating complex facet definitions by
        combining several simpler facet definitions. FacetCompound is the
        underlying handler for the general forms of the Facet() function.

        A value is a valid value for a facet attribute based on a FacetCompound
        instance if the value is valid for at least one of the FacetHandler or
        facet objects supplied to the constructor. In addition, if at least one
        of the FacetHandler or facet objects is mapped (e.g., based on a
        FacetMap or FacetPrefixMap instance), then the FacetCompound is also
        mapped. In this case, any non-mapped facets or facet handlers use
        identity mapping.
    """

    #-- Class Constants --------------------------------------------------------

    _items_event = None

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, * handlers ):
        """ Creates a FacetCompound handler.

            Parameters
            ----------
            handlers : list or tuple of FacetHandler or facet objects
                The facet handlers to be combined

            Description
            -----------
            The FacetHandler or facet objects can be provided directly as
            arguments to the constructor.
        """
        if (len( handlers ) == 1) and (type( handlers[0]) in SequenceTypes):
            handlers = handlers[0]

        self.handlers = handlers
        self.set_validate()


    def set_validate ( self ):
        self.is_mapped  = False
        self.has_items  = False
        self.reversable = True
        post_setattrs   = []
        mapped_handlers = []
        validates       = []
        fast_validates  = []
        slow_validates  = []

        for handler in self.handlers:
            fv = getattr( handler, 'fast_validate', None )
            if fv is not None:
                validates.append( handler.validate )
                if fv[0] == 7:
                    # If this is a nested complex fast validator, expand its
                    # contents and adds its list to our list:
                    fast_validates.extend( fv[ 1 ] )
                else:
                    # Else just add the entire validator to the list:
                    fast_validates.append( fv )
            else:
                slow_validates.append( handler.validate )

            post_setattr = getattr( handler, 'post_setattr', None )
            if post_setattr is not None:
                post_setattrs.append( post_setattr )

            if handler.is_mapped:
                self.is_mapped = True
                mapped_handlers.append( handler )
            else:
                self.reversable = False

            if handler.has_items:
                self.has_items = True

        self.validates      = validates
        self.slow_validates = slow_validates

        if self.is_mapped:
            self.mapped_handlers = mapped_handlers
        elif hasattr( self, 'mapped_handlers' ):
            del self.mapped_handlers

        # If there are any fast validators, then we create a 'complex' fast
        # validator that composites them:
        if len( fast_validates ) > 0:
            # If there are any 'slow' validators, add a special handler at
            # the end of the fast validator list to handle them:
            if len( slow_validates ) > 0:
                fast_validates.append( ( 8, self ) )

            # Create the 'complex' fast validator:
            self.fast_validate = ( 7, tuple( fast_validates ) )

        elif hasattr( self, 'fast_validate' ):
            del self.fast_validate

        if len( post_setattrs ) > 0:
            self.post_setattrs = post_setattrs
            self.post_setattr  = self._post_setattr
        elif hasattr( self, 'post_setattr' ):
            del self.post_setattr


    def validate ( self, object, name, value ):
        for validate in self.validates:
            try:
                return validate( object, name, value )
            except FacetError:
                pass

        return self.slow_validate( object, name, value )


    def slow_validate ( self, object, name, value ):
        for validate in self.slow_validates:
            try:
                return validate( object, name, value )
            except FacetError:
                pass

        self.error( object, name, self.repr( value ) )


    def full_info ( self, object, name, value ):
        return ' or '.join( [ x.full_info( object, name, value )
                              for x in self.handlers ] )


    def info ( self ):
        return ' or '.join( [ x.info() for x in self.handlers ] )


    def mapped_value ( self, value ):
        for handler in self.mapped_handlers:
            try:
                return handler.mapped_value( value )
            except:
                pass

        return value


    def _post_setattr ( self, object, name, value ):
        for post_setattr in self.post_setattrs:
            try:
                post_setattr( object, name, value )
                return
            except FacetError:
                pass

        setattr( object, name + '_', value )


    def get_editor ( self, facet ):
        from facets.api import TextEditor, CompoundEditor

        the_editors = [ x.get_editor( facet ) for x in self.handlers ]
        text_editor = TextEditor()
        count       = 0
        editors     = []
        for editor in the_editors:
            if isinstance( text_editor, editor.__class__ ):
                count += 1
                if count > 1:
                    continue

            editors.append( editor )

        return CompoundEditor( editors = editors )

    #-- Private Methods --------------------------------------------------------

    def items_event ( self ):
        cls = self.__class__
        if cls._items_event is None:
            cls._items_event = \
                Event( FacetListEvent, is_base = False ).as_cfacet()

        return cls._items_event

#-------------------------------------------------------------------------------
#  Tell the C-based facets module the PyProtocols 'adapt' function:
#-------------------------------------------------------------------------------

import cfacets
cfacets._adapt( adapt )

#-- EOF ------------------------------------------------------------------------