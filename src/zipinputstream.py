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

#import sys
#import io
#import struct

class NonStreamable(Exception):
    pass

class ZipDecodeError(Exception):
    pass
#
# This allows processing a Zip file in streaming mode.  It's just utilizing
# the existing zipfile infrastucture.  Usage:
#
# inputHandle = open(filename, 'rb')
# zstream = ZipInputStream(inputHandle)
#
# for entry in zstream.nextFile():
#     filename = entry.name
#     x = entry.read(...)
#
class ZipInputStream:
    __handle = None
    __current = None
    __zinfo = None
    __data = None
    
    def __init__(self, filehandle):
        self.__handle = filehandle
        self.__current = None
        self.__data = None
        z = self.__zinfo = ZipFile.ZipInfo()
        z.orig_filename = None
        z.filename = None
        z.date_time = None
        z.compress_type = None
        z.comment = None
        z.extra = None
        z.create_system = None
        z.create_version = None
        z.extract_version = None
        z.reserved = None
        z.flag_bits = None
        z.volume = None
        z.internal_attr = None
        z.external_attr = None
        z.header_offset = None
        z.CRC = None
        z.compress_size = None
        z.file_size = None
        z._raw_time = None

    def readN(self, nbytes):
        res = None
        while nbytes > 0:
            d = self.__handle.read(nbytes)
            if d is None:
                break
            n = len(d)
            if n <= 0:
                break
            if res is None:
                res = d
            else:
                res = res + d
            nbytes = nbytes - n
        return res

    def nextFile(self):

        zinfo = self.__zinfo

        while True:

            if self.__current is not None:
                try:
                    while True:
                        d = self.__current.read(1024)
                        if d is None:
                            break
                        n = len(d)
                        if n <= 0:
                            break
                except:
                    pass

                if zinfo.flag_bits & 0x08 == 0x08:
                    d = self.readN(4)
                    if d == b'PK\x07\x08':
                        self.readN(12)
                    else:
                        self.readN(8)

            if self.__data is None:
                buffer = self.readN(ZipFile.sizeFileHeader)
            else:
                buffer = self.__data
                self.__data = None

            if buffer is None:
                break

            if len(buffer) != ZipFile.sizeFileHeader:
                raise AttributeError("Truncated file header")

            header = struct.unpack(ZipFile.structFileHeader, buffer)

            if header[ZipFile._FH_SIGNATURE] == ZipFile.stringEndArchive:
                break
            if header[ZipFile._FH_SIGNATURE] == ZipFile.stringCentralDir:
                break
            if header[ZipFile._FH_SIGNATURE] == ZipFile.stringEndArchive64Locator:
                break
            if header[ZipFile._FH_SIGNATURE] == ZipFile.stringEndArchive64:
                break

            if header[ZipFile._FH_SIGNATURE] != ZipFile.stringFileHeader:
                self.__data = buffer
                raise ZipDecodeError("Bad magic number for file header")

            fname = self.readN(header[ZipFile._FH_FILENAME_LENGTH])

            if header[ZipFile._FH_EXTRA_FIELD_LENGTH]:
                self.readN(header[ZipFile._FH_EXTRA_FIELD_LENGTH])

            if header[ZipFile._FH_GENERAL_PURPOSE_FLAG_BITS] & 0x800:
                fname_str = fname.decode("utf-8")
            else:
                fname_str = fname.decode("cp437")

            zinfo.compress_type = header[ZipFile._FH_COMPRESSION_METHOD]
            zinfo.compress_size = header[ZipFile._FH_COMPRESSED_SIZE]
            zinfo.file_size = header[ZipFile._FH_UNCOMPRESSED_SIZE]
            zinfo.extract_version = header[ZipFile._FH_EXTRACT_VERSION]
            zinfo.create_system = header[ZipFile._FH_EXTRACT_SYSTEM]
            zinfo.filename = fname_str
            zinfo.CRC = header[ZipFile._FH_CRC]
            zinfo.flag_bits = header[ZipFile._FH_GENERAL_PURPOSE_FLAG_BITS]
            if zinfo.file_size == 0 and zinfo.compress_size == 0 and (zinfo.flag_bits & 0x08 == 0x08):
                raise NonStreamable("Zip file can't be streamed at "+fname_str)

            self.__current = ZipFile.ZipExtFile(self.__handle,
                                          'r',
                                          zinfo)
            return self.__current

    def attemptResync(self):
        data = b''
        if self.__data is not None:
            data = self.__data
            self.__data = None
        if len(data) < ZipFile.sizeFileHeader:
            n = ZipFile.sizeFileHeader - len(data)
            b = self.readN(n)
            if b is None:
                return
            data = data + b

        while True:
            i = 0
            n = len(data)
            while i < n-1:
                if data[i] == 80 and data[i+1] == 75:
                    data = data[i:]
                    n = len(data)
                    if n < ZipFile.sizeFileHeader:
                        n = ZipFile.sizeFileHeader - n
                        b = self.readN(n)
                        if b is not None:
                            data = data + b
                    if data[2] == 3 and data[3] == 4:
                        self.__current = None
                        self.__data = data
                        return True
                i = i + 1
            n = ZipFile.sizeFileHeader
            if data[-1] == 'P':
                data = data[-1:]
                n = n - 1
            else:
                data = b''
            buf = self.readN(n)
            if buf is None:
                return False
            if len(buf) != n:
                return False
            data = data + buf
