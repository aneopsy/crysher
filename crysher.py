#!/usr/bin/env python

'''
Implement openssl compatible AES-256 CBC mode encryption/decryption.

This module provides encrypt() and decrypt() functions that are compatible
with the openssl algorithms.
'''

import argparse
import base64
import os
import re
import hashlib
import sys
from getpass import getpass
from Crypto.Cipher import AES

VERSION = '1.1'
AUTHOR = "AneoPsy"


def get_key_and_iv(password, salt, klen=32, ilen=16, msgdgst='md5'):
    '''
    Derive the key and the IV from the given password and salt.

    @param password  The password to use as the seed.
    @param salt      The salt.
    @param klen      The key length.
    @param ilen      The initialization vector length.
    @param msgdgst   The message digest algorithm to use.
    '''

    mdf = getattr(__import__('hashlib', fromlist=[msgdgst]), msgdgst)
    password = password.encode('ascii', 'ignore')  # convert to ASCII

    try:
        maxlen = klen + ilen
        keyiv = mdf(password + salt).digest()
        tmp = [keyiv]
        while len(tmp) < maxlen:
            tmp.append(mdf(tmp[-1] + password + salt).digest())
            keyiv += tmp[-1]  # append the last byte
            key = keyiv[:klen]
            iv = keyiv[klen:klen + ilen]
        return key, iv
    except UnicodeDecodeError:
        return None, None


def encrypt(password, plaintext, chunkit=True, msgdgst='md5'):
    '''
    @param password  The password.
    @param plaintext The plaintext to encrypt.
    @param chunkit   Flag that tells encrypt to split the ciphertext
                     into 64 character (MIME encoded) lines.
                     This does not affect the decrypt operation.
    @param msgdgst   The message digest algorithm.
    '''

    salt = os.urandom(8)
    key, iv = get_key_and_iv(password, salt, msgdgst=msgdgst)
    if key is None:
        return None

    padding_len = 16 - (len(plaintext) % 16)
    padded_plaintext = plaintext + (chr(padding_len) * padding_len)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(padded_plaintext)

    openssl_ciphertext = 'Salted__' + salt + ciphertext
    b64 = base64.b64encode(openssl_ciphertext)
    if not chunkit:
        return b64

    LINELEN = 64
    chunk = lambda s: '\n'.join(s[i:min(i + LINELEN, len(s))]
                                for i in xrange(0, len(s), LINELEN))
    return chunk(b64)


def decrypt(password, ciphertext, msgdgst='md5'):
    '''
    @param password   The password.
    @param ciphertext The ciphertext to decrypt.
    @param msgdgst    The message digest algorithm.
    @returns the decrypted data.
    '''

    # unfilter -- ignore blank lines and comments
    filtered = ''
    for line in ciphertext.split('\n'):
        line = line.strip()
        if re.search('^\s*$', line) or re.search('^\s*#', line):
            continue
        filtered += line + '\n'

    # Base64 decode
    raw = base64.b64decode(filtered)
    assert (raw[:8] == 'Salted__')
    salt = raw[8:16]  # get the salt

    # Now create the key and iv.
    key, iv = get_key_and_iv(password, salt, msgdgst=msgdgst)
    if key is None:
        return None

    # The original ciphertext
    ciphertext = raw[16:]

    # Decrypt
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = cipher.decrypt(ciphertext)

    padding_len = ord(padded_plaintext[-1])
    plaintext = padded_plaintext[:-padding_len]
    return plaintext


def _open_ios(args):
    '''
    Open the IO files.
    '''

    ifp = sys.stdin
    ofp = sys.stdout

    if args.input is not None:
        try:
            ifp = open(args.input, 'r')
        except IOError:
            print 'ERROR: can\'t read file: %s' % (args.input)
            sys.exit(1)

    if args.output is not None:
        try:
            ofp = open(args.output, 'w')
        except IOError:
            print 'ERROR: can\'t write file: %s' % (args.output)
            sys.exit(1)

    return ifp, ofp


def _close_ios(ifp, ofp):
    '''
    Close the IO files if necessary.
    '''

    if ifp != sys.stdin:
        ifp.close()

    if ofp != sys.stdout:
        ofp.close()


def _runenc(args):
    '''
    Encrypt data.
    '''
    if args.passphrase is None:
        while True:
            passphrase = getpass('Passphrase: ')
            tmp = getpass('Re-enter passphrase: ')
            if passphrase == tmp:
                break
            print
            print 'Passphrases don\'t match, please try again.'
    else:
        passphrase = args.passphrase

    ifp, ofp = _open_ios(args)
    text = ifp.read()
    out = encrypt(passphrase, text, msgdgst=args.msgdgst)
    ofp.write(out + '\n')
    _close_ios(ifp, ofp)


def _rundec(args):
    '''
    Decrypt data.
    '''
    if args.passphrase is None:
        passphrase = getpass('Passphrase: ')
    else:
        passphrase = args.passphrase

    ifp, ofp = _open_ios(args)
    text = ifp.read()
    out = decrypt(passphrase, text, msgdgst=args.msgdgst)
    ofp.write(out)
    _close_ios(ifp, ofp)


def _runtest(args):
    '''
    @param args  The args parse arguments.
    '''
    import string
    import random
    from random import randint

    # Encrypt/decrypt N random sets of plaintext and passwords.
    num = args.test
    ofp = sys.stdout
    if args.output is not None:
        try:
            ofp = open(args.output, 'w')
        except IOError:
            print 'ERROR: can open file for writing: %s' % (args.output)
            sys.exit(1)

    chset = string.printable
    passed = 0
    failed = []
    maxlen = len(str(num))
    for i in range(num):
        ran1 = randint(8, 32)
        password = ''.join(random.choice(chset) for x in range(ran1))

        ran2 = randint(20, 256)
        plaintext = ''.join(random.choice(chset) for x in range(ran2))

        ciphertext = encrypt(password, plaintext, msgdgst=args.msgdgst)
        verification = decrypt(password, ciphertext, msgdgst=args.msgdgst)

        if plaintext != verification:
            failed.append([password, plaintext])
        else:
            passed += 1

        output = '%*d / %d| %6.2f%% %3d %3d %*d %*d %s' % (maxlen, i + 1,
                                                           num,
                                                           100 * (i + 1) / num,
                                                           len(password),
                                                           len(plaintext),
                                                           maxlen, passed,
                                                           maxlen, len(failed),
                                                           args.msgdgst)
        if args.output is None:
            ofp.write('\b' * 80)
            ofp.write(output)
            ofp.flush()
        else:
            ofp.write(output + '\n')

    ofp.write('\n')

    if len(failed):
        for i in range(len(failed)):
            ofp.write('%3d %2d %-34s %3d %s\n' % (i,
                                                  len(failed[i][0]),
                                                  '"' + failed[i][0] + '"',
                                                  len(failed[i][1]),
                                                  '"' + failed[i][1] + '"'))
        ofp.write('\n')

    if args.output is not None:
        ofp.close()


def _cli_opts():
    '''
    Parse command line options.
    @returns the arguments
    '''
    mepath = unicode(os.path.abspath(sys.argv[0]))
    mebase = '%s' % (os.path.basename(mepath))

    description = '''
        Implements encryption/decryption that is compatible with openssl
        AES-256 CBC mode.
        '''
    desc = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog=mebase,
                                     formatter_class=desc,
                                     description=description,
                                     )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--decrypt',
                       action='store_true',
                       help='decryption mode')
    group.add_argument('-e', '--encrypt',
                       action='store_true',
                       help='encryption mode')
    parser.add_argument('-i', '--input',
                        action='store',
                        help='input file, default is stdin')
    parser.add_argument('-m', '--msgdgst',
                        action='store',
                        default='md5',
                        help='message digest (md5, sha, sha1, sha256, sha512),\
                              default is md5')
    parser.add_argument('-o', '--output',
                        action='store',
                        help='output file, default is stdout')
    parser.add_argument('-p', '--passphrase',
                        action='store',
                        help='passphrase for encrypt/decrypt operations')
    group.add_argument('-t', '--test',
                       action='store',
                       default=-1,
                       type=int,
                       help='test mode (TEST is an integer)')
    parser.add_argument('-v', '--verbose',
                        action='count',
                        help='the level of verbosity')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s v' + VERSION + " by " + AUTHOR)

    args = parser.parse_args()
    return args


def main():
    args = _cli_opts()
    if args.test > 0:
        if args.input is not None:
            print 'WARNING: input argument will be ignored.'
        if args.passphrase is not None:
            print 'WARNING: passphrase argument will be ignored.'
        _runtest(args)
    elif args.encrypt:
        _runenc(args)
    elif args.decrypt:
        _rundec(args)


if __name__ == "__main__":
    main()
