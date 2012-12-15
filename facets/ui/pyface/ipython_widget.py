"""
The implementation of an IPython shell.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

# Import the toolkit specific version:
try:
    import IPython.frontend
except ImportError:
    raise ImportError, '''
________________________________________________________________________________
Could not load the Wx frontend for ipython.
You need to have ipython >= 0.9 installed to use the ipython widget.'''


from toolkit \
    import toolkit_object

#-------------------------------------------------------------------------------
#  Define the GUI toolkit specific implementation:
#-------------------------------------------------------------------------------

IPythonWidget = toolkit_object( 'ipython_widget:IPythonWidget' )

#-- EOF ------------------------------------------------------------------------