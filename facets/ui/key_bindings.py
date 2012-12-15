"""
Defines KeyBinding and KeyBindings classes, which manage the mapping of
keystroke events into method calls on controller objects that are supplied
by the application.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, HasStrictFacets, Str, List, Any, Instance, Event, \
           Property, on_facet_set, cached_property, View, HGroup, Item,        \
           ListEditor, KeyBindingEditor, toolkit

from facets.core.facet_base \
    import SequenceTypes, invoke

#-------------------------------------------------------------------------------
#  Key binding facet definition:
#-------------------------------------------------------------------------------

# Facet definition for key bindings
Binding = Str( event = 'modified', editor = KeyBindingEditor() )

#-------------------------------------------------------------------------------
#  'KeyBinding' class:
#-------------------------------------------------------------------------------

class KeyBinding ( HasStrictFacets ):
    """ Binds one or two keystrokes to a method.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Primary key binding:
    binding = Binding

    # Secondary (alternate) key binding:
    alt_binding = Binding

    # The key any similar child key bindings with the should be rebound to:
    rebinding = Binding

    # Description of what application function the method performs:
    description = Str

    # Name of controller method the key is bound to:
    method = Str

    # KeyBindings object that "owns" the KeyBinding:
    owner = Instance( 'KeyBindings' )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        HGroup(
            Item( 'binding' ),
            Item( 'alt_binding' ),
            Item( 'description', style = 'readonly' ),
            show_labels = False
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the object when it is no longer used.
        """
        del self.owner

    #-- Facet Event Handlers ---------------------------------------------------

    def _modified_set ( self ):
        """ Handles a binding facet being changed.
        """
        if self.owner is not None:
            self.owner.binding_modified = self

#-------------------------------------------------------------------------------
#  'KeyBindings' class:
#-------------------------------------------------------------------------------

class KeyBindings ( HasPrivateFacets ):
    """ A set of key bindings.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Set of defined key bindings (redefined dynamically):
    bindings = List( KeyBinding )

    # Optional prefix to add to each method name:
    prefix = Str

    # Optional suffix to add to each method name:
    suffix = Str

    #-- Private Facets ---------------------------------------------------------

    # The (optional) list of controllers associated with this KeyBindings
    # object. The controllers may also be provided with the 'do' method:
    controllers = List( transient = True )

    # The 'parent' KeyBindings object of this one (if any):
    parent = Instance( 'KeyBindings', transient = True )

    # The root of the KeyBindings tree this object is part of:
    root = Property( depends_on = 'parent' )

    # The child KeyBindings of this object (if any):
    children = List( transient = True )

    # Event fired when one of the contained KeyBinding objects is changed:
    binding_modified = Event( KeyBinding )

    # Control that currently has the focus (if any):
    focus_owner = Any( transient = True )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View( [
        Item( 'bindings',
              style      = 'custom',
              show_label = False,
              editor     = ListEditor( style = 'custom' )
        ),
        '|{Click on an entry field, then press the key to assign. Double-click '
        'a field to clear it.}<>' ],
        title     = 'Update Key Bindings',
        kind      = 'livemodal',
        resizable = True,
        width     = 0.4,
        height    = 0.4
    )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, *bindings, **facets ):
        """ Initializes the object.
        """
        super( KeyBindings, self ).__init__( **facets )

        if (len( bindings ) == 1) and isinstance( bindings[0], SequenceTypes ):
            bindings = bindings[0]

        n = len( bindings )
        self.add_facet( 'bindings',
                        List( KeyBinding, minlen = n,
                                          maxlen = n,
                                          mode   = 'list' ) )
        self.bindings = [ binding.set( owner = self ) for binding in bindings ]


    def do ( self, event, controllers = [], *args, **kw ):
        """ Processes a keyboard event.
        """
        if isinstance( controllers, dict ):
            controllers = controllers.values()
        elif not isinstance( controllers, SequenceTypes ):
            controllers = [ controllers ]
        else:
            controllers = list( controllers )

        key_name = toolkit().key_event_to_name( event )
        if key_name == '':
            return False

        return self._do( ( key_name, ), controllers, args )


    def merge ( self, key_bindings ):
        """ Merges another set of key bindings into this set.
        """
        binding_dic = {}
        for binding in self.bindings:
            binding_dic[ binding.method ] = binding

        for binding in key_bindings.bindings:
            binding2 = binding_dic.get( binding.method )
            if binding2 is not None:
                binding2.binding     = binding.binding
                binding2.alt_binding = binding.alt_binding


    def clone ( self, **facets ):
        """ Returns a clone of the KeyBindings object.
        """
        return self.__class__( *self.bindings ).set(
            **self.get( 'prefix', 'suffix', 'controllers' )
        ).set( **facets )


    def dispose ( self ):
        """ Dispose of the object.
        """
        if self.parent is not None:
            self.parent.children.remove( self )

        for binding in self.bindings:
            binding.dispose()

        del self.controllers
        del self.children
        del self.bindings

        self.parent = self.focus_owner = None


    def edit ( self ):
        """ Edits a possibly hierarchical set of KeyBindings.
        """
        bindings = list( set( self.root._get_bindings( [] ) ) )
        bindings.sort( lambda l, r:
            cmp( '%s%02d' % ( l.binding[-1:], len( l.binding ) ),
                 '%s%02d' % ( r.binding[-1:], len( r.binding ) ) ) )
        KeyBindings( bindings ).edit_facets()


    def key_binding_for ( self, binding, key_name ):
        """ Returns the current binding for a specified key (if any).
        """
        if key_name != '':
            for a_binding in self.bindings:
                if ((a_binding is not binding ) and
                    ((key_name == a_binding.binding) or
                     (key_name == a_binding.alt_binding))):
                    return a_binding

        return None

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_root ( self ):
        root = self
        while root.parent is not None:
            root = root.parent

        return root

    #-- Facet Event Handlers ---------------------------------------------------

    def _binding_modified_set ( self, binding ):
        """ Handles a binding being changed.
        """
        binding     = binding.binding
        alt_binding = binding.alt_binding
        for a_binding in self.bindings:
            if binding is not a_binding:
                if binding == a_binding.binding:
                    a_binding.binding = ''
                if binding == a_binding.alt_binding:
                    a_binding.alt_binding = ''
                if alt_binding == a_binding.binding:
                    a_binding.binding = ''
                if alt_binding == a_binding.alt_binding:
                    a_binding.alt_binding = ''


    def _focus_owner_set ( self, old, new ):
        """ Handles the focus owner being changed.
        """
        if old is not None:
            old.border_size = 0


    @on_facet_set( 'children[]' )
    def _children_modified ( self, added ):
        """ Handles child KeyBindings being added to the object.
        """
        for item in added:
            item.parent = self

    #-- object Method Overrides ------------------------------------------------

    def __setstate__ ( self, state ):
        """ Restores the state of a previously pickled object.
        """
        n = len( state[ 'bindings' ] )
        self.add_facet( 'bindings', List( KeyBinding, minlen = n, maxlen = n ) )
        self.__dict__.update( state )
        self.bindings = self.bindings[:]

    #-- Private Methods --------------------------------------------------------

    def _get_bindings ( self, bindings ):
        """ Returns all of the bindings of this object and all of its children.
        """
        bindings.extend( self.bindings )
        for child in self.children:
            child._get_bindings( bindings )

        return bindings


    def _do ( self, key_names, controllers, args ):
        """ Process the specified key for the specified set of controllers for
            this KeyBindings object and all of its children.
        """
        # Search through our own bindings for a match:
        for binding in self.bindings:
            if ((binding.binding     in key_names) or
                (binding.alt_binding in key_names)):
                method_name = '%s%s%s' % ( self.prefix, binding.method,
                                           self.suffix )
                for controller in (self.controllers + controllers):
                    method = getattr( controller, method_name, None )
                    if method is not None:
                        result = invoke( method, *args )
                        if result is not False:
                            return True

                if binding.method == 'edit_bindings':
                    self.edit()

                    return True

            elif binding.rebinding in key_names:
                key_names = key_names + ( binding.binding, )
                if binding.alt_binding != '':
                    key_names = key_names + ( binding.alt_binding, )

        # Continue searching through any children's bindings:
        for child in self.children:
            if child._do( key_names, controllers, args ):
                return True

        # Indicate no one processed the key:
        return False

#-- EOF ------------------------------------------------------------------------