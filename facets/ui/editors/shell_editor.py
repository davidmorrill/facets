"""
Editor that displays an interactive Python shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Str, Font, Event, BasicEditorFactory

from facets.ui.editor \
    import Editor

from facets.ui.pyface.python_shell \
    import PythonShell

#-------------------------------------------------------------------------------
#  '_ShellEditor' class:
#-------------------------------------------------------------------------------

class _ShellEditor ( Editor ):
    """ Editor that displays an interactive Python shell.
    """

    #-- Facet Definitions ------------------------------------------------------

    # An event fired whenever the user executes a command in the shell:
    command_executed = Event( Bool )

    # An external command to be executed by the interpreter:
    command = Event

    # Is the shell editor is scrollable? This value overrides the default.
    scrollable = True

    # The font to use for the editor:
    font = Font( 'Courier 10' )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        locals = None
        value  = self.value
        if self.factory.share and isinstance( value, dict ):
            locals = value
        self._shell       = shell = PythonShell( parent, locals = locals )
        self.control      = shell.control
        self.adapter.font = self.font
        if locals is None:
            object = self.object
            shell.bind( 'self', object )
            shell.on_facet_set( self.update_object, 'command_executed',
                                dispatch = 'ui' )
            if not isinstance( value, dict ):
                object.on_facet_set( self.update_any, dispatch = 'ui' )
            else:
                self._base_locals = locals = {}
                for name in shell.interpreter().locals.keys():
                    locals[ name ] = None

        # Synchronize any editor events:
        self.sync_value( self.factory.command_executed,
                         'command_executed', 'to' )
        self.sync_value( self.factory.command, 'command', 'from' )

        self.set_tooltip()


    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        locals      = self._shell.interpreter().locals
        base_locals = self._base_locals
        if base_locals is None:
            object = self.object
            for name in object.facet_names():
                if name in locals:
                    try:
                        setattr( object, name, locals[ name ] )
                    except:
                        pass
        else:
            dic = self.value
            for name in locals.keys():
                if name not in base_locals:
                    try:
                        dic[ name ] = locals[ name ]
                    except:
                        pass

        self.command_executed = True


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self.factory.share:
            value = self.value
            if isinstance( value, dict ):
                self._shell.interpreter().locals = value
        else:
            locals      = self._shell.interpreter().locals
            base_locals = self._base_locals
            if base_locals is None:
                object = self.object
                for name in object.facet_names():
                    locals[ name ] = getattr( object, name, None )
            else:
                dic = self.value
                for name, value in dic.items():
                    locals[ name ] = value


    def update_any ( self, object, name, old, new ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        locals = self._shell.interpreter().locals
        if self._base_locals is None:
            locals[ name ] = new
        else:
            self.value[ name ] = new


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self._shell.on_facet_set( self.update_object, 'command_executed',
                                  remove = True )
        if self._base_locals is None:
            self.object.on_facet_set( self.update_any, remove = True )

        super( _ShellEditor, self ).dispose()


    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        control = self._shell.control
        try:
            control.history      = prefs.get( 'history', [] )
            control.historyIndex = prefs.get( 'historyIndex', -1 )
        except:
            pass


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        control = self._shell.control

        return {
            'history':      control.history,
            'historyIndex': control.historyIndex
        }

    #-- Facet Event Handlers ---------------------------------------------------

    def _command_set ( self, command ):
        """ Handles a Python command being passed in externally.
        """
        self._shell.execute_command( command, False )

#-------------------------------------------------------------------------------
#  'ShellEditor' class:
#-------------------------------------------------------------------------------

class ShellEditor ( BasicEditorFactory ):

    # The class used to construct editor objects:
    klass = _ShellEditor

    # Should the shell interpreter use the object value's dictionary?
    share = Bool( False )

    # Extended facet name of the object event facet which is fired when a
    # command is executed
    command_executed = Str

    # Extended facet name of the object facet to which Python commands can be
    # assigned in order to have the shell interpreter execute them:
    command = Str

#-- EOF ------------------------------------------------------------------------