"""
Defines the ViewCommand shell command that allows the default Facets view for a
specified object to be displayed in-line within the shell history.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets

from facets.ui.vip_shell.items.view_item \
    import ViewItem

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The help message for the command:
HELP = """
Adds the default facets view for the [[options]] object to the shell history.
[[Options]] should be a Python expression that evaluates to a HasFacets object.
The [[options]] can also specify an initial height for the view, using the form:
[[object, height]] (e.g. <<myobject, 300>>).
"""[1:-1]

#-------------------------------------------------------------------------------
#  'ViewCommand' class:
#-------------------------------------------------------------------------------

class ViewCommand ( ShellCommand ):
    """ Defines the 'view' shell command.
    """

    summary = 'Displays the default Facets view for the [[options]] object.'
    help    = HELP
    options_type = 'expression'


    def execute ( self ):
        """ Analyzes and validates the options, then displays the requested
            view.
        """
        if self.options == '':
            print 'A Python expression must be provided.'
        else:
            object = self.evaluate()
            view   = None
            height = -1
            if isinstance( object, tuple ):
                for element in object:
                    if isinstance( element, HasFacets ):
                        object = element
                    elif isinstance( element, int ):
                        height = element
                    else:
                        view = element

            if not isinstance( object, HasFacets ):
                print 'The expression must evaluate to a HasFacets object.'
            else:
                return self.shell.history_item_for(
                    ViewItem, object, height = height, view = view, lod = 1
                )

#-- EOF ------------------------------------------------------------------------
