"""
Define the 'toolkit' interface for accessing GUI toolkit specific
implementations using a GUI toolkit neutral interface.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from facets.core.facets_config \
    import facets_config

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# This is set to the root part of the module path for the selected backend:
_toolkit_backend = None

#-------------------------------------------------------------------------------
#  Module Functions:
#-------------------------------------------------------------------------------

def _init_toolkit ( ):
    """ Initialise the current toolkit.
    """
    # Toolkits to check for if none is explicitly specified:
    known_toolkits = ( 'qt4', 'wx', 'null' )

    # Get the toolkit:
    toolkit = facets_config.toolkit

    if toolkit:
        toolkits = ( toolkit, )
    else:
        toolkits = known_toolkits

    for tk in toolkits:
        # Try and import the toolkit's pyface backend init module:
        be = 'facets.ui.%s.pyface.' % tk

        try:
            __import__( be + 'init' )
            break
        except ImportError:
            pass
    else:
        # Try to import the null toolkit but don't set the facets_config
        # toolkit:
        try:
            be = 'facets.ui.null.pyface.'
            __import__( be + 'init' )
            import warnings
            warnings.warn( "Unable to import the %s backend for pyface; using "
                           "the 'null' toolkit instead." )
        except:
            if toolkit:
                raise ImportError(
                    "Unable to import a pyface backend for the %s toolkit" %
                    toolkit
                )
            else:
                raise ImportError(
                    ("Unable to import a pyface backend for any of the %s "
                     "toolkits") % ", ".join( known_toolkits )
                 )

    # In case we have just decided on a toolkit, tell everybody else:
    facets_config.toolkit = tk

    # Save the imported toolkit module:
    global _toolkit_backend
    _toolkit_backend = be


# Do this once then disappear:
_init_toolkit()
del _init_toolkit


def toolkit_object ( name ):
    """ Return the toolkit specific object with the given name.  The name
        consists of the relative module path and the object name separated by a
        colon.
    """
    mname, oname = name.split( ':' )
    be_mname     = _toolkit_backend + mname

    try:
        __import__( be_mname )

        try:
            return getattr( sys.modules[ be_mname ], oname )
        except AttributeError:
            pass

    except ImportError:
        pass

    class Unimplemented ( object ):
        """ This is returned if an object isn't implemented by the selected
            toolkit.  It raises an exception if it is ever instantiated.
        """

        def __init__ ( self, *args, **kwargs ):
            raise NotImplementedError(
                "The %s pyface backend doesn't implement %s" %
                ( facets_config.toolkit, oname )
            )

    return Unimplemented

#-- EOF ------------------------------------------------------------------------