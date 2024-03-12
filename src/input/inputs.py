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


class Input:
    __name = None
    __file = None
    __children = None
    __versions = None
    __parent = None
    __hidden = False
    __type = None
    __comment = None
    __fullname = None
    __appname = None
    __traits = None
    __displayname = None
    
    def __init__(self,name,type,fileHandle):
        self.__name = name
        self.__type = type
        self.__file = fileHandle
        self.__children = None
        self.__versions = None
        self.__parent = None
        self.__hidden = False
        self.__comment = None
        self.__fullname = None
        self.__appname = None
        self.__traits = None
        self.__displayname = name

    def isFile(self):
        return False

    def addAppName(self, name, evidence):
        if self.__appname is None:
            self.__appname = set()
        self.__appname.add((name,evidence))

    def setName(self, name):
        self.__name = name

    def setDisplay(self,name):
        self.__displayname = name

    def getDisplay(self):
        return self.__displayname

    def setType(self, t):
        self.__type = t

    def close(self):
        self.__file.close()

    def getFullName(self):
        if self.__fullname is None:
            return self.__name
        return self.__fullname

    def setFullName(self,fn):
        self.__fullname = fn

    def setStream(self, handle):
        self.__file = handle

    def addTraits(self, traits):
        if self.__traits is None:
            self.__traits = []
        self.__traits.append(traits)

    def getName(self):
        return self.__name

    def setHidden(self,status):
        self.__hidden = status

    def getHandle(self):
        return self.__file

    def setComment(self, comment):
        self.__comment = comment

    def hasVersions(self):
        if self.__versions is not None:
            return True
        if self.__children is not None:
            for c in self.__children:
                if c.hasVersions():
                    return True
        return False

    def to_dict(self):
        if self.__hidden:
            if self.__children is None:
                return {}
            return self.__children[0].to_dict()

        res = {}
        res['type'] = self.__type
        res['name'] = self.__displayname

        if self.__name != self.__displayname:
            res['alternate_name'] = self.__name

        if self.__comment is not None:
            res['comment'] = self.__comment

        if self.__appname is not None and not self.hasVersions():
            aset=[]
            for (app,ev) in self.__appname:
                x = {}
                x['appname'] = app
                if ev is not None:
                    x['evidence'] = ev
                aset.append(x)
            res['application'] = aset
            
        if self.__children is not None and len(self.__children) != 0:
            cset = []
            for child in self.__children:
                cset.append(child.to_dict())
            res['children'] = cset

        if self.__versions is not None:
            vset = []
            for v in self.__versions:
                vset.append(self.__versions[v].to_dict())
            res['versions'] = vset

        if self.__traits is not None:
            res['traits'] = self.__traits

        return res

    def toJSON(self):
        return json.dumps(self.to_dict(),separators=(',',':'))

    def addChild(self,child):
        if self.__children is None:
            self.__children = []
        self.__children.append(child)
        child.__parent = self

    def clean(self):
        if self.__getvcount() != 0:
            return
        if self.__parent is None:
            return
        if self.__traits is not None:
            return
        self.__parent.__rmchild(self)

    def __rmchild(self,child):
        if self.__children is None:
            return

        self.__children.remove(child)
        child.__parent = None


    def __getvcount(self):
        total = 0
        if self.__versions is not None:
            total = total + len(list(self.__versions))
        if self.__appname is not None:
            total = total + len(list(self.__appname))

        if self.__children != None:
            for child in self.__children:
                total = total + child.__getvcount()
        return total

    def addVersion(self, version):
        if self.__versions is None:
            self.__versions = {}
        v = version.getVersionID()
        if v not in self.__versions:
            self.__versions[v] = version
        else:
            self.__versions[v].add(version)

class FileInput(Input):

    def __init__(self,filename,name,type):
        f = open(filename,"rb")
        Input.__init__(self, filename, type, f)
        self.setFullName(filename)
        self.setDisplay(name)

    def isFile(self):
        return True
