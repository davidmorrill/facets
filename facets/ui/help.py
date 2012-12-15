"""
Defines the help interface for displaying the help associated with a Facets UI
View object.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  Function Definitions:
#-------------------------------------------------------------------------------

def default_show_help ( info, control ):
    """ Default handler for showing the help associated with a view.
    """
    toolkit().show_help( info.ui, control )


# The default handler for showing help
show_help = default_show_help


def on_help_call ( new_show_help = None ):
    """ Sets a new global help provider function.

        Parameters
        ----------
        new_show_help : function
            The function to set as the new global help provider

        Returns
        -------
        The previous global help provider function

        Description
        -----------
        The help provider function must have a signature of
        *function*(*info*, *control*), where *info* is a UIInfo object for the
        current view, and *control* is the UI control that invokes the function
        (typically, a **Help** button). It is provided in case the help provider
        needs to position the help window relative to the **Help** button.

        To retrieve the current help provider function, call this function with
        no arguments.
    """
    global show_help

    result = show_help
    if new_show_help is not None:
        show_help = new_show_help

    return result

#-- EOF ------------------------------------------------------------------------