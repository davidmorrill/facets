"""
Defines helper functions and classes used to define Qt-based facet editors and
facet editor factories.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os.path

from PySide.QtCore \
    import Qt, QObject, SIGNAL

from PySide.QtGui \
    import QPixmap, QPixmapCache, QApplication, QPushButton, QStyle, QIcon

from facets.core_api \
    import Enum, CFacet, BaseFacetHandler, FacetError

from facets.ui.ui_facets \
    import SequenceTypes, image_for

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum( 'horizontal', 'vertical' )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def pixmap_cache ( name ):
    """ Return the QPixmap corresponding to a filename.  If the filename does
        not contain a path component then the local 'images' directory is used.
    """
    if name[:1] == '@':
        image = image_for( name )
        if image is not None:
            return image.bitmap

    path, _ = os.path.split( name )
    if not path:
        name = os.path.join( os.path.dirname( __file__ ), 'images', name )

    pm = QPixmap()

    if not QPixmapCache.find( name, pm ):
        pm.load( name )
        QPixmapCache.insert( name, pm )

    return pm


def enum_values_changed ( values ):
    """ Recomputes the mappings for a new set of enumeration values.
    """

    if isinstance( values, dict ):
        data = [ ( str( v ), n ) for n, v in values.items() ]
        if len( data ) > 0:
            data.sort( lambda x, y: cmp( x[ 0 ], y[ 0 ] ) )
            col = data[ 0 ][ 0 ].find( ':' ) + 1
            if col > 0:
                data = [ ( n[ col: ], v ) for n, v in data ]
    elif not isinstance( values, SequenceTypes ):
        handler = values
        if isinstance( handler, CFacet ):
            handler = handler.handler

        if not isinstance( handler, BaseFacetHandler ):
            raise FacetError( "Invalid value for 'values' specified" )

        if handler.is_mapped:
            data = [ ( str( n ), n ) for n in handler.map.keys() ]
            data.sort( lambda x, y: cmp( x[ 0 ], y[ 0 ] ) )
        else:
            data = [ ( str( v ), v ) for v in handler.values ]
    else:
        data = [ ( str( v ), v ) for v in values ]

    names           = [ x[0] for x in data ]
    mapping         = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[ name ] = value
        inverse_mapping[ value ] = name

    return ( names, mapping, inverse_mapping )

#-------------------------------------------------------------------------------
#  'IconButton' class:
#-------------------------------------------------------------------------------

class IconButton ( QPushButton ):
    """ The IconButton class is a push button that contains a small image or a
        standard icon provided by the current style.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, icon, slot ):
        """ Initialise the button.  icon is either the name of an image file or
            one of the QStyle.SP_* values.
        """
        QPushButton.__init__( self )

        # Get the current style.
        sty = QApplication.instance().style()

        # Get the minimum icon size to use.
        ico_sz = sty.pixelMetric( QStyle.PM_ButtonIconSize )

        if isinstance( icon, basestring ):
            pm = pixmap_cache( icon )

            # Increase the icon size to accomodate the image if needed.
            pm_width = pm.width()
            pm_height = pm.height()

            if ico_sz < pm_width:
                ico_sz = pm_width

            if ico_sz < pm_height:
                ico_sz = pm_height

            ico = QIcon( pm )
        else:
            ico = sty.standardIcon( icon )

        # Configure the button.
        self.setIcon( ico )
        self.setMaximumSize( ico_sz, ico_sz )
        self.setFlat( True )
        self.setFocusPolicy( Qt.NoFocus )

        QObject.connect( self, SIGNAL( 'clicked()' ), slot )

#-- EOF ------------------------------------------------------------------------