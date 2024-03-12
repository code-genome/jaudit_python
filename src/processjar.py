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

def processJar(inputHandle):
    stream = inputHandle.getHandle()

    analytics=[]
    for a in State.analyticSet:
        name = a.get_name()
        if name in State.enabledAnalytics:
            analytics.append(a())

    State.currentJar.append(analytics)

    for a in analytics:
        if not a.scans_input_stream():
            continue
        stream = a.add_input_stream(stream)

    inputHandle.setStream(stream)

    checkZip(inputHandle)

    result = False
    for a in analytics:
        if a.identify(inputHandle):
            result = True

    State.currentJar.pop()
    return result
