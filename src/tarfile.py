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


TAG_File = 48

def getString(data, offset, limit):
    for n in range(0,limit):
        d = data[offset+n:offset+n+1]
        b = struct.unpack('B', d)[0]
        if b == 0:
            end = offset+n
            return data[offset:end].decode()
    end = offset+limit
    return data[offset:end].decode()

def readN(file, n):
    res=None
    while n > 0:
        b = file.read(n)
        if len(b) == 0:
            break
        nb = len(b)
        if res is None:
            res = b
        else:
            res = res + b
        n = n - nb
    if res is None:
        return b''
    return res

class TarSparseUnsupported(Exception):
    pass

def checkTar(inputHandle):
    file = inputHandle.getHandle()
    status = False
    while True:
        data = readN(file,512);
        if len(data) != 512:
            break
        #if data[482] != 0:
        #raise TarSparseUnsupported(inputHandle.getName()+" contains sparse records which are unsupported.")
        d = data[156:157]
        type = struct.unpack('B',d)[0]
        if type != TAG_File:
            continue
        name = getString(data, 0, 100)
        ms = getString(data, 100, 8)
        ss = getString(data, 124, 12)
        size = int(ss, base=8)
        nblocks = int(size / 512)
        if nblocks * 512 != size:
            nblocks = nblocks + 1
        tar = TarFileReader(file, size, name=name)
        tin = Input(name, getFileType(name), tar)
        inputHandle.addChild(tin)
        if dispatchFile(tin):
            status = True
        tin.clean()
        tin.close()
    return status
