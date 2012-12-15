"""
Creates a GUI toolkit neutral "wizard"-style user interface for a specified UI
object which allows a user to be guided through a series of sub-views.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Any, Int, List, Button, Property, View, \
           VGroup, HGroup, Item, Handler, spring

from view_element \
    import ViewSubElement

#-------------------------------------------------------------------------------
#  'ui_wizard' function:
#-------------------------------------------------------------------------------

def ui_wizard ( ui, parent ):
    """ Creates a GUI toolkit neutral "wizard"-style user interface for a
        specified UI object which allows a user to be guided through a series of
        sub-views.
    """
    Wizard( ui = ui ).edit_facets( parent = parent )

#-------------------------------------------------------------------------------
#  'WizardPage' class:
#-------------------------------------------------------------------------------

class WizardPage ( HasPrivateFacets ):
    """ Defines a single "page" within a wizard dialog.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The wizard this page is part of:
    wizard = Any # Instance( Wizard )

    # The view sub-element defining the content of this wizard page:
    element = Instance( ViewSubElement )

    # The enabled_when expression for this page:
    enabled_when = Any

    # The defined_when expression for this page:
    defined_when = Any

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        """ Returns the view to use for this wizard page.
        """
        return View( self.element )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        """ Complete the object initialization.
        """
        self.enabled_when = self._init_when( 'enabled_when', 'True'  )
        self.defined_when = self._init_when( 'defined_when', 'False' )


    def facet_context ( self ):
        """ Returns the default context to use for editing or configuring
            facets.
        """
        context = self.wizard.context.copy()
        del context[ 'handler' ]

        return context

    #-- Private Methods --------------------------------------------------------

    def _init_when ( self, name, default ):
        """ Returns a compiled 'when' clause for the specified conditional
            element value specified by *name". If the *name* clause has no
            value, then the value specified by *default* is used.
        """
        when = getattr( self.element, name ) or default
        setattr( self.element, name, '' )

        try:
            return compile( when, '<string>', 'eval' )
        except:
            return compile( default, '<string>', 'eval' )

#-------------------------------------------------------------------------------
#  'Wizard' class:
#-------------------------------------------------------------------------------

class Wizard ( Handler ):
    """ Defines the collection of pages displayed by a wizard view.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The original UI object this wizard was created from:
    ui = Any # Instance( UI )

    # The UIInfo object associated with this wizard handler:
    info = Any # Instance( UIInfo )

    # The modified version of the original UI context used while the wizard is
    # being displayed:
    context = Any # Dict( Str, Any )

    # The list of all wizard pages to be displayed:
    pages = List # ( Instance( WizardPage ) )

    # The current wizard page being displayed:
    page = Instance( WizardPage )

    # The indices of the pages the wizard has already visited:
    indices = List

    # The index of the current wizard page being displayed:
    index = Int

    # The event fired when the previous wizard page should be displayed:
    previous = Button( 'Previous' )

    # The event fired when the next wizard page should be displayed:
    next = Button( 'Next' )

    # The event fired when the wizard is finished:
    finish = Button( 'Finish' )

    # Does the current page have a previous wizard page?
    has_previous = Property

    # Does the current page have an enabled next wizard page?
    has_next = Property

    # Does the current page allow the wizard to be finished?
    has_finish = Property

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        view = self.ui.view

        return View(
            VGroup(
                VGroup(
                    Item( 'handler.page',
                          style     = 'custom',
                          resizable = True
                    ),
                    show_labels = False
                ),
                '_',
                HGroup(
                    spring,
                    Item( 'handler.previous',
                          enabled_when = 'handler.has_previous'
                    ),
                    Item( 'handler.next',
                          enabled_when = 'handler.has_next'
                    ),
                    Item( 'handler.finish',
                          enabled_when = 'handler.has_finish'
                    ),
                    show_labels = False
                ),
                show_labels = False
            ),
            kind   = 'livemodal',
            title  = view.title,
            id     = view.id,
            width  = view.width,
            height = view.height
        )

    #-- Facet Default Values ---------------------------------------------------

    def _context_default ( self ):
        context = self.ui.context
        result  = {}

        for name, value in context.iteritems():
            if name != 'handler':
                result[ name ] = value.clone_facets()

        return result


    def _pages_default ( self ):
        result  = []
        content = self.ui.view.content.content
        if (len( content ) == 1) and (len( content[0].content ) > 1):
            content = content[0].content

        for element in content:
            result.append( WizardPage( wizard = self, element = element ) )

        return result


    def _page_default ( self ):
        return self.pages[ self.index ]

    #-- Property Implementations -----------------------------------------------

    def _get_has_previous ( self ):
        return (len( self.indices ) > 0)


    def _get_has_next ( self ):
        global_context = globals()
        local_context  = self.info.ui._get_context()
        for i in xrange( self.index + 1, len( self.pages ) ):
            page = self.pages[ i ]
            try:
                if eval( page.enabled_when, global_context, local_context ):
                    return True
            except:
                # fixme: Should the exception be logged somewhere?
                pass

        return False


    def _get_has_finish ( self ):
        try:
            return ((self.index == (len( self.pages ) - 1)) or
                    eval( self.page.defined_when, globals(),
                          self.info.ui._get_context() ))
        except:
            # fixme: Should the exception be logged somewhere?
            pass

        return False

    #-- Facet Event Handlers ---------------------------------------------------

    def _previous_set ( self ):
        """ Handles the 'previous' event being fired.
        """
        self.index = self.indices.pop()


    def _next_set ( self ):
        """ Handles the 'next' event being fired.
        """
        global_context = globals()
        local_context  = self.info.ui._get_context()
        for i in xrange( self.index + 1, len( self.pages ) ):
            page = self.pages[ i ]
            try:
                if eval( page.enabled_when, global_context, local_context ):
                    self.indices.append( self.index )
                    self.index = i

                    break
            except:
                # fixme: Should the exception be logged somewhere?
                pass


    def _finish_set ( self ):
        """ Handles the 'finish' event being fired.
        """
        context = self.info.ui.context
        for name, value in self.ui.context.iteritems():
            if name != 'handler':
                value.copy_facets( context[ name ] )

        self.info.ui.dispose( True )


    def _index_set ( self, index ):
        """ Handles the 'index' facet being changed.
        """
        self.page = self.pages[ index ]

    #-- HasFacets Method Overrides ---------------------------------------------

    def facet_context ( self ):
        """ Returns the default context to use for editing or configuring
            facets.
        """
        return self.context

    #-- Handler Method Overrides -----------------------------------------------

    def init_info ( self, info ):
        self.info = info

#-- EOF ------------------------------------------------------------------------
