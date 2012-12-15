"""
Implements a collection of useful debugging functions.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os

#-------------------------------------------------------------------------------
#  Get the debug mode:
#-------------------------------------------------------------------------------

try:
    DEBUG = int( os.environ.get( 'FACETS_DEBUG', '0' ) )
except:
    DEBUG = 0

#-------------------------------------------------------------------------------
#  Debug Functions:
#-------------------------------------------------------------------------------

if DEBUG:
    #-- Define the Debug Functions ---------------------------------------------

    from inspect \
        import stack

    from os.path \
        import basename, splitext

    LogObject = None

    def log_object ( ):
        """ Attempts to return the singleton LogObject class.
        """
        global LogObject

        if LogObject is None:

            from facets.core.has_facets \
                import HasFacets, SingletonHasPrivateFacets

            from facets.core.facet_types \
                import Str, Instance

            from facets.ui.view \
                import View

            from facets.extra.helper.themes \
                import TTitle

            #-------------------------------------------------------------------
            #  '_LogObject' class:
            #-------------------------------------------------------------------

            class _LogObject ( SingletonHasPrivateFacets ):
                """ Class for logging objects for debugging purposes.
                """

                #-- Facet Definitions ------------------------------------------

                # The name of the plugin:
                name = Str( 'Log Object' )

                # Event fired when an object is logged:
                object = Instance( HasFacets, connect = 'from' )

                # The fully qualified name of the most recent object logged:
                class_name = Str

                #-- Facet View Definitions -------------------------------------

                view = View( TTitle( 'class_name' ) )

                #-- Facet Event Handlers ---------------------------------------

                def _object_set ( self, value ):
                    self.class_name = '%s.%s' % ( value.__class__.__module__,
                                                  value.__class__.__name__ )

            LogObject = _LogObject

        return LogObject()


    def log ( msg ):
        """ Prints a message to standard out or logs a HasFacets object to the
            LogObject tool.
        """
        try:
            from facets.core.has_facets import HasFacets
        except:
            return

        if isinstance( msg, HasFacets ):
            log_object().object = msg
        else:
            print msg


    def log_if ( mask, msg ):
        """ If the specified mask matches the debug mask, prints a message to
            standard out or logs a HasFacets object to the LogObject tool.
        """
        if mask & DEBUG:
            log( msg )


    def called_from ( levels = 1, context = 1 ):
        """ Print the current call stack. """
        stk = stack( context )
        frame, file_name, line_num, func_name, lines, index = stk[1]
        print '-' * 79
        print "'%s' called from:" % func_name

        for frame_rec in stk[ levels + 1: 1: -1 ]:
            frame, file_name, line_num, func_name, lines, index = frame_rec
            print '   %s (%s: %d)' % ( func_name, file_name, line_num )
            if lines is not None:
                if len( lines ) == 1:
                    print '      ' + lines[0].strip()[:73]
                else:
                    for i, line in enumerate( lines ):
                        print '   %s  %s' % ( '|>'[ i == index ],
                                              line.rstrip() )

        print '-' * 79


    def created_from ( object, level = 1 ):
        """ Attaches to 'object' a message called '_created_from' describing
            where 'object' was created. Should be called from the 'object'
            class's top-level constructor.
        """
        _, file_name, line_num, func_name, lines, _ = stack( 1 )[ level + 1 ]
        info = '%s (%s:%d)' % ( func_name, file_name, line_num )
        if lines is not None:
            info += ' [%s]' % lines[0].strip()
        object._created_from       = info
        object._created_from_short = '%s:%d' % (
            splitext( basename( file_name ) )[0], line_num )


    def object_info ( object ):
        """ Returns a simple object reference string.
        """
        return '%s%s: %08X' % ( object.__class__.__name__,
                                _created_info( object ), id( object ) )


    def wdump ( control, msg = '', root = True ):
        """ Dumps a GUI toolkit neutral control hierarchy to standard out.
        """
        from facets.ui.toolkit import toolkit

        control = toolkit().as_toolkit_adapter( control )
        if root:
            parent = control.parent
            while parent is not None:
                control = parent
                parent = control.parent

        if msg == '':
            msg = stack( 1 )[1][3]

        print '--- %s %s' % ( msg, '-' * (74 - len( msg )) )

        _wdump( control, 0, '' )


    def wdump_if ( mask, control, msg = '', root = True ):
        """ Dumps a GUI toolkit neutral control hierarchy to standard out if
            the mask matches the debug mask.
        """
        if mask & DEBUG:
            if msg == '':
                msg = stack( 1 )[1][3]

            wdump( control, msg, root )

    #-- Private Helper Functions -----------------------------------------------

    def _wdump ( control, indent, mark ):
        """ Dumps a GUI toolkit neutral control hierarchy to standard out.
        """
        pad = '   ' * indent

        # Attempt to detect a recursive control/layout data structure:
        if indent > 10:
            print '%s<<<<< Recursive data structure >>>>>' % pad
            return

        children = control.children
        layout   = control.layout
        if layout is not None:
            print '%s%s%s [%s]' % ( pad, mark, object_info( control() ),
                                    _layout_info( layout ) )
            _wdump_layout( layout, children, indent + 1 )
            mark = '*: '
        else:
            print '%s%s%s' % ( pad, mark, object_info( control() ) )
            mark = ''

        for child in children:
            _wdump( child, indent + 1, mark )


    def _wdump_layout ( layout, children, indent ):
        """ Dumps a GUI toolkit neutral layout manager hierarchy to standard
            out.
        """
        pad = '   ' * indent
        for item in layout.children:
            control = item.control
            if control is not None:
                _wdump( control, indent,
                         _wcheck_control( control, children, indent ) )

            else:
                inner_layout = item.layout
                if inner_layout is not None:
                    print '%s<%s(' % ( pad, _layout_info( inner_layout ) )

                    ###if isinstance( inner_sizer, wx.StaticBoxSizer ):
                    ###    window = inner_sizer.GetStaticBox()
                    ###    _wxdump( window, indent + 1,
                    ###             _wxcheck_window( window, children, indent ) )

                    _wdump_layout( inner_layout, children, indent )
                    print '%s)>' % pad
                else:
                    print '%s<spacer>' % pad


    def _wcheck_control ( control, children, indent ):
        """ Checks to see if the specified layout control is in the list of
            children for the layout's control.
        """
        if control in children:
            children.remove( control )
            return ''

        parent = control.parent
        print '%s>>>> Invalid parent: %s <<<<' % ( '   ' * indent,
                                                   object_info( parent() ) )

        return '?: '


    def _layout_info ( layout ):
        """ Returns a printable name for the specified layout manager instance.
        """
        dir = 'H'
        if layout.is_vertical:
            dir = 'V'

        return '%s(%s)%s: %08X' % ( layout().__class__.__name__, dir,
                                   _created_info( layout ), id( layout ) )


    def _created_info ( object ):
        """ Returns the 'created from' info for an object if available.
        """
        created_from = getattr( object, '_created_from_short', None )
        if created_from is None:
            return ''

        return (' (%s)' % created_from)

else:
    #-- Define 'noop' stubs ----------------------------------------------------

    def log ( *args, **kw ):
        pass

    log_if = called_from = created_from = object_info = wdump = wdump_if = log

#-- EOF ------------------------------------------------------------------------