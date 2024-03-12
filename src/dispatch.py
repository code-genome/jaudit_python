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


def dispatchFile(inputHandle, fromUser=False):

    name = inputHandle.getDisplay()

    if isJarFile(name):
        return processJar(inputHandle)

    lname = name.lower()

    if lname.endswith(".zip"):
        if State.scanZipFiles or fromUser:
            return checkZip(inputHandle)
        return False

    if lname.endswith(".tar"):
        if State.scanTarFiles or fromUser:
            try:
                state = checkTar(inputHandle)
                return state
            except TarSparseUnsupported as e:
                errorOut("DIS1:"+str(e))
            
        return False

    if lname.endswith(".tgz") or lname.endswith(".tar.gz"):
        if State.scanTarFiles or fromUser:
            if inputHandle.isFile():
                zin = gzip.open(name, mode='rb')
            else:
                zin = gzip.GzipFile(fileobj=inputHandle.getHandle())
                
            h = Input(name, "gz", zin)
            inputHandle.addChild(h)
            h.setHidden(True)
            status = False
            try:
                status = checkTar(h)
                return status
            except TarSparseUnsupported as e:
                errorOut("DIS2:"+str(e))
            h.clean()
        return False

    if lname.endswith(".class"):
        return checkClass(inputHandle)

    return False
