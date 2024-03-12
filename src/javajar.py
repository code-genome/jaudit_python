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

def isJarFile(file):
    lfn = file.lower()

    if lfn.endswith(".jar"):
        return True
    if lfn.endswith(".jpi"):
        return True
    if lfn.endswith(".war"):
        return True
    if lfn.endswith(".ear"):
        return True
    if lfn.endswith(".hpi"):
        return True
    if lfn.endswith(".sar"):
        return True
    if lfn.endswith(".kar"):
        return True
    if lfn.endswith(".par"):
        return True
    return False

def getFileType(file):
    lfn = file.lower()
    
    if lfn.endswith(".jar"):
        return "jar"
    if lfn.endswith(".zip"):
        return "zip"
    if lfn.endswith(".tar"):
        return "tar"
    if lfn.endswith(".tar.gz"):
        return "tar"
    if lfn.endswith(".tgz"):
        return "tar"
    if lfn.endswith(".class"):
        return "class"
    if lfn.endswith(".pom"):
        return "pom"
    if lfn.endswith(".jpi"):
        return "jpi"
    if lfn.endswith(".war"):
        return "war"
    if lfn.endswith(".ear"):
        return "ear"
    if lfn.endswith(".hpi"):
        return "hpi"
    if lfn.endswith(".sar"):
        return "sar"
    if lfn.endswith(".kar"):
        return "kar"
    if lfn.endswith(".par"):
        return "par"
    
