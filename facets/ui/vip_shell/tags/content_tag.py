"""
Defines the ContentTag class used to dynamically include or exclude content from
its containing shell item.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Bool, Int, Property

from shell_tag \
    import ShellTag

#-------------------------------------------------------------------------------
#  'ContentTag' class:
#-------------------------------------------------------------------------------

class ContentTag ( ShellTag ):
    """ Defines the ContentTag class used to dynamically include or exclude
        content from its containing shell item.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The content the tag can dynamically add to its containing shell item:
    content = Str

    # The current content the tag adds to its containing shell item:
    text = Property

    # Is the dynamic content currently enabled?
    enabled = Bool( False )

    # The minimum 'lod' setting for its containing shell item that will
    # auto-enable the content:
    auto_lod = Int( 2 )

    #-- Public Methods ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left-clicking on the tag.
        """
        self.enabled = not self.enabled

    #-- Property Implementations -----------------------------------------------

    def _get_text ( self ):
        if self.enabled or (self.auto_lod <= self.shell_item.lod):
            return self.content

        return ''

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self ):
        self.shell_item.reset = True

#-- EOF ------------------------------------------------------------------------
