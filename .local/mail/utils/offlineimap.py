# -*- coding: utf-8- -*-

# ~/.local/mail/utils/offlineimap.py

# offlineimap pythonfile

# encoding and decoding taken from:
# http://piao-tech.blogspot.no/2010/03/\
#   get-offlineimap-working-with-non-ascii.html#resources


import binascii
import codecs
import six


# encoding


def modified_base64(string):
    ''' convert to ascii (base64 coding) '''
    string = string.encode('utf-16be')
    return binascii.b2a_base64(string).rstrip('\n=').replace('/', ',')


def do_base64(_in, right):
    ''' not sure '''
    if _in:
        right.append('&%s-' % modified_base64(''.join(_in)))
        del _in[:]


def encoder(string):
    ''' main encoding function '''
    right = []
    _in = []
    for char in string:
        ord_c = ord(char)
        if 0x20 <= ord_c <= 0x25 or 0x27 <= ord_c <= 0x7e:
            do_base64(_in, right)
            right.append(char)
        elif char == '&':
            do_base64(_in, right)
            right.append('&-')
        else:
            _in.append(char)
    do_base64(_in, right)
    return(str(''.join(right)), len(string))


# decoding


def modified_unbase64(string):
    ''' convert to ascii (base64 coding) '''
    asc = binascii.a2b_base64(string.replace(',', '/') + '===')
    return six.u(asc)


def decoder(string):
    ''' main decoder function '''
    right = []
    decode = []
    for char in string:
        if char == '&' and not decode:
            decode.append('&')
        elif char == '-' and decode:
            if len(decode) == 1:
                right.append('&')
            else:
                right.append(modified_unbase64(''.join(decode[1:])))
            decode = []
        elif decode:
            decode.append(char)
        else:
            right.append(char)

    if decode:
        right.append(modified_unbase64(''.join(decode[1:])))
    bin_str = ''.join(right)
    return(bin_str, len(string))


class StreamReader(codecs.StreamReader):
    ''' read stream '''
    def decode(self, s, errors='strict'):
        return decoder(s)


class StreamWriter(codecs.StreamWriter):
    ''' write stream '''
    def decode(self, s, errors='strict'):
        return encoder(s)


def imap4_utf_7(name):
    ''' codec '''
    if name == 'imap4-utf-7':
        return(encoder, decoder, StreamReader, StreamWriter)


codecs.register(imap4_utf_7)


# required for reading passwords

import subprocess
