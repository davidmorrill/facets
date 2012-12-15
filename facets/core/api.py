"""
Pseudo-package for all of the core symbols from the Facets core (no UI).
Use this module for importing Facets names into your namespace. For example::

    from facets.core_api \
        import HasFacets
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

from facets_version \
    import __version__

from facet_base \
    import Uninitialized, Undefined, Missing, Self, python_version, inn

from facets_config \
    import facets_config

from facet_errors \
    import FacetError, FacetNotificationError, DelegationError

from facet_notifiers \
   import push_exception_handler, pop_exception_handler, FacetSetWrapper

from category \
    import Category

from facet_defs \
    import CFacet, Facet, Property, FacetFactory, Default, Color, RGBColor, Font

from facet_types                                                               \
    import Any, Generic, Int, Long, Float, Complex, Str, Title, Unicode, Bool, \
           CInt, CLong, CFloat, CComplex, CStr, CUnicode, CBool, String,       \
           Regex, Code, HTML, Password, Callable, This, self, Function,        \
           Method, Class, Module, Python, ReadOnly, Disallow, missing,         \
           Constant, Delegate, DelegatesTo, PrototypedFrom, Expression,        \
           PythonValue, File, Directory, Range, Enum, Tuple, List, CList,      \
           Set, CSet, Dict, Instance, AdaptedTo, AdaptsTo, Event, Button,      \
           ToolbarButton, Either, Type, Symbol, WeakRef, false, true, undefined

from facet_types                                                               \
    import ListInt, ListFloat, ListStr, ListUnicode, ListComplex, ListBool,    \
           ListFunction, ListMethod, ListClass, ListInstance, ListThis,        \
           DictStrAny, DictStrStr, DictStrInt, DictStrLong, DictStrFloat,      \
           DictStrBool, DictStrList

from facet_types                                                               \
    import BaseInt, BaseLong, BaseFloat, BaseComplex, BaseStr, BaseUnicode,    \
           BaseBool, BaseCInt, BaseCLong, BaseCFloat, BaseCComplex, BaseCStr,  \
           BaseCUnicode, BaseCBool, BaseRange, BaseEnum, BaseTuple, BaseInstance

from color_facets \
    import RGB, RGBA, RGBInt, RGBAInt, RGBFloat, RGBAFloat, HLS, HLSA

if python_version >= 2.5:
    from facet_types \
        import UUID

from has_facets                                                                \
    import method, HasFacets, HasStrictFacets, HasPrivateFacets, Interface,    \
           SingletonHasFacets, SingletonHasStrictFacets,                       \
           SingletonHasPrivateFacets, MetaHasFacets, Vetoable, VetoableEvent,  \
           implements, facets_super, on_facet_set, cached_property,            \
           property_depends_on

from facet_handlers                                                            \
    import BaseFacetHandler, FacetType, FacetHandler, FacetCoerceType,         \
           FacetCastType, ThisClass, FacetPrefixList, FacetMap,                \
           FacetPrefixMap, FacetCompound, NO_COMPARE, OBJECT_IDENTITY_COMPARE, \
           RICH_COMPARE

from facet_collections                                                         \
    import FacetListObject, FacetListEvent, FacetDictObject, FacetDictEvent,   \
           FacetSetObject, FacetSetEvent

from facet_value \
    import BaseFacetValue, FacetValue, SyncValue, TypeValue, DefaultValue

from adapter \
    import Adapter, adapts

from facet_numeric \
    import Array, CArray

#-- EOF ------------------------------------------------------------------------