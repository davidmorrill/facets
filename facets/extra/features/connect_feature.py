"""
Adds a 'connect' feature to DockWindow which allows users to dynamically connect
(i.e. synchronize) facets on one object with another. To make an object
'connectable' the developer must specify the 'connect' metadata on any facet
that can be connected to another object's facet. The value of the 'connect'
metadata should be:  'to|from|both[:[:]description]', indicating the direction
of synchronization supported (i.e. to, from or both), as well as an optional
description to display in the feature's tooltip. If a double colon (i.e. ::)
precedes the description, then the description is also used as a type, meaning
that both ends of the connection must specify the same type information. This is
useful when using simple facet types list Str or File, and you want to add an
additional level of type checking to the connection.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from weakref \
    import WeakKeyDictionary

from facets.core_api \
    import HasFacets, HasPrivateFacets, Any, Str, Dict, Instance, Enum

from facets.core.facet_db \
    import facet_db

from facets.ui.menu \
    import Menu, Action

from facets.ui.dock.api \
    import DockWindowFeature

from facets.ui.ui_facets \
    import image_for

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

no_connections_image = image_for( '@facets:no_connections_feature' )
connections_image    = image_for( '@facets:connections_feature' )

# Menu to display when there are no available connections/disconnections:
no_connections = Menu(
    Action( name    = 'No connections available',
            enabled = False ),
    name = 'popup'
)

PermanentConnections = 'facets.extra.features.ConnectFeature.' \
                       'permanent_connections'

#-------------------------------------------------------------------------------
#  Filter for extracting facets which support the 'connect' protocol:
#-------------------------------------------------------------------------------

supported_protocols = ( 'to', 'from', 'both' )

def can_connect ( value ):
    if isinstance( value, str ):
        col = value.find( ':' )
        if col >= 0:
            value = value[ : col ].strip()

        return (value in supported_protocols)

    return False

#-------------------------------------------------------------------------------
#  'ConnectFeature' class:
#-------------------------------------------------------------------------------

class ConnectFeature ( DockWindowFeature ):

    #-- Class Constants --------------------------------------------------------

    # The user interface name of the feature:
    feature_name = 'Connect'

    #-- Facet Definitions ------------------------------------------------------

    # The context id this feature is part of:
    context = Str

    # Set of 'connectable' object facets:
    connectable_facets = Any  # Dict( name, facet )

    # Set of current connections that have been made:
    connections = Dict # ( name, Connection )

    # The current image to display on the feature bar:
    image = '@facets:no_connections_feature'

    # The tooltip to display when the mouse is hovering over the image:
    tooltip = 'Click to make or break connections to other views.'

    #-- DockWindowFeature Methods ----------------------------------------------

    def drag ( self ):
        """ Returns the object to be dragged when the user drags feature image.
        """
        return self


    def drop ( self, object ):
        """ Handles the user dropping a specified object on the feature image.
        """
        new_connections = []
        connects        = {}
        self.get_available_connections( object, connects, new_connections )

        if len( new_connections ) == 1:
            # If only one possible connection, just go ahead and make it:
            self.make_connection( new_connections[0] )
        else:
            # Else let the user pick which one they want:
            self.pop_connection_menu( connects, new_connections, [ ] )


    def can_drop ( self, object ):
        """ Returns whether a specified object can be dropped on the feature
            image.
        """
        if isinstance( object, ConnectFeature ):
            connections = []
            self.get_available_connections( object, {}, connections )
            if len( connections ) > 0:
                return True

        return False


    def right_click ( self ):
        """ Handles the user right clicking on the feature image.
        """
        self.click()


    def click ( self ):
        """ Handles the user left clicking on the feature image.
        """
        new_connections = []
        connects        = {}

        # Iterate over all other DockControls in the same window:
        for dc in self.dock_control.dock_controls:

            # Find those which have objects supporting the 'connect' protocol:
            for feature2 in dc.features_of_type( ConnectFeature ):
                self.get_available_connections( feature2, connects,
                                                new_connections )

        # If there are no actions that can be taken, then display empty menu:
        connections = self.connections
        if (len( connects ) == 0) and (len( connections ) == 0):
            self.popup_menu( no_connections )
        else:
            # Else display pop-up menu of available connections/disconnections:
            self.pop_connection_menu( connects, new_connections, connections )


    def dispose ( self ):
        """ Performs any clean-up needed when the feature is being removed.
        """
        self.dock_control.on_facet_set( self.activate, 'activated',
                                        remove = True )

    #-- ConnectFeature Methods -------------------------------------------------

    def get_available_connections ( self, feature2, connects, new_connections ):
        """ Returns the connections that can be made between two
            ConnectFeatures.
        """
        connectable_facets = feature2.connectable_facets
        dc                 = feature2.dock_control
        label2             = dc.name
        object2            = dc.object
        object1            = self.dock_control.object
        label1             = self.dock_control.name
        no_name1           = (len( self.connectable_facets ) == 1)
        no_name2           = (len( connectable_facets ) == 1)
        connections        = self.connections

        for name1, facet1 in self.connectable_facets.items():
            connect1, type1, ui_name1 = self.parse_connect( facet1.connect,
                                                            name1 )
            if no_name1:
                ui_name1 = ''

            actions           = []
            name1_connections = connections.get( name1, [] )
            for name2, facet2 in connectable_facets.items():
                # Only allow a connection that hasn't already been made:
                for connection in name1_connections:
                    if connection.feature1 is self:
                        if ((name2  == connection.name2) and
                            (label2 == connection.label2)):
                            break
                    else:
                        if ((name2  == connection.name1) and
                            (label2 == connection.label1)):
                            break
                else:
                    # Determine if a connection will actually work:
                    connect2, type2, ui_name2 = self.parse_connect(
                                                         facet2.connect, name2 )
                    if no_name2:
                        ui_name2 = ''

                    if (((connect1 == 'both') or
                         (connect2 == 'both') or
                         (connect1 != connect2)) and
                         (((type1 == '') and (type2 == '')) or
                          (type1 == type2))):
                        if (connect1 == 'to') or (connect2 == 'from'):
                            try:
                                facet1.validate( object1, name1,
                                                 getattr( object2, name2 ) )
                            except:
                                continue
                        else:
                            try:
                                facet2.validate( object2, name2,
                                                 getattr( object1, name1 ) )
                            except:
                                continue

                        # Establish the type of connection to make:
                        connect = connect1
                        if connect1 != connect2:
                            if connect1 == 'both':
                                connect = 'to'
                                if connect2 == 'to':
                                    connect = 'from'

                        # Add the action to connect it:
                        actions.append( ( ui_name1, ui_name2, dc.name,
                                          len( new_connections ) ) )

                        # Create the corresponding Connection object:
                        new_connections.append( Connection(
                            object1    = object1,
                            name1      = name1,
                            ui_name1   = ui_name1,
                            feature1   = self,
                            label1     = label1,
                            object2    = object2,
                            name2      = name2,
                            ui_name2   = ui_name2,
                            feature2   = feature2,
                            label2     = label2,
                            connection = connect ) )

            # If there are any actions, then add them to the list:
            if len( actions ) > 0:
                if name1 not in connects:
                    connects[ name1 ] = []

                connects[ name1 ].extend( actions )


    def parse_connect ( self, connect, name ):
        """ Parses a 'connect' string into the connection type and an optional
            user friendly name.
        """
        col = connect.find( ':' )
        if col < 0:
            return ( connect, '', name )

        connection = connect[ : col ].strip()
        has_type   = ( connect[ col + 1: col + 2 ] == ':' )
        if has_type:
            col += 1

        name = connect[ col + 1: ].strip()
        type = ''
        if has_type:
            type = name

        return ( connection, type, name )


    def connect_actions ( self, actions ):
        """ Returns a list of Actions for a list of potential connections.
        """
        force  = (len( actions ) == 1)
        result = []
        for ui_name1, ui_name2, dc_name, index in actions:
            if (not force) and (ui_name2 != ''):
                result.append( Action(
                         name   = 'to the %s in the %s' % ( ui_name2, dc_name ),
                         action = "self.connect(%d)" % index ) )
            else:
                result.append( Action(
                         name   = 'to the %s' % dc_name,
                         action = "self.connect(%d)" % index ) )

        return result


    def disconnect_actions ( self, connections ):
        """ Returns a list of Actions for a list of potential disconnects.
        """
        force   = (len( connections ) == 1)
        actions = []

        for i, connection in enumerate( connections ):
            if connection.feature1 is self:
                ui_name2 = connection.ui_name2
                if (not force) and (ui_name2 != ''):
                    actions.append(
                        Action( name   = 'from the %s in the %s' % (
                                         ui_name2, connection.label2 ),
                                action = "self.disconnect('%s',%d)" %
                                         ( connection.name1, i ) ) )
                else:
                    actions.append(
                        Action( name   = 'from the %s' % connection.label2,
                                action = "self.disconnect('%s',%d)" %
                                         ( connection.name1, i ) ) )
            else:
                ui_name1 = connection.ui_name1
                if (not force) and (ui_name1 != ''):
                    actions.append(
                        Action( name   = 'from the %s in the %s' % (
                                         ui_name1, connection.label1 ),
                                action = "self.disconnect('%s',%d)" %
                                         ( connection.name2, i ) ) )
                else:
                    actions.append(
                        Action( name   = 'from the %s' % connection.label1,
                                action = "self.disconnect('%s',%d)" %
                                         ( connection.name2, i ) ) )

        return actions


    def connect ( self, index ):
        """ Makes a connection specified by index.
        """
        self.make_connection( self._new_connections[ index ] )
        self._new_connections = None


    def make_connection ( self, connection, permanent = True ):
        """ Makes a specified connection.
        """
        # Add the connection to our list of connections:
        self.add_connection( connection )

        # Add the connection to the other ConnectFeature's list of connections:
        connection.feature2.add_connection( connection )

        # Make the connection:
        connection.connect()

        # Persist the connection:
        if permanent:
            self.add_permanent_connection( connection )


    def add_connection ( self, connection ):
        """ Adds a new connection to our list of connections.
        """
        # If this is our first connection, change the feature image:
        connections = self.connections
        if len( connections ) == 0:
            self.image = connections_image
            self.refresh()

        # Add the connection to our list of connections:
        name = connection.name2
        if connection.feature1 is self:
            name = connection.name1

        connections.setdefault( name, [] ).append( connection )


    def add_permanent_connection ( self, connection ):
        """ Adds a permanent connection.
        """
        connections = ConnectFeature.get_permanent_connections( self.context )
        connections.append( connection.clone() )
        facet_db.set( self.context, connections )


    def disconnect ( self, name, connection ):
        """ Disconnects a specified connection.
        """
        # Handle the case of 'connection' being a list index:
        if not isinstance( connection, Connection ):
            # Get the connection to be broken:
            connection = self.connections[ name ][ connection ]

        # Remove the connection from our list:
        self.remove_connection( name, connection )

        # Remove the connection from the other ConnectFeature's list:
        if connection.feature1 is self:
            connection.feature2.remove_connection( connection.name2,
                                                   connection )
        else:
            connection.feature1.remove_connection( connection.name1,
                                                   connection )

        # Break the connection:
        connection.disconnect()

        # Unpersist the connection:
        self.remove_permanent_connection( connection )


    def remove_connection ( self, name, connection ):
        """ Removes a specified connection.
        """
        connections = self.connections[ name ]
        connections.remove( connection )
        if len( connections ) == 0:
            del self.connections[ name ]

        if len( self.connections ) == 0:
            self.image = no_connections_image
            self.refresh()


    def remove_permanent_connection ( self, connection ):
        """ Removes a permanent connection.
        """
        connections = ConnectFeature.get_permanent_connections( self.context )
        for i, connection2 in enumerate( connections ):
            if connection == connection2:
                del connections[ i ]
                if len( connections ) == 0:
                    facet_db.set( self.context )
                else:
                    facet_db.set( self.context, connections )

                break


    def pop_connection_menu ( self, connects, new_connections,
                                              old_connections ):
        """ Displays the pop-up connection menu for a specified set of
            connections.
        """

        # Create the list for holding the main menu actions:
        actions = []

        # Create the 'connect' submenus:
        if len( connects ) > 0:
            names = connects.keys()
            if len( names ) == 1:
                sub_menus = self.connect_actions( connects[ names[0] ] )
            else:
                names.sort()
                sub_menus = []
                for name in names:
                    items = connects[ name ]
                    sub_menus.append( Menu(
                        name = items[0][0],
                        *self.connect_actions( items )
                    ) )

            actions.append( Menu( name = 'Connect', *sub_menus ) )

        # Create the 'disconnect' submenus:
        disconnects = []
        n = len( old_connections )
        if n > 0:
            names = old_connections.keys()
            if n == 1:
                sub_menus = self.disconnect_actions(
                                old_connections[ names[0] ] )
            else:
                names.sort()
                sub_menus = []
                for name in names:
                    sub_menus.append( Menu( name = name,
                        * self.disconnect_actions( old_connections[ name ] ) ) )
            actions.append( Menu( name = 'Disconnect', *sub_menus ) )

        # Display the pop-up menu:
        self._new_connections = new_connections
        self.popup_menu( Menu( name = 'popup', *actions ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _dock_control_set ( self, dock_control ):
        """ Handles the 'dock_control' facet beinch changed.
        """
        dock_control.on_facet_set( self.activate, 'activated' )


    def activate ( self ):
        """ Handles the associated DockControl being activated by the user.
        """
        dock_control = self.dock_control
        regions      = [ dock_control.parent ]
        controls     = [ dock_control ]
        queue        = []

        # Add to the work queue all of our connections:
        for connections in self.connections.values():
            for connection in connections:
                queue.append( ( dock_control, connection ) )

        # Loop until we've processed all reachable connections:
        while len( queue ) > 0:

            # Get the next connection to analyze:
            dock_control, connection = queue.pop()

            # Only process the connection if it is 'downstream' from this one:
            if dock_control is connection.feature1.dock_control:
                if connection.connection == 'to':
                    continue

                feature2 = connection.feature2
            elif connection.connection == 'from':
                continue
            else:
                feature2 = connection.feature1

            # Only process it if we haven't already visited it before:
            dock_control2 = feature2.dock_control
            if dock_control2 in controls:
                continue

            controls.append( dock_control2 )

            # Add all of its connections to the work queue:
            for connections2 in feature2.connections.values():
                for connection2 in connections2:
                    queue.append( ( dock_control2, connection2 ) )

            # Only activate it if we haven't already activated something in the
            # same notebook:
            region = dock_control2.parent
            if region in regions:
                continue

            regions.append( region )

            # OK, passed all tests...activate it:
            dock_control2.activate( False )

    #-- Class Attributes -------------------------------------------------------

    # The mapping of permanent, persisted connections to DockWindow id's:
    permanent_connections = {}

    # The mapping from objects to their set of currently active connections:
    active_connections = WeakKeyDictionary()

    #-- Overidable Class Methods -----------------------------------------------

    @classmethod
    def feature_for ( cls, dock_control ):
        """ Returns a new feature object for a specified DockControl (or None
            if the feature does not apply to it).
        """
        object  = dock_control.object
        context = dock_control.control.parent.owner.id
        if isinstance( object, HasFacets ) and (context != ''):
            # Only proceed if there is a valid HasFacets object and a DockWindow
            # which has a persistent id to use as a context:
            connectable_facets = object.facets( connect = can_connect )
            if len( connectable_facets ) > 0:
                context += '.Connections'
                result   = cls( dock_control       = dock_control,
                                connectable_facets = connectable_facets,
                                context            = context )

                # Get the current permanent connections for this Dockwindow:
                connections = cls.get_permanent_connections( context )

                # Get the currently active connections for the object:
                active = cls.active_connections.get( object, [] )

                # Restore any permanent connections this feature may be in:
                name1         = dock_control.name
                dock_controls = dock_control.dock_controls
                for c in connections:
                    if (name1 == c.label1) or (name1 == c.label2):
                        for ac in active:
                            if c == ac:
                                break
                        else:
                            for dc in dock_controls:
                                for feature2 in dc.features:
                                    if isinstance( feature2, ConnectFeature ):
                                        break
                                else:
                                    continue

                                name2 = dc.name
                                if name2 == c.label1:
                                    feature2.make_connection( c.clone().set(
                                        feature1 = feature2,
                                        object1  = dc.object,
                                        feature2 = result,
                                        object2  = object ), False )
                                elif name2 == c.label2:
                                    result.make_connection( c.clone().set(
                                        feature2 = feature2,
                                        object2  = dc.object,
                                        feature1 = result,
                                        object1  = object ), False )

                return result

        return None


    @classmethod
    def get_permanent_connections ( cls, context ):
        connections = cls.permanent_connections.get( context )
        if connections is None:
            connections = facet_db.get( context, [] )
            cls.permanent_connections[ context ] = connections

        return connections

#-------------------------------------------------------------------------------
#  'Connection' class:
#-------------------------------------------------------------------------------

class Connection ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The first object in the connection:
    object1 = Instance( HasFacets )

    # The name of the facet connected on that object:
    name1 = Str

    # The user friendly name of the facet connected on that object:
    ui_name1 = Str

    # The ConnectFeature for that object:
    feature1 = Instance( ConnectFeature )

    # Label of the object:
    label1 = Str

    # The second object in the connection:
    object2 = Instance( HasFacets )

    # The name of the facet on that object:
    name2 = Str

    # The user friendly name of the facet connected on that object:
    ui_name2 = Str

    # The ConnectFeature for that object:
    feature2 = Instance( ConnectFeature )

    # Label of the object:
    label2 = Str

    # The direction of the connection:
    connection = Enum( 'to', 'from', 'both' )

    #-- Public Methods ---------------------------------------------------------

    def connect ( self ):
        """ Connects the objects.
        """
        # Mark the connection as 'active' on both ends of the connection:
        ac = ConnectFeature.active_connections
        ac.setdefault( self.object1, [] ).append( self )
        ac.setdefault( self.object2, [] ).append( self )

        connection = self.connection
        if connection in ( 'from', 'both' ):
            self.object1.on_facet_set( self.connect_from, self.name1,
                                       dispatch = 'ui' )
            self.connect_from( getattr( self.object1, self.name1 ) )

        if connection in ( 'to', 'both' ):
            self.object2.on_facet_set( self.connect_to, self.name2,
                                       dispatch = 'ui' )
            if connection == 'to':
                self.connect_to( getattr( self.object2, self.name2 ) )


    def disconnect ( self ):
        """ Disconnects the objects.
        """
        # Remove the connection from both ends list of 'active' connections:
        ac = ConnectFeature.active_connections
        self.drop_connection( ac, self.object1 )
        self.drop_connection( ac, self.object2 )

        connection = self.connection
        if connection in ( 'from', 'both' ):
            self.object1.on_facet_set( self.connect_from, self.name1,
                                       remove = True )

        if connection in ( 'to', 'both' ):
            self.object2.on_facet_set( self.connect_to, self.name2,
                                       remove = True )


    def drop_connection ( self, active_connections, object ):
        """ Remove this connection from a specified object's list of active
            connections.
        """
        connections = active_connections[ object ]
        for i, c in enumerate( connections ):
            if c == self:
                del connections[i]
                if len( connections ) == 0:
                    del active_connections[ object ]

                break


    def connect_from ( self, value ):
        """ Copies a value from object1 to object2.
        """
        if not self._frozen:
            self._frozen = True
            try:
                setattr( self.object2, self.name2, value )
            except:
                pass
            self._frozen = False


    def connect_to ( self, value ):
        """ Copies a value from object1 to object2.
        """
        if not self._frozen:
            self._frozen = True
            try:
                setattr( self.object1, self.name1, value )
            except:
                pass
            self._frozen = False


    def clone ( self ):
        """ Returns a persistable clone of this connection.
        """
        return self.clone_facets( [ 'name1', 'label1', 'name2', 'label2',
                                    'connection' ] )


    def __eq__ ( self, other ):
        return (isinstance( other, Connection )  and
               (self.name1      == other.name1)  and
               (self.label1     == other.label1) and
               (self.name2      == other.name2)  and
               (self.label2     == other.label2) and
               (self.connection == other.connection))


    def __ne__ ( self, other ):
        return ( not self.__eq__( other ) )

#-- EOF ------------------------------------------------------------------------