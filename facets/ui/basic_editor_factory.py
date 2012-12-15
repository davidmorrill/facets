"""
Defines the BasicEditorFactory class, which allows creating editor
factories that use the same class for creating all editor styles.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Any

from editor_factory \
    import EditorFactory

#-------------------------------------------------------------------------------
#  'BasicEditorFactory' base class:
#-------------------------------------------------------------------------------

class BasicEditorFactory ( EditorFactory ):
    """ Base class for editor factories that use the same class for creating
        all editor styles.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Editor class to be instantiated:
    klass = Any

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return self.klass( factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = name,
                           description = description )


    def custom_editor ( self, ui, object, name, description ):
        return self.klass( factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = name,
                           description = description )


    def text_editor ( self, ui, object, name, description ):
        return self.klass( factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = name,
                           description = description )


    def readonly_editor ( self, ui, object, name, description ):
        return self.klass( factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = name,
                           description = description )

    #-- Public Method Overrides ------------------------------------------------

    def __call__ ( self, *args, **facets ):
        return self.set( **facets )

#-- EOF ------------------------------------------------------------------------