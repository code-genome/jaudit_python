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

class ClassDigest(JarIdentifier):

    myname="class-digest"

    def __init__(self):
        self.stream = None
        self.digester = None
        self.hashes = []
        return

    @classmethod
    def priority(cls):
        return 90

    @classmethod
    def supported(cls):
        if Configuration.get_analytic_data(cls.myname):
            return True
        return False

    @classmethod
    def initialize(cls):
        cls.config = Configuration.get_analytic_data('class-digest')
        if cls.config is None:
            return False
        cls.versionmap = cls.config['identifiers']
        return True

    @classmethod
    def scans_class_file(cls):
        return True

    def add_input_stream(self,streamIn):
        if self.stream is not None:
            self.stream.close()
            
        self.digester = sha256()
        self.stream = DigestInput(streamIn, self)
        
        return self.stream

    def add(self, data):
        self.digester.update(data)

    def finish(self):
        digest = hex(self.digester.digest())
        self.hashes.append(digest)
        self.digester = None
        self.stream = None

    def identify(self,inputHandle):

        if self.stream is not None:
            self.stream.close()

        if len(self.hashes) == 0:
            return False
        
        candidates = {}
        size = self.config['size']
        
        self.hashes = [h[0:size] for h in self.hashes]


        pkgmap = self.config['package-map']
        prefix_map = self.config['prefix-map']
        class_map = self.config['class-map']

        for h in self.hashes:
            if h not in self.versionmap:
                continue
            for pid,cid,vid,v in self.versionmap[h]:
                cname = class_map[cid]
                
                if pid == -1:
                    if cname == 'module-info':
                        continue
                    package = ''
                else:
                    package = pkgmap[pid]

                if vid != -1:
                    prefix = prefix_map[vid]
                else:
                    prefix = ""

                version = prefix + v

                if version not in candidates:
                    candidates[version] = 1
                else:
                    candidates[version] += 1

        max = 0
        for v in candidates:
            if candidates[v] > max:
                max = candidates[v]

        if max == 0:
            return False

        version_info = self.config['version_info']
        for version in candidates:
            
            if candidates[version] != max:
                continue
            nv = Version(version, self.myname)
            nc = version_info[version]['class_count']
            if max < nc:
                nv.add_note(str(max) + " of " + str(nc) + " classes from " + version + " embedded in this jar file.")
            if State.addEvidence:
                nv.addEvidence(self.myname, "Digests of class files found.")
            inputHandle.addVersion(nv)

        return True

    @classmethod
    def get_name(cls):
        return cls.myname

    @classmethod
    def get_description(cls):
        return "Uses cryptographic digests (SHA256) of class files in the jar file to identify the version. It is not robust against recompilation, however it can identify versions where the class files have been included directly in a larger project, barring recompilation."
