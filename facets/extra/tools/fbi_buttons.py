"""
Defines a tool for allowing the developer to control the FBI debugging context
by clicking 'run', 'step', ... buttons.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import SingletonHasPrivateFacets, Str, Constant, Property, Button, View, \
           HToolbar, Item, property_depends_on

from facets.extra.helper.themes \
    import TButton

from facets.extra.helper.fbi \
    import FBI

#-------------------------------------------------------------------------------
#  'FBIButtons' class:
#-------------------------------------------------------------------------------

class FBIButtons ( SingletonHasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'FBI Buttons' )

    # Reference to the FBI debugger context:
    fbi = Constant( FBI() )

    # Has the FBI debugging environment been initialized yet?
    initialized = Property

    # Is the FBI debugger context live (i.e. application is suspended)?
    is_live = Property

    # Is the FBI debugger context active (i.e. in an event loop)?
    is_active = Property

    # The debugger 'Start' button:
    start = Button( 'Start', image       = '@facets:fbi_quit',
                             orientation = 'horizontal' )

    # The debugger 'Step' button:
    step = Button( 'Step', image       = '@facets:fbi_step',
                           orientation = 'horizontal' )

    # The debugger 'Next' button:
    next = Button( 'Next', image       = '@facets:fbi_next',
                           orientation = 'horizontal' )

    # The debugger 'Return' button:
    ret = Button( 'Return', image       = '@facets:fbi_return',
                            orientation = 'horizontal' )

    # The debugger 'Go' button:
    go = Button( 'Go', image       = '@facets:fbi_go',
                       orientation = 'horizontal' )

    # The debugger 'Quit' button:
    quit = Button( 'Quit', image       = '@facets:fbi_quit',
                           orientation = 'horizontal' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HToolbar(
            TButton( 'start',
                     label        = 'Start',
                     image        = '@facets:fbi_quit',
                     width        = 80,
                     enabled_when = 'not initialized' ),
            TButton( 'step',
                     label        = 'Step',
                     image        = '@facets:fbi_step',
                     width        = 80,
                     enabled_when = 'is_live' ),
            TButton( 'next',
                     label        = 'Next',
                     image        = '@facets:fbi_next',
                     width        = 80,
                     enabled_when = 'is_live' ),
            TButton( 'ret',
                     label        = 'Return',
                     image        = '@facets:fbi_return',
                     width        = 80,
                     enabled_when = 'is_live' ),
            TButton( 'go',
                     label        = 'Go',
                     image        = '@facets:fbi_go',
                     width        = 80,
                     enabled_when = 'is_active' ),
            TButton( 'quit',
                     label        = 'Quit',
                     image        = '@facets:fbi_quit',
                     width        = 80,
                     enabled_when = 'is_active' ),
            Item( 'object.fbi.msg',
                  style      = 'readonly',
                  show_label = False
            ),
            id = 'toolbar'
        ),
        id = 'facets.extra.tools.fbi_buttons.FBIButtons'
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'fbi:initialized' )
    def _get_initialized ( self ):
        return self.fbi.initialized


    @property_depends_on( 'fbi:debug_frame' )
    def _get_is_live ( self ):
        return (self.fbi.debug_frame is not None)


    @property_depends_on( 'fbi:active' )
    def _get_is_active ( self ):
        return self.fbi.active

    #-- Facet Event Handlers ---------------------------------------------------

    def _start_set ( self ):
        """ Handles the 'Start' button being clicked.
        """
        self.fbi.start()


    def _step_set ( self ):
        """ Handles the 'Step' button being clicked.
        """
        self.fbi.step()


    def _next_set ( self ):
        """ Handles the 'Next' button being clicked.
        """
        self.fbi.next()


    def _ret_set ( self ):
        """ Handles the 'Return' button being clicked.
        """
        self.fbi.return_()


    def _go_set ( self ):
        """ Handles the 'Go' button being clicked.
        """
        self.fbi.go()


    def _quit_set ( self ):
        """ Handles the 'Quit' button being clicked.
        """
        self.fbi.quit()

#-- EOF ------------------------------------------------------------------------