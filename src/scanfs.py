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

def isOfInterest(fn):

    if isJarFile(fn):
        return True

    if fn == 'METADATA':
        return True

    if fn == 'PKG-INFO':
        return True

    lfn = fn.lower()

    if lfn.endswith(".class"):
        return True

    
    if State.scanZipFiles and lfn.endswith(".zip"):
        return True
    
    if State.scanTarFiles:
        if lfn.endswith(".tar"):
            return True
        if lfn.endswith(".tgz"):
            return True
        if lfn.endswith(".tar.gz"):
            return True
        
    if State.scanPomFiles and lfn.endswith(".pom"):
        return True
    
    return False

def scanfs(fs, skipset, inputHandle):

    n = len(fs)
    if fs[-1] == '/':
        n = n - 1

    fsh = FileSystem()

    for path, file in fsh.walkFileSystem([fs], skipset, match=lambda fn : isOfInterest(fn)):
        tpath = path[n+1:]
        pfile = path + "/" + file
        if len(tpath) != 0:
            dname=pfile
        else:
            dname=file
        try:
            sin = FileInput(pfile, dname, getFileType(file))
            inputHandle.addChild(sin)
            try:
                dispatchFile(sin)
            except Exception as e:
                errorOut("FS["+pfile+"]:"+str(e))
                #traceback.print_exc()

            sin.clean()
            sin.close()
        except Exception as e:
            errorOut(pfile+":"+str(e))

