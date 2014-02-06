"""
# VIPShellEditor Demo #

This example demonstrates using the **VIPShellEditor**, which provides a
*Visual Interactive Python* shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Any, View, Item, VIPShellEditor

#-- VIPShellDemo class ---------------------------------------------------------

class VIPShellDemo ( HasPrivateFacets ):

    # The 'locals' dictionary for the shell:
    values = Any( {} )

    view = View(
       Item( 'values',
             id         = 'values',
             show_label = False,
             editor     = VIPShellEditor( share = True )
        ),
        id = 'facets.extra.demo.ui.Advanced.VIPShell_editor_demo'
    )

#-- Create the demo ------------------------------------------------------------

demo = VIPShellDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
