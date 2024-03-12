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

class JarFingerprint(JarIdentifier):

    myname="jar-fingerprint"
    
    def __init__(self):
        self.jde = JarDataExtract()
        return

    @classmethod
    def priority(cls):
        return 80    

    @classmethod
    def supported(cls):
        if Configuration.get_analytic_data(cls.myname):
            return True
        return False    

    @classmethod
    def initialize(cls):
        cls.config = Configuration.get_analytic_data('jar-fingerprint')
        if cls.config is None:
            return False
        cls.versionmap = cls.config['identifiers']
        return True


    @classmethod
    def uses_class_file(cls):
        return True

    @classmethod
    def get_name(cls):
        return cls.myname

    @classmethod
    def get_description(cls):
        return "Uses string constants, method names, field names, referenced methods and referenced fields to create a fingerprint of each class. These fingerprints are then used to identify the version of the jar file containing them. This analytic is robust against compilation with different Java compilers and different compiler options. It also is able to identify versions where the class files have been included directly in a larger project."

    #------------------------------------------------------------------------

    def add_class_file(self,cf):
        self.jde.get_class_fingerprints(cf)

    def identify(self,inputHandle):

        if self.jde.get_class_count() == 0:
            return False
        
        info = self.jde.get()
        size = self.config['size']
        fingerprint = info['jar-fingerprint'][0:size]

        if fingerprint not in self.versionmap:
            return None

        info = self.versionmap[fingerprint]
        prefixes = self.config['prefix-map']

        versions = []
        for pid,v in info:
            if pid != -1:
                v = prefixes[pid] + v
            versions.append(v)

        for v in versions:
            nv = Version(v, self.myname)
            if State.addEvidence:
                nv.addEvidence(self.myname, "Fingerprint matched "+fingerprint)
            inputHandle.addVersion(nv)

    
