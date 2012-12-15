"""
Defines the various Boolean editors and the Boolean editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Dict, Str, Any, View, Editor

from facets.ui.toolkit \
    import toolkit

from facets.ui.colors \
    import ReadonlyColor

from text_editor \
    import TextEditor, SimpleEditor as StandardTextEditor

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Mapping from user input text to Boolean values
mapping_facet = Dict( Str, Any, {
    'True':  True,
    'true':  True,
    't':     True,
    'yes':   True,
    'y':     True,
    'False': False,
    'false': False,
    'f':     False,
    'no':    False,
    'n':     False,
} )

#-------------------------------------------------------------------------------
#  'BooleanEditor' class:
#-------------------------------------------------------------------------------

class BooleanEditor ( TextEditor ):
    """ Editor factory for Boolean editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Dictionary mapping user input to other values.
    # These definitions override definitions in the 'text_editor' version
    mapping = mapping_facet

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View()

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

    def custom_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

    def text_editor ( self, ui, object, name, description ):
        return StandardTextEditor( factory     = self,
                                   ui          = ui,
                                   object      = object,
                                   name        = name,
                                   description = description )

    def readonly_editor ( self, ui, object, name, description ):
        return ReadonlyEditor( factory     = self,
                               ui          = ui,
                               object      = object,
                               name        = name,
                               description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style of editor for Boolean values, which displays a check box.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.adapter = toolkit().create_checkbox( parent )
        self.adapter.set_event_handler( checked = self.update_object )

        self.set_tooltip()


    def update_object ( self, event ):
        """ Handles the user clicking the checkbox.
        """
        self.value = (self.adapter.value != 0)


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.adapter.value = self.value


    def dispose ( self ):
        """ Disposes of the editor.
        """
        self.adapter.unset_event_handler( checked = self.update_object )

        super( SimpleEditor, self ).dispose()

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( Editor ):
    """ Read-only style of editor for Boolean values, which displays static text
        of either "True" or "False".
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.adapter = toolkit().create_text_input( parent, read_only = True )
        self.adapter.background_color = ReadonlyColor

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self.value:
            self.adapter.value = 'True'
        else:
            self.adapter.value = 'False'

#-- EOF ------------------------------------------------------------------------