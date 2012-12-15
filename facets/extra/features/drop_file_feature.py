"""
Defines a 'drop_file' feature which allows the object associated with a
DockControl to expose a facet which can accept files dropped onto it. The facet
can either accept strings (i.e. file names), FilePosition objects, or lists of
the above. The facet which accepts files should have 'drop_file' metadata, which
can either be True, a file suffix (e.g. '.py'), a list of file extensions, or a
DropFile object. If file extensions are specified, then only files with
corresponding extensions can be dropped on the view.

Specifying a DropFile object as the 'drop_file' metadata also provides the
option of making the facet draggable, as well as specifying a custom tooltip.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import exists, splitext

from facets.core_api \
    import HasFacets, Str, List, Enum, Bool

from facets.ui.pyface.api \
    import FileDialog, OK

from facets.ui.dock.api \
    import DockWindowFeature

from facets.ui.ui_facets \
    import image_for

from facets.lib.io.api \
    import File

from facets.extra.api \
    import HasPayload, FilePosition

from feature_metadata \
    import DropFile

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

a_file_position = FilePosition()

# Valid 'drop styles' and their corresponding types:
valid_types = (
    ( 'file_positions', [ a_file_position ] ),
    ( 'file_position',  a_file_position ),
    ( 'file_names',     [ '\\test' ] ),
    ( 'file_name',      '\\test' )
)

# Feature images:
feature_images = (
    image_for( '@facets:drop_file_feature' ),
    image_for( '@facets:drag_file_feature' )
)

#-------------------------------------------------------------------------------
#  Defines the 'drop_file' metadata filter:
#-------------------------------------------------------------------------------

def drop_file_filter ( value ):
    return ((value is True) or
            isinstance( value, ( str, list, tuple, DropFile ) ))

#-------------------------------------------------------------------------------
#  'DropFileFeature' class:
#-------------------------------------------------------------------------------

class DropFileFeature ( DockWindowFeature ):

    #-- Class Constants --------------------------------------------------------

    # The user interface name of the feature:
    feature_name = 'Drag and Drop Files'

    #-- Facet Definitions ------------------------------------------------------

    # The facet on the object to assign dropped files to:
    name = Str

    # The list of valid extensions for dropped files:
    extensions = List( Str )

    # Is the facet also draggable?
    draggable = Bool( False )

    # The type of value expected by the facet:
    drop_style = Enum( 'file_name',     'file_names',
                       'file_position', 'file_positions' )

    #-- DockWindowFeature Method Overrides -------------------------------------

    def click ( self ):
        """ Handles the user left clicking on the feature image.
        """
        # Create the file dialog:
        fd = FileDialog()

        # Set up the default path based on the current value (if any):
        default_path = getattr( self.dock_control.object, self.name, None )
        if default_path is not None:
            fd.default_path = default_path

        # Set up the appropriate extension filters (if any):
        if len( self.extensions ) > 0:
            fd.wildcard = '\n'.join( [
                FileDialog.create_wildcard( '', '*' + ext )
                for ext in self.extensions
            ] )

        # Display the file dialog, and if successful, set the new file name:
        if fd.open() == OK:
            self.drop( fd.path )


    def drag ( self ):
        """ Returns the object to be dragged when the user drags the feature
            image.
        """
        if self.draggable:
            result = getattr( self.dock_control.object, self.name, None )
            if result:
                return result

        return None


    def drop ( self, object ):
        """ Handles the user dropping a specified object on the feature image.
        """
        # Extract the list of FilePositions to be assigned:
        if isinstance( object, FilePosition ):
            file_positions = [ object ]
        elif isinstance( object, HasPayload ):
            file_positions = [ FilePosition( file_name = object.payload ) ]
        elif isinstance( object, basestring ):
            file_positions = [ FilePosition( file_name = object ) ]
        else:
            file_positions = [ FilePosition( file_name = file.absolute_path )
                               for file in object ]

        # Assign them using the correct 'drop_style':
        getattr( self, '_drop_' + self.drop_style )( file_positions )


    def can_drop ( self, object ):
        """ Returns whether a specified object can be dropped on the feature
            image.
        """
        if isinstance( object, FilePosition ):
            file_names = [ object.file_name ]
        elif ( isinstance( object, HasPayload ) and
              isinstance( object.payload, str ) ):
            file_names = [ object.payload ]
        elif isinstance( object, basestring ) and exists( object ):
            file_names = [ object ]
        elif isinstance( object, list ):
            file_names = [ file.absolute_path for file in object
                           if isinstance( file, File ) ]
            if len( file_names ) != len( object ):
                return False
        else:
            return False

        extensions = self.extensions
        if len( extensions ) == 0:
            return True

        for file_name in file_names:
            ext = splitext( file_name )[1]
            if ext not in extensions:
                return False

        return True

    #-- Private Methods --------------------------------------------------------

    def _drop_file_name ( self, file_positions ):
        """ Drops a single file name.
        """
        object = self.dock_control.object
        name   = self.name
        for fp in file_positions:
            setattr( object, name, fp.file_name )


    def _drop_file_position ( self, file_positions ):
        """ Drops a single file name.
        """
        object = self.dock_control.object
        name   = self.name
        for fp in file_positions:
            setattr( object, name, fp )


    def _drop_file_names ( self, file_positions ):
        """ Drops a list of file names.
        """
        setattr( self.dock_control.object, self.name,
                 [ fp.file_name for fp in file_positions ] )


    def _drop_file_positions ( self, file_positions ):
        """ Drops a list of file names.
        """
        setattr( self.dock_control.object, self.name, file_positions )


    def _set_image ( self ):
        """ Set the correct images based on the current 'draggable' setting.
        """
        self.image = feature_images[ self.draggable ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _draggable_set ( self, draggable ):
        """ Handles the 'draggable' facet being changed.
        """
        self._set_image()

    #-- Overridable Class Methods ----------------------------------------------

    @classmethod
    def feature_for ( cls, dock_control ):
        """ Returns a feature object for use with the specified DockControl (or
            None if the feature does not apply to the DockControl object).
        """
        object = dock_control.object
        if isinstance( object, HasFacets ):
            facets = object.facets( drop_file = drop_file_filter )
            if len( facets ) == 1:
                name, facet = facets.items()[0]
                drop_file   = facet.drop_file
                draggable   = False
                tooltip     = ''

                # Determine the set of valid file extensions and generate a
                # corresponding tooltip to describe them:
                if isinstance( drop_file, DropFile ):
                    extensions = drop_file.extensions
                    draggable  = drop_file.draggable
                    tooltip    = drop_file.tooltip
                elif isinstance( drop_file, basestring ):
                    extensions = [ drop_file ]
                elif isinstance( drop_file, ( list, tuple ) ):
                    extensions = list( drop_file )
                else:
                    extensions = []

                if tooltip == '':
                    if draggable:
                        tooltip = 'Drag this file.\n'

                    exts = ', '.join( extensions )
                    if len( exts ) > 0:
                        exts += ' '

                    tooltip += 'Drop a %sfile here.' % exts

                # Determine the type of value the facet accepts and save it as
                # the feature's 'drop_style':
                for drop_style, type in valid_types:
                    try:
                        facet.validate( object, name, type )

                        break
                    except:
                        pass
                else:
                    # Doesn't accept any type we know how to make...give up!
                    return None

                # Return the feature for this object:
                result = cls(
                    dock_control = dock_control,
                    name         = name,
                    drop_style   = drop_style,
                    extensions   = extensions,
                    draggable    = draggable,
                    tooltip      = tooltip
                )
                result._set_image()

                return result

        # Indicate this feature does not apply to this object:
        return None

#-- EOF ------------------------------------------------------------------------