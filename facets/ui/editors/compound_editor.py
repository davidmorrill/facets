"""
Defines the compound editor and the compound editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import List, Str, Bool, toolkit, EditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# List of component editor factories used to build a compound editor
editors_facet = List( EditorFactory )

#-------------------------------------------------------------------------------
#  'CompoundEditor' class:
#-------------------------------------------------------------------------------

class CompoundEditor ( EditorFactory ):
    """ wxPython editor factory for compound editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Component editor factories used to build the editor:
    editors  = editors_facet

    # Is user input set on every keystroke?
    auto_set = Bool( True )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return _CompoundEditor( factory     = self,
                                ui          = ui,
                                object      = object,
                                name        = name,
                                description = description,
                                kind        = 'simple_editor' )


    def custom_editor ( self, ui, object, name, description ):
        return _CompoundEditor( factory     = self,
                                ui          = ui,
                                object      = object,
                                name        = name,
                                description = description,
                                kind        = 'custom_editor' )

#-------------------------------------------------------------------------------
#  '_CompoundEditor' class:
#-------------------------------------------------------------------------------

class _CompoundEditor ( Editor ):
    """ Editor for compound facets, which displays editors for each of the
        combined facets, in the appropriate style.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The kind of editor to create for each list item
    kind = Str

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create a panel to hold all of the component facet editors:
        self.adapter = control = toolkit().create_panel( parent )
        layout       = toolkit().create_box_layout()

        # Add all of the component facet editors:
        self._editors = editors = []
        panel         = self.adapter()
        for factory in self.factory.editors:
            editor = getattr( factory, self.kind )( self.ui, self.object,
                                       self.name, self.description )
            editor.prepare( panel )
            layout.add( editor.adapter, stretch = 1 * editor.scrollable,
                        fill = editor.fill, top = 3, bottom = 3 )
            editors.append( editor )

        # Set-up the layout:
        control.layout = layout
        control.shrink_wrap()

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        pass


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        for editor in self._editors:
            editor.dispose()

        super( _CompoundEditor, self ).dispose()

#-- EOF ------------------------------------------------------------------------