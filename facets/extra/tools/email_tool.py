"""
Defines the email tool for sending plain, HTML and markdown formatted emails.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import dirname, join, splitext, isfile

from smtplib \
    import SMTP

from email.mime.multipart \
    import MIMEMultipart

from email.mime.text \
    import MIMEText

from facets.api \
    import Str, Int, Bool, Button, Property, View, HGroup, VGroup, UItem,     \
           Item, TextEditor, HistoryEditor, HTMLEditor, ThemedCheckboxEditor, \
           property_depends_on

from facets.core.facet_base \
    import read_file

from tools \
    import Tool

import facets.extra.markdown.markdown2 as markdown2

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Specially recognized content types:
ContentTypes = ( '.md', '.htm', '.html' )

# The HTML template used to create a web page from converted markdown text:
HTMLTemplate = """
<!DOCTYPE html>
<html>
  <head>
    <title>Markdown</title>
    <style type="text/css">
%s
    </style>
  </head>
  <body>
%s  </body>
</html>
"""[1:-1]

# The CSS to use when formatting markdown:
MarkdownCSS = ''

#-------------------------------------------------------------------------------
#  'Email' class:
#-------------------------------------------------------------------------------

class Email ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Email'

    # The subject of the e-mail:
    subject = Str

    # The content of the e-mail:
    content = Str( connect = 'to: email content or file name' )

    # The rendered body of the e-mail:
    body = Property # ( Str )

    # The e-mail address of the person sending the e-mail:
    sender = Str( save_state = True )

    # The password used to access the sender's account:
    password = Str( save_state = True )

    # The comma separated list of recipients for the e-mail:
    receivers = Str

    # The host name of the SMTP server the e-mail is transmitted to:
    host = Str( 'smtp.gmail.com', save_state = True )

    # The port number of the SMTP server the e-mail is transmitted to:
    port = Int( 587, save_state = True )

    # Is the e-mail ready to be sent?
    can_send = Property # ( Bool )

    # Event fired when the user wants to send the e-mail:
    send = Button( 'Send' )

    # Should text input be interpreted as markdown:
    is_markdown = Bool( True )

    # Is the 'body' of the email HTML?
    is_html = Bool( False )

    #-- Facet View Definitions -------------------------------------------------

    facets_view = View(
        HGroup(
            Item( 'subject', springy = True ),
            UItem( 'is_markdown',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@facets:method',
                       off_image   = '@facets:method?L6s',
                       on_tooltip  = 'Input is markdown',
                       off_tooltip = 'Input is plain text' )
            ),
            group_theme = '#themes:tool_options_group'
        ),
        HGroup(
            Item( 'receivers',
                  id      = 'receivers',
                  label   = 'Send to',
                  springy = True,
                  editor  = HistoryEditor( entries = 20 )
            ),
            UItem( 'send', enabled_when = 'can_send' ),
            group_theme = '#themes:tool_options_group'
        ),
        VGroup(
            UItem( 'body', editor = HTMLEditor() ),
            group_theme = '#themes:tool_options_group'
        ),
        id     = 'facets.extra.tools.email_tool.Email',
        width  = 0.5,
        height = 0.5
    )

    options = View(
        HGroup(
            VGroup(
                Item( 'sender' ),
                Item( 'password', editor = TextEditor( password = True ) ),
                group_theme = '#themes:tool_options_group'
            ),
            VGroup(
                Item( 'host' ),
                Item( 'port' ),
                group_theme = '#themes:tool_options_group'
            ),
        )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'sender, password, receivers, host, port, subject, body' )
    def _get_can_send ( self ):
        return (
            (self.subject.strip()   != '') and
            (self.body.strip()      != '') and
            (self.sender.strip()    != '') and
            (self.password.strip()  != '') and
            (self.host.strip()      != '') and
            (self.receivers.strip() != '') and
            (0 < self.port < 65536)
        )


    @property_depends_on( 'content, is_markdown' )
    def _get_body ( self ):
        is_markdown = self.is_markdown
        content     = self.content
        if content.find( '\n' ) < 0:
           ext = splitext( content )[1].lower()
           if (ext in ContentTypes) and isfile( content ):
               content     = read_file( content )
               is_markdown = (ext == '.md')

        if is_markdown:
            content = self._convert_markdown( content )

        cl           = content.lower()
        self.is_html = ((cl.find( '<html>' )  >= 0) and
                        (cl.find( '</html>' ) >= 0))

        return content


    def _send_set ( self ):
        """ Handles the 'send' button being clicked.
        """
        sender    = self.sender.strip()
        receivers = self.receivers.strip()

        # Create a message container with MIME type multipart/alternative:
        msg = MIMEMultipart( 'alternative' )
        msg[ 'Subject' ] = self.subject.strip()
        msg[ 'From' ]    = sender
        msg[ 'To' ]      = receivers

        # Attach the correctly encoded message into message container:
        msg.attach(
            MIMEText( self.body.strip(), 'html' if self.is_html else 'plain' )
        )

        # Send the message to the SMTP server:
        server = SMTP( self.host.strip(), self.port )
        #server.set_debuglevel( 1 ) # <-- Comment out to avoid debug messages
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login( sender, self.password )
        server.sendmail(
            sender,
            [ receiver.strip() for receiver in receivers.split( ',' ) ],
            msg.as_string()
        )
        server.quit()

        self.subject = self.receivers = ''

    #-- Private Methods --------------------------------------------------------

    def _convert_markdown ( self, text ):
        """Returns the HTML representation of the markdown formatted text
           represented by *text*.
        """
        global MarkdownCSS, HTMLTemplate

        if MarkdownCSS == '':
            MarkdownCSS = read_file(
                join( dirname( markdown2.__file__ ), 'default.css' )
            )

        return (HTMLTemplate % ( MarkdownCSS, markdown2.markdown( text ) ))

#-- Run the tool (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    Email().edit_facets()

#-- EOF ------------------------------------------------------------------------
