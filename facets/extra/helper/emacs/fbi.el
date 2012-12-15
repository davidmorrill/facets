;------------------------------------------------------------------------------
;
;  emacs FBI break point functions
;
;  Written by: David C. Morrill
;
;  Date: 09/27/2007
;
;  (c) Copyright 2007 by Enthought, Inc.
;
;------------------------------------------------------------------------------

; Clear all break points:

( defun clear-all-breakpoints ()
    ( interactive )
    ( call-process "python.exe" nil 0 nil fbi-path )
)

; Clear all break points in the current file:

( defun clear-breakpoints ()
    ( interactive )
    ( call-process "python.exe" nil 0 nil fbi-path
        ( buffer-file-name ) )
)

; Toggles a break point on the current line:

( defun toggle-breakpoint ()
    ( interactive )
    ( call-process "python.exe" nil 0 nil fbi-path
        ( buffer-file-name ) 
        ( concat "?" ( number-to-string ( line-number-at-pos ) ) ) )
)

; Sets a count break point on the current line:

( defun count-breakpoint ()
    ( interactive )
    ( call-process "python.exe" nil 0 nil fbi-path
        ( buffer-file-name ) 
        ( concat "#" ( number-to-string ( line-number-at-pos ) ) ) )
)

; Sets a trace break point using the current selection:

( defun trace-breakpoint ( first last )
    ( interactive "r" )
    ( call-process "python.exe" nil 0 nil fbi-path
        ( buffer-file-name ) 
        ( concat
            "@" 
            ( number-to-string ( line-number-at-pos first ) )
            ","
            ( number-to-string ( line-number-at-pos ( - last 1 ) ) )
        )
    )
)

; Sets a print break point using the current selected region:

( defun print-breakpoint ( first last )
    ( interactive "r" )
    ( call-process "python.exe" nil 0 nil fbi-path
        ( buffer-file-name ) 
        ( concat
            "+"
            ( number-to-string ( line-number-at-pos ) )
            "["
            ( buffer-substring first last )
            "]"
        )
    )
)

; Sets a patch break point using the current clipboard contents:

( defun patch-breakpoint ()
    ( interactive )
    ( call-process "python.exe" nil 0 nil fbi-path
        ( buffer-file-name ) 
        ( concat "?" ( number-to-string ( line-number-at-pos ) ) ) )
)

; Sample key bindings:

( global-set-key [?\M-b]       'toggle-breakpoint )
( global-set-key [?\C-\M-b]    'trace-breakpoint )
( global-set-key [?\C-\M-\S-b] 'count-breakpoint )
( global-set-key [?\C-\S-b]    'print-breakpoint )
( global-set-key [?\C-\M-p]    'patch-breakpoint )
( global-set-key [?\C-\S-p]    'clear-breakpoints )
( global-set-key [?\C-\M-\S-p] 'clear-all-breakpoints )

