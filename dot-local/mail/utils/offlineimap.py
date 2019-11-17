# ~/.local/mail/utils/offlineimap.py

# offlineimap pythonfile

# encoding and decoding taken from:
# http://piao-tech.blogspot.no/2010/03/get-offlineimap-working-with-non-ascii.html#resources

""" Convert utf-7 imap directory names to utf-8

Imap folder names are encoded using a special version of utf-7 as defined in
RFC 2060 section 5.1.3:

5.1.3. Mailbox International Naming Convention

By convention, international mailbox names are specified using a modified
version of the UTF-7 encoding described in [UTF-7].  The purpose of these
modifications is to correct the following problems with UTF-7:

1) UTF-7 uses the "+" character for shifting; this conflicts with the common
   use of "+" in mailbox names, in particular USENET newsgroup names.

2) UTF-7's encoding is BASE64 which uses the "/" character; this conflicts with
   the use of "/" as a popular hierarchy delimiter.

3) UTF-7 prohibits the unencoded usage of "\"; this conflicts with the use of
   "\" as a popular hierarchy delimiter.

4) UTF-7 prohibits the unencoded usage of "~"; this conflicts with the use of
   "~" in some servers as a home directory indicator.

5) UTF-7 permits multiple alternate forms to represent the same string; in
   particular, printable US-ASCII chararacters can be represented in encoded
   form.

In modified UTF-7, printable US-ASCII characters except for "&" represent
themselves; that is, characters with octet values 0x20-0x25 and 0x27-0x7e.  The
character "&" (0x26) is represented by the two- octet sequence "&-".

All other characters (octet values 0x00-0x1f, 0x7f-0xff, and all Unicode 16-bit
octets) are represented in modified BASE64, with a further modification from
[UTF-7] that "," is used instead of "/".  Modified BASE64 MUST NOT be used to
represent any printing US-ASCII character which can represent itself.

"&" is used to shift to modified BASE64 and "-" to shift back to US- ASCII.
All names start in US-ASCII, and MUST end in US-ASCII (that is, a name that
ends with a Unicode 16-bit octet MUST end with a "- ").

For example, here is a mailbox name which mixes English, Japanese, and Chinese
text: ~peter/mail/&ZeVnLIqe-/&U,BTFw-

"""
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
