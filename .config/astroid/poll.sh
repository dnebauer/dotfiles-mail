#!/usr/bin/env bash

# ~/.config/astroid/poll.sh

# astroid poll script

set -e  # exit on failure

# need internet connection
if ! ping -w 1 -W 1 -c 1 mail.google.com &>/dev/null ; then
    echo 'No internet connection'
    exit
fi

# fetch new mail
offlineimap -o -u quiet -l $HOME/.local/mail/log/offlineimap.log

# notmuch check for new mail
notmuch new
