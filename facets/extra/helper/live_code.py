"""
Defines the LiveCode class, a component for developing code using live objects.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from time \
    import strftime

from facets.api \
    import HasFacets, HasPrivateFacets, DelegatesTo, Any, Str, Bool, Range, \
           Button, Instance, View, UItem, ThemedCheckboxEditor, toolkit

from facets.ui.pyface.timer.api \
    import do_after

from facets.extra.tools.text_file \
    import TextFile

#-------------------------------------------------------------------------------
#  'LiveCode' class:
#-------------------------------------------------------------------------------

class LiveCode ( HasPrivateFacets ):
    """ Defines the LiveCode class, a component for developing code using live
        objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The code being developed:
    code = DelegatesTo( 'text_file', 'text' )

    # The name of the live code object within the source:
    target = Str( 'demo' )

    # The class the live object must be an instance of:
    klass = Any( HasFacets )

    # Should the code be reloaded each time the source code is modified?
    auto_reload = Bool( False )

    # The delay (in milliseconds) after which modified 'auto_reload' code is
    # reloaded:
    reload_delay = Range( 100, 5000, 1000 )

    # Event fired when the code should be reloaded:
    reload = Button( '@icons2:GearExecute' )

    # Event fired when the source code should be copied to the clipboard:
    copy_to_clipboard = Button( '@icons2:Clipboard' )

    # The object created from the live code:
    object = Any

    # The TextFile object used to edit the code:
    text_file = Instance( TextFile )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'text_file', style = 'custom' )
    )

    #-- Facet Default Values ---------------------------------------------------

    def _text_file_default ( self ):
        return TextFile( toolbar_items = [
            UItem( 'context.auto_reload',
                   editor = ThemedCheckboxEditor(
                       image       = '@icons2:Synchronize',
                       on_tooltip  = 'Source is automatically reloaded on '
                                     'change (click to disable)',
                       off_tooltip = 'Source is not automatically reloaded on '
                                     'change (click to enable)'
                   )
            ),
            UItem( 'context.reload',
                   enabled_when = 'not context.auto_reload',
                   tooltip      = 'Reload the source code'
            ),
            UItem( 'context.copy_to_clipboard',
                   tooltip = 'Copy source code to clipboard'
            )
        ] )

    #-- Facet Event Handlers ---------------------------------------------------

    def _copy_to_clipboard_set ( self ):
        """ Handles the 'copy_to_clipboard' facet being changed.
        """
        toolkit().clipboard().text = self.code.rstrip()


    def _reload_set ( self ):
        """ Handles the 'reload' event being fired.
        """
        self._reload_code()


    def _auto_reload_set ( self ):
        """ Handles the 'auto_reload' facet being changed.
        """
        if self.auto_reload:
            self._reload_code()


    def _code_set ( self ):
        """ Handles the 'code' facet being changed.
        """
        if self.auto_reload:
            do_after( self.reload_delay, self._reload_code )


    def _target_set ( self ):
        """ Handles the 'target' facet being changed.
        """
        if self.auto_reload:
            do_after( self.reload_delay, self._reload_code )

    #-- Private Methods --------------------------------------------------------

    def _reload_code ( self ):
        """ Attempts to reload the code to define a new live object.
        """
        dic = {}
        try:
            exec self.code in dic, dic
        except Exception, excp:
            msg   = str( excp )
            match = re.search( r'(.*)\(<string>,\s*line\s+(\d+)\)', msg )
            if match:
                msg = match.group( 1 )
                self.text_file.selected_line = int( match.group( 2 ) )

            items    = msg.split( ' ', 1 )
            items[0] = items[0].capitalize()
            self.text_file.status = ' '.join( items )

            return

        target = self.target
        object = dic.get( target )
        if object is not None:
            klass = self.klass
            if ((klass is not None) and
                (not isinstance( object, klass )) and
                callable( object )):
                object = object()

            if object is not None:
                if (klass is not None) and isinstance( object, klass ):
                    self.object = object
                    self.text_file.status = ("New '%s' object loaded "
                        "successfully at %s" %
                        ( target, strftime( '%I:%M:%S %p' ) ))
                else:
                    self.text_file.status = ("New '%s' object is not a '%s' "
                        "instance" % ( target, klass.__name__ ))
            else:
                self.text_file.status = ("The new '%s' object is None." %
                                         target)
        else:
            self.text_file.status = ("The code does not contain a '%s' object" %
                                     target)

#-- Run the test case (if invoked from the command line) -----------------------

if __name__ == '__main__':
    from facets.api \
        import Instance, ValueEditor, InstanceEditor, PropertySheetEditor, \
               HSplit, VSplit

    class LiveCodeTest ( HasPrivateFacets ):
        live_code = Instance( LiveCode, () )

        view = View(
            HSplit(
                UItem( 'live_code', style = 'custom' ),
                VSplit(
                    UItem( 'object.live_code.object',
                           editor = ValueEditor(),
                           dock   = 'tab'
                    ),
                    UItem( 'object.live_code.object',
                           editor = PropertySheetEditor( monitor = 'all' ),
                           dock   = 'tab'
                    ),
                    UItem( 'object.live_code.object',
                           style  = 'custom',
                           editor = InstanceEditor(),
                           dock   = 'tab'
                    )
                ),
                id = 'splitter'
            ),
            width  = 0.9,
            height = 0.9
        )

    LiveCodeTest().edit_facets()

#-- EOF ------------------------------------------------------------------------
