"""
Defines an editor for playing animated GIF files.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.api \
    import Bool, Str, BasicEditorFactory

from editor \
    import Editor


# Define the wx version dependent version of the editor:
if wx.__version__[:3] == '2.6':

    #---------------------------------------------------------------------------
    #  Imports:
    #---------------------------------------------------------------------------

    from wx.animate \
        import GIFAnimationCtrl

    from facets.ui.pyface.timer.api \
        import do_after

    #---------------------------------------------------------------------------
    #  '_AnimatedGIFEditor' class:
    #---------------------------------------------------------------------------

    class _AnimatedGIFEditor ( Editor ):
        """ Editor that displays an animated GIF file.
        """

        #-- Facet Definitions --------------------------------------------------

        # Is the animated GIF file currently playing?
        playing = Bool( True )

        #-- Public Methods -----------------------------------------------------

        def init ( self, parent ):
            """ Finishes initializing the editor by creating the underlying
                toolkit widget.
            """
            self.control = GIFAnimationCtrl( parent, -1 )
            self.control.GetPlayer().UseBackgroundColour( True )
            self.sync_value( self.factory.playing, 'playing', 'from' )
            self.set_tooltip()


        def update_editor ( self ):
            """ Updates the editor when the object facet changes externally to
                the editor.
            """
            control = self.control
            if self.playing:
                control.Stop()

            control.LoadFile( self.value )
            self._file_loaded = True

            # Note: It seems to be necessary to Play/Stop the control to avoid a
            # hard wx crash when 'PlayNextFrame' is called the first time (must
            # be some kind of internal initialization issue):
            control.Play()
            control.Stop()

            if self.playing or self._not_first:
                self._playing_set()
            else:
                do_after( 300, self._frame_changed )

            self._not_first = True

        #-- Facet Event Handlers -----------------------------------------------

        def _playing_set ( self ):
            """ Handles the editor 'playing' facet being changed.
            """
            if self._file_loaded:
                try:
                    if self.playing:
                        self.control.Play()
                    else:
                        player = self.control.GetPlayer()
                        player.SetCurrentFrame( 0 )
                        player.PlayNextFrame()
                        player.Stop()
                except:
                    pass

else:

    #---------------------------------------------------------------------------
    #  Imports:
    #---------------------------------------------------------------------------

    from wx.animate \
        import Animation, AnimationCtrl

    #---------------------------------------------------------------------------
    #  '_AnimatedGIFEditor' class:
    #---------------------------------------------------------------------------

    class _AnimatedGIFEditor ( Editor ):
        """ Editor that displays an animated GIF file.
        """

        #-- Facet Definitions --------------------------------------------------

        # Is the animated GIF file currently playing?
        playing = Bool( True )

        #-- Public Methods -----------------------------------------------------

        def init ( self, parent ):
            """ Finishes initializing the editor by creating the underlying
                toolkit widget.
            """
            self._animate = Animation( self.value )
            self.control  = AnimationCtrl( parent, -1, self._animate )
            self.control.SetUseWindowBackgroundColour()
            self.sync_value( self.factory.playing, 'playing', 'from' )
            self.set_tooltip()


        def update_editor ( self ):
            """ Updates the editor when the object facet changes externally to
                the editor.
            """
            if not self.playing:
                self.control.Stop()

            self.control.LoadFile( self.value )
            self._file_loaded = True

            if self.playing:
                self.control.Play()


        def _playing_set ( self ):
            if self._file_loaded:
                if self.playing:
                    self.control.Play()
                else:
                    self.control.Stop()

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for animated GIF editors:
class AnimatedGIFEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _AnimatedGIFEditor

    # The optional facet used to control whether the animated GIF file is
    # playing or not:
    playing = Str

#-- EOF ------------------------------------------------------------------------