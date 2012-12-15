"""
Defines the PathItem class used by the VIP Shell as a base class used to
represent file system objects.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from labeled_item \
    import LabeledItem

#-------------------------------------------------------------------------------
#  'PathItem' class:
#-------------------------------------------------------------------------------

class PathItem ( LabeledItem ):
    """ A labeled item that displays file path based information.
    """

    #-- Facet Definitions ------------------------------------------------------

    type       = 'file'
    icon       = '@facets:shell_file'
    color_code = '\x006'

    #-- Public Methods ---------------------------------------------------------

    def label_value_for_1 ( self ):
        return self.shell.colorize( self.add_id( self.item ) )


    def label_value_for_2 ( self ):
        return self.label_value_for_1()

#-- EOF ------------------------------------------------------------------------
