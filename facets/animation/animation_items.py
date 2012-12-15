"""
Defines the AnimationItems class that provides an abstract base class for
managing collections of animatable items.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import List

from i_animatable \
    import IAnimatable

from base_animation \
   import BaseAnimation

#-------------------------------------------------------------------------------
#  'AnimationItems' class:
#-------------------------------------------------------------------------------

class AnimationItems ( BaseAnimation ):
    """ Defines the AnimationItems class that provides an abstract base class
        for managing collections of animatable items.
    """

    # The collection of animatable items being managed:
    items = List( IAnimatable )

#-- EOF ------------------------------------------------------------------------
