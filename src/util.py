##
## This code is part of the Jaudit utilty.
##
## (C) Copyright IBM 2023.
##
## This code is licensed under the Apache License, Version 2.0. You may
## obtain a copy of this license in the LICENSE.txt file in the root directory
## of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
##
## Any modifications or derivative works of this code must retain this
## copyright notice, and modified files need to carry a notice indicating
## that they have been altered from the originals.
##

#
# Python2 doesn't have bytestrings with a hex() method, so we do it
# the hard way.
#

def hexnyb(n):
    return "0123456789abcdef"[n]

def hexbyte(b):
    a = (b >> 4) & 15
    b = b & 15
    return hexnyb(a) + hexnyb(b)

def hex(data):
    res=[]
    for b in struct.unpack(str(len(data))+"B", data):
        res.append(hexbyte(b))
    return "".join(res)

def getplugins(parent):
    result = []
    gset = globals().items()
    for name, object in gset:
        if inspect.isclass(object):
            if issubclass(object, parent):
                if parent == object:
                    continue
                result.append(object)
    return result
