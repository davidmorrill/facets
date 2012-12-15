"""
Defines a Python shell tool for interacting with the local variables in the
currently selected frame in FBI debugging context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import SingletonHasPrivateFacets, Constant, Str, View, Item, ShellEditor

from facets.extra.helper.fbi \
    import FBI

#-------------------------------------------------------------------------------
#  'LocalVariablesShell' class:
#-------------------------------------------------------------------------------

class LocalVariablesShell ( SingletonHasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Local Variables Shell' )

    # Reference to the FBI debugger context:
    fbi = Constant( FBI() )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'object.fbi.frame_locals',
              show_label = False,
              editor     = ShellEditor( share = True )
        )
    )

#-- EOF ------------------------------------------------------------------------