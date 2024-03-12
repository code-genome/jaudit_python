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

class JarDigest(JarIdentifier):

    myname="jar-digest"
    
    def __init__(self):
        self.hashes = []
        self.stream = None
        return

    @classmethod
    def priority(cls):
        return 70
    
    @classmethod
    def supported(cls):
        if Configuration.get_analytic_data(cls.myname):
            return True
        return False

    @classmethod
    def initialize(cls):
        cls.config = Configuration.get_analytic_data('jar-digest')
        if cls.config is None:
            return False
        cls.versionmap = cls.config['identifiers']
        return True

    @classmethod
    def scans_class_file(cls):
        return True
    
    @classmethod
    def get_name(cls):
        return cls.myname

    @classmethod
    def get_description(cls):
        return "Uses cryptographic digests (SHA256) of the contents of the jar file to identify the version of the jar file. This analytic is not robust against compilation using different Java compilers or different options. It also can not detect when class files have been included directly in a larger project."

    #------------------------------------------------------------------------


    #
    # Called by DigestInput for any data that is read from the stream
    #
    def add(self, data):
        self.digester.update(data)
        self.nbytes += len(data)
    #
    # Called by DigestInput when the stream is closed()
    #
    def finish(self):
        d = hex(self.digester.digest())
        self.hashes.append(d)
        self.digester = None
        self.stream = None

    #
    # Called by class file handler for each class file
    #
    def add_input_stream(self, stream):
        if self.stream is not None:
            self.stream.close()
            
        self.nbytes = 0
        self.digester = sha256()
        self.stream = DigestInput(stream, self)
        return self.stream
        

    #
    # Called after jar file has been completely scanned
    #
    def identify(self,inputHandle):

        if self.stream is not None:
            self.stream.close()

        if len(self.hashes) == 0:
            return False
        
        h = sha256()
        for hv in sorted(self.hashes):
            h.update(hv.encode('utf8'))

        size = self.config['size']
        jar_digest = hex(h.digest())[0:size]

        if jar_digest in self.versionmap:
            pmap = self.config['prefix-map']
            for p,v in self.versionmap[jar_digest]:
                if p != -1:
                    v = pmap[p] + v
                nv = Version(v, self.myname)
                if State.addEvidence:
                    nv.addEvidence(self.myname, "Digest matched "+jar_digest)
                inputHandle.addVersion(nv)
            return True
            
        return False

