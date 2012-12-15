"""
Defines the LabeledItem class used as a base class for all VIP Shell items that
display data using a theme having a label as well as a content area.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str

from generated_item \
    import GeneratedItem

#-------------------------------------------------------------------------------
#  'LabeledItem' class:
#-------------------------------------------------------------------------------

class LabeledItem ( GeneratedItem ):
    """ An item that has a separate label from its content when expanded.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The contents of the item:
    item_contents = Str

    # The label for the item:
    item_label = Str

    #-- Public Methods ---------------------------------------------------------

    def text_value_for_0 ( self ):
        """ Returns the text to display for level of detail 0.
        """
        return self.display( self.item_label )


    def label_value_for_1 ( self ):
        return self.shell.colorize( self.add_id( self.item_label ) )


    def label_value_for_2 ( self ):
        return self.shell.colorize( self.add_id( self.item_label ) )


    def display_for_1 ( self, item ):
        return self.shell.colorize( self.add_line_numbers( item ) )


    def display_for_2 ( self, item ):
        return self.shell.colorize( self.add_line_numbers( item ) )


    def label_image_value_for_1 ( self ):
        return self.image_value()


    def label_image_value_for_2 ( self ):
        return self.image_value()


    def image_value_for_1 ( self ):
        return None


    def image_value_for_2 ( self ):
        return None


    def str ( self, item ):
        """ Returns the string value of *item*.
        """
        return self.item_contents

#-- EOF ------------------------------------------------------------------------
