"""
A custom editor for grabbing GUI toolkit neutral 'control' objects.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Event, Instance, Str, Control, Image, Editor, BasicEditorFactory, \
           on_facet_set

from facets.ui.controls.themed_control \
    import ThemedControl

#-------------------------------------------------------------------------------
#  'ControlGrabber' class:
#-------------------------------------------------------------------------------

class ControlGrabber ( ThemedControl ):
    """ Defines a control that can be used to "grab" other controls.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The most recent control selected:
    selected = Event # Instance( Control )

    # The most recent window the mouse pointer passed over:
    over = Instance( Control )

    # The image to be drawn inside the control:
    image = Image( '@facets:control_grabber_inactive' )

    # The image to display when inactive:
    image_inactive = Image( '@facets:control_grabber_inactive' )

    # The image to display when the mouse is hovering over the editor:
    image_hover = Image( '@facets:control_grabber_hover' )

    # The image to display when active but not over a valid control:
    image_tracking = Image( '@facets:control_grabber_tracking' )

    # The image to display when active and over a valid control:
    image_locked = Image( '@facets:control_grabber_locked' )

    #-- Mouse Event Handlers ---------------------------------------------------

    def normal_enter ( self, x, y, event ):
        self.image = self.image_hover


    def normal_leave ( self, x, y, event ):
        self.image = self.image_inactive


    def normal_left_down ( self, x, y, event ):
        self.state          = 'tracking'
        self.image          = self.image_tracking
        self.control.cursor = 'question'


    def tracking_left_up ( self, x, y, event ):
        self.state          = 'normal'
        self.selected       = self._get_control_at( x, y )
        self.image          = self.image_inactive
        self.control.cursor = None


    def tracking_motion ( self, x, y, event ):
        self.over = self._get_control_at( x, y )
        if self.over is None:
            self.image = self.image_tracking
        else:
            self.image = self.image_locked

    #-- Private Methods --------------------------------------------------------

    def _get_control_at ( self, x, y ):
        """ Locates the control at the specified control coordinates (if any).
        """
        control = self.control.find_control( x, y )
        if control is self.control:
            control = None

        return control

#-------------------------------------------------------------------------------
#  '_ControlGrabberEditor' class:
#-------------------------------------------------------------------------------

class _ControlGrabberEditor ( Editor ):
    """ A custom editor for grabbing GUI toolkit neutral 'control' objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ControlGrabber control we are using to implement the editor:
    grabber = Instance( ControlGrabber, () )

    # The most recent control the mouse pointer passed over:
    over = Instance( Control )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying control.
        """
        self.adapter = self.grabber.set( parent = parent )()
        self.sync_value( self.factory.over, 'over', 'to' )
        self.set_tooltip()


    def update_editor ( self ):
        """ Handles the facet bound to the editor being updated.
        """
        pass

    #-- Facets Event Handlers --------------------------------------------------

    @on_facet_set( 'grabber:selected' )
    def _selected_modified ( self, control ):
        self.value = control


    @on_facet_set( 'grabber:over' )
    def _over_modified ( self, control ):
        self.over = control

#-------------------------------------------------------------------------------
#  'ControlGrabberEditor' class:
#-------------------------------------------------------------------------------

class ControlGrabberEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ControlGrabberEditor

    # The extended facet name to synchronize the most recent control passed over
    # by the ControlGrabber with:
    over = Str

#-- EOF ------------------------------------------------------------------------