__author__ = 'hari'

import math
import hashlib
from binascii import hexlify
from binascii import unhexlify

#
# Turns a byte array into a long
# val appears to be a byte array, nbytes is a number
#

def byte_array_to_long(byte_array, nbytes=None):
    #
    # If nbytes is not present
    #
    if nbytes is None:
        #
        # Convert byte -> hex -> int/long
        #
        return int(hexlify(byte_array), 16)
    else:
        #
        # Convert byte -> hex -> int/long
        #
        return int(hexlify(byte_array[-nbytes:]), 16)


def long_to_byte_array(val, nbytes=None):
    hexval = hex(val)[2:-1] if type(val) is long else hex(val)[2:]
    if nbytes is None:
        return unhexlify('0' * (len(hexval) & 1) + hexval)
    else:
        return unhexlify('0' * (nbytes * 2 - len(hexval)) + hexval[-nbytes * 2:])


def generate_derived_parameters(password, salt, iterationcount, id, length_of_key_or_iv_desired):

    #
    # Let r be the iteration count
    #

    r = iterationcount

    #
    # Block size for SHA-256: 512 bits (64 bytes)
    #
    v = 64

    #
    # Length of SHA-256 Hash: 256 bits (32 bytes)
    #
    u = 32

    # In this specification however, all passwords are created from BMPStrings with a NULL
    # terminator. This means that each character in the original BMPString is encoded in 2
    # bytes in big-endian format (most-significant byte first). There are no Unicode byte order
    # marks. The 2 bytes produced from the last character in the BMPString are followed by
    # two additional bytes with the value 0x00.

    password = (unicode(password) + u'\0').encode('utf-16-be') if password is not None else b''

    #
    # Length of password string, p
    #
    p = len(password)

    #
    # Length of salt, s
    #
    s = len(salt)

    #
    # Step 1: Construct a string, D (the "diversifier"), by concatenating v copies of ID.
    #

    D = chr(id) * v
    print hexlify(D)

    #
    # Step 2: Concatenate copies of the salt, s, together to create a string S of length v * [s/v] bits (the
    # final copy of the salt may be truncated to create S). Note that if the salt is the empty
    # string, then so is S
    #

    S = b''

    if salt is not None:
        limit = int(float(v) * math.ceil((float(s)/float(v))))
        for i in range(0, limit):
            S += (salt[i % s])
    else:
        S += '0'

    print "S: ", hexlify(S)

    #
    # Step 3: Concatenate copies of the password, p, together to create a string P of length v * [p/v] bits
    # (the final copy of the password may be truncated to create P). Note that if the
    # password is the empty string, then so is P.
    #

    P = b''

    if password is not None:
        limit = int(float(v) * math.ceil((float(p)/float(v))))
        for i in range(0, limit):
            P += password[i % p]
    else:
        P += '0'

    print "P: ", hexlify(P)

    #
    # Step 4: Set I=S||P to be the concatenation of S and P.  
    #

    I = bytearray(S) + bytearray(P)

    print "I: ", hexlify(I)

    #
    # 5. Set c=[n/u]. (n = length of key/IV required)
    #

    n = length_of_key_or_iv_desired
    c = int(math.ceil(float(n)/float(u)))

    print "C: ", c

    #
    # Step 6 For i=1, 2,..., c, do the following:
    #

    Ai = bytearray()

    for i in range(0, c):
        #
        # Step 6a.Set Ai=Hr(D||I). (i.e. the rth hash of D||I, H(H(H(...H(D||I))))
        #

        hashfunc = hashlib.sha256()
        hashfunc.update(bytearray(D))
        hashfunc.update(bytearray(I))

        Ai = hashfunc.digest()

        print "A before iteration: ", hexlify(Ai)

        for j in range(1, r):
            hashfunc = hashlib.sha256()
            hashfunc.update(Ai)
            Ai = hashfunc.digest()

        print "A after iteration: :", hexlify(Ai)

        #
        # Step 6b: Concatenate copies of Ai to create a string B of length v bits (the final copy of Ai
        # may be truncated to create B).
        #

        B = b''

        for j in range(0, v):
            B += Ai[j % len(Ai)]

        print "B: ", hexlify(B)

        #
        # Step 6c: Treating I as a concatenation I0, I1,..., Ik-1 of v-bit blocks, where k=[s/v]+[p/v],
        # modify I by setting Ij=(Ij+B+1) mod 2v for each j.
        #

        k = int(math.ceil(float(s)/float(v)) + math.ceil((float(p)/float(v))))
        print "K: ", k

        for j in range(0, k-1):
            I = ''.join([
                long_to_byte_array(
                    byte_array_to_long(I[j:j + v]) + byte_array_to_long(bytearray(B)), v
                )
            ])

        print "I after modification: ", hexlify(I)

    return Ai[:length_of_key_or_iv_desired]
