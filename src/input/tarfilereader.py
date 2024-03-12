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


class TarFileReader(IOBase):

    __handle = None
    __fileSize = None
    __filename = None
    __origSize = None
    __padding = None
    __filePos = 0

    def __init__(self, handle, bytes, name=None):
        self.__filename = name
        self.__handle = handle
        self.__filePos = 0
        self.__fileSize = bytes
        self.__origSize = bytes
        self.__filePos = 0
        p = bytes % 512
        if p != 0:
            p = 512 - p
        self.__padding = p

    def close(self):
        if self.__handle is not None:
            remaining = self.__fileSize - self.__filePos
            remaining = remaining + self.__padding

            while remaining > 0:
                b = self.__handle.read(remaining)
                if b is None:
                    break
                n = len(b)
                if n <= 0:
                    break
                remaining = remaining - n
            self.__handle = None

    def read(self, size = -1):
        remaining = self.__fileSize - self.__filePos 
        if size == -1:
            size = remaining
        elif size > remaining:
            size = remaining
        res = b''
        while size > 0:
            b = self.__handle.read(size)
            if b is None:
                break
            n = len(b)
            res = res + b
            size = size - n
            self.__filePos = self.__filePos + n
        return res

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
