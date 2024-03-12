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

def checkZip(inputHandle):

    stream = inputHandle.getHandle()

    if inputHandle.isFile():
        with ZipFile.ZipFile(inputHandle.getName()) as z:
            for file in z.infolist():
                fn = file.filename
                with z.open(fn,'r') as h:
                    #fd = BytesIO(h.read())
                    #pin = Input(fn, getFileType(fn), fd)
                    pin = Input(fn, getFileType(fn), h)
                    inputHandle.addChild(pin)
                    try:
                        dispatchFile(pin)
                    except Exception as e:
                        errorOut("ZH2:"+str(e))
                        traceback.print_exc()
                    pin.clean()

    else:
        zin = ZipInputStream(stream)

        try:
            while True:
                try:
                    entry = zin.nextFile()
                    if entry is None:
                        break
                    fn = entry.name
                    if fn[-1] == '/':
                        continue
                    fin = Input(fn, getFileType(fn), entry)
                    inputHandle.addChild(fin)
                    try:
                        dispatchFile(fin)
                    except Exception as e:
                        errorOut("ZH1:"+str(e))
                    fin.clean()
                except ZipDecodeError as e:
                    if not zin.attemptResync():
                        break

        except NonStreamable as e:
            analytic = JarName()
            analytic.identify(inputHandle)
            
                            
        
