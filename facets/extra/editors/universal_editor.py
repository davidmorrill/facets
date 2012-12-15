"""
Defines the UniversalEditor for displaying Python values.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, Range, View, UItem, UIEditor, BasicEditorFactory

from facets.extra.tools.universal_inspector \
    import UniversalInspector

#-------------------------------------------------------------------------------
#  '_UniversalEditor' class:
#-------------------------------------------------------------------------------

class _UniversalEditor ( UIEditor ):
    """ Defines the implementation of the editor class for viewing Python
        values.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Mark the editor as scrollable. This value overrides the default:
    scrollable = True

    # The UniversalInspector tool used to view the Python values:
    inspector = Instance( UniversalInspector, () )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'inspector', style = 'custom' )
    )

    #-- Editor Method Overrides ------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        self.inspector.max_inspectors = \
            self.factory.facet_value( 'max_inspectors' )

        return self.edit_facets( parent = parent, kind = 'editor' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.inspector.item = self.value

#-------------------------------------------------------------------------------
#  'UniversalEditor' class:
#-------------------------------------------------------------------------------

class UniversalEditor ( BasicEditorFactory ):
    """ Defines an editor class for viewing Python values.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _UniversalEditor

    # Maximum number of open inspectors allowed:
    max_inspectors = Range( 1, 50, 1, facet_value = True )

#-- EOF ------------------------------------------------------------------------
