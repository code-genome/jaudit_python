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

class DigestInput(IOBase):

    __handle = None
    __digest = None

    def __init__(self, handle, digester):
        self.__handle = handle
        self.__digest = digester

    def close(self):
        if self.__handle is not None:
            while True:
                b = self.__handle.read(512)
                if b is None:
                    break
                if len(b) == 0:
                    break
                self.__digest.add(b)
        self.__handle = None
        self.__digest.finish()

    def read(self, size = -1):
        data = self.__handle.read(size)
        if data is not None:
            self.__digest.add(data)
        return data

    def isFile(self):
        return False

    def writable(self):
        return False

    def readable(self):
        return True

    def seekable(self):
        return False

    def __enter__(self):
        return 0

    def __exit__(self):
        return 0

    def __iter__(self):
        raise UnsupportedOperation("Not supported")

    def __next__(self):
        raise UnsupportedOperation("Not supported")

    def readlines(self):
        raise UnsupportedOperation("Not supported")

    def readline(self):
        raise UnsupportedOperation("Not supported")

    def writelines(self):
        raise UnsupportedOperation("Not supported")

    def isatty(self):
        return False

    def flush(self):
        raise UnsupportedOperation("Not supported")
