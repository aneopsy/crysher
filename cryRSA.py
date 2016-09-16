#!/usr/bin/env python

import argparse
import os
import sys
from getpass import getpass
from itertools import combinations
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random
from base64 import b64decode

VERSION = '1.0'
AUTHOR = "AneoPsy"

def generate_RSA(bits=2048, passphrase=""):
    '''
    Generate an RSA keypair with an exponent of 65537 in PEM format
    param: bits The key length in bits
    Return private key and public key
    '''
    rdm = Random.new().read
    key = RSA.generate(bits, randfunc=rdm, e=65537, progress_func=None)

    print key.can_encrypt()
    print key.can_sign()
    print key.has_private()

    public_key = key.publickey().exportKey(format="PEM", passphrase=passphrase, pkcs=1)
    private_key = key.exportKey(format="PEM", passphrase=passphrase, pkcs=1)
    return private_key, public_key

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

    parser = argparse.ArgumentParser(prog=mebase,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
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
    parser.add_argument('-k', '--key',
                        action='store',
                        help='input file, default is stdin')
    parser.add_argument('-m', '--msgdgst',
                        action='store',
                        default='md5',
                        help='message digest (md5, sha, sha1, sha256, sha512), default is md5')
    parser.add_argument('-o', '--output',
                        action='store',
                        help='output file, default is stdout')
    parser.add_argument('-p', '--passphrase',
                        action='store',
                        help='passphrase for encrypt/decrypt operations')
    group.add_argument('-g', '--generate',
                       action='store',
                       default=1024,
                       type=int,
                       help='generate Public & Private keys')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s v' + VERSION + " by " + AUTHOR )

    args = parser.parse_args()
    return args

# ================================================================
# _open_ios
# ================================================================
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

    if args.key is not None:
        try:
            kfp = open(args.key, 'r')
        except IOError:
            print 'ERROR: can\'t read file: %s' % (args.key)
            sys.exit(1)

    return ifp, ofp, kfp


# ================================================================
# _close_ios
# ================================================================
def _close_ios(ifp, ofp, kfp):
    '''
    Close the IO files if necessary.
    '''

    if ifp != sys.stdin:
        ifp.close()

    if ofp != sys.stdout:
        ofp.close()

    if kfp != sys.stdin:
        kfp.close()

def _rundec(args):

    import ast

    if args.passphrase is None:
        passphrase = getpass('Passphrase: ')
    else:
        passphrase = args.passphrase

    ifp, ofp, kfp = _open_ios(args)
    key = RSA.importKey(kfp.read(), passphrase=passphrase)
    decrypted = key.decrypt(ast.literal_eval(str(ifp.read())))
    _close_ios(ifp, ofp, kfp)
    print decrypted

    h = SHA.new()
    h.update(decrypted)
    verifier = PKCS1_PSS.new(key)
    if verifier.verify(h, signature):
        print "The signature is authentic."
    else:
        print "The signature is not authentic."

def _runenc(args):

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

    ifp, ofp, kfp = _open_ios(args)
    key = RSA.importKey(kfp.read(), passphrase=passphrase)
    message = ifp.read()
    out = key.encrypt(message, 32)
    ofp.write(str(out))
    _close_ios(ifp, ofp, kfp)

    h = SHA.new()
    h.update(message)
    signer = PKCS1_PSS.new(key)
    signature = PKCS1_PSS.sign(key)
    print signature

def _rungen(args):

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

    privateKey, publicKey = generate_RSA(args.generate, passphrase)
    f = open('public_key.pem','w')
    f.write(publicKey)
    f.close()
    f = open('private_key.pem','w')
    f.write(privateKey)
    f.close()
    exit()

if __name__ == '__main__':

    args = _cli_opts()
    if args.encrypt:
        _runenc(args)
    elif args.decrypt:
        _rundec(args)
    elif args.generate:
        _rungen(args)
