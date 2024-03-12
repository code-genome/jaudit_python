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

class Version:

    __version = None
    __analytics = set()
    __evidence = {}

    def __init__(self, version, analytic=None):
        self.__version = version
        self.__appname = None
        self.__notes = None
        if analytic is not None:
            self.__analytics.add(analytic)

    def getVersionID(self):
        return  self.__version

    def addEvidence(self,a,e):
        if a not in self.__evidence:
            self.__evidence[a] = []
        if e not in self.__evidence[a]:
            self.__evidence[a].append(e)

    def add_note(self, note):
        if self.__notes is None:
            self.__notes = []
        self.__notes.append(note)

    def add(self, v):
        for a in v.__analytics:
            self.__analytics.add(a)
        for a in v.__evidence:
            for e in v.__evidence[a]:
                self.addEvidence(a,e)

    def to_dict(self):
        res = {}

        res['version'] = self.__version;

        if len(self.__analytics) != 0:
            res['analytics'] = list(self.__analytics)

        if len(self.__evidence) != 0:
            eset = []
            for a in self.__evidence:
                ev = {}
                ev['analytic'] = a
                ev['evidence'] = self.__evidence[a]
                eset.append(ev)
            res['evidence'] = eset

        if self.__notes is not None:
            res['notes'] = self.__notes

        return res

    def toJSON(self):
        result = "{\"version\":\""+self.__version+"\""

        if len(self.__analytics) != 0:
            result = result + ",\"analytics\":["
            result = result + ",".join(["\""+x+"\"" for x in self.__analytics])
            result = result + "]"
        
        if len(self.__evidence) != 0:
            result = result + ",\"evidence\":["
            sep = ""
            for a in self.__evidence:
                result = result + sep
                sep = ","
                result = result + "{\"analytic\":\""+a+"\",\"evidence\":["
                result = result + ",".join(["\""+x+"\"" for x in self.__evidence[a]])
                result = result + "]}"
            result = result + "]"

        if self.__notes is not None:
            result = result + ",\"notes\":["
            sep = ""
            for note in self.__notes:
                result += sep
                sep = ","
                result += '"' + note + '"'
            result += ']'
            
        result = result + "}"
        return result
