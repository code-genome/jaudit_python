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

def checkClass(inputHandle):
    #
    # Add code here to handle loose class files
    #
    if len(State.currentJar) == 0:
        State.looseClasses.append(inputHandle.getFullName())
        return False

    stream = inputHandle.getHandle()

    #
    # For now, skip class files that are in META-INF/version
    #
    filename = inputHandle.getFullName()
    if filename.find("META-INF/version") != -1:
        return False

    needClassLoaded = False
    if len(State.currentJar) != 0:
        for a in State.currentJar[-1]:
            if a.scans_class_file():
                stream = a.add_input_stream(stream)
                if stream is None:
                    errorOut(a.get_name() + ".add_input_stream() returned None")
                needClassLoaded = True
            elif a.uses_class_file():
                needClassLoaded = True


    if needClassLoaded:
        jcf = JavaClass().load(stream)
        if jcf is None:
            return False

    analytics = State.currentJar[-1]

    for a in analytics:
        if a.uses_class_file():
            a.add_class_file(jcf)
            
    return True

