"""
Allows creating 'permanent' debugging break points that work correctly even if
the original source file changes as long as the source file changes are not too
drastic, like deleting the line that oiginally contained the breakpoint.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import abspath

from facets.core_api \
    import HasPrivateFacets, SingletonHasPrivateFacets, Str, Int, Bool, List, \
           Dict

from facets.core.facets_env \
    import facets_env

from facets.core.facet_db \
    import facet_db

#-------------------------------------------------------------------------------
#  'SourceFile' class:
#-------------------------------------------------------------------------------

class SourceFile ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The file name of the source file:
    file_name = Str

    # The source lines associated with the source file:
    source = List( Str )

    # The line numbers containing break points:
    bp_lines = List( Int )

    # Additional break point information:
    bp_info = List

    # Was the list of break points modified?
    modified = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def save ( self, fh ):
        """ Saves all break points to a specified file handle.
        """
        if (len( self.bp_lines ) > 0) or self.modified:
            fh.write( self.file_name + '\n' )
            bp_info = self.bp_info
            for i, line in enumerate( self.bp_lines ):
                bp_type, code, end_line = bp_info[ i ]

                if code != '':
                    code = ':' + code

                type = ''
                if (code != '') or (bp_type != 'Breakpoint'):
                    type = '[%s%s]' % ( bp_type, code )

                source = self.source[ line - 1 ].strip()

                if end_line > line:
                    line = '%s,%s' % ( line, end_line )

                fh.write( '  %s%s:: %s\n' % ( line, type, source ) )


    def restore ( self ):
        """ Restores all break points and activates them in the FBI debugger.
        """
        from fbi import fbi_object, fbi_bdb

        file_name = self.file_name
        file_bps  = fbi_bdb.get_file_breaks( file_name ).copy()
        bp_info   = self.bp_info
        for i, line in enumerate( self.bp_lines ):
            bp_type, code, end_line = bp_info[ i ]
            code = code.replace( '[[nl]]', '\n' )
            for bp in list( file_bps ):
                if bp.line == line:
                    file_bps.remove( bp )
                    if ((bp.end_line == end_line) and
                        (bp.bp_type  == bp_type)  and
                        (bp.code     == code)):
                        break
            else:
                fbi_object.remove_break_point( file_name, line )
                fbi_object.add_break_point( file_name, line, bp_type, code,
                                            end_line )

        for bp in file_bps:
            fbi_object.remove_break_point( file_name, bp.line )


    def clear_bp ( self ):
        """ Clears (i.e. deletes) all break points in the source file.
        """
        del self.bp_lines[:]
        del self.bp_info[:]


    def set_bp ( self, line, text = None, bp_type = 'Breakpoint', code = '',
                             end_line = None ):
        """ Sets a break point on the specified line number. If the optional
            **text** argument is specified, it will check to see if the
            specified line matches the specified text, and if not, set the
            bp on the closest line matching the text. If no matching line is
            found, no breakpoint is set.
        """
        info = ( bp_type, code, end_line or line )
        if text is None:
            if 1 <= line <= len( self.source ):
                try:
                    i = self.bp_lines.index( line )
                    self.bp_info[i] = info
                except:
                    self.bp_lines.append( line )
                    self.bp_info.append( info )

            return

        text = text.strip()
        if text != '':
            delta  = 0
            source = self.source
            start  = max( line - 100, 1 )
            end    = min( line + 100, len( source ) )

            while True:
                done  = True
                tline = line + delta
                if tline <= end:
                    done = False
                    if text == source[ tline - 1 ].strip():
                        if tline not in self.bp_lines:
                            self.bp_lines.append( tline )
                            self.bp_info.append( info )

                        return

                tline = line - delta
                if tline >= start:
                    done = False
                    if text == source[ tline - 1 ].strip():
                        if tline not in self.bp_lines:
                            self.bp_lines.append( tline )
                            self.bp_info.append( info )

                        return

                if done:
                    break

                delta += 1


    def reset_bp ( self, line ):
        """ Resets (i.e. deletes) a break point on the specified line number.
        """
        try:
            i = self.bp_lines.index( line )
            del self.bp_lines[ i ]
            del self.bp_info[ i ]
        except:
            pass


    def toggle_bp ( self, line, bp_type = 'Breakpoint', code = '',
                                end_line = None ):
        """ Toggles the break point on the specified line number.
        """
        try:
            i = self.bp_lines.index( line )
            del self.bp_lines[i]
            del self.bp_info[i]
        except:
            self.bp_lines.append( line )
            self.bp_info.append( ( bp_type, code, end_line ) )

    #-- Facets Event Handlers --------------------------------------------------

    def _file_name_set ( self, file_name ):
        """ Handles the 'file_name' facet being changed.
        """
        fh = None
        try:
            fh = open( file_name, 'rb' )
            self.source = fh.readlines()
        except:
            pass

        if fh is not None:
            fh.close()


    def _bp_lines_items_set ( self ):
        """ Handles the list of break points being modified.
        """
        self.modified = True

#-------------------------------------------------------------------------------
#  'SavedBreakpoints' class:
#-------------------------------------------------------------------------------

class SavedBreakpoints ( SingletonHasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the saved break points file:
    file_name = Str

    # The source files containing break points. The keys are the fully
    # qualified source file names:
    source_files = Dict( Str, SourceFile )

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        if self.file_name == '':
            self.file_name = abspath( facets_env.bp or facet_db.db( 'fbi.bp' ) )


    def save ( self ):
        """ Saves the current set of break points back to the break point file.
        """
        fh = None
        try:
            fh = open( self.file_name, 'wb' )
            for source_file in self.source_files.values():
                source_file.save( fh )
        except:
            pass

        if fh is not None:
            fh.close()


    def restore ( self ):
        """ Restores all break points and activates them in the FBI debugger.
        """
        for source_file in self.source_files.values():
            source_file.restore()


    def source_file_for ( self, file_name ):
        """ Returns the SourceFile object corresponding to a specified file
            name.
        """
        file_name   = abspath( file_name )
        source_file = self.source_files.setdefault( file_name, SourceFile() )
        source_file.file_name = file_name

        return source_file


    def clear_bp ( self ):
        """ Clears all currently defined break points.
        """
        for source_file in self.source_files.values():
            source_file.clear_bp()

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        """ Handles the 'file_name' facet being changed.
        """
        fh = source_file = None
        try:
            fh = open( file_name, 'rb' )
            for text in fh.readlines():
                stext = text.strip()
                if stext[0:1] not in ( '', '#' ):
                    if text[0:1] != ' ':
                        source_file = self.source_file_for( stext )
                    elif source_file is not None:
                        col = stext.find( '::' )
                        if col >= 0:
                            line    = stext[ : col ].strip()
                            bp_type = 'Breakpoint'
                            code    = ''
                            tcol    = line.find( '[' )
                            if tcol >= 0:
                                bp_type = line[ tcol + 1: -1 ].strip()
                                line    = line[ : tcol ].strip()
                                ccol    = bp_type.find( ':' )
                                if ccol >= 0:
                                    code    = bp_type[ ccol + 1: ]
                                    bp_type = bp_type[ : ccol ]

                            lcol = line.find( ',' )
                            if lcol >= 0:
                                end_line = int( line[ lcol + 1: ] )
                                line     = line[ : lcol ].strip()
                            else:
                                end_line = int( line )

                            source_file.set_bp( int( line ),
                                                stext[ col + 2: ].strip(),
                                                bp_type, code, end_line )
        except:
            pass

        if fh is not None:
            fh.close()

#-- EOF ------------------------------------------------------------------------