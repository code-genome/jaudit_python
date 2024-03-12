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

class ClassFingerprint(JarIdentifier):

    myname="class-fingerprint"
    
    def __init__(self):
        self.jde = JarDataExtract()
        return

    @classmethod
    def priority(cls):
        return 100
    
    @classmethod
    def supported(cls):
        if Configuration.get_analytic_data(cls.myname):
            return True
        return False

    @classmethod
    def initialize(cls):
        cls.config = Configuration.get_analytic_data('class-fingerprint')
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

        versions={}
        unknown=0

        name = inputHandle.getDisplay()

        pkgmap = self.config['package-map']
        prefix_map = self.config['prefix-map']
        class_map = self.config['class-map']

        for crec in info['classes']:
            fingerprint = crec['fingerprint'][0:size]

            if fingerprint not in self.versionmap:
                unknown += 1
                continue

            for pid, cid, vid, version in self.versionmap[fingerprint]:
                cname = class_map[cid]
                if pid == -1:
                    continue
                else:
                    package = pkgmap[pid]

                if package == '':
                    continue

                if vid != -1:
                    prefix = prefix_map[vid]
                else:
                    prefix = ""

                if prefix not in versions:
                    versions[prefix] = {}
                vi = versions[prefix]
                
                if version not in vi:
                    vi[version] = {}
                vi = vi[version]
                
                if package not in vi:
                    vi[package] = set()
                vp = vi[package]
                
                vp.add(cname)

        matches={}
        for p in versions:
            max = 0
            candidates = []

            version_info = self.config['version_info']
            package_data = {}
            for v in versions[p]:
                version_name = p + v

                x = version_info[version_name]['packages']

                count = 0
                packages = set()
                
                for pkg in versions[p][v]:
                    if pkg not in version_info[version_name]['packages']:
                        continue
                    packages.add(pkg)
                    count += len(versions[p][v][pkg])

                if count > max:
                    max = count
                    candidates = [version_name]
                    package_data[version_name] = list(packages)
                elif count == max:
                    package_data[version_name] = list(packages)
                    candidates.append(version_name)
                    
            if max == 0:
                continue
            
            for v in sorted(candidates):
                nc = version_info[v]['class_count']
                nv = Version(v, self.myname)
                if max < nc/4:
                    nv.add_note(str(max) + " of " + str(nc) + " classes from " + v + " embedded in this jar file.")
                elif max < (nc*3/4):
                    nv.add_note(str(max) + " of " + str(nc) + " classes from " + v + " found in this jar file.")
                    
                if State.addEvidence:
                    pkgs = package_data[v]
                    if max < nc:
                        nv.addEvidence(self.myname, str(max) + " fingerprints out of "+str(nc)+" found.")
                        nv.addEvidence(self.myname, "Packages: " + ",".join(pkgs))
                    else:
                        nv.addEvidence(self.myname, "Fingerprints of all class files found ("+str(max)+"/"+str(nc)+").")
                inputHandle.addVersion(nv)

    
