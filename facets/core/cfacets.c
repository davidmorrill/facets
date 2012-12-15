//-----------------------------------------------------------------------------
//  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
//  Includes:
//-----------------------------------------------------------------------------

#include "Python.h"
#include "structmember.h"
#include "stdio.h"

//-----------------------------------------------------------------------------
//  Constants:
//-----------------------------------------------------------------------------

static PyObject * class_facets;        // == "__class_facets__"
static PyObject * listener_facets;     // == "__listener_facets__"
static PyObject * editor_property;     // == "editor"
static PyObject * class_prefix;        // == "__prefix__"
static PyObject * facet_added;         // == "facet_added"
static PyObject * fn_item_index;       // == 0 ('item' notification type index)
static PyObject * fn_event;            // == "event"
static PyObject * fn_item;             // == "item"
static PyObject * fn_list;             // == "list"
static PyObject * fn_set;              // == "set"
static PyObject * fn_dict;             // == "dict"
static PyObject * empty_tuple;         // == ()
static PyObject * Undefined;           // Global 'Undefined' value
static PyObject * Uninitialized;       // Global 'Uninitialized' value
static PyObject * FacetError;          // FacetError exception
static PyObject * DelegationError;     // DelegationError exception
static PyObject * FacetValue;          // FacetValue class
static PyObject * adapt;               // PyProtocols 'adapt' function
static PyObject * validate_implements; // 'validate implementation' function
static PyObject * is_callable;         // Marker for 'callable' value
static PyObject * _HasFacets_monitors; // Object creation monitors.
static PyObject * _facet_notification_handler; // User supplied facet
                // notification handler (intended for use by debugging tools)
static PyTypeObject * cfacet_type;     // Python-level CFacet type reference

/*-----------------------------------------------------------------------------
|  Macro definitions:
+----------------------------------------------------------------------------*/

// The following macro is automatically defined in Python 2.4 and later:
#ifndef Py_VISIT
#define Py_VISIT(op) \
do { \
    if (op) { \
        int vret = visit((PyObject *)(op), arg);	\
        if (vret) return vret; \
    } \
} while (0)
#endif

// The following macro is automatically defined in Python 2.4 and later:
#ifndef Py_CLEAR
#define Py_CLEAR(op) \
do { \
    if (op) { \
        PyObject *tmp = (PyObject *)(op); \
        (op) = NULL;	 \
        Py_DECREF(tmp); \
    } \
} while (0)
#endif

#define UNDEFINED(op) \
do { \
    PyObject * tmp = (PyObject *) (op); \
    if (tmp == NULL) { \
        tmp = Undefined; \
    } \
    Py_INCREF( tmp ); \
    return tmp; \
} while (0)

#define DEFERRED_ADDRESS(ADDR) 0
#define PyFacet_CheckExact(op) ((op)->ob_type == cfacet_type)

#define PyHasFacets_Check(op) PyObject_TypeCheck(op, &has_facets_type)
#define PyHasFacets_CheckExact(op) ((op)->ob_type == &has_facets_type)

// Facet method related:

#define TP_DESCR_GET(t) \
    (PyType_HasFeature(t, Py_TPFLAGS_HAVE_CLASS) ? (t)->tp_descr_get : NULL)
#define OFF(x) offsetof(facet_method_object, x)

// Notification related:
#define has_notifiers(tnotifiers,onotifiers) \
    ((((tnotifiers) != NULL) && (PyList_GET_SIZE((tnotifiers))>0)) || \
     (((onotifiers) != NULL) && (PyList_GET_SIZE((onotifiers))>0)))

// Field accessors:
#define facet_method_GET_NAME(meth) \
    (((facet_method_object *) meth)->tm_name)
#define facet_method_GET_FUNCTION(meth) \
    (((facet_method_object *) meth)->tm_func)
#define facet_method_GET_SELF(meth) \
	(((facet_method_object *) meth)->tm_self)
#define facet_method_GET_FACETS(meth) \
	(((facet_method_object *) meth)->tm_facets)
#define facet_method_GET_CLASS(meth) \
	(((facet_method_object *) meth)->tm_class)

// Python version dependent macros:
#if ( (PY_MAJOR_VERSION == 2) && (PY_MINOR_VERSION < 3) )
#define PyMODINIT_FUNC void
#define PyDoc_VAR(name) static char name[]
#define PyDoc_STRVAR(name,str) PyDoc_VAR(name) = PyDoc_STR(str)
#ifdef WITH_DOC_STRINGS
#define PyDoc_STR(str) str
#else
#define PyDoc_STR(str) ""
#endif
#endif
#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

// Define a type to match the results of a PyArg_ParseTuple "s#" length:
#ifdef PY_SSIZE_T_CLEAN
#define ParseTuple_StringLen Py_ssize_t
#else
#define ParseTuple_StringLen int
#endif

//-----------------------------------------------------------------------------
//  Forward declarations:
//-----------------------------------------------------------------------------

static PyTypeObject facet_type;
static PyTypeObject facet_method_type;
static PyTypeObject facet_notification_type;
static PyTypeObject has_facets_type;

//-----------------------------------------------------------------------------
//  'cfacets' module doc string:
//---------------------------------------------------------------------------//

PyDoc_STRVAR( cfacets__doc__,
"The cfacets module defines the CHasFacets and CFacet C extension types that\n"
"define the core performance oriented portions of the Facets package." );

//-----------------------------------------------------------------------------
//  HasFacets behavior modification flags:
//-----------------------------------------------------------------------------

// Object has been initialized:
#define HASFACETS_INITED      0x00000001

// Do not send notifications when a facet changes value:
#define HASFACETS_NO_NOTIFY   0x00000002

// Requests that no event notifications be sent when this object is assigned to
// a facet:
#define HASFACETS_VETO_NOTIFY 0x00000004

//-----------------------------------------------------------------------------
//  'CHasFacets' instance definition:
//
//  Note: facets are normally stored in the type's dictionary, but are added to
//  the instance's facets dictionary 'facet_dict' when the facets are defined
//  dynamically or 'on_facet_change' is called on an instance of the facet.
//
//  All 'anyfacet_changed' notification handlers are stored in the instance's
//  'notifiers' list.
//-----------------------------------------------------------------------------

typedef struct {
    PyObject_HEAD               // Standard Python object header
	PyDictObject * cfacet_dict; // Class facets dictionary
	PyDictObject * ifacet_dict; // Instance facets dictionary
    PyListObject * notifiers;   // List of 'any facet changed' notification
                                // handlers
    int            flags;       // Behavior modification flags
	PyObject     * obj_dict;    // Object attribute dictionary ('__dict__')
                                // NOTE: 'obj_dict' field MUST be last field
} has_facets_object;

static int call_notifiers ( PyListObject *, PyListObject *,
                            has_facets_object *, PyObject *, PyObject *,
                            PyObject * new_value, PyObject * notify );

//-----------------------------------------------------------------------------
//  'CFacet' flag values:
//-----------------------------------------------------------------------------

// The facet is a Property:
#define FACET_PROPERTY                    0x00000001

// Should the delegate be modified (or the original object)?
#define FACET_MODIFY_DELEGATE             0x00000002

// Should a simple object identity test be performed (or a rich compare)?
#define FACET_OBJECT_IDENTITY             0x00000004

// Make 'setattr' store the original unvalidated value:
#define FACET_SETATTR_ORIGINAL_VALUE      0x00000008

// Send the 'post_setattr' method the original unvalidated value:
#define FACET_POST_SETATTR_ORIGINAL_VALUE 0x00000010

// Can a 'FacetValue' be assigned to override the facet definition?
#define FACET_VALUE_ALLOWED               0x00000020

// Is this facet a special 'FacetValue' facet that uses a property?
#define FACET_VALUE_PROPERTY              0x00000040

// Does this facet have an associated 'mapped' facet?
#define FACET_IS_MAPPED                   0x00000080

// Should any old/new value test be performed before generating
// notifications?
#define FACET_NO_VALUE_TEST               0x00000100

// The mask and shift values used to extract the CFacetNotification type:
#define FACET_NOTIFY_SHIFT                16
#define FACET_NOTIFY_MASK                 0x0000000F

//-----------------------------------------------------------------------------
//  'CFacet' instance definition:
//-----------------------------------------------------------------------------

typedef struct _facet_object a_facet_object;
typedef PyObject * (*facet_getattr)( a_facet_object *, has_facets_object *,
                                     PyObject * );
typedef int (*facet_setattr)( a_facet_object *, a_facet_object *,
                              has_facets_object *, PyObject *, PyObject * );
typedef int (*facet_post_setattr)( a_facet_object *, has_facets_object *,
                                   PyObject *, PyObject * );
typedef PyObject * (*facet_validate)( a_facet_object *, has_facets_object *,
                              PyObject *, PyObject * );
typedef PyObject * (*delegate_attr_name_func)( a_facet_object *,
                                             has_facets_object *, PyObject * );

typedef struct _facet_object {
    PyObject_HEAD                    // Standard Python object header
    int                flags;        // Flag bits
    facet_getattr      getattr;      // Get facet value handler
    facet_setattr      setattr;      // Set facet value handler
    facet_post_setattr post_setattr; // Optional post 'setattr' handler
    PyObject *         py_post_setattr; // Python-based post 'setattr' hndlr
    facet_validate     validate;     // Validate facet value handler
    PyObject *         py_validate;  // Python-based validate value handler
    int                default_value_type; // Type of default value: see the
                                           //   'default_value_for' function
    PyObject *         default_value;   // Default value for facet
    PyObject *         delegate_name;   // Optional delegate name
                                        // Also used for 'property get'
    PyObject *         delegate_prefix; // Optional delegate prefix
                                        // Also used for 'property set'
    delegate_attr_name_func delegate_attr_name; // Optional routine to return
                                  // the computed delegate attribute name
    PyListObject *     notifiers; // Optional list of notification handlers
    PyObject *         handler;   // Associated facet handler object
                                  // NOTE: The 'obj_dict' field MUST be last
    PyObject *         obj_dict;  // Standard Python object dictionary
} facet_object;

//-----------------------------------------------------------------------------
//  'CFacetsNotification' instance definition:
//-----------------------------------------------------------------------------

typedef struct {
    PyObject_HEAD         // Standard Python object header
	PyObject * type;      // Notification type ('event', 'item', 'list',...)
	PyObject * object;    // Object modified         (all)
	PyObject * name;      // Name of modified facet  (all)
	PyObject * new;       // New facet value         (event, item)
	PyObject * old;       // Old facet value         (item)
	PyObject * index;     // Starting index          (list)
	PyObject * added;     // Items added             (list, dict, set)
	PyObject * removed;   // Items removed           (list, dict, set)
	PyObject * updated;   // Items updated           (dict)
	PyObject * obj_dict;  // Object attribute dictionary ('__dict__')
} facet_notification_object;

//-- Forward declarations ------------------------------------------------------

static void facet_clone ( facet_object *, facet_object * );

static PyObject * has_facets_getattro ( has_facets_object * obj,
                                        PyObject          * name );

static int has_facets_setattro ( has_facets_object * obj,
                                 PyObject          * name,
                                 PyObject          * value );

static PyObject * get_facet ( has_facets_object * obj,
                              PyObject          * name,
                              int                 instance );

static int facet_property_set ( has_facets_object * obj,
                                PyObject          * name,
                                PyObject          * old_value,
                                PyObject          * new_value );

static int setattr_event ( facet_object      * faceto,
                           facet_object      * facetd,
                           has_facets_object * obj,
                           PyObject          * name,
                           PyObject          * value );

static int setattr_disallow ( facet_object      * faceto,
                              facet_object      * facetd,
                              has_facets_object * obj,
                              PyObject          * name,
                              PyObject          * value );

//-----------------------------------------------------------------------------
//  Raise a FacetError:
//-----------------------------------------------------------------------------

static PyObject *
raise_facet_error ( facet_object * facet, has_facets_object * obj,
				    PyObject * name, PyObject * value ) {

    PyObject * result = PyObject_CallMethod( facet->handler,
                                          "error", "(OOO)", obj, name, value );
    Py_XDECREF( result );
    return NULL;
}

//-----------------------------------------------------------------------------
//  Raise a fatal facet error:
//-----------------------------------------------------------------------------

static int
fatal_facet_error ( void ) {

    PyErr_SetString( FacetError, "Non-facet found in facet dictionary" );

    return -1;
}

//-----------------------------------------------------------------------------
//  Raise an "attribute is not a string" error:
//-----------------------------------------------------------------------------

static int
invalid_attribute_error ( void ) {

    PyErr_SetString( PyExc_TypeError, "attribute name must be string" );

    return -1;
}

//-----------------------------------------------------------------------------
//  Raise an "invalid facet definition" error:
//-----------------------------------------------------------------------------

static int
bad_facet_error ( void ) {

    PyErr_SetString( FacetError, "Invalid argument to facet constructor." );

    return -1;
}

//-----------------------------------------------------------------------------
//  Raise an "cant set items error" error:
//-----------------------------------------------------------------------------

static PyObject *
cant_set_items_error ( void ) {

    PyErr_SetString( FacetError, "Can not set a collection's '_items' facet." );

    return NULL;
}

//-----------------------------------------------------------------------------
//  Raise an "invalid facet definition" error:
//-----------------------------------------------------------------------------

static int
bad_facet_value_error ( void ) {

    PyErr_SetString( FacetError,
        "Result of 'as_cfacet' method was not a 'CFacets' instance." );

    return -1;
}


//-----------------------------------------------------------------------------
//  Raise an invalid delegate error:
//-----------------------------------------------------------------------------

static int
bad_delegate_error ( has_facets_object * obj, PyObject * name ) {

    if ( PyString_Check( name ) ) {
        PyErr_Format( DelegationError,
            "The '%.400s' attribute of a '%.50s' object delegates to an attribute which is not a defined facet.",
	        PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }

    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Raise an invalid delegate error:
//-----------------------------------------------------------------------------

static int
bad_delegate_error2 ( has_facets_object * obj, PyObject * name ) {

    if ( PyString_Check( name ) ) {
        PyErr_Format( DelegationError,
            "The '%.400s' attribute of a '%.50s' object has a delegate which does not have facets.",
	        PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }

    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Raise a delegation recursion error:
//-----------------------------------------------------------------------------

static int
delegation_recursion_error ( has_facets_object * obj, PyObject * name ) {

    if ( PyString_Check( name ) ) {
        PyErr_Format( DelegationError,
	                  "Delegation recursion limit exceeded while setting the '%.400s' attribute of a '%.50s' object.",
	                  PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }

    return invalid_attribute_error();
}

static int
delegation_recursion_error2 ( has_facets_object * obj, PyObject * name ) {

    if ( PyString_Check( name ) ) {
        PyErr_Format( DelegationError,
	                  "Delegation recursion limit exceeded while getting the definition of the '%.400s' facet of a '%.50s' object.",
	                  PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }

    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Raise an attempt to delete read-only attribute error:
//-----------------------------------------------------------------------------

static int
delete_readonly_error ( has_facets_object * obj, PyObject * name ) {

    if ( PyString_Check( name ) ) {
        PyErr_Format( FacetError,
	                  "Cannot delete the read only '%.400s' attribute of a '%.50s' object.",
	                  PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }

    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Raise an attempt to set a read-only attribute error:
//-----------------------------------------------------------------------------

static int
set_readonly_error ( has_facets_object * obj, PyObject * name ) {

    if ( PyString_Check( name ) ) {
        PyErr_Format( FacetError,
	                  "Cannot modify the read only '%.400s' attribute of a '%.50s' object.",
	                  PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }

    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Raise an attempt to set an undefined attribute error:
//-----------------------------------------------------------------------------

static int
set_disallow_error ( has_facets_object * obj, PyObject * name ) {

    if ( PyString_Check( name ) ) {
        PyErr_Format( FacetError,
	                  "Cannot set the undefined '%.400s' attribute of a '%.50s' object.",
	                  PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }

    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Raise an attempt to delete a property error:
//-----------------------------------------------------------------------------

static int
set_delete_property_error ( has_facets_object * obj, PyObject * name ) {

    if ( PyString_Check( name ) ) {
        PyErr_Format( FacetError,
	        "Cannot delete the '%.400s' property of a '%.50s' object.",
	        PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }

    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Raise an undefined attribute error:
//-----------------------------------------------------------------------------

static void
unknown_attribute_error ( has_facets_object * obj, PyObject * name ) {

    PyErr_Format( PyExc_AttributeError,
                  "'%.50s' object has no attribute '%.400s'",
                  obj->ob_type->tp_name, PyString_AS_STRING( name ) );
}

//-----------------------------------------------------------------------------
//  Raise a '__dict__' must be set to a dictionary error:
//-----------------------------------------------------------------------------

static int
dictionary_error ( void ) {

    PyErr_SetString( PyExc_TypeError,
                     "__dict__ must be set to a dictionary." );

    return -1;
}

//-----------------------------------------------------------------------------
//  Raise an exception when a facet method argument is of the wrong type:
//-----------------------------------------------------------------------------

static PyObject *
argument_error ( facet_object * facet, PyObject * meth, int arg,
                 PyObject * obj, PyObject * name, PyObject * value ) {

    PyObject * arg_num = PyInt_FromLong( arg );
    if ( arg_num != NULL ) {
        PyObject * result = PyObject_CallMethod( facet->handler,
                     "arg_error", "(OOOOO)", meth, arg_num, obj, name, value );
        Py_XDECREF( result );
        Py_XDECREF( arg_num );
    }

    return NULL;
}

//-----------------------------------------------------------------------------
//  Raise an exception when a facet method keyword argument is the wrong type:
//-----------------------------------------------------------------------------

static PyObject *
keyword_argument_error ( facet_object * facet, PyObject * meth,
                         PyObject * obj, PyObject * name, PyObject * value ) {

    PyObject * result = PyObject_CallMethod( facet->handler,
                           "keyword_error", "(OOOO)", meth, obj, name, value );
    Py_XDECREF( result );

    return NULL;
}

//-----------------------------------------------------------------------------
//  Raise an exception when a facet method keyword argument is the wrong type:
//-----------------------------------------------------------------------------

static PyObject *
dup_argument_error ( facet_object * facet, PyObject * meth, int arg,
                     PyObject * obj, PyObject * name ) {

    PyObject * arg_num = PyInt_FromLong( arg );
    if ( arg_num != NULL ) {
        PyObject * result = PyObject_CallMethod( facet->handler,
                       "dup_arg_error", "(OOOO)", meth, arg_num, obj, name );
        Py_XDECREF( result );
        Py_XDECREF( arg_num );
    }

    return NULL;
}

//-----------------------------------------------------------------------------
//  Raise an exception when a required facet method argument is missing:
//-----------------------------------------------------------------------------

static PyObject *
missing_argument_error ( facet_object * facet, PyObject * meth, int arg,
                         PyObject * obj, PyObject * name ) {

    PyObject * arg_num = PyInt_FromLong( arg );
    if ( arg_num != NULL ) {
        PyObject * result = PyObject_CallMethod( facet->handler,
                     "missing_arg_error", "(OOOO)", meth, arg_num, obj, name );
        Py_XDECREF( result );
        Py_XDECREF( arg_num );
    }

    return NULL;
}

//-----------------------------------------------------------------------------
//  Raise an exception when a required facet method argument is missing:
//-----------------------------------------------------------------------------

static PyObject *
too_may_args_error ( PyObject * name, Py_ssize_t wanted, Py_ssize_t received ) {

    switch ( wanted ) {
        case 0:
            PyErr_Format( PyExc_TypeError,
                  "%.400s() takes no arguments (%.3zd given)",
                  PyString_AS_STRING( name ), received );
            break;
        case 1:
            PyErr_Format( PyExc_TypeError,
                  "%.400s() takes exactly 1 argument (%.3zd given)",
                  PyString_AS_STRING( name ), received );
            break;
        default:
            PyErr_Format( PyExc_TypeError,
                  "%.400s() takes exactly %.3zd arguments (%.3zd given)",
                  PyString_AS_STRING( name ), wanted, received );
            break;
    }

    return NULL;
}

//-----------------------------------------------------------------------------
//  Raise an exception when a facet method argument is of the wrong type:
//-----------------------------------------------------------------------------

static void
invalid_result_error ( facet_object * facet, PyObject * meth, PyObject * obj,
                       PyObject * value ) {

    PyObject * result = PyObject_CallMethod( facet->handler,
                                   "return_error", "(OOO)", meth, obj, value );
    Py_XDECREF( result );
}

//-----------------------------------------------------------------------------
//  Gets/Sets a possibly NULL (or callable) value:
//-----------------------------------------------------------------------------

static PyObject *
get_callable_value ( PyObject * value ) {
    PyObject * tuple, * temp;
    if ( value == NULL )
        value = Py_None;
    else if ( PyCallable_Check( value ) )
        value = is_callable;
    else if ( PyTuple_Check( value ) &&
              (PyInt_AsLong( PyTuple_GET_ITEM( value, 0 ) ) == 10) ) {
        tuple = PyTuple_New( 3 );
        if ( tuple != NULL ) {
            PyTuple_SET_ITEM( tuple, 0, temp = PyTuple_GET_ITEM( value, 0 ) );
            Py_INCREF( temp );
            PyTuple_SET_ITEM( tuple, 1, temp = PyTuple_GET_ITEM( value, 1 ) );
            Py_INCREF( temp );
            PyTuple_SET_ITEM( tuple, 2, is_callable );
            Py_INCREF( is_callable );
            value = tuple;
        }
    }
    Py_INCREF( value );
    return value;
}

static PyObject *
get_value ( PyObject * value ) {
    if ( value == NULL )
        value = Py_None;
    Py_INCREF( value );
    return value;
}

static int
set_value ( PyObject ** field, PyObject * value ) {

    Py_INCREF( value );
    Py_XDECREF( *field );
    *field = value;
    return 0;
}

//-----------------------------------------------------------------------------
//  Returns the result of calling a specified 'class' object with 1 argument:
//-----------------------------------------------------------------------------

static PyObject *
call_class ( PyObject * class, facet_object * facet, has_facets_object * obj,
             PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 4 );
    if ( args == NULL )
        return NULL;
    PyTuple_SET_ITEM( args, 0, facet->handler );
    PyTuple_SET_ITEM( args, 1, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 2, name );
    PyTuple_SET_ITEM( args, 3, value );
    Py_INCREF( facet->handler );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    result = PyObject_Call( class, args, NULL );
    Py_DECREF( args );
    return result;
}

//-----------------------------------------------------------------------------
//  Attempts to get the value of a key in a 'known to be a dictionary' object:
//-----------------------------------------------------------------------------

static PyObject *
dict_getitem ( PyDictObject * dict, PyObject *key ) {

	long hash;

	assert( PyDict_Check( dict ) );

	if ( !PyString_CheckExact( key ) ||
         ((hash = ((PyStringObject *) key)->ob_shash) == -1) ) {
		hash = PyObject_Hash( key );
		if ( hash == -1 ) {
			PyErr_Clear();
            return NULL;
		}
	}

	return (dict->ma_lookup)( dict, key, hash )->me_value;
}

//-----------------------------------------------------------------------------
//  Gets the definition of the matching prefix based facet for a specified name:
//
//  - This should always return a facet definition unless a fatal Python error
//    occurs.
//  - The bulk of the work is delegated to a Python implemented method because
//    the implementation is complicated in C and does not need to be executed
//    very often relative to other operations.
//-----------------------------------------------------------------------------

static facet_object *
get_prefix_facet ( has_facets_object * obj, PyObject * name, int is_set ) {

    PyObject * facet = PyObject_CallMethod( (PyObject *) obj,
                           "__prefix_facet__", "(Oi)", name, is_set );

    if ( facet != NULL ) {
        assert( obj->cfacet_dict != NULL );
	    PyDict_SetItem( (PyObject *) obj->cfacet_dict, name, facet );
        Py_DECREF( facet );

        if ( has_facets_setattro( obj, facet_added, name ) < 0 )
            return NULL;

        facet = get_facet( obj, name, 0 );
        Py_DECREF( facet );
    }

    return (facet_object *) facet;
}

//-----------------------------------------------------------------------------
//  Assigns a special FacetValue to a specified facet attribute:
//-----------------------------------------------------------------------------

static int
setattr_value ( facet_object      * facet,
                has_facets_object * obj,
                PyObject          * name,
                PyObject          * value ) {

    PyDictObject * dict;
    PyObject * facet_new, * result, * obj_dict;
    PyObject * facet_old = NULL;
    PyObject * value_old = NULL;

    facet_new = PyObject_CallMethod( value, "as_cfacet", "(O)", facet );
    if ( facet_new == NULL )
        goto error2;

    if ( (facet_new != Py_None) && (!PyFacet_CheckExact( facet_new )) ) {
        Py_DECREF( facet_new );
        return bad_facet_value_error();
    }

    dict = obj->ifacet_dict;
    if ( (dict != NULL) &&
         ((facet_old = dict_getitem( dict, name )) != NULL) &&
         ((((facet_object *) facet_old)->flags & FACET_VALUE_PROPERTY) != 0) ) {
        result = PyObject_CallMethod( facet_old, "_unregister",
                                      "(OO)", obj, name );
        if ( result == NULL )
            goto error1;

        Py_DECREF( result );
    }

    if ( facet_new == Py_None ) {
        if ( facet_old != NULL ) {
            PyDict_DelItem( (PyObject *) dict, name );
        }
        goto success;
    }

    if ( dict == NULL ) {
        obj->ifacet_dict = dict = (PyDictObject *) PyDict_New();
        if ( dict == NULL )
            goto error1;
    }

    if ( (((facet_object *) facet_new)->flags & FACET_VALUE_PROPERTY) != 0 ) {
        if ( (value_old = has_facets_getattro( obj, name )) == NULL ) {
            /* fixme: If we get an error getting the old value, assume it is
               because the value is read-only. It might be a good idea to verify
               this though. The old code was: goto error1; */
            PyErr_Clear();
            value_old = Undefined;
            Py_INCREF( value_old );
        }

        obj_dict = obj->obj_dict;
        if ( (obj_dict != NULL) &&
             (dict_getitem( (PyDictObject *) obj_dict, name ) != NULL) )
            PyDict_DelItem( obj_dict, name );
    }

    if ( PyDict_SetItem( (PyObject *) dict, name, facet_new ) < 0 )
        goto error0;

    if ( (((facet_object *) facet_new)->flags & FACET_VALUE_PROPERTY) != 0 ) {
        result = PyObject_CallMethod( facet_new, "_register",
                                      "(OO)", obj, name );
        if ( result == NULL )
            goto error0;

        Py_DECREF( result );

        if ( facet_property_set( obj, name, value_old, NULL ) )
            goto error0;

        Py_DECREF( value_old );
    }
success:
    Py_DECREF( facet_new );
    return 0;

error0:
    Py_XDECREF( value_old );
error1:
    Py_DECREF( facet_new );
error2:
    return -1;
}

//-----------------------------------------------------------------------------
//  Handles the 'setattr' operation on a 'CHasFacets' instance:
//-----------------------------------------------------------------------------

static int
has_facets_setattro ( has_facets_object * obj,
                      PyObject          * name,
                      PyObject          * value ) {

    facet_object * facet;

    if ( (obj->ifacet_dict == NULL) ||
         ((facet = (facet_object *) dict_getitem( obj->ifacet_dict, name )) ==
           NULL) ) {
        facet = (facet_object *) dict_getitem( obj->cfacet_dict, name );
        if ( (facet == NULL) &&
             ((facet = get_prefix_facet( obj, name, 1 )) == NULL) )
            return -1;
    }

    if ( ((facet->flags & FACET_VALUE_ALLOWED) != 0) &&
          (PyObject_IsInstance( value, FacetValue ) > 0) ) {
        return setattr_value( facet, obj, name, value );
    }

    return facet->setattr( facet, facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Allocates a CFacet instance:
//-----------------------------------------------------------------------------

PyObject *
has_facets_new ( PyTypeObject * type, PyObject * args, PyObject * kwds ) {

    has_facets_object * obj = (has_facets_object *) type->tp_alloc( type, 0 );
    if ( obj != NULL ) {
        assert( type->tp_dict != NULL );
        obj->cfacet_dict = (PyDictObject *) PyDict_GetItem( type->tp_dict,
                                                            class_facets );
        assert( obj->cfacet_dict != NULL );
        assert( PyDict_Check( (PyObject *) obj->cfacet_dict ) );
        Py_INCREF( obj->cfacet_dict );
    }

    return (PyObject *) obj;
}

int
has_facets_init ( PyObject * obj, PyObject * args, PyObject * kwds ) {

    PyObject * key;
    PyObject * value;
    PyObject * klass;
    PyObject * handler;
    PyObject * handler_args;
    PyObject * listeners;
    Py_ssize_t n;
    Py_ssize_t i = 0;

    // Make sure no non-keyword arguments were specified:
    if ( !PyArg_ParseTuple( args, "" ) )
        return -1;

    // If the object has already been initialized, it is a singleton, so don't
    // re-initialize it:
    if ( (((has_facets_object *) obj)->flags & HASFACETS_INITED) != 0 )
        return 0;

    // Make sure all of the object's listeners have been set up:
    listeners = PyDict_GetItem( obj->ob_type->tp_dict, listener_facets );
    if ( PyList_Size( PyTuple_GetItem( listeners, 0 ) ) > 0 ) {
        value = PyObject_CallMethod( obj, "_init_facet_listeners", "()" );
        if ( value == NULL )
            return -1;

        Py_DECREF( value );
    }

    // Set any facets specified in the constructor:
    if ( kwds != NULL ) {
        while ( PyDict_Next( kwds, &i, &key, &value ) ) {
            if ( has_facets_setattro( (has_facets_object *) obj, key, value )
                 == -1 )
                return -1;
        }
    }

    // Make sure all post constructor argument assignment listeners have been
    // set up:
    if ( PyList_Size( PyTuple_GetItem( listeners, 1 ) ) > 0 ) {
        value = PyObject_CallMethod( obj, "_post_init_facet_listeners", "()" );
        if ( value == NULL )
            return -1;

        Py_DECREF( value );
    }

    // Notify any interested monitors that a new object has been created:
    for ( i = 0, n = PyList_GET_SIZE( _HasFacets_monitors ); i < n; i++ ) {
        value = PyList_GET_ITEM( _HasFacets_monitors, i );
        assert( PyTuple_Check( value ) );
        assert( PyTuple_GET_SIZE( value ) == 2 );

        klass   = PyTuple_GET_ITEM( value, 0 );
        handler = PyTuple_GET_ITEM( value, 1 );

        if ( PyObject_IsInstance( obj, klass ) > 0 ) {
            handler_args = PyTuple_New( 1 );
            PyTuple_SetItem( handler_args, 0, obj );
            Py_INCREF( obj );
            PyObject_Call( handler, handler_args, NULL );
            Py_DECREF( handler_args );
        }
    }

    // Call the 'facets_init' method to finish up initialization:
    value = PyObject_CallMethod( obj, "facets_init", "()" );
    if ( value == NULL )
        return -1;

    Py_DECREF( value );

    // Indicate that the object has finished being initialized:
    ((has_facets_object *) obj)->flags |= HASFACETS_INITED;

    return 0;
}

//-----------------------------------------------------------------------------
//  Object clearing method:
//-----------------------------------------------------------------------------

static int
has_facets_clear ( has_facets_object * obj ) {

    Py_CLEAR( obj->cfacet_dict );
    Py_CLEAR( obj->ifacet_dict );
    Py_CLEAR( obj->notifiers );
    Py_CLEAR( obj->obj_dict );

    return 0;
}

//-----------------------------------------------------------------------------
//  Deallocates an unused 'CHasFacets' instance:
//-----------------------------------------------------------------------------

static void
has_facets_dealloc ( has_facets_object * obj ) {

    has_facets_clear( obj );
    obj->ob_type->tp_free( (PyObject *) obj );
}

//-----------------------------------------------------------------------------
//  Garbage collector traversal method:
//-----------------------------------------------------------------------------

static int
has_facets_traverse ( has_facets_object * obj, visitproc visit, void * arg ) {

    Py_VISIT( obj->cfacet_dict );
    Py_VISIT( obj->ifacet_dict );
    Py_VISIT( obj->notifiers );
    Py_VISIT( obj->obj_dict );

	return 0;
}

//-----------------------------------------------------------------------------
//  Returns whether an object's '__dict__' value is defined or not:
//-----------------------------------------------------------------------------

static int
has_value_for ( has_facets_object * obj, PyObject * name ) {

    PyObject * uname;
    long hash;
    int  rc;

    PyDictObject * dict = (PyDictObject *) obj->obj_dict;

	if ( dict == NULL )
        return 0;

    assert( PyDict_Check( dict ) );

    if ( PyString_CheckExact( name ) ) {
         if ( (hash = ((PyStringObject *) name)->ob_shash) == -1 )
             hash = PyObject_Hash( name );
	     return ((dict->ma_lookup)( dict, name, hash )->me_value != NULL);
    }

    if ( PyString_Check( name ) ) {
        hash = PyObject_Hash( name );
        if ( hash == -1 ) {
            PyErr_Clear();
            return 0;
        }
        return ((dict->ma_lookup)( dict, name, hash )->me_value != NULL );
    }
#ifdef Py_USING_UNICODE
    if ( !PyUnicode_Check( name ) )
        return 0;

    uname = PyUnicode_AsEncodedString( name, NULL, NULL );
    if ( uname == NULL ) {
        PyErr_Clear();
	    return 0;
    }

	hash = PyObject_Hash( uname );
	if ( hash == -1 ) {
        Py_DECREF( uname );
        PyErr_Clear();
        return 0;
    }

    rc = ((dict->ma_lookup)( dict, uname, hash )->me_value != NULL);
    Py_DECREF( uname );
    return rc;
#else
    return 0;
#endif
}

//-----------------------------------------------------------------------------
//  Handles the 'getattr' operation on a 'CHasFacets' instance:
//-----------------------------------------------------------------------------

static PyObject *
has_facets_getattro ( has_facets_object * obj, PyObject * name ) {

    // The following is a performance hack to short-circuit the normal look-up
    // when the value is in the object's dictionary.
	facet_object * facet;
	PyObject     * value;
    PyObject     * uname;
    long hash;

    PyDictObject * dict = (PyDictObject *) obj->obj_dict;

	if ( dict != NULL ) {
         assert( PyDict_Check( dict ) );
         if ( PyString_CheckExact( name ) ) {
              if ( (hash = ((PyStringObject *) name)->ob_shash) == -1 )
                  hash = PyObject_Hash( name );
	         value = (dict->ma_lookup)( dict, name, hash )->me_value;
             if ( value != NULL ) {
                 Py_INCREF( value );
                 return value;
             }
         } else {
            if ( PyString_Check( name ) ) {
	    	    hash = PyObject_Hash( name );
	    	    if ( hash == -1 )
	    		    return NULL;
        	    value = (dict->ma_lookup)( dict, name, hash )->me_value;
                if ( value != NULL ) {
                    Py_INCREF( value );
                    return value;
                }
            } else {
#ifdef Py_USING_UNICODE
                if ( PyUnicode_Check( name ) ) {
                    uname = PyUnicode_AsEncodedString( name, NULL, NULL );
                    if ( uname == NULL )
            		    return NULL;
                } else {
                    invalid_attribute_error();
                    return NULL;
                }
	    	    hash = PyObject_Hash( uname );
	    	    if ( hash == -1 ) {
                    Py_DECREF( uname );
	    		    return NULL;
                }
        	    value = (dict->ma_lookup)( dict, uname, hash )->me_value;
                Py_DECREF( uname );
                if ( value != NULL ) {
                    Py_INCREF( value );
                    return value;
                }
#else
                invalid_attribute_error();
                return NULL;
#endif
            }
         }
    }
    // End of performance hack

    if ( ((obj->ifacet_dict != NULL) &&
         ((facet = (facet_object *) dict_getitem( obj->ifacet_dict, name )) !=
          NULL)) ||
         ((facet = (facet_object *) dict_getitem( obj->cfacet_dict, name )) !=
          NULL) )
        return facet->getattr( facet, obj, name );

    if ( (value = PyObject_GenericGetAttr( (PyObject *) obj, name )) != NULL )
        return value;

    PyErr_Clear();

    if ( (facet = get_prefix_facet( obj, name, 0 )) != NULL )
        return facet->getattr( facet, obj, name );

    return NULL;
}

//-----------------------------------------------------------------------------
//  Returns (and optionally creates) a specified instance or class facet:
//-----------------------------------------------------------------------------

static PyObject *
get_facet ( has_facets_object * obj, PyObject * name, int instance ) {

    Py_ssize_t i, n;
    PyDictObject * ifacet_dict;
    facet_object * facet;
    facet_object * ifacet;
    PyListObject * notifiers;
    PyListObject * inotifiers;
    PyObject     * item;

    // If there already is an instance specific version of the requested facet,
    // then return it:
    ifacet_dict = obj->ifacet_dict;
    if ( ifacet_dict != NULL ) {
        facet = (facet_object *) dict_getitem( ifacet_dict, name );
        if ( facet != NULL ) {
            assert( PyFacet_CheckExact( facet ) );
            Py_INCREF( facet );
            return (PyObject *) facet;
        }
    }

    // If only an instance facet can be returned (but not created), then
    // return None:
    if ( instance == 1 ) {
        Py_INCREF( Py_None );
        return Py_None;
    }

    // Otherwise, get the class specific version of the facet (creating a
    // facet class version if necessary):
    assert( obj->cfacet_dict != NULL );
    facet = (facet_object *) dict_getitem( obj->cfacet_dict, name );
    if ( facet == NULL ) {
        if ( instance == 0 ) {
            Py_INCREF( Py_None );
            return Py_None;
        }
        if ( (facet = get_prefix_facet( obj, name, 0 )) == NULL )
            return NULL;
    }

    assert( PyFacet_CheckExact( facet ) );

    // If an instance specific facet is not needed, return the class facet:
    if ( instance <= 0 ) {
        Py_INCREF( facet );
        return (PyObject *) facet;
    }

    // Otherwise, create an instance facet dictionary if it does not exist:
    if ( ifacet_dict == NULL ) {
		obj->ifacet_dict = ifacet_dict = (PyDictObject *) PyDict_New();
		if ( ifacet_dict == NULL )
            return NULL;
    }

    // Create a new instance facet and clone the class facet into it:
    ifacet = (facet_object *) PyType_GenericAlloc( cfacet_type, 0 );
    facet_clone( ifacet, facet );
    ifacet->obj_dict = facet->obj_dict;
    Py_XINCREF( ifacet->obj_dict );

    // Copy the class facet's notifier list into the instance facet:
    if ( (notifiers = facet->notifiers) != NULL ) {
        n = PyList_GET_SIZE( notifiers );
        ifacet->notifiers = inotifiers = (PyListObject *) PyList_New( n );
        if ( inotifiers == NULL )
            return NULL;

        for ( i = 0; i < n; i++ ) {
            item = PyList_GET_ITEM( notifiers, i );
            PyList_SET_ITEM( inotifiers, i, item );
            Py_INCREF( item );
        }
    }

    // Add the instance facet to the instance's facet dictionary and return
    // the instance facet if successful:
    if ( PyDict_SetItem( (PyObject *) ifacet_dict, name,
                         (PyObject *) ifacet ) >= 0 )
        return (PyObject *) ifacet;

    // Otherwise, indicate that an error ocurred updating the dictionary:
    return NULL;
}

//-----------------------------------------------------------------------------
//  Returns (and optionally creates) a specified instance or class facet:
//
//  The legal values for 'instance' are:
//     2: Return instance facet (force creation if it does not exist)
//     1: Return existing instance facet (do not create)
//     0: Return existing instance or class facet (do not create)
//    -1: Return instance facet or force create class facet (i.e. prefix facet)
//    -2: Return the base facet (after all delegation has been resolved)
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_facet ( has_facets_object * obj, PyObject * args ) {

    has_facets_object * delegate;
    has_facets_object * temp_delegate;
    facet_object      * facet;
    PyObject          * name;
    PyObject          * daname;
    PyObject          * daname2;
	PyObject          * dict;
    int i, instance;

    // Parse arguments, which specify the facet name and whether or not an
    // instance specific version of the facet is needed or not:
	if ( !PyArg_ParseTuple( args, "Oi", &name, &instance ) )
        return NULL;

    facet = (facet_object *) get_facet( obj, name, instance );
    if ( (instance >= -1) || (facet == NULL) )
        return (PyObject *) facet;

    // Follow the delegation chain until we find a non-delegated facet:
    delegate = obj;
    Py_INCREF( delegate );

    daname = name;
    Py_INCREF( daname );
    for ( i = 0; ; ) {

        if ( facet->delegate_attr_name == NULL ) {
            Py_DECREF( delegate );
            Py_DECREF( daname );
            return (PyObject *) facet;
        }

        dict = delegate->obj_dict;
        if ( ((dict == NULL) ||
              ((temp_delegate = (has_facets_object *) PyDict_GetItem( dict,
                                          facet->delegate_name )) == NULL)) &&
              ((temp_delegate = (has_facets_object *) has_facets_getattro(
                  delegate, facet->delegate_name )) == NULL) )
            break;

        Py_DECREF( delegate );
        delegate = temp_delegate;
        Py_INCREF( delegate );

        if ( !PyHasFacets_Check( delegate ) ) {
            bad_delegate_error2( obj, name );
            break;
        }

        daname2 = facet->delegate_attr_name( facet, obj, daname );
        Py_DECREF( daname );
        daname = daname2;
        Py_DECREF( facet );
        if ( ((delegate->ifacet_dict == NULL) ||
              ((facet = (facet_object *) dict_getitem( delegate->ifacet_dict,
                      daname )) == NULL)) &&
             ((facet = (facet_object *) dict_getitem( delegate->cfacet_dict,
                      daname )) == NULL) &&
             ((facet = get_prefix_facet( delegate, daname2, 0 )) == NULL) ) {
            bad_delegate_error( obj, name );
            break;
        }

        if ( facet->ob_type != cfacet_type ) {
            fatal_facet_error();
            break;
        }

        if ( ++i >= 100 ) {
            delegation_recursion_error2( obj, name );
            break;
        }

        Py_INCREF( facet );
    }
    Py_DECREF( delegate );
    Py_DECREF( daname );

    return NULL;
}

//-----------------------------------------------------------------------------
//  Calls notifiers when a facet 'property' is explicitly changed:
//-----------------------------------------------------------------------------

static int
facet_property_set ( has_facets_object * obj, PyObject * name,
                     PyObject * old_value, PyObject * new_value ) {

    facet_object * facet;
    PyListObject * tnotifiers;
    PyListObject * onotifiers;
    int null_new_value;
    int rc = 0;

    if ( (facet = (facet_object *) get_facet( obj, name, -1 )) == NULL )
        return -1;

    tnotifiers = facet->notifiers;
    onotifiers = obj->notifiers;
    Py_DECREF( facet );

    if ( has_notifiers( tnotifiers, onotifiers ) ) {

        null_new_value = (new_value == NULL);
        if ( null_new_value ) {
           new_value = has_facets_getattro( obj, name );
           if ( new_value == NULL )
               return -1;
        }

        rc = call_notifiers( tnotifiers, onotifiers, obj, name,
                             old_value, new_value, NULL );

        if ( null_new_value ) {
            Py_DECREF( new_value );
        }
    }

    return rc;
}

//-----------------------------------------------------------------------------
//  Calls notifiers when a facet 'property' is explicitly changed:
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_property_set ( has_facets_object * obj, PyObject * args ) {

    PyObject * name, * old_value;
    PyObject * new_value = NULL;

    // Parse arguments, which specify the name of the changed facet, the
    // previous value, and the new value:
	if ( !PyArg_ParseTuple( args, "OO|O", &name, &old_value, &new_value ) )
        return NULL;

    if ( facet_property_set( obj, name, old_value, new_value ) )
        return NULL;

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Handles firing a facets 'xxx_items' event:
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_items_event ( has_facets_object * obj, PyObject * args ) {

    PyObject * name;
    PyObject * event_object;
    PyObject * event_facet;
    PyObject * result;
    facet_object * facet;
    int can_retry = 1;

	if ( !PyArg_ParseTuple( args, "OOO", &name, &event_object, &event_facet ) )
        return NULL;

    if ( !PyFacet_CheckExact( event_facet ) ) {
        bad_facet_value_error();
        return NULL;
    }

    if ( !PyString_Check( name ) ) {
        invalid_attribute_error();
        return NULL;
    }
retry:
    if ( ((obj->ifacet_dict == NULL) ||
          ((facet = (facet_object *) dict_getitem( obj->ifacet_dict, name )) ==
            NULL)) &&
          ((facet = (facet_object *) dict_getitem( obj->cfacet_dict, name )) ==
            NULL) ) {
add_facet:
        if ( !can_retry )
            return cant_set_items_error();

        result = PyObject_CallMethod( (PyObject *) obj, "add_facet",
                                      "(OO)", name, event_facet );
        if ( result == NULL )
            return NULL;

        Py_DECREF( result );
        can_retry = 0;
        goto retry;
    }

    if ( facet->setattr == setattr_disallow )
        goto add_facet;

    if ( facet->setattr( facet, facet, obj, name, event_object ) < 0 )
        return NULL;

    Py_INCREF( Py_None );

    return Py_None;
}

//-----------------------------------------------------------------------------
//  Enables/Disables facet change notification for the object:
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_change_notify ( has_facets_object * obj, PyObject * args ) {

    int enabled;

    // Parse arguments, which specify the new facet notification
    // enabled/disabled state:
	if ( !PyArg_ParseTuple( args, "i", &enabled ) )
        return NULL;

    if ( enabled ) {
        obj->flags &= (~HASFACETS_NO_NOTIFY);
    } else {
        obj->flags |= HASFACETS_NO_NOTIFY;
    }

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Enables/Disables facet change notifications when this object is assigned to
//  a facet:
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_veto_notify ( has_facets_object * obj, PyObject * args ) {

    int enabled;

    // Parse arguments, which specify the new facet notification veto
    // enabled/disabled state:
	if ( !PyArg_ParseTuple( args, "i", &enabled ) )
        return NULL;

    if ( enabled ) {
        obj->flags |= HASFACETS_VETO_NOTIFY;
    } else {
        obj->flags &= (~HASFACETS_VETO_NOTIFY);
    }

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  This method is called at the end of a HasFacets constructor and the
//  __setstate__ method to perform any final object initialization needed.
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_init ( has_facets_object * obj ) {

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Returns whether or not the object has finished being initialized:
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_inited ( has_facets_object * obj, PyObject * args ) {

    int facets_inited = -1;

	if ( !PyArg_ParseTuple( args, "|i", &facets_inited ) )
        return NULL;

    if ( facets_inited > 0 )
        obj->flags |= HASFACETS_INITED;

    if ( obj->flags & HASFACETS_INITED ) {
        Py_INCREF( Py_True );
        return Py_True;
    }
    Py_INCREF( Py_False );
    return Py_False;
}

//-----------------------------------------------------------------------------
//  Returns the instance facet dictionary:
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_instance_facets ( has_facets_object * obj, PyObject * args ) {

	if ( !PyArg_ParseTuple( args, "" ) )
        return NULL;

    if ( obj->ifacet_dict == NULL )
		obj->ifacet_dict = (PyDictObject *) PyDict_New();

    Py_XINCREF( obj->ifacet_dict );

    return (PyObject *) obj->ifacet_dict;
}

//-----------------------------------------------------------------------------
//  Returns (and optionally creates) the anyfacet 'notifiers' list:
//-----------------------------------------------------------------------------

static PyObject *
_has_facets_notifiers ( has_facets_object * obj, PyObject * args ) {

    PyObject * result;
    PyObject * list;
    int force_create;

	if ( !PyArg_ParseTuple( args, "i", &force_create ) )
        return NULL;

    result = (PyObject *) obj->notifiers;
    if ( result == NULL ) {
        result = Py_None;
        if ( force_create && ((list = PyList_New( 0 )) != NULL) ) {
            obj->notifiers = (PyListObject *) (result = list);
            Py_INCREF( result );
        }
    }
    Py_INCREF( result );

    return result;
}

//-----------------------------------------------------------------------------
//  Returns the object's instance dictionary:
//-----------------------------------------------------------------------------

static PyObject *
get_has_facets_dict ( has_facets_object * obj, void * closure ) {

    PyObject * obj_dict = obj->obj_dict;
    if ( obj_dict == NULL ) {
        obj->obj_dict = obj_dict = PyDict_New();
        if ( obj_dict == NULL )
            return NULL;
    }
    Py_INCREF( obj_dict );

    return obj_dict;
}

//-----------------------------------------------------------------------------
//  Sets the object's dictionary:
//-----------------------------------------------------------------------------

static int
set_has_facets_dict ( has_facets_object * obj, PyObject * value,
                      void * closure ) {

    if ( !PyDict_Check( value ) )
        return dictionary_error();

    return set_value( &obj->obj_dict, value );
}

//-----------------------------------------------------------------------------
//  'CHasFacets' instance methods:
//-----------------------------------------------------------------------------

static PyMethodDef has_facets_methods[] = {
	{ "facet_property_set", (PyCFunction) _has_facets_property_set,
      METH_VARARGS,
      PyDoc_STR( "facet_property_set(name,old_value[,new_value])" ) },
	{ "facet_items_event", (PyCFunction) _has_facets_items_event, METH_VARARGS,
      PyDoc_STR( "facet_items_event(name,event_object,event_facet)" ) },
	{ "_facet_change_notify", (PyCFunction) _has_facets_change_notify,
      METH_VARARGS,
      PyDoc_STR( "_facet_change_notify(boolean)" ) },
	{ "_facet_veto_notify", (PyCFunction) _has_facets_veto_notify,
      METH_VARARGS,
      PyDoc_STR( "_facet_veto_notify(boolean)" ) },
	{ "facets_init", (PyCFunction) _has_facets_init,
      METH_NOARGS,
      PyDoc_STR( "facets_init()" ) },
	{ "facets_inited", (PyCFunction) _has_facets_inited,       METH_VARARGS,
      PyDoc_STR( "facets_inited([True])" ) },
	{ "_facet",           (PyCFunction) _has_facets_facet,     METH_VARARGS,
      PyDoc_STR( "_facet(name,instance) -> facet" ) },
	{ "_instance_facets", (PyCFunction) _has_facets_instance_facets,
      METH_VARARGS,
      PyDoc_STR( "_instance_facets() -> dict" ) },
	{ "_notifiers",       (PyCFunction) _has_facets_notifiers, METH_VARARGS,
      PyDoc_STR( "_notifiers(force_create) -> list" ) },
	{ NULL,	NULL },
};

//-----------------------------------------------------------------------------
//  'CHasFacets' property definitions:
//-----------------------------------------------------------------------------

static PyGetSetDef has_facets_properties[] = {
	{ "__dict__",  (getter) get_has_facets_dict,
                   (setter) set_has_facets_dict },
	{ 0 }
};

//-----------------------------------------------------------------------------
//  'CHasFacets' type definition:
//-----------------------------------------------------------------------------

static PyTypeObject has_facets_type = {
	PyObject_HEAD_INIT( DEFERRED_ADDRESS( &PyType_Type ) )
	0,
	"CHasFacets",
	sizeof( has_facets_object ),
	0,
	(destructor) has_facets_dealloc,                    // tp_dealloc
	0,                                                  // tp_print
	0,                                                  // tp_getattr
	0,                                                  // tp_setattr
	0,                                                  // tp_compare
	0,                                                  // tp_repr
	0,                                                  // tp_as_number
	0,                                                  // tp_as_sequence
	0,                                                  // tp_as_mapping
	0,                                                  // tp_hash
	0,                                                  // tp_call
	0,                                                  // tp_str
	(getattrofunc) has_facets_getattro,                 // tp_getattro
	(setattrofunc) has_facets_setattro,                 // tp_setattro
	0,					                                // tp_as_buffer
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, // tp_flags
	0,                                                  // tp_doc
	(traverseproc) has_facets_traverse,                 // tp_traverse
	(inquiry) has_facets_clear,                         // tp_clear
	0,                                                  // tp_richcompare
	0,                                                  // tp_weaklistoffset
	0,                                                  // tp_iter
	0,                                                  // tp_iternext
	has_facets_methods,                                 // tp_methods
	0,                                                  // tp_members
	has_facets_properties,                              // tp_getset
	DEFERRED_ADDRESS( &PyBaseObject_Type ),             // tp_base
	0,                                                  // tp_dict
	0,                                                  // tp_descr_get
	0,				        	                        // tp_descr_set
	sizeof( has_facets_object ) - sizeof( PyObject * ), // tp_dictoffset
	has_facets_init,                                    // tp_init
	DEFERRED_ADDRESS( PyType_GenericAlloc ),            // tp_alloc
	has_facets_new                                      // tp_new
};

//-----------------------------------------------------------------------------
//  Returns the default value associated with a specified facet:
//-----------------------------------------------------------------------------

static PyObject *
default_value_for ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name ) {

    PyObject * result = NULL, * value, * dv, * kw, * tuple;

    switch ( facet->default_value_type ) {
        case 0:
        case 1:
            result = facet->default_value;
            Py_INCREF( result );
            break;
        case 2:
            result = (PyObject *) obj;
            Py_INCREF( obj );
            break;
        case 3:
            return PySequence_List( facet->default_value );
        case 4:
            return PyDict_Copy( facet->default_value );
        case 5:
            dv = facet->default_value;
            return call_class( PyTuple_GET_ITEM( dv, 0 ), facet, obj, name,
                               PyTuple_GET_ITEM( dv, 1 ) );
//      case 6: No longer in use...can be re-used if necessary.
        case 7:
            dv = facet->default_value;
            kw = PyTuple_GET_ITEM( dv, 2 );
            if ( kw == Py_None )
                kw = NULL;
            return PyObject_Call( PyTuple_GET_ITEM( dv, 0 ),
                                  PyTuple_GET_ITEM( dv, 1 ), kw );
        case 8:
            if ( (tuple = PyTuple_New( 1 )) == NULL )
                return NULL;
            PyTuple_SET_ITEM( tuple, 0, (PyObject *) obj );
            Py_INCREF( obj );
            result = PyObject_Call( facet->default_value, tuple, NULL );
            Py_DECREF( tuple );
            if ( (result != NULL) && (facet->validate != NULL) ) {
                value = facet->validate( facet, obj, name, result );
                Py_DECREF( result );
                return value;
            }
            break;
    }
    return result;
}

//-----------------------------------------------------------------------------
//  Returns the value assigned to a standard Python attribute:
//-----------------------------------------------------------------------------

static PyObject *
getattr_python ( facet_object      * facet,
                 has_facets_object * obj,
                 PyObject          * name ) {

    return PyObject_GenericGetAttr( (PyObject *) obj, name );
}

//-----------------------------------------------------------------------------
//  Returns the value assigned to a generic Python attribute:
//-----------------------------------------------------------------------------

static PyObject *
getattr_generic ( facet_object      * facet,
                  has_facets_object * obj,
                  PyObject          * name ) {

    return PyObject_GenericGetAttr( (PyObject *) obj, name );
}

//-----------------------------------------------------------------------------
//  Returns the value assigned to an event facet:
//-----------------------------------------------------------------------------

static PyObject *
getattr_event ( facet_object      * facet,
                has_facets_object * obj,
                PyObject          * name ) {

    PyErr_Format( PyExc_AttributeError,
        "The %.400s facet of a %.50s instance is an 'event', which is write only.",
        PyString_AS_STRING( name ), obj->ob_type->tp_name );

    return NULL;
}

//-----------------------------------------------------------------------------
//  Returns the value assigned to a standard facet:
//-----------------------------------------------------------------------------

static PyObject *
getattr_facet ( facet_object      * facet,
                has_facets_object * obj,
                PyObject          * name ) {

    int rc;
    PyListObject * tnotifiers;
    PyListObject * onotifiers;
    PyObject * result;
    PyObject * dict = obj->obj_dict;

	if ( dict == NULL ) {
		dict = PyDict_New();
		if ( dict == NULL )
            return NULL;

		obj->obj_dict = dict;
	}

	if ( PyString_Check( name ) ) {
        if ( (result = default_value_for( facet, obj, name )) != NULL ) {
            if ( PyDict_SetItem( dict, name, result ) >= 0 ) {

                rc = 0;
                if ( (facet->post_setattr != NULL) &&
                     ((facet->flags & FACET_IS_MAPPED) == 0) )
                    rc = facet->post_setattr( facet, obj, name, result );

                if ( (rc == 0) && ((obj->flags & HASFACETS_NO_NOTIFY) == 0) ) {
                    tnotifiers = facet->notifiers;
                    onotifiers = obj->notifiers;
                    if ( has_notifiers( tnotifiers, onotifiers ) )
                        rc = call_notifiers( tnotifiers, onotifiers, obj, name,
                                             Uninitialized, result, NULL );
                }
                if ( rc == 0 )
                    return result;
            }
            Py_DECREF( result );
        }

        if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
    		PyErr_SetObject( PyExc_AttributeError, name );

        return NULL;
    }

#ifdef Py_USING_UNICODE
    if ( PyUnicode_Check( name ) ) {
        name = PyUnicode_AsEncodedString( name, NULL, NULL );
        if ( name == NULL )
		    return NULL;
    } else {
        invalid_attribute_error();
        return NULL;
    }

    if ( (result = default_value_for( facet, obj, name )) != NULL ) {
        if ( PyDict_SetItem( dict, name, result ) >= 0 ) {

            rc = 0;
            if ( (facet->post_setattr != NULL) &&
                 ((facet->flags & FACET_IS_MAPPED) == 0) )
                rc = facet->post_setattr( facet, obj, name, result );

            if ( (rc == 0) && ((obj->flags & HASFACETS_NO_NOTIFY) == 0) ) {
                tnotifiers = facet->notifiers;
                onotifiers = obj->notifiers;
                if ( has_notifiers( tnotifiers, onotifiers ) )
                    rc = call_notifiers( tnotifiers, onotifiers, obj, name,
                                         Uninitialized, result, NULL );
            }
            if ( rc == 0 ) {
                Py_DECREF( name );
                return result;
            }
        }
        Py_DECREF( result );
    }

    if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
		PyErr_SetObject( PyExc_AttributeError, name );

    Py_DECREF( name );
    return NULL;
#else
    invalid_attribute_error();
    return NULL;
#endif
}

//-----------------------------------------------------------------------------
//  Returns the value assigned to a delegated facet:
//-----------------------------------------------------------------------------

static PyObject *
getattr_delegate ( facet_object      * facet,
                   has_facets_object * obj,
                   PyObject          * name ) {

	PyTypeObject * tp;
    PyObject     * delegate_attr_name;
    PyObject     * delegate;
    PyObject     * result;
    PyObject     * dict = obj->obj_dict;

    if ( (dict == NULL) ||
         ((delegate = PyDict_GetItem( dict, facet->delegate_name )) == NULL) ){
        // Handle the case when the delegate is not in the instance dictionary
        // (could be a method that returns the real delegate):
        delegate = has_facets_getattro( obj, facet->delegate_name );
        if ( delegate == NULL )
            return NULL;
    } else {
        Py_INCREF( delegate );
    }

	if ( PyString_Check( name ) ) {
        delegate_attr_name = facet->delegate_attr_name( facet, obj, name );
    	tp = delegate->ob_type;

    	if ( tp->tp_getattro != NULL ) {
    		result = (*tp->tp_getattro)( delegate, delegate_attr_name );
            goto done2;
        }

    	if ( tp->tp_getattr != NULL ) {
    		result = (*tp->tp_getattr)( delegate,
                                     PyString_AS_STRING( delegate_attr_name ) );
            goto done2;
        }

    	PyErr_Format( DelegationError,
    	    "The '%.50s' object has no attribute '%.400s' because its %.50s delegate has no attribute '%.400s'.",
    		obj->ob_type->tp_name, PyString_AS_STRING( name ),
            tp->tp_name, PyString_AS_STRING( delegate_attr_name ) );
        result = NULL;
        goto done2;
    }

#ifdef Py_USING_UNICODE
    if ( PyUnicode_Check( name ) ) {
        name = PyUnicode_AsEncodedString( name, NULL, NULL );
        if ( name == NULL ) {
            Py_DECREF( delegate );
		    return NULL;
        }
    } else {
        invalid_attribute_error();
        Py_DECREF( delegate );

        return NULL;
    }

    delegate_attr_name = facet->delegate_attr_name( facet, obj, name );
	tp = delegate->ob_type;

	if ( tp->tp_getattro != NULL ) {
		result = (*tp->tp_getattro)( delegate, delegate_attr_name );
        goto done;
    }

	if ( tp->tp_getattr != NULL ) {
		result = (*tp->tp_getattr)( delegate,
                                    PyString_AS_STRING( delegate_attr_name ) );
        goto done;
    }

	PyErr_Format( DelegationError,
	    "The '%.50s' object has no attribute '%.400s' because its %.50s delegate has no attribute '%.400s'.",
		obj->ob_type->tp_name, PyString_AS_STRING( name ),
        tp->tp_name, PyString_AS_STRING( delegate_attr_name ) );
    result = NULL;

done:
    Py_DECREF( name );
done2:
    Py_DECREF( delegate_attr_name );
    Py_DECREF( delegate );

	return result;
#else
    invalid_attribute_error();
    Py_DECREF( delegate );

    return NULL;

done2:
    Py_DECREF( delegate_attr_name );
    Py_DECREF( delegate );

	return result;
#endif
}

//-----------------------------------------------------------------------------
//  Raises an exception when a disallowed facet is accessed:
//-----------------------------------------------------------------------------

static PyObject *
getattr_disallow ( facet_object      * facet,
                   has_facets_object * obj,
                   PyObject          * name ) {

    if ( PyString_Check( name ) )
        unknown_attribute_error( obj, name );
    else
        invalid_attribute_error();

    return NULL;
}

//-----------------------------------------------------------------------------
//  Returns the value of a constant facet:
//-----------------------------------------------------------------------------

static PyObject *
getattr_constant ( facet_object      * facet,
                   has_facets_object * obj,
                   PyObject          * name ) {

    Py_INCREF( facet->default_value );
    return facet->default_value;
}

//-----------------------------------------------------------------------------
//  Assigns a value to a specified property facet attribute:
//-----------------------------------------------------------------------------

static PyObject *
getattr_property0 ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name ) {

    return PyObject_Call( facet->delegate_name, empty_tuple, NULL );
}

static PyObject *
getattr_property1 ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 1 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    Py_INCREF( obj );
    result = PyObject_Call( facet->delegate_name, args, NULL );
    Py_DECREF( args );

    return result;
}

static PyObject *
getattr_property2 ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 2 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    Py_INCREF( obj );
    PyTuple_SET_ITEM( args, 1, name );
    Py_INCREF( name );
    result = PyObject_Call( facet->delegate_name, args, NULL );
    Py_DECREF( args );

    return result;
}

static PyObject *
getattr_property3 ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    Py_INCREF( obj );
    PyTuple_SET_ITEM( args, 1, name );
    Py_INCREF( name );
    PyTuple_SET_ITEM( args, 2, (PyObject *) facet );
    Py_INCREF( facet );
    result = PyObject_Call( facet->delegate_name, args, NULL );
    Py_DECREF( args );

    return result;
}

static facet_getattr getattr_property_handlers[] = {
    getattr_property0, getattr_property1, getattr_property2, getattr_property3
};

//-----------------------------------------------------------------------------
//  Assigns a value to a specified standard Python attribute:
//-----------------------------------------------------------------------------

static int
setattr_python ( facet_object      * faceto,
                 facet_object      * facetd,
                 has_facets_object * obj,
                 PyObject          * name,
                 PyObject          * value ) {

    int rc;
    PyObject * dict = obj->obj_dict;

    if ( value != NULL ) {
        if ( dict == NULL ) {
            dict = PyDict_New();
            if ( dict == NULL )
                return -1;
        	obj->obj_dict = dict;
        }
        if ( PyString_Check( name ) ) {
            if ( PyDict_SetItem( dict, name, value ) >= 0 )
                return 0;
    		if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
    			PyErr_SetObject( PyExc_AttributeError, name );
            return -1;
    	}
#ifdef Py_USING_UNICODE
        if ( PyUnicode_Check( name ) ) {
            name = PyUnicode_AsEncodedString( name, NULL, NULL );
            if ( name == NULL )
        	    return -1;
        } else
            return invalid_attribute_error();

        rc = PyDict_SetItem( dict, name, value );
        if ( (rc < 0) && PyErr_ExceptionMatches( PyExc_KeyError ) )
             PyErr_SetObject( PyExc_AttributeError, name );
        Py_DECREF( name );

        return rc;
#else
        return invalid_attribute_error();
#endif
    }

    if ( dict != NULL ) {
        if ( PyString_Check( name ) ) {
            if ( PyDict_DelItem( dict, name ) >= 0 )
                return 0;

            if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
                unknown_attribute_error( obj, name );

            return -1;
        }
#ifdef Py_USING_UNICODE
        if ( PyUnicode_Check( name ) ) {
            name = PyUnicode_AsEncodedString( name, NULL, NULL );
            if ( name == NULL )
        	    return -1;
        } else
            return invalid_attribute_error();

        rc = PyDict_DelItem( dict, name );
        if ( (rc < 0) && PyErr_ExceptionMatches( PyExc_KeyError ) )
            unknown_attribute_error( obj, name );

        Py_DECREF( name );

        return rc;
#else
        return invalid_attribute_error();
#endif
    }

    if ( PyString_Check( name ) ) {
        unknown_attribute_error( obj, name );

        return -1;
    }

    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Assigns a value to a specified generic Python attribute:
//-----------------------------------------------------------------------------

static int
setattr_generic ( facet_object      * faceto,
                  facet_object      * facetd,
                  has_facets_object * obj,
                  PyObject          * name,
                  PyObject          * value ) {

    return PyObject_GenericSetAttr( (PyObject *) obj, name, value );
}

//-----------------------------------------------------------------------------
//  Call all notifiers for a specified facet:
//-----------------------------------------------------------------------------

static int
call_notifiers ( PyListObject      * tnotifiers,
                 PyListObject      * onotifiers,
                 has_facets_object * obj,
                 PyObject          * name,
                 PyObject          * old_value,
                 PyObject          * new_value,
                 PyObject          * notify ) {

    int new_value_has_facets, rc;
    Py_ssize_t i, n;
    PyObject * result, * item, * temp, * args, * arg_temp, * user_args;

    if ( notify == NULL ) {
        notify = PyObject_CallFunctionObjArgs(
            (PyObject *) &facet_notification_type, fn_item_index, obj, name,
            new_value, old_value, NULL
        );
        if ( notify == NULL )
            return -1;
    }

    args = PyTuple_New( 5 );
    if ( args == NULL ) {
        Py_DECREF( notify );
        return -1;
    }

    new_value_has_facets = PyHasFacets_Check( new_value );
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, old_value );
    PyTuple_SET_ITEM( args, 3, new_value );
    PyTuple_SET_ITEM( args, 4, notify );  // Give the notify reference to args
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( old_value );
    Py_INCREF( new_value );

    rc        = 0;
    arg_temp  = Py_None;
    user_args = NULL;

    if ( _facet_notification_handler != NULL ) {
        user_args = PyTuple_New( 2 );
        if ( user_args == NULL ) {
            Py_DECREF( args );
            return -1;
        }
        PyTuple_SET_ITEM( user_args, 0, arg_temp );
        PyTuple_SET_ITEM( user_args, 1, args );
        Py_INCREF( arg_temp );
        Py_INCREF( args );
    }

    if ( tnotifiers != NULL ) {
        n    = PyList_GET_SIZE( tnotifiers );
        temp = NULL;
        if ( n > 1 ) {
            temp = PyList_New( n );
            if ( temp == NULL ) {
                rc = -1;
                goto exit2;
            }
            for ( i = 0; i < n; i++ ) {
                item = PyList_GET_ITEM( tnotifiers, i );
                PyList_SET_ITEM( temp, i, item );
                Py_INCREF( item );
            }
            tnotifiers = (PyListObject *) temp;
        }
        for ( i = 0; i < n; i++ ) {
            if ( new_value_has_facets &&
                 (((has_facets_object *) new_value)->flags &
                    HASFACETS_VETO_NOTIFY) ) {
                goto exit;
            }
            if ( (_facet_notification_handler != NULL) &&
                 (user_args != NULL) ) {
                Py_DECREF( arg_temp );
                arg_temp = PyList_GET_ITEM( tnotifiers, i );
                Py_INCREF( arg_temp );
                PyTuple_SET_ITEM( user_args, 0, arg_temp );
                result = PyObject_Call( _facet_notification_handler,
                                        user_args, NULL );
            } else {
                result = PyObject_Call( PyList_GET_ITEM( tnotifiers, i ),
                                        args, NULL );
            }
            if ( result == NULL ) {
                rc = -1;
                goto exit;
            }
            Py_DECREF( result );
        }
        Py_XDECREF( temp );
    }

    temp = NULL;
    if ( onotifiers != NULL ) {
        n = PyList_GET_SIZE( onotifiers );
        if ( n > 1 ) {
            temp = PyList_New( n );
            if ( temp == NULL ) {
                rc = -1;
                goto exit2;
            }
            for ( i = 0; i < n; i++ ) {
                item = PyList_GET_ITEM( onotifiers, i );
                PyList_SET_ITEM( temp, i, item );
                Py_INCREF( item );
            }
            onotifiers = (PyListObject *) temp;
        }
        for ( i = 0; i < n; i++ ) {
            if ( new_value_has_facets &&
                 (((has_facets_object *) new_value)->flags &
                    HASFACETS_VETO_NOTIFY) ) {
                break;
            }
            if ( (_facet_notification_handler != NULL) && (user_args != NULL) ){
                Py_DECREF( arg_temp );
                arg_temp = PyList_GET_ITEM( onotifiers, i );
                Py_INCREF( arg_temp );
                PyTuple_SET_ITEM( user_args, 0, arg_temp );
                result = PyObject_Call( _facet_notification_handler,
                                        user_args, NULL );
            } else {
                result = PyObject_Call( PyList_GET_ITEM( onotifiers, i ),
                                        args, NULL );
            }
            if ( result == NULL ) {
                rc = -1;
                goto exit;
            }
            Py_DECREF( result );
        }
    }
exit:
    Py_XDECREF( temp );
exit2:
    Py_XDECREF( user_args );
    Py_DECREF( args );

    return rc;
}

//-----------------------------------------------------------------------------
//  Assigns a value to a specified event facet attribute:
//-----------------------------------------------------------------------------

static int
setattr_event ( facet_object      * faceto,
                facet_object      * facetd,
                has_facets_object * obj,
                PyObject          * name,
                PyObject          * value ) {

    int rc = 0;
    PyListObject * tnotifiers;
    PyListObject * onotifiers;

    if ( value != NULL ) {
        if ( facetd->validate != NULL ) {
            value = facetd->validate( facetd, obj, name, value );
            if ( value == NULL )
                return -1;
        } else {
            Py_INCREF( value );
        }

        tnotifiers = faceto->notifiers;
        onotifiers = obj->notifiers;

        if ( ((obj->flags & HASFACETS_NO_NOTIFY) == 0) &&
             has_notifiers( tnotifiers, onotifiers ) )
            rc = call_notifiers( tnotifiers, onotifiers, obj, name,
                                 Undefined, value, NULL );

        Py_DECREF( value );
    }

    return rc;
}

//-----------------------------------------------------------------------------
//  Assigns a value to a specified normal facet attribute:
//-----------------------------------------------------------------------------

static int
setattr_facet ( facet_object      * faceto,
                facet_object      * facetd,
                has_facets_object * obj,
                PyObject          * name,
                PyObject          * value ) {

    int rc;
    int changed;
    int do_notifiers;
    facet_post_setattr post_setattr;
    PyListObject * tnotifiers = NULL;
    PyListObject * onotifiers = NULL;
    PyObject     * old_value  = NULL;
    PyObject     * original_value;
    PyObject     * new_value;

    PyObject * dict = obj->obj_dict;

    changed = (facetd->flags & FACET_NO_VALUE_TEST);

    if ( value == NULL ) {
        if ( dict == NULL )
            return 0;

        if ( PyString_Check( name ) ) {
            old_value = PyDict_GetItem( dict, name );
            if ( old_value == NULL )
                return 0;

            Py_INCREF( old_value );
            if ( PyDict_DelItem( dict, name ) < 0 ) {
                Py_DECREF( old_value );
                return -1;
            }

            Py_INCREF( name );
notify:
            rc = 0;
            if ( (obj->flags & HASFACETS_NO_NOTIFY) == 0 ) {
                tnotifiers = faceto->notifiers;
                onotifiers = obj->notifiers;
                if ( (tnotifiers != NULL) || (onotifiers != NULL) ) {
                    value = faceto->getattr( faceto, obj, name );
                    if ( value == NULL ) {
                        Py_DECREF( old_value );
                        Py_DECREF( name );
                        return -1;
                    }

                    if ( !changed ) {
                        changed = (old_value != value );
                        if ( changed &&
                             ((facetd->flags & FACET_OBJECT_IDENTITY) == 0) ) {
                            changed = PyObject_RichCompareBool( old_value,
                                                                value, Py_NE );
                            if ( changed == -1 ) {
                                PyErr_Clear();
                            }
                        }
                    }

                    if ( changed ) {
                        if ( facetd->post_setattr != NULL )
                            rc = facetd->post_setattr( facetd, obj, name,
                                                       value );
                        if ( (rc == 0) &&
                             has_notifiers( tnotifiers, onotifiers ) )
                            rc = call_notifiers( tnotifiers, onotifiers,
                                            obj, name, old_value, value, NULL );
                    }

                    Py_DECREF( value );
                }
            }
            Py_DECREF( name );
            Py_DECREF( old_value );
            return rc;
        }
#ifdef Py_USING_UNICODE
        if ( PyUnicode_Check( name ) ) {
            name = PyUnicode_AsEncodedString( name, NULL, NULL );
            if ( name == NULL ) {
          	    return -1;
            }
        } else {
            return invalid_attribute_error();
        }

        old_value = PyDict_GetItem( dict, name );
        if ( old_value == NULL ) {
            Py_DECREF( name );
            return 0;
        }

        Py_INCREF( old_value );
        if ( PyDict_DelItem( dict, name ) < 0 ) {
            Py_DECREF( old_value );
            Py_DECREF( name );
            return -1;
        }

        goto notify;
#else
        return invalid_attribute_error();
#endif
    }

    original_value = value;
    if ( facetd->validate != NULL ) {
        value = facetd->validate( facetd, obj, name, value );
        if ( value == NULL ) {
            return -1;
        }
    } else {
        Py_INCREF( value );
    }

    if ( dict == NULL ) {
        obj->obj_dict = dict = PyDict_New();
        if ( dict == NULL ) {
            Py_DECREF( value );
            return -1;
        }
    }

    if ( !PyString_Check( name ) ) {
#ifdef Py_USING_UNICODE
        if ( PyUnicode_Check( name ) ) {
            name = PyUnicode_AsEncodedString( name, NULL, NULL );
            if ( name == NULL ) {
                Py_DECREF( value );
        	        return -1;
            }
        } else {
            Py_DECREF( value );
            return invalid_attribute_error();
        }
#else
        Py_DECREF( value );
        return invalid_attribute_error();
#endif
    } else {
        Py_INCREF( name );
    }

    new_value    = (facetd->flags & FACET_SETATTR_ORIGINAL_VALUE)?
                   original_value: value;
    old_value    = NULL;
    do_notifiers = ((obj->flags & HASFACETS_NO_NOTIFY) == 0);
    if ( do_notifiers ) {
        tnotifiers    = faceto->notifiers;
        onotifiers    = obj->notifiers;
        do_notifiers &= has_notifiers( tnotifiers, onotifiers );
    }

    post_setattr = facetd->post_setattr;
    if ( (post_setattr != NULL) || do_notifiers ) {
        old_value = PyDict_GetItem( dict, name );
        if ( old_value == NULL ) {
            if ( facetd != faceto ) {
                old_value = faceto->getattr( faceto, obj, name );
            } else {
                old_value = default_value_for( facetd, obj, name );
            }
            if ( old_value == NULL ) {
                Py_DECREF( name );
                Py_DECREF( value );

                return -1;
            }
        } else {
            Py_INCREF( old_value );
        }

        if ( !changed ) {
            changed = (old_value != value);
            if ( changed &&
                 ((facetd->flags & FACET_OBJECT_IDENTITY) == 0) ) {
                changed = PyObject_RichCompareBool( old_value, value, Py_NE );
                if ( changed == -1 ) {
                    PyErr_Clear();
                }
            }
        }
    }

    if ( PyDict_SetItem( dict, name, new_value ) < 0 ) {
        if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
            PyErr_SetObject( PyExc_AttributeError, name );
        Py_XDECREF( old_value );
        Py_DECREF( name );
        Py_DECREF( value );

        return -1;
    }

    rc = 0;

    if ( changed ) {
        if ( post_setattr != NULL )
            rc = post_setattr( facetd, obj, name,
                    (facetd->flags & FACET_POST_SETATTR_ORIGINAL_VALUE)?
                    original_value: value );

        if ( (rc == 0) && do_notifiers )
            rc = call_notifiers( tnotifiers, onotifiers, obj, name,
                                 old_value, new_value, NULL );
    }

    Py_XDECREF( old_value );
    Py_DECREF( name );
    Py_DECREF( value );

    return rc;
}

//-----------------------------------------------------------------------------
//  Assigns a value to a specified delegate facet attribute:
//-----------------------------------------------------------------------------

static int
setattr_delegate ( facet_object      * faceto,
                   facet_object      * facetd,
                   has_facets_object * obj,
                   PyObject          * name,
                   PyObject          * value ) {

	PyObject          * dict;
    PyObject          * daname;
    PyObject          * daname2;
    PyObject          * temp;
    has_facets_object * delegate;
    has_facets_object * temp_delegate;
	int i, result;

    // Follow the delegation chain until we find a non-delegated facet:
    daname = name;
    Py_INCREF( daname );
    delegate = obj;
    for ( i = 0; ; ) {
        dict = delegate->obj_dict;
        if ( (dict != NULL) &&
             ((temp_delegate = (has_facets_object *) PyDict_GetItem( dict,
                                          facetd->delegate_name )) != NULL) ) {
            delegate = temp_delegate;
        } else {
            // Handle the case when the delegate is not in the instance
            // dictionary (could be a method that returns the real delegate):
            delegate = (has_facets_object *) has_facets_getattro( delegate,
                                                       facetd->delegate_name );
            if ( delegate == NULL ) {
                Py_DECREF( daname );
                return -1;
            }
            Py_DECREF( delegate );
        }

        // Verify that 'delegate' is of type 'CHasFacets':
        if ( !PyHasFacets_Check( delegate ) ) {
            Py_DECREF( daname );
            return bad_delegate_error2( obj, name );
        }

        daname2 = facetd->delegate_attr_name( facetd, obj, daname );
        Py_DECREF( daname );
        daname = daname2;
        if ( ((delegate->ifacet_dict == NULL) ||
              ((facetd = (facet_object *) dict_getitem( delegate->ifacet_dict,
                      daname )) == NULL)) &&
             ((facetd = (facet_object *) dict_getitem( delegate->cfacet_dict,
                      daname )) == NULL) &&
             ((facetd = get_prefix_facet( delegate, daname, 1 )) == NULL) ) {
            Py_DECREF( daname );
            return bad_delegate_error( obj, name );
        }

        if ( facetd->ob_type != cfacet_type ) {
            Py_DECREF( daname );
            return fatal_facet_error();
        }

        if ( facetd->delegate_attr_name == NULL ) {
            if ( faceto->flags & FACET_MODIFY_DELEGATE ) {
                result = facetd->setattr( facetd, facetd, delegate, daname,
                                          value );
            } else {
                result = facetd->setattr( faceto, facetd, obj, name, value );
                if ( result >= 0 ) {
                    temp = PyObject_CallMethod( (PyObject *) obj,
                               "_remove_facet_delegate_listener", "(OOi)",
                               name, faceto, value != NULL );
                    if ( temp == NULL ) {
                        result = -1;
                    } else {
                        Py_DECREF( temp );
                    }
                }
            }
            Py_DECREF( daname );

            return result;
        }

        if ( ++i >= 100 )
            return delegation_recursion_error( obj, name );
    }
}

//-----------------------------------------------------------------------------
//  Assigns a value to a specified property facet attribute:
//-----------------------------------------------------------------------------

static int
setattr_property0 ( facet_object      * faceto,
                    facet_object      * facetd,
                    has_facets_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * result;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    result = PyObject_Call( facetd->delegate_prefix, empty_tuple, NULL );
    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

static int
setattr_property1 ( facet_object      * faceto,
                    facet_object      * facetd,
                    has_facets_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * result;
    PyObject * args;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    args = PyTuple_New( 1 );
    if ( args == NULL )
        return -1;

    PyTuple_SET_ITEM( args, 0, value );
    Py_INCREF( value );
    result = PyObject_Call( facetd->delegate_prefix, args, NULL );
    Py_DECREF( args );
    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

static int
setattr_property2 ( facet_object      * faceto,
                    facet_object      * facetd,
                    has_facets_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * result;
    PyObject * args;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    args = PyTuple_New( 2 );
    if ( args == NULL )
        return -1;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, value );
    Py_INCREF( obj );
    Py_INCREF( value );
    result = PyObject_Call( facetd->delegate_prefix, args, NULL );
    Py_DECREF( args );
    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

static int
setattr_property3 ( facet_object      * faceto,
                    facet_object      * facetd,
                    has_facets_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * result;
    PyObject * args;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    args = PyTuple_New( 3 );
    if ( args == NULL )
        return -1;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    result = PyObject_Call( facetd->delegate_prefix, args, NULL );
    Py_DECREF( args );
    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

//-----------------------------------------------------------------------------
//  Validates then assigns a value to a specified property facet attribute:
//-----------------------------------------------------------------------------

static int
setattr_validate_property ( facet_object      * faceto,
                            facet_object      * facetd,
                            has_facets_object * obj,
                            PyObject          * name,
                            PyObject          * value ) {

    int result;

    PyObject * validated = facetd->validate( facetd, obj, name, value );
    if ( validated == NULL )
        return -1;
    result = ((facet_setattr) facetd->post_setattr)( faceto, facetd, obj, name,
		                                             validated );
    Py_DECREF( validated );
    return result;
}

static PyObject *
setattr_validate0 ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    return PyObject_Call( facet->py_validate, empty_tuple, NULL );
}

static PyObject *
setattr_validate1 ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * validated;

    PyObject * args = PyTuple_New( 1 );
    if ( args == NULL )
        return NULL;
    PyTuple_SET_ITEM( args, 0, value );
    Py_INCREF( value );
    validated = PyObject_Call( facet->py_validate, args, NULL );
    Py_DECREF( args );
    return validated;
}

static PyObject *
setattr_validate2 ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * validated;

    PyObject * args = PyTuple_New( 2 );
    if ( args == NULL )
        return NULL;
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, value );
    Py_INCREF( obj );
    Py_INCREF( value );
    validated = PyObject_Call( facet->py_validate, args, NULL );
    Py_DECREF( args );
    return validated;
}

static PyObject *
setattr_validate3 ( facet_object      * facet,
                    has_facets_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * validated;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return NULL;
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    validated = PyObject_Call( facet->py_validate, args, NULL );
    Py_DECREF( args );
    return validated;
}

facet_validate setattr_validate_handlers[] = {
    setattr_validate0, setattr_validate1, setattr_validate2, setattr_validate3
};

//-----------------------------------------------------------------------------
//  Raises an exception when attempting to assign to a disallowed facet:
//-----------------------------------------------------------------------------

static int
setattr_disallow ( facet_object      * faceto,
                   facet_object      * facetd,
                   has_facets_object * obj,
                   PyObject          * name,
                   PyObject          * value ) {

    return set_disallow_error( obj, name );
}

//-----------------------------------------------------------------------------
//  Assigns a value to a specified read-only facet attribute:
//-----------------------------------------------------------------------------

static int
setattr_readonly ( facet_object      * faceto,
                   facet_object      * facetd,
                   has_facets_object * obj,
                   PyObject          * name,
                   PyObject          * value ) {

    PyObject * dict;
    PyObject * result;

    if ( value == NULL )
        return delete_readonly_error( obj, name );

    if ( facetd->default_value != Undefined )
        return set_readonly_error( obj, name );

	dict = obj->obj_dict;
    if ( dict == NULL )
        return setattr_python( faceto, facetd, obj, name, value );

    if ( !PyString_Check( name ) ) {
#ifdef Py_USING_UNICODE
        if ( PyUnicode_Check( name ) ) {
            name = PyUnicode_AsEncodedString( name, NULL, NULL );
            if ( name == NULL )
        	    return -1;
        } else
            return invalid_attribute_error();

#else
        return invalid_attribute_error();
#endif
    } else
        Py_INCREF( name );

    result = PyDict_GetItem( dict, name );
    Py_DECREF( name );
    if ( (result == NULL) || (result == Undefined) )
        return setattr_python( faceto, facetd, obj, name, value );

    return set_readonly_error( obj, name );
}

//-----------------------------------------------------------------------------
//  Generates exception on attempting to assign to a constant facet:
//-----------------------------------------------------------------------------

static int
setattr_constant ( facet_object      * faceto,
                   facet_object      * facetd,
                   has_facets_object * obj,
                   PyObject          * name,
                   PyObject          * value ) {

    if ( PyString_Check( name ) ) {
	    PyErr_Format( FacetError,
		      "Cannot modify the constant '%.400s' attribute of a '%.50s' object.",
		      PyString_AS_STRING( name ), obj->ob_type->tp_name );
        return -1;
    }
    return invalid_attribute_error();
}

//-----------------------------------------------------------------------------
//  Initializes a CFacet instance:
//-----------------------------------------------------------------------------

static facet_getattr getattr_handlers[] = {
    getattr_facet,     getattr_python,    getattr_event,  getattr_delegate,
    getattr_event,     getattr_disallow,  getattr_facet,  getattr_constant,
    getattr_generic,
//  The following entries are used by the __getstate__ method:
    getattr_property0, getattr_property1, getattr_property2,
    getattr_property3,
//  End of __getstate__ method entries
    NULL
};

static facet_setattr setattr_handlers[] = {
    setattr_facet,     setattr_python,    setattr_event,     setattr_delegate,
    setattr_event,     setattr_disallow,  setattr_readonly,  setattr_constant,
    setattr_generic,
//  The following entries are used by the __getstate__ method:
    setattr_property0, setattr_property1, setattr_property2, setattr_property3,
//  End of __setstate__ method entries
    NULL
};

static int
facet_init ( facet_object * facet, PyObject * args, PyObject * kwds ) {

    int kind;

	if ( !PyArg_ParseTuple( args, "i", &kind ) )
		return -1;

    if ( (kind >= 0) && (kind <= 8) ) {
        facet->getattr = getattr_handlers[ kind ];
        facet->setattr = setattr_handlers[ kind ];
        return 0;
    }

    return bad_facet_error();
}

//-----------------------------------------------------------------------------
//  Object clearing method:
//-----------------------------------------------------------------------------

static int
facet_clear ( facet_object * facet ) {

    Py_CLEAR( facet->default_value );
    Py_CLEAR( facet->py_validate );
    Py_CLEAR( facet->py_post_setattr );
    Py_CLEAR( facet->delegate_name );
    Py_CLEAR( facet->delegate_prefix );
    Py_CLEAR( facet->notifiers );
    Py_CLEAR( facet->handler );
    Py_CLEAR( facet->obj_dict );

    return 0;
}

//-----------------------------------------------------------------------------
//  Deallocates an unused 'CFacet' instance:
//-----------------------------------------------------------------------------

static void
facet_dealloc ( facet_object * facet ) {

    facet_clear( facet );
    facet->ob_type->tp_free( (PyObject *) facet );
}

//-----------------------------------------------------------------------------
//  Garbage collector traversal method:
//-----------------------------------------------------------------------------

static int
facet_traverse ( facet_object * facet, visitproc visit, void * arg ) {

    Py_VISIT( facet->default_value );
    Py_VISIT( facet->py_validate );
    Py_VISIT( facet->py_post_setattr );
    Py_VISIT( facet->delegate_name );
    Py_VISIT( facet->delegate_prefix );
    Py_VISIT( (PyObject *) facet->notifiers );
    Py_VISIT( facet->handler );
    Py_VISIT( facet->obj_dict );

	return 0;
}

//-----------------------------------------------------------------------------
//  Casts a 'CFacet' which attempts to validate the argument passed as being a
//  valid value for the facet:
//-----------------------------------------------------------------------------

static PyObject *
_facet_cast ( facet_object * facet, PyObject * args ) {

    PyObject * obj;
    PyObject * name;
    PyObject * value;
    PyObject * result;
    PyObject * info;

    switch ( PyTuple_GET_SIZE( args ) ) {
        case 1:
            obj   = name = Py_None;
            value = PyTuple_GET_ITEM( args, 0 );
            break;
        case 2:
            name  = Py_None;
            obj   = PyTuple_GET_ITEM( args, 0 );
            value = PyTuple_GET_ITEM( args, 1 );
            break;
        case 3:
            obj   = PyTuple_GET_ITEM( args, 0 );
            name  = PyTuple_GET_ITEM( args, 1 );
            value = PyTuple_GET_ITEM( args, 2 );
            break;
        default:
            PyErr_Format( PyExc_TypeError,
                "Facet cast takes 1, 2 or 3 arguments (%zd given).",
                PyTuple_GET_SIZE( args ) );
            return NULL;
    }
    if ( facet->validate == NULL ) {
        Py_INCREF( value );
        return value;
    }

	result = facet->validate( facet, (has_facets_object *) obj, name, value );
    if ( result == NULL ) {
        PyErr_Clear();
        info = PyObject_CallMethod( facet->handler, "info", NULL );
        if ( (info != NULL) && PyString_Check( info ) )
            PyErr_Format( PyExc_ValueError,
                "Invalid value for facet, the value should be %s.",
                PyString_AS_STRING( info ) );
        else
            PyErr_Format( PyExc_ValueError, "Invalid value for facet." );
        Py_XDECREF( info );
    }

    return result;
}

//-----------------------------------------------------------------------------
//  Handles the 'getattr' operation on a 'CHasFacets' instance:
//-----------------------------------------------------------------------------

static PyObject *
facet_getattro ( facet_object * obj, PyObject * name ) {

    PyObject * value = PyObject_GenericGetAttr( (PyObject *) obj, name );
    if ( value != NULL )
        return value;

    PyErr_Clear();

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'default_value' field of a CFacet instance:
//-----------------------------------------------------------------------------

static PyObject *
_facet_default_value ( facet_object * facet, PyObject * args ) {

    int        value_type;
    PyObject * value;

    if ( PyArg_ParseTuple( args, "" ) ) {
        if ( facet->default_value == NULL )
            return Py_BuildValue( "iO", 0, Py_None );

        return Py_BuildValue( "iO", facet->default_value_type,
                                    facet->default_value );
    }

    if ( !PyArg_ParseTuple( args, "iO", &value_type, &value ) )
        return NULL;

    PyErr_Clear();
    if ( (value_type < 0) || (value_type > 9) ) {
        PyErr_Format( PyExc_ValueError,
                "The default value type must be 0..9, but %d was specified.",
                value_type );

        return NULL;
    }

    Py_INCREF( value );
    Py_XDECREF( facet->default_value );
    facet->default_value_type = value_type;
    facet->default_value = value;

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Gets the default value of a CFacet instance for a specified object and facet
//  name:
//-----------------------------------------------------------------------------

static PyObject *
_facet_default_value_for ( facet_object * facet, PyObject * args ) {

    PyObject * object;
    PyObject * name;

    if ( !PyArg_ParseTuple( args, "OO", &object, &name ) )
        return NULL;

    if ( ((facet->flags & FACET_PROPERTY) != 0) ||
         has_value_for( (has_facets_object *) object, name ) )
        return default_value_for( facet, (has_facets_object *) object, name );

    return facet->getattr( facet, (has_facets_object *) object, name );
}

//-----------------------------------------------------------------------------
//  Calls a Python-based facet validator:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_python ( facet_object * facet, has_facets_object * obj,
                        PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return NULL;

    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    result = PyObject_Call( facet->py_validate, args, NULL );
    Py_DECREF( args );

    return result;
}

//-----------------------------------------------------------------------------
//  Calls the specified validator function:
//-----------------------------------------------------------------------------

static PyObject *
call_validator ( PyObject * validator, has_facets_object * obj,
                 PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    result = PyObject_Call( validator, args, NULL );
    Py_DECREF( args );

    return result;
}

//-----------------------------------------------------------------------------
//  Calls the specified type convertor:
//-----------------------------------------------------------------------------

static PyObject *
type_converter ( PyObject * type, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 1 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, value );
    Py_INCREF( value );
    result = PyObject_Call( type, args, NULL );
    Py_DECREF( args );

    return result;
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is of a specified type (or None):
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_type ( facet_object * facet, has_facets_object * obj,
                      PyObject * name, PyObject * value ) {

    PyObject * type_info = facet->py_validate;
    Py_ssize_t kind      = PyTuple_GET_SIZE( type_info );

    if ( ((kind == 3) && (value == Py_None)) ||
         PyObject_TypeCheck( value,
                 (PyTypeObject *) PyTuple_GET_ITEM( type_info, kind - 1 ) ) ) {

        Py_INCREF( value );
        return value;
    }

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is an instance of a specified type (or None):
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_instance ( facet_object * facet, has_facets_object * obj,
                          PyObject * name, PyObject * value ) {

    PyObject * type_info = facet->py_validate;
    Py_ssize_t kind      = PyTuple_GET_SIZE( type_info );

    if ( ((kind == 3) && (value == Py_None)) ||
        (PyObject_IsInstance( value,
             PyTuple_GET_ITEM( type_info, kind - 1 ) ) > 0) ) {
        Py_INCREF( value );
        return value;
    }

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is of a the same type as the object being assigned
//  to (or None):
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_self_type ( facet_object * facet, has_facets_object * obj,
                           PyObject * name, PyObject * value ) {

    if ( ((PyTuple_GET_SIZE( facet->py_validate ) == 2) &&
          (value == Py_None)) ||
          PyObject_TypeCheck( value, obj->ob_type ) ) {
        Py_INCREF( value );
        return value;
    }

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is an int within a specified range:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_int ( facet_object * facet, has_facets_object * obj,
                     PyObject * name, PyObject * value ) {

    register PyObject * low;
    register PyObject * high;
    long exclude_mask;
    long int_value;

    PyObject * type_info = facet->py_validate;

    if ( PyInt_Check( value ) ) {
        int_value    = PyInt_AS_LONG( value );
        low          = PyTuple_GET_ITEM( type_info, 1 );
        high         = PyTuple_GET_ITEM( type_info, 2 );
        exclude_mask = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) );
        if ( low != Py_None ) {
            if ( (exclude_mask & 1) != 0 ) {
                if ( int_value <= PyInt_AS_LONG( low ) )
                    goto error;
            } else {
                if ( int_value < PyInt_AS_LONG( low ) )
                    goto error;
            }
        }

        if ( high != Py_None ) {
            if ( (exclude_mask & 2) != 0 ) {
                if ( int_value >= PyInt_AS_LONG( high ) )
                    goto error;
            } else {
                if ( int_value > PyInt_AS_LONG( high ) )
                    goto error;
            }
        }

        Py_INCREF( value );
        return value;
    }
error:
    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is a float within a specified range:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_float ( facet_object * facet, has_facets_object * obj,
                       PyObject * name, PyObject * value ) {

    register PyObject * low;
    register PyObject * high;
    long exclude_mask;
    double float_value;

    PyObject * type_info = facet->py_validate;

    if ( !PyFloat_Check( value ) ) {
        if ( !PyInt_Check( value ) )
            goto error;
        float_value = (double) PyInt_AS_LONG( value );
        value       = PyFloat_FromDouble( float_value );
        if ( value == NULL )
            goto error;
        Py_INCREF( value );
    } else {
        float_value = PyFloat_AS_DOUBLE( value );
    }

    low          = PyTuple_GET_ITEM( type_info, 1 );
    high         = PyTuple_GET_ITEM( type_info, 2 );
    exclude_mask = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) );

    if ( low != Py_None ) {
        if ( (exclude_mask & 1) != 0 ) {
            if ( float_value <= PyFloat_AS_DOUBLE( low ) )
                goto error;
        } else {
            if ( float_value < PyFloat_AS_DOUBLE( low ) )
                goto error;
        }
    }

    if ( high != Py_None ) {
        if ( (exclude_mask & 2) != 0 ) {
            if ( float_value >= PyFloat_AS_DOUBLE( high ) )
                goto error;
        } else {
            if ( float_value > PyFloat_AS_DOUBLE( high ) )
                goto error;
        }
    }

    Py_INCREF( value );
    return value;
error:
    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is in a specified enumeration:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_enum ( facet_object * facet, has_facets_object * obj,
                      PyObject * name, PyObject * value ) {

    PyObject * type_info = facet->py_validate;
    if ( PySequence_Contains( PyTuple_GET_ITEM( type_info, 1 ), value ) > 0 ) {
        Py_INCREF( value );
        return value;
    }

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is in a specified map (i.e. dictionary):
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_map ( facet_object * facet, has_facets_object * obj,
                     PyObject * name, PyObject * value ) {

    PyObject * type_info = facet->py_validate;
    if ( PyDict_GetItem( PyTuple_GET_ITEM( type_info, 1 ), value ) != NULL ) {
        Py_INCREF( value );
        return value;
    }

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is in a specified prefix map (i.e. dictionary):
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_prefix_map ( facet_object * facet, has_facets_object * obj,
                            PyObject * name, PyObject * value ) {

    PyObject * type_info    = facet->py_validate;
    PyObject * mapped_value = PyDict_GetItem( PyTuple_GET_ITEM( type_info, 1 ),
                                              value );
    if ( mapped_value != NULL ) {
        Py_INCREF( mapped_value );
        return mapped_value;
    }

    return call_validator( PyTuple_GET_ITEM( facet->py_validate, 2 ),
                           obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is a tuple of a specified type and content:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_tuple_check ( PyObject * facets, has_facets_object * obj,
                             PyObject * name, PyObject * value ) {

    facet_object * ifacet;
    PyObject     * bitem, * aitem, * tuple;
    Py_ssize_t i, j, n;

    if ( PyTuple_Check( value ) ) {
        n = PyTuple_GET_SIZE( facets );
        if ( n == PyTuple_GET_SIZE( value ) ) {
            tuple = NULL;
            for ( i = 0; i < n; i++ ) {
                bitem  = PyTuple_GET_ITEM( value, i );
                ifacet = (facet_object *) PyTuple_GET_ITEM( facets, i );
                if ( ifacet->validate == NULL ) {
                    aitem = bitem;
                    Py_INCREF( aitem );
                } else
                    aitem = ifacet->validate( ifacet, obj, name, bitem );

                if ( aitem == NULL ) {
                    PyErr_Clear();
                    Py_XDECREF( tuple );
                    return NULL;
                }

                if ( tuple != NULL )
                    PyTuple_SET_ITEM( tuple, i, aitem );
                else if ( aitem != bitem ) {
                    tuple = PyTuple_New( n );
                    if ( tuple == NULL )
                        return NULL;
                    for ( j = 0; j < i; j++ ) {
                        bitem = PyTuple_GET_ITEM( value, j );
                        Py_INCREF( bitem );
                        PyTuple_SET_ITEM( tuple, j, bitem );
                    }
                    PyTuple_SET_ITEM( tuple, i, aitem );
                } else
                    Py_DECREF( aitem );
            }
            if ( tuple != NULL )
                return tuple;

            Py_INCREF( value );
            return value;
        }
    }

    return NULL;
}

static PyObject *
validate_facet_tuple ( facet_object * facet, has_facets_object * obj,
                       PyObject * name, PyObject * value ) {

    PyObject * result = validate_facet_tuple_check(
                            PyTuple_GET_ITEM( facet->py_validate, 1 ),
                            obj, name, value );
    if ( result != NULL )
        return result;

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is of a specified (possibly coercable) type:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_coerce_type ( facet_object * facet, has_facets_object * obj,
                             PyObject * name, PyObject * value ) {

    Py_ssize_t i, n;
    PyObject * type2;

    PyObject * type_info = facet->py_validate;
    PyObject * type      = PyTuple_GET_ITEM( type_info, 1 );
    if ( PyObject_TypeCheck( value, (PyTypeObject *) type ) ) {
        Py_INCREF( value );
        return value;
    }

    n = PyTuple_GET_SIZE( type_info );
    for ( i = 2; i < n; i++ ) {
        type2 = PyTuple_GET_ITEM( type_info, i );
        if ( type2 == Py_None )
            break;

        if ( PyObject_TypeCheck( value, (PyTypeObject *) type2 ) ) {
            Py_INCREF( value );
            return value;
        }
    }

    for ( i++; i < n; i++ ) {
        type2 = PyTuple_GET_ITEM( type_info, i );
        if ( PyObject_TypeCheck( value, (PyTypeObject *) type2 ) )
            return type_converter( type, value );
    }

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value is of a specified (possibly castable) type:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_cast_type ( facet_object * facet, has_facets_object * obj,
                           PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * type_info = facet->py_validate;
    PyObject * type      = PyTuple_GET_ITEM( type_info, 1 );
    if ( PyObject_TypeCheck( value, (PyTypeObject *) type ) ) {
        Py_INCREF( value );
        return value;
    }

    if ( (result = type_converter( type, value )) != NULL )
        return result;

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value satisifies a specified function validator:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_function ( facet_object * facet, has_facets_object * obj,
                          PyObject * name, PyObject * value ) {

    PyObject * result;

    result = call_validator( PyTuple_GET_ITEM( facet->py_validate, 1 ),
                             obj, name, value );
    if ( result != NULL )
        return result;

    PyErr_Clear();

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Attempts to 'adapt' an object to a specified interface:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_adapt ( facet_object * facet, has_facets_object * obj,
                       PyObject * name, PyObject * value ) {

    PyObject * result;
    PyObject * args;
    PyObject * type;
    PyObject * type_info = facet->py_validate;
    long mode, rc;

    if ( value == Py_None ) {
        if ( PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) ) ) {
            Py_INCREF( value );
            return value;
        }
        return raise_facet_error( facet, obj, name, value );
    }

    type = PyTuple_GET_ITEM( type_info, 1 );
    mode = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 2 ) );

    if ( mode == 2 ) {
        args = PyTuple_New( 3 );
        if ( args == NULL )
            return NULL;

        PyTuple_SET_ITEM( args, 2, Py_None );
        Py_INCREF( Py_None );
    } else {
        args = PyTuple_New( 2 );
        if ( args == NULL )
            return NULL;
    }

    PyTuple_SET_ITEM( args, 0, value );
    PyTuple_SET_ITEM( args, 1, type );
    Py_INCREF( value );
    Py_INCREF( type );
    result = PyObject_Call( adapt, args, NULL );
    if ( result != NULL ) {
        if ( result != Py_None ) {
            if ( (mode > 0) || (result == value) ) {
                Py_DECREF( args );
                return result;
            }
            Py_DECREF( result );
            goto check_implements;
        }

        Py_DECREF( result );
        result = PyObject_Call( validate_implements, args, NULL );
        rc     = PyInt_AS_LONG( result );
        Py_DECREF( args );
        Py_DECREF( result );
        if ( rc ) {
            Py_INCREF( value );
            return value;
        }

        result = default_value_for( facet, obj, name );
        if ( result != NULL )
            return result;

        PyErr_Clear();
        return raise_facet_error( facet, obj, name, value );
    }
    PyErr_Clear();
check_implements:
    result = PyObject_Call( validate_implements, args, NULL );
    rc     = PyInt_AS_LONG( result );
    Py_DECREF( args );
    Py_DECREF( result );
    if ( rc ) {
        Py_INCREF( value );
        return value;
    }

    return raise_facet_error( facet, obj, name, value );
}

//-----------------------------------------------------------------------------
//  Verifies a Python value satisifies a complex facet definition:
//-----------------------------------------------------------------------------

static PyObject *
validate_facet_complex ( facet_object * facet, has_facets_object * obj,
                         PyObject * name, PyObject * value ) {

    Py_ssize_t i, j, k, kind;
    long   int_value, exclude_mask, mode, rc;
    double float_value;
    PyObject * low, * high, * result, * type_info, * type, * type2, * args;

    PyObject * list_type_info = PyTuple_GET_ITEM( facet->py_validate, 1 );
    Py_ssize_t n = PyTuple_GET_SIZE( list_type_info );
    for ( i = 0; i < n; i++ ) {

        type_info = PyTuple_GET_ITEM( list_type_info, i );

        switch ( PyInt_AsLong( PyTuple_GET_ITEM( type_info, 0 ) ) ) {

            case 0:  // Type check:
                kind = PyTuple_GET_SIZE( type_info );
                if ( ((kind == 3) && (value == Py_None)) ||
                     PyObject_TypeCheck( value, (PyTypeObject *)
                                    PyTuple_GET_ITEM( type_info, kind - 1 ) ) )
                    goto done;
                break;

            case 1:  // Instance check:
                kind = PyTuple_GET_SIZE( type_info );
                if ( ((kind == 3) && (value == Py_None)) ||
                    (PyObject_IsInstance( value,
                         PyTuple_GET_ITEM( type_info, kind - 1 ) ) > 0) )
                    goto done;
                break;

            case 2:  // Self type check:
                if ( ((PyTuple_GET_SIZE( type_info ) == 2) &&
                      (value == Py_None)) ||
                      PyObject_TypeCheck( value, obj->ob_type ) )
                    goto done;
                break;

            case 3:  // Integer range check:
                if ( PyInt_Check( value ) ) {
                    int_value    = PyInt_AS_LONG( value );
                    low          = PyTuple_GET_ITEM( type_info, 1 );
                    high         = PyTuple_GET_ITEM( type_info, 2 );
                    exclude_mask = PyInt_AS_LONG(
                                       PyTuple_GET_ITEM( type_info, 3 ) );
                    if ( low != Py_None ) {
                        if ( (exclude_mask & 1) != 0 ) {
                            if ( int_value <= PyInt_AS_LONG( low  ) )
                                break;
                        } else {
                            if ( int_value < PyInt_AS_LONG( low  ) )
                                break;
                        }
                    }
                    if ( high != Py_None ) {
                        if ( (exclude_mask & 2) != 0 ) {
                            if ( int_value >= PyInt_AS_LONG( high ) )
                                break;
                        } else {
                            if ( int_value > PyInt_AS_LONG( high ) )
                                break;
                        }
                    }
                    goto done;
                }
                break;

            case 4:  // Floating point range check:
                if ( !PyFloat_Check( value ) ) {
                    if ( !PyInt_Check( value ) )
                        break;

                    float_value = (double) PyInt_AS_LONG( value );
                    value       = PyFloat_FromDouble( float_value );
                    if ( value == NULL ) {
                        PyErr_Clear();
                        break;
                    }
                } else {
                    float_value = PyFloat_AS_DOUBLE( value );
                    Py_INCREF( value );
                }
                low          = PyTuple_GET_ITEM( type_info, 1 );
                high         = PyTuple_GET_ITEM( type_info, 2 );
                exclude_mask = PyInt_AS_LONG(
                                   PyTuple_GET_ITEM( type_info, 3 ) );
                if ( low != Py_None ) {
                    if ( (exclude_mask & 1) != 0 ) {
                        if ( float_value <= PyFloat_AS_DOUBLE( low ) )
                            break;
                    } else {
                        if ( float_value < PyFloat_AS_DOUBLE( low ) )
                            break;
                    }
                }
                if ( high != Py_None ) {
                    if ( (exclude_mask & 2) != 0 ) {
                        if ( float_value >= PyFloat_AS_DOUBLE( high ) )
                            break;
                    } else {
                        if ( float_value > PyFloat_AS_DOUBLE( high ) )
                            break;
                    }
                }
                goto done2;

            case 5:  // Enumerated item check:
                if ( PySequence_Contains( PyTuple_GET_ITEM( type_info, 1 ),
                                          value ) > 0 )
                    goto done;

                break;
            case 6:  // Mapped item check:
                if ( PyDict_GetItem( PyTuple_GET_ITEM( type_info, 1 ),
                                     value ) != NULL )
                    goto done;
                PyErr_Clear();
                break;

            case 8:  // Perform 'slow' validate check:
                return PyObject_CallMethod( PyTuple_GET_ITEM( type_info, 1 ),
                                  "slow_validate", "(OOO)", obj, name, value );

            case 9:  // Tuple item check:
                result = validate_facet_tuple_check(
                             PyTuple_GET_ITEM( type_info, 1 ),
                             obj, name, value );
                if ( result != NULL )
                    return result;

                PyErr_Clear();
                break;

            case 10:  // Prefix map item check:
                result = PyDict_GetItem( PyTuple_GET_ITEM( type_info, 1 ),
                                         value );
                if ( result != NULL ) {
                    Py_INCREF( result );
                    return result;
                }
                result = call_validator( PyTuple_GET_ITEM( type_info, 2 ),
                                         obj, name, value );
                if ( result != NULL )
                    return result;
                PyErr_Clear();
                break;

            case 11:  // Coercable type check:
                type = PyTuple_GET_ITEM( type_info, 1 );
                if ( PyObject_TypeCheck( value, (PyTypeObject *) type ) )
                    goto done;

                k = PyTuple_GET_SIZE( type_info );
                for ( j = 2; j < k; j++ ) {
                    type2 = PyTuple_GET_ITEM( type_info, j );
                    if ( type2 == Py_None )
                        break;
                    if ( PyObject_TypeCheck( value, (PyTypeObject *) type2 ) )
                        goto done;
                }

                for ( j++; j < k; j++ ) {
                    type2 = PyTuple_GET_ITEM( type_info, j );
                    if ( PyObject_TypeCheck( value, (PyTypeObject *) type2 ) )
                        return type_converter( type, value );
                }
                break;

            case 12:  // Castable type check:
                type = PyTuple_GET_ITEM( type_info, 1 );
                if ( PyObject_TypeCheck( value, (PyTypeObject *) type ) )
                    goto done;

                if ( (result = type_converter( type, value )) != NULL )
                    return result;

                PyErr_Clear();
                break;

            case 13:  // Function validator check:
                result = call_validator( PyTuple_GET_ITEM( type_info, 1 ),
                                         obj, name, value );
                if ( result != NULL )
                    return result;

                PyErr_Clear();
                break;

            // case 14: Python-based validator check:

            // case 15..18: Property 'setattr' validate checks:

            case 19:  // PyProtocols 'adapt' check:
                if ( value == Py_None ) {
                    if ( PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) ) )
                        goto done;
                    break;
                }
                type = PyTuple_GET_ITEM( type_info, 1 );
                mode = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 2 ) );
                if ( mode == 2 ) {
                    args = PyTuple_New( 3 );
                    if ( args == NULL )
                        return NULL;

                    PyTuple_SET_ITEM( args, 2, Py_None );
                    Py_INCREF( Py_None );
                } else {
                    args = PyTuple_New( 2 );
                    if ( args == NULL )
                        return NULL;
                }

                PyTuple_SET_ITEM( args, 0, value );
                PyTuple_SET_ITEM( args, 1, type );
                Py_INCREF( value );
                Py_INCREF( type );
                result = PyObject_Call( adapt, args, NULL );
                if ( result != NULL ) {
                    if ( result != Py_None ) {
                        if ( (mode == 0) && (result != value) ) {
                            Py_DECREF( result );
                            goto check_implements;
                        }
                        Py_DECREF( args );
                        return result;
                    }

                    Py_DECREF( result );
                    result = PyObject_Call( validate_implements, args, NULL );
                    rc     = PyInt_AS_LONG( result );
                    Py_DECREF( args );
                    Py_DECREF( result );
                    if ( rc )
                        goto done;
                    result = default_value_for( facet, obj, name );
                    if ( result != NULL )
                        return result;

                    PyErr_Clear();
                    break;
                }
                PyErr_Clear();
check_implements:
                result = PyObject_Call( validate_implements, args, NULL );
                rc     = PyInt_AS_LONG( result );
                Py_DECREF( args );
                Py_DECREF( result );
                if ( rc )
                    goto done;
                break;

            default:  // Should never happen...indicates an internal error:
                goto error;
        }
    }
error:
    return raise_facet_error( facet, obj, name, value );
done:
    Py_INCREF( value );
done2:
    return value;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'validate' field of a CFacet instance:
//-----------------------------------------------------------------------------

static facet_validate validate_handlers[] = {
    validate_facet_type,        validate_facet_instance,
    validate_facet_self_type,   validate_facet_int,
    validate_facet_float,       validate_facet_enum,
    validate_facet_map,         validate_facet_complex,
    NULL,                       validate_facet_tuple,
    validate_facet_prefix_map,  validate_facet_coerce_type,
    validate_facet_cast_type,   validate_facet_function,
    validate_facet_python,
//  The following entries are used by the __getstate__ method...
    setattr_validate0,           setattr_validate1,
    setattr_validate2,           setattr_validate3,
//  ...End of __getstate__ method entries
    validate_facet_adapt
};

static PyObject *
_facet_set_validate ( facet_object * facet, PyObject * args ) {

    PyObject * validate;
    PyObject * v1, * v2, * v3;
    Py_ssize_t n;
    int        kind;

    if ( !PyArg_ParseTuple( args, "O", &validate ) )
        return NULL;

    if ( PyCallable_Check( validate ) ) {
        kind = 14;
        goto done;
    }

    if ( PyTuple_CheckExact( validate ) ) {
        n = PyTuple_GET_SIZE( validate );
        if ( n > 0 ) {

            kind = PyInt_AsLong( PyTuple_GET_ITEM( validate, 0 ) );

            switch ( kind ) {
                case 0:  // Type check:
                    if ( (n <= 3) &&
                         PyType_Check( PyTuple_GET_ITEM( validate, n - 1 ) ) &&
                         ((n == 2) ||
                          (PyTuple_GET_ITEM( validate, 1 ) == Py_None)) )
                        goto done;
                    break;

                case 1:  // Instance check:
                    if ( (n <= 3) &&
                         ((n == 2) ||
                          (PyTuple_GET_ITEM( validate, 1 ) == Py_None)) )
                        goto done;
                    break;

                case 2:  // Self type check:
                    if ( (n == 1) ||
                         ((n == 2) &&
                          (PyTuple_GET_ITEM( validate, 1 ) == Py_None)) )
                        goto done;
                    break;

                case 3:  // Integer range check:
                    if ( n == 4 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        v2 = PyTuple_GET_ITEM( validate, 2 );
                        v3 = PyTuple_GET_ITEM( validate, 3 );
                        if ( ((v1 == Py_None) || PyInt_Check( v1 )) &&
                             ((v2 == Py_None) || PyInt_Check( v2 )) &&
                             PyInt_Check( v3 ) )
                            goto done;
                    }
                    break;

                case 4:  // Floating point range check:
                    if ( n == 4 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        v2 = PyTuple_GET_ITEM( validate, 2 );
                        v3 = PyTuple_GET_ITEM( validate, 3 );
                        if ( ((v1 == Py_None) || PyFloat_Check( v1 )) &&
                             ((v2 == Py_None) || PyFloat_Check( v2 )) &&
                             PyInt_Check( v3 ) )
                            goto done;
                    }
                    break;

                case 5:  // Enumerated item check:
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyTuple_CheckExact( v1 ) )
                            goto done;
                    }
                    break;

                case 6:  // Mapped item check:
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyDict_Check( v1 ) )
                            goto done;
                    }
                    break;

                case 7:  // FacetComplex item check:
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyTuple_CheckExact( v1 ) )
                            goto done;
                    }
                    break;

                // case 8: 'Slow' validate check:
                case 9:  // TupleOf item check:
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyTuple_CheckExact( v1 ) )
                            goto done;
                    }
                    break;

                case 10:  // Prefix map item check:
                    if ( n == 3 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyDict_Check( v1 ) )
                            goto done;
                    }
                    break;

                case 11:  // Coercable type check:
                    if ( n >= 2 )
                       goto done;
                    break;

                case 12:  // Castable type check:
                    if ( n == 2 )
                       goto done;
                    break;

                case 13:  // Function validator check:
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyCallable_Check( v1 ) )
                            goto done;
                    }
                    break;

                // case 14: Python-based validator check:
                // case 15..18: Property 'setattr' validate checks:
                case 19:  // PyProtocols 'adapt' check:
                    // Note: We don't check the 'class' argument (item[1])
                    // because some old-style code creates classes that are not
                    // strictly classes or types (e.g. VTK), and yet they work
                    // correctly with the rest of the Instance code
                    if ( (n == 4) &&
                         PyInt_Check(  PyTuple_GET_ITEM( validate, 2 ) )  &&
                         PyBool_Check( PyTuple_GET_ITEM( validate, 3 ) ) ) {
                        goto done;
                    }
                    break;
            }
		}
    }

    PyErr_SetString( PyExc_ValueError,
                     "The argument must be a tuple or callable." );

    return NULL;

done:
    facet->validate = validate_handlers[ kind ];
    Py_INCREF( validate );
    Py_XDECREF( facet->py_validate );
    facet->py_validate = validate;

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Gets the value of the 'validate' field of a CFacet instance:
//-----------------------------------------------------------------------------

static PyObject *
_facet_get_validate ( facet_object * facet ) {

    if ( facet->validate != NULL ) {
        Py_INCREF( facet->py_validate );
        return facet->py_validate;
    }

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Validates that a particular value can be assigned to an object facet:
//-----------------------------------------------------------------------------

static PyObject *
_facet_validate ( facet_object * facet, PyObject * args ) {

    PyObject * object, * name, * value;

    if ( !PyArg_ParseTuple( args, "OOO", &object, &name, &value ) )
        return NULL;

    if ( facet->validate == NULL ) {
        Py_INCREF( value );
        return value;
    }

    return facet->validate( facet, (has_facets_object *)object, name, value );
}

//-----------------------------------------------------------------------------
//  Calls a Python-based facet post_setattr handler:
//-----------------------------------------------------------------------------

static int
post_setattr_facet_python ( facet_object * facet, has_facets_object * obj,
                            PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return -1;

    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    result = PyObject_Call( facet->py_post_setattr, args, NULL );
    Py_DECREF( args );

    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

//-----------------------------------------------------------------------------
//  Returns the various forms of delegate names:
//-----------------------------------------------------------------------------

static PyObject *
delegate_attr_name_name ( facet_object      * facet,
                          has_facets_object * obj,
                          PyObject          * name ) {

    Py_INCREF( name );
    return name;
}

static PyObject *
delegate_attr_name_prefix ( facet_object      * facet,
                            has_facets_object * obj,
                            PyObject          * name ) {

    Py_INCREF( facet->delegate_prefix );
    return facet->delegate_prefix;
}

static PyObject *
delegate_attr_name_prefix_name ( facet_object      * facet,
                                 has_facets_object * obj,
                                 PyObject          * name ) {

    char * p;

    Py_ssize_t prefix_len = PyString_GET_SIZE( facet->delegate_prefix );
    Py_ssize_t name_len   = PyString_GET_SIZE( name );
    Py_ssize_t total_len  = prefix_len + name_len;
    PyObject * result     = PyString_FromStringAndSize( NULL, total_len );

    if ( result == NULL ) {
        Py_INCREF( Py_None );
        return Py_None;
    }

    p = PyString_AS_STRING( result );
    memcpy( p, PyString_AS_STRING( facet->delegate_prefix ), prefix_len );
    memcpy( p + prefix_len, PyString_AS_STRING( name ), name_len );

    return result;
}

static PyObject *
delegate_attr_name_class_name ( facet_object      * facet,
                                has_facets_object * obj,
                                PyObject          * name ) {

	PyObject * prefix, * result;
    char     * p;
    Py_ssize_t prefix_len, name_len, total_len;

	prefix = PyObject_GetAttr( (PyObject *) obj->ob_type, class_prefix );
    // fixme: Should verify that prefix is a string...
	if ( prefix == NULL ) {
		PyErr_Clear();

        Py_INCREF( name );

		return name;
	}

    prefix_len = PyString_GET_SIZE( prefix );
    name_len   = PyString_GET_SIZE( name );
    total_len  = prefix_len + name_len;
    result     = PyString_FromStringAndSize( NULL, total_len );
    if ( result == NULL ) {
        Py_INCREF( Py_None );

        return Py_None;
    }

    p = PyString_AS_STRING( result );
    memcpy( p, PyString_AS_STRING( prefix ), prefix_len );
    memcpy( p + prefix_len, PyString_AS_STRING( name ), name_len );
    Py_DECREF( prefix );

    return result;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'post_setattr' field of a CFacet instance:
//-----------------------------------------------------------------------------

static delegate_attr_name_func delegate_attr_name_handlers[] = {
    delegate_attr_name_name,         delegate_attr_name_prefix,
    delegate_attr_name_prefix_name,  delegate_attr_name_class_name,
    NULL
};

static PyObject *
_facet_delegate ( facet_object * facet, PyObject * args ) {

    PyObject * delegate_name;
    PyObject * delegate_prefix;
    int prefix_type;
    int modify_delegate;

    if ( !PyArg_ParseTuple( args, "O!O!ii",
                            &PyString_Type, &delegate_name,
                            &PyString_Type, &delegate_prefix,
                            &prefix_type,   &modify_delegate ) )
        return NULL;

    if ( modify_delegate ) {
        facet->flags |= FACET_MODIFY_DELEGATE;
    } else {
        facet->flags &= (~FACET_MODIFY_DELEGATE);
    }

    facet->delegate_name   = delegate_name;
    facet->delegate_prefix = delegate_prefix;
    Py_INCREF( delegate_name );
    Py_INCREF( delegate_prefix );
    if ( (prefix_type < 0) || (prefix_type > 3) )
        prefix_type = 0;

    facet->delegate_attr_name = delegate_attr_name_handlers[ prefix_type ];

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'comparison' mode of a CFacet instance:
//-----------------------------------------------------------------------------

static PyObject *
_facet_rich_comparison ( facet_object * facet, PyObject * args ) {

    int compare_type;

    if ( !PyArg_ParseTuple( args, "i", &compare_type ) )
        return NULL;

    facet->flags &= (~(FACET_NO_VALUE_TEST | FACET_OBJECT_IDENTITY));
    if ( compare_type == 0 )
        facet->flags |= FACET_OBJECT_IDENTITY;

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the appropriate value comparison mode flags of a CFacet instance:
//-----------------------------------------------------------------------------

static PyObject *
_facet_comparison_mode ( facet_object * facet, PyObject * args ) {

    int comparison_mode;

    if ( !PyArg_ParseTuple( args, "i", &comparison_mode ) )
        return NULL;

    facet->flags &= (~(FACET_NO_VALUE_TEST | FACET_OBJECT_IDENTITY));
    switch ( comparison_mode ) {
        case 0:  facet->flags |= FACET_NO_VALUE_TEST;
                 break;
        case 1:  facet->flags |= FACET_OBJECT_IDENTITY;
        default: break;
    }

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'value allowed' mode of a CFacet instance:
//-----------------------------------------------------------------------------

static PyObject *
_facet_value_allowed ( facet_object * facet, PyObject * args ) {

    int value_allowed;

    if ( !PyArg_ParseTuple( args, "i", &value_allowed ) )
        return NULL;

    if ( value_allowed ) {
        facet->flags |= FACET_VALUE_ALLOWED;
    } else {
        facet->flags &= (~FACET_VALUE_ALLOWED);
    }

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'value facet' mode of a CFacet instance:
//-----------------------------------------------------------------------------

static PyObject *
_facet_value_property ( facet_object * facet, PyObject * args ) {

    int value_facet;

    if ( !PyArg_ParseTuple( args, "i", &value_facet ) )
        return NULL;

    if ( value_facet ) {
        facet->flags |= FACET_VALUE_PROPERTY;
    } else {
        facet->flags &= (~FACET_VALUE_PROPERTY);
    }

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'setattr_original_value' flag of a CFacet instance:
//-----------------------------------------------------------------------------

static PyObject *
_facet_setattr_original_value ( facet_object * facet, PyObject * args ) {

    int original_value;

    if ( !PyArg_ParseTuple( args, "i", &original_value ) )
        return NULL;

    if ( original_value != 0 ) {
        facet->flags |= FACET_SETATTR_ORIGINAL_VALUE;
    } else {
        facet->flags &= (~FACET_SETATTR_ORIGINAL_VALUE);
    }

    Py_INCREF( facet );
    return (PyObject *) facet;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'post_setattr_original_value' flag of a CFacet
//  instance (used in the processing of 'post_settattr' calls):
//-----------------------------------------------------------------------------

static PyObject *
_facet_post_setattr_original_value ( facet_object * facet, PyObject * args ) {

    int original_value;

    if ( !PyArg_ParseTuple( args, "i", &original_value ) )
        return NULL;

    if ( original_value != 0 ) {
        facet->flags |= FACET_POST_SETATTR_ORIGINAL_VALUE;
    } else {
        facet->flags &= (~FACET_POST_SETATTR_ORIGINAL_VALUE);
    }

    Py_INCREF( facet );
    return (PyObject *) facet;
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'is_mapped' flag of a CFacet instance (used in the
//  processing of the default value of a facet with a 'post_settattr' handler):
//-----------------------------------------------------------------------------

static PyObject *
_facet_is_mapped ( facet_object * facet, PyObject * args ) {

    int is_mapped;

    if ( !PyArg_ParseTuple( args, "i", &is_mapped ) )
        return NULL;

    if ( is_mapped != 0 ) {
        facet->flags |= FACET_IS_MAPPED;
    } else {
        facet->flags &= (~FACET_IS_MAPPED);
    }

    Py_INCREF( facet );
    return (PyObject *) facet;
}

//-----------------------------------------------------------------------------
//  Sets the 'property' value fields of a CFacet instance:
//-----------------------------------------------------------------------------

static facet_setattr setattr_property_handlers[] = {
    setattr_property0, setattr_property1, setattr_property2, setattr_property3,
//  The following entries are used by the __getstate__ method__:
    (facet_setattr) post_setattr_facet_python, NULL
};

static PyObject *
_facet_property ( facet_object * facet, PyObject * args ) {

    PyObject * get, * set, * validate, * result, * temp;
    int get_n, set_n, validate_n;

    if ( PyTuple_GET_SIZE( args ) == 0 ) {
        if ( facet->flags & FACET_PROPERTY ) {
            result = PyTuple_New( 3 );
            if ( result != NULL ) {
                PyTuple_SET_ITEM( result, 0, temp = facet->delegate_name );
                Py_INCREF( temp );
                PyTuple_SET_ITEM( result, 1, temp = facet->delegate_prefix );
                Py_INCREF( temp );
                PyTuple_SET_ITEM( result, 2, temp = facet->py_validate );
                Py_INCREF( temp );
                Py_INCREF( result );
                return result;
            }
            return NULL;
        } else {
            Py_INCREF( Py_None );
            return Py_None;
        }
    }

    if ( !PyArg_ParseTuple( args, "OiOiOi", &get, &get_n, &set, &set_n,
                                            &validate, &validate_n ) )
        return NULL;
    if ( !PyCallable_Check( get ) || !PyCallable_Check( set )     ||
         ((validate != Py_None) && !PyCallable_Check( validate )) ||
         (get_n < 0)      || (get_n > 3) ||
         (set_n < 0)      || (set_n > 3) ||
         (validate_n < 0) || (validate_n > 3) ) {
        PyErr_SetString( PyExc_ValueError, "Invalid arguments." );
        return NULL;
    }

    facet->flags  |= FACET_PROPERTY;
    facet->getattr = getattr_property_handlers[ get_n ];
	if ( validate != Py_None ) {
        facet->setattr      = setattr_validate_property;
        facet->post_setattr = (facet_post_setattr) setattr_property_handlers[
                                                                      set_n ];
        facet->validate     = setattr_validate_handlers[ validate_n ];
	} else
        facet->setattr = setattr_property_handlers[ set_n ];

    facet->delegate_name   = get;
    facet->delegate_prefix = set;
    facet->py_validate     = validate;
    Py_INCREF( get );
    Py_INCREF( set );
    Py_INCREF( validate );
    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Clones one facet into another:
//-----------------------------------------------------------------------------

static void
facet_clone ( facet_object * facet, facet_object * source ) {

    facet->flags              = source->flags;
    facet->getattr            = source->getattr;
    facet->setattr            = source->setattr;
    facet->post_setattr       = source->post_setattr;
    facet->py_post_setattr    = source->py_post_setattr;
    facet->validate           = source->validate;
    facet->py_validate        = source->py_validate;
    facet->default_value_type = source->default_value_type;
    facet->default_value      = source->default_value;
    facet->delegate_name      = source->delegate_name;
    facet->delegate_prefix    = source->delegate_prefix;
    facet->delegate_attr_name = source->delegate_attr_name;
    facet->handler            = source->handler;
    Py_XINCREF( facet->py_post_setattr );
    Py_XINCREF( facet->py_validate );
    Py_XINCREF( facet->delegate_name );
    Py_XINCREF( facet->default_value );
    Py_XINCREF( facet->delegate_prefix );
    Py_XINCREF( facet->handler );
}

static PyObject *
_facet_clone ( facet_object * facet, PyObject * args ) {

    facet_object * source;

	if ( !PyArg_ParseTuple( args, "O!", cfacet_type, &source ) )
        return NULL;

    facet_clone( facet, source );

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Returns (and optionally creates) the facet 'notifiers' list:
//-----------------------------------------------------------------------------

static PyObject *
_facet_notifiers ( facet_object * facet, PyObject * args ) {

    PyObject * result;
    PyObject * list;
    int force_create;

	if ( !PyArg_ParseTuple( args, "i", &force_create ) )
        return NULL;

    result = (PyObject *) facet->notifiers;
    if ( result == NULL ) {
        result = Py_None;
        if ( force_create && ((list = PyList_New( 0 )) != NULL) )
            facet->notifiers = (PyListObject *) (result = list);
    }

    Py_INCREF( result );
    return result;
}

//-----------------------------------------------------------------------------
//  Converts a function to an index into a function table:
//-----------------------------------------------------------------------------

static int
func_index ( void * function, void ** function_table ) {

    int i;

    for ( i = 0; function != function_table[i]; i++ );
    return i;
}

//-----------------------------------------------------------------------------
//  Gets the pickleable state of the facet:
//-----------------------------------------------------------------------------

static PyObject *
_facet_getstate ( facet_object * facet, PyObject * args ) {

    PyObject * result;

    if ( !PyArg_ParseTuple( args, "" ) )
        return NULL;

    result = PyTuple_New( 15 );
    if ( result == NULL )
        return NULL;

    PyTuple_SET_ITEM( result,  0, PyInt_FromLong( func_index(
                  (void *) facet->getattr, (void **) getattr_handlers ) ) );
    PyTuple_SET_ITEM( result,  1, PyInt_FromLong( func_index(
                  (void *) facet->setattr, (void **) setattr_handlers ) ) );
    PyTuple_SET_ITEM( result,  2, PyInt_FromLong( func_index(
                  (void *) facet->post_setattr,
                  (void **) setattr_property_handlers ) ) );
    PyTuple_SET_ITEM( result,  3, get_callable_value( facet->py_post_setattr ));
    PyTuple_SET_ITEM( result,  4, PyInt_FromLong( func_index(
                  (void *) facet->validate, (void **) validate_handlers ) ) );
    PyTuple_SET_ITEM( result,  5, get_callable_value( facet->py_validate ) );
    PyTuple_SET_ITEM( result,  6, PyInt_FromLong( facet->default_value_type ) );
    PyTuple_SET_ITEM( result,  7, get_value( facet->default_value ) );
    PyTuple_SET_ITEM( result,  8, PyInt_FromLong( facet->flags ) );
    PyTuple_SET_ITEM( result,  9, get_value( facet->delegate_name ) );
    PyTuple_SET_ITEM( result, 10, get_value( facet->delegate_prefix ) );
    PyTuple_SET_ITEM( result, 11, PyInt_FromLong( func_index(
                  (void *) facet->delegate_attr_name,
                  (void **) delegate_attr_name_handlers ) ) );
    PyTuple_SET_ITEM( result, 12, get_value( NULL ) ); // facet->notifiers
    PyTuple_SET_ITEM( result, 13, get_value( facet->handler ) );
    PyTuple_SET_ITEM( result, 14, get_value( facet->obj_dict ) );

    return result;
}

//-----------------------------------------------------------------------------
//  Restores the pickled state of the facet:
//-----------------------------------------------------------------------------

static PyObject *
_facet_setstate ( facet_object * facet, PyObject * args ) {

    PyObject * ignore, * temp, *temp2;
    int getattr_index, setattr_index, post_setattr_index, validate_index,
        delegate_attr_name_index;

    if ( !PyArg_ParseTuple( args, "(iiiOiOiOiOOiOOO)",
                &getattr_index,             &setattr_index,
                &post_setattr_index,        &facet->py_post_setattr,
                &validate_index,            &facet->py_validate,
                &facet->default_value_type, &facet->default_value,
                &facet->flags,              &facet->delegate_name,
                &facet->delegate_prefix,    &delegate_attr_name_index,
                &ignore,                    &facet->handler,
                &facet->obj_dict ) )
        return NULL;

    facet->getattr      = getattr_handlers[ getattr_index ];
    facet->setattr      = setattr_handlers[ setattr_index ];
    facet->post_setattr = (facet_post_setattr) setattr_property_handlers[
                              post_setattr_index ];
    facet->validate     = validate_handlers[ validate_index ];
    facet->delegate_attr_name = delegate_attr_name_handlers[
                                    delegate_attr_name_index ];

    // Convert any references to callable methods on the handler back into
    // bound methods:
    temp = facet->py_validate;
    if ( PyInt_Check( temp ) )
        facet->py_validate = PyObject_GetAttrString( facet->handler,
                                                     "validate" );
    else if ( PyTuple_Check( temp ) &&
              (PyInt_AsLong( PyTuple_GET_ITEM( temp, 0 ) ) == 10) ) {
        temp2 = PyObject_GetAttrString( facet->handler, "validate" );
        Py_INCREF( temp2 );
        Py_DECREF( PyTuple_GET_ITEM( temp, 2 ) );
        PyTuple_SET_ITEM( temp, 2, temp2 );
    }

    if ( PyInt_Check( facet->py_post_setattr ) )
        facet->py_post_setattr = PyObject_GetAttrString( facet->handler,
                                                         "post_setattr" );

    Py_INCREF( facet->py_post_setattr );
    Py_INCREF( facet->py_validate );
    Py_INCREF( facet->default_value );
    Py_INCREF( facet->delegate_name );
    Py_INCREF( facet->delegate_prefix );
    Py_INCREF( facet->handler );
    Py_INCREF( facet->obj_dict );

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Returns the current facet dictionary:
//-----------------------------------------------------------------------------

static PyObject *
get_facet_dict ( facet_object * facet, void * closure ) {

    PyObject * obj_dict = facet->obj_dict;
    if ( obj_dict == NULL ) {
        facet->obj_dict = obj_dict = PyDict_New();
        if ( obj_dict == NULL )
            return NULL;
    }
    Py_INCREF( obj_dict );
    return obj_dict;
}

//-----------------------------------------------------------------------------
//  Sets the current facet dictionary:
//-----------------------------------------------------------------------------

static int
set_facet_dict ( facet_object * facet, PyObject * value, void * closure ) {

    if ( !PyDict_Check( value ) )
        return dictionary_error();
    return set_value( &facet->obj_dict, value );
}

//-----------------------------------------------------------------------------
//  Returns the current facet handler (if any):
//-----------------------------------------------------------------------------

static PyObject *
get_facet_handler ( facet_object * facet, void * closure ) {

    return get_value( facet->handler );
}

//-----------------------------------------------------------------------------
//  Sets the current facet dictionary:
//-----------------------------------------------------------------------------

static int
set_facet_handler ( facet_object * facet, PyObject * value, void * closure ) {

    return set_value( &facet->handler, value );
}

//-----------------------------------------------------------------------------
//  Returns the current post_setattr (if any):
//-----------------------------------------------------------------------------

static PyObject *
get_facet_post_setattr ( facet_object * facet, void * closure ) {

    return get_value( facet->py_post_setattr );
}

//-----------------------------------------------------------------------------
//  Sets the value of the 'post_setattr' field of a CFacet instance:
//-----------------------------------------------------------------------------

static int
set_facet_post_setattr ( facet_object * facet, PyObject * value,
                         void * closure ) {

    if ( !PyCallable_Check( value ) ) {
        PyErr_SetString( PyExc_ValueError,
                         "The assigned value must be callable." );
        return -1;
    }
    facet->post_setattr = post_setattr_facet_python;
    return set_value( &facet->py_post_setattr, value );
}

//-----------------------------------------------------------------------------
//  'CFacet' instance methods:
//-----------------------------------------------------------------------------

static PyMethodDef facet_methods[] = {
	{ "__getstate__", (PyCFunction) _facet_getstate,       METH_VARARGS,
	 	PyDoc_STR( "__getstate__()" ) },
	{ "__setstate__", (PyCFunction) _facet_setstate,       METH_VARARGS,
	 	PyDoc_STR( "__setstate__(state)" ) },
	{ "default_value", (PyCFunction) _facet_default_value, METH_VARARGS,
	 	PyDoc_STR( "default_value(default_value)" ) },
	{ "default_value_for", (PyCFunction) _facet_default_value_for, METH_VARARGS,
	 	PyDoc_STR( "default_value_for(object,name)" ) },
	{ "set_validate",  (PyCFunction) _facet_set_validate,  METH_VARARGS,
	 	PyDoc_STR( "set_validate(validate_function)" ) },
	{ "get_validate",  (PyCFunction) _facet_get_validate,  METH_NOARGS,
	 	PyDoc_STR( "get_validate()" ) },
	{ "validate",      (PyCFunction) _facet_validate,      METH_VARARGS,
	 	PyDoc_STR( "validate(object,name,value)" ) },
	{ "delegate",      (PyCFunction) _facet_delegate,      METH_VARARGS,
	 	PyDoc_STR( "delegate(delegate_name,prefix,prefix_type,modify_delegate)" ) },
	{ "rich_comparison",  (PyCFunction) _facet_rich_comparison,  METH_VARARGS,
	 	PyDoc_STR( "rich_comparison(rich_comparison_boolean)" ) },
	{ "comparison_mode",  (PyCFunction) _facet_comparison_mode,  METH_VARARGS,
	 	PyDoc_STR( "comparison_mode(comparison_mode_enum)" ) },
	{ "value_allowed",  (PyCFunction) _facet_value_allowed,  METH_VARARGS,
	 	PyDoc_STR( "value_allowed(value_allowed_boolean)" ) },
	{ "value_property",  (PyCFunction) _facet_value_property, METH_VARARGS,
	 	PyDoc_STR( "value_property(value_facet_boolean)" ) },
	{ "setattr_original_value",
        (PyCFunction) _facet_setattr_original_value,       METH_VARARGS,
	 	PyDoc_STR( "setattr_original_value(original_value_boolean)" ) },
	{ "post_setattr_original_value",
        (PyCFunction) _facet_post_setattr_original_value,  METH_VARARGS,
	 	PyDoc_STR( "post_setattr_original_value(original_value_boolean)" ) },
	{ "is_mapped", (PyCFunction) _facet_is_mapped,  METH_VARARGS,
	 	PyDoc_STR( "is_mapped(is_mapped_boolean)" ) },
	{ "property",      (PyCFunction) _facet_property,      METH_VARARGS,
	 	PyDoc_STR( "property([get,set,validate])" ) },
	{ "clone",         (PyCFunction) _facet_clone,         METH_VARARGS,
	 	PyDoc_STR( "clone(facet)" ) },
	{ "cast",          (PyCFunction) _facet_cast,          METH_VARARGS,
	 	PyDoc_STR( "cast(value)" ) },
	{ "_notifiers",    (PyCFunction) _facet_notifiers,     METH_VARARGS,
	 	PyDoc_STR( "_notifiers(force_create)" ) },
	{ NULL,	NULL },
};

//-----------------------------------------------------------------------------
//  'CFacet' property definitions:
//-----------------------------------------------------------------------------

static PyGetSetDef facet_properties[] = {
	{ "__dict__",     (getter) get_facet_dict,    (setter) set_facet_dict },
	{ "handler",      (getter) get_facet_handler, (setter) set_facet_handler },
	{ "post_setattr", (getter) get_facet_post_setattr,
                      (setter) set_facet_post_setattr },
	{ 0 }
};

//-----------------------------------------------------------------------------
//  'CFacet' type definition:
//-----------------------------------------------------------------------------

static PyTypeObject facet_type = {
    PyObject_HEAD_INIT( DEFERRED_ADDRESS( &PyType_Type ) )
    0,
    "cFacet",
    sizeof( facet_object ),
    0,
    (destructor) facet_dealloc,                    // tp_dealloc
    0,                                             // tp_print
    0,                                             // tp_getattr
    0,                                             // tp_setattr
    0,                                             // tp_compare
    0,                                             // tp_repr
    0,                                             // tp_as_number
    0,                                             // tp_as_sequence
    0,                                             // tp_as_mapping
    0,                                             // tp_hash
    0,                                             // tp_call
    0,                                             // tp_str
    (getattrofunc) facet_getattro,                 // tp_getattro
    0,                                             // tp_setattro
    0,					                           // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, // tp_flags
    0,                                             // tp_doc
    (traverseproc) facet_traverse,                 // tp_traverse
    (inquiry) facet_clear,                         // tp_clear
    0,                                             // tp_richcompare
    0,                                             // tp_weaklistoffset
    0,                                             // tp_iter
    0,                                             // tp_iternext
    facet_methods,                                 // tp_methods
    0,                                             // tp_members
    facet_properties,                              // tp_getset
    DEFERRED_ADDRESS( &PyBaseObject_Type ),        // tp_base
    0,                                             // tp_dict
    0,                                             // tp_descr_get
    0,                                             // tp_descr_set
    sizeof( facet_object ) - sizeof( PyObject * ), // tp_dictoffset
    (initproc) facet_init,                         // tp_init
    DEFERRED_ADDRESS( PyType_GenericAlloc ),       // tp_alloc
    DEFERRED_ADDRESS( PyType_GenericNew )          // tp_new
};

//-----------------------------------------------------------------------------
//  Initializes a 'CFacetNotification' instance:
//-----------------------------------------------------------------------------

int
facet_notification_init ( PyObject * obj, PyObject * args, PyObject * kwds ) {

    PyObject * okind, * object, * name, * arg3,       // Required args
             * arg4 = Undefined, * arg5 = Undefined;  // Possibly optional args
    facet_notification_object * fno;

    if ( !PyArg_UnpackTuple( args, "CFacetNotification", 4, 6,
                             &okind, &object, &name, &arg3, &arg4, &arg5 ) ) {
		return -1;
    }
    fno = (facet_notification_object *) obj;
    switch ( PyInt_AS_LONG( okind ) ) {
        case 0: // "item"
            fno->type = fn_item;
            fno->new = arg3;
            fno->old = arg4;
            Py_INCREF( arg4 );
            break;

        case 1: // "event"
            fno->type = fn_event;
            fno->new  = arg3;
            break;

        case 2: // "list" (assign)
            fno->new = arg3;
            fno->old = arg4;
            Py_INCREF( arg3 );
            Py_INCREF( arg4 ); // fall through into common "list" code...
        case 3:  // "list" (update)
            fno->type    = fn_list;
            fno->added   = arg3;
            fno->removed = arg4;
            fno->index   = arg5;
            Py_INCREF( arg4 );
            Py_INCREF( arg5 );
            break;

        case 4:  // "set" (assign)
            fno->new = arg3;
            fno->old = arg4;
            Py_INCREF( arg3 );
            Py_INCREF( arg4 ); // fall through into common "set" code...
        case 5: // "set" (update)
            fno->type    = fn_set;
            fno->added   = arg3;
            fno->removed = arg4;
            Py_INCREF( arg4 );
            break;

        case 6: // "dict" (assign)
            fno->new = arg3;
            fno->old = arg4;
            Py_INCREF( arg3 );
            Py_INCREF( arg4 ); // fall through into common "dict" code...
        case 7: // "dict" (update)
            fno->type    = fn_dict;
            fno->added   = arg3;
            fno->removed = arg4;
            fno->updated = arg5;
            Py_INCREF( arg4 );
            Py_INCREF( arg5 );
            break;

        default: // invalid 'kind'
            break;
    }
    fno->object = object;
    fno->name   = name;
    Py_INCREF( fno->type );
    Py_INCREF( object );
    Py_INCREF( name );
    Py_INCREF( arg3 );

    return 0;
}

//-----------------------------------------------------------------------------
//  Clears a 'CFacetNotification' instance:
//-----------------------------------------------------------------------------

static int
facet_notification_clear ( facet_notification_object * obj ) {

    Py_CLEAR( obj->type );
    Py_CLEAR( obj->object );
    Py_CLEAR( obj->name );
    Py_CLEAR( obj->new );
    Py_CLEAR( obj->old );
    Py_CLEAR( obj->index );
    Py_CLEAR( obj->added );
    Py_CLEAR( obj->removed );
    Py_CLEAR( obj->updated );
    Py_CLEAR( obj->obj_dict );

    return 0;
}

//-----------------------------------------------------------------------------
//  Deallocates a 'CFacetNotification' instance:
//-----------------------------------------------------------------------------

static void
facet_notification_dealloc ( facet_notification_object * obj ) {

    facet_notification_clear( obj );
    obj->ob_type->tp_free( (PyObject *) obj );
}

//-----------------------------------------------------------------------------
//  Garbage collector traversal method for a 'CFacetNotification' instance:
//-----------------------------------------------------------------------------

static int
facet_notification_traverse ( facet_notification_object * obj, visitproc visit,
                              void * arg ) {

    Py_VISIT( obj->type );
    Py_VISIT( obj->object );
    Py_VISIT( obj->name );
    Py_VISIT( obj->new );
    Py_VISIT( obj->old );
    Py_VISIT( obj->index );
    Py_VISIT( obj->added );
    Py_VISIT( obj->removed );
    Py_VISIT( obj->updated );
    Py_VISIT( obj->obj_dict );

	return 0;
}

//-----------------------------------------------------------------------------
//  Methods for accessing a 'CFacetNotification' instance's fields:
//-----------------------------------------------------------------------------

static PyObject *
get_fn_type ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->type );
}

static PyObject *
get_fn_object ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->object );
}

static PyObject *
get_fn_name ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->name );
}

static PyObject *
get_fn_new ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->new );
}

static PyObject *
get_fn_old ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->old );
}

static PyObject *
get_fn_index ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->index );
}

static PyObject *
get_fn_added ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->added );
}

static PyObject *
get_fn_removed ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->removed );
}

static PyObject *
get_fn_updated ( facet_notification_object * obj, void * closure ) {
    UNDEFINED( obj->updated );
}

//-----------------------------------------------------------------------------
//  'CFacetsNotification' property definitions:
//-----------------------------------------------------------------------------

static PyGetSetDef facet_notification_properties[] = {
	{ "type",    (getter) get_fn_type,    NULL, },
	{ "object",  (getter) get_fn_object,  NULL, },
	{ "name",    (getter) get_fn_name,    NULL, },
	{ "new",     (getter) get_fn_new,     NULL, },
	{ "old",     (getter) get_fn_old,     NULL, },
	{ "index",   (getter) get_fn_index,   NULL, },
	{ "added",   (getter) get_fn_added,   NULL, },
	{ "removed", (getter) get_fn_removed, NULL, },
	{ "updated", (getter) get_fn_updated, NULL, },
	{ 0 }
};

//-----------------------------------------------------------------------------
//  'CFacetNotification' __doc__ string:
//-----------------------------------------------------------------------------

PyDoc_STRVAR( facet_notification_doc,
"CFacetNotification(???)\n\
\n\
Create a Facet Notification object.");

//-----------------------------------------------------------------------------
//  'CFacetNotification' type definition:
//-----------------------------------------------------------------------------

static PyTypeObject facet_notification_type = {
	PyObject_HEAD_INIT( DEFERRED_ADDRESS( &PyType_Type ) )
	0,
	"CFacetNotification",
	sizeof( facet_notification_object ),
	0,
	(destructor) facet_notification_dealloc,         // tp_dealloc
	0,                                               // tp_print
	0,                                               // tp_getattr
	0,                                               // tp_setattr
	0,                                               // tp_compare
	0,                                               // tp_repr
	0,                                               // tp_as_number
	0,                                               // tp_as_sequence
	0,                                               // tp_as_mapping
	0,                                               // tp_hash
    0,                                               // tp_call
	0,                                               // tp_str
	0,                                               // tp_getattro
    0,                                               // tp_setattro
	0,					                             // tp_as_buffer
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE| Py_TPFLAGS_HAVE_GC, // tp_flags
	facet_notification_doc,                          // tp_doc
	(traverseproc) facet_notification_traverse,      // tp_traverse
	(inquiry) facet_notification_clear,              // tp_clear
	0,                                               // tp_richcompare
 	0,                                               // tp_weaklistoffset
	0,				                                 // tp_iter
	0,				                                 // tp_iternext
	0,				                                 // tp_methods
    0,                                               // tp_members
    facet_notification_properties,                   // tp_getset
	0,				                                 // tp_base
	0,				                                 // tp_dict
	0,                                               // tp_descr_get
	0,                                               // tp_descr_set
	0,                                               // tp_dictoffset
	facet_notification_init,                         // tp_init
	0,                                               // tp_alloc
    0,                                               // tp_new
};

//-----------------------------------------------------------------------------
//  Sets the global 'Undefined' and 'Uninitialized' values:
//-----------------------------------------------------------------------------

static PyObject *
_cfacets_undefined ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "OO", &Undefined, &Uninitialized ) )
        return NULL;

    Py_INCREF( Undefined );
    Py_INCREF( Uninitialized );

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the global 'FacetError' and 'DelegationError' exception types:
//-----------------------------------------------------------------------------

static PyObject *
_cfacets_exceptions ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "OO", &FacetError, &DelegationError ) )
        return NULL;

    Py_INCREF( FacetError );
    Py_INCREF( DelegationError );

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the global 'FacetValue' class:
//-----------------------------------------------------------------------------

static PyObject *
_cfacets_value_class ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "O", &FacetValue ) )
        return NULL;

    Py_INCREF( FacetValue );

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the global 'adapt' reference to the PyProtocols 'adapt' function:
//-----------------------------------------------------------------------------

static PyObject *
_cfacets_adapt ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "O", &adapt ) )
        return NULL;

    Py_INCREF( adapt );

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the global 'validate_implements' reference to the Python level
//  function:
//-----------------------------------------------------------------------------

static PyObject *
_cfacets_validate_implements ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "O", &validate_implements ) )
        return NULL;

    Py_INCREF( validate_implements );

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the global 'cfacet_type' class reference:
//-----------------------------------------------------------------------------

static PyObject *
_cfacets_cfacet ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "O", &cfacet_type ) )
        return NULL;

    Py_INCREF( cfacet_type );

    Py_INCREF( Py_None );
    return Py_None;
}

//-----------------------------------------------------------------------------
//  Sets the global 'facet_notification_handler' function, and returns the
//  previous value:
//-----------------------------------------------------------------------------

static PyObject *
_cfacets_facet_notification_handler ( PyObject * self, PyObject * args ) {

    PyObject * result = _facet_notification_handler;

    if ( !PyArg_ParseTuple( args, "O", &_facet_notification_handler ) ) {
        return NULL;
    }

    if ( _facet_notification_handler == Py_None ) {
        _facet_notification_handler = NULL;
    } else {
        Py_INCREF( _facet_notification_handler );
    }

    if ( result == NULL ) {
        Py_INCREF( Py_None );
        result = Py_None;
    }

    return result;
}

//-----------------------------------------------------------------------------
//  Performs an HLSA image transform on a specified image buffer and returns the
//  transformed image buffer (or None, if no transform is specified).
//-----------------------------------------------------------------------------

unsigned char
hls ( double m1, double m2, double hue ) {
    if ( hue > 1.0 )
        hue -= 1.0;

    if ( hue < (1.0 / 6.0) )
        return (unsigned char) ((m1 + ((m2 - m1) * hue * 6.0)) * 255.0);

    if ( hue < 0.5 )
        return (unsigned char) (m2 * 255.0);

    if ( hue >= (2.0 / 3.0) )
        return (unsigned char) (m1 * 255.0);

    return (unsigned char) ((m1 + ((m2 - m1) * ((2.0 / 3.0) - hue) * 6.0))
                            * 255.0);
}

static PyObject *
_cfacets_hlsa_transform ( PyObject * self, PyObject * args ) {

    unsigned char * image, * new_image, rgb;
    ParseTuple_StringLen image_len;
    unsigned int width, height;
    int r, g, b, max_rgb, min_rgb, accept_all;
    double hue, hue_masked, hue_low, hue_high, lightness, lightness_masked,
           lightness_low, lightness_high, saturation, saturation_masked,
           saturation_low, saturation_high, alpha, alpha_masked, alpha_low,
           alpha_high, h, l, s, a, max_plus, chroma, m1, m2;
    PyObject * result;

    if ( !PyArg_ParseTuple( args, "s#iidddddddd(dd)(dd)(dd)(dd)",
             &image, &image_len, &width, &height, &hue, &lightness, &saturation,
             &alpha, &hue_masked, &lightness_masked, &saturation_masked,
             &alpha_masked, &hue_low, &hue_high, &lightness_low,
             &lightness_high, &saturation_low, &saturation_high, &alpha_low,
             &alpha_high ) ) {
        return NULL;
    }

    if ( image_len != (4 * width * height) ) {
        // fixme: raise an exception here...
    }

    // Check to see if the mask is degenerate:
    accept_all = ((hue_low        == 0.0) && (hue_high        == 1.0) &&
                  (lightness_low  == 0.0) && (lightness_high  == 1.0) &&
                  (saturation_low == 0.0) && (saturation_high == 1.0) &&
                  (alpha_low      == 0.0) && (alpha_high      == 1.0));

    if ( ((hue        == 0.0) && (hue_masked        == 0.0)  &&
          (lightness  == 0.0) && (lightness_masked  == 0.0)  &&
          (saturation == 0.0) && (saturation_masked == 0.0)  &&
          (alpha      == 0.0) && (alpha_masked      == 0.0)) ||
         (hue_low        > hue_high)        ||
         (lightness_low  > lightness_high)  ||
         (saturation_low > saturation_high) ||
         (alpha_low      > alpha_high) ) {
        Py_INCREF( Py_None );

        return Py_None;
    }

    result = PyString_FromStringAndSize( NULL, (Py_ssize_t) image_len );
    if ( result == NULL ) {
        return NULL;
    }

    new_image = (unsigned char *) PyString_AsString( result );
    while ( image_len > 0 ) {

        // Extract the next rgba values and calculate their max/min values:
        max_rgb = min_rgb = b = *image++;

        if ( (g = *image++) > max_rgb )
            max_rgb = g;
        else if ( g < min_rgb )
            min_rgb = g;

        if ( (r = *image++) > max_rgb )
            max_rgb = r;
        else if ( r < min_rgb )
            min_rgb = r;

        a = (*image++) / 255.0;

        // Convert rgb to hls:
        max_plus = max_rgb + min_rgb;
        chroma   = max_rgb - min_rgb;
        l        = max_plus / 510.0;
        if ( chroma == 0.0 ) {
            h = s = 0.0;
        } else {
            if ( l <= 0.5 ) {
                s = chroma / max_plus;
            } else {
                s = chroma / (510.0 - max_plus);
            }

            if ( r == max_rgb ) {
                h = (g - b) / chroma;
            } else {
                if ( g == max_rgb ) {
                    h = 2.0 + ((b - r) / chroma);
                } else {
                    h = 4.0 + ((r - g) / chroma);
                }
            }
            h = h / 6.0;
            if ( h < 0.0 ) {
                h += 1.0;
            } else if ( h > 1.0 ) {
                h -= 1.0;
            }
        }

        // Perform the mask and transform operation:
        if ( accept_all ||
             ((h >= hue_low)        && (h <= hue_high)        &&
              (l >= lightness_low)  && (l <= lightness_high)  &&
              (s >= saturation_low) && (s <= saturation_high) &&
              (a >= alpha_low)      && (s <= alpha_high)) ) {
            h += hue;
            l += lightness;
            s += saturation;
            a += alpha;
        } else {
            h += hue_masked;
            l += lightness_masked;
            s += saturation_masked;
            a += alpha_masked;
        }

        // Make sure all values are in their defined range:
        if      ( h < 0.0 ) h += 1.0;
        else if ( h > 1.0 ) h -= 1.0;

        if      ( l < 0.0 ) l = 0.0;
        else if ( l > 1.0 ) l = 1.0;

        if      ( s < 0.0 ) s = 0.0;
        else if ( s > 1.0 ) s = 1.0;

        if      ( a < 0.0 ) a = 0.0;
        else if ( a > 1.0 ) a = 1.0;

        // Convert hlsa back to rgba and save result in the new image buffer:
        if ( s == 0.0 ) {
            rgb          = (unsigned char) (255.0 * l);
            *new_image++ = rgb;
            *new_image++ = rgb;
            *new_image++ = rgb;
        } else {
            if ( l <= 0.5 )
                m2 = l * (1.0 + s);
            else
                m2 = l + s - (l * s);
            m1 = (2.0 * l) - m2;

            *new_image++ = hls( m1, m2, h + (2.0 / 3.0) );
            *new_image++ = hls( m1, m2, h );
            *new_image++ = hls( m1, m2, h + (1.0 / 3.0) );
        }
        *new_image++ = (unsigned char) (255.0 * a);

        image_len -= 4;
    }

    return result;
}

//-----------------------------------------------------------------------------
//  Performs an image scaling transform on a specified image buffer and returns
//  the scaled image buffer.
//
//  This is derived from code written by Carlo Pallini in the article on "Plain
//  C Resampling DLL" on The Code Project:
//  - http://www.codeproject.com/KB/GDI/plain_c_resampling_dll.aspx
//  which in turn was based on Libor Tinka's article "Image Resizing -
//  outperform GDI+" that may also be found at The Code Project:
//  - http://www.codeproject.com/KB/GDI-plus/imgresizoutperfgdiplus.aspx
//-----------------------------------------------------------------------------

#define _USE_MATH_DEFINES
#include <math.h>

// Minimum and maximum resampling sizes:
#define MIN_RESAMPLE_WIDTH  1
#define MIN_RESAMPLE_HEIGHT 1
#define MAX_RESAMPLE_WIDTH  0x2000
#define MAX_RESAMPLE_HEIGHT 0x2000

// RGBA:
#define COLOR_COMPONENTS 4

// Filter function type:
typedef double (* image_filter) ( double );

#define STOCK_FILTERS 13

//-- 'image_transform' function filtering kernel routines ---------------------

// Bell filter, default radius 1.5:
double _Bell ( double x ) {
	if ( x < 0.0 )
	    x = -x;

    if ( x < 0.5 )
        return (0.75 - (x * x));

    if ( x < 1.5 )
        return (0.5 * pow( x - 1.5, 2.0 ));

    return 0.0;
}

// Box filter, default radius 0.5:
double _Box ( double x ) {
	if ( x < 0.0 )
	    x = -x;

	if ( x <= 0.5 )
	    return 1.0;

    return 0.0;
}

// CatmullRom filter, default radius 2:
double _CatmullRom ( double x ) {
	double x2;

	if ( x < 0.0 )
	    x = -x;

	x2 = x * x;
	if ( x <= 1.0 )
	    return ((1.5 * x2 * x) - (2.5 * x2) + 1.0);

	if ( x <= 2.0 )
	    return ((-0.5 * x2 * x) + (2.5 * x2) - (4.0 * x) + 2);

	return 0.0;
}

// Cosine filter, default radius 1:
double _Cosine ( double x ) {
	if ( (x >= -1.0) && (x <= 1.0) )
	    return ((cos( x * M_PI ) + 1.0) / 2.0);

	return 0.0;
}

// CubicConvolution filter, default radius 3:
double _CubicConvolution ( double x ) {
	double x2;

	if ( x < 0.0 )
	    x = -x;

	x2 = x * x;
	if ( x <= 1.0 )
	    return (((4.0 / 3.0) * x2 * x) - ((7.0 / 3.0) * x2) + 1.0);

	if ( x <= 2.0 )
	    return (-((7.0 / 12.0) * x2 * x) + (3.0 * x2) - ((59.0 / 12.0) * x) +
	            2.5);

	if ( x <= 3.0 )
	    return ( ((1.0/12.0) * x2 * x) - ((2.0 / 3.0) * x2) + (1.75 * x) - 1.5);

	return 0.0;
}

// CubicSpline filter, default radius 2:
double _CubicSpline ( double x ) {
	double x2;

	if ( x < 0.0 )
	    x = -x;

	if ( x < 1.0 ) {
	    x2 = x * x;

	    return ((0.5 * x2 * x) - x2 + (2.0 / 3.0));
    }

    if ( x < 2.0 ) {
		x = 2.0 - x;

		return (pow( x, 3.0 ) / 6.0);
   }

   return 0.0;
}

// Hermite filter, default radius 1:
double _Hermite ( double x ) {
	if ( x < 0.0 )
	    x = -x;

	if ( x < 1.0 )
	    return ((((2.0 * x) - 3.0) * x * x) + 1.0 );

	return 0.0;
}

// Lanczos3 filter, default radius 3:
double _Lanczos3 ( double x ) {
	const double R = 3.0;

    if (x  < 0.0 )
        x = -x;

	if ( x == 0.0 )
	    return 1.0;

	if ( x < R ) {
		x *= M_PI;

		return ((R * sin( x ) * sin( x / R )) / (x * x));
	}

	return 0.0;
}

// Lanczos8 filter, default radius 8:
double _Lanczos8 ( double x ) {
	const double R = 8.0;

	if ( x  < 0.0 )
	    x = -x;

	if ( x == 0.0 )
	    return 1;

	if ( x < R ) {
		x *= M_PI;

		return ((R * sin( x ) * sin( x / R )) / (x * x));
	}

	return 0.0;
}

// Mitchell filter, default radius 2.0:
double _Mitchell ( double x ) {
	const double C = 1.0/3.0;
	double x2;

	if ( x < 0.0 )
	    x = -x;

	x2 = x * x;
	if ( x < 1.0 ) {
		x = (((12.0 - (9.0 * C) - (6.0 * C)) * (x * x2)) +
		     ((-18.0 + (12.0 * C) + (6.0 * C)) * x2) + (6.0 - (2.0 * C)));

		return (x / 6.0);
    }

    if ( x < 2.0 ) {
		x = (((-C - (6.0 * C)) * (x * x2)) + (((6.0 * C) + (30.0 * C)) * x2) +
		     (((-12.0 * C) - (48.0 * C)) * x) + ((8.0 * C) + (24.0 * C)));

        return (x / 6.0);
    }

    return 0.0;
}

// Quadratic filter, default radius 1.5:
double _Quadratic ( double x ) {
    if ( x < 0.0 )
        x = -x;

    if ( x <= 0.5 )
        return ((-2.0 * x * x) + 1.0);

    if ( x <= 1.5 )
        return ((x * x) - (2.5 * x) + 1.5);

    return 0.0;
}

// QuadraticBSpline filter, default radius 1.5:
double _QuadraticBSpline ( double x ) {
  if ( x < 0.0 )
      x = -x;

  if ( x <= 0.5 )
      return (0.75 - (x * x));

  if ( x <= 1.5 )
      return ((0.5 * x * x) - (1.5 * x) + 1.125);

  return 0.0;
}

// Trangle filter, default radius 1:
double _Triangle ( double x ) {
    if ( x < 0.0 )
        x = -x;

    if ( x < 1.0 )
        return (1.0 - x);

    return 0.0;
}

// The core filter routines mapped by filter index:
static image_filter core_filters[] = {
    _Bell, _Box, _CatmullRom, _Cosine, _CubicConvolution, _CubicSpline,
    _Hermite, _Lanczos3, _Lanczos8, _Mitchell, _Quadratic, _QuadraticBSpline,
    _Triangle
};

// The core filter radii mapped by filter index:
static double core_radius[] = {
    8.0, 3.0, 1.0, 0.5, 1.0, 1.5, 2.0, 2.0, 1.0, 2.0, 1.5, 1.5, 3.0
};

static PyObject *
_cfacets_image_transform ( PyObject * self, PyObject * args ) {

	int          i, j, k, m, n, col, swidth, sheight, dwidth, dheight;
	unsigned int val, filter_index, hneed, vneed;
	double       xscale, yscale, radius, wsum;
	double       center;     // Center of current sampling
	double       weight;     // Current weight
	int          left;       // Left of current sampling
	int          right;      // Right of current sampling

	unsigned int * ib;       // Input buffer
	unsigned int * ob;       // Output buffer
	unsigned int * tb;       // Temporary intermediate buffer

	double       * hweight;  // Weight contribution    [dwidth][HMAX_CONTRIBS]
	int          * hpixel;   // Pixel that contributes [dwidth][HMAX_CONTRIBS]
	int          * hcount;   // How many contribution for the pixel [dwidth]
	double       * hwsum;    // Sum of weights                      [dwidth]

	double       * vweight;  // Weight contribution    [dheight][VMAX_CONTRIBS]
	int          * vpixel;   // Pixel that contributes [dheight][VMAX_CONTRIBS]
	int          * vcount;   // How many contribution for the pixel [dheight]
	double       * vwsum;    // Sum of weights                      [dheight]

	double       * pweight;  // Temporary pointer
	int          * ppixel;   // Temporary pointer

	double intensity[ COLOR_COMPONENTS ];	// RGBA component intensities

	// Almost-const: Maximum number of contribution for current sampling:
	int HMAX_CONTRIBS, VMAX_CONTRIBS;

	// Almost-const: Scaled radius for downsampling operations:
	double HSCALED_RADIUS, VSCALED_RADIUS;

	// Almost-const: Filter factor for downsampling operations:
	double HFILTER_FACTOR, VFILTER_FACTOR;

	ParseTuple_StringLen image_len;  // The length of the input image buffer
	image_filter         filter;     // The image filter to be applied
    PyObject           * image, * result;

    // Parse the arguments passed in:
    if ( !PyArg_ParseTuple( args, "s#iiiii", &ib, &image_len, &swidth, &sheight,
                            &dwidth, &dheight, &filter_index ) ) {
        return NULL;
    }

    if ( image_len != (4 * swidth * sheight) ) {
        // fixme: raise an exception here...
        return NULL;
    }

	filter = core_filters[ filter_index % STOCK_FILTERS ];
	radius = core_radius[  filter_index % STOCK_FILTERS ];

    // Validate the destination image size:
	if ( dwidth < MIN_RESAMPLE_WIDTH ) {
		dwidth = MIN_RESAMPLE_WIDTH;
	} else if (dwidth > MAX_RESAMPLE_WIDTH ) {
		dwidth = MAX_RESAMPLE_WIDTH;
	}

	if ( dheight < MIN_RESAMPLE_HEIGHT ) {
		dheight = MIN_RESAMPLE_HEIGHT;
	} else if ( dheight > MAX_RESAMPLE_HEIGHT ) {
		dheight = MAX_RESAMPLE_HEIGHT;
	}

	if ( (dwidth == swidth) && (dheight == sheight) ) {
	    // Same size, no resampling needed, so return the input image buffer:
        if ( !PyArg_ParseTuple( args, "Oiiiii", &image, &swidth, &sheight,
                                &dwidth, &dheight, &filter_index ) ) {
            return NULL;
        }
        Py_INCREF( image );

        return image;
    }

	xscale = (((double) dwidth)  / swidth);
	yscale = (((double) dheight) / sheight);

	if ( xscale > 1.0 ) {
		// Horizontal upsampling:
		HFILTER_FACTOR = 1.0;
		HSCALED_RADIUS = radius;
	} else {
	    // Horizontal downsampling:
		HFILTER_FACTOR = xscale;
		HSCALED_RADIUS = radius / xscale;
	}

	if ( yscale > 1.0 ) {
	    // Vertical upsampling:
		VFILTER_FACTOR = 1.0;
		VSCALED_RADIUS = radius;
	} else {
	    // Vertical downsampling:
		VFILTER_FACTOR = yscale;
		VSCALED_RADIUS = radius / yscale;
	}

	// The maximum number of contributions for a target pixel:
	HMAX_CONTRIBS = (int) ((2 * HSCALED_RADIUS) + 1);
	VMAX_CONTRIBS = (int) ((2 * VSCALED_RADIUS) + 1);

	hneed = dwidth  * (HMAX_CONTRIBS + 1) * (sizeof( double ) + sizeof( int ));
	vneed = dheight * (VMAX_CONTRIBS + 1) * (sizeof( double ) + sizeof( int ));
	if ( vneed > hneed ) {
	    hneed = vneed;
	}
    hneed += (dwidth * sheight * sizeof( unsigned int ));

	tb = (unsigned int *) PyMem_Malloc( hneed );
	if ( tb == NULL ) {
	    return NULL;
	}

    result = PyString_FromStringAndSize(
        NULL, (Py_ssize_t) (COLOR_COMPONENTS * dwidth * dheight)
    );
    if ( result == NULL ) {
        return NULL;
    }

	ob = (unsigned int *) PyString_AsString( result );

	// Weights:
	hweight = (double *) (tb + (dwidth * sheight));

	// Contributing pixels:
	hpixel = (int *) (hweight + (dwidth * HMAX_CONTRIBS));

	// How may contributions for the target pixel:
	hcount = (int *) (hpixel + (dwidth * HMAX_CONTRIBS));

	// Sum of the weights for the target pixel:
	hwsum = (double *) (hcount + dwidth);

	// Pre-calculate weights contribution for a row:
	for ( i = 0; i < dwidth; i++ ) {
		pweight = hweight + (i * HMAX_CONTRIBS);
		ppixel  = hpixel  + (i * HMAX_CONTRIBS);
		n       = 0;
		wsum    = 0.0;
		center  = ((double) i) / xscale;
		left    = (int) ((center + .5) - HSCALED_RADIUS);
		right   = (int) (left + (2 * HSCALED_RADIUS));
		if ( right >= swidth )
		    right = swidth - 1;

		for ( j = (left < 0)? 0: left; j <= right; j++ ) {
			weight = (*filter)( (center - j) * HFILTER_FACTOR );
			if ( weight != 0.0 ) {
			    ppixel[ n ]  = j;
			    pweight[ n ] = weight;
			    wsum        += weight;
			    n++;  // Increment contribution count
			}
		}
		hwsum[ i ]  = wsum;
		hcount[ i ] = n;
	}

	// Filter horizontally from input to temporary buffer:
	for ( n = 0, k = 0, m = 0; n < sheight; n++, k += swidth, m += dwidth ) {

		// Here 'n' runs on the vertical coordinate:
		for ( i = 0, pweight = hweight, ppixel = hpixel;
		      i < dwidth;
		      i++, pweight += HMAX_CONTRIBS, ppixel += HMAX_CONTRIBS ) {

			intensity[0] = intensity[1] = intensity[2] = intensity[3] = 0.0;

			for ( j = 0; j < hcount[ i ]; j++ ) {
				weight        = pweight[ j ];
				val           = ib[ ppixel[ j ] + k ];
				intensity[0] += (val         & 0xFF) * weight;
				intensity[1] += ((val >>  8) & 0xFF) * weight;
				intensity[2] += ((val >> 16) & 0xFF) * weight;
				intensity[3] += ((val >> 24) & 0xFF) * weight;
			}

		    wsum = hwsum[ i ];
			col  = (int) ((intensity[3] / wsum) + 0.5);
			val  = (col < 0)? 0: (col > 255)? 255: col;
			col  = (int) ((intensity[2] / wsum) + 0.5);
			val  = (val << 8) | ((col < 0)? 0: (col > 255)? 255: col);
			col  = (int) ((intensity[1] / wsum) + 0.5);
			val  = (val << 8) | ((col < 0)? 0: (col > 255)? 255: col);
			col  = (int) ((intensity[0] / wsum) + 0.5);
			val  = (val << 8) | ((col < 0)? 0: (col > 255)? 255: col);

			// Save result in temporary buffer[ dwidth x sheight ]:
			tb[ i + m ] = val;
		}
	}

	// Weights:
	vweight = hweight;

	/* The contributing pixels: */
	vpixel = (int *) (vweight + (dheight * VMAX_CONTRIBS));

	/* How may contributions for the target pixel: */
	vcount = (int *) (vpixel + (dheight * VMAX_CONTRIBS));

	/* Sum of the weights for the target pixel: */
	vwsum = (double *) (vcount + dheight);

	for ( i = 0; i < dheight; i++ ) {
		pweight = vweight + (i * VMAX_CONTRIBS);
		ppixel  = vpixel  + (i * VMAX_CONTRIBS);
		n       = 0;
		wsum    = 0.0;
		center = ((double) i) / yscale;
		left   = (int) (center + 0.5 - VSCALED_RADIUS);
		right  = (int) (left + (2 * VSCALED_RADIUS));
		if ( right >= sheight )
		    right = sheight - 1;

		for ( j = (left < 0)? 0: left; j <= right; j++ ) {
			weight = (*filter)( (center - j) * VFILTER_FACTOR );
			if ( weight != 0.0 ) {
			    ppixel[ n ]  = j;
			    pweight[ n ] = weight;
			    wsum        += weight;
			    n++;               // Increment the contribution count
			}
		}
		vwsum[ i ]  = wsum;
		vcount[ i ] = n;
	}

	// Filter vertically from temporary buffer to output buffer:
	for ( n = 0; n < dwidth; n++ ) {
	    for ( i = 0, pweight = vweight, ppixel = vpixel;
	          i < dheight;
	          i++, pweight += VMAX_CONTRIBS, ppixel += VMAX_CONTRIBS ) {

	        intensity[0] = intensity[1] = intensity[2] = intensity[3] = 0.0;

            for ( j = 0; j < vcount[ i ]; j++ ) {
                weight        = pweight[ j ];
                val           = tb[ n + (dwidth * ppixel[ j ]) ];
                intensity[0] += (val         & 0xFF) * weight;
                intensity[1] += ((val >>  8) & 0xFF) * weight;
                intensity[2] += ((val >> 16) & 0xFF) * weight;
                intensity[3] += ((val >> 24) & 0xFF) * weight;
            }

		    wsum = vwsum[ i ];
			col  = (int) ((intensity[3] / wsum) + 0.5);
			val  = (col < 0)? 0: (col > 255)? 255: col;
			col  = (int) ((intensity[2] / wsum) + 0.5);
			val  = (val << 8) | ((col < 0)? 0: (col > 255)? 255: col);
			col  = (int) ((intensity[1] / wsum) + 0.5);
			val  = (val << 8) | ((col < 0)? 0: (col > 255)? 255: col);
			col  = (int) ((intensity[0] / wsum) + 0.5);
			val  = (val << 8) | ((col < 0)? 0: (col > 255)? 255: col);
            ob[ n + (i * dwidth) ] = val;
        }
    }

	PyMem_Free( tb );

    return result;
}

//-----------------------------------------------------------------------------
//  'cfacets' module methods:
//-----------------------------------------------------------------------------

static PyMethodDef cfacets_methods[] = {
	{ "_undefined",    (PyCFunction) _cfacets_undefined,    METH_VARARGS,
	 	PyDoc_STR( "_undefined(Undefined,Uninitialized)" ) },
	{ "_exceptions",   (PyCFunction) _cfacets_exceptions,   METH_VARARGS,
	 	PyDoc_STR( "_exceptions(FacetError,DelegationError)" ) },
	{ "_value_class", (PyCFunction) _cfacets_value_class,   METH_VARARGS,
	 	PyDoc_STR( "_value_class(FacetValue)" ) },
	{ "_adapt", (PyCFunction) _cfacets_adapt, METH_VARARGS,
	 	PyDoc_STR( "_adapt(PyProtocols._speedups.adapt)" ) },
	{ "_validate_implements", (PyCFunction) _cfacets_validate_implements,
        METH_VARARGS, PyDoc_STR( "_validate_implements(validate_implements)" )},
	{ "_cfacet",       (PyCFunction) _cfacets_cfacet,       METH_VARARGS,
	 	PyDoc_STR( "_cfacet(CFacet_class)" ) },
	{ "_facet_notification_handler",
        (PyCFunction) _cfacets_facet_notification_handler,  METH_VARARGS,
        PyDoc_STR( "_facet_notification_handler(handler)" ) },
	{ "hlsa_transform",
        (PyCFunction) _cfacets_hlsa_transform,  METH_VARARGS,
        PyDoc_STR( "hlsa_transform(buffer,width,height,hue_shift,lightness_shift,saturation_shift,alpha_shift,hue_range,lightness_range,saturation_range,alpha_range)" ) },
	{ "image_transform",
        (PyCFunction) _cfacets_image_transform,  METH_VARARGS,
        PyDoc_STR( "image_transform(buffer,src_width,src_height,dst_width,dst_height,filter_index)" ) },
	{ NULL,	NULL },
};

//-----------------------------------------------------------------------------
//  Facet method object definition:
//-----------------------------------------------------------------------------

typedef struct {
    PyObject_HEAD
    PyObject * tm_name;        // The name of the method
    PyObject * tm_func;        // The callable object implementing the method
    PyObject * tm_self;        // The instance it is bound to, or NULL
    PyObject * tm_facets;      // Tuple containing return/arguments facets
    PyObject * tm_class;       // The class that asked for the method
    PyObject * tm_weakreflist; // List of weak references
} facet_method_object;

//-----------------------------------------------------------------------------
//  Instance method objects are used for two purposes:
//  (a) as bound instance methods (returned by instancename.methodname)
//  (b) as unbound methods (returned by ClassName.methodname)
//  In case (b), tm_self is NULL
//-----------------------------------------------------------------------------

static facet_method_object * free_list;

//-----------------------------------------------------------------------------
//  Creates a new facet method instance:
//-----------------------------------------------------------------------------

static PyObject *
create_facet_method ( PyObject * name, PyObject * func, PyObject * self,
                      PyObject * facets,PyObject * class_obj ) {

	register facet_method_object * im;

	assert( PyCallable_Check( func ) );

	im = free_list;
	if ( im != NULL ) {
		free_list = (facet_method_object *)(im->tm_self);
		PyObject_INIT( im, &facet_method_type );
	} else {
        // fixme: Should we use this form of New if the other 'fixme's are
        // commented out?...
		im = PyObject_GC_New( facet_method_object, &facet_method_type );
		if ( im == NULL )
			return NULL;
	}
	im->tm_weakreflist = NULL;
	Py_INCREF( name );
	im->tm_name = name;
	Py_INCREF( func );
	im->tm_func = func;
	Py_XINCREF( self );
	im->tm_self = self;
	Py_INCREF( facets );
	im->tm_facets = facets;
	Py_XINCREF( class_obj );
	im->tm_class = class_obj;
    // fixme: The following line doesn't link into a separate DLL:
	//_PyObject_GC_TRACK( im );
	return (PyObject *) im;
}

//-----------------------------------------------------------------------------
//  Gets the value of a facet method attribute:
//
//  The getattr() implementation for facet method objects is similar to
//  PyObject_GenericGetAttr(), but instead of looking in __dict__ it
//  asks tm_self for the attribute.  Then the error handling is a bit
//  different because we want to preserve the exception raised by the
//  delegate, unless we have an alternative from our class.
//-----------------------------------------------------------------------------

static PyObject *
facet_method_getattro ( PyObject * obj, PyObject * name ) {

	facet_method_object *im = (facet_method_object *) obj;
	PyTypeObject * tp       = obj->ob_type;
	PyObject     * descr    = NULL, * res;
	descrgetfunc f          = NULL;

	if ( PyType_HasFeature( tp, Py_TPFLAGS_HAVE_CLASS ) ) {
		if ( tp->tp_dict == NULL ) {
			if ( PyType_Ready(tp) < 0 )
				return NULL;
		}
		descr = _PyType_Lookup( tp, name );
	}

	f = NULL;
	if ( descr != NULL ) {
		f = TP_DESCR_GET( descr->ob_type );
		if ( (f != NULL) && PyDescr_IsData( descr ) )
			return f( descr, obj, (PyObject *) obj->ob_type );
	}

	res = PyObject_GetAttr( im->tm_func, name );
	if ( (res != NULL) || !PyErr_ExceptionMatches( PyExc_AttributeError ) )
		return res;

	if ( f != NULL ) {
		PyErr_Clear();
		return f( descr, obj, (PyObject *) obj->ob_type );
	}

	if ( descr != NULL ) {
		PyErr_Clear();
		Py_INCREF( descr );
		return descr;
	}

	assert( PyErr_Occurred() );
	return NULL;
}

//-----------------------------------------------------------------------------
//  Creates a new facet method:
//-----------------------------------------------------------------------------

static PyObject *
facet_method_new ( PyTypeObject * type, PyObject * args, PyObject * kw ) {

	PyObject * name;
	PyObject * func;
    PyObject * facets;

	if ( !PyArg_UnpackTuple( args, "facetmethod", 3, 3,
	                         &name, &func, &facets ) ) {
		return NULL;
    }
	if ( !PyCallable_Check( func ) ) {
		PyErr_SetString( PyExc_TypeError, "second argument must be callable" );
		return NULL;
	}
    // fixme: Should we sanity check the 'facets' argument here?...
	return create_facet_method( name, func, NULL, facets, NULL );
}

//-----------------------------------------------------------------------------
//  Deallocates a facet method:
//-----------------------------------------------------------------------------

static void
facet_method_dealloc ( register facet_method_object * tm ) {

    // fixme: The following line complements the _PyObject_GC_TRACK( im )
    // line commented out above...
	//_PyObject_GC_UNTRACK( tm );
	if ( tm->tm_weakreflist != NULL ) {
		PyObject_ClearWeakRefs( (PyObject *) tm );
    }
	Py_DECREF(  tm->tm_name );
	Py_DECREF(  tm->tm_func );
	Py_XDECREF( tm->tm_self );
	Py_DECREF(  tm->tm_facets );
	Py_XDECREF( tm->tm_class );
	tm->tm_self = (PyObject *) free_list;
	free_list   = tm;
}

//-----------------------------------------------------------------------------
//  Compare two facet methods:
//-----------------------------------------------------------------------------

static int
facet_method_compare ( facet_method_object * a, facet_method_object * b ) {

	if ( a->tm_self != b->tm_self ) {
		return (a->tm_self < b->tm_self) ? -1 : 1;
    }
	return PyObject_Compare( a->tm_func, b->tm_func );
}

//-----------------------------------------------------------------------------
//  Returns the string representation of a facet method:
//-----------------------------------------------------------------------------

static PyObject *
facet_method_repr ( facet_method_object * a ) {

	PyObject * self     = a->tm_self;
	PyObject * func     = a->tm_func;
	PyObject * klass    = a->tm_class;
	PyObject * funcname = NULL, * klassname  = NULL, * result = NULL;
	char     * sfuncname = "?", * sklassname = "?";

	funcname = PyObject_GetAttrString( func, "__name__" );
	if ( funcname == NULL ) {
		if ( !PyErr_ExceptionMatches( PyExc_AttributeError ) )
			return NULL;
		PyErr_Clear();
	} else if ( !PyString_Check( funcname ) ) {
		Py_DECREF( funcname );
		funcname = NULL;
	} else
		sfuncname = PyString_AS_STRING( funcname );

	if ( klass == NULL )
		klassname = NULL;
	else {
		klassname = PyObject_GetAttrString( klass, "__name__" );
		if (klassname == NULL) {
			if ( !PyErr_ExceptionMatches( PyExc_AttributeError ) )
				return NULL;
			PyErr_Clear();
		} else if ( !PyString_Check( klassname ) ) {
			Py_DECREF( klassname );
			klassname = NULL;
		} else
			sklassname = PyString_AS_STRING( klassname );
	}

	if ( self == NULL )
		result = PyString_FromFormat( "<unbound method %s.%s>",
					                  sklassname, sfuncname );
	else {
		// fixme: Shouldn't use repr() here!
		PyObject * selfrepr = PyObject_Repr( self );
		if ( selfrepr == NULL )
			goto fail;
		if ( !PyString_Check( selfrepr ) ) {
			Py_DECREF( selfrepr );
			goto fail;
		}
		result = PyString_FromFormat( "<bound method %s.%s of %s>",
					                  sklassname, sfuncname,
					                  PyString_AS_STRING( selfrepr ) );
		Py_DECREF( selfrepr );
	}

  fail:
	Py_XDECREF( funcname );
	Py_XDECREF( klassname );
	return result;
}

//-----------------------------------------------------------------------------
//  Computes the hash of a facet method:
//-----------------------------------------------------------------------------

static long
facet_method_hash ( facet_method_object * a ) {

	long x, y;
	if ( a->tm_self == NULL )
		x = PyObject_Hash( Py_None );
	else
		x = PyObject_Hash( a->tm_self );
	if ( x == -1 )
		return -1;
	y = PyObject_Hash( a->tm_func );
	if ( y == -1 )
		return -1;
	return x ^ y;
}

//-----------------------------------------------------------------------------
//  Garbage collector traversal method:
//-----------------------------------------------------------------------------

static int
facet_method_traverse ( facet_method_object * tm, visitproc visit,
                        void * arg ) {

    Py_VISIT( tm->tm_func );
    Py_VISIT( tm->tm_self );
    Py_VISIT( tm->tm_facets );
    Py_VISIT( tm->tm_class );
	return 0;
}

//-----------------------------------------------------------------------------
//  Garbage collector object clearing method:
//-----------------------------------------------------------------------------

static int
facet_method_clear ( facet_method_object * tm ) {

    Py_CLEAR( tm->tm_func );
    Py_CLEAR( tm->tm_self );
    Py_CLEAR( tm->tm_facets );
    Py_CLEAR( tm->tm_class );
	return 0;
}

//-----------------------------------------------------------------------------
//  Returns the class name of the class:
//-----------------------------------------------------------------------------

static void
getclassname ( PyObject * class, char * buf, int bufsize ) {

	PyObject * name;

	assert( bufsize > 1 );
	strcpy( buf, "?" ); // Default outcome
	if ( class == NULL )
		return;
	name = PyObject_GetAttrString( class, "__name__" );
	if ( name == NULL ) {
		// This function cannot return an exception:
		PyErr_Clear();
		return;
	}
	if ( PyString_Check( name ) ) {
		strncpy( buf, PyString_AS_STRING( name ), bufsize );
		buf[ bufsize - 1 ] = '\0';
	}
	Py_DECREF( name );
}

//-----------------------------------------------------------------------------
//  Returns the class name of an instance:
//-----------------------------------------------------------------------------

static void
getinstclassname ( PyObject * inst, char * buf, int bufsize ) {

	PyObject *class;

	if ( inst == NULL ) {
		assert( (bufsize > 0) && ((size_t) bufsize > strlen( "nothing" )) );
		strcpy( buf, "nothing" );
		return;
	}

	class = PyObject_GetAttrString( inst, "__class__" );
	if ( class == NULL ) {
		// This function cannot return an exception:
		PyErr_Clear();
		class = (PyObject *)(inst->ob_type);
		Py_INCREF( class );
	}
	getclassname( class, buf, bufsize );
	Py_XDECREF( class );
}

//-----------------------------------------------------------------------------
//  Calls the facet methods and type checks the arguments and result:
//
//  NOTE: This code is no longer functional due to changes in the facets default
//  value encoding (cases 5, 6, 9). These cases have all been merged into a new
//  single case 5. Since this code is not in active use, no effort was made to
//  adapt the code to work with these changes.
//-----------------------------------------------------------------------------

static PyObject *
facet_method_call ( PyObject * meth, PyObject * arg, PyObject * kw ) {

	PyObject     * class,  * result, * self, * new_arg, * func, * value = NULL,
                 * facets, * valid_result, * name = NULL, * dv, * tkw, * tuple;
    facet_object * facet;
	int from, to, ti;
	Py_ssize_t to_args, facets_len, nfacets;
    Py_ssize_t nargs = PyTuple_GET_SIZE( arg );

    // Determine if this is an 'unbound' method call:
    if ( (self = facet_method_GET_SELF( meth )) == NULL ) {
		char clsbuf[256];
		char instbuf[256];
		int  ok;

		// Unbound methods must be called with an instance of the class
        // (or a derived class) as first argument:
        from = 1;
        class = facet_method_GET_CLASS( meth );
		if ( nargs >= 1 ) {
			self = PyTuple_GET_ITEM( arg, 0 );
            assert( self != NULL );
			ok = PyObject_IsInstance( self, class );
            if ( ok > 0 ) {
                to_args = nargs;
                goto build_args;
            } else if ( ok < 0 )
                return NULL;
        }
        func = facet_method_GET_FUNCTION( meth );
		getclassname( class, clsbuf, sizeof( clsbuf ) );
		getinstclassname( self, instbuf, sizeof( instbuf ) );
		PyErr_Format( PyExc_TypeError,
			     "unbound method %s%s must be called with "
			     "%s instance as first argument "
			     "(got %s%s instead)",
                 PyString_AS_STRING( facet_method_GET_NAME( meth ) ),
			     PyEval_GetFuncDesc( func ),
			     clsbuf, instbuf, (self == NULL)? "" : " instance" );
		return NULL;
	}
    from    = 0;
    to_args = nargs + 1;

build_args:
    // Build the argument list, type checking all arguments as needed:
    facets     = facet_method_GET_FACETS( meth );
    facets_len = PyTuple_GET_SIZE( facets );
    nfacets    = facets_len >> 1;
    if ( to_args > nfacets )
        return too_may_args_error( facet_method_GET_NAME( meth ),
                                   nfacets, to_args );
	new_arg = PyTuple_New( nfacets );
	if ( new_arg == NULL )
		return NULL;
	Py_INCREF( self );
	PyTuple_SET_ITEM( new_arg, 0, self );
	for ( to = 1, ti = 3; from < nargs; to++, from++, ti += 2 ) {
		value = PyTuple_GET_ITEM( arg, from );
        assert( value != NULL );
        name  = PyTuple_GET_ITEM( facets, ti );
        facet = (facet_object *) PyTuple_GET_ITEM( facets, ti + 1 );
        if ( kw != NULL ) {
            if ( PyDict_GetItem( kw, name ) != NULL ) {
                Py_DECREF( new_arg );
                return dup_argument_error( facet, meth, from + 1, self,
                                           name );
            }
        }
        if ( facet->validate == NULL ) {
            Py_INCREF( value );
            PyTuple_SET_ITEM( new_arg, to, value );
            continue;
        }
        value = facet->validate( facet, (has_facets_object *) self, name,
                                 value );
        if ( value != NULL ) {
            PyTuple_SET_ITEM( new_arg, to, value );
            continue;
        }
        Py_DECREF( new_arg );
        return argument_error( facet, meth, from + 1, self, name,
                               PyTuple_GET_ITEM( arg, from ) );
	}

    // Substitute default values for any missing arguments:
    for ( ; ti < facets_len; to++, from++, ti += 2 ) {
        facet = (facet_object *) PyTuple_GET_ITEM( facets, ti + 1 );
        if ( kw != NULL ) {
            name  = PyTuple_GET_ITEM( facets, ti );
            value = PyDict_GetItem( kw, name );
            if ( value != NULL ) {
                if ( facet->validate != NULL ) {
                    valid_result = facet->validate( facet,
                                     (has_facets_object *) self, name, value );
                    if ( valid_result == NULL ) {
                        Py_DECREF( new_arg );
                        return keyword_argument_error( facet, meth, self, name,
                                                       value );
                    }
                    value = valid_result;
                } else
                    Py_INCREF( value );
                PyTuple_SET_ITEM( new_arg, to, value );
                if ( PyDict_DelItem( kw, name ) < 0 ) {
                    Py_DECREF( new_arg );
                    return NULL;
                }
                continue;
            }
        }
        switch ( facet->default_value_type ) {
            case 0:
                value = facet->default_value;
                Py_INCREF( value );
                break;
            case 1:
                Py_DECREF( new_arg );
                return missing_argument_error( facet, meth, from + 1, self,
                                              PyTuple_GET_ITEM( facets, ti ) );
            case 2:
                value = (PyObject *) self;
                Py_INCREF( value );
                break;
            case 3:
            case 5:  // Invalid: See NOTE above...
                value = PySequence_List( facet->default_value );
                if ( value == NULL ) {
                    Py_DECREF( new_arg );
                    return NULL;
                }
                break;
            case 4:
            case 6:  // Invalid: See NOTE above...
                value = PyDict_Copy( facet->default_value );
                if ( value == NULL ) {
                    Py_DECREF( new_arg );
                    return NULL;
                }
                break;
            case 7:
                dv  = facet->default_value;
                tkw = PyTuple_GET_ITEM( dv, 2 );
                if ( tkw == Py_None )
                    tkw = NULL;
                value = PyObject_Call( PyTuple_GET_ITEM( dv, 0 ),
                                       PyTuple_GET_ITEM( dv, 1 ), tkw );
                if ( value == NULL ) {
                    Py_DECREF( new_arg );
                    return NULL;
                }
                break;
            case 8:
                if ( (tuple = PyTuple_New( 1 )) == NULL ) {
                    Py_DECREF( new_arg );
                    return NULL;
                }
                PyTuple_SET_ITEM( tuple, 0, self );
                Py_INCREF( self );
                Py_INCREF( tuple );
                value = PyObject_Call( facet->default_value, tuple, NULL );
                Py_DECREF( tuple );
                if ( value == NULL ) {
                    Py_DECREF( new_arg );
                    return NULL;
                }
                if ( facet->validate != NULL ) {
                    result = facet->validate( facet,
						         (has_facets_object *) self, name, value );
                    Py_DECREF( value );
                    if ( result == NULL ) {
                        Py_DECREF( new_arg );
                        return NULL;
                    }
                    value = result;
                }
                break;
            // case 9:  Missing: See NOTE above...
        }
		PyTuple_SET_ITEM( new_arg, to, value );
    }

    // Invoke the method:
	result = PyObject_Call( facet_method_GET_FUNCTION( meth ), new_arg, kw );
	Py_DECREF( new_arg );

    // Type check the method result (if valid and it was requested):
    if ( result != NULL ) {
        facet = (facet_object *) PyTuple_GET_ITEM( facets, 0 );
        if ( facet->validate != NULL ) {
            valid_result = facet->validate( facet, (has_facets_object *) self,
                                            Py_None, result );
            if ( valid_result != NULL ) {
                Py_DECREF( result );
                return valid_result;
            }
            invalid_result_error( facet, meth, self, result );
            Py_DECREF( result );
            return NULL;
        }
    }

    // Finally, return the result:
	return result;
}

//-----------------------------------------------------------------------------
//  'get' handler that converts from 'unbound' to 'bound' method:
//-----------------------------------------------------------------------------

static PyObject *
facet_method_descr_get ( PyObject * meth, PyObject * obj, PyObject * cls ) {

	return create_facet_method( facet_method_GET_NAME( meth ),
	                            facet_method_GET_FUNCTION( meth ),
                                (obj == Py_None)? NULL: obj,
                                facet_method_GET_FACETS( meth ), cls );
}

//-----------------------------------------------------------------------------
//  Descriptors for facet method attributes:
//-----------------------------------------------------------------------------

static PyMemberDef facet_method_memberlist[] = {
    { "tm_name",     T_OBJECT,   OFF( tm_name ),    READONLY | RESTRICTED,
      "the name of the method" },
    { "tm_func",     T_OBJECT,   OFF( tm_func ),    READONLY | RESTRICTED,
      "the function (or other callable) implementing a method" },
    { "tm_self",     T_OBJECT,   OFF( tm_self ),    READONLY | RESTRICTED,
      "the instance to which a method is bound; None for unbound methods" },
    { "tm_facets",   T_OBJECT,   OFF( tm_facets ),  READONLY | RESTRICTED,
      "the facets associated with a method" },
    { "tm_class",    T_OBJECT,   OFF( tm_class ),   READONLY | RESTRICTED,
      "the class associated with a method" },
    { NULL }	// Sentinel
};

//-----------------------------------------------------------------------------
//  'CFacetMethod' __doc__ string:
//-----------------------------------------------------------------------------

PyDoc_STRVAR( facet_method_doc,
"facetmethod(function, facets)\n\
\n\
Create a type checked instance method object.");

//-----------------------------------------------------------------------------
//  'CFacetMethod' type definition:
//-----------------------------------------------------------------------------

static PyTypeObject facet_method_type = {
	PyObject_HEAD_INIT( DEFERRED_ADDRESS( &PyType_Type ) )
	0,
	"facetmethod",
	sizeof( facet_method_object ),
	0,
	(destructor) facet_method_dealloc,               // tp_dealloc
	0,                                               // tp_print
	0,                                               // tp_getattr
	0,                                               // tp_setattr
	(cmpfunc) facet_method_compare,                  // tp_compare
	(reprfunc) facet_method_repr,                    // tp_repr
	0,                                               // tp_as_number
	0,                                               // tp_as_sequence
	0,                                               // tp_as_mapping
	(hashfunc) facet_method_hash,                    // tp_hash
	facet_method_call,                               // tp_call
	0,                                               // tp_str
	(getattrofunc) facet_method_getattro,            // tp_getattro
    DEFERRED_ADDRESS( PyObject_GenericSetAttr ),     // tp_setattro
	0,					                             // tp_as_buffer
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,         // tp_flags
	facet_method_doc,                                // tp_doc
	(traverseproc) facet_method_traverse,            // tp_traverse
	(inquiry) facet_method_clear,                    // tp_clear
	0,                                               // tp_richcompare
 	offsetof( facet_method_object, tm_weakreflist ), // tp_weaklistoffset
	0,				                                 // tp_iter
	0,				                                 // tp_iternext
	0,				                                 // tp_methods
    facet_method_memberlist,                         // tp_members
	0,				                                 // tp_getset
	0,				                                 // tp_base
	0,				                                 // tp_dict
	facet_method_descr_get,  	                     // tp_descr_get
	0,					                             // tp_descr_set
	0,					                             // tp_dictoffset
	0,					                             // tp_init
	0,					                             // tp_alloc
	facet_method_new,		                         // tp_new
};

//-----------------------------------------------------------------------------
//  Performs module and type initialization:
//-----------------------------------------------------------------------------

PyMODINIT_FUNC
initcfacets ( void ) {

    PyObject * tmp;

    // Create the 'cfacets' module:
	PyObject * module = Py_InitModule3( "cfacets", cfacets_methods,
                                        cfacets__doc__ );
	if ( module == NULL )
		return;

	// Create the 'CHasFacets' type:
	if ( PyType_Ready( &has_facets_type ) < 0 )
		return;

	Py_INCREF( &has_facets_type );
	if ( PyModule_AddObject( module, "CHasFacets",
                             (PyObject *) &has_facets_type ) < 0 )
        return;

	// Create the 'CFacet' type:
	facet_type.tp_new = PyType_GenericNew;
	if ( PyType_Ready( &facet_type ) < 0 )
		return;

	Py_INCREF( &facet_type );
	if ( PyModule_AddObject( module, "cFacet",
                             (PyObject *) &facet_type ) < 0 )
        return;

	// Create the 'CFacetNotification' type:
	facet_notification_type.tp_new = PyType_GenericNew;
	if ( PyType_Ready( &facet_notification_type ) < 0 )
		return;

	Py_INCREF( &facet_notification_type );
	if ( PyModule_AddObject( module, "CFacetNotification",
                             (PyObject *) &facet_notification_type ) < 0 )
	    return;

	// Create the 'CFacetMethod' type:
	if ( PyType_Ready( &facet_method_type ) < 0 )
		return;

	Py_INCREF( &facet_method_type );
	if ( PyModule_AddObject( module, "CFacetMethod",
                             (PyObject *) &facet_method_type ) < 0 )
	    return;

	// Create the 'HasFacetsMonitor' list:
	tmp = PyList_New( 0 );
	Py_INCREF( tmp );
	if ( PyModule_AddObject( module, "_HasFacets_monitors",
				 (PyObject*) tmp) < 0 )
	    return;

	_HasFacets_monitors = tmp;

    // Predefine a Python string == "__class_facets__":
    class_facets = PyString_FromString( "__class_facets__" );

    // Predefine a Python string == "__listener_facets__":
    listener_facets = PyString_FromString( "__listener_facets__" );

    // Predefine a Python string == "editor":
    editor_property = PyString_FromString( "editor" );

    // Predefine a Python string == "__prefix__":
    class_prefix = PyString_FromString( "__prefix__" );

    // Predefine a Python string == "facet_added":
    facet_added = PyString_FromString( "facet_added" );

    // Predefine the CFacetNotification type strings:
    fn_event = PyString_FromString( "event" );
    fn_item  = PyString_FromString( "item" );
    fn_list  = PyString_FromString( "list" );
    fn_set   = PyString_FromString( "set" );
    fn_dict  = PyString_FromString( "dict" );

    // Create an empty tuple:
    empty_tuple = PyTuple_New( 0 );

    // Create the 'is_callable' marker:
    is_callable = PyInt_FromLong( -1 );

    // Create the 'item' index value:
    fn_item_index = PyInt_FromLong( 0 );
}

//-- EOF ----------------------------------------------------------------------
