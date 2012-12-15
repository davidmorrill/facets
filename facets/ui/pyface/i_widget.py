"""
The base interface for all pyface widgets.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Any, Interface

#-------------------------------------------------------------------------------
#  'IWidget' class:
#-------------------------------------------------------------------------------

class IWidget ( Interface ):
    """ The base interface for all pyface widgets.

        Pyface widgets delegate to a toolkit specific control.
    """

    #-- 'IWidget' interface ----------------------------------------------------

    # The toolkit specific control that represents the widget.
    control = Any

    # The control's optional parent control.
    parent = Any

    #-- 'IWidget' Interface ----------------------------------------------------

    def destroy ( self ):
        """ Destroy the control if it exists.
        """

    #-- Protected 'IWidget' Interface ------------------------------------------

    def _create ( self ):
        """ Creates the toolkit specific control.
        """


    def _create_control ( self, parent ):
        """ Create and return the toolkit specific control that represents the
            widget.
        """

#-------------------------------------------------------------------------------
#  'MWidget' class:
#-------------------------------------------------------------------------------

class MWidget ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IWidget interface.

        Implements: _create()
    """

    #-- Protected 'IWidget' Interface ------------------------------------------

    def _create ( self ):
        self.control = self._create_control( self.parent )


    def _create_control ( self, parent ):
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------