#!/usr/bin/env bash

# ~/.config/astroid/poll.sh

# astroid poll script

USE_POPUP='false'
command -v notify-send &>/dev/null && USE_POPUP='true'

MAILICON='/usr/share/astroid/ui/icons/astroid.svg'
USE_ICON='false'
[ -e "$MAILICON" ] && USE_ICON='true'

function abortscript {
    local msg
    msg="$1"
    # display desktop notification message
    # - it is a fatal error to not have DISPLAY -- when Astroid starts,
    #   it should add DISPLAY to systemd --user's environment
    if [ "$USE_POPUP" = 'true' ] && [ "x$DISPLAY" != "x" ] ; then
        if [ "$USE_ICON" = 'true' ] ; then
            notify-send -i "$MAILICON" 'Astroid mail fetch FAILED' "$msg"
        else
            notify-send 'Astroid mail fetch FAILED' "$msg"
        fi
    fi
    echo "Astroid mail fetch failed: $msg"
    exit 1
}

STATUS='success'

# need internet connection

URL='mail.google.com'
ping -w 1 -W 1 -c 1 "$URL" &>/dev/null || STATUS='failure'
[ "$STATUS" = 'success' ] || abortscript 'No internet connection'

# do a full offlineimap sync once every two hours, otherwise only quicksync

LASTFULL_D="$HOME/.cache/astroid"
if [ ! -d "$LASTFULL_D" ] ; then
    mkdir -p "$LASTFULL_D"
    [ -d "$LASTFULL_D" ] || abortscript 'Unable to create cache file'
fi
LASTFULL_F="$LASTFULL_D/offlineimap-last-full-sync"
if [ -f "$LASTFULL_F" ]; then
    LASTFULL="$(cat "$LASTFULL_F")"
else
    LASTFULL=0
fi
DELTA=$((2 * 60 * 60))  # seconds between full sync (2 hours)
NOW=$(date +%s)
DIFF=$((NOW - LASTFULL))

# fetch new mail with offlineimap

LOG="$HOME/.local/mail/log/offlineimap.log"
if [ $DIFF -gt $DELTA ]; then
    echo "Full offlineimap sync"
    offlineimap -o -u quiet -l "$LOG" || STATUS='failure'
    echo -n "$NOW" > "$LASTFULL_F"
else
    echo 'Quick offlineimap sync'
    offlineimap -o -q -u quiet -l "$LOG" || STATUS='failure'
fi

[ "$STATUS" = 'success' ] || abortscript "See offlineimap log: $LOG"

# notmuch check for new mail

notmuch new
