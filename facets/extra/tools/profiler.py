"""
Defines the Profiler tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import facets.extra.helper.profiler as profiler_module

from types \
    import UnboundMethodType

from facets.api \
    import HasPrivateFacets, Str, Instance, List, Directory, Bool, Any, Color, \
           View, VGroup, HGroup, Item, GridEditor, spring

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.features.api \
    import CustomFeature

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.api \
    import PythonFilePosition, FilePosition, import_module

from facets.extra.helper.profiler \
    import begin_profiling, end_profiling

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

HandlerTemplate = """
def template ( method, profile ):
    def %(method_name)s ( %(args)s, **kw ):
        return profile( method, %(args)s, **kw )
    return %(method_name)s
handler = template( method, profile )
"""

#-------------------------------------------------------------------------------
#  'ProfilerGridAdapter' class:
#-------------------------------------------------------------------------------

class ProfilerGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping profiler tool data into a GridEditor.
    """

    columns = [ ( 'Package', 'package_name' ),
                ( 'Module',  'module_name' ),
                ( 'Class',   'class_name' ),
                ( 'Method',  'method_name') ]

    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )


profiler_grid_editor = GridEditor(
    adapter    = ProfilerGridAdapter,
    operations = [ 'delete' ]
)

#-------------------------------------------------------------------------------
#  'Profiler' tool:
#-------------------------------------------------------------------------------

class Profiler ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Profiler'

    # Custom button used to begin profiling:
    start = CustomFeature(
        image   = '@facets:start_profiler',
        click   = 'start_profiler',
        tooltip = 'Click to begin profiling.',
        enabled = False
    )

    # Custom button used to end profiling:
    stop = CustomFeature(
        image   = '@facets:stop_profiler',
        click   = 'stop_profiler',
        tooltip = 'Click to end profiling.',
        enabled = False
    )

    # Current item to be added to the profile:
    profile = Instance( PythonFilePosition,
                        droppable = 'Drop a class or method item here to '
                                    'profile it.',
                        connect   = 'to: class or method item' )

    # The FilePosition of the file used to store the most recent profiling
    # statistics:
    file_position = Instance( FilePosition,
                              draggable = 'Drag profile statistics file name.',
                              connect   = 'from: profile statistics file name' )

    # Current list of methods being profiled:
    profiles = List( save_state = True )

    # The directory used to store profiler data files:
    path = Directory( save_state = True )

    # Should classes be expanded into individual methods:
    expand_classes = Bool( False, save_state = True )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'profiles',
              id         = 'profiles',
              show_label = False,
              editor     = profiler_grid_editor
        ),
        id = 'facets.extra.tools.profiler'
    )

    options = View(
        VGroup(
            VGroup(
                Item( 'path',
                      label = 'Profiler Data Files Path',
                      width = -300
                ),
                '_'
            ),
            HGroup(
                Item( 'expand_classes',
                      label = 'Expand classes to show methods'
                ),
                spring
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def start_profiler ( self ):
        """ Starts profiling.
        """
        begin_profiling( self.path )
        self.start.enabled = False
        self.stop.enabled  = True


    def stop_profiler ( self ):
        """ Stops profiling.
        """
        end_profiling()
        self.file_position = FilePosition(
                                 file_name = profiler_module.profile_name )
        self.stop.enabled  = False
        self.set_start()


    def set_start ( self ):
        """ Sets the current state of the 'start profiling' button.
        """
        self.start.enabled = (len( self.profiles ) > 0)


    def add_method ( self, file_position ):
        """ Adds a new method to the list of profiled methods.
        """
        # Get the particulars:
        module_name = '%s.%s' % ( file_position.package_name,
                                  file_position.module_name )
        class_name  = file_position.class_name
        method_name = file_position.method_name

        # Make sure we are not already profiling it:
        for pm in self.profiles:
            if ((module_name == pm.module_name) and
                (class_name  == pm.class_name)  and
                (method_name == pm.method_name)):
                return False

        module, klass = self.get_module_class( file_position )
        if module is None:
            return False

        # Set up the profiler intercept:
        method = self.set_handler( klass, method_name )
        if method is None:
            return False

        # Add the method to the list of profiled methods:
        self.profiles.append( ProfileMethod( klass = klass, method = method ) )

        # Indicate the method was successfully added:
        return True


    def add_class ( self, file_position ):
        """ Adds all of the methods for a class to the list of profiled methods.
        """
        # Get the module and class:
        module, klass = self.get_module_class( file_position )
        if module is None:
            return False

        # Add each method found in the class:
        method_position = PythonFilePosition( **file_position.get(
                              'package_name', 'module_name', 'class_name' ) )
        for name in klass.__dict__.keys():
            if isinstance( getattr( klass, name ), UnboundMethodType ):
                method_position.method_name = name
                self.add_method( method_position )


    def get_module_class ( self, file_position ):
        """ Returns the module_name, module and class for a specified file
            position.
        """
        # Get the full module name:
        module_name = '%s.%s' % ( file_position.package_name,
                                  file_position.module_name )

        # Locate the module containing the class:
        module = import_module( module_name )
        if module is None:
            # fixme: Report some kind of an error here...
            return ( None, None )

        # Locate the class containing the method:
        klass = getattr( module, file_position.class_name, None )
        if klass is None:
            # fixme: Report some kind of an error here...
            return ( None, None )

        # Return the module and class:
        return ( module, klass )


    def set_handler ( self, klass, method_name ):
        """ Sets up the handler for a specified class's method.
        """
        method = getattr( klass, method_name, None )
        if method is not None:
            # We create different handler versions so that the argument counts
            # match up for cases handled by the facets notification wrappers
            # (i.e. self + 0..4 arguments):
            arg_count = method.im_func.func_code.co_argcount
            if 1 <= arg_count <= 5:
                args = 'a1, a2, a3, a4, a5'[ : 4 * arg_count - 2 ]
            else:
                args = '*args'

            exec HandlerTemplate % { 'method_name': method_name, 'args': args }

            setattr( klass, method.__name__, handler )

            return method

        # fixme: Report some kind of error here...
        return None

    #-- Facet Event Handlers ---------------------------------------------------

    def _profile_set ( self, file_position ):
        """ Handles the 'profile' facet being changed.
        """
        if file_position is not None:
            do_later( self.set, profile = None )
            if file_position.class_name != '':
                if file_position.method_name != '':
                    self.add_method( file_position )
                else:
                    self.add_class( file_position )


    def _profiles_set ( self, profiles ):
        """ Handles the 'profiles' facet being changed.
        """
        for pm in profiles:
            if pm.klass is None:
                # fixme: Need to check for errors in the next two statements...
                module, pm.klass = self.get_module_class(
                    PythonFilePosition(
                        **pm.get( 'package_name', 'module_name', 'class_name',
                                  'method_name' )
                    )
                )
                pm.method = self.set_handler( pm.klass, pm.method_name )

        self.set_start()


    def _profiles_items_set ( self, event ):
        """ Handles the 'profiles' facet being changed.
        """
        for pm in event.removed:
            pm.restore()

        self.set_start()

#-------------------------------------------------------------------------------
#  'ProfileMethod' class:
#-------------------------------------------------------------------------------

class ProfileMethod ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The original class the method belongs to:
    klass = Any

    # The original method extracted from the class:
    method = Any

    # The name of the associated package:
    package_name = Str

    # The name of the associated module:
    module_name = Str

    # The name of the associated class:
    class_name = Str

    # The name of the associated method:
    method_name = Str

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, **facets ):
        """ Initializes the object.
        """
        super( ProfileMethod, self ).__init__( **facets )

        module_name = self.klass.__module__
        col = module_name.rfind( '.' )
        if col >= 0:
            self.package_name = module_name[ : col ]

        self.module_name = module_name[ col + 1: ]
        self.class_name  = self.klass.__name__
        self.method_name = self.method.__name__


    def __getstate__ ( self ):
        """ Returns a persistible form of the object state.
        """
        return self.get( 'package_name', 'module_name', 'class_name',
                         'method_name' )


    def restore ( self ):
        """ Restores the original method for a class.
        """
        setattr( self.klass, self.method_name, self.method )

#-- EOF ------------------------------------------------------------------------