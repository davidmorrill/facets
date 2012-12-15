"""
Facets UI MS Internet Explorer editor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

if wx.Platform == '__WXMSW__':
    import  wx.lib.iewin as iewin

from facets.core_api \
    import Str, Event, Property

from facets.ui.wx.editors.editor \
    import Editor

from facets.ui.wx.editors.basic_editor_factory \
    import BasicEditorFactory

#-------------------------------------------------------------------------------
#  '_IEHTMLEditor' class:
#-------------------------------------------------------------------------------

class _IEHTMLEditor ( Editor ):
    """ Facets UI MS Internet Explorer editor.
    """

    #---------------------------------------------------------------------------
    #  Facet definitions:
    #---------------------------------------------------------------------------

    # Is the table editor is scrollable? This value overrides the default.
    scrollable = True

    # Event fired when the browser home page should be displayed:
    home = Event

    # Event fired when the browser should show the previous page:
    back = Event

    # Event fired when the browser should show the next page:
    forward = Event

    # Event fired when the browser should stop loading the current page:
    stop = Event

    # Event fired when the browser should refresh the current page:
    refresh = Event

    # Event fired when the browser should search the current page:
    search = Event

    # The current browser status:
    status = Str

    # The current browser page title:
    title = Str

    # The URL of the page that just finished loading:
    page_loaded = Str

    # The current page content as HTML:
    html = Property

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = ie = iewin.IEHtmlWindow( parent, -1,
                                      style = wx.NO_FULL_REPAINT_ON_RESIZE )
        self.set_tooltip()

        factory = self.factory
        self.sync_value( factory.home,        'home',        'from' )
        self.sync_value( factory.back,        'back',        'from' )
        self.sync_value( factory.forward,     'forward',     'from' )
        self.sync_value( factory.stop,        'stop',        'from' )
        self.sync_value( factory.refresh,     'refresh',     'from' )
        self.sync_value( factory.search,      'search',      'from' )
        self.sync_value( factory.status,      'status',      'to' )
        self.sync_value( factory.title,       'title',       'to' )
        self.sync_value( factory.page_loaded, 'page_loaded', 'to' )
        self.sync_value( factory.html,        'html',        'to' )

        parent.Bind( iewin.EVT_StatusTextChange, self._status_modified, ie )
        parent.Bind( iewin.EVT_TitleChange,      self._title_modified,  ie )
        parent.Bind( iewin.EVT_DocumentComplete, self._page_loaded_modified,
                     ie )
        parent.Bind( iewin.EVT_NewWindow2,       self._new_window_modified, ie )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object facet changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        value = self.str_value.strip()

        if value[ : 1 ] == '<':
            self.control.LoadString( value )
            return

        if ( value[ : 4 ] != 'http' ) or ( value.find( '://' ) < 0 ):
            try:
                file = open( value, 'rb' )
                self.control.LoadStream( file )
                file.close()
                return
            except:
                pass

        self.control.Navigate( value )

    #-- Property Implementations -----------------------------------------------

    def _get_html ( self ):
        return self.control.GetText()

    def _set_html ( self, value ):
        self.control.LoadString( value )

    #-- Facet Event Handlers ---------------------------------------------------

    def _home_set ( self ):
        self.control.GoHome()

    def _back_set ( self ):
        self.control.GoBack()

    def _forward_set ( self ):
        self.control.GoForward()

    def _stop_set ( self ):
        self.control.Stop()

    def _refresh_set ( self ):
        self.control.Refresh( iewin.REFRESH_COMPLETELY )

    def _search_set ( self ):
        self.control.GoSearch()

    def _status_modified ( self, event ):
        self.status = event.Text

    def _title_modified ( self, event ):
        self.title = event.Text

    def _page_loaded_modified ( self, event ):
        self.page_loaded = event.URL
        self.facet_property_set( 'html', '', self.html )

    def _new_window_modified ( self, event ):
        # If the event is cancelled, new windows can be disabled.
        # At this point we've opted to allow new windows
        pass

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for MS Internet Explorer editors:
class IEHTMLEditor ( BasicEditorFactory ):

    # The editor class to be created:
    klass = _IEHTMLEditor

    # Optional name of facet used to tell browser to show Home page:
    home = Str

    # Optional name of facet used to tell browser to view the previous page:
    back = Str

    # Optional name of facet used to tell browser to view the next page:
    forward = Str

    # Optional name of facet used to tell browser to stop loading page:
    stop = Str

    # Optional name of facet used to tell browser to refresh the current page:
    refresh = Str

    # Optional name of facet used to tell browser to search the current page:
    search = Str

    # Optional name of facet used to contain the current browser status:
    status = Str

    # Optional name of facet used to contain the current browser page title:
    title = Str

    # Optional name of facet used to contain the URL of the page that just
    # completed loading:
    page_loaded = Str

    # Optional name of facet used to get/set the page content as HTML:
    html = Str

#-- EOF ------------------------------------------------------------------------