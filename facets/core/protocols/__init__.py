"""
Trivial Interfaces and Adaptation from PyProtocols.

This package is a direct copy of a subset of the files from Phillip J. Eby's
PyProtocols package. They are only included here to help remove dependencies
on external packages from the Facets package.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

from api \
    import *

from adapters \
    import NO_ADAPTER_NEEDED, DOES_NOT_SUPPORT, Adapter, StickyAdapter

from adapters \
    import AdaptationFailure

from interfaces \
    import *

from advice \
    import metamethod, supermeta

from classic \
    import ProviderMixin

from generate \
    import protocolForType, protocolForURI

from generate \
    import sequenceOf, IBasicSequence

#-- EOF ------------------------------------------------------------------------